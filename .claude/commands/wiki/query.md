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
STANDARDS: `.claude/rules/wiki-layer/wiki-standards.md` — schema and status vocabulary

## Instructions

- Read-only on the wiki, always. No `Write`/`Edit` call ever targets a file under `ai-docs/wiki/` — not a page, not the index, not the log, not even for a good answer.
- Read INDEX first, then open only the pages whose title or type plausibly bears on QUESTION — the smallest relevant set, not every page in a domain.
- Follow a page's `[[wikilinks]]` only when the linked page would materially change or extend the answer. Stop once new links stop adding evidence.
- Every claim in the answer cites the page(s) it came from. A page whose `status` is `disputed` or `superseded` gets flagged inline at the point it's used — never presented as settled, never silently dropped.
- If no page in INDEX bears on QUESTION, say plainly that the wiki doesn't cover it. Never guess, and never fall back to the raw `ai-docs/` mirrors to fill the gap.
- On a seed-only wiki (every domain table empty), report that the wiki has no pages yet — not an error.

## Workflow

1. Read INDEX. Identify the domain(s) and candidate pages matching QUESTION.
2. If no candidates exist (empty tables or no title/type match), skip to Report with the no-coverage case.
3. Open the candidate pages, following their `[[wikilinks]]` per the Instructions.
4. Synthesize an answer in your own words from what the pages say, citing each source page per claim and flagging any non-`current` status inline.
5. Report.

## Report

Give the answer with inline page citations (or the no-coverage statement). Close by naming whether this answer is worth crystallizing — a synthesis not already captured in the wiki — and if so, tell the user to run `/wiki:ingest` on it.
