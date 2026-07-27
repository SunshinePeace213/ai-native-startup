#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""PostToolUse format hook: ESLint --fix then Prettier --write for JS/TS.

Self-filters to ``.js/.jsx/.ts/.tsx`` via the shared guards (extension,
vendored path, missing file). Unfixable ESLint errors are printed as capped
``file:line rule message`` diagnostics on stderr with exit 2 so the agent
can fix them; every infrastructure failure (missing binaries, config error,
Prettier crash) notes to stderr and exits 0 (fail-open). Files outside the
project are outside ESLint's base path and would be silently ignored, so
they are linted from their own directory with the project config instead.
"""

import json
import sys
from pathlib import Path

import _common

EXTS = {".js", ".jsx", ".ts", ".tsx"}


def eslint_cmd(eslint: Path, path: Path, root: Path) -> tuple[list[str], Path]:
    """The eslint invocation and its cwd; out-of-repo files need the fallback."""
    cmd = [str(eslint), "--fix", "--format", "json"]
    try:
        path.resolve().relative_to(root)
    except ValueError:
        config = root / "eslint.config.mjs"
        return [*cmd, "--config", str(config), str(path)], path.parent
    return [*cmd, str(path)], root


def diagnostics(stdout: str) -> list[str]:
    """Error-severity messages as ``file:line rule message``; raw lines if unparseable."""
    try:
        results = json.loads(stdout)
        return [
            f"{res.get('filePath', '?')}:{msg.get('line', 0)} "
            f"{msg.get('ruleId') or 'fatal'} {msg.get('message', '')}"
            for res in results
            for msg in res.get("messages", [])
            if msg.get("severity") == 2
        ]
    except (ValueError, AttributeError):
        return [line for line in stdout.splitlines() if line.strip()]


def format_one(path: Path, root: Path, eslint: Path, prettier: Path) -> list[str]:
    """ESLint --fix then Prettier --write on one path; its diagnostic lines, if any."""
    cmd, cwd = eslint_cmd(eslint, path, root)
    res = _common.run(cmd, cwd=cwd)
    if res is None or res[0] < 0:
        _common.note(f"could not run eslint: {res[2].strip() if res else 'binary vanished'}")
        return []
    code, out, err = res
    if code == 1:  # eslint: 1 = lint errors remain after --fix
        lines = diagnostics(out)
        if lines:
            return lines
        _common.note(f"eslint exited 1 without diagnostics: {_common.tail(err)}")
        return []
    if code != 0:  # 2 = config or other fatal problem: infrastructure
        _common.note(f"eslint exited {code}: {_common.tail(err or out)}")
        return []

    res = _common.run([str(prettier), "--write", str(path)], cwd=root)
    if res is None or res[0] != 0:
        detail = _common.tail(res[2] or res[1]) if res else "binary vanished"
        _common.note(f"prettier failed after eslint passed: {detail}")
    return []


def main() -> int:
    pairs = _common.target(EXTS)
    if not pairs:
        return 0
    _, root = pairs[0]  # target() pairs every path with the same project root
    eslint = root / "node_modules" / ".bin" / "eslint"
    prettier = root / "node_modules" / ".bin" / "prettier"
    if not eslint.is_file() or not prettier.is_file():
        _common.note("eslint/prettier not installed; skipping (run the meta-install skill)")
        return 0

    # A failure on one path must not skip the rest: diagnostics from every
    # path aggregate into one capped report and one exit code.
    all_lines: list[str] = []
    for path, path_root in pairs:
        all_lines.extend(format_one(path, path_root, eslint, prettier))
    if all_lines:
        print(_common.format_diagnostics(all_lines), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    # Fail-open on our own bugs: exit 2 is reserved for confirmed lint errors.
    try:
        sys.exit(main())
    except Exception as exc:  # noqa: BLE001
        _common.note(f"unexpected error: {exc}")
        sys.exit(0)
