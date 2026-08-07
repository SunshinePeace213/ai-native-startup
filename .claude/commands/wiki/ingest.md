---
description: Ingest a source into the ai-docs wiki — reads a mirror, local file, or plan artifact, integrates it across wiki pages, and updates the index and log. Use when the user asks to ingest, absorb, file, or crystallize something into the wiki.
argument-hint: <mirror-path | file-or-folder | plan-artifact> [--domain <name>]
model: opus
effort: high
---

# Purpose

Compile a source into the wiki's understanding: read it, integrate it across every page
it belongs on, and leave the domain's index and log current.

## Variables

SOURCE: `$ARGUMENTS` — a mirror path under `ai-docs/`, a local file or folder, or a plan
artifact under `specs/`. `--domain <name>` pins the domain; otherwise infer it from the
content.
STANDARDS: `.claude/rules/wiki-layer/wiki-standards.md` — the page schema, writing
standards, and privacy rules this command writes against.
INDEX + LOG: `ai-docs/wiki/index.md` and `ai-docs/wiki/log.md` for the shared domains;
`ai-docs/wiki/personal/index.md` and `ai-docs/wiki/personal/log.md` for personal.
KEY: the canonical source path — recorded in both the page's `sources:` frontmatter and
the log entry, and the identity a re-run matches on.

## Instructions

- An external URL is not a source. Refuse it and point at `/harness-layer:kb add <url>`:
  a page becomes an immutable mirror before it is ingested.
- Mirrors are read-only — read them, never edit or move them.
- Integrate, never append. One source may touch several pages: create the pages it
  earns, enrich the pages it deepens, and leave each reading as a coherent whole under
  STANDARDS' writing standards and length bounds. Re-read a page immediately before
  editing it.
- Idempotent on KEY. Before writing, search the pages, INDEX, and LOG for that path.
  Present → update those pages in place and bump `updated:`; never add a second page,
  index row, or log entry. A second identical run leaves the tree unchanged.
- A personal ingest touches only the personal index and log. The shared pair never names
  a personal page, source, or topic.
- Strip secrets and PII per STANDARDS before any text lands on a page.
- Every page you touch leaves with all seven frontmatter fields set, `related:`
  consistent with its inline `[[wikilinks]]`, and every claim carrying a citation.
- A claim contradicting an existing one flags both `disputed` on their pages, each
  cross-referencing the other. Nothing is deleted.
- A plan artifact passes the crystallization gate first — cited and non-duplicative.
  Fails either half → decline and say which.

## Workflow

1. Parse SOURCE. External URL → refuse per the Instructions and stop. A folder expands
   to its file list, processed in order.
2. Read STANDARDS, then the target domain's INDEX, then the source itself.
3. Match KEY against existing pages, INDEX rows, and LOG entries — that decides update
   in place versus first ingest.
4. Decide the page set: which existing pages gain a real dimension, which topics carry
   enough material for a page of their own, which are only noted where they already
   appear.
5. Write the pages, re-reading each immediately before the edit.
6. Update the domain's INDEX rows and append its LOG entry:
   `## [YYYY-MM-DD] ingest | <title> | <source-path>`.
7. Batch input: checkpoint every 5 sources — update INDEX and LOG, then re-read the
   index and the pages you are about to touch before continuing.

## Report

- Pages created and pages updated, with paths.
- The index rows and log entry written, or "unchanged" for a repeat ingest.
- Anything flagged `disputed`, declined at the gate, or stripped as secret/PII.
