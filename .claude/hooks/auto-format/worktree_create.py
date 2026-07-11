#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""WorktreeCreate hook: create the worktree and install its formatter deps.

Registering this hook REPLACES Claude Code's default worktree creation, so
it owns the whole contract: read the worktree name from stdin JSON
(``worktreeName`` per the hooks reference, or ``name`` per the reference
implementation), ``git worktree add`` at ``<root>/.claude/worktrees/<name>``
on branch ``worktree-<name>`` based on the origin default branch (fallback:
local ``HEAD``; an existing branch is reused), then run ``bun install`` and
``uv sync`` inside it so the format hooks work there. stdout carries exactly
the absolute worktree path and nothing else -- all git/install output is
captured or sent to stderr. Install failures log and still print the path;
failures that prevent creation itself note to stderr and exit 0 (fail-open).
"""

import sys
from pathlib import Path

import _common


def detect_base(root: Path) -> str:
    """Base ref for new branches: the origin default branch, else local HEAD."""
    _common.run(["git", "fetch", "origin"], cwd=root)  # best effort; offline is fine
    res = _common.run(["git", "symbolic-ref", "--short", "refs/remotes/origin/HEAD"], cwd=root)
    if res is not None and res[0] == 0 and res[1].strip():
        return res[1].strip()  # e.g. "origin/main"
    return "HEAD"


def branch_exists(root: Path, branch: str) -> bool:
    res = _common.run(["git", "rev-parse", "--verify", "--quiet", f"refs/heads/{branch}"], cwd=root)
    return res is not None and res[0] == 0


def install_dependencies(worktree: Path) -> None:
    """bun install + uv sync inside the worktree; failures log and never abort."""
    for cmd in (["bun", "install"], ["uv", "sync"]):
        res = _common.run(cmd, cwd=worktree)
        if res is None:
            _common.note(f"{cmd[0]} not found; skipping install (run the meta-install skill)")
        elif res[0] != 0:
            _common.note(
                f"`{' '.join(cmd)}` exited {res[0]} in {worktree}: {_common.tail(res[2] or res[1])}"
            )


def main() -> int:
    payload = _common.read_payload()
    if payload is None:
        return 0
    name = payload.get("worktreeName") or payload.get("name")
    if not isinstance(name, str) or not name.strip():
        _common.note("no worktree name in payload (worktreeName/name); skipping")
        return 0
    name = name.strip()

    root = _common.resolve_root()
    worktree = root / ".claude" / "worktrees" / name
    branch = f"worktree-{name}"

    if branch_exists(root, branch):
        res = _common.run(["git", "worktree", "add", str(worktree), branch], cwd=root)
    else:
        base = detect_base(root)
        res = _common.run(["git", "worktree", "add", "-b", branch, str(worktree), base], cwd=root)
    if res is None:
        _common.note("git not found; cannot create worktree")
        return 0
    if res[0] != 0:
        _common.note(f"git worktree add failed ({res[0]}): {res[2].strip()}")
        return 0

    install_dependencies(worktree)
    print(worktree)  # the contract: stdout is exactly the absolute path
    return 0


if __name__ == "__main__":
    # Fail-open on our own bugs: note to stderr, exit 0, never wedge the session.
    try:
        sys.exit(main())
    except Exception as exc:  # noqa: BLE001
        _common.note(f"unexpected error: {exc}")
        sys.exit(0)
