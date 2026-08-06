#!/usr/bin/env python3
"""AC5 — AGENTS.md carries the wiki-first protocol, crystallization, and registration."""

import sys
from pathlib import Path

AGENTS = Path("AGENTS.md")

FAILURES: list[str] = []


def fail(msg: str) -> None:
    FAILURES.append(msg)


def main() -> int:
    if not AGENTS.is_file():
        print("FAIL: AGENTS.md missing")
        return 1

    text = AGENTS.read_text(encoding="utf-8")
    lower = text.lower()

    # Wiki-first task-start protocol: the wiki index is named, and it is named
    # before the mirror-catalog index in the Knowledge Base section.
    if "ai-docs/wiki/index.md" not in text:
        fail("AGENTS.md never names ai-docs/wiki/index.md — wiki-first protocol absent")
    else:
        wiki_pos = text.index("ai-docs/wiki/index.md")
        mirror_pos = text.index("ai-docs/index.md")
        if mirror_pos < wiki_pos:
            fail("mirror index is named before the wiki index — check order is not wiki-first")

    # Crystallization amendment to the durability rule.
    if "crystalliz" not in lower:
        fail("durability rule carries no crystallization amendment")

    # Layer registration with pointers to the surface.
    if "/wiki:" not in text:
        fail("no /wiki:* command pointer — layer not registered")
    if "wiki-standards.md" not in text:
        fail("no pointer to the wiki-standards rule")

    if FAILURES:
        for message in FAILURES:
            print(f"FAIL: {message}")
        return 1
    print("PASS: AGENTS.md amendments present")
    return 0


if __name__ == "__main__":
    sys.exit(main())
