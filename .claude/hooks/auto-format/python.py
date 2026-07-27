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
fix them. A missing toolchain -- uv itself absent, or uv present but
unable to spawn ruff (fresh clone, project env without ruff) -- notes the
meta-install skill and exits 0; other uv/ruff infrastructure failures also
fail open with a note. A format-stage parse failure is not final -- the
same problem resurfaces as a check diagnostic.
"""

import re
import sys
from pathlib import Path

import _common

EXTS = {".py", ".pyi"}
CONCISE = re.compile(r"^.+:\d+:\d+: ")  # e.g. "src/x.py:1:7: F821 Undefined name `x`"
MISSING = "uv/ruff not installed; skipping (run the meta-install skill)"


def run_ruff(args: list[str], root: Path) -> tuple[int, str, str] | None:
    """Run ruff via uv; None means the toolchain is missing (meta-install case).

    uv itself absent -> FileNotFoundError -> None from run(); uv present but
    unable to spawn ruff (no ruff in the project env or on PATH) -> uv exits
    2 with 'Failed to spawn' on stderr -> also None.
    """
    res = _common.run(["uv", "run", "--no-sync", "ruff", *args], cwd=root)
    if res is None or (res[0] == 2 and "Failed to spawn" in res[2]):
        return None
    return res


def format_one(path: Path, root: Path) -> list[str]:
    """ruff format then ruff check --fix on one path; its diagnostic lines, if any."""
    res = run_ruff(["format", str(path)], root)
    if res is None:
        _common.note(MISSING)
        return []
    # Format failures fall through: ruff check reports parse errors properly.

    res = run_ruff(["check", "--fix", "--output-format", "concise", str(path)], root)
    if res is None:
        _common.note(MISSING)
        return []
    code, out, err = res
    if code == 0:
        return []
    if code == 1:  # ruff: 1 = violations remain; anything else is abnormal
        lines = [line for line in out.splitlines() if CONCISE.match(line)]
        if lines:
            return lines
    _common.note(f"ruff (via uv) exited {code}: {_common.tail(err or out)}")
    return []


def main() -> int:
    pairs = _common.target(EXTS)
    if not pairs:
        return 0

    # A failure on one path must not skip the rest: diagnostics from every
    # path aggregate into one capped report and one exit code.
    all_lines: list[str] = []
    for path, root in pairs:
        all_lines.extend(format_one(path, root))
    if all_lines:
        print(_common.format_diagnostics(all_lines), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    # Fail-open on our own bugs: exit 2 is reserved for confirmed rule violations.
    try:
        sys.exit(main())
    except Exception as exc:  # noqa: BLE001
        _common.note(f"unexpected error: {exc}")
        sys.exit(0)
