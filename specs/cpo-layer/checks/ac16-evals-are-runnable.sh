#!/usr/bin/env bash
# AC16 — the non-deterministic surfaces carry evals the repo's harness can actually execute.
# A suite nothing runs cannot produce a reproducible pass rate, so this asserts both the
# committed evals.json schema AND that each suite has a runner that can reach it.
# Run from the repo root. Exit 0 = pass.
set -uo pipefail

root=$(git rev-parse --show-toplevel)
cd "$root" || exit 1

uv run python - <<'PY'
import json
import sys
from pathlib import Path

TARGETS = [
    Path(".claude/skills/studio-layer/studio-client-questions/evals/evals.json"),
    Path(".claude/commands/studio-layer/evals/evals.json"),
]

failures = []

# The commands suite is unreachable by the meta-skills runner: scripts/eval.py requires a
# SKILL.md and run_behavior_eval.py stages into .claude/skills/<name>. Without its own runner
# the suite is prose with a JSON extension, which is the defect this criterion exists to stop.
runner = Path(".claude/scripts/studio-layer/run_command_evals.py")
if not runner.is_file():
    failures.append(f"{runner} is missing — the commands eval suite has no runner that can execute it")

# The skill suite is reached by the meta-skills runner, which resolves its target relative to
# its own directory and refuses one without a SKILL.md.
skill_md = Path(".claude/skills/studio-layer/studio-client-questions/SKILL.md")
if not skill_md.is_file():
    failures.append(f"{skill_md} is missing — the meta-skills runner cannot grade the skill suite without it")

for path in TARGETS:
    if not path.is_file():
        failures.append(f"{path} is missing — the eval tier is unrun without it")
        continue
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        failures.append(f"{path} is not valid JSON: {exc}")
        continue

    if not isinstance(data, dict) or "evals" not in data:
        failures.append(f"{path} has no 'evals' array — not the harness schema")
        continue
    if not data.get("skill_name"):
        failures.append(f"{path} declares no skill_name")

    evals = data.get("evals") or []
    if len(evals) < 2:
        failures.append(f"{path} has {len(evals)} eval case(s); write at least 2")

    for case in evals:
        label = case.get("name") or case.get("id")
        for field in ("id", "name", "prompt"):
            if case.get(field) in (None, ""):
                failures.append(f"{path} case {label!r} is missing '{field}'")
        assertions = case.get("assertions") or []
        if not assertions:
            failures.append(f"{path} case {label!r} has no assertions — it grades nothing")
        for assertion in assertions:
            if not assertion.get("text"):
                failures.append(f"{path} case {label!r} has an assertion with no text")
        # At least one assertion per case must be machine-checkable, or the whole case rests
        # on a human reading prose and the pass rate is not reproducible.
        if assertions and not any(a.get("check") for a in assertions):
            failures.append(
                f"{path} case {label!r} has no executable 'check' — its pass rate is not reproducible"
            )

if failures:
    for message in failures:
        print(f"FAIL: {message}")
    sys.exit(1)

print("AC16 pass: both eval suites are present, harness-shaped, and machine-gradeable")
PY
