#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""PostToolUse format hook: Prettier --write for JSON and YAML.

Self-filters to ``.json/.jsonc/.yaml/.yml`` via the shared guards. YAML
rides this hook because Prettier -- not markdownlint -- is the tool that
formats it. Parse errors (Prettier names the offending file on stderr) are
real defects: capped diagnostics + exit 2. Everything else -- missing
binary, config trouble, crashes -- notes to stderr and exits 0 (fail-open).
"""

import sys

import _common

EXTS = {".json", ".jsonc", ".yaml", ".yml"}


def main() -> int:
    tgt = _common.target(EXTS)
    if tgt is None:
        return 0
    path, root = tgt
    prettier = root / "node_modules" / ".bin" / "prettier"
    if not prettier.is_file():
        _common.note("prettier not installed; skipping (run the meta-install skill)")
        return 0

    res = _common.run([str(prettier), "--write", str(path)], cwd=root)
    if res is None or res[0] < 0:
        _common.note(f"could not run prettier: {res[2].strip() if res else 'binary vanished'}")
        return 0
    code, _, err = res
    if code == 0:
        return 0
    # A genuine parse error names the offending file AND the parser's
    # SyntaxError on the same stderr line (JSON and YAML alike). Config or
    # tooling failures may also name the file ("Invalid configuration for
    # file ...") but never with that marker -- those are infrastructure.
    lines = [line for line in err.splitlines() if path.name in line and "SyntaxError" in line]
    if lines:
        print(_common.format_diagnostics(lines), file=sys.stderr)
        return 2
    _common.note(f"prettier exited {code}: {_common.tail(err)}")
    return 0


if __name__ == "__main__":
    # Fail-open on our own bugs: exit 2 is reserved for confirmed parse errors.
    try:
        sys.exit(main())
    except Exception as exc:  # noqa: BLE001
        _common.note(f"unexpected error: {exc}")
        sys.exit(0)
