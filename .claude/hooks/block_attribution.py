#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""PreToolUse guard: deny git/gh commands that carry Claude attribution.

Reads the hook payload from stdin and, only when ``tool_name == "Bash"`` and
``tool_input.command`` contains a word-boundary ``git``/``gh`` token, scans the
command (case-insensitively) for the default Claude attribution forms: the
``Co-Authored-By: Claude`` trailer, the ``Claude-Session:`` trailer, and the
"Generated with [Claude Code]" footer. A match prints the policy to stderr and
exits 2 (deny; stderr is fed back to Claude). Everything else -- including
empty, unreadable, or malformed input -- exits 0 (fail-open: a guard must
never wedge unrelated Bash calls).
"""

import json
import re
import select
import sys

GIT_TOKEN = re.compile(r"\b(git|gh)\b", re.IGNORECASE)
PATTERNS = [
    (
        "'Co-Authored-By: Claude ...' trailer",
        re.compile(r"co-authored-by:\s*claude\b", re.IGNORECASE),
    ),
    (
        "'Claude-Session:' trailer",
        re.compile(r"claude-session:", re.IGNORECASE),
    ),
    (
        "'Generated with [Claude Code]' footer",
        re.compile(r"generated\s+with\s+\[?claude\s+code\]?", re.IGNORECASE),
    ),
]


def note(msg: str) -> None:
    print(f"[block_attribution] {msg}", file=sys.stderr)


def read_command() -> str | None:
    """Extract tool_input.command from a Bash payload on stdin; None otherwise.

    Bounded wait: a TTY or empty/unreadable/malformed stdin yields None
    (fail-open), as does any payload whose tool_name is not "Bash" or whose
    command is not a non-empty string. Expected no-payload cases stay silent;
    unexpected I/O errors are noted to stderr.
    """
    try:
        stdin = sys.stdin
        if stdin is None or stdin.closed or stdin.isatty():
            return None
        ready, _, _ = select.select([stdin], [], [], 5.0)
        if not ready:
            note("no payload on stdin after 5s; allowing (fail-open)")
            return None
        raw = stdin.read()
    except Exception as exc:  # noqa: BLE001
        note(f"could not read stdin ({exc}); allowing (fail-open)")
        return None
    if not raw or not raw.strip():
        return None
    try:
        payload = json.loads(raw)
        if payload.get("tool_name") != "Bash":
            return None
        command = payload.get("tool_input", {}).get("command")
    except (ValueError, AttributeError):
        return None  # malformed payload is an expected fail-open case
    return command if isinstance(command, str) and command.strip() else None


def main() -> int:
    command = read_command()
    if not command or not GIT_TOKEN.search(command):
        return 0
    for form, pattern in PATTERNS:
        if pattern.search(command):
            note(f"Blocked: this git/gh command contains a {form}.")
            note(
                "Repo policy (GIT-COMMIT-PR-MESSAGE.md): commit/PR messages "
                "must carry no Claude attribution."
            )
            note("Fix: remove the attribution line and rerun the command.")
            return 2
    return 0


if __name__ == "__main__":
    # Fail-open on our own bugs: unexpected errors note to stderr and exit 0
    # (same posture as lint.py). Only a confirmed attribution match exits 2.
    try:
        sys.exit(main())
    except Exception as exc:  # noqa: BLE001
        note(f"unexpected error: {exc}")
        sys.exit(0)
