---
type: pattern
domain: agentic-systems
status: current
created: 2026-08-09
updated: 2026-08-09
sources: ["ai-docs/graph-engineering/02-four-design-patterns.md", "ai-docs/graph-engineering/03-anthropic-five-workflows.md", "ai-docs/graph-engineering/06-implementation-guide.md", "ai-docs/graph-engineering/07-decision-framework.md", "ai-docs/graph-engineering/09-appendices-b-and-c.md"]
related: ["[[reflection-loop]]", "[[planning-agents]]", "[[workflow-patterns]]", "[[loops-to-graphs]]", "[[agentic-anti-patterns]]", "[[staged-build-path]]"]
---

# Multi-Agent Collaboration

Multiple LLM instances, each prompted with a different role, work on a task that benefits
from specialization
([playbook §II.D](../../graph-engineering/02-four-design-patterns.md)). Ng's
cited example is ChatDev, which prompts one instance as CEO, another as designer, another
as product manager, another as tester; asked to develop a Go game, the group spends minutes
writing code, testing, and iterating before producing the program
([playbook §II.D](../../graph-engineering/02-four-design-patterns.md)). His
assessment places the pattern with planning as emerging, but with the qualifier that it
"works much better than you might think"
([playbook §II.D](../../graph-engineering/02-four-design-patterns.md)).

## Why different roles help, and when they do not

The mechanism is error-class coverage rather than added intelligence. Two agents given
different role prompts and the same evidence tend to catch different classes of error: a
coder agent optimizes for functionality, a reviewer agent for edge cases, a tester agent for
coverage, and no single rubric captures all three
([playbook §II.D](../../graph-engineering/02-four-design-patterns.md)).
Multi-agent debate, in which agents argue different positions, is reported to improve
performance for the same reason
([playbook §II.D](../../graph-engineering/02-four-design-patterns.md)).

The limitation is stated in the same breath as the benefit. Three agents consume three times
the tokens, and if all three see the same evidence and optimize the same weak rubric, the
system reproduces the same error three times at higher cost
([playbook §II.D](../../graph-engineering/02-four-design-patterns.md)). This
yields a single admission test for any new role: does it catch an error class that the
existing roles demonstrably miss
([playbook §II.D](../../graph-engineering/02-four-design-patterns.md))? A role
that fails the test is the *echo chamber* in [[agentic-anti-patterns]]
([playbook §VII.B](../../graph-engineering/07-decision-framework.md)). The same
caution appears in the parallelization workflow: ten outputs from one model under nearly
identical prompts are not ten independent judgments, and voting adds signal only when the
prompts or models differ enough to induce different error distributions
([playbook §III](../../graph-engineering/03-anthropic-five-workflows.md)).

## Artifact contracts, not conversation

Every handoff gets a typed artifact contract: the researcher returns claims with sources,
the planner returns typed steps, the coder returns code and assumptions, the evaluator
returns defects and a decision
([playbook §II.D](../../graph-engineering/02-four-design-patterns.md)). Agents
are told to communicate through artifacts and shared state rather than unlimited
conversational history — a constraint the playbook presents as the preparation for graph
architecture rather than merely as hygiene
([playbook §II.D](../../graph-engineering/02-four-design-patterns.md)).

The cost of ignoring it is quantified in the orchestrator's context. A worker returning a
200-token artifact keeps the orchestrator's window manageable where a 5,000-token
conversation transcript does not
([playbook §III](../../graph-engineering/03-anthropic-five-workflows.md)), and
an orchestrator that receives every worker's full transcript grows its context linearly with
team size until it exceeds the window
([playbook §VII.B](../../graph-engineering/07-decision-framework.md)). This
bottleneck is the specific failure that motivates the graph stage in [[loops-to-graphs]].

## Readiness questions and measured lift

Three checks apply at this stage: does every handoff use a typed schema, do the roles catch
genuinely different error classes, and does the orchestrator receive bounded summaries
([playbook App. B](../../graph-engineering/09-appendices-b-and-c.md)). The
minimum viable configuration is generator plus critic, using the same model with different
system prompts and iterating until the critic is satisfied or the iteration limit is reached
([playbook §VI.D](../../graph-engineering/06-implementation-guide.md)) — which
is [[reflection-loop]] with the roles held by separate instances.

In the worked code-review example, the added role is a security auditor whose system prompt
instructs it to assume every input is malicious. It runs alongside the general reviewer and
catches injection vulnerabilities the general agent missed, moving combined accuracy from
84% to 88% ([playbook App. C](../../graph-engineering/09-appendices-b-and-c.md)).
The gain is smaller than reflection's or tool use's in the same progression, which is
consistent with the pattern's position late on the [[staged-build-path]].
