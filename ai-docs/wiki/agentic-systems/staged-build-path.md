---
type: pattern
domain: agentic-systems
status: current
created: 2026-08-09
updated: 2026-08-09
sources: ["ai-docs/graph-engineering/06-implementation-guide.md", "ai-docs/graph-engineering/07-decision-framework.md", "ai-docs/graph-engineering/09-appendices-b-and-c.md", "ai-docs/graph-engineering/10-limitations-adoption-conclusion.md"]
related: ["[[reflection-loop]]", "[[tool-use]]", "[[planning-agents]]", "[[multi-agent-collaboration]]", "[[loops-to-graphs]]", "[[pattern-selection]]", "[[agentic-anti-patterns]]", "[[architecture-over-model]]"]
---

# Staged Build Path

The playbook's implementation guidance is a sequence, not a menu: start with the smallest
reliable loop and add one capability at a time, giving each stage a baseline, a task-level
metric, a cost budget, and a rollback path
([playbook §VI](../../graph-engineering/06-implementation-guide.md)). The
governing rule is that each stage earns the right to the next by addressing a specific,
measured failure of the previous one
([playbook App. C](../../graph-engineering/09-appendices-b-and-c.md)).

## The sequence and its costs

Day 1 adds [[reflection-loop]] to one existing LLM call whose output can be evaluated: a
critique call against an explicit rubric, then a revision call, compared against the
baseline. Expected lift is 10–30% quality, which teams are told to measure for themselves
([playbook §VI.A](../../graph-engineering/06-implementation-guide.md)).

Day 2 adds [[tool-use]] — at minimum code execution or web search — with the agent deciding
when to call and the results validated before incorporation, read-only tools before write
access ([playbook §VI.B](../../graph-engineering/06-implementation-guide.md)).

Week 1 adds [[planning-agents]] for complex tasks: a plan written as structured JSON before
execution, steps executed and results collected, replanning on failure with successful work
preserved. The budget note is that this runs roughly 10× the tokens of a direct call
([playbook §VI.C](../../graph-engineering/06-implementation-guide.md)).

Week 2 goes to [[multi-agent-collaboration]], minimally generator plus critic on the same
model with different system prompts, iterating until the critic is satisfied or the limit is
reached, with artifact contracts on every handoff
([playbook §VI.D](../../graph-engineering/06-implementation-guide.md)).

Month 1 wires in persistent state — starting with a shared JSON file or database and
graduating to a knowledge graph when agents need to chain facts across sessions, adding
provenance tracking and version history
([playbook §VI.E](../../graph-engineering/06-implementation-guide.md)). The
published timeline attaches a complexity and an expected return to each step: reflection and
tool use are one day and low complexity, planning one week at medium, multi-agent two weeks
at medium, and graph architecture one month at high, returning persistence and scale
([playbook Table IV](../../graph-engineering/06-implementation-guide.md)).

## The worked progression

The playbook walks a code-review assistant through every stage with measured accuracy at
each ([playbook App. C](../../graph-engineering/09-appendices-b-and-c.md)). A
zero-shot baseline — "review this code for bugs" returning a free-form paragraph that
sometimes catches real issues and sometimes praises correct code — measures 55%. Reflection
against a rubric asking for line numbers and severity levels takes it to 72%. Executing the
test suite and reading linter output takes it to 84%, changing reviews from hypothetical
bugs to cited test failures. A planning stage applied only to PRs over 500 lines moves large-PR
accuracy from 61% to 79%. A security-auditor role alongside the general reviewer brings
combined accuracy to 88%. Storing findings as entities with typed relations, so a new PR
touching a previously vulnerable file is flagged against accumulated history, reaches 95% on
repeat patterns ([playbook App. C](../../graph-engineering/09-appendices-b-and-c.md)).

Two conclusions are drawn from the sequence. Each stage addressed a specific measured
failure of the one before it, and the compound effect from 55% to 95% is far larger than any
single stage contributed
([playbook App. C](../../graph-engineering/09-appendices-b-and-c.md)). The
same point in general form is [[architecture-over-model]].

## Do not skip stages

The adoption data is presented as tracking the build path: most organizations start with
reflection, add tool use, and only then consider planning and multi-agent, with graph
architecture the least adopted stage
([playbook §X](../../graph-engineering/10-limitations-adoption-conclusion.md)).
The instruction drawn from it is that reflection is the highest-return pattern for almost any
existing LLM application and also the most mature, so a team that cannot demonstrate
measurable lift from reflection is unlikely to benefit from multi-agent coordination or graph
architecture ([playbook §X](../../graph-engineering/10-limitations-adoption-conclusion.md)).
The path is characterized as an engineering sequence rather than a ladder of prestige — each
stage earns the next by showing the previous stage's failure mode is the binding constraint
([playbook §X](../../graph-engineering/10-limitations-adoption-conclusion.md)).

Skipping the baseline in particular has its own entry in [[agentic-anti-patterns]]: without
measuring a zero-shot call first, a team cannot tell whether agentic overhead is producing
lift or only cost
([playbook §VII.B](../../graph-engineering/07-decision-framework.md)).

## Readiness before promotion

Appendix B supplies a per-stage checklist to run before a stage is considered production
ready ([playbook App. B](../../graph-engineering/09-appendices-b-and-c.md)).
Reflection asks whether the rubric is explicit and stable, whether revision rounds are
capped, and whether every draft, critique, and revision is stored. Tool use asks whether
names, arguments, and return types are validated, whether read and write permissions are
separated, and what happens on failure or rate-limit. Planning asks whether plans are
structured JSON with dependencies, whether step count is bounded, and whether successful work
survives replanning. Multi-agent asks whether handoffs are typed, whether roles catch
genuinely different error classes, and whether the orchestrator receives bounded summaries.
Graph architecture asks whether every edge traces to a source, whether overwrites are
replaced by supersession links, and whether entity resolution decisions are inspectable
([playbook App. B](../../graph-engineering/09-appendices-b-and-c.md)).
