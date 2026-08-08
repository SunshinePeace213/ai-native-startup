---
type: comparison
domain: engineering
status: current
created: 2026-08-08
updated: 2026-08-08
sources: ["ai-docs/llm-wiki/karpathy/llm-wiki.md", "ai-docs/llm-wiki/lucianfialho/graphwiki-pattern.md", "ai-docs/llm-wiki/rohitg00/llm-wiki.md", "ai-docs/llm-wiki/farzaa/wiki-gen-skill.md", ".claude/rules/wiki-layer/wiki-standards.md"]
related: ["[[llm-wiki-pattern]]", "[[graph-wiki-variant]]", "[[ingest-pipeline]]", "[[knowledge-lifecycle]]", "[[wiki-drift]]"]
---

# LLM Wiki Instantiations

The [[llm-wiki-pattern]] is published as an idea file meant to be pasted into an agent so
the agent builds the specifics with its user, with everything it describes presented as
optional and modular ([Karpathy](../../llm-wiki/karpathy/llm-wiki.md)). Divergence between
implementations is therefore the expected outcome rather than a sign of disagreement. Four
statements of the pattern are archived here, and the differences between them fall on three
axes.

## The documented statements

The original is an abstract idea file that deliberately declines to specify directory
structure, schema conventions, page formats, and tooling, on the grounds that all of it
depends on the domain and the tools in use
([Karpathy](../../llm-wiki/karpathy/llm-wiki.md)). The other three each fill that space
differently. One is a Claude Code skill specification aimed at personal data — journals,
notes, messages — that expands the three operations into six commands and supplies a
directory taxonomy and a writing style guide
([wiki skill](../../llm-wiki/farzaa/wiki-gen-skill.md)). One replaces markdown with a Neo4j
property graph and is the only statement accompanied by measurements
([graphwiki](../../llm-wiki/lucianfialho/graphwiki-pattern.md)). One extends the original
with lessons from running the pattern across thousands of sessions in a persistent memory
engine for coding agents, framed as what breaks at scale
([LLM Wiki v2](../../llm-wiki/rohitg00/llm-wiki.md)).

All three of the later statements affirm the original's core before departing from it. The
production extension says the three-layer architecture works, the operations cover the
basics, and everything in the original still applies
([LLM Wiki v2](../../llm-wiki/rohitg00/llm-wiki.md)). The graph variant keeps the three
layers and changes only how the middle one is stored
([graphwiki](../../llm-wiki/lucianfialho/graphwiki-pattern.md)).

## Storage, operations, automation

Storage is the first axis. One variant replaces pages with typed nodes and edges and keeps
the prose inside the node ([graphwiki](../../llm-wiki/lucianfialho/graphwiki-pattern.md));
another keeps the pages and layers a graph beside them, on the division that pages are for
reading and the graph is for navigation
([LLM Wiki v2](../../llm-wiki/rohitg00/llm-wiki.md)). Both are compared in
[[graph-wiki-variant]].

Operations is the second. The base three grow a mechanical normalization step ahead of
compilation, and two expansion passes behind it: one that audits and restructures every
existing article, and one that mines the article set for concrete entities that deserve
pages of their own, each run by parallel subagents in batches
([wiki skill](../../llm-wiki/farzaa/wiki-gen-skill.md)). The split between normalization and
compilation is treated in [[ingest-pipeline]].

Automation is the third, and the sharpest criticism of the original lands here: everything
in it is manual, so the human drops a source and tells the LLM to process it, remembers to
run lint, and decides when to file an answer back
([LLM Wiki v2](../../llm-wiki/rohitg00/llm-wiki.md)). The proposed replacement fires on
events — new source, session start, session end, query, memory write, and a schedule — while
leaving curation and direction with the human
([LLM Wiki v2](../../llm-wiki/rohitg00/llm-wiki.md)). The same conclusion is reached
independently from the graph side, where lint is said to belong on cron or CI because the
store stays healthy in proportion to how automatic the check is
([graphwiki](../../llm-wiki/lucianfialho/graphwiki-pattern.md)).

## The choices stage rather than compete

The differences are presented as increments on one path rather than as rival designs. The
staging runs from a minimal wiki of raw sources, pages, an index, and a schema — roughly
what the original describes and explicitly recommended as the starting point — through
lifecycle management, then entity extraction and a knowledge graph, then automation, then
hybrid search and consolidation tiers past a few hundred pages, and finally multi-agent
collaboration ([LLM Wiki v2](../../llm-wiki/rohitg00/llm-wiki.md)). Each rung is credited
with fixing a specific failure: lifecycle prevents a junk drawer, structure surfaces
connections flat pages lose, automation drops the maintenance burden toward zero, and scale
work is what a few hundred pages require
([LLM Wiki v2](../../llm-wiki/rohitg00/llm-wiki.md)). The claim attached is that the pattern
works at every level and the entry point is chosen from need
([LLM Wiki v2](../../llm-wiki/rohitg00/llm-wiki.md)).

This repository sits on the first rung plus part of the second: pages, an index, a log, and
a schema, with the status half of [[knowledge-lifecycle]] implemented and no confidence
scoring, no graph, no hybrid search, and no scheduled automation
([wiki-standards.md](../../../.claude/rules/wiki-layer/wiki-standards.md)).

## Independent reinvention

The variants are not a single lineage. A survey of the original gist's comment thread found
independently built implementations including Obsidian paired with its graph view, hybrids
of NetworkX and ChromaDB, a Ruby gem serving a live graph, and several local-first
applications ([graphwiki](../../llm-wiki/lucianfialho/graphwiki-pattern.md)). What that
discussion converged on is more useful than the inventory: multiple builders independently
named drift and staleness as the dominant failure mode
([graphwiki](../../llm-wiki/lucianfialho/graphwiki-pattern.md)), which is the finding
[[wiki-drift]] is built around. One comment from that thread — that trust should be graded
and made to travel so a stale or disputed page degrades honestly — is credited with the
design decision to propagate status all the way into query answers rather than confining it
to lint output ([graphwiki](../../llm-wiki/lucianfialho/graphwiki-pattern.md)).
