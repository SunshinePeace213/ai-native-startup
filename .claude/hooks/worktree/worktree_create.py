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
local ``HEAD``; an existing branch is reused), copy gitignored files listed
in ``.worktreeinclude``, seed the worktree's own ``.qmd`` search index from
the project's, then run ``bun install`` and ``uv sync`` inside it so the
format hooks work there. The name must be a plain name -- absolute paths,
separators, and dot segments are rejected so nothing can escape
``.claude/worktrees``. stdout carries exactly the absolute worktree path
and nothing else -- all git/install output is captured or sent to stderr.
Install/copy/index failures log and still print the path; failures that
prevent creation itself note to stderr and exit 0 (fail-open).
"""

import os
import re
import shutil
import sys
from fnmatch import fnmatch
from pathlib import Path

import _common

QMD_ROLE_ENV = {
    "embed": "QMD_EMBED_MODEL",
    "generate": "QMD_GENERATE_MODEL",
    "rerank": "QMD_RERANK_MODEL",
}


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


def copy_worktree_includes(root: Path, worktree: Path) -> None:
    """Copy gitignored files matching ``.worktreeinclude`` into the worktree.

    The hook replaces default creation, so it owns this documented contract
    too. Patterns are matched only against untracked-and-ignored files
    (``git ls-files -oi``), so tracked files are never duplicated. Matching
    is simplified gitignore syntax: a pattern matches a candidate's relative
    path or basename. Every failure notes and continues (fail-open).
    """
    include = root / ".worktreeinclude"
    if not include.is_file():
        return
    try:
        patterns = [
            line.strip()
            for line in include.read_text().splitlines()
            if line.strip() and not line.strip().startswith("#")
        ]
    except OSError as exc:
        _common.note(f"could not read .worktreeinclude ({exc}); skipping includes")
        return
    if not patterns:
        return
    res = _common.run(["git", "ls-files", "-oi", "--exclude-standard"], cwd=root)
    if res is None or res[0] != 0:
        _common.note("could not list gitignored files; skipping .worktreeinclude copy")
        return
    for rel in res[1].splitlines():
        rel = rel.strip()
        if not rel:
            continue
        matched = any(
            fnmatch(rel, pat.lstrip("/")) or fnmatch(Path(rel).name, pat) for pat in patterns
        )
        if not matched:
            continue
        try:
            dest = worktree / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(root / rel, dest)
        except OSError as exc:
            _common.note(f"could not copy {rel} into worktree ({exc})")


def qmd_config_home() -> Path:
    """qmd's global config directory, by its own precedence rules."""
    override = os.environ.get("QMD_CONFIG_DIR", "").strip()
    if override:
        return Path(override)
    xdg = os.environ.get("XDG_CONFIG_HOME", "").strip()
    if xdg:
        return Path(xdg) / "qmd"
    return Path.home() / ".config" / "qmd"


def read_qmd_models(config: Path) -> dict[str, str]:
    """The ``models:`` block of a qmd ``index.yml``, as ``{role: model-uri}``."""
    models: dict[str, str] = {}
    try:
        lines = config.read_text().splitlines()
    except OSError:
        return models
    in_block = False
    for line in lines:
        if line.startswith("models:"):
            in_block = True
            continue
        if in_block:
            if line.strip() and not line.startswith(" "):
                break
            match = re.match(r"\s+(embed|generate|rerank):\s*(\S+)", line)
            if match:
                models[match.group(1)] = match.group(2)
    return models


def seed_qmd_index(root: Path) -> tuple[Path | None, Path | None]:
    """The index to seed a worktree from: the project's ``.qmd``, else the global one.

    ``qmd status`` is asked for the global database path rather than guessing
    at XDG layout, because that is qmd's own answer to the same question.
    """
    local_config = root / ".qmd" / "index.yml"
    if local_config.is_file():
        return (root / ".qmd" / "index.sqlite", local_config)
    res = _common.run(["qmd", "status"], cwd=root)
    if res is None or res[0] != 0:
        return (None, None)
    database = None
    for line in res[1].splitlines():
        if line.startswith("Index:"):
            database = Path(line.split(":", 1)[1].strip())
            break
    config = qmd_config_home() / "index.yml"
    return (database, config if config.is_file() else None)


def bootstrap_qmd_index(root: Path, worktree: Path) -> None:
    """Give the worktree its own qmd index, seeded from the project's.

    qmd resolves its index by walking up from the working directory, so a
    worktree left without its own ``.qmd`` writes its throwaway paths into
    whichever index sits above it -- the project's, or the global one. Seeding
    beats building from scratch because vectors are keyed by content hash, so
    every document the branch has not touched keeps the vector it already had.
    The seed's models are carried over deliberately: a vector's dimension is
    fixed by the model that produced it, and a worktree left to resolve its own
    defaults would reject the very vectors it was just handed.
    """
    vault = worktree / "ai-docs"
    if not vault.is_dir():
        return

    database, config = seed_qmd_index(root)
    try:
        (worktree / ".qmd").mkdir(parents=True, exist_ok=True)
        if database is not None and database.is_file():
            shutil.copy2(database, worktree / ".qmd" / "index.sqlite")
    except OSError as exc:
        _common.note(f"could not seed qmd index ({exc}); skipping index bootstrap")
        return

    # `qmd init` resolves models from the environment and records them in the
    # worktree's index.yml. This process is short-lived and exits right after,
    # so mutating the environment in place is safe.
    if config is not None:
        for role, model in read_qmd_models(config).items():
            os.environ[QMD_ROLE_ENV[role]] = model
    # qmd picks its target directory from $PWD before falling back to the real
    # cwd, and a subprocess `cwd=` does not update $PWD -- without this, `qmd
    # init` would quietly initialise the parent's directory instead.
    os.environ["PWD"] = str(worktree)

    res = _common.run(["qmd", "init"], cwd=worktree)
    if res is None:
        _common.note("qmd not found; skipping index bootstrap (see .claude/scripts/qmd-setup.sh)")
        return
    if res[0] != 0:
        _common.note(f"`qmd init` exited {res[0]}: {_common.tail(res[2] or res[1])}")
        return

    # Re-adding is how this stays idempotent when a worktree path is reused.
    # An absent collection makes remove exit non-zero, which is not a failure.
    for name in ("wiki", "sources"):
        _common.run(["qmd", "collection", "remove", name], cwd=worktree)

    steps = [
        ["qmd", "collection", "add", str(vault / "wiki"), "--name", "wiki", "--mask", "**/*.md"],
        ["qmd", "collection", "add", str(vault), "--name", "sources", "--mask", "!(wiki)/**/*.md"],
        ["qmd", "update"],
        ["qmd", "embed"],
    ]
    for cmd in steps:
        res = _common.run(cmd, cwd=worktree)
        if res is None:
            _common.note(
                "qmd not found; skipping index bootstrap (see .claude/scripts/qmd-setup.sh)"
            )
            return
        if res[0] != 0:
            _common.note(f"`{' '.join(cmd)}` exited {res[0]}: {_common.tail(res[2] or res[1])}")
            return
        # The one failure qmd reports without a non-zero exit, and the one that
        # would otherwise degrade search silently.
        if "dimension mismatch" in (res[1] + res[2]).lower():
            _common.note(
                "qmd embedding dimension mismatch: this worktree's model disagrees with the "
                "index it was seeded from; search results here are incomplete. Re-run "
                ".claude/scripts/qmd-setup.sh in the main checkout, then recreate the worktree."
            )
            return


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
    if "/" in name or "\\" in name or name in {".", ".."}:
        _common.note(f"invalid worktree name {name!r} (must be a plain name); skipping")
        return 0

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

    copy_worktree_includes(root, worktree)
    bootstrap_qmd_index(root, worktree)  # after the includes: they add ai-docs/ content
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
