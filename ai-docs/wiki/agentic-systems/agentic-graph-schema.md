---
type: architecture
domain: agentic-systems
status: current
created: 2026-08-09
updated: 2026-08-09
sources: ["ai-docs/graph-engineering/04-from-loops-to-graphs.md", "ai-docs/graph-engineering/06-implementation-guide.md", "ai-docs/graph-engineering/07-decision-framework.md", "ai-docs/graph-engineering/09-appendices-b-and-c.md", "ai-docs/graph-engineering/10-limitations-adoption-conclusion.md"]
related: ["[[loops-to-graphs]]", "[[pattern-selection]]", "[[agentic-anti-patterns]]", "[[graph-wiki-variant]]", "[[entity-resolution]]"]
---

# Agentic Graph Schema

The shape of the durable store that agents share once the network stage in [[loops-to-graphs]]
outgrows the orchestrator's context window. The playbook specifies a deliberately small
starting schema rather than a domain ontology, on the argument that the graph is
infrastructure for coordination and traceability rather than a modelling exercise.

## Five nodes and five edges

The starting schema has five node types. **Entity** covers a person, organization, product,
or concept. **Claim** is a statement that may be supported or contradicted. **Source** is a
document, API response, or test result. **Artifact** is a plan, draft, code, or report.
**Run** is an execution record
([playbook §IV.E](../../graph-engineering/04-from-loops-to-graphs.md)).

Edges carry the relationships: `mentions`, `supports`, `contradicts`, `derived_from`, and
`supersedes` ([playbook §IV.E](../../graph-engineering/04-from-loops-to-graphs.md)).
Two invariants sit on top of them. Every claim retains provenance, and every revision points
at the version it replaced. The minimal write operation is additive: rather than overwriting
a claim silently, the system creates a new version and links it with `supersedes`
([playbook §IV.E](../../graph-engineering/04-from-loops-to-graphs.md)).

The `Artifact` and `Run` nodes are what distinguish this from a general knowledge graph.
They make the schema a record of agent execution as well as of subject matter, which is what
lets the conclusion's traceability test be satisfied — that every important output can be
traced to a task, a plan, an artifact, a source, an evaluator decision, and a bounded
execution record
([playbook §XI](../../graph-engineering/10-limitations-adoption-conclusion.md)).
The playbook treats that sentence as the definition of a reliable agentic system: when it is
false, more autonomy usually increases uncertainty
([playbook §XI](../../graph-engineering/10-limitations-adoption-conclusion.md)).

## The graph is not automatic truth

A graph preserves errors as efficiently as facts. The named ways it goes wrong are entity
resolution merging distinct organizations, extraction attaching the wrong date, and a
confident evaluator marking a weak source as sufficient
([playbook §IV.F](../../graph-engineering/04-from-loops-to-graphs.md)). The
required counterweights are schema validation, canonical identifiers, provenance, explicit
representation of conflict, confidence calibration, and periodic review
([playbook §IV.F](../../graph-engineering/04-from-loops-to-graphs.md)).

The limitations section adds stale provenance, schema drift, and the operating cost of
maintaining a durable store to the list, and states the general principle: the graph
amplifies corpus quality just as the loop amplifies the judgment of its builder
([playbook §IX](../../graph-engineering/10-limitations-adoption-conclusion.md)).
The readiness checklist reduces this to three questions asked of any graph stage — does
every edge trace to a source document, are overwrites replaced by supersession links, and
are entity resolution decisions inspectable
([playbook App. B](../../graph-engineering/09-appendices-b-and-c.md)). The
third question is the one with measured technique behind it elsewhere in this vault; see
[[entity-resolution]].

## A graph has to earn itself

The justification test is a query test, not a modelling one: a knowledge graph is warranted
when the same entity or relationship is queried by more than one agent or across more than
one session, and a graph written to once and never queried is "a database table with extra
overhead" ([playbook §VII.A](../../graph-engineering/07-decision-framework.md)).
The failure of that test has its own entry in [[agentic-anti-patterns]] — the phantom graph,
an elaborate ontology no agent ever queries
([playbook §VII.B](../../graph-engineering/07-decision-framework.md)).

This is also why the build path stages the store rather than starting with one. The
recommended first step is a shared JSON file or database, graduating to a knowledge graph
only when agents need to chain facts across sessions, with provenance tracking and version
history added at that point
([playbook §VI.E](../../graph-engineering/06-implementation-guide.md)).

## Against the knowledge-base schemas

This schema arrives at the same primitives as the graph proposals catalogued in
[[graph-wiki-variant]] from a different starting point — agent coordination rather than
knowledge compilation — and the convergence is on provenance and supersession. Both make the
citation edge structural rather than annotative, and both replace deletion with a
supersession link. The differences are in what each counts as a node: the wiki-side schemas
center `:Concept` and `:Claim` nodes for reading, while this one adds `Artifact` and `Run`
to record how an output was produced
([playbook §IV.E](../../graph-engineering/04-from-loops-to-graphs.md)).
