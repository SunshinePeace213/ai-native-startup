#!/usr/bin/env python3
"""Score a skill across all three layers, cheapest first.

    lint      static checks on SKILL.md — free, always runs
    trigger   does the description fire on the right queries — ~20 x k `claude -p`
    behavior  does the body beat baseline on real tasks — evals x 2 x k `claude -p`

Each layer gates the next, so a skill that fails the free check never spends on
the expensive one. Pass a layer flag to run just that layer.

Usage:
    uv run --with pyyaml python -m scripts.eval <skill-dir>            # dry run
    uv run --with pyyaml python -m scripts.eval <skill-dir> --yes      # execute
    uv run --with pyyaml python -m scripts.eval <skill-dir> --lint     # lint only
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

from scripts.run_eval import isolated_project_root, run_eval
from scripts.utils import parse_skill_md
from scripts.validate import validate

TRIGGER_BAR = 0.8


def layer_lint(skill_dir: Path) -> bool:
    print("── lint ──────────────────────────────────────────")
    fails, warns = validate(str(skill_dir / "SKILL.md"))
    for w in warns:
        print(f"  {w}")
    for f in fails:
        print(f"  {f}")
    if fails:
        print(f"  {len(fails)} failure(s). Fix these before spending on the paid layers.")
        return False
    print(f"  PASS ({len(warns)} warning(s))")
    return True


def layer_trigger(
    skill_dir: Path, repeats: int, model: str | None, workers: int, timeout: int
) -> bool:
    print("\n── trigger ───────────────────────────────────────")
    eval_set_path = skill_dir / "evals" / "trigger-eval.json"
    if not eval_set_path.exists():
        print(f"  SKIP: no {eval_set_path.relative_to(skill_dir)}")
        return True

    eval_set = json.loads(eval_set_path.read_text())
    name, description, _ = parse_skill_md(skill_dir)
    result = run_eval(
        eval_set=eval_set,
        skill_name=name,
        description=description,
        num_workers=workers,
        timeout=timeout,
        project_root=isolated_project_root(),
        runs_per_query=repeats,
        trigger_threshold=0.5,
        model=model,
    )
    summary = result["summary"]
    score = summary["passed"] / summary["total"] if summary["total"] else 0.0
    for r in result["results"]:
        if r["pass"] is None:
            print(f"  UNMEASURED (every run broke): {r['query'][:60]}")
        elif not r["pass"]:
            want = "should trigger" if r["should_trigger"] else "should not trigger"
            errs = f", {r['errors']} errored" if r.get("errors") else ""
            print(f"  MISS ({want}, fired {r['triggers']}/{r['runs']}{errs}): {r['query'][:60]}")
    print(f"  {summary['passed']}/{summary['total']} queries route correctly ({score:.0%})")
    if summary.get("unmeasured"):
        print(f"  {summary['unmeasured']} query(s) unmeasurable — lower --concurrency and rerun")
    if score < TRIGGER_BAR:
        print(f"  Below the {TRIGGER_BAR:.0%} bar — fix the description before behavior evals.")
        return False
    return True


def layer_behavior(skill_dir: Path, args: argparse.Namespace) -> bool:
    print("\n── behavior ──────────────────────────────────────")
    if not (skill_dir / "evals" / "evals.json").exists():
        print("  SKIP: no evals/evals.json")
        return True

    cmd = [
        sys.executable,
        "-m",
        "scripts.run_behavior_eval",
        str(skill_dir),
        "--iteration",
        str(args.iteration),
        "-k",
        str(args.repeats),
        "--concurrency",
        str(args.concurrency),
        "--permission-mode",
        args.permission_mode,
    ]
    if args.model:
        cmd.extend(["--model", args.model])
    if args.yes:
        cmd.append("--yes")
    if subprocess.run(cmd, cwd=Path(__file__).resolve().parent.parent).returncode != 0:
        return False
    if not args.yes:
        return True

    name, _, _ = parse_skill_md(skill_dir)
    workspace = skill_dir.parent / f"{skill_dir.name}-workspace" / f"iteration-{args.iteration}"
    agg = subprocess.run(
        [sys.executable, "-m", "scripts.aggregate_benchmark", str(workspace), "--skill-name", name],
        cwd=Path(__file__).resolve().parent.parent,
    )
    return agg.returncode == 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Score a skill across lint, trigger, and behavior")
    ap.add_argument("skill_dir")
    ap.add_argument("--lint", action="store_true", help="Run the lint layer only")
    ap.add_argument("--trigger", action="store_true", help="Run the trigger layer only")
    ap.add_argument("--behavior", action="store_true", help="Run the behavior layer only")
    ap.add_argument("-k", "--repeats", type=int, default=3)
    ap.add_argument("--iteration", type=int, default=1)
    ap.add_argument("--concurrency", type=int, default=4)
    ap.add_argument("--model", default=None, help="Model alias for the runs under test")
    ap.add_argument("--permission-mode", default="acceptEdits")
    ap.add_argument(
        "--trigger-timeout",
        type=int,
        default=180,
        help="Seconds per trigger query; Claude often does groundwork before consulting a skill",
    )
    ap.add_argument("--yes", action="store_true", help="Execute the paid layers")
    args = ap.parse_args()

    skill_dir = Path(args.skill_dir).resolve()
    if not (skill_dir / "SKILL.md").exists():
        sys.exit(f"No SKILL.md at {skill_dir}")

    chosen = (args.lint, args.trigger, args.behavior)
    run_all = not any(chosen)

    if (run_all or args.lint) and not layer_lint(skill_dir):
        return 1
    if run_all and not args.yes:
        print("\nLint clean. Re-run with --yes to spend on the trigger and behavior layers.")
        return 0
    if (run_all or args.trigger) and not layer_trigger(
        skill_dir, args.repeats, args.model, args.concurrency, args.trigger_timeout
    ):
        return 1
    if (run_all or args.behavior) and not layer_behavior(skill_dir, args):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
