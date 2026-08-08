---
type: pattern
domain: agentic-systems
status: current
created: 2026-08-09
updated: 2026-08-09
sources: ["ai-docs/graph-engineering/02-four-design-patterns.md", "ai-docs/graph-engineering/03-anthropic-five-workflows.md", "ai-docs/graph-engineering/06-implementation-guide.md", "ai-docs/graph-engineering/07-decision-framework.md", "ai-docs/graph-engineering/09-appendices-b-and-c.md", "ai-docs/graph-engineering/10-limitations-adoption-conclusion.md"]
related: ["[[tool-use]]", "[[planning-agents]]", "[[multi-agent-collaboration]]", "[[workflow-patterns]]", "[[loops-to-graphs]]", "[[staged-build-path]]", "[[agentic-anti-patterns]]"]
---

# Reflection Loop

An LLM examines an output, compares it against a task or rubric, names the defects, and
produces a revision ([playbook §II.A](../../graph-engineering/02-four-design-patterns.md)).
The pattern can run as one model instance alternating between generator and critic
prompts, or as two role-separated instances. The number of model objects is not the
defining property — the defining properties are an explicit feedback loop and a stopping
rule ([playbook §II.A](../../graph-engineering/02-four-design-patterns.md)).

Of the four patterns in Ng's vocabulary, reflection is the one he assesses as robust:
"I can almost always get them to work well"
([playbook §II.A](../../graph-engineering/02-four-design-patterns.md)). It is
also named the cheapest and most reliable route to better output quality
([playbook §VII](../../graph-engineering/07-decision-framework.md)), which is
why it sits first on the [[staged-build-path]].

## Three construction rules

Separate critique from rewriting. Asking a model to "improve this" and accepting an opaque
replacement collapses two decisions into one; the working form requests a structured list
of issues first, then feeds that list into a distinct revision step
([playbook §II.A](../../graph-engineering/02-four-design-patterns.md)).

Make the evaluator cite evidence from the draft, the tests, or the source material. The
contrast drawn is between "the function might not handle edge cases" and "line 12 does not
handle the case where the input list is empty, which violates requirement 3 in the
specification" ([playbook §II.A](../../graph-engineering/02-four-design-patterns.md)).
Only the second is actionable, and only the second can be checked.

Store every intermediate artifact — draft, critique, revision, and the stopping decision.
Without that record, a failure cannot be attributed to weak generation, weak evaluation,
or a faulty stopping rule; the playbook compares it to debugging a program without logs
([playbook §II.A](../../graph-engineering/02-four-design-patterns.md)). The
production-readiness checklist asks the same three questions of any reflection stage: is
the rubric explicit and stable, is there a maximum number of revision rounds, and is every
draft, critique, and revision stored
([playbook App. B](../../graph-engineering/09-appendices-b-and-c.md)).

## Failure modes and controls

Three failure modes recur. Self-confirmation: the critic repeats the assumptions that
produced the draft. Rubric drift: the evaluator rewards fluency instead of correctness.
Non-monotonic revision: a fix introduces another bug
([playbook §II.A](../../graph-engineering/02-four-design-patterns.md)).

The controls are structural rather than prompt-level. Keep the task statement immutable so
the target cannot move. Compare every revision against the rubric rather than against the
previous draft. Run deterministic checks before subjective evaluation, so a failing test
settles what a critique would otherwise argue about. Cap iterations
([playbook §II.A](../../graph-engineering/02-four-design-patterns.md)). A loop
without the cap is the *infinite loop* in [[agentic-anti-patterns]] — it iterates until the
token budget is exhausted, producing stylistic churn rather than substantive improvement
([playbook §VII.B](../../graph-engineering/07-decision-framework.md)).

The rubric is written before the first run, not discovered after. A usable starting rubric
names the qualities the output must have — correct information, appropriate length,
required sections — and the defects the critic should hunt: unsupported claims, missing
citations, logical contradictions. The playbook describes the rubric as a kind of unit test
for the output ([playbook §VI.A](../../graph-engineering/06-implementation-guide.md)).

## Evaluator-optimizer is the production form

Anthropic's evaluator-optimizer workflow is this pattern with the roles formally split: one
LLM produces a response, another evaluates it against explicit criteria, and the loop
continues until a threshold is met
([playbook §III](../../graph-engineering/03-anthropic-five-workflows.md)). The
addition over plain reflection is explicit role separation and stopping criteria
([playbook §III](../../graph-engineering/03-anthropic-five-workflows.md)). It is
reported to run 2–4 cycles typically, and to suit translation, code with security
requirements, professional communications where tone matters, and structured documents
([playbook §III](../../graph-engineering/03-anthropic-five-workflows.md)).
Grounding the evaluator against a durable store rather than against its own judgment is
one of the three roles a graph plays in [[loops-to-graphs]].

## Measured lift

Adding reflection to one existing LLM call is a one-day change: two additional calls and a
for-loop, with an expected 10–30% quality improvement that each team is told to measure for
itself ([playbook §VI.A](../../graph-engineering/06-implementation-guide.md)).
In the worked code-review example, reflection moves a zero-shot baseline from 55% to 72%
measured accuracy — the largest single-stage jump in that progression
([playbook App. C](../../graph-engineering/09-appendices-b-and-c.md)). Because
it is both the highest-return and the most mature stage, a team that cannot demonstrate lift
from reflection is judged unlikely to benefit from multi-agent or graph complexity
([playbook §X](../../graph-engineering/10-limitations-adoption-conclusion.md)).
