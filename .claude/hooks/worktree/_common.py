"""Shared helpers for the worktree lifecycle hooks in this directory.

Plain importable module -- the sibling hook scripts do ``import _common``
(Python puts the running script's directory on ``sys.path``). These helpers
back the WorktreeCreate/WorktreeRemove lifecycle hooks, and everything here
fails open: a lifecycle hook must never block worktree creation or removal
over plumbing.
"""

import json
import os
import select
import subprocess
import sys
from pathlib import Path

STDIN_TIMEOUT = 5.0


def note(msg: str, hook: str | None = None) -> None:
    """One-line stderr note prefixed with the hook name.

    Default prefix is the running script's stem (e.g. ``js_ts``), so hooks
    need no configuration; pass ``hook`` to override.
    """
    prefix = hook or Path(sys.argv[0]).stem or "auto-format"
    print(f"[{prefix}] {msg}", file=sys.stderr)


def read_payload() -> dict | None:
    """Parse the hook payload JSON from stdin; None on any problem (fail-open).

    Bounded wait: a TTY, empty, unreadable, malformed, or timed-out stdin
    yields None. Expected no-payload cases stay silent; unexpected I/O
    errors and timeouts are noted to stderr.
    """
    try:
        stdin = sys.stdin
        if stdin is None or stdin.closed or stdin.isatty():
            return None
        ready, _, _ = select.select([stdin], [], [], STDIN_TIMEOUT)
        if not ready:
            note(f"no payload on stdin after {STDIN_TIMEOUT:g}s; skipping (fail-open)")
            return None
        raw = stdin.read()
    except Exception as exc:  # noqa: BLE001
        note(f"could not read stdin ({exc}); skipping (fail-open)")
        return None
    if not raw or not raw.strip():
        return None
    try:
        payload = json.loads(raw)
    except ValueError:
        return None  # malformed payload is an expected fail-open case
    return payload if isinstance(payload, dict) else None


def resolve_root() -> Path:
    """Project root: ``$CLAUDE_PROJECT_DIR`` when it is a directory, else script-relative.

    The hooks live at ``<root>/.claude/hooks/worktree/``, so the fallback
    is three directories above this file's own directory.
    """
    env_dir = os.environ.get("CLAUDE_PROJECT_DIR", "").strip()
    if env_dir:
        path = Path(env_dir).expanduser()
        if path.is_dir():
            return path.resolve()
    return Path(__file__).resolve().parents[3]


def run(cmd: list[str], cwd: Path | str | None = None) -> tuple[int, str, str] | None:
    """Run ``cmd``; never raise. Returns ``(exit_code, stdout, stderr)``.

    Returns None when the binary is missing (FileNotFoundError) so callers
    can point at the meta-install skill. Any other launch failure returns
    ``(-1, "", str(exc))``; signal deaths also surface as negative codes,
    so callers treat ``code < 0`` uniformly as infrastructure failure.
    Color-forcing env vars are stripped and NO_COLOR is set so captured
    output stays machine-readable for diagnostics fed back to the agent.
    """
    env = {k: v for k, v in os.environ.items() if k not in ("FORCE_COLOR", "CLICOLOR_FORCE")}
    env["NO_COLOR"] = "1"
    try:
        proc = subprocess.run(
            cmd, cwd=str(cwd) if cwd else None, capture_output=True, text=True, env=env
        )
    except FileNotFoundError:
        return None
    except Exception as exc:  # noqa: BLE001
        return (-1, "", str(exc))
    return (proc.returncode, proc.stdout, proc.stderr)


def tail(text: str, lines: int = 3) -> str:
    """Last ``lines`` lines of ``text``, joined with ' | ' for a one-line note."""
    stripped = text.strip()
    return " | ".join(stripped.splitlines()[-lines:]) if stripped else ""
