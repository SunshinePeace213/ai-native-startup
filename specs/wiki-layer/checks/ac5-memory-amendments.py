#!/usr/bin/env python3
"""AC5 — AGENTS.md amendments, asserted section by section with a size budget."""

import re
import sys
from pathlib import Path

AGENTS = Path("AGENTS.md")
WIKI_COMMANDS = ("/wiki:ingest", "/wiki:query", "/wiki:lint", "/wiki:status")
WIKI_SECTION_BUDGET = 8  # lines including the heading — the section's share of the ≤14-line total

FAILURES: list[str] = []


def fail(msg: str) -> None:
    FAILURES.append(msg)


def section(text: str, title: str) -> str | None:
    match = re.search(
        rf"^##\s+{re.escape(title)}\s*$(.*?)(?=^##\s|\Z)", text, re.MULTILINE | re.DOTALL
    )
    return match.group(0) if match else None


def main() -> int:
    if not AGENTS.is_file():
        print("FAIL: AGENTS.md missing")
        return 1
    text = AGENTS.read_text(encoding="utf-8")

    kb = section(text, "Knowledge Base")
    if kb is None:
        fail("no '## Knowledge Base' section")
    else:
        if "ai-docs/wiki/index.md" not in kb:
            fail("Knowledge Base section never names ai-docs/wiki/index.md")
        else:
            wiki_pos = kb.index("ai-docs/wiki/index.md")
            mirror_matches = [m.start() for m in re.finditer(r"ai-docs/index\.md", kb)]
            if mirror_matches and min(mirror_matches) < wiki_pos:
                fail("within Knowledge Base, the mirror index is named before the wiki index")
        durability = next((line for line in kb.splitlines() if "Durability rule" in line), None)
        if durability is None:
            fail("Knowledge Base section has no durability-rule bullet")
        else:
            if "crystalliz" not in durability.lower():
                fail("durability rule carries no crystallization amendment")
            if "/wiki:ingest" not in durability:
                fail("durability rule does not route synthesis via /wiki:ingest")

    wiki = section(text, "Wiki Layer")
    if wiki is None:
        fail("no '## Wiki Layer' section")
    else:
        for cmd in WIKI_COMMANDS:
            if cmd not in wiki:
                fail(f"Wiki Layer section does not register {cmd}")
        if "wiki-standards.md" not in wiki:
            fail("Wiki Layer section does not point at the wiki-standards rule")
        lines = [line for line in wiki.splitlines() if line.strip()]
        if len(lines) > WIKI_SECTION_BUDGET:
            fail(f"Wiki Layer section: {len(lines)} lines > budget {WIKI_SECTION_BUDGET}")

    if FAILURES:
        for message in FAILURES:
            print(f"FAIL: {message}")
        return 1
    print("PASS: AGENTS.md amendments present and within budget")
    return 0


if __name__ == "__main__":
    sys.exit(main())
