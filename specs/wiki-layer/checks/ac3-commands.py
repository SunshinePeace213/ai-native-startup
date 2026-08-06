#!/usr/bin/env python3
"""AC3 — the /wiki:* command family exists and honors its frontmatter contract."""

import re
import sys
from pathlib import Path

COMMANDS_DIR = Path(".claude/commands/wiki")
EXPECTED = {"ingest", "query", "lint", "status"}
TAKES_ARGS = {"ingest", "query"}
MODEL_ALIASES = {"fable", "opus", "sonnet", "haiku"}
EFFORTS = {"low", "medium", "high", "xhigh", "max"}

FAILURES: list[str] = []


def fail(msg: str) -> None:
    FAILURES.append(msg)


def parse_frontmatter(text: str) -> dict[str, str] | None:
    match = re.match(r"\A---\n(.*?)\n---\n", text, re.DOTALL)
    if not match:
        return None
    fields: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if not line or line.startswith((" ", "\t", "#", "-")):
            continue
        key, sep, value = line.partition(":")
        if sep:
            fields[key.strip()] = value.strip()
    return fields


def main() -> int:
    if not COMMANDS_DIR.is_dir():
        print(f"FAIL: {COMMANDS_DIR} missing")
        return 1

    found = {p.stem for p in COMMANDS_DIR.glob("*.md")}
    for missing in sorted(EXPECTED - found):
        fail(f"command file missing: {COMMANDS_DIR}/{missing}.md")

    for name in sorted(EXPECTED & found):
        path = COMMANDS_DIR / f"{name}.md"
        fm = parse_frontmatter(path.read_text(encoding="utf-8"))
        if fm is None:
            fail(f"{path}: no YAML frontmatter block")
            continue
        if not fm.get("description"):
            fail(f"{path}: frontmatter 'description' missing or empty")
        model = fm.get("model", "")
        if model not in MODEL_ALIASES:
            fail(f"{path}: model {model!r} is not a roster alias {sorted(MODEL_ALIASES)}")
        if fm.get("effort", "") not in EFFORTS:
            fail(f"{path}: effort {fm.get('effort')!r} is not one of {sorted(EFFORTS)}")
        if name in TAKES_ARGS and not fm.get("argument-hint"):
            fail(f"{path}: takes arguments but has no 'argument-hint'")

    query = COMMANDS_DIR / "query.md"
    if query.is_file():
        body = query.read_text(encoding="utf-8")
        if "read-only" not in body.lower():
            fail(f"{query}: body does not declare the operation read-only")

    if FAILURES:
        for message in FAILURES:
            print(f"FAIL: {message}")
        return 1
    print("PASS: /wiki:* command family satisfies its contract")
    return 0


if __name__ == "__main__":
    sys.exit(main())
