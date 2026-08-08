---
type: failure-mode
domain: agentic-systems
status: current
created: 2026-08-09
updated: 2026-08-09
sources: ["ai-docs/graph-engineering/07-decision-framework.md", "ai-docs/graph-engineering/02-four-design-patterns.md", "ai-docs/graph-engineering/04-from-loops-to-graphs.md", "ai-docs/graph-engineering/10-limitations-adoption-conclusion.md"]
related: ["[[pattern-selection]]", "[[staged-build-path]]", "[[reflection-loop]]", "[[multi-agent-collaboration]]", "[[planning-agents]]", "[[agentic-graph-schema]]", "[[loops-to-graphs]]"]
---

# Agentic Anti-Patterns

Seven configurations the playbook names as recurring in production agentic systems
([playbook §VII.B](../../graph-engineering/07-decision-framework.md)). They
group into three causes: responsibility that was never divided, complexity adopted without a
measured failure behind it, and loops left without a bound.

## Undivided responsibility

**The everything-agent** is one agent holding every tool, every role, and a fifty-page system
prompt meant to handle all cases. The stated cost is diagnostic rather than performance: with
no clear responsibility it has no clear failure mode, which makes it impossible to debug
([playbook §VII.B](../../graph-engineering/07-decision-framework.md)).

**The conversational bottleneck** is an orchestrator receiving every worker's full
conversation transcript, its context growing linearly with team size until it exceeds the
window ([playbook §VII.B](../../graph-engineering/07-decision-framework.md)).
This is the failure that the artifact contracts in [[multi-agent-collaboration]] prevent and
that the graph stage in [[loops-to-graphs]] resolves structurally.

## Complexity without a measured failure

**The premature agent** builds a multi-agent system for a task a single well-prompted call
handles, motivated by the architectural pattern rather than the task's requirements
([playbook §VII.B](../../graph-engineering/07-decision-framework.md)).

**The missing baseline** deploys an agentic system without first measuring a zero-shot call,
so the team cannot tell whether the agentic overhead is producing lift or only cost
([playbook §VII.B](../../graph-engineering/07-decision-framework.md)). It is
the direct violation of the measure-before-promoting rule in [[pattern-selection]], and the
reason every stage of [[staged-build-path]] carries a baseline.

**The echo chamber** runs multiple agents on identical prompts and identical evidence,
producing identical outputs at higher cost — more agents is not more intelligence
([playbook §VII.B](../../graph-engineering/07-decision-framework.md)). The
limitations section states the same failure as a general caution: if all agents see the same
evidence and optimize the same weak rubric, the system reproduces the same error several
times at higher cost
([playbook §IX](../../graph-engineering/10-limitations-adoption-conclusion.md)).

**The phantom graph** is a knowledge graph with an elaborate ontology no agent ever queries —
infrastructure cost without value
([playbook §VII.B](../../graph-engineering/07-decision-framework.md)). The
countertest is that a graph earns itself only when more than one agent or more than one
session queries the same entity or relationship
([playbook §VII.A](../../graph-engineering/07-decision-framework.md)); the
schema that follows is [[agentic-graph-schema]].

## No stopping rule

**The infinite loop** is a reflection or planning agent without a stopping rule, iterating
until the token budget is exhausted and producing marginal stylistic changes rather than
substantive improvement
([playbook §VII.B](../../graph-engineering/07-decision-framework.md)). The
control is the iteration cap that [[reflection-loop]] treats as a defining property of the
pattern rather than as a safeguard added afterwards
([playbook §II.A](../../graph-engineering/02-four-design-patterns.md)); its
planning-side twin is the unbounded replanning failure in [[planning-agents]], where the agent
replans indefinitely without converging
([playbook §II.C](../../graph-engineering/02-four-design-patterns.md)).

## The graph inherits its own set

Moving to a durable store does not retire these failures — it adds entity resolution errors,
extraction attaching wrong values, and a confident evaluator accepting a weak source, since a
graph preserves errors as efficiently as facts
([playbook §IV.F](../../graph-engineering/04-from-loops-to-graphs.md)). Stale
provenance, schema drift, and the operating cost of the store are named alongside them
([playbook §IX](../../graph-engineering/10-limitations-adoption-conclusion.md)).
