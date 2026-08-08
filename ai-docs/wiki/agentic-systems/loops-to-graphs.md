---
type: architecture
domain: agentic-systems
status: current
created: 2026-08-09
updated: 2026-08-09
sources: ["ai-docs/graph-engineering/04-from-loops-to-graphs.md", "ai-docs/graph-engineering/08-graphs-vs-loops-debate.md", "ai-docs/graph-engineering/01-abstract-and-introduction.md", "ai-docs/graph-engineering/10-limitations-adoption-conclusion.md"]
related: ["[[agentic-graph-schema]]", "[[multi-agent-collaboration]]", "[[workflow-patterns]]", "[[reflection-loop]]", "[[staged-build-path]]", "[[pattern-selection]]", "[[graph-wiki-variant]]"]
---

# Loops to Graphs

The playbook's organizing claim is that the agentic patterns are not isolated recipes but
successive stages in the externalization of cognition: a loop externalizes revision, a chain
externalizes task order, a network externalizes role specialization, and a graph
externalizes shared state and relationships
([playbook §I](../../graph-engineering/01-abstract-and-introduction.md)). The
progression is explicitly not a maturity ladder every project must climb — many tasks should
remain direct calls or fixed chains
([playbook §IV](../../graph-engineering/04-from-loops-to-graphs.md)).

Each stage is reached by a specific breakdown in the one before it, which is what makes the
sequence an engineering argument rather than a taxonomy.

## What breaks at each boundary

**The loop** has one agent inspecting and revising its own work, with reflection as the
defining mechanism. It is compact, easy to prototype, and effective while the task fits one
context window ([playbook §IV.A](../../graph-engineering/04-from-loops-to-graphs.md)).
Every iteration may resend task, draft, critique, tool results, and prior decisions, so
context becomes expensive and noisy as history accumulates. The strength is the limitation:
everything lives in one context window, so everything must fit in one context window, and
when it stops fitting the options are to truncate and lose information, summarize and lose
precision, or restructure
([playbook §IV.A](../../graph-engineering/04-from-loops-to-graphs.md)).

**The chain** externalizes order into application code, giving each stage its own prompt,
model, tools, and validation, and making the path known in advance. Its cost is that
unexpected cases must be anticipated
([playbook §IV.B](../../graph-engineering/04-from-loops-to-graphs.md)). An
extract → validate → summarize → format chain meeting an unexpected document format either
fails at extraction, which the playbook marks as the good outcome because the failure is
visible and early, or passes garbled output forward, which compounds silently through every
later stage. Programmatic gates between stages are the fix: each gate checks the previous
stage's output against the next stage's input contract and routes failures to a fallback
([playbook §IV.B](../../graph-engineering/04-from-loops-to-graphs.md)).

**The network** introduces role-specialized workers with an orchestrator delegating and
synthesizing. Its central limitation is context management — Anthropic's observation is that
"context grows too complex for one agent to manage effectively, creating performance
bottlenecks" ([playbook §IV.C](../../graph-engineering/04-from-loops-to-graphs.md)).
The orchestrator's load rises with team size, and each worker output may itself be the
product of a multi-turn interaction, so at some point the orchestrator's window holds more
summary than substance and the summaries have dropped the detail that mattered
([playbook §IV.C](../../graph-engineering/04-from-loops-to-graphs.md)). This is
the moment the playbook names as the motivation for the graph.

**The graph** moves shared state into a durable, queryable structure. Each worker reads the
subgraph relevant to its task and writes new entities and relations back, so the
orchestrator's context stays small while the shared state lives outside it
([playbook §IV.D](../../graph-engineering/04-from-loops-to-graphs.md)). The
schema this implies is treated in [[agentic-graph-schema]].

## Three roles a knowledge graph plays

The graph is not one mechanism serving one pattern. As **shared memory** for
orchestrator-workers it lets workers read and write directly, replacing the fragile
alternative of passing summaries through the orchestrator bottleneck — described as the
multi-agent analogue of the principle that the session is not the context window. As a
**grounding layer** for evaluator-optimizer it lets the evaluator check claims against edges
carrying provenance, so feedback becomes a statement about what the store does and does not
contain rather than an impression. As a **persistent world model** for loops it survives
context-window flushes: the agent forgets, the graph does not
([playbook §IV.D](../../graph-engineering/04-from-loops-to-graphs.md)).

## When the loop stops being enough

The July 2026 debate — framed by a widely-read post asking whether the field was still
talking loops or had shifted to graphs — resolves in the playbook into three criteria
([playbook §VIII](../../graph-engineering/08-graphs-vs-loops-debate.md)).
Session persistence: work spanning multiple sessions where transcript replay is no longer
practical needs state outside the context window. Cross-agent coordination: multiple
specialized agents sharing facts without copying transcripts through a bottleneck need a
shared blackboard. Traceability: a system that must explain why a result changed needs
provenance on typed edges
([playbook §VIII](../../graph-engineering/08-graphs-vs-loops-debate.md)).

Loops handle the first criterion poorly because state is flushed with the context, the
second not at all because a loop is one agent, and the third weakly because conversation
history is the only record; graphs handle all three structurally
([playbook §VIII](../../graph-engineering/08-graphs-vs-loops-debate.md)). The
playbook is explicit that this does not make graphs better — loops are simpler to build,
cheaper to run, and sufficient for the large majority of single-agent, single-session tasks,
so the engineering question is when the loop's limitation becomes the binding constraint
([playbook §VIII](../../graph-engineering/08-graphs-vs-loops-debate.md)). The
prescribed sequence is to start with a loop, measure where it fails, and add graph
infrastructure at that specific failure point: "A loop with a state file is already partway
to a graph. A graph that nobody queries is an overengineered loop"
([playbook §VIII](../../graph-engineering/08-graphs-vs-loops-debate.md)).

## Compound, not sequential

Production systems are described as rarely using one pattern in isolation. The effective
architectures compound them — a planning agent using reflection at each step, tool use for
evidence, multi-agent collaboration for review, and a graph for persistence — and the
performance is attributed to the specific combination tuned to the task rather than to any
single pattern ([playbook §VIII.A](../../graph-engineering/08-graphs-vs-loops-debate.md)).
The staged build path in [[staged-build-path]] exists to make that compounding incremental
and measurable rather than all-at-once and opaque
([playbook §VIII.A](../../graph-engineering/08-graphs-vs-loops-debate.md)).

The playbook's closing framing is that the path from loops to graphs is not a path from
simplicity to complexity but one from implicit to explicit state, from volatile to durable
memory, and from estimation to evidence
([playbook §XI](../../graph-engineering/10-limitations-adoption-conclusion.md)).
The same loops-versus-graphs question, asked of a knowledge base rather than of an agent
team, is the subject of [[graph-wiki-variant]].
