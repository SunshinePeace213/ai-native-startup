#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""PreToolUse guard: deny Read/Grep/Edit/Write/MultiEdit calls that target a
cataloged sensitive file. This is the file-tool surface of the sensitive-files
catalog (access blocking -- read AND write/tamper); the sibling `security-scan/`
family covers the other concern, scanning secret content the agent writes out.

Reads the hook payload from stdin. For Read/Edit/Write/MultiEdit,
`tool_input.file_path` is checked with `_common.match_path` (tilde/relative/
symlink normalization applied inside the engine). For Grep, `tool_input.path`
is checked the same way and `tool_input.glob` -- a selection pattern, not a
path -- is checked with `_common.match_glob`, a conservative matcher that denies
only globs clearly targeting a cataloged basename family. A confirmed match
prints the three `_common.denial_lines` to stderr and exits 2; every other case
-- including tools outside this set, missing/non-string fields, and any plumbing
failure -- exits 0 (fail-open).
"""

import sys

import _common

FILE_PATH_TOOLS = {"Read", "Edit", "Write", "MultiEdit"}


def _deny(path_or_token: str, rule: _common.Rule) -> int:
    print("\n".join(_common.denial_lines(path_or_token, rule)), file=sys.stderr)
    return 2


def main() -> int:
    payload = _common.read_payload()
    if payload is None:
        return 0
    tool_input = payload.get("tool_input")
    if not isinstance(tool_input, dict):
        return 0
    tool_name = payload.get("tool_name")

    if tool_name in FILE_PATH_TOOLS:
        file_path = tool_input.get("file_path")
        rule = _common.match_path(file_path)
        if rule is not None:
            return _deny(file_path, rule)
        return 0

    if tool_name == "Grep":
        path = tool_input.get("path")
        rule = _common.match_path(path)
        if rule is not None:
            return _deny(path, rule)
        glob = tool_input.get("glob")
        rule = _common.match_glob(glob)
        if rule is not None:
            return _deny(glob, rule)
        return 0

    return 0


def run() -> int:
    """Fail-open wrapper (AC6): a bug in the guard must never wedge a tool call,
    so any unexpected error notes to stderr and returns 0. Exit 2 stays reserved
    for a confirmed catalog match. A named entry (not just the `__main__` block)
    so tests can drive it in-process and prove an injected engine exception exits
    0 -- not 1 (which would wedge the tool) or 2 (a false deny)."""
    try:
        return main()
    except Exception as exc:  # noqa: BLE001
        _common.note(f"unexpected error: {exc}")
        return 0


if __name__ == "__main__":
    sys.exit(run())
