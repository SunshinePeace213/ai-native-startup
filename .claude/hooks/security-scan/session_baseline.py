#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""SessionStart hook: records the baseline of already-dirty files and the
current git HEAD into the session state, then prunes stale state files.

The baseline is what makes the Bash tracker (track_bash_writes.py) safe: a
file that's already dirty when the session starts is the user's own
uncommitted work, and Bash edits to it are deliberately never attributed to
the agent (see decisions.md). SessionStart cannot block, so this always
exits 0; a git problem just leaves the baseline empty / last_head absent,
noted to stderr.

Path convention: see _common.py's "Git helpers" section -- baseline paths
are stored absolute, resolved from git's root-relative output against the
project root.
"""

import sys

import _common


def main() -> int:
    payload = _common.read_payload()
    session_id = payload.get("session_id") if payload else None
    if not isinstance(session_id, str) or not session_id.strip():
        return 0  # nothing to key state on

    root = _common.resolve_root()
    state = _common.load_state(root, session_id)

    dirty = _common.git_dirty_paths(root)
    if dirty is None:
        _common.note("git unavailable or not a repo; baseline left empty")
        dirty = []
    state["baseline"] = dirty

    head = _common.git_head(root)
    if head is None:
        _common.note("HEAD unborn or unreadable; last_head left empty")
        head = ""
    state["last_head"] = head

    try:
        _common.save_state(root, session_id, state)
    except Exception as exc:  # noqa: BLE001
        _common.note(f"could not save session state: {exc}")

    try:
        _common.prune_stale_states(root)
    except Exception as exc:  # noqa: BLE001
        _common.note(f"could not prune stale states: {exc}")

    return 0


if __name__ == "__main__":
    # SessionStart always exits 0 -- fail-open on our own bugs too.
    try:
        sys.exit(main())
    except Exception as exc:  # noqa: BLE001
        _common.note(f"unexpected error: {exc}")
        sys.exit(0)
