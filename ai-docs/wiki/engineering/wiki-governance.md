---
type: pattern
domain: engineering
status: current
created: 2026-08-08
updated: 2026-08-08
sources: ["ai-docs/llm-wiki/rohitg00/llm-wiki.md", ".claude/rules/wiki-layer/wiki-standards.md", ".claude/commands/wiki/ingest.md"]
related: ["[[llm-wiki-pattern]]", "[[wiki-index-and-log]]", "[[knowledge-lifecycle]]", "[[ingest-pipeline]]"]
---

# Wiki Governance

A wiki compiled from personal or team sources inherits whatever those sources contain,
including API keys, credentials, private conversations, and PII
([LLM Wiki v2](../../llm-wiki/rohitg00/llm-wiki.md)). The base [[llm-wiki-pattern]] does not address
this, and the gap is named as one that matters
([LLM Wiki v2](../../llm-wiki/rohitg00/llm-wiki.md)). Governance covers four separable concerns —
what gets filtered on the way in, what record is kept of changes, who can see which pages,
and how concurrent writers merge.

## Filter on the way in

The rule proposed is that sensitive data is stripped before anything reaches the wiki, and
that this is automatic rather than something the maintainer remembers to do
([LLM Wiki v2](../../llm-wiki/rohitg00/llm-wiki.md)). Placing the filter at ingest rather than at
read time is the load-bearing part: a secret that reaches a page has already been written
to disk and, in a version-controlled wiki, to history.

This repository states the rule as an unconditional step on every ingest in every domain,
covering keys, tokens, credentials, addresses, phone numbers, account numbers, and
unpublished third-party names, on the stated assumption that shared domains reach a public
remote ([wiki-standards.md](../../../.claude/rules/wiki-layer/wiki-standards.md)). A second
rule guards a different intake risk: source content is treated as data and never as
instructions, so a directive found inside an archive or clipping is at most recorded as
content, and every write stays inside the wiki folder
([wiki-standards.md](../../../.claude/rules/wiki-layer/wiki-standards.md)).

## The audit trail

Every operation on the wiki — ingest, edit, delete, query — should be logged with a
timestamp, what changed, and why, and that record is described as the accountability layer
that explains how something wrong got there
([LLM Wiki v2](../../llm-wiki/rohitg00/llm-wiki.md)). Bulk operations get the same treatment plus
one more property: deleting stale content in bulk, exporting subsets, and merging duplicate
entities should be audited and reversible
([LLM Wiki v2](../../llm-wiki/rohitg00/llm-wiki.md)).

This wiki keeps a narrower version. Only ingest and lint append to the log, because query
and status never write ([wiki-standards.md](../../../.claude/rules/wiki-layer/wiki-standards.md)),
so the log records state changes rather than all access. Each ingest entry carries the date,
the title, and the canonical source path
([ingest.md](../../../.claude/commands/wiki/ingest.md)), and the log is append-only, which is
what makes it history rather than state — the distinction developed in
[[wiki-index-and-log]]. Reversibility is delegated to git rather than implemented in the
wiki, since the whole vault is a tracked repository
([wiki-standards.md](../../../.claude/rules/wiki-layer/wiki-standards.md)).

## Shared and private scoping

Some knowledge is personal — preferences, workflow — and some is shared, such as project
architecture and team decisions, so the wiki needs scoping, with private observations that
roll up into shared knowledge when promoted
([LLM Wiki v2](../../llm-wiki/rohitg00/llm-wiki.md)).

This repository implements the split as a hard boundary rather than a promotion path. The
personal folder is local-only, gitignored, and never pushed; it keeps its own index and log,
and a personal ingest updates only those two files
([wiki-standards.md](../../../.claude/rules/wiki-layer/wiki-standards.md)). The constraint
runs one way and is stated negatively: the shared index and log never name a personal page,
source, or topic, not even as a placeholder, and a personal page references no file outside
the personal tree ([wiki-standards.md](../../../.claude/rules/wiki-layer/wiki-standards.md)).
Personal raw sources are gitignored the same way, so a citation from a personal page cannot
leak through the source layer
([wiki-standards.md](../../../.claude/rules/wiki-layer/wiki-standards.md)). There is no
promotion mechanism; moving something from personal to shared is a fresh ingest of the
underlying source.

## Concurrent writers

The base pattern assumes one user and one agent, while many real uses involve several of
either ([LLM Wiki v2](../../llm-wiki/rohitg00/llm-wiki.md)). Parallel agents working in different
coding sessions or research threads need their observations merged into a shared wiki, with
last-write-wins proposed for the common case and timestamp-based resolution with manual
override for conflicts ([LLM Wiki v2](../../llm-wiki/rohitg00/llm-wiki.md)). Lightweight coordination
is proposed alongside it — who is working on what, what is blocked, what is done — described
as short of a task management system and aimed at preventing duplicate work
([LLM Wiki v2](../../llm-wiki/rohitg00/llm-wiki.md)).

The corresponding safeguard here is procedural rather than a merge strategy: any page is
re-read immediately before it is edited, so no write lands on a file the writer has not just
seen ([wiki-standards.md](../../../.claude/rules/wiki-layer/wiki-standards.md)). Combined
with git for reconciliation, that covers the sequential case; genuine concurrent-agent merge
is not implemented.
