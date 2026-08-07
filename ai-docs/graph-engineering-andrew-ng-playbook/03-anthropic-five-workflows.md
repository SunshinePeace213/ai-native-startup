---
source: Graph-Engineering-Andrew-Ng-Playbook.pdf
fetched: 2026-08-05
pages: 4-5
---
> **In here:** Prompt chaining, routing, parallelization, orchestrator-workers, evaluator-optimizer · Workflow before agent · Mapping Ng's patterns to Anthropic's (Table II)

# III. Anthropic's Five Workflow Patterns

Anthropic's "Building Effective Agents" distinguishes *workflows* (LLMs and tools operating through predefined code paths) from *agents* (the model dynamically directs its own process). The distinction resists unnecessary autonomy: many reliable systems can be built from simple, composable workflows.

**Prompt Chaining** sends output of one call into the next in a fixed sequence; each stage performs a narrow transformation with programmatic checks between. Use when tasks "decompose easily and cleanly into fixed subtasks." Strength: predictability, each stage testable separately. Weakness: inflexibility to unexpected inputs. A practical implementation uses typed intermediate outputs between stages so that each stage validates its input before processing — a malformed output from stage 2 is caught at stage 3's entrance, not at the final output.

**Routing** classifies an input and sends it to a specialized prompt, tool set, or workflow. A support system may route billing questions to a billing agent, technical incidents to a diagnostic workflow. Routing enables separation of concerns without requiring agents to converse. Main failure mode: misclassification. Controls include confidence thresholds (below 0.8 → fallback route) and explicit fallback paths for inputs that match no category. Routing is also the cheapest form of "intelligence" in a multi-agent system: a fast, small model classifies; a capable, expensive model processes.

**Parallelization** runs multiple calls simultaneously — sectioning (independent subtasks divided among workers) or voting (same task run multiple times, aggregator selects best). Sectioning reduces latency; voting increases robustness. The critical caveat: ten outputs from the same model with nearly identical prompts are not ten independent judgments. For voting to add genuine signal, the prompts or models should differ in ways that induce different error distributions — a code review with three different rubrics (correctness, security, performance) produces more signal than three identical reviews.

**Orchestrator-Workers** uses a central LLM to analyze a task, create subtasks dynamically, delegate them to workers, and synthesize outputs. This pattern combines Planning and Multi-Agent Collaboration. The architecture is powerful because it adapts, but the orchestrator can become a context bottleneck. Practical systems should require workers to return structured artifacts rather than raw conversation — bounded summaries with typed fields, not open-ended text. The orchestrator's context stays manageable when it receives a 200-token artifact per worker rather than a 5,000-token conversation transcript.

**Evaluator-Optimizer** separates generation from evaluation: one LLM produces a response, another evaluates against explicit criteria, the loop continues until a threshold is met. This is Reflection formalized as a production workflow with explicit role separation. Especially effective for translation, code with security requirements, professional communications where tone matters, and structured documents. Anthropic notes this pattern typically runs 2–4 cycles, significantly improving output quality while maintaining accuracy.

## A. Choosing Workflow Before Agent

The production default should be the simplest pattern that satisfies the task. Use a direct LLM call for a simple question. Use a chain when the steps are fixed. Use routing when requests belong to clear categories. Use parallel workers when independent coverage matters. Use an orchestrator when decomposition must be discovered. Use evaluator-optimizer when quality can be judged and improved iteratively. This order is not conservative for its own sake. Each step adds cost, latency, nondeterminism, and failure modes. Agentic design is effective when complexity is added in response to observed errors, not when every available pattern is included from the beginning.

### Table II — Mapping Ng's Patterns to Anthropic's Workflows

| Ng Pattern | Anthropic Workflow | Key Addition |
| --- | --- | --- |
| Reflection | Evaluator-Optimizer | Explicit role separation and stopping criteria |
| Tool Use | Augmented LLM | Building block for all workflows |
| Planning | Orch.-Workers + Chaining | Dynamic vs. fixed decomposition |
| Multi-Agent | Parallel. + Orch.-Workers | Production orchestration |
