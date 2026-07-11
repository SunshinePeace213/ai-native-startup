"""Shared helpers for the auto-format hooks in this directory.

Plain importable module -- the sibling hook scripts do ``import _common``
(Python puts the running script's directory on ``sys.path``). Everything
here fails open: a hook built on these helpers must never wedge an edit
over plumbing. Exit 2 belongs only to genuine unfixable lint errors, and
that decision stays in the hooks themselves.
"""

import json
import os
import select
import subprocess
import sys
from pathlib import Path

VENDORED_DIRS = {"node_modules", ".venv", "dist"}
DIAGNOSTIC_CAP = 10
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


def read_file_path() -> str | None:
    """``tool_input.file_path`` from the stdin payload; None unless a non-empty string."""
    payload = read_payload()
    if payload is None:
        return None
    tool_input = payload.get("tool_input")
    file_path = tool_input.get("file_path") if isinstance(tool_input, dict) else None
    return file_path if isinstance(file_path, str) and file_path.strip() else None


def resolve_root() -> Path:
    """Project root: ``$CLAUDE_PROJECT_DIR`` when it is a directory, else script-relative.

    The hooks live at ``<root>/.claude/hooks/auto-format/``, so the fallback
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


def is_vendored(file_path: Path | str, root: Path) -> bool:
    """True when ``file_path`` sits under node_modules/.venv/dist INSIDE ``root``.

    Matched on the path relative to the project root so an ancestor
    directory named e.g. ``dist`` outside the repo can't skip every file;
    paths outside the root are never vendored.
    """
    try:
        rel_parts = Path(file_path).resolve().relative_to(root.resolve()).parts
    except ValueError:
        return False  # outside the project: not ours to skip
    return bool(VENDORED_DIRS.intersection(rel_parts))


def format_diagnostics(lines: list[str], cap: int = DIAGNOSTIC_CAP) -> str:
    """Join ``file:line rule message`` lines, capped at ``cap`` plus an "and N more" tail."""
    shown = list(lines[:cap])
    extra = len(lines) - cap
    if extra > 0:
        shown.append(f"... and {extra} more")
    return "\n".join(shown)


def target(exts: set[str]) -> tuple[Path, Path] | None:
    """Shared format-hook guards: ``(file, project root)``, or None to exit 0.

    None for: no/invalid stdin payload, non-matching extension, vendored
    path, or a file deleted before the hook ran (only that case notes).
    """
    file_path = read_file_path()
    if not file_path:
        return None
    path = Path(file_path)
    if path.suffix.lower() not in exts:
        return None
    root = resolve_root()
    if is_vendored(path, root):
        return None
    if not path.is_file():
        note(f"{path} no longer exists; skipping")
        return None
    return path, root
