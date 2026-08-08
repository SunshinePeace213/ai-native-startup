---
source: raw/Graph-Engineering-Andrew-Ng-Playbook.pdf
fetched: 2026-08-05
pages: 10-11
---
> **In here:** Planning and multi-agent are still "emerging" · Adoption trajectory and why teams shouldn't skip stages · The traceability sentence that defines a reliable system

# IX. Limitations

Three limitations are worth stating plainly. First, Ng himself calls Planning and Multi-Agent "emerging" — they do not always work. "At least at this moment in time, I don't feel like I can always get them to work reliably." Second, agentic workflows trade latency for quality. Ng: "we need to learn to delegate tasks to an AI agent and patiently wait minutes, maybe even hours, for a response." Third, each loop iteration costs tokens. More agents do not automatically produce more intelligence — if all agents see the same evidence and optimize the same weak rubric, the system reproduces the same error several times at higher cost.

Additionally, the HumanEval benchmark is a coding benchmark. The 95.1% figure should not be assumed to transfer directly to all domains. Teams should build their own evaluation sets and measure lift in their specific context. Graph architecture adds its own failure modes: entity resolution errors, stale provenance, schema drift, and the operational cost of maintaining a durable store. The graph amplifies corpus quality, just as the loop amplifies the judgment of its builder.

# X. Industry Adoption

The adoption trajectory gives context for the maturity assessments. A 2025 industry poll found 93% of IT leaders plan to introduce autonomous AI agents within two years, and nearly half have already started pilot implementations. Deloitte predicts that by 2025, one-quarter of companies using generative AI will have launched pilot agentic AI projects, growing to 50% by 2027. In his year-end letter for 2025, Ng characterized the year as "the dawn of the AI industrial era" — a period when AI moved from research and experimentation into industrial-scale infrastructure, with capital expenditure across the industry exceeding $300 billion.

The adoption pattern mirrors the staged build path of this note. Most organizations start with reflection (adding a review step to an existing LLM call), then add tool use (connecting the model to databases and APIs), and only then consider planning and multi-agent architectures. Graph architecture is the least adopted stage, which is consistent with its position at the end of the build path and with the fact that Ng's course on the topic is only days old. The debate on X — "are we still talking loops, or did we shift to graphs yet?" — reflects the moment at which the early-adopter segment is crossing from network-stage to graph-stage, while the majority is still in the loop-stage or chain-stage.

The practical implication for teams: do not skip stages. Reflection is the highest-ROI pattern for almost any existing LLM application, and it is also the most mature. A team that cannot demonstrate measurable lift from reflection is unlikely to benefit from the complexity of multi-agent coordination or graph architecture. The build path is not a ladder of prestige; it is an engineering sequence where each stage earns the right to the next by demonstrating that the previous stage's failure mode is the binding constraint.

# XI. Conclusion

Ng's four patterns are the vocabulary. Anthropic's five workflows are the grammar. The graph is the language. The single most important takeaway: workflow architecture matters more than model capability. GPT-3.5 with an agentic workflow (95.1%) outperforms GPT-4 in zero-shot mode (67.0%).

The build path is incremental. Start with reflection — it works today, reliably, on most tasks where quality can be evaluated. Add tools to ground answers in real data. Build planning agents for complex tasks. Go multi-agent when specialization adds measurable signal. Wire into a graph when state must persist across sessions and agents must share a world model.

The compound effect of layering patterns is where the real performance lives. Each pattern addresses a specific limitation of the previous stage: reflection addresses single-pass errors, tools address knowledge gaps, planning addresses complexity, multi-agent addresses perspective limits, and graphs address memory limits. The progression is not mandatory, but it is directional.

Ng's observation captures the broader significance: "The path to AGI feels like a journey rather than a destination, but this type of agent workflow could help us take a small step forward on this very long journey." The engineering version of the same insight: every important output should be traceable to a task, a plan, an artifact, a source, an evaluator decision, and a bounded execution record. When that is true, loops, tools, plans, workers, and graphs become composable engineering mechanisms rather than opaque behavior. The path from loops to graphs is not a path from simplicity to complexity — it is a path from implicit state to explicit state, from volatile memory to durable memory, and from estimation to evidence.

A reliable agentic system should make the following sentence true: *every important output can be traced to a task, a plan, an artifact, a source, an evaluator decision, and a* bounded execution record. When that sentence is false, more autonomy usually increases uncertainty. When it is true, the system is composable and debuggable regardless of how many patterns it compounds. The question to ask of any agentic system is not "how many patterns does it use" but "can I explain, for any output, why it is what it is." The graph — with its typed edges, provenance, and version history — is the infrastructure that makes the answer yes.
