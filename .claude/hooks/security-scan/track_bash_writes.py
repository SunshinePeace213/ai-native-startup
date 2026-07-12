#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""PostToolUse / PostToolUseFailure hook for Bash: tracks files a Bash call
newly dirtied, so the end-of-turn sweep (task #4) can re-scan them.

Registered on both events because a command can write a file and then exit
non-zero -- only the failure event fires in that case. Adds
(current dirty set - baseline) to the tracked set; baseline-dirty files are
never added via this dirty-set path, even if the Bash call touched them,
because attribution to agent vs. user is impossible for uncommitted changes
(see decisions.md -- the never-flag-user-files principle wins).

Separately, when HEAD has moved since the session's last-seen HEAD, this
also unions `git diff --name-only <last_head>..HEAD` -- this covers a file
written *and committed* within one Bash call (the tree is clean afterwards,
so the dirty-set path would miss it). This diff union is NOT filtered by
baseline: a mid-session commit is agent-era by design, and a committed
secret is the highest-value finding to surface. A stored last_head that git
can no longer reach (history rewritten mid-session) fails the diff open
with a note and resets last_head to current HEAD.

Never blocks: always exits 0. Path convention: see _common.py's "Git
helpers" section -- tracked paths are stored absolute, resolved from git's
root-relative output against the project root (matching post_write_scan.py,
which stores the already-absolute tool_input.file_path as-is). The state
merge itself goes through ``_common.update_state`` (load-mutate-save under a
per-session lock) so a concurrent hook event for the same session can't
clobber this one's tracked/last_head update.
"""

import sys

import _common


def main() -> int:
    payload = _common.read_payload()
    if payload is None:
        return 0
    if payload.get("tool_name") != "Bash":
        return 0
    session_id = payload.get("session_id")
    if not isinstance(session_id, str) or not session_id.strip():
        return 0

    root = _common.resolve_root()

    dirty = _common.git_dirty_paths(root)
    if dirty is None:
        _common.note("git unavailable or not a repo; skipping Bash tracking")
        return 0
    head = _common.git_head(root)

    def _merge(state: dict) -> dict:
        baseline = set(state.get("baseline", []))
        tracked = set(state.get("tracked", []))
        tracked |= set(dirty) - baseline

        last_head = state.get("last_head") or ""
        if head is None:
            _common.note("HEAD unborn or unreadable; skipping commit-diff union")
        else:
            if not last_head:
                _common.note("no stored last_head; skipping commit-diff union")
            elif head != last_head:
                diff_paths = _common.git_diff_paths(root, last_head, head)
                if diff_paths is None:
                    _common.note(f"stored last_head {last_head!r} unreachable; resetting to HEAD")
                else:
                    tracked |= set(diff_paths)
            state["last_head"] = head

        state["tracked"] = sorted(tracked)
        return state

    try:
        _common.update_state(root, session_id, _merge)
    except Exception as exc:  # noqa: BLE001
        _common.note(f"could not save session state: {exc}")

    return 0


if __name__ == "__main__":
    # Never blocks -- fail-open on our own bugs too.
    try:
        sys.exit(main())
    except Exception as exc:  # noqa: BLE001
        _common.note(f"unexpected error: {exc}")
        sys.exit(0)
