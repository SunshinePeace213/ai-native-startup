#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""PreToolUse guard: deny Bash commands that reference a cataloged sensitive
file/path. This is the Bash-command surface of the same sensitive-files catalog
``file_guard.py`` enforces on the file tools -- both block read AND write/tamper
access; scanning secret content the agent writes lives in ``security-scan/``.

Reads the hook payload from stdin and, only when ``tool_name == "Bash"`` and
``tool_input.command`` is a non-empty string, hands the raw command text to
``_common.match_command_text()``. A match prints the engine's three-line
denial (naming the matched token and its category) to stderr and exits 2;
everything else -- including empty, unreadable, or malformed input, and any
unexpected error -- exits 0 (fail-open: a guard must never wedge unrelated
Bash calls). This is best-effort text matching, not a sandbox: obfuscated
payloads can evade it (see spec.md Non-Goals).
"""

import sys

import _common


def main() -> int:
    payload = _common.read_payload()
    if payload is None or payload.get("tool_name") != "Bash":
        return 0
    tool_input = payload.get("tool_input")
    command = tool_input.get("command") if isinstance(tool_input, dict) else None
    if not isinstance(command, str) or not command.strip():
        return 0
    match = _common.match_command_text(command)
    if match is None:
        return 0
    token, rule = match
    print("\n".join(_common.denial_lines(token, rule)), file=sys.stderr)
    return 2


def run() -> int:
    """Fail-open wrapper (AC6): unexpected errors note to stderr and return 0
    (same posture as block_attribution.py); only a confirmed catalog match
    returns 2. A named entry (not just the `__main__` block) so tests can drive
    it in-process and prove an injected engine exception exits 0 -- not 1 (which
    would wedge the tool) or 2 (a false deny)."""
    try:
        return main()
    except Exception as exc:  # noqa: BLE001
        _common.note(f"unexpected error: {exc}")
        return 0


if __name__ == "__main__":
    sys.exit(run())
