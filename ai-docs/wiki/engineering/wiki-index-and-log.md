---
type: pattern
domain: engineering
status: disputed
created: 2026-08-08
updated: 2026-08-08
sources: ["ai-docs/llm-wiki/karpathy/llm-wiki.md", "ai-docs/llm-wiki/farzaa/wiki-gen-skill.md", "ai-docs/llm-wiki/rohitg00/llm-wiki.md", ".claude/rules/wiki-layer/wiki-standards.md", ".claude/commands/wiki/ingest.md"]
related: ["[[llm-wiki-pattern]]", "[[rag-vs-compiled-knowledge]]", "[[wiki-governance]]", "[[entity-resolution]]", "[[ingest-pipeline]]"]
---

# Wiki Index and Log

Two files carry navigation in an LLM-maintained wiki, and they do different jobs: the
index is content-oriented and the log is chronological
([Karpathy](../../llm-wiki/karpathy/llm-wiki.md)). Both are special-cased in the
[[llm-wiki-pattern]] because both are maintained by the LLM as a side effect of every
ingest, not written by the reader.

## The index is the retrieval mechanism

The index is a catalog of everything in the wiki: each page listed with a link, a one-line
summary, optional metadata such as date or source count, and organized by category
([Karpathy](../../llm-wiki/karpathy/llm-wiki.md)). It is updated on every ingest, and a query reads
it first to find the relevant pages before drilling into them
([Karpathy](../../llm-wiki/karpathy/llm-wiki.md)). That read-index-then-drill loop is what stands
in for embedding-based retrieval at moderate scale, and it is reported to work well up to
roughly 100 sources and hundreds of pages ([Karpathy](../../llm-wiki/karpathy/llm-wiki.md))
*[disputed — a production account puts the ceiling at 100 to 200 pages and calls hybrid
search mandatory past it; see [[rag-vs-compiled-knowledge]]]* — the trade-off examined in
[[rag-vs-compiled-knowledge]]. Where the ceiling actually falls decides whether an index
file is a permanent mechanism or a stage, and the two published figures disagree by roughly
an order of magnitude at the top end.

This repository's `ai-docs/wiki/index.md` carries one table per domain, with page, type,
status, and updated date per row. Keeping it current is a stated metric rather than a
convention: 100% of ingests must update the index and the log
([wiki-standards.md](../../../.claude/rules/wiki-layer/wiki-standards.md)). Re-ingesting a
changed source refreshes the page's existing row instead of adding a second one, so the
index stays a current-state view of the wiki
([ingest.md](../../../.claude/commands/wiki/ingest.md)).

## Aliases and a reverse-link file

Two additions turn the catalog from a list into something the maintainer can match against.
The first is an alias field on every index entry, holding the other names a topic goes by,
maintained specifically so entry text can be matched to an article whose title does not
appear verbatim ([wiki skill](../../llm-wiki/farzaa/wiki-gen-skill.md)). That makes the index the
lookup table for the matching problem covered in [[entity-resolution]], not only a table of
contents.

The second is a generated reverse-link index — a machine-readable file built by scanning
every page for wikilinks and recording who links to whom
([wiki skill](../../llm-wiki/farzaa/wiki-gen-skill.md)). It answers the question the forward links
cannot: which articles reference this topic. Backlink counts are then read as a centrality
signal, with high counts marking central topics worth reading first during a query
([wiki skill](../../llm-wiki/farzaa/wiki-gen-skill.md)), and used during expansion to rank
frequently referenced topics that have no page of their own
([wiki skill](../../llm-wiki/farzaa/wiki-gen-skill.md)). Both files are rebuilt from current state
rather than edited incrementally, and rebuilt only at the end of a command
([wiki skill](../../llm-wiki/farzaa/wiki-gen-skill.md)).

This repository maintains neither. Its index carries type, status, and updated date instead
of aliases and summaries, and backlinks are left to the reading surface — Obsidian computes
them from the files ([wiki-standards.md](../../../.claude/rules/wiki-layer/wiki-standards.md)).

## The log is history, not state

The log is an append-only record of what happened and when — ingests, queries, and lint
passes ([Karpathy](../../llm-wiki/karpathy/llm-wiki.md)). It gives a timeline of the wiki's
evolution and tells the maintainer what has been done recently
([Karpathy](../../llm-wiki/karpathy/llm-wiki.md)). Append-only is the property that separates it
from the index: a re-ingest that rewrites a page's index row still appends a new dated log
entry rather than editing the old one
([ingest.md](../../../.claude/commands/wiki/ingest.md)).

This repository narrows what gets logged. Only ingest and lint write to it; query and
status are read-only and add no entry
([wiki-standards.md](../../../.claude/rules/wiki-layer/wiki-standards.md)), where Karpathy
lists queries among the logged events ([Karpathy](../../llm-wiki/karpathy/llm-wiki.md)). The source
presents its conventions as optional and modular, so this is an instantiation choice
rather than a disagreement ([Karpathy](../../llm-wiki/karpathy/llm-wiki.md)).

Widening it again is the position taken from the production side, where every operation —
ingest, edit, delete, and query — is logged with a timestamp, what changed, and why, on the
argument that this is the accountability layer explaining how a wrong page got that way
([LLM Wiki v2](../../llm-wiki/rohitg00/llm-wiki.md)). The trade is between a log that records state
changes and one that records access; [[wiki-governance]] covers what the wider version
buys.

## Consistent prefixes make the log a queryable file

A consistent entry prefix turns the log into something unix tools can read. Karpathy's
example is `## [2026-04-02] ingest | Article Title`, which makes
`grep "^## \[" log.md | tail -5` return the last five entries
([Karpathy](../../llm-wiki/karpathy/llm-wiki.md)). The format is the whole mechanism — no parser,
no database, just a line shape held stable across writes.

This wiki's entries follow that shape with the source path appended:
`## [YYYY-MM-DD] ingest | <title> | <source-path>`
([ingest.md](../../../.claude/commands/wiki/ingest.md)). Lint entries take a two-line
form, a header plus a payload line carrying missing-page and mechanical-fix counts
([wiki-standards.md](../../../.claude/rules/wiki-layer/wiki-standards.md)). The source
path in the ingest line does double duty: it is one of the two places a canonical source
path is recorded, alongside the `sources:` frontmatter of the pages built from it, and
matching against both is how a repeat ingest of the same source is detected
([ingest.md](../../../.claude/commands/wiki/ingest.md)).
