---
type: pattern
domain: engineering
status: current
created: 2026-08-08
updated: 2026-08-08
sources: ["ai-docs/llm-wiki/rohitg00/llm-wiki.md", "ai-docs/llm-wiki/farzaa/wiki-gen-skill.md", "ai-docs/llm-wiki/lucianfialho/graphwiki-pattern.md", "ai-docs/llm-wiki/karpathy/llm-wiki.md", ".claude/rules/wiki-layer/wiki-standards.md"]
related: ["[[llm-wiki-pattern]]", "[[graph-wiki-variant]]", "[[page-writing-standards]]", "[[ingest-pipeline]]"]
---

# Wiki Schema Layer

The third layer of the [[llm-wiki-pattern]] is a configuration document stating how the
wiki is structured and which workflows to follow, and it is what makes the LLM a
disciplined wiki maintainer rather than a generic chatbot
([Karpathy](../../llm-wiki/karpathy/llm-wiki.md)). One extension makes a stronger claim about the
same file: the schema document is the most important file in the system, and calling it the
real product is the point being made explicit
([LLM Wiki v2](../../llm-wiki/rohitg00/llm-wiki.md)). Everything else — the pages, the graph, the
index — is output the schema determines.

## What the schema encodes

The enumerated contents are the decisions that would otherwise be re-litigated on every
ingest: what types of entities and relationships exist in the domain, how to ingest each
kind of source, when to create a new page rather than update an existing one, what quality
standards apply, how to handle contradictions, what the consolidation schedule looks like,
and what is private versus shared ([LLM Wiki v2](../../llm-wiki/rohitg00/llm-wiki.md)). Each of
those is a judgment call an unconstrained model would make differently each time, which is
why writing them down is the mechanism rather than the documentation.

## Fixed and generic, or open and expressive

The two variant implementations pull opposite ways on how much a schema should constrain.
The graph variant fixes its vocabulary at three node labels and four relationship types and
enforces it with database constraints, on the stated trade that this keeps every query
simple at the cost of domain expressiveness, with domain nuance pushed into node properties
rather than into new labels ([graphwiki](../../llm-wiki/lucianfialho/graphwiki-pattern.md)). It also
names what that costs when the vocabulary is too narrow: one relationship type ends up
serving two distinct purposes, and whether the resulting ambiguity produces wrong query
results is left as an open question
([graphwiki](../../llm-wiki/lucianfialho/graphwiki-pattern.md)). Giving the extractor a fixed schema
to fill is credited with producing structured typed output where asking it to "extract
triples" does not ([graphwiki](../../llm-wiki/lucianfialho/graphwiki-pattern.md)).

The page-based instantiation goes the other way. Its directories emerge from the data and
are explicitly not pre-created, with new ones to be created freely when a type does not fit
([wiki skill](../../llm-wiki/farzaa/wiki-gen-skill.md)). What it supplies instead of a constraint is
a large reference taxonomy of roughly forty directory types grouped by kind — core
categories such as people, projects, places, and events; media and culture such as books,
films, tools, and platforms; inner-life categories such as philosophies, patterns,
tensions, and identities; narrative structure such as eras, transitions, decisions,
experiments, and setbacks; and work categories such as strategies, techniques, skills, and
artifacts ([wiki skill](../../llm-wiki/farzaa/wiki-gen-skill.md)). The taxonomy is a menu the
maintainer draws from, not a schema it validates against.

Placement is treated as revisable in that model. A reorganization mode moves misclassified
articles between directories, with named common moves: articles stating beliefs go from the
general life category to philosophies, articles with a trigger-response structure go to
patterns, multi-week uncertain periods go from events to transitions, and articles with
enumerated reasons go from events to decisions
([wiki skill](../../llm-wiki/farzaa/wiki-gen-skill.md)).

## Co-evolution

Neither position expects the schema to be right initially. The first version will be rough,
and after a few dozen sources and a few lint passes the schema reflects how the domain
actually works, arrived at by the human and the LLM co-evolving the document
([LLM Wiki v2](../../llm-wiki/rohitg00/llm-wiki.md)). A schema reached that way is described as
transferable: handing it to someone working on a similar domain gives them a running start
([LLM Wiki v2](../../llm-wiki/rohitg00/llm-wiki.md)).

This repository splits the layer in two rather than keeping one file. A single rule file
fixes the spine every domain shares — seven mandatory frontmatter fields, five core types,
the status values, the citation and privacy rules, and the writing standards
([wiki-standards.md](../../../.claude/rules/wiki-layer/wiki-standards.md)). Each domain then
owns a `schema.md` at its root defining its own additional types, folder layout, and
hub-page convention, drafted by the first ingest into that domain and co-evolved by later
ones ([wiki-standards.md](../../../.claude/rules/wiki-layer/wiki-standards.md)). Domains are
open-ended and created by the ingest that needs one, never pre-created and never seeded with
placeholder pages ([wiki-standards.md](../../../.claude/rules/wiki-layer/wiki-standards.md)),
which is the emergent-structure position applied one level up from directories. Lint checks
each page's type and placement against its domain's schema, which is where the fixed half
regains its enforcement
([wiki-standards.md](../../../.claude/rules/wiki-layer/wiki-standards.md)).
