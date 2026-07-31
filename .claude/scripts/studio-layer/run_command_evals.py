#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Run behavior evals for the studio phase commands.

Usage:
    run_command_evals.py <commands-dir> -k 3 --yes
    run_command_evals.py <commands-dir> --lint

Modeled on `.claude/skills/meta-skills/scripts/run_behavior_eval.py` -- scratch project,
`claude -p` per run, judge-graded assertions, a pass rate over k runs. It exists because
that runner cannot reach a command: it stages its target into `<scratch>/.claude/skills/
<name>` and `eval.py` refuses a directory with no SKILL.md, while a command is only
invocable as `/<namespace>:<name>` from `.claude/commands/`.

Per run it stages the whole namespace -- `.claude/{commands,agents,skills,rules,scripts}/
<namespace>/` plus `.claude/hooks/check_gate_signoff.py` -- into a throwaway project
outside this repo, so the command resolves, the roles it spawns exist, the check scripts
it calls are on disk, and the four hard-gate commands find the hook their frontmatter
registers, while the repo's own rules never contaminate the run. The case's prompt is
invoked verbatim as a slash command with the scratch project as cwd, so what the command
writes lands inside it.

Each assertion carrying a `check` is graded by running it (exit 0 = pass); the rest go to
a fresh-context judge that sees the produced files and never the executor's own account of
them. A case clears when its mean pass rate over k runs reaches the `pass_rate` it records
(default 1.0).

Exit 0 when every case clears its rate, 1 when one does not, 2 on a usage or parse
failure. `--lint` validates the suite schema only: it grades nothing and spends no tokens.
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

STAGED_NAMESPACE_DIRS = ("commands", "agents", "skills", "rules", "scripts")
STAGED_HOOKS = ("check_gate_signoff.py",)
DEFAULT_PASS_RATE = 1.0
MAX_JUDGE_FILE_CHARS = 20000

JUDGE_PROMPT = """\
You are grading one run of an automated command evaluation.

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


class SuiteError(Exception):
    """The suite cannot be located, parsed, or staged."""


def load_suite(commands_dir: Path) -> tuple[dict, Path]:
    path = commands_dir / "evals" / "evals.json"
    if not path.is_file():
        raise SuiteError(f"no eval suite at {path} -- write one before running command evals")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as err:
        raise SuiteError(f"{path} is unreadable: {err}") from err
    return data, path


def validate(suite: object, path: Path) -> list[str]:
    """Every way the suite can be unrunnable, reported at once rather than one per run."""
    if not isinstance(suite, dict):
        return [f"{path} is not a JSON object"]

    problems = []
    if not suite.get("skill_name"):
        problems.append(f"{path} declares no skill_name")

    evals = suite.get("evals")
    if not isinstance(evals, list) or not evals:
        problems.append(f"{path} has no 'evals' array")
        return problems

    for case in evals:
        if not isinstance(case, dict):
            problems.append(f"{path} has a case that is not an object")
            continue
        label = case.get("name") or case.get("id")
        for field in ("id", "name", "prompt"):
            if case.get(field) in (None, ""):
                problems.append(f"{path} case {label!r} is missing '{field}'")
        prompt = case.get("prompt")
        # The runner invokes the prompt verbatim; one that is not a slash command
        # evaluates the model's general behavior rather than the command under test.
        if isinstance(prompt, str) and prompt and not prompt.startswith("/"):
            problems.append(
                f"{path} case {label!r} does not open with a slash command -- "
                "nothing under test would be invoked"
            )
        rate = case.get("pass_rate", DEFAULT_PASS_RATE)
        if not isinstance(rate, (int, float)) or isinstance(rate, bool) or not 0 < rate <= 1:
            problems.append(f"{path} case {label!r} records a pass_rate outside (0, 1]")

        assertions = case.get("assertions")
        if not isinstance(assertions, list) or not assertions:
            problems.append(f"{path} case {label!r} has no assertions -- it grades nothing")
            continue
        seen = set()
        for assertion in assertions:
            if not isinstance(assertion, dict) or not assertion.get("id"):
                problems.append(f"{path} case {label!r} has an assertion with no id")
                continue
            if not assertion.get("text"):
                problems.append(f"{path} case {label!r} assertion {assertion['id']!r} has no text")
            if assertion["id"] in seen:
                problems.append(
                    f"{path} case {label!r} reuses assertion id {assertion['id']!r} -- "
                    "one verdict would overwrite the other"
                )
            seen.add(assertion["id"])
            if "check" in assertion and not str(assertion["check"]).strip():
                problems.append(
                    f"{path} case {label!r} assertion {assertion['id']!r} has an empty check"
                )
    return problems


def stage_project(commands_dir: Path, root: Path) -> None:
    """Stage the whole namespace into `root` so the command resolves with its machinery.

    The hook sits outside the namespace but is load-bearing: the hard-gate commands
    register `"$CLAUDE_PROJECT_DIR"/.claude/hooks/check_gate_signoff.py`, so omitting it
    would evaluate them with their gate silently absent.
    """
    claude = commands_dir.parents[1]
    namespace = commands_dir.name
    dest = root / ".claude"
    for kind in STAGED_NAMESPACE_DIRS:
        src = claude / kind / namespace
        if not src.is_dir():
            raise SuiteError(f"{src} is missing -- the staged project would be incomplete")
        shutil.copytree(src, dest / kind / namespace)
    (dest / "hooks").mkdir(parents=True, exist_ok=True)
    for hook in STAGED_HOOKS:
        src = claude / "hooks" / hook
        if not src.is_file():
            raise SuiteError(f"{src} is missing -- the hard gates would run ungated")
        shutil.copy2(src, dest / "hooks" / hook)


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
    env["CLAUDE_PROJECT_DIR"] = str(cwd)

    started = time.time()
    try:
        proc = subprocess.run(
            cmd, cwd=cwd, env=env, capture_output=True, text=True, timeout=timeout
        )
    except subprocess.TimeoutExpired:
        return {"error": f"timed out after {timeout}s"}
    except OSError as err:
        return {"error": f"could not launch claude: {err}"}

    elapsed_ms = int((time.time() - started) * 1000)
    try:
        payload = json.loads(proc.stdout)
    except json.JSONDecodeError:
        return {
            "error": f"unparseable claude output (exit {proc.returncode})",
            "stderr": proc.stderr[-2000:],
            "duration_ms": elapsed_ms,
        }

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


def collect_outputs(root: Path, outputs_dir: Path) -> list[Path]:
    """Copy what the run wrote into the scratch project, minus the staged namespace."""
    outputs_dir.mkdir(parents=True, exist_ok=True)
    staged = root / ".claude"
    produced = []
    for item in sorted(root.rglob("*")):
        if not item.is_file() or staged == item or staged in item.parents:
            continue
        rel = item.relative_to(root)
        target = outputs_dir / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(item, target)
        produced.append(rel)
    return produced


def run_checks(assertions: list[dict], cwd: Path) -> dict[str, dict]:
    """Grade every assertion carrying a `check` by running it: exit 0 = pass.

    Checks run in the scratch project root, where the produced files and the staged
    `.claude/scripts/` a check invokes both resolve from the paths a case writes.
    """
    results = {}
    for assertion in assertions:
        check = assertion.get("check")
        if not check:
            continue
        try:
            proc = subprocess.run(
                ["bash", "-c", check], cwd=cwd, capture_output=True, text=True, timeout=120
            )
            passed = proc.returncode == 0
            detail = (proc.stdout or proc.stderr).strip()[:400]
            evidence = f"`{check}` exited {proc.returncode}"
            if detail:
                evidence += f": {detail}"
        except subprocess.TimeoutExpired:
            passed, evidence = False, f"`{check}` timed out"
        results[assertion["id"]] = {"passed": passed, "evidence": evidence}
    return results


def judge_outputs(
    prompt: str, assertions: list[dict], outputs_dir: Path, timeout: int, model: str | None
) -> dict[str, dict]:
    """Grade the assertions with no `check` from the produced files alone."""
    pending = [a for a in assertions if not a.get("check")]
    if not pending:
        return {}

    rendered = []
    for produced in sorted(outputs_dir.rglob("*")):
        if not produced.is_file():
            continue
        try:
            body = produced.read_text(encoding="utf-8")[:MAX_JUDGE_FILE_CHARS]
        except (UnicodeDecodeError, OSError):
            body = f"<binary file, {produced.stat().st_size} bytes>"
        rendered.append(f"--- {produced.relative_to(outputs_dir)} ---\n{body}")
    outputs_blob = "\n\n".join(rendered) if rendered else "<no files were produced>"

    listed = "\n".join(f"- id={a['id']}: {a['text']}" for a in pending)
    filled = JUDGE_PROMPT.format(prompt=prompt, outputs=outputs_blob, assertions=listed)

    scratch = Path(tempfile.mkdtemp(prefix="command-judge-"))
    try:
        envelope = claude_headless(filled, scratch, timeout, model, "acceptEdits")
    finally:
        shutil.rmtree(scratch, ignore_errors=True)

    verdicts: dict[str, dict] = {}
    raw = envelope.get("result", "")
    try:
        start, end = raw.index("{"), raw.rindex("}") + 1
        parsed = json.loads(raw[start:end])
        for verdict in parsed.get("verdicts", []):
            verdicts[str(verdict.get("id"))] = {
                "passed": bool(verdict.get("passed")),
                "evidence": str(verdict.get("evidence", ""))[:600],
            }
    except (ValueError, json.JSONDecodeError):
        pass

    for a in pending:
        verdicts.setdefault(
            a["id"], {"passed": False, "evidence": "judge returned no verdict for this assertion"}
        )
    return verdicts


def run_one(spec: dict) -> dict:
    """Execute and grade a single (case, run) cell."""
    case, k = spec["case"], spec["k"]
    run_dir = spec["workspace"] / f"eval-{case['id']}" / f"run-{k}"
    outputs_dir = run_dir / "outputs"
    run_dir.mkdir(parents=True, exist_ok=True)

    root = Path(tempfile.mkdtemp(prefix="command-eval-"))
    try:
        stage_project(spec["commands_dir"], root)
        envelope = claude_headless(
            case["prompt"], root, spec["timeout"], spec["model"], spec["permission_mode"]
        )
        collect_outputs(root, outputs_dir)
        assertions = case.get("assertions", [])
        graded = run_checks(assertions, root)
    finally:
        shutil.rmtree(root, ignore_errors=True)

    graded.update(
        judge_outputs(case["prompt"], assertions, outputs_dir, spec["timeout"], spec["judge_model"])
    )

    # The assistant's closing text, kept for debugging a run that produced nothing.
    # The judge never sees it -- it grades the files alone.
    (run_dir / "result.md").write_text(
        str(envelope.get("result", envelope.get("error", ""))), encoding="utf-8"
    )

    expectations = []
    for assertion in assertions:
        verdict = graded.get(assertion["id"], {})
        expectations.append(
            {
                "text": assertion["text"],
                "passed": verdict.get("passed", False),
                "evidence": verdict.get("evidence", "not graded"),
            }
        )
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
    }
    if "error" in envelope:
        grading["run_error"] = envelope["error"]
    (run_dir / "grading.json").write_text(json.dumps(grading, indent=2), encoding="utf-8")

    return {
        "eval_id": case["id"],
        "run": k,
        "pass_rate": grading["summary"]["pass_rate"],
        "error": envelope.get("error"),
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Run behavior evals for a command namespace")
    ap.add_argument("commands_dir", help="Path to the command namespace directory")
    ap.add_argument(
        "--lint", action="store_true", help="Validate the suite schema only; grades nothing"
    )
    ap.add_argument("-k", "--repeats", type=int, default=3, help="Runs per case")
    ap.add_argument("--workspace", default=None, help="Defaults to a fresh temporary directory")
    ap.add_argument("--concurrency", type=int, default=4)
    ap.add_argument("--timeout", type=int, default=900, help="Seconds per run")
    ap.add_argument("--model", default=None, help="Model alias for the runs under test")
    ap.add_argument("--judge-model", default="sonnet", help="Model alias for the grader")
    ap.add_argument("--permission-mode", default="bypassPermissions")
    ap.add_argument("--yes", action="store_true", help="Execute; without it this is a dry run")
    args = ap.parse_args(argv)

    commands_dir = Path(args.commands_dir).resolve()
    try:
        suite, suite_path = load_suite(commands_dir)
    except SuiteError as err:
        print(err)
        return 2

    problems = validate(suite, suite_path)
    if problems:
        for problem in problems:
            print(f"FAIL: {problem}")
        return 2

    cases = suite["evals"]
    if args.lint:
        print(f"{suite_path}: {len(cases)} case(s), schema valid")
        return 0

    if args.repeats < 1:
        print("-k must be at least 1")
        return 2

    workspace = (
        Path(args.workspace).resolve()
        if args.workspace
        else Path(tempfile.mkdtemp(prefix="studio-command-evals-"))
    )

    print(f"Commands:   {suite.get('skill_name')} ({commands_dir})")
    print(f"Cases:      {len(cases)}  ×  repeats: {args.repeats}")
    print(f"Total runs: {len(cases) * args.repeats} `claude -p` invocations")
    print(f"Workspace:  {workspace}")
    if not args.yes:
        print("\nDry run. Re-run with --yes to execute.")
        return 0

    workspace.mkdir(parents=True, exist_ok=True)
    for case in cases:
        eval_dir = workspace / f"eval-{case['id']}"
        eval_dir.mkdir(parents=True, exist_ok=True)
        (eval_dir / "eval_metadata.json").write_text(
            json.dumps(
                {
                    "eval_id": case["id"],
                    "eval_name": case["name"],
                    "prompt": case["prompt"],
                    "assertions": [a["text"] for a in case["assertions"]],
                    "pass_rate": case.get("pass_rate", DEFAULT_PASS_RATE),
                },
                indent=2,
            ),
            encoding="utf-8",
        )

    specs = [
        {
            "case": case,
            "k": k,
            "commands_dir": commands_dir,
            "workspace": workspace,
            "timeout": args.timeout,
            "model": args.model,
            "judge_model": args.judge_model,
            "permission_mode": args.permission_mode,
        }
        for case in cases
        for k in range(1, args.repeats + 1)
    ]

    rates: dict[object, list[float]] = {case["id"]: [] for case in cases}
    done = 0
    with ThreadPoolExecutor(max_workers=args.concurrency) as pool:
        futures = {pool.submit(run_one, s): s for s in specs}
        for fut in as_completed(futures):
            spec = futures[fut]
            done += 1
            try:
                result = fut.result()
            except Exception as err:  # noqa: BLE001 - one bad cell must not kill the sweep
                rates[spec["case"]["id"]].append(0.0)
                print(f"[{done}/{len(specs)}] eval-{spec['case']['id']} FAILED: {err}")
                continue
            rates[result["eval_id"]].append(result["pass_rate"])
            flag = f"  ({result['error']})" if result["error"] else ""
            print(
                f"[{done}/{len(specs)}] eval-{result['eval_id']} run-{result['run']}: "
                f"pass_rate={result['pass_rate']}{flag}"
            )

    print(f"\nWrote {workspace}")
    short = []
    for case in cases:
        scored = rates[case["id"]]
        mean = round(sum(scored) / len(scored), 4) if scored else 0.0
        required = case.get("pass_rate", DEFAULT_PASS_RATE)
        verdict = "PASS" if mean >= required else "FAIL"
        print(f"{verdict} eval-{case['id']} {case['name']}: {mean} (needs {required})")
        if mean < required:
            short.append(case["id"])
    return 1 if short else 0


if __name__ == "__main__":
    sys.exit(main())
