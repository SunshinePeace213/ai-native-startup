#!/usr/bin/env python3
"""AC2 — wiki seed structure, parsed section by section against the spec contract."""

import json
import re
import sys
from pathlib import Path

SHARED_DOMAINS = ("engineering", "business", "development", "books", "articles")
TABLE_HEADER = re.compile(r"^\|\s*Page\s*\|\s*Type\s*\|\s*Status\s*\|\s*Updated\s*\|", re.MULTILINE)

FAILURES: list[str] = []


def fail(msg: str) -> None:
    FAILURES.append(msg)


def sections_of(text: str) -> dict[str, str]:
    """Split a markdown document into {heading-lower: body} for ## headings."""
    parts = re.split(r"^##\s+(.+)$", text, flags=re.MULTILINE)
    out: dict[str, str] = {}
    for i in range(1, len(parts) - 1, 2):
        out[parts[i].strip().lower()] = parts[i + 1]
    return out


def check_index() -> None:
    index = Path("ai-docs/wiki/index.md")
    if not index.is_file():
        fail("ai-docs/wiki/index.md missing")
        return
    text = index.read_text(encoding="utf-8")
    if not text.lstrip().startswith("# "):
        fail("wiki index.md has no top-level heading")
    sections = sections_of(text)
    for domain in SHARED_DOMAINS:
        if domain not in sections:
            fail(f"wiki index.md has no '## {domain.title()}' section")
        elif not TABLE_HEADER.search(sections[domain]):
            fail(f"'## {domain.title()}' section lacks the Page|Type|Status|Updated table")
    personal = sections.get("personal")
    if personal is None:
        fail("wiki index.md has no '## Personal' section")
    else:
        if "local-only" not in personal.lower() or "personal/index.md" not in personal:
            fail("Personal section is not the local-only pointer to wiki/personal/index.md")
        if TABLE_HEADER.search(personal):
            fail("Personal section must hold only the pointer — no catalog table (privacy leak)")


def check_log() -> None:
    log = Path("ai-docs/wiki/log.md")
    if not log.is_file():
        fail("ai-docs/wiki/log.md missing")
        return
    text = log.read_text(encoding="utf-8")
    contract = re.search(r"##\s*\[YYYY-MM-DD\]\s*<op>\s*\|\s*<title>\s*\|\s*<source-path>", text)
    if not contract:
        fail("log.md does not document '## [YYYY-MM-DD] <op> | <title> | <source-path>'")
    if not re.search(r"ingest\s*\|\s*lint", text):
        fail("log.md does not restrict <op> to ingest|lint")
    if re.search(r"query\s*\|\s*status", text):
        fail("log.md still permits query/status entries — read-only ops must never write")


def check_obsidian() -> None:
    app = Path("ai-docs/.obsidian/app.json")
    if not app.is_file():
        fail("ai-docs/.obsidian/app.json missing")
        return
    try:
        config = json.loads(app.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"app.json is not valid JSON: {exc}")
        return
    if config.get("attachmentFolderPath") != "wiki/assets":
        fail(
            "app.json attachmentFolderPath is "
            f"{config.get('attachmentFolderPath')!r}, expected 'wiki/assets'"
        )
    if config.get("alwaysUpdateLinks") is not True:
        fail("app.json alwaysUpdateLinks is not true")


def main() -> int:
    check_index()
    check_log()
    check_obsidian()
    if FAILURES:
        for message in FAILURES:
            print(f"FAIL: {message}")
        return 1
    print("PASS: wiki seed structure correct")
    return 0


if __name__ == "__main__":
    sys.exit(main())
