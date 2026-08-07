---
description: Report ai-docs wiki health at a glance — page counts by domain and type, orphans, disputed pages, last lint, and the expansion-trigger readout.
model: haiku
effort: medium
---

# Purpose

Report the wiki's current health as a read-only readout.

## Variables

INDEX: `ai-docs/wiki/index.md` — page catalog with per-page `Page | Type | Status | Updated` rows, by domain
LOG: `ai-docs/wiki/log.md` — append-only ingest/lint history
RAW: everything under `ai-docs/` outside `wiki/` — the raw-source layer; one archive
per `.md` file, a PDF-conversion folder counting once via its `index.md`
PERSONAL: `ai-docs/wiki/personal/` — local-only domain, present only on this machine when it exists

## Instructions

- Read-only, always. No `Write`/`Edit` call targets any file.
- Count pages by reading each domain's table in INDEX; a domain's type breakdown comes from that table's `Type` column, not a page's frontmatter re-read, unless a count needs disambiguating.
- Orphan count: pages that no `[[wikilink]]` from any other page reaches. A page's own outgoing links do not count, and a missing index row is lint's drift check, not an orphan.
- Disputed count: pages whose INDEX `Status` column reads `disputed`.
- Last lint date: the most recent `## [date] lint | ...` heading in LOG.
- Expansion triggers, each derived from tracked state, never guessed:
  - **absorb** — count RAW archives whose path appears in no wiki page's `sources:` frontmatter. Backlog >10 fires the trigger.
  - **breakdown** — a page name recurring in the `missing-pages:` payload line of 3 or more *consecutive* lint entries in LOG.
  - **cleanup** — the `mechanical-fixes:` payload value trending upward across the last 3 lint entries in LOG.
- absorb is computed on every run — it derives from a RAW file walk and page `sources:` alone, never from LOG. Only breakdown and cleanup can be insufficient history.
- Fewer than 3 lint entries in LOG: report breakdown and cleanup as "insufficient history", not as unfired or errored.
- No lint entries at all: report "no lint yet"; breakdown and cleanup are insufficient history.
- Seed-only wiki (every domain table empty, no lint entries): report zero page counts and "no lint yet" — not an error. absorb still runs, and a seed wiki cites no archive at all, so it fires whenever RAW holds more than 10 archives.
- PERSONAL: check whether the directory exists locally. If it does, report its page count and type breakdown as its own line. If it doesn't, omit the Personal line entirely. Never name a personal page, topic, or source in the report — counts only.

## Workflow

1. Read INDEX; tally page counts by domain and by type from each domain's table, and the disputed count from the `Status` column.
2. Compute the orphan count from inbound links: collect the `[[wikilinks]]` every page points out, then count the pages no other page's set names (read page content only as needed to resolve this).
3. Read LOG; find the last lint date and the ordered list of lint entries with their `missing-pages:` and `mechanical-fixes:` payloads.
4. Walk RAW; count archives whose path is absent from every page's `sources:` list.
5. Evaluate the three triggers per Instructions, respecting the insufficient-history and no-lint-yet cases.
6. Check PERSONAL's local existence; include or omit its line accordingly.
7. Report.

## Report

```text
Wiki status

Pages by domain: <domain: count, ...>
Pages by type: <type: count, ...>
Personal: <count by type — only if ai-docs/wiki/personal/ exists locally>
Orphans: <N>
Disputed: <N>
Last lint: <date, or "no lint yet">

Expansion triggers:
- absorb: <fired (backlog N>10) | not fired (backlog N) — N archives uncited by any wiki page>
- breakdown: <fired (page X in ≥3 consecutive entries) | not fired | insufficient history>
- cleanup: <fired (mechanical-fixes trending up: a, b, c) | not fired | insufficient history>
```
