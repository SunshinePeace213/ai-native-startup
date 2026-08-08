---
type: pattern
domain: agentic-systems
status: current
created: 2026-08-09
updated: 2026-08-09
sources: ["ai-docs/graph-engineering/03-anthropic-five-workflows.md", "ai-docs/graph-engineering/10-limitations-adoption-conclusion.md"]
related: ["[[reflection-loop]]", "[[tool-use]]", "[[planning-agents]]", "[[multi-agent-collaboration]]", "[[pattern-selection]]", "[[loops-to-graphs]]", "[[agentic-anti-patterns]]"]
---

# Workflow Patterns

Anthropic's "Building Effective Agents" separates *workflows* — LLMs and tools operating
through predefined code paths — from *agents*, where the model directs its own process
([playbook §III](../../graph-engineering/03-anthropic-five-workflows.md)). The
distinction exists to resist unnecessary autonomy: many reliable systems can be assembled
from simple, composable workflows without ever handing control of the path to the model
([playbook §III](../../graph-engineering/03-anthropic-five-workflows.md)).

Five workflows carry the vocabulary. [[tool-use]] is not among them — it is the augmented
LLM, the building block the five are assembled from
([playbook §III](../../graph-engineering/03-anthropic-five-workflows.md)).

## The five

**Prompt chaining** feeds the output of one call into the next in a fixed sequence, each
stage performing a narrow transformation with programmatic checks between. It suits tasks
that "decompose easily and cleanly into fixed subtasks"; its strength is predictability and
per-stage testability, its weakness inflexibility to unexpected inputs
([playbook §III](../../graph-engineering/03-anthropic-five-workflows.md)). Typed
intermediate outputs let each stage validate its input on entry, so a malformed stage-2
output is caught at stage 3's entrance rather than at the final output
([playbook §III](../../graph-engineering/03-anthropic-five-workflows.md)).

**Routing** classifies an input and dispatches it to a specialized prompt, tool set, or
workflow — billing questions to a billing agent, technical incidents to a diagnostic
workflow. It achieves separation of concerns without requiring agents to converse. Its
failure mode is misclassification, controlled with confidence thresholds and an explicit
fallback path for inputs matching no category
([playbook §III](../../graph-engineering/03-anthropic-five-workflows.md)). It is
also named the cheapest form of intelligence in a multi-agent system: a fast, small model
classifies and a capable, expensive model processes
([playbook §III](../../graph-engineering/03-anthropic-five-workflows.md)).

**Parallelization** runs multiple calls simultaneously, in one of two shapes — sectioning,
which divides independent subtasks among workers, and voting, which runs the same task
several times and has an aggregator select. Sectioning reduces latency; voting increases
robustness ([playbook §III](../../graph-engineering/03-anthropic-five-workflows.md)).
The caveat is the one that governs [[multi-agent-collaboration]]: identical prompts do not
produce independent judgments, and three code reviews under three different rubrics —
correctness, security, performance — produce more signal than three identical reviews
([playbook §III](../../graph-engineering/03-anthropic-five-workflows.md)).

**Orchestrator-workers** has a central LLM analyze a task, create subtasks dynamically,
delegate them, and synthesize the outputs — the combination of planning and multi-agent
collaboration. Its power is adaptation; its structural risk is the orchestrator becoming a
context bottleneck, which bounded structured artifacts rather than raw conversation are the
fix for ([playbook §III](../../graph-engineering/03-anthropic-five-workflows.md)).

**Evaluator-optimizer** splits generation from evaluation: one LLM produces, another judges
against explicit criteria, and the loop runs until a threshold is met. It is [[reflection-loop]]
formalized with explicit role separation and stopping criteria, typically running 2–4 cycles
([playbook §III](../../graph-engineering/03-anthropic-five-workflows.md)).

## Choose the workflow before the agent

The production default is the simplest pattern that satisfies the task, and the escalation
order is specified: a direct call for a simple question, a chain when the steps are fixed,
routing when requests fall into clear categories, parallel workers when independent coverage
matters, an orchestrator when the decomposition must be discovered, and evaluator-optimizer
when quality can be judged and improved iteratively
([playbook §III.A](../../graph-engineering/03-anthropic-five-workflows.md)).

The justification is not conservatism for its own sake. Each step adds cost, latency,
nondeterminism, and failure modes, so complexity is added in response to observed errors
rather than included from the start
([playbook §III.A](../../graph-engineering/03-anthropic-five-workflows.md)). The
same principle drives the ordering in [[pattern-selection]] and the anti-patterns of the
missing baseline and the premature agent in [[agentic-anti-patterns]].

## How the two vocabularies map

Ng's four design patterns and Anthropic's five workflows describe overlapping ground from
different angles, and the playbook aligns them explicitly. Reflection corresponds to
evaluator-optimizer, which adds role separation and stopping criteria. Tool use corresponds
to the augmented LLM. Planning corresponds to orchestrator-workers plus chaining, the added
distinction being dynamic against fixed decomposition. Multi-agent corresponds to
parallelization plus orchestrator-workers, the addition being production orchestration
([playbook §III](../../graph-engineering/03-anthropic-five-workflows.md)).

The playbook's own summary of the relationship is that the four patterns are the vocabulary
and the five workflows are the grammar, with the graph as the language
([playbook §XI](../../graph-engineering/10-limitations-adoption-conclusion.md)) —
the progression [[loops-to-graphs]] sets out.
