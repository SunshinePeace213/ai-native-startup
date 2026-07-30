#!/usr/bin/env bash
# AC16 — the non-deterministic surfaces carry evals the repo's harness can actually execute.
# A markdown rubric nothing runs cannot produce a reproducible pass rate, so this asserts the
# committed evals.json schema rather than the presence of prose.
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
