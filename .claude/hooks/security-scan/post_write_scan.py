#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""PostToolUse gate for Write|Edit|MultiEdit: scans the just-written file and
records it in the session's tracked-file set.

Secret ("block") findings print capped ``file:line rule message``
diagnostics to stderr and exit 2 -- any vulnerability ("warn") findings on
the same file ride along in that same stderr report. Vulnerability findings
alone exit 0 with a single ``hookSpecificOutput.additionalContext`` JSON
object on stdout (the KB non-blocking channel); exit 2 and stdout JSON are
never mixed. No findings, no payload, or no file_path exit 0 silently.

Path convention: ``tool_input.file_path`` arrives already absolute from
Claude Code and is stored/scanned as-is (matching the auto-format hooks'
convention) -- see _common.py's "Git helpers" section for how git-derived
paths are made to match. State updates (load_state/save_state) are
best-effort: any failure there is noted to stderr but never changes the
exit code (fail-open).
"""

import json
import sys

import _common


def main() -> int:
    payload = _common.read_payload()
    if payload is None:
        return 0
    tool_input = payload.get("tool_input")
    file_path = tool_input.get("file_path") if isinstance(tool_input, dict) else None
    if not isinstance(file_path, str) or not file_path.strip():
        return 0

    root = _common.resolve_root()
    findings = _common.scan_file(file_path, root)

    session_id = payload.get("session_id")
    if isinstance(session_id, str) and session_id.strip():
        try:
            state = _common.load_state(root, session_id)
            tracked = set(state.get("tracked", []))
            tracked.add(file_path)
            state["tracked"] = sorted(tracked)
            _common.save_state(root, session_id, state)
        except Exception as exc:  # noqa: BLE001
            _common.note(f"could not update session state: {exc}")

    if not findings:
        return 0

    lines = [_common.finding_line(f) for f in findings]
    if any(f.severity == "block" for f in findings):
        print(_common.format_diagnostics(lines), file=sys.stderr)
        return 2

    output = {
        "hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "additionalContext": _common.format_diagnostics(lines),
        }
    }
    print(json.dumps(output))
    return 0


if __name__ == "__main__":
    # Fail-open on our own bugs: exit 2 is reserved for confirmed secret findings.
    try:
        sys.exit(main())
    except Exception as exc:  # noqa: BLE001
        _common.note(f"unexpected error: {exc}")
        sys.exit(0)
