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
fed back to Claude) -- identically under Claude and Codex. Otherwise, if any
ask-tier rule matches: under Codex (``_common.hook_host() == "codex"``) the
ask tier denies too, printing the same BLOCKED/Why/Fix shape (using each
rule's Codex-specific fix line) and exiting 2 -- Codex has no
``permissionDecision: "ask"`` support and would run the command anyway.
Under any other host, the highest-priority ask match is emitted as a
``permissionDecision: "ask"`` JSON object on stdout (exit 0) so the human
approves per call. Everything else -- non-Bash tools, empty/unreadable/
malformed input, our own bugs -- exits 0 (fail-open: a guard must never wedge
unrelated Bash calls). Exit 2 and stdout JSON are never mixed.

Pure inspection, stdlib only: the guard never executes, shells out, or writes.
"""

import json
import sys
from collections.abc import Callable

import _common

MAX_COMMAND_BYTES = 64 * 1024  # scan only the first 64 KB of the command


def _format_blocked(rules: list[_common.Rule], fix_of: Callable[[_common.Rule], str]) -> str:
    """Render up to three BLOCKED/Why/Fix blocks plus a remainder line.

    Shared by the deny path and the Codex ask-tier-deny path so both stderr
    diagnostics stay byte-for-byte identical in shape; ``fix_of`` picks which
    fix text a rule contributes (its deny-tier ``fix_hint``, or an ask rule's
    host-neutral ``codex_fix_hint``).
    """
    blocks = [
        f"[destructive-guard] BLOCKED ({rule.category}/{rule.rule_id}): {rule.message}\n"
        f"Why: {rule.why}\n"
        f"Fix: {fix_of(rule)}"
        for rule in rules[:3]
    ]
    extra = len(rules) - 3
    if extra > 0:
        blocks.append(f"[destructive-guard] ... and {extra} more rule(s) matched")
    return "\n".join(blocks)


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

    encoded = command.encode("utf-8", errors="replace")
    if len(encoded) > MAX_COMMAND_BYTES:
        _common.note(
            f"command exceeds {MAX_COMMAND_BYTES} bytes; scanning first {MAX_COMMAND_BYTES} only"
        )
        # Cap on ENCODED bytes, not code points; decode back dropping any partial
        # multibyte char left at the truncation boundary (fail-open: never raises).
        command = encoded[:MAX_COMMAND_BYTES].decode("utf-8", errors="ignore")

    deny_matches, ask_matches = _common.evaluate(command)

    if deny_matches:
        print(_format_blocked(deny_matches, lambda rule: rule.fix_hint), file=sys.stderr)
        return 2

    if ask_matches:
        if _common.hook_host() == "codex":
            print(
                _format_blocked(ask_matches, lambda rule: rule.codex_fix_hint),
                file=sys.stderr,
            )
            return 2

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
