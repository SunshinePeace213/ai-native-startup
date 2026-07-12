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
project root. The write goes through ``_common.update_state`` (load-mutate-
save under a per-session lock): baseline/last_head are overwritten with the
freshly computed values, but any tracked set already on disk is merged
forward, never clobbered.
"""

import sys

import _common


def main() -> int:
    payload = _common.read_payload()
    session_id = payload.get("session_id") if payload else None
    if not isinstance(session_id, str) or not session_id.strip():
        return 0  # nothing to key state on

    root = _common.resolve_root()

    dirty = _common.git_dirty_paths(root)
    if dirty is None:
        _common.note("git unavailable or not a repo; baseline left empty")
        dirty = []

    head = _common.git_head(root)
    if head is None:
        _common.note("HEAD unborn or unreadable; last_head left empty")
        head = ""

    def _set_baseline(state: dict) -> dict:
        # Overwrite baseline/last_head (freshly computed each SessionStart),
        # but leave tracked as loaded -- never clobber tracked paths a
        # parallel/earlier hook event already recorded for this session.
        state["baseline"] = dirty
        state["last_head"] = head
        return state

    try:
        _common.update_state(root, session_id, _set_baseline)
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
