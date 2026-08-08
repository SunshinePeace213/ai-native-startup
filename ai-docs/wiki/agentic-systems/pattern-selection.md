---
type: decision
domain: agentic-systems
status: current
created: 2026-08-09
updated: 2026-08-09
sources: ["ai-docs/graph-engineering/07-decision-framework.md", "ai-docs/graph-engineering/03-anthropic-five-workflows.md", "ai-docs/graph-engineering/08-graphs-vs-loops-debate.md"]
related: ["[[workflow-patterns]]", "[[reflection-loop]]", "[[tool-use]]", "[[planning-agents]]", "[[multi-agent-collaboration]]", "[[loops-to-graphs]]", "[[agentic-graph-schema]]", "[[staged-build-path]]", "[[agentic-anti-patterns]]"]
---

# Pattern Selection

Which pattern to reach for, and what has to be true before reaching for the next one. The
governing rule of thumb: if the current pattern's failure mode is understood and the next
pattern addresses that specific failure, add it; if the failure mode is unclear, measure
before adding complexity
([playbook §VII](../../graph-engineering/07-decision-framework.md)). Every
pattern adds cost, latency, and debugging surface, so the cheapest pattern that satisfies the
task is usually the right one
([playbook §VII](../../graph-engineering/07-decision-framework.md)).

## The starting map

Six situations map to six starting points
([playbook Table V](../../graph-engineering/07-decision-framework.md)). Wanting
better output quality starts at [[reflection-loop]], named the cheapest and most reliable
improvement. Needing external data starts at [[tool-use]], which grounds answers in real
information. A complex multi-step task starts at [[planning-agents]], which decomposes it.
Needing multiple perspectives starts at [[multi-agent-collaboration]], since different roles
catch different errors. State that must survive across sessions starts at graph architecture
([[loops-to-graphs]]). A simple single question stays zero-shot, with the stated reason being
not to over-engineer ([playbook Table V](../../graph-engineering/07-decision-framework.md)).

The workflow vocabulary in [[workflow-patterns]] supplies a parallel ordering for the same
decision — direct call, chain, routing, parallel workers, orchestrator, evaluator-optimizer —
escalated only in response to observed errors
([playbook §III.A](../../graph-engineering/03-anthropic-five-workflows.md)).

## Five rules

*Start with the cheapest pattern.* A reflection loop is cheaper than a multi-agent system,
and a multi-agent system is cheaper than a graph architecture; complexity is added only when
a specific measured failure demands it
([playbook §VII.A](../../graph-engineering/07-decision-framework.md)).

*Measure before promoting.* Establish a baseline with the current pattern and measure the
failure rate the new pattern is supposed to address. Below a 5% failure rate, the new
pattern's complexity cost likely exceeds its benefit
([playbook §VII.A](../../graph-engineering/07-decision-framework.md)).

*Match control to risk.* High-stakes work — financial transactions, safety-critical
operations — uses predictable patterns such as chains and evaluation loops with explicit
gates. Low-stakes work such as brainstorming and research drafts can absorb the
unpredictability of planning and multi-agent systems
([playbook §VII.A](../../graph-engineering/07-decision-framework.md)). This is
the rule that makes the maturity assessments actionable: the two patterns Ng calls emerging
are the two that risk-matching keeps away from high-stakes paths.

*Count tokens, not agents.* Cost is proportional to tokens consumed, not to the number of
conceptual agents — a three-agent system at 20,000 tokens each costs what one agent running
60,000 tokens costs. The instruction is to design for token efficiency rather than conceptual
elegance ([playbook §VII.A](../../graph-engineering/07-decision-framework.md)).

*The graph earns itself.* A knowledge graph is justified when the same entity or relationship
is queried by more than one agent or across more than one session
([playbook §VII.A](../../graph-engineering/07-decision-framework.md)); the
schema that follows from it is [[agentic-graph-schema]].

## Applying the rules to the loops-versus-graphs question

The three criteria that make a graph necessary — session persistence, cross-agent
coordination, and traceability — are the concrete test behind rule five
([playbook §VIII](../../graph-engineering/08-graphs-vs-loops-debate.md)). The
playbook's practical instruction is to start with a loop, measure where it fails, and add
graph infrastructure at the specific failure point rather than in advance
([playbook §VIII](../../graph-engineering/08-graphs-vs-loops-debate.md)).

It also notes what changed the calculation in 2026: building an agentic knowledge graph
previously required expertise in graph databases, ontology design, and NLP extraction
pipelines, whereas with an agent-orchestration toolkit, a graph store, and an LLM for
extraction, a working implementation is claimed to be reachable in under an hour
([playbook §VIII](../../graph-engineering/08-graphs-vs-loops-debate.md)). A
lower bar to building one does not change when one is warranted — the decision framework
still gates the transition, and the sequencing lives in [[staged-build-path]]. Choosing a
pattern for its architecture rather than for a measured failure is the shared root of the
entries in [[agentic-anti-patterns]].
