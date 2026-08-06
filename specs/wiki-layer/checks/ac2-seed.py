#!/usr/bin/env python3
"""AC2 — wiki seed structure: index.md, log.md, and Obsidian vault config."""

import json
import sys
from pathlib import Path

FAILURES: list[str] = []


def fail(msg: str) -> None:
    FAILURES.append(msg)


def main() -> int:
    index = Path("ai-docs/wiki/index.md")
    if not index.is_file():
        fail("ai-docs/wiki/index.md missing")
    else:
        text = index.read_text(encoding="utf-8")
        if not text.lstrip().startswith("# "):
            fail("wiki index.md has no top-level heading")
        # Domain grouping: the seed documents at least the six agreed domains.
        for domain in ("engineering", "business", "development", "books", "articles", "personal"):
            if domain not in text.lower():
                fail(f"wiki index.md does not mention domain '{domain}'")

    log = Path("ai-docs/wiki/log.md")
    if not log.is_file():
        fail("ai-docs/wiki/log.md missing")
    else:
        text = log.read_text(encoding="utf-8")
        if "## [" not in text:
            fail("wiki log.md does not document the '## [YYYY-MM-DD] <op> | <title>' entry format")

    app = Path("ai-docs/.obsidian/app.json")
    if not app.is_file():
        fail("ai-docs/.obsidian/app.json missing")
    else:
        try:
            config = json.loads(app.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            fail(f"app.json is not valid JSON: {exc}")
        else:
            if config.get("attachmentFolderPath") != "wiki/assets":
                fail(
                    "app.json attachmentFolderPath is "
                    f"{config.get('attachmentFolderPath')!r}, expected 'wiki/assets'"
                )

    if FAILURES:
        for message in FAILURES:
            print(f"FAIL: {message}")
        return 1
    print("PASS: wiki seed structure correct")
    return 0


if __name__ == "__main__":
    sys.exit(main())
