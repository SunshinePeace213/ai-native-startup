#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""PostToolUse format hook: markdownlint-cli2 --fix for Markdown.

Self-filters to ``.md/.markdown`` via the shared guards. Rule violations
that survive --fix are real defects: markdownlint's ``file:line rule
message`` finding lines (it prints them to stderr) are capped and relayed
with exit 2 so the agent can fix them. Missing binary or any abnormal
markdownlint exit notes to stderr and exits 0 (fail-open).
"""

import re
import sys

import _common

EXTS = {".md", ".markdown"}
FINDING = re.compile(r"^.+:\d+")  # e.g. "docs/x.md:3 error MD001/heading-increment ..."


def main() -> int:
    tgt = _common.target(EXTS)
    if tgt is None:
        return 0
    path, root = tgt
    mdl = root / "node_modules" / ".bin" / "markdownlint-cli2"
    if not mdl.is_file():
        _common.note("markdownlint-cli2 not installed; skipping (run the meta-install skill)")
        return 0

    res = _common.run([str(mdl), "--fix", str(path)], cwd=root)
    if res is None or res[0] < 0:
        _common.note(f"could not run markdownlint: {res[2].strip() if res else 'binary vanished'}")
        return 0
    code, out, err = res
    if code == 0:
        return 0
    if code == 1:  # markdownlint-cli2: 1 = findings remain after --fix
        lines = [line for line in err.splitlines() if FINDING.match(line)]
        if lines:
            print(_common.format_diagnostics(lines), file=sys.stderr)
            return 2
        _common.note(f"markdownlint exited 1 without findings: {_common.tail(err or out)}")
        return 0
    _common.note(f"markdownlint-cli2 exited {code}: {_common.tail(err or out)}")
    return 0


if __name__ == "__main__":
    # Fail-open on our own bugs: exit 2 is reserved for confirmed rule violations.
    try:
        sys.exit(main())
    except Exception as exc:  # noqa: BLE001
        _common.note(f"unexpected error: {exc}")
        sys.exit(0)
