#!/usr/bin/env python3
"""Run behavior evals for a skill: does the skill beat baseline on real tasks?

Owns the workspace layout end to end, so nothing hand-builds the directories the
aggregator reads:

    <workspace>/iteration-<N>/eval-<id>/
        eval_metadata.json
        with_skill/run-<k>/{outputs/, grading.json, timing.json}
        without_skill/run-<k>/{outputs/, grading.json, timing.json}

Each run is a `claude -p` invocation inside a throwaway project outside this
repo, so the repo's own CLAUDE.md, rules, and skills never contaminate either
configuration. The with_skill config gets the skill copied in and invokes it by
name; the baseline gets the bare prompt.

Usage:
    uv run python -m scripts.run_behavior_eval <skill-dir> --iteration 1 -k 3 --yes
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

CONFIGS = ("with_skill", "without_skill")

# Appended to every prompt in both configurations so deliverables land where the
# grader looks. Identical across configs to keep the comparison fair.
OUTPUT_DIRECTIVE = "\n\nWrite every file you produce into the current working directory."

JUDGE_PROMPT = """\
You are grading one run of an automated skill evaluation.

The task given to the assistant was:
<task>
{prompt}
</task>

These files are what it produced:
<outputs>
{outputs}
</outputs>

Grade each assertion below against those files alone. An assertion passes only
when the files show it is satisfied in substance, not merely in form: a correct
filename with wrong or empty contents is a failure. When the files do not
settle it, fail it.

<assertions>
{assertions}
</assertions>

Return JSON only, no prose, in exactly this shape:
{{"verdicts": [
  {{"id": "<assertion id>", "passed": true, "evidence": "<what decided it>"}}
]}}
"""

MAX_JUDGE_FILE_CHARS = 20000


def load_evals(skill_dir: Path) -> dict:
    path = skill_dir / "evals" / "evals.json"
    if not path.exists():
        sys.exit(f"No eval suite at {path} — write one before running behavior evals.")
    data = json.loads(path.read_text())
    if not data.get("evals"):
        sys.exit(f"{path} has no evals.")
    return data


def build_scratch_project(skill_dir: Path, config: str) -> tuple[Path, Path]:
    """Create a throwaway project outside the repo. Returns (root, workdir)."""
    root = Path(tempfile.mkdtemp(prefix="skill-eval-"))
    work = root / "work"
    work.mkdir()
    if config == "with_skill":
        dest = root / ".claude" / "skills" / skill_dir.name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(skill_dir, dest)
    else:
        (root / ".claude").mkdir()
    return root, work


def claude_headless(
    prompt: str, cwd: Path, timeout: int, model: str | None, permission_mode: str
) -> dict:
    """Run `claude -p` and return the parsed result envelope."""
    cmd = ["claude", "-p", prompt, "--output-format", "json"]
    if model:
        cmd.extend(["--model", model])
    if permission_mode:
        cmd.extend(["--permission-mode", permission_mode])

    # Drop CLAUDECODE so a nested `claude -p` is allowed; the guard exists for
    # interactive terminal conflicts, not programmatic subprocess use.
    env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}

    started = time.time()
    try:
        proc = subprocess.run(
            cmd,
            cwd=cwd,
            env=env,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return {"error": f"timed out after {timeout}s", "duration_ms": timeout * 1000}

    elapsed_ms = int((time.time() - started) * 1000)
    try:
        payload = json.loads(proc.stdout)
    except json.JSONDecodeError:
        return {
            "error": f"unparseable claude output (exit {proc.returncode})",
            "stderr": proc.stderr[-2000:],
            "duration_ms": elapsed_ms,
        }

    # `claude -p --output-format json` emits the full message list; the closing
    # `result` entry carries the text, usage, and timing.
    if isinstance(payload, list):
        envelope = next(
            (m for m in reversed(payload) if isinstance(m, dict) and m.get("type") == "result"),
            None,
        )
        if envelope is None:
            return {
                "error": f"no result message in claude output (exit {proc.returncode})",
                "duration_ms": elapsed_ms,
            }
    else:
        envelope = payload

    envelope.setdefault("duration_ms", elapsed_ms)
    if envelope.get("is_error"):
        envelope["error"] = envelope.get("subtype") or "claude reported an error"
    return envelope


def collect_outputs(work: Path, outputs_dir: Path) -> list[Path]:
    outputs_dir.mkdir(parents=True, exist_ok=True)
    produced = []
    for item in sorted(work.rglob("*")):
        if item.is_file():
            rel = item.relative_to(work)
            target = outputs_dir / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, target)
            produced.append(rel)
    return produced


def run_checks(assertions: list[dict], outputs_dir: Path, skill_dir: Path) -> dict[str, dict]:
    """Run every assertion carrying a `check` as a shell command in outputs/.

    `$SKILL_DIR` is exported so a check can reach the skill's own bundled
    scripts without hardcoding a machine-specific path.
    """
    env = {**os.environ, "SKILL_DIR": str(skill_dir)}
    results = {}
    for a in assertions:
        check = a.get("check")
        if not check:
            continue
        try:
            proc = subprocess.run(
                ["bash", "-c", check],
                cwd=outputs_dir,
                env=env,
                capture_output=True,
                text=True,
                timeout=60,
            )
            passed = proc.returncode == 0
            detail = (proc.stdout or proc.stderr).strip()[:400]
            evidence = f"`{check}` exited {proc.returncode}"
            if detail:
                evidence += f": {detail}"
        except subprocess.TimeoutExpired:
            passed, evidence = False, f"`{check}` timed out"
        results[a["id"]] = {"passed": passed, "evidence": evidence}
    return results


def judge_outputs(
    prompt: str, assertions: list[dict], outputs_dir: Path, timeout: int, model: str | None
) -> dict[str, dict]:
    """Grade assertions with no `check` using a fresh-context judge.

    The judge sees the task and the produced files — never the transcript the
    executor wrote about itself.
    """
    pending = [a for a in assertions if not a.get("check")]
    if not pending:
        return {}

    rendered = []
    for f in sorted(outputs_dir.rglob("*")):
        if not f.is_file():
            continue
        try:
            body = f.read_text()[:MAX_JUDGE_FILE_CHARS]
        except (UnicodeDecodeError, OSError):
            body = f"<binary file, {f.stat().st_size} bytes>"
        rendered.append(f"--- {f.relative_to(outputs_dir)} ---\n{body}")
    outputs_blob = "\n\n".join(rendered) if rendered else "<no files were produced>"

    listed = "\n".join(f"- id={a['id']}: {a['text']}" for a in pending)
    filled = JUDGE_PROMPT.format(prompt=prompt, outputs=outputs_blob, assertions=listed)

    scratch = Path(tempfile.mkdtemp(prefix="skill-judge-"))
    try:
        envelope = claude_headless(filled, scratch, timeout, model, "acceptEdits")
    finally:
        shutil.rmtree(scratch, ignore_errors=True)

    raw = envelope.get("result", "")
    verdicts = {}
    try:
        start, end = raw.index("{"), raw.rindex("}") + 1
        parsed = json.loads(raw[start:end])
        for v in parsed.get("verdicts", []):
            verdicts[str(v.get("id"))] = {
                "passed": bool(v.get("passed")),
                "evidence": str(v.get("evidence", ""))[:600],
            }
    except (ValueError, json.JSONDecodeError):
        pass

    for a in pending:
        verdicts.setdefault(
            a["id"], {"passed": False, "evidence": "judge returned no verdict for this assertion"}
        )
    return verdicts


def run_one(spec: dict) -> dict:
    """Execute and grade a single (eval, config, run) cell."""
    ev, config, k = spec["eval"], spec["config"], spec["k"]
    run_dir = spec["iteration_dir"] / f"eval-{ev['id']}" / config / f"run-{k}"
    outputs_dir = run_dir / "outputs"
    run_dir.mkdir(parents=True, exist_ok=True)

    prompt = ev["prompt"]
    if config == "with_skill":
        prompt = f"/{spec['skill_name']}\n\n{prompt}"
    prompt += OUTPUT_DIRECTIVE

    root, work = build_scratch_project(spec["skill_dir"], config)
    try:
        for f in ev.get("files", []):
            src = spec["skill_dir"] / f
            if src.exists():
                shutil.copy2(src, work / src.name)
        envelope = claude_headless(
            prompt, work, spec["timeout"], spec["model"], spec["permission_mode"]
        )
        collect_outputs(work, outputs_dir)
    finally:
        shutil.rmtree(root, ignore_errors=True)

    # The assistant's closing text, kept for debugging a run that produced
    # nothing. The judge never sees it — it grades the files alone.
    (run_dir / "result.md").write_text(str(envelope.get("result", envelope.get("error", ""))))

    usage = envelope.get("usage", {}) or {}
    total_tokens = (usage.get("input_tokens", 0) or 0) + (usage.get("output_tokens", 0) or 0)
    duration_ms = envelope.get("duration_ms", 0)
    (run_dir / "timing.json").write_text(
        json.dumps(
            {
                "total_tokens": total_tokens,
                "duration_ms": duration_ms,
                "total_duration_seconds": round(duration_ms / 1000, 1),
                "total_cost_usd": envelope.get("total_cost_usd"),
            },
            indent=2,
        )
    )

    assertions = ev.get("assertions", [])
    graded = run_checks(assertions, outputs_dir, spec["skill_dir"])
    graded.update(
        judge_outputs(ev["prompt"], assertions, outputs_dir, spec["timeout"], spec["judge_model"])
    )

    expectations = [
        {
            "text": a["text"],
            "passed": graded.get(a["id"], {}).get("passed", False),
            "evidence": graded.get(a["id"], {}).get("evidence", "not graded"),
        }
        for a in assertions
    ]
    passed = sum(1 for e in expectations if e["passed"])
    total = len(expectations)
    grading = {
        "expectations": expectations,
        "summary": {
            "passed": passed,
            "failed": total - passed,
            "total": total,
            "pass_rate": round(passed / total, 4) if total else 0.0,
        },
        "timing": {"total_duration_seconds": round(duration_ms / 1000, 1)},
    }
    if "error" in envelope:
        grading["run_error"] = envelope["error"]
    (run_dir / "grading.json").write_text(json.dumps(grading, indent=2))

    return {
        "eval_id": ev["id"],
        "config": config,
        "run": k,
        "pass_rate": grading["summary"]["pass_rate"],
        "error": envelope.get("error"),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Run behavior evals for a skill")
    ap.add_argument("skill_dir", help="Path to the skill directory")
    ap.add_argument("--iteration", type=int, default=1)
    ap.add_argument("-k", "--repeats", type=int, default=3, help="Runs per eval per config")
    ap.add_argument("--workspace", default=None, help="Defaults to a sibling <name>-workspace/")
    ap.add_argument("--concurrency", type=int, default=4)
    ap.add_argument("--timeout", type=int, default=600, help="Seconds per run")
    ap.add_argument("--model", default=None, help="Model alias for the runs under test")
    ap.add_argument("--judge-model", default="sonnet", help="Model alias for the grader")
    ap.add_argument(
        "--permission-mode",
        default="acceptEdits",
        help="acceptEdits blocks Bash; pass bypassPermissions for skills that shell out",
    )
    ap.add_argument("--yes", action="store_true", help="Execute; without it this is a dry run")
    args = ap.parse_args()

    skill_dir = Path(args.skill_dir).resolve()
    suite = load_evals(skill_dir)
    evals = suite["evals"]
    skill_name = suite.get("skill_name", skill_dir.name)

    workspace = (
        Path(args.workspace).resolve()
        if args.workspace
        else skill_dir.parent / f"{skill_dir.name}-workspace"
    )
    iteration_dir = workspace / f"iteration-{args.iteration}"

    total_runs = len(evals) * len(CONFIGS) * args.repeats
    print(f"Skill:      {skill_name} ({skill_dir})")
    print(f"Evals:      {len(evals)}  ×  configs: {len(CONFIGS)}  ×  repeats: {args.repeats}")
    print(f"Total runs: {total_runs} `claude -p` invocations")
    print(f"Workspace:  {iteration_dir}")
    if not args.yes:
        print("\nDry run. Re-run with --yes to execute.")
        return 0

    iteration_dir.mkdir(parents=True, exist_ok=True)
    for ev in evals:
        eval_dir = iteration_dir / f"eval-{ev['id']}"
        eval_dir.mkdir(parents=True, exist_ok=True)
        (eval_dir / "eval_metadata.json").write_text(
            json.dumps(
                {
                    "eval_id": ev["id"],
                    "eval_name": ev.get("name", f"eval-{ev['id']}"),
                    "prompt": ev["prompt"],
                    "assertions": [a["text"] for a in ev.get("assertions", [])],
                },
                indent=2,
            )
        )

    specs = [
        {
            "eval": ev,
            "config": config,
            "k": k,
            "skill_dir": skill_dir,
            "skill_name": skill_name,
            "iteration_dir": iteration_dir,
            "timeout": args.timeout,
            "model": args.model,
            "judge_model": args.judge_model,
            "permission_mode": args.permission_mode,
        }
        for ev in evals
        for config in CONFIGS
        for k in range(1, args.repeats + 1)
    ]

    done = 0
    errors = 0
    with ThreadPoolExecutor(max_workers=args.concurrency) as pool:
        futures = {pool.submit(run_one, s): s for s in specs}
        for fut in as_completed(futures):
            s = futures[fut]
            done += 1
            try:
                r = fut.result()
            except Exception as e:  # noqa: BLE001 - one bad cell must not kill the sweep
                errors += 1
                print(f"[{done}/{total_runs}] eval-{s['eval']['id']} {s['config']} FAILED: {e}")
                continue
            if r["error"]:
                errors += 1
            flag = f"  ({r['error']})" if r["error"] else ""
            print(
                f"[{done}/{total_runs}] eval-{r['eval_id']} {r['config']} "
                f"run-{r['run']}: pass_rate={r['pass_rate']}{flag}"
            )

    print(f"\nWrote {iteration_dir}")
    print(
        "Next: uv run python -m scripts.aggregate_benchmark "
        f"{iteration_dir} --skill-name {skill_name}"
    )
    if errors:
        print(
            f"{errors} run(s) reported an error — read their grading.json before trusting totals."
        )
    return 1 if errors == total_runs else 0


if __name__ == "__main__":
    sys.exit(main())
