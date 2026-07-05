#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""PostToolUse dispatcher: auto-format the file just written/edited.

Reads the hook's stdin JSON, pulls ``tool_input.file_path``, routes by extension
to Prettier (JS/TS/JSON/CSS), Ruff (Python), or markdownlint (Markdown), fixes in
place, and ALWAYS exits 0 -- it never blocks or denies an edit. A missing tool is a
one-line stderr note and a skip (install is owned by install_deps.py / /meta-install).
"""

import json
import os
import select
import subprocess
import sys
from pathlib import Path

PRETTIER_EXTS = {".ts", ".tsx", ".js", ".jsx", ".json", ".css"}
RUFF_EXTS = {".py", ".pyi"}
MARKDOWN_EXTS = {".md", ".markdown"}
SKIP_SEGMENTS = {"node_modules", ".venv", "dist"}


def note(msg: str) -> None:
    print(f"[lint] {msg}", file=sys.stderr)


def read_file_path() -> str | None:
    """Extract tool_input.file_path from stdin JSON; None on any problem.

    Never hangs: a TTY or empty/unreadable stdin yields None.
    """
    try:
        stdin = sys.stdin
        if stdin is None or stdin.closed or stdin.isatty():
            return None
        ready, _, _ = select.select([stdin], [], [], 0.5)
        if not ready:
            return None
        raw = stdin.read()
        if not raw or not raw.strip():
            return None
        payload = json.loads(raw)
        fp = payload.get("tool_input", {}).get("file_path")
        return fp if isinstance(fp, str) and fp.strip() else None
    except Exception:
        return None


def resolve_root() -> Path:
    env_dir = os.environ.get("CLAUDE_PROJECT_DIR", "").strip()
    if env_dir:
        path = Path(env_dir).expanduser()
        if path.is_dir():
            return path.resolve()
    return Path(__file__).resolve().parents[2]


def run(cmd: list[str], root: Path) -> subprocess.CompletedProcess | None:
    """Run a formatter; capture output, never raise. None => could not launch."""
    try:
        return subprocess.run(cmd, cwd=str(root), capture_output=True, text=True)
    except Exception as exc:  # noqa: BLE001
        note(f"could not run `{' '.join(cmd)}`: {exc}")
        return None


def format_prettier(file_path: str, root: Path) -> None:
    binary = root / "node_modules" / ".bin" / "prettier"
    if not binary.exists():
        note("prettier not installed; skipping (run /meta-install)")
        return
    proc = run([str(binary), "--write", file_path], root)
    if proc is not None and proc.returncode != 0:
        note(f"prettier could not format {file_path}")


def format_ruff(file_path: str, root: Path) -> None:
    fmt = run(["uv", "run", "--no-sync", "ruff", "format", file_path], root)
    if fmt is None:
        return
    if fmt.returncode != 0:
        note("ruff unavailable or format failed; skipping (run /meta-install)")
        return
    check = run(["uv", "run", "--no-sync", "ruff", "check", "--fix", file_path], root)
    if check is not None and check.returncode != 0:
        note(f"ruff: unfixable lint remains in {file_path}")


def format_markdown(file_path: str, root: Path) -> None:
    binary = root / "node_modules" / ".bin" / "markdownlint-cli2"
    if not binary.exists():
        note("markdownlint-cli2 not installed; skipping (run /meta-install)")
        return
    proc = run([str(binary), "--fix", file_path], root)
    if proc is not None and proc.returncode != 0:
        note(f"markdownlint: unfixable issues remain in {file_path}")


def dispatch(file_path: str, root: Path) -> None:
    path = Path(file_path)
    if SKIP_SEGMENTS.intersection(path.parts):
        return
    ext = path.suffix.lower()
    if ext in PRETTIER_EXTS:
        format_prettier(file_path, root)
    elif ext in RUFF_EXTS:
        format_ruff(file_path, root)
    elif ext in MARKDOWN_EXTS:
        format_markdown(file_path, root)
    # Unknown extension: silent no-op.


def main() -> None:
    file_path = read_file_path()
    if not file_path:
        return
    dispatch(file_path, resolve_root())


if __name__ == "__main__":
    # The dispatcher must never block an edit: swallow everything, always exit 0.
    try:
        main()
    except Exception as exc:  # noqa: BLE001
        note(f"unexpected error: {exc}")
    sys.exit(0)
