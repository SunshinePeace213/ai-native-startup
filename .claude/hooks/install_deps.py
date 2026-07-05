#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Install this repo's dev linters (Prettier, markdownlint-cli2, Ruff) from the
committed manifests + lockfiles.

Reused by the ``WorktreeCreate`` hook (fresh worktree) and the ``/meta-install``
command (first contributor checkout). Runs ``bun install`` + ``uv sync`` in the
project root, then warns (never mutates a manifest) if a declared tool is absent.
Always exits 0 so it can never break the caller.
"""

import json
import os
import select
import subprocess
import sys
from pathlib import Path


def warn(msg: str) -> None:
    print(f"[install_deps] {msg}", file=sys.stderr)


def read_payload() -> dict:
    """Read the hook's stdin JSON without ever hanging.

    WorktreeCreate delivers a JSON payload on stdin; /meta-install does not.
    A TTY or an empty/unreadable stdin is treated as "no payload".
    """
    try:
        stdin = sys.stdin
        if stdin is None or stdin.closed or stdin.isatty():
            return {}
        ready, _, _ = select.select([stdin], [], [], 0.5)
        if not ready:
            return {}
        raw = stdin.read()
        if not raw or not raw.strip():
            return {}
        data = json.loads(raw)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def resolve_root(payload: dict) -> Path:
    """Resolve the install target / project root.

    Order: WorktreeCreate payload path (snake_case then camelCase, since the
    classic-schema field name is unverified) -> $CLAUDE_PROJECT_DIR -> the
    script location (``.claude/hooks/install_deps.py`` -> repo root).
    """
    for key in ("worktree_path", "worktreePath"):
        val = payload.get(key)
        if isinstance(val, str) and val.strip():
            path = Path(val).expanduser()
            if path.is_dir():
                return path.resolve()

    env_dir = os.environ.get("CLAUDE_PROJECT_DIR", "").strip()
    if env_dir:
        path = Path(env_dir).expanduser()
        if path.is_dir():
            return path.resolve()

    return Path(__file__).resolve().parents[2]


def run(cmd: list[str], cwd: Path) -> int:
    """Run a subprocess, capturing output; never raise. Returns exit code."""
    try:
        proc = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True)
        if proc.returncode != 0:
            tail = (proc.stderr or proc.stdout or "").strip().splitlines()
            detail = tail[-1] if tail else "no output"
            warn(f"`{' '.join(cmd)}` exited {proc.returncode}: {detail}")
        return proc.returncode
    except FileNotFoundError:
        warn(f"`{cmd[0]}` not found on PATH; skipping")
        return 127
    except Exception as exc:  # noqa: BLE001
        warn(f"`{' '.join(cmd)}` failed: {exc}")
        return 1


def verify_tools(root: Path) -> None:
    """Warn (do NOT mutate any manifest) if a declared tool is unresolvable."""
    for tool in ("prettier", "markdownlint-cli2"):
        if not (root / "node_modules" / ".bin" / tool).exists():
            warn(f"{tool} not resolvable after install (declared in package.json?)")

    try:
        proc = subprocess.run(
            ["uv", "run", "--no-sync", "ruff", "--version"],
            cwd=str(root),
            capture_output=True,
            text=True,
        )
        if proc.returncode != 0:
            warn("ruff not resolvable after install (declared in pyproject.toml?)")
    except Exception as exc:  # noqa: BLE001
        warn(f"could not verify ruff: {exc}")


def install(root: Path) -> None:
    run(["bun", "install"], root)
    run(["uv", "sync"], root)
    verify_tools(root)


def main() -> int:
    root = resolve_root(read_payload())
    print(f"[install_deps] installing dev linters in {root}", file=sys.stderr)
    install(root)
    return 0


if __name__ == "__main__":
    # Exit 0 always; never break the caller.
    try:
        sys.exit(main())
    except Exception as exc:  # noqa: BLE001
        warn(f"unexpected error: {exc}")
        sys.exit(0)
