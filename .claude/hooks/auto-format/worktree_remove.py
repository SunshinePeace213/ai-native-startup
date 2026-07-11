#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""WorktreeRemove hook: remove the worktree and its ``worktree-*`` branch.

Reads the worktree path from stdin JSON (``worktreePath`` per the hooks
reference, or ``worktree_path`` per the reference implementation), records
the checked-out branch, runs ``git worktree remove --force``, and deletes
the branch only when it matches ``worktree-*`` -- a foreign branch checked
out in the worktree is always preserved. A missing path, a non-worktree
directory, or any git error notes to stderr and exits 0 (fail-open); this
hook never deletes anything git does not recognize as a worktree.
"""

import sys
from pathlib import Path

import _common


def main() -> int:
    payload = _common.read_payload()
    if payload is None:
        return 0
    raw_path = payload.get("worktreePath") or payload.get("worktree_path")
    if not isinstance(raw_path, str) or not raw_path.strip():
        _common.note("no worktree path in payload (worktreePath/worktree_path); skipping")
        return 0
    worktree = Path(raw_path.strip())
    if not worktree.is_dir():
        _common.note(f"worktree path {worktree} does not exist; nothing to remove")
        return 0

    # The branch must be read BEFORE removal -- afterwards there is no HEAD to ask.
    branch = None
    res = _common.run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=worktree)
    if res is not None and res[0] == 0:
        branch = res[1].strip()

    root = _common.resolve_root()
    res = _common.run(["git", "worktree", "remove", "--force", str(worktree)], cwd=root)
    if res is None:
        _common.note("git not found; cannot remove worktree")
        return 0
    if res[0] != 0:
        _common.note(f"git worktree remove failed ({res[0]}): {res[2].strip()}")
        return 0

    if branch and branch.startswith("worktree-"):
        res = _common.run(["git", "branch", "-D", branch], cwd=root)
        if res is None or res[0] != 0:
            detail = res[2].strip() if res else "git not found"
            _common.note(f"could not delete branch {branch}: {detail}")
    return 0


if __name__ == "__main__":
    # Fail-open on our own bugs: note to stderr, exit 0, never wedge the session.
    try:
        sys.exit(main())
    except Exception as exc:  # noqa: BLE001
        _common.note(f"unexpected error: {exc}")
        sys.exit(0)
