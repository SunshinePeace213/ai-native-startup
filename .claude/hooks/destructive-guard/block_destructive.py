#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""PreToolUse guard: cancel destructive Bash commands before they execute.

Reads the hook payload from stdin and, only when ``tool_name == "Bash"`` and
``tool_input.command`` is a non-empty string, evaluates the command against the
flat rule table in ``_common``. Deny matches win: up to three are printed to
stderr as a ``BLOCKED / Why / Fix`` block and the hook exits 2 (deny; stderr is
fed back to Claude). Otherwise, if any ask-tier rule matches, the highest
-priority one is emitted as a ``permissionDecision: "ask"`` JSON object on
stdout (exit 0) so the human approves per call. Everything else -- non-Bash
tools, empty/unreadable/malformed input, our own bugs -- exits 0 (fail-open: a
guard must never wedge unrelated Bash calls). Exit 2 and stdout JSON are never
mixed.

Pure inspection, stdlib only: the guard never executes, shells out, or writes.
"""

import json
import sys

import _common

MAX_COMMAND_BYTES = 64 * 1024  # scan only the first 64 KB of the command


def main() -> int:
    payload = _common.read_payload()
    if payload is None:
        return 0
    if payload.get("tool_name") != "Bash":
        return 0
    tool_input = payload.get("tool_input")
    command = tool_input.get("command") if isinstance(tool_input, dict) else None
    if not isinstance(command, str) or not command.strip():
        return 0

    if len(command) > MAX_COMMAND_BYTES:
        _common.note(
            f"command exceeds {MAX_COMMAND_BYTES} bytes; scanning first {MAX_COMMAND_BYTES} only"
        )
        command = command[:MAX_COMMAND_BYTES]

    deny_matches, ask_matches = _common.evaluate(command)

    if deny_matches:
        blocks = [
            f"[destructive-guard] BLOCKED ({rule.category}/{rule.rule_id}): {rule.message}\n"
            f"Why: {rule.why}\n"
            f"Fix: {rule.fix_hint}"
            for rule in deny_matches[:3]
        ]
        print("\n".join(blocks), file=sys.stderr)
        return 2

    if ask_matches:
        rule = ask_matches[0]
        output = {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "ask",
                "permissionDecisionReason": (
                    f"[destructive-guard] {rule.category}: {rule.message} "
                    "— approve only if intended."
                ),
            }
        }
        print(json.dumps(output))
        return 0

    return 0


if __name__ == "__main__":
    # Fail-open on our own bugs: unexpected errors note to stderr and exit 0
    # (same posture as block_attribution.py). Only a confirmed deny match exits 2.
    try:
        sys.exit(main())
    except Exception as exc:  # noqa: BLE001
        _common.note(f"unexpected error: {exc}")
        sys.exit(0)
