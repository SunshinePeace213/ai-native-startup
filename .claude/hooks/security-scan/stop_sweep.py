#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Stop / SubagentStop hook: re-scans every file tracked this session and
blocks the turn from ending while a secret finding survives.

Only the session's tracked set is swept -- never the whole working tree.
Tracked paths are stored absolute (see _common.py's "Git helpers" section),
so each one feeds straight into ``scan_file``; a tracked file that was
deleted or moved into a vendored dir degrades gracefully inside the engine.

Secret ("block") findings -> capped ``file:line rule message`` diagnostics
on stderr and exit 2, with any vuln ("warn") findings riding along in the
same report. Per the KB ``stop_hook_active`` contract the sweep blocks at
most once per turn without progress: when the payload carries
``stop_hook_active: true`` it prints a final loud warning naming the
surviving findings and exits 0. Vuln-only findings never block -- a brief
stderr note only (Stop has no additionalContext channel; nothing is ever
written to stdout). Missing/corrupt state, no session_id, or engine
trouble all fail open to exit 0.
"""

import sys

import _common


def main() -> int:
    payload = _common.read_payload()
    if payload is None:
        return 0
    session_id = payload.get("session_id")
    if not isinstance(session_id, str) or not session_id.strip():
        return 0

    root = _common.resolve_root()
    state = _common.load_state(root, session_id)
    tracked = state.get("tracked", [])
    if not tracked:
        return 0

    findings = []
    for path in sorted(tracked):
        findings.extend(_common.scan_file(path, root))
    if not findings:
        return 0

    lines = [_common.finding_line(f) for f in findings]
    if not any(f.severity == "block" for f in findings):
        _common.note("non-blocking vulnerability findings in files touched this session:")
        print(_common.format_diagnostics(lines), file=sys.stderr)
        return 0

    if payload.get("stop_hook_active") is True:
        # Already forced one continuation this turn -- warn loudly, never loop.
        _common.note(
            "SECURITY WARNING: secret findings remain but this stop was already "
            "blocked once (stop_hook_active); allowing the turn to end. FIX THESE:"
        )
        print(_common.format_diagnostics(lines), file=sys.stderr)
        return 0

    print(_common.format_diagnostics(lines), file=sys.stderr)
    return 2


if __name__ == "__main__":
    # Fail-open on our own bugs: exit 2 is reserved for confirmed secret findings.
    try:
        sys.exit(main())
    except Exception as exc:  # noqa: BLE001
        _common.note(f"unexpected error: {exc}")
        sys.exit(0)
