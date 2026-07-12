#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""PreToolUse guard: deny Read/Edit/Write/MultiEdit/Grep calls that target a
cataloged sensitive file (the read-side complement to `security-scan/`).

Reads the hook payload from stdin. For Read/Edit/Write/MultiEdit,
`tool_input.file_path` is checked with `_common.match_path` (tilde/relative/
symlink normalization applied inside the engine). For Grep, `tool_input.path`
is checked the same way and `tool_input.glob` is checked with
`_common.match_command_text` (a glob is a pattern/token, not necessarily a
full path). A confirmed match prints the three `_common.denial_lines` to
stderr and exits 2; every other case -- including tools outside this set,
missing/non-string fields, and any plumbing failure -- exits 0 (fail-open).
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
        match = _common.match_command_text(tool_input.get("glob"))
        if match is not None:
            token, rule = match
            return _deny(token, rule)
        return 0

    return 0


if __name__ == "__main__":
    # Fail-open on our own bugs: exit 2 is reserved for a confirmed catalog match.
    try:
        sys.exit(main())
    except Exception as exc:  # noqa: BLE001
        _common.note(f"unexpected error: {exc}")
        sys.exit(0)
