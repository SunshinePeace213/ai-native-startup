---
type: pattern
domain: engineering
status: current
created: 2026-08-07
updated: 2026-08-07
sources: ["specs/wiki-layer/checks/fixtures/article-a-llm-wiki-pattern.md", "specs/wiki-layer/checks/fixtures/article-b-obsidian-vaults.md", ".claude/rules/wiki-layer/wiki-standards.md"]
related: ["[[obsidian-vault]]"]
---

# LLM Wiki Pattern

An architecture in which an LLM incrementally builds and maintains a persistent wiki —
a structured, interlinked set of markdown pages — that sits between a reader and the raw
sources ([article A](../../../specs/wiki-layer/checks/fixtures/article-a-llm-wiki-pattern.md)).
It is defined against retrieve-and-forget document chat, where every question rebuilds
its answer from raw chunks and the synthesis disappears with the session
([article A](../../../specs/wiki-layer/checks/fixtures/article-a-llm-wiki-pattern.md)).
The pattern's claim is that the reconciliation work is worth writing down: the pages are
the durable artifact, not the conversation.

## Three-layer architecture

Raw sources form the bottom layer and are immutable — the LLM reads them and never edits
them ([article A](../../../specs/wiki-layer/checks/fixtures/article-a-llm-wiki-pattern.md)).
The wiki is the maintained layer above them: entity pages, topic syntheses, comparisons,
an index, and a log, all written by the LLM
([article A](../../../specs/wiki-layer/checks/fixtures/article-a-llm-wiki-pattern.md)).
The third layer is the schema — a configuration document stating how the wiki is
structured and which workflows to follow, which is what turns a generic assistant into a
disciplined maintainer
([article A](../../../specs/wiki-layer/checks/fixtures/article-a-llm-wiki-pattern.md)).

The layer boundary is the load-bearing part. This repository's implementation keeps the
same split: the cached mirrors under `ai-docs/` stay immutable and ingest reads them
without editing, while `ai-docs/wiki/` holds everything the LLM writes
([wiki-standards.md](../../../.claude/rules/wiki-layer/wiki-standards.md)). Its schema
layer is a rule file rather than prose in a prompt — seven required frontmatter fields,
six domains over one shared schema, and writing standards the pages are held to
([wiki-standards.md](../../../.claude/rules/wiki-layer/wiki-standards.md)).

## The operation loop

Three operations drive the pattern. Ingest reads a new source and integrates it across
existing pages, so one source can touch a dozen of them
([article A](../../../specs/wiki-layer/checks/fixtures/article-a-llm-wiki-pattern.md)).
Query reads the index, drills into the relevant pages, and synthesizes an answer with
citations; filing good answers back in is what makes exploration compound the way sources
do ([article A](../../../specs/wiki-layer/checks/fixtures/article-a-llm-wiki-pattern.md)).
Lint is the periodic health check, looking for orphan pages, stale claims,
contradictions, and missing cross-references
([article A](../../../specs/wiki-layer/checks/fixtures/article-a-llm-wiki-pattern.md)).

The three map onto this repository as `/wiki:ingest`, `/wiki:query`, and `/wiki:lint`,
with a fourth read-only reporter, `/wiki:status`
([wiki-standards.md](../../../.claude/rules/wiki-layer/wiki-standards.md)). The write
boundary is drawn between them: only ingest and lint write, and crystallizing a query
answer is itself an ingest
([wiki-standards.md](../../../.claude/rules/wiki-layer/wiki-standards.md)).

## Why the maintenance cost changed

The argument for the pattern is about bookkeeping, not intelligence. Its admirers hold
that "the bottleneck of human wikis was never the reading or the thinking — it was the
bookkeeping", and that a maintained wiki became cheap once a machine that does not get
bored could do that work
([article A](../../../specs/wiki-layer/checks/fixtures/article-a-llm-wiki-pattern.md)).
The corollary is that the pattern's cost sits in upkeep rather than authoring: the
operations that keep pages consistent run forever, while any single page is written once.

## Reading and writing are separate programs

Practitioners typically read the result in a dedicated markdown editor while the LLM
edits the same folder — two programs over one set of files
([article A](../../../specs/wiki-layer/checks/fixtures/article-a-llm-wiki-pattern.md)).
Plain markdown on disk is what allows that separation, and it is the reason the reading
surface is a choice made independently of the maintainer.

The [[obsidian-vault]] is the reading surface this repository uses, and it fits the
pattern for a structural reason: a vault is a folder of plain markdown, so nothing about
the pages lives inside the application and another program can maintain the folder while
a human reads it
([article B](../../../specs/wiki-layer/checks/fixtures/article-b-obsidian-vaults.md)).
The pairing also gives the pattern's lint operation a human counterpart — the vault's
graph view exposes hub pages, clusters, and orphans at a glance, which is a visual
complement to the automated consistency check
([article B](../../../specs/wiki-layer/checks/fixtures/article-b-obsidian-vaults.md)).
