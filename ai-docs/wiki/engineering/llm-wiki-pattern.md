---
type: pattern
domain: engineering
status: current
created: 2026-08-07
updated: 2026-08-08
sources: ["ai-docs/llm-wiki/karpathy/llm-wiki.md", "ai-docs/llm-wiki/lucianfialho/graphwiki-pattern.md", "ai-docs/llm-wiki/rohitg00/llm-wiki.md", "ai-docs/llm-wiki/farzaa/wiki-gen-skill.md", ".claude/rules/wiki-layer/wiki-standards.md"]
related: ["[[obsidian-vault]]", "[[rag-vs-compiled-knowledge]]", "[[wiki-index-and-log]]", "[[llm-wiki-instantiations]]", "[[graph-wiki-variant]]", "[[wiki-schema-layer]]", "[[ingest-pipeline]]", "[[knowledge-lifecycle]]", "[[wiki-drift]]", "[[page-writing-standards]]", "[[wiki-governance]]"]
---

# LLM Wiki Pattern

An architecture in which an LLM incrementally builds and maintains a persistent wiki —
a structured, interlinked collection of markdown files — that sits between a reader and the
raw sources ([Karpathy](../../llm-wiki/karpathy/llm-wiki.md)). It is defined against RAG-style
document chat, where the LLM rediscovers knowledge from scratch on every question and
nothing accumulates ([Karpathy](../../llm-wiki/karpathy/llm-wiki.md)); that contrast is worked
through in [[rag-vs-compiled-knowledge]].
The pattern's claim is that the reconciliation work is worth writing down: the pages are
the durable artifact, not the conversation.

The primary statement of the pattern is Andrej Karpathy's "LLM Wiki" gist
([Karpathy](../../llm-wiki/karpathy/llm-wiki.md)). It is written as an
idea file meant to be pasted into an agent — Claude Code, Codex, OpenCode — so the agent
builds the specifics with its user ([Karpathy](../../llm-wiki/karpathy/llm-wiki.md)). The document
is deliberately abstract about directory structure, schema conventions, page formats, and
tooling, on the grounds that all of it depends on the domain and the tools in use
([Karpathy](../../llm-wiki/karpathy/llm-wiki.md)). Everything it describes is presented as optional
and modular ([Karpathy](../../llm-wiki/karpathy/llm-wiki.md)), which is why two instantiations can
diverge on specifics and both still be the pattern.

## Three-layer architecture

Raw sources form the bottom layer and are immutable — the LLM reads from them but never
modifies them ([Karpathy](../../llm-wiki/karpathy/llm-wiki.md)).
The wiki is the maintained layer above them: summaries, entity pages, concept pages,
comparisons, an overview, and a synthesis, a layer the LLM owns entirely
([Karpathy](../../llm-wiki/karpathy/llm-wiki.md)).
The third layer is the schema — a configuration document such as CLAUDE.md or AGENTS.md
stating how the wiki is structured and which workflows to follow, which is what makes the
LLM a disciplined wiki maintainer rather than a generic chatbot
([Karpathy](../../llm-wiki/karpathy/llm-wiki.md)). One extension argues that this layer, not the
pages, is the system's real product, on the grounds that it is what encodes every judgment
the maintainer would otherwise remake on each ingest
([LLM Wiki v2](../../llm-wiki/rohitg00/llm-wiki.md)); [[wiki-schema-layer]] takes up what it holds
and how it co-evolves.

The layer boundary is the load-bearing part. This repository's implementation keeps the
same split: the raw-source layer under `ai-docs/` stays immutable and ingest reads it
without editing, while `ai-docs/wiki/` holds everything the LLM writes
([wiki-standards.md](../../../.claude/rules/wiki-layer/wiki-standards.md)). Its schema
layer is a rule file rather than prose in a prompt — seven required frontmatter fields,
open-ended domains each owning a `schema.md` over one shared spine, and writing standards
([wiki-standards.md](../../../.claude/rules/wiki-layer/wiki-standards.md)).

## The operation loop

Three operations drive the pattern. Ingest reads a new source and integrates it across
existing pages: the LLM reads the source, discusses the takeaways with its user, writes a
summary page, updates the index, updates the entity and concept pages the source touches,
and appends a log entry — one source plausibly reaching 10 to 15 pages
([Karpathy](../../llm-wiki/karpathy/llm-wiki.md)). Karpathy states a preference for
ingesting one source at a time while staying involved, reading the summaries and directing
what to emphasize, while noting batch ingestion with less supervision is available
([Karpathy](../../llm-wiki/karpathy/llm-wiki.md)). The two files ingest always touches, the index
and the log, are covered in [[wiki-index-and-log]]; how the operation splits into a
mechanical half and a compilation half is covered in [[ingest-pipeline]].

Query reads the index first to find relevant pages, drills into them, and synthesizes an
answer with citations; filing good answers back in as new pages is what makes exploration
compound the way ingested sources do ([Karpathy](../../llm-wiki/karpathy/llm-wiki.md)).
Lint is the periodic health check, and its checklist is more specific than
consistency: contradictions between pages, stale claims newer sources have superseded,
orphan pages with no inbound links, concepts mentioned without a page of their own, missing
cross-references, and data gaps a web search could fill
([Karpathy](../../llm-wiki/karpathy/llm-wiki.md)). What lint is sweeping for has a name and a
reported frequency — drift, the maintainer under-updating cross-references and status
during ingest, described as the pattern's most common failure mode in either storage form
([graphwiki](../../llm-wiki/lucianfialho/graphwiki-pattern.md)) — and is treated in [[wiki-drift]].

The three map onto this repository as `/wiki:ingest`, `/wiki:query`, and `/wiki:lint`,
with a fourth read-only reporter, `/wiki:status`
([wiki-standards.md](../../../.claude/rules/wiki-layer/wiki-standards.md)). The write
boundary is drawn between them: only ingest and lint write, and crystallizing a query
answer is itself an ingest
([wiki-standards.md](../../../.claude/rules/wiki-layer/wiki-standards.md)).

## Why the maintenance cost changed

The argument for the pattern is about bookkeeping, not intelligence. The tedious part of
maintaining a knowledge base is not the reading or the thinking but the bookkeeping —
updating cross-references, keeping summaries current, noting when new data contradicts old
claims, holding dozens of pages consistent ([Karpathy](../../llm-wiki/karpathy/llm-wiki.md)).
The corollary is that the pattern's cost sits in upkeep rather than authoring: the
operations that keep pages consistent run forever, while any single page is written once.

Karpathy's claim is that this is why human wikis get abandoned:
the maintenance burden grows faster than the value, and an LLM does not get bored, does not
forget a cross-reference, and can touch 15 files in one pass
([Karpathy](../../llm-wiki/karpathy/llm-wiki.md)). That fixes the division of labor. The human
curates sources, directs the analysis, asks the questions, and decides what it means; the
LLM does the summarizing, cross-referencing, filing, and bookkeeping, and the human rarely
writes the wiki at all ([Karpathy](../../llm-wiki/karpathy/llm-wiki.md)). Karpathy places the idea
in the lineage of Vannevar Bush's 1945 Memex — a private, curated store with associative
trails between documents, where the connections matter as much as the documents — and
identifies unsolved maintenance as the part Bush could not answer
([Karpathy](../../llm-wiki/karpathy/llm-wiki.md)).

## Where the pattern applies

The pattern is domain-agnostic, and the primary source lists the contexts it is meant for:
personal tracking of goals, health, and psychology fed by journal entries and podcast
notes; research deep-dives over weeks or months with an evolving thesis; reading a book by
filing chapters and building out characters, themes, and plot threads; and a team wiki fed
by threads, meeting transcripts, project documents, and customer calls, with humans
optionally reviewing updates ([Karpathy](../../llm-wiki/karpathy/llm-wiki.md)). Competitive
analysis, due diligence, trip planning, course notes, and hobby deep-dives are named as
the same shape ([Karpathy](../../llm-wiki/karpathy/llm-wiki.md)).

The book case is the one with an existing proof at scale. Karpathy points at community fan
wikis such as Tolkien Gateway — thousands of interlinked pages on characters, places,
events, and languages, built by volunteers over years — as the artifact a single reader
could now produce alone while reading
([Karpathy](../../llm-wiki/karpathy/llm-wiki.md)). The common thread across every context is
accumulation: knowledge arriving over time that would otherwise stay scattered
([Karpathy](../../llm-wiki/karpathy/llm-wiki.md)). This repository's domains are open-ended for the
same reason — a folder appears when a context earns one
([wiki-standards.md](../../../.claude/rules/wiki-layer/wiki-standards.md)).

## Reading and writing are separate programs

The maintainer and the reading surface are separate programs over one set of files, and
plain markdown on disk is what allows the separation: the wiki is a git repo of markdown
files, so one program can maintain the folder while a human reads it
([Karpathy](../../llm-wiki/karpathy/llm-wiki.md)). Karpathy runs that arrangement with the agent on
one side and Obsidian on the other, under the framing that Obsidian is the IDE, the LLM is
the programmer, and the wiki is the codebase ([Karpathy](../../llm-wiki/karpathy/llm-wiki.md)). The
reading surface is therefore a choice made independently of the maintainer;
[[obsidian-vault]] covers the one this repository uses and what its graph view contributes
to the health checks in [[wiki-drift]].

## Where instantiations diverge

Independently built implementations agree on the three layers and disagree on nearly
everything below them, which is what the source's own optional-and-modular framing predicts
([Karpathy](../../llm-wiki/karpathy/llm-wiki.md)). They part on storage, on how many
operations the base three grow into, and on how much of the loop fires automatically, and
those choices are presented as rungs on one path rather than as rivals
([LLM Wiki v2](../../llm-wiki/rohitg00/llm-wiki.md)). [[llm-wiki-instantiations]] surveys
the four documented statements of the pattern and where this repository sits among them.
