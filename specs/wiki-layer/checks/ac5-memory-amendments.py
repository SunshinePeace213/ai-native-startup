#!/usr/bin/env python3
"""AC5 — AGENTS.md carries the exact prescribed amendments within the 14-line budget."""

import re
import sys
from pathlib import Path

AGENTS = Path("AGENTS.md")

# The exact prescribed fragments from spec.md ## Interfaces & Contracts. The two
# KB bullets and the durability bullet REPLACE existing single-line bullets
# (net added lines: 0 each); the Wiki Layer section is wholly new.
KB_BULLET_1 = (
    "- `ai-docs/` is the shared KB — the wiki (`ai-docs/wiki/`, compiled synthesis; "
    "catalog: `ai-docs/wiki/index.md`) over cached official docs (mirror catalog: "
    "`ai-docs/index.md`, manifest: `ai-docs/sources.yaml`)."
)
KB_BULLET_2 = (
    "- Start every task wiki-first: check `ai-docs/wiki/index.md` for pages matching "
    "the work, then `ai-docs/index.md` for mirrors; skim a match's summary line "
    "before a full read. Nothing relevant → move on."
)
DURABILITY_BULLET = (
    "- Durability rule: official pages get mirrored via `kb-fetcher` and registered "
    "in `sources.yaml`; synthesis that passes the crystallization gate — cited, "
    "non-duplicative — files into the wiki via `/wiki:ingest`; synthesis that "
    "doesn't stays in that plan's `discovery/research.md`; raw search results go "
    "nowhere."
)
WIKI_SECTION_LINES = [
    "## Wiki Layer",
    "- `ai-docs/wiki/` — LLM-maintained synthesis over the mirrors; domain folders "
    "over one shared schema; `personal/` is gitignored and local-only.",
    "- Operations: `/wiki:ingest`, `/wiki:query`, `/wiki:lint` (weekly routine + "
    "on-demand), `/wiki:status`.",
    "- Standards, schema, lane fit, metrics, archetypes: "
    "[wiki-standards.md](.claude/rules/wiki-layer/wiki-standards.md). Mirrors stay "
    "immutable; ingest reads, never edits them.",
]
TOTAL_BUDGET = 14

FAILURES: list[str] = []


def fail(msg: str) -> None:
    FAILURES.append(msg)


def section(text: str, title: str) -> str | None:
    match = re.search(
        rf"^##\s+{re.escape(title)}\s*$(.*?)(?=^##\s|\Z)",
        text,
        re.MULTILINE | re.DOTALL,
    )
    return match.group(0) if match else None


def main() -> int:
    if not AGENTS.is_file():
        print("FAIL: AGENTS.md missing")
        return 1
    text = AGENTS.read_text(encoding="utf-8")

    file_lines = text.splitlines()

    kb = section(text, "Knowledge Base")
    if kb is None:
        fail("no '## Knowledge Base' section")
    else:
        for name, fragment in (
            ("KB bullet 1 (wiki-over-mirrors)", KB_BULLET_1),
            ("KB bullet 2 (wiki-first task start)", KB_BULLET_2),
            ("durability bullet (crystallization gate)", DURABILITY_BULLET),
        ):
            if fragment not in kb:
                fail(f"Knowledge Base section lacks the exact prescribed {name}")
            elif fragment not in file_lines:
                # Each replaced bullet must occupy exactly one line for the net-0
                # accounting below to hold; a wrapped or extended bullet adds lines.
                fail(f"{name} is not exactly one line in AGENTS.md")
        if KB_BULLET_1 in kb:
            wiki_pos = kb.index("ai-docs/wiki/index.md")
            mirror_matches = [m.start() for m in re.finditer(r"ai-docs/index\.md", kb)]
            if mirror_matches and min(mirror_matches) < wiki_pos:
                fail("within Knowledge Base, the mirror index is named before the wiki index")

    wiki = section(text, "Wiki Layer")
    if wiki is None:
        fail("no '## Wiki Layer' section")
    else:
        for line in WIKI_SECTION_LINES:
            if line not in wiki:
                fail(f"Wiki Layer section lacks the exact prescribed line starting: {line[:60]!r}")
        extra = [
            line for line in wiki.splitlines() if line.strip() and line not in WIKI_SECTION_LINES
        ]
        if extra:
            fail(f"Wiki Layer section carries {len(extra)} unprescribed non-empty line(s)")

        # Budget: the three replaced bullets add 0 net lines (asserted one-line
        # above), so the whole amendment's footprint is the Wiki Layer section as
        # it actually stands in AGENTS.md — its heading plus every line under it.
        added = len(wiki.rstrip().splitlines())
        if added > TOTAL_BUDGET:
            fail(
                f"the '## Wiki Layer' section spans {added} lines in AGENTS.md > "
                f"budget {TOTAL_BUDGET}"
            )

    if FAILURES:
        for message in FAILURES:
            print(f"FAIL: {message}")
        return 1
    print("PASS: AGENTS.md amendments exact and within budget")
    return 0


if __name__ == "__main__":
    sys.exit(main())
