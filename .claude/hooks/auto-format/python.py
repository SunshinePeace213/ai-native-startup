#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""PostToolUse format hook: ruff format then ruff check --fix for Python.

Self-filters to ``.py/.pyi`` via the shared guards, running ruff through
``uv run --no-sync`` so the project venv's pinned ruff does the work.
Violations that survive --fix are real defects: concise ``file:line:col:
CODE message`` lines are capped and relayed with exit 2 so the agent can
fix them. uv/ruff infrastructure failures (missing tool, no project, ruff
config error) note to stderr and exit 0 (fail-open). A format-stage parse
failure is not final -- the same problem resurfaces as a check diagnostic.
"""

import re
import sys

import _common

EXTS = {".py", ".pyi"}
CONCISE = re.compile(r"^.+:\d+:\d+: ")  # e.g. "src/x.py:1:7: F821 Undefined name `x`"
MISSING = "uv not found; skipping (run the meta-install skill)"


def main() -> int:
    tgt = _common.target(EXTS)
    if tgt is None:
        return 0
    path, root = tgt

    res = _common.run(["uv", "run", "--no-sync", "ruff", "format", str(path)], cwd=root)
    if res is None:
        _common.note(MISSING)
        return 0
    # Format failures fall through: ruff check reports parse errors properly.

    check = ["uv", "run", "--no-sync", "ruff", "check", "--fix", "--output-format", "concise"]
    res = _common.run([*check, str(path)], cwd=root)
    if res is None:
        _common.note(MISSING)
        return 0
    code, out, err = res
    if code == 0:
        return 0
    if code == 1:  # ruff: 1 = violations remain; anything else is abnormal
        lines = [line for line in out.splitlines() if CONCISE.match(line)]
        if lines:
            print(_common.format_diagnostics(lines), file=sys.stderr)
            return 2
    _common.note(f"ruff (via uv) exited {code}: {_common.tail(err or out)}")
    return 0


if __name__ == "__main__":
    # Fail-open on our own bugs: exit 2 is reserved for confirmed rule violations.
    try:
        sys.exit(main())
    except Exception as exc:  # noqa: BLE001
        _common.note(f"unexpected error: {exc}")
        sys.exit(0)
