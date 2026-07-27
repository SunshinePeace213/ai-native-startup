#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""PostToolUse gate for Write|Edit|MultiEdit (Claude) and apply_patch (Codex):
scans every just-written file and records them in the session's tracked-file
set.

Secret ("block") findings print capped ``file:line rule message``
diagnostics to stderr and exit 2 -- any vulnerability ("warn") findings on
the same files ride along in that same stderr report. Vulnerability findings
alone exit 0 with a single ``hookSpecificOutput.additionalContext`` JSON
object on stdout (the KB non-blocking channel); exit 2 and stdout JSON are
never mixed. No findings, no payload, or no edited path exit 0 silently.

Path convention: ``_common.edited_paths`` yields absolute paths -- Claude's
``tool_input.file_path`` arrives absolute, and a Codex ``apply_patch``
envelope's paths are resolved against the payload's ``cwd``. They are
stored/scanned as-is (matching the auto-format hooks' convention) -- see
_common.py's "Git helpers" section for how git-derived paths are made to
match. State updates go through ``_common.update_state``
(load-mutate-save under a per-session lock, so parallel hook events don't
drop each other's tracked paths): best-effort, any failure there is noted to
stderr but never changes the exit code (fail-open).
"""

import json
import sys

import _common


def main() -> int:
    payload = _common.read_payload()
    if payload is None:
        return 0
    # edited_paths does not de-dupe (one envelope may name a file twice); dedupe
    # here so a repeated path is neither scanned nor reported twice.
    paths = list(dict.fromkeys(_common.edited_paths(payload)))
    if not paths:
        return 0

    root = _common.resolve_root()

    session_id = payload.get("session_id")
    if isinstance(session_id, str) and session_id.strip():

        def _add_tracked(state: dict) -> dict:
            tracked = set(state.get("tracked", []))
            tracked.update(paths)
            state["tracked"] = sorted(tracked)
            return state

        try:
            _common.update_state(root, session_id, _add_tracked)
        except Exception as exc:  # noqa: BLE001
            _common.note(f"could not update session state: {exc}")

    # scan_file fails open per path, so a missing/unreadable file (e.g. a
    # rename's old path) never skips the paths after it.
    findings = [f for path in paths for f in _common.scan_file(path, root)]

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
