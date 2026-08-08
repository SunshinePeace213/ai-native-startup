---
type: pattern
domain: engineering
status: current
created: 2026-08-08
updated: 2026-08-08
sources: ["ai-docs/llm-wiki/farzaa/wiki-gen-skill.md", "ai-docs/llm-wiki/rohitg00/llm-wiki.md", "ai-docs/llm-wiki/karpathy/llm-wiki.md", ".claude/commands/wiki/ingest.md"]
related: ["[[llm-wiki-pattern]]", "[[page-writing-standards]]", "[[entity-resolution]]", "[[wiki-drift]]"]
---

# Ingest Pipeline

Two different jobs travel under the name ingest, and one instantiation of the
[[llm-wiki-pattern]] separates them into distinct commands. Getting source data into
uniform markdown is mechanical work explicitly described as needing no LLM intelligence and
handled by a generated Python script; compiling those entries into articles is the step
where understanding happens ([wiki skill](../../llm-wiki/farzaa/wiki-gen-skill.md)). The split
matters because the two halves have different failure modes and different costs — the first
is a parsing problem, the second is a writing problem.

## The mechanical half

The normalization step converts heterogeneous personal data into one markdown file per
logical entry, auto-detecting the format. The handled formats include Day One JSON, Apple
Notes exports, an Obsidian vault, a Notion export, plain text folders, iMessage exports,
CSV, mbox and .eml email, and a Twitter archive, each with its own extraction rules — an
iMessage export groups by conversation and date so one day with one person becomes one
entry, while a CSV turns each row into an entry using column headers as frontmatter fields
([wiki skill](../../llm-wiki/farzaa/wiki-gen-skill.md)). Unknown formats are handled by reading a
sample, working out the structure, and writing a custom parser toward the same target
([wiki skill](../../llm-wiki/farzaa/wiki-gen-skill.md)).

Two properties are stated as requirements rather than niceties. The script must be
idempotent, so running it twice produces the same output
([wiki skill](../../llm-wiki/farzaa/wiki-gen-skill.md)). And the source data directory is marked do
not modify after ingest ([wiki skill](../../llm-wiki/farzaa/wiki-gen-skill.md)), which is the same
immutability rule the base pattern places on raw sources
([Karpathy](../../llm-wiki/karpathy/llm-wiki.md)).

## The absorption half

The compilation step processes entries one at a time and chronologically, and two rules are
marked non-negotiable: read the index before each entry to match it against existing
articles, and re-read every article immediately before updating it
([wiki skill](../../llm-wiki/farzaa/wiki-gen-skill.md)). The controlling question at each update is
what new dimension this entry adds — not whether it confirms or contradicts, but what is
now understood that was not before
([wiki skill](../../llm-wiki/farzaa/wiki-gen-skill.md)). A new facet earns a full section or a rich
paragraph rather than a sentence, integrated so the article still reads as a coherent
whole, and never appended to the bottom
([wiki skill](../../llm-wiki/farzaa/wiki-gen-skill.md)). What that produces is the subject of
[[page-writing-standards]]; which article an entry attaches to is the matching problem in
[[entity-resolution]].

Absorption also has a pattern-detection duty distinct from filing. When the same theme
recurs across multiple entries, that pattern earns its own article, and those concept
articles are named as the ones that make the wiki a map of a mind rather than a contact
list ([wiki skill](../../llm-wiki/farzaa/wiki-gen-skill.md)).

## Checkpoints inside a batch

Batch absorption is interrupted on a fixed interval rather than run to completion. Every 15
entries the loop stops to rebuild the index and the reverse-link file, then runs two audits
([wiki skill](../../llm-wiki/farzaa/wiki-gen-skill.md)). The first counts new articles created in the
last 15 entries and treats zero as evidence of cramming
([wiki skill](../../llm-wiki/farzaa/wiki-gen-skill.md)). The second picks the three most-updated
articles, re-reads each as a whole piece, and asks whether it tells a coherent story or is a
chronological dump, whether its sections are organized by theme, and whether a reader would
learn something non-obvious — with instruction to rewrite any article that reads like an
event log ([wiki skill](../../llm-wiki/farzaa/wiki-gen-skill.md)). The checkpoint also checks for
articles over 150 lines that should be split
([wiki skill](../../llm-wiki/farzaa/wiki-gen-skill.md)).

This repository runs the same idea at a different interval and scope: a batch ingest
checkpoints every 5 sources by updating the index and log, then re-reading the index and
the pages it is about to touch before continuing
([ingest.md](../../../.claude/commands/wiki/ingest.md)).

## Supervised, batched, or event-driven

The three sources sit at different points on how much human presence ingest assumes. The
base pattern states a preference for one source at a time with the human reading summaries
and directing emphasis, while noting batch ingestion with less supervision is available
([Karpathy](../../llm-wiki/karpathy/llm-wiki.md)). The skill spec defaults to a date range —
absorbing the last 30 days unless told otherwise — which is batch by default
([wiki skill](../../llm-wiki/farzaa/wiki-gen-skill.md)).

The third position is that manual triggering is the largest practical gap in the original,
and that the pipeline should be event-driven: auto-ingest on a new source, load relevant
context on session start, compress the session into observations and file insights on
session end, check on each query whether the answer is worth filing back against a quality
threshold, check for contradictions on each memory write, and run lint, consolidation, and
retention decay on a schedule ([LLM Wiki v2](../../llm-wiki/rohitg00/llm-wiki.md)). The boundary it
draws is that the human stays in the loop for curation and direction while the bookkeeping —
named as the part that makes people abandon wikis — is fully automated
([LLM Wiki v2](../../llm-wiki/rohitg00/llm-wiki.md)).

## Repeat ingests

An idempotent normalizer solves re-running the parser but not re-ingesting the same source
into the maintained layer. This repository resolves that by matching the canonical source
path against page frontmatter and log entries, and branching three ways: a first ingest
writes pages and rows, a changed source updates the existing pages and refreshes their
existing rows while appending a new dated log entry, and an identical repeat writes nothing
at all ([ingest.md](../../../.claude/commands/wiki/ingest.md)). The asymmetry between the
index and the log — one refreshed in place, one appended to — is covered in
[[wiki-index-and-log]].
