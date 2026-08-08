---
type: architecture
domain: engineering
status: current
created: 2026-08-08
updated: 2026-08-09
sources: ["ai-docs/llm-wiki/lucianfialho/graphwiki-pattern.md", "ai-docs/llm-wiki/rohitg00/llm-wiki.md", "ai-docs/llm-wiki/karpathy/llm-wiki.md", "ai-docs/graph-engineering/04-from-loops-to-graphs.md", "ai-docs/graph-engineering/07-decision-framework.md", "ai-docs/graph-engineering/10-limitations-adoption-conclusion.md"]
related: ["[[llm-wiki-pattern]]", "[[entity-resolution]]", "[[rag-vs-compiled-knowledge]]", "[[knowledge-lifecycle]]", "[[wiki-schema-layer]]", "[[agentic-graph-schema]]", "[[loops-to-graphs]]"]
---

# Graph Wiki Variant

An instantiation of the [[llm-wiki-pattern]] that stores the maintained layer as a
property graph rather than as markdown pages. The stated motivation is that the
cross-references a markdown wiki approximates with links become real, typed, queryable
edges, and that retrieval can then use graph algorithms instead of only following links
([graphwiki](../../llm-wiki/lucianfialho/graphwiki-pattern.md)). The variant keeps the pattern's
three layers and changes only how the middle one is stored
([graphwiki](../../llm-wiki/lucianfialho/graphwiki-pattern.md)).

The layer mapping is direct. Raw sources become immutable `:Source` nodes whose original
text is never modified after ingest, which is the same immutability rule the markdown form
places on its archive folder ([graphwiki](../../llm-wiki/lucianfialho/graphwiki-pattern.md)). The
maintained layer becomes `:Concept` nodes — a synthesized entity or topic carrying a prose
`summary`, named explicitly as the page equivalent — plus `:Claim` nodes holding atomic
assertions extracted from a source
([graphwiki](../../llm-wiki/lucianfialho/graphwiki-pattern.md)). The schema layer becomes a small
fixed set of node labels and relationship types enforced with database constraints
([graphwiki](../../llm-wiki/lucianfialho/graphwiki-pattern.md)).

## Nodes and edges

The vocabulary is small on purpose: three node labels and four relationship types —
`RELATES_TO` for generic association, `CONTRADICTS` for conflict, `DERIVED_FROM` for
provenance, and `PART_OF` for hierarchy
([graphwiki](../../llm-wiki/lucianfialho/graphwiki-pattern.md)). `DERIVED_FROM` is described as
being the citation itself rather than a pointer to one
([graphwiki](../../llm-wiki/lucianfialho/graphwiki-pattern.md)). Fixing the label set is presented
as a trade: it keeps every query simple at the cost of domain expressiveness, and domain
nuance is pushed into node properties such as `type: 'Gene'` instead of into new labels
([graphwiki](../../llm-wiki/lucianfialho/graphwiki-pattern.md)). The source flags the cost of its
own narrowness — `RELATES_TO` carries both structural links and claim-to-concept links,
and whether that ambiguity produces wrong query results is left open
([graphwiki](../../llm-wiki/lucianfialho/graphwiki-pattern.md)).

Nodes carry the same `current | superseded | disputed` status the markdown form uses, with
the same rule that two claims joined by `CONTRADICTS` and left unresolved are both
`disputed`, and that a resolved loser flips to `superseded` rather than being deleted
([graphwiki](../../llm-wiki/lucianfialho/graphwiki-pattern.md)). Status and its propagation to
answers are treated in [[knowledge-lifecycle]].

## Query picks an algorithm from the question shape

Retrieval here is not one traversal depth applied uniformly. Four question shapes map to
four techniques: "what is X" to an N-hop traversal from the entry node gathering
`DERIVED_FROM` sources for citation, "what else relates to X" to personalized PageRank
seeded at X, "how does X connect to Y" to a shortest path whose intermediate nodes are
themselves the explanation, and "find something shaped like X" to subgraph pattern
matching ([graphwiki](../../llm-wiki/lucianfialho/graphwiki-pattern.md)). An LLM synthesizes the
final answer from whichever subgraph came back, always citing through `DERIVED_FROM`
([graphwiki](../../llm-wiki/lucianfialho/graphwiki-pattern.md)).

A smoke test against a real Neo4j 5 instance with the GDS plugin ran the full cycle.
Traversal returned the expected one- and two-hop neighborhoods with citations,
`gds.pageRank.stream` with `sourceNodes` ranked directly connected concepts above indirect
ones, and `shortestPath` explained an indirect relationship as a chain through two
intermediate concepts ([graphwiki](../../llm-wiki/lucianfialho/graphwiki-pattern.md)). Lint on the
same graph found zero orphans, surfaced the single unresolved contradiction, and flagged a
near-duplicate concept pair for review without auto-merging it
([graphwiki](../../llm-wiki/lucianfialho/graphwiki-pattern.md)).

## The graph augments the pages, or replaces them

A second source proposing a graph layer reaches a different conclusion about what the
graph is for. It layers a typed knowledge graph on top of markdown pages, with entity
extraction at ingest producing typed entities — people, projects, libraries, concepts,
files, decisions — each with attributes and relationships
([LLM Wiki v2](../../llm-wiki/rohitg00/llm-wiki.md)). Its argument for typed edges is that "uses",
"depends on", "contradicts", "caused", "fixed", and "supersedes" carry different semantic
weight, so an edge annotated with a relationship type, a supporting-source count, and a
confidence value beats an untyped association
([LLM Wiki v2](../../llm-wiki/rohitg00/llm-wiki.md)). Its stated division of labor is that pages are
for reading and the graph is for navigation and discovery
([LLM Wiki v2](../../llm-wiki/rohitg00/llm-wiki.md)).

The two positions differ in where the prose lives. The graph-database variant puts the
summary inside the `:Concept` node and keeps no markdown page at all
([graphwiki](../../llm-wiki/lucianfialho/graphwiki-pattern.md)); the augmentation variant keeps the
pages and builds the graph beside them
([LLM Wiki v2](../../llm-wiki/rohitg00/llm-wiki.md)). Both retain the three-layer split they
inherit ([Karpathy](../../llm-wiki/karpathy/llm-wiki.md)).

## A third schema, arrived at from agent coordination

Both schemas above are designed to hold compiled knowledge for reading. A third proposal
reaches a near-identical vocabulary from the opposite direction — the state that multiple
LLM agents must share once an orchestrator's context window stops holding it
([playbook §IV.D](../../graph-engineering/04-from-loops-to-graphs.md)). Its
minimal schema is five node types — Entity, Claim, Source, Artifact, Run — with the edges
`mentions`, `supports`, `contradicts`, `derived_from`, and `supersedes`
([playbook §IV.E](../../graph-engineering/04-from-loops-to-graphs.md)).

The convergence is on the two rules this vault already runs on. Every claim retains
provenance, matching `DERIVED_FROM` being the citation itself rather than a pointer to one
([graphwiki](../../llm-wiki/lucianfialho/graphwiki-pattern.md)). And the minimal write is
additive: rather than overwriting a claim silently, the system creates a new version and
links it with `supersedes`
([playbook §IV.E](../../graph-engineering/04-from-loops-to-graphs.md)) — the
same rule that flips a resolved loser to `superseded` instead of deleting it
([graphwiki](../../llm-wiki/lucianfialho/graphwiki-pattern.md)), treated in
[[knowledge-lifecycle]].

Where it diverges is `Artifact` and `Run`. Neither wiki-side schema records how an output
was produced, because neither is holding the execution of a process; adding a plan-or-draft
node and an execution-record node is what lets the agent-side schema satisfy its own
traceability test, that every important output trace to a task, a plan, an artifact, a
source, an evaluator decision, and a bounded execution record
([playbook §XI](../../graph-engineering/10-limitations-adoption-conclusion.md)).
The full treatment is [[agentic-graph-schema]], and the progression that motivates the store
is [[loops-to-graphs]].

The same source supplies a justification test this page's variants do not state: a graph
earns itself only when the same entity or relationship is queried by more than one agent or
across more than one session, and a graph written once and never queried is called a
database table with extra overhead
([playbook §VII.A](../../graph-engineering/07-decision-framework.md)). It also
names the standing hazard directly — a graph preserves errors as efficiently as facts, with
entity resolution merging distinct organizations given as the first example
([playbook §IV.F](../../graph-engineering/04-from-loops-to-graphs.md)), which
is the risk [[entity-resolution]] measures.

## What the validation covers and what it does not

The graph variant is unusual among instantiations of the pattern in publishing measured
results rather than a design. Its multi-hop retrieval comparison appears in
[[rag-vs-compiled-knowledge]] and its entity-resolution measurements in
[[entity-resolution]]. The author lists what the smoke test did not establish: embeddings
in that first run were hand-authored eight-dimension vectors rather than model output and
the merge decision was scripted, staleness lint was not exercised because it needs
wall-clock time, and the run was a single ingest session with no re-ingest cycle, leaving
untested how a concept's summary behaves when rewritten across several later sources
([graphwiki](../../llm-wiki/lucianfialho/graphwiki-pattern.md)). Open questions carried forward
include at what corpus size and sparsity adding a hop stops being the right answer, and
whether tighter relationship typing, edge weights, or a max-fanout cutoff replaces it
([graphwiki](../../llm-wiki/lucianfialho/graphwiki-pattern.md)).
