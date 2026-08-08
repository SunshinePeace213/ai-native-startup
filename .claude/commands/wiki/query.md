---
description: Answer a question from the ai-docs wiki — read-only; index → pages → linked pages, synthesized with citations and status flags. Use when the user asks what the wiki knows about a topic.
argument-hint: <question>
model: sonnet
effort: high
---

# Purpose

Answer QUESTION from what the wiki already knows — strictly read-only. Crystallizing a new synthesis is `/wiki:ingest`'s job, not this one's.

## Variables

QUESTION: $ARGUMENTS
INDEX: `ai-docs/wiki/index.md` — the page catalog, by domain
STANDARDS: `.claude/rules/wiki-layer/wiki-standards.md` — schema, status vocabulary, and the `qmd` search contract

## Instructions

- Read-only on the wiki, always. No `Write`/`Edit` call ever targets a file under `ai-docs/wiki/` — not a page, not the index, not the log, not even for a good answer. Mutating the search index counts: never run `qmd update`, `qmd embed`, or any `qmd collection` command here.
- Find candidates with `qmd`, scoped `-c wiki` on every call. This command answers from the synthesis layer only, so `-c sources` and unscoped searches are both wrong.
- Write the query yourself instead of pasting QUESTION into it: `qmd query $'intent: …\nlex: …\nvec: …'` for a concept, `qmd search` for an exact title, term, or citation path. Add `-c wiki` to either.
- Search ranks leads; it never answers. `Read` every page a claim rests on — a snippet is not evidence — and take each page's catalog row from INDEX.
- Follow a page's `[[wikilinks]]` only when the linked page would materially change or extend the answer. Stop once new links stop adding evidence.
- Read a page's embedded images only when the answer turns on what one shows; describe an image only after reading it.
- Every claim in the answer cites the page(s) it came from, and any page whose `status` is not `current` is flagged inline where it is used, per STANDARDS.
- If the search surfaces nothing bearing on QUESTION, say plainly that the wiki doesn't cover it. Never guess, and never fall back to the raw `ai-docs/` sources to fill the gap.
- No `wiki` collection on this machine (a fresh clone indexes nothing): fall back to INDEX and page titles for this run, and tell the user to rebuild the index per STANDARDS. An empty result from a healthy index is no-coverage, not a missing index — `qmd status` separates the two.
- On a seed-only wiki (every domain table empty), report that the wiki has no pages yet — not an error.

## Workflow

1. Search `-c wiki` for candidates per the Instructions, widening or re-phrasing once if the first pass returns nothing.
2. No candidates → skip to Report with the no-coverage case (or the missing-index case).
3. `Read` the candidate pages, following their `[[wikilinks]]` per the Instructions, and read INDEX for their rows.
4. Synthesize an answer in your own words from what the pages say, citing each source page per claim and flagging any non-`current` status inline.
5. Report.

## Report

Give the answer with inline page citations (or the no-coverage statement). Close by naming whether this answer is worth crystallizing — a synthesis not already captured in the wiki — and if so, tell the user to run `/wiki:ingest` on it.
