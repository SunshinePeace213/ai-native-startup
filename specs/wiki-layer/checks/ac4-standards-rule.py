#!/usr/bin/env python3
"""AC4 — the wiki-standards rule is path-scoped and carries the full schema."""

import re
import sys
from pathlib import Path

RULE = Path(".claude/rules/wiki-layer/wiki-standards.md")

CORE_FIELDS = ("type", "domain", "status", "created", "updated", "sources", "related")
STATUS_VALUES = ("current", "superseded", "disputed")
DOMAINS = ("engineering", "business", "development", "books", "articles", "personal")
REQUIRED_TOPICS = (
    "[[",  # wikilink linking rule
    "secret",  # secret/PII stripping obligation
    "lane",  # lane fit
    "metric",  # metrics targets
    "archetype",  # archetype staffing
    "dataview",  # supported plugin set
    "web clipper",
    "marp",
)

FAILURES: list[str] = []


def fail(msg: str) -> None:
    FAILURES.append(msg)


def main() -> int:
    if not RULE.is_file():
        print(f"FAIL: {RULE} missing")
        return 1

    text = RULE.read_text(encoding="utf-8")

    match = re.match(r"\A---\n(.*?)\n---\n", text, re.DOTALL)
    if not match:
        fail("no YAML frontmatter block")
    else:
        frontmatter = match.group(1)
        if "paths:" not in frontmatter:
            fail("frontmatter has no 'paths:' scoping")
        if "ai-docs/wiki/**" not in frontmatter:
            fail("paths scoping does not cover ai-docs/wiki/**")

    lower = text.lower()
    for field in CORE_FIELDS:
        if not re.search(rf"`?{field}`?\s*[:—-]", text) and field not in lower:
            fail(f"core frontmatter field '{field}' not documented")
    for value in STATUS_VALUES:
        if value not in lower:
            fail(f"status value '{value}' not documented")
    for domain in DOMAINS:
        if domain not in lower:
            fail(f"domain '{domain}' not documented")
    for topic in REQUIRED_TOPICS:
        if topic not in lower:
            fail(f"required topic marker {topic!r} not found")

    if FAILURES:
        for message in FAILURES:
            print(f"FAIL: {message}")
        return 1
    print("PASS: wiki-standards rule satisfies its contract")
    return 0


if __name__ == "__main__":
    sys.exit(main())
