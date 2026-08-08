---
type: pattern
domain: agentic-systems
status: current
created: 2026-08-09
updated: 2026-08-09
sources: ["ai-docs/graph-engineering/02-four-design-patterns.md", "ai-docs/graph-engineering/03-anthropic-five-workflows.md", "ai-docs/graph-engineering/06-implementation-guide.md", "ai-docs/graph-engineering/07-decision-framework.md", "ai-docs/graph-engineering/09-appendices-b-and-c.md"]
related: ["[[reflection-loop]]", "[[tool-use]]", "[[multi-agent-collaboration]]", "[[workflow-patterns]]", "[[staged-build-path]]", "[[agentic-anti-patterns]]", "[[pattern-selection]]"]
---

# Planning Agents

Planning uses an LLM to decide autonomously what sequence of steps to execute, rather than
having that sequence fixed in application code
([playbook §II.C](../../graph-engineering/02-four-design-patterns.md)). The
working shape is plan-then-execute: the model emits a structured plan, each step runs, and
results accumulate. Its distinguishing property against a fixed chain is that the
decomposition is discovered at run time rather than anticipated at design time
([playbook §III](../../graph-engineering/03-anthropic-five-workflows.md)).

Ng's maturity assessment is the least confident of the four patterns. He describes planning
as emerging — "sometimes my mind is blown by how well they work, but at least at this
moment in time, I don't feel like I can always get them to work reliably"
([playbook §II.C](../../graph-engineering/02-four-design-patterns.md)). The
prescribed response to that unreliability is tighter constraint rather than avoidance:
structured plan formats, dependency validation, bounded step counts, and fallback policies
([playbook §II.C](../../graph-engineering/02-four-design-patterns.md)).

## Replanning preserves successful work

The load-bearing detail in the pattern is what happens on failure. When a step fails, the
agent replans with the context of what already worked
([playbook §II.C](../../graph-engineering/02-four-design-patterns.md)). Without
that, a failure at step 5 of 8 discards the successful results of steps 1–4 and starts over,
spending both tokens and wall-clock time to return to where it already was; with it, the
replan builds on established ground
([playbook §II.C](../../graph-engineering/02-four-design-patterns.md)). The
readiness checklist turns this into a question to ask of any planning stage: does successful
work survive replanning
([playbook App. B](../../graph-engineering/09-appendices-b-and-c.md)).

Dependency validation runs before execution, not during. The check is whether every step's
inputs can be produced either by a prior step or by an available tool
([playbook §II.C](../../graph-engineering/02-four-design-patterns.md)). Failure
criteria are explicit rather than emergent — the stated example is escalating to a human if
a step fails twice after a replan instead of attempting a third time
([playbook §II.C](../../graph-engineering/02-four-design-patterns.md)).

## Four failure modes

Over-planning: elaborate plans generated for tasks a single call would handle. The
plan-execution gap: the plan describes steps the agent cannot perform with the tools it
actually has. Cascading failure: one bad step corrupts every subsequent step that depends on
its output. Unbounded replanning: the agent replans indefinitely without converging
([playbook §II.C](../../graph-engineering/02-four-design-patterns.md)).

Over-planning and the premature-agent entry in [[agentic-anti-patterns]] are the same error
seen from two angles — architecture chosen for its own sake rather than in response to a
measured failure ([playbook §VII.B](../../graph-engineering/07-decision-framework.md)).

## The cost is roughly ten times a direct call

Planning agents consume substantially more tokens than direct calls because the plan is
generated text, each step's execution is generated text, and the synthesis of results is
generated text again
([playbook §VI.C](../../graph-engineering/06-implementation-guide.md)). The
worked figure: eight steps at 2,000 tokens each plus a 3,000-token synthesis is about 19,000
tokens, roughly 10× a direct call, and the lift in task completion rate has to justify that
— for simple tasks it usually does not
([playbook §VI.C](../../graph-engineering/06-implementation-guide.md)). This
is the concrete instance of the "count tokens, not agents" rule in [[pattern-selection]].

## Where the pattern pays

Planning agents are most useful when the human's time is more expensive than the agent's
tokens, and when the task is defined tightly enough that the plan can be judged against
objective criteria
([playbook §II.C](../../graph-engineering/02-four-design-patterns.md)). The
contrast drawn is between open-ended research — "find something interesting" — which yields
plans that are hard to evaluate and easy to waste tokens on, and focused research — find all
papers citing X that report Y — which yields plans that are straightforward to validate
([playbook §II.C](../../graph-engineering/02-four-design-patterns.md)).

In the worked code-review example, planning is applied selectively rather than globally:
only PRs over 500 lines get a plan that orders security-sensitive files, then business
logic, then tests, so each section receives a focused review with the right rubric. Measured
accuracy on large PRs moves from 61% with reflection alone to 79%
([playbook App. C](../../graph-engineering/09-appendices-b-and-c.md)). In
Anthropic's vocabulary the same capability appears as orchestrator-workers combined with
chaining, the distinction being dynamic against fixed decomposition
([playbook §III](../../graph-engineering/03-anthropic-five-workflows.md)) —
covered in [[workflow-patterns]].
