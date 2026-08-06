#!/usr/bin/env python3
"""AC2 — wiki seed structure, parsed section by section against the spec contract."""

import json
import re
import sys
from pathlib import Path

SHARED_DOMAINS = ("engineering", "business", "development", "books", "articles")
TABLE_HEADER = re.compile(
    r"^\|\s*Page\s*\|\s*Type\s*\|\s*Status\s*\|\s*Updated\s*\|\s*$", re.MULTILINE
)
TABLE_SEPARATOR = re.compile(r"^\|(\s*-+\s*\|){4}\s*$", re.MULTILINE)

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
        body = sections.get(domain)
        if body is None:
            fail(f"wiki index.md has no '## {domain.title()}' section")
            continue
        if not TABLE_HEADER.search(body):
            fail(
                f"'## {domain.title()}' lacks the exact '| Page | Type | Status | Updated |' header"
            )
        if not TABLE_SEPARATOR.search(body):
            fail(f"'## {domain.title()}' table has no separator row")
    personal = sections.get("personal")
    if personal is None:
        fail("wiki index.md has no '## Personal' section")
    else:
        lines = [line for line in personal.strip().splitlines() if line.strip()]
        if len(lines) != 1:
            fail(f"Personal section must be exactly the pointer line; found {len(lines)} lines")
        pointer = lines[0] if lines else ""
        if "local-only" not in pointer.lower() or "personal/index.md" not in pointer:
            fail("Personal pointer must state local-only and name wiki/personal/index.md")


def check_log() -> None:
    log = Path("ai-docs/wiki/log.md")
    if not log.is_file():
        fail("ai-docs/wiki/log.md missing")
        return
    text = log.read_text(encoding="utf-8")
    ingest_form = re.search(
        r"##\s*\[YYYY-MM-DD\]\s*ingest\s*\|\s*<title>\s*\|\s*<source-path>", text
    )
    if not ingest_form:
        fail("log.md does not document '## [YYYY-MM-DD] ingest | <title> | <source-path>'")
    lint_form = re.search(r"##\s*\[YYYY-MM-DD\]\s*lint\s*\|\s*<scope>\s*\|\s*<summary>", text)
    if not lint_form:
        fail("log.md does not document '## [YYYY-MM-DD] lint | <scope> | <summary>'")
    payload = re.search(r"missing-pages:.*mechanical-fixes:", text)
    if not payload:
        fail("log.md does not document the lint payload line (missing-pages … mechanical-fixes)")
    # The complete allowed writer set is exactly {ingest, lint}.
    op_forms = set(re.findall(r"##\s*\[YYYY-MM-DD\]\s*([a-z]+)\s*\|", text))
    if op_forms and op_forms != {"ingest", "lint"}:
        fail(f"log.md documents writer ops {sorted(op_forms)}; allowed set is exactly ingest, lint")
    if re.search(r"\bquery\b[^\n]*\bwrit", text.lower()):
        pass  # prose may explain read-only ops; entry forms above are the contract
    for forbidden in ("[YYYY-MM-DD] query", "[YYYY-MM-DD] status"):
        if forbidden in text:
            fail(f"log.md documents a '{forbidden}' entry — read-only ops must never write")


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
