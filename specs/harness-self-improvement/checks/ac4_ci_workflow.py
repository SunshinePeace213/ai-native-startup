# /// script
# requires-python = ">=3.12"
# ///
"""AC4 — .github/workflows/harness-tests.yml triggers on pull_request (types
including 'edited') over exactly the five harness paths, skips on a '[skip-ci]'
PR title, and runs uv run pytest tests/harness-layer via astral-sh/setup-uv.
String asserts on purpose: stdlib-only so the Codex sandbox (no network) can
run it. Run from the repo root."""

import sys
from pathlib import Path

WORKFLOW = Path(".github/workflows/harness-tests.yml")
REQUIRED = [
    "pull_request",
    "edited",  # a late [skip-ci] title edit must re-evaluate the skip
    ".claude/**",
    ".agents/**",
    "tests/**",
    "pyproject.toml",
    "uv.lock",
    "[skip-ci]",
    "contains(",
    "github.event.pull_request.title",
    "astral-sh/setup-uv",
    "uv run pytest tests/harness-layer",
]

if not WORKFLOW.is_file():
    print(f"AC4 FAIL: {WORKFLOW} missing")
    sys.exit(1)
body = WORKFLOW.read_text()
missing = [token for token in REQUIRED if token not in body]
if missing:
    print("AC4 FAIL: workflow missing tokens:\n" + "\n".join(f"  - {t}" for t in missing))
    sys.exit(1)
print("AC4 ok — workflow carries trigger, paths, skip condition, setup-uv, and pytest invocation")
