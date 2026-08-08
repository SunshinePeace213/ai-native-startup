---
source: raw/Graph-Engineering-Andrew-Ng-Playbook.pdf
fetched: 2026-08-05
pages: 6-7
---
> **In here:** HumanEval numbers (Table III) · Fast inference as a capability multiplier · Model selection and workflow design are not independent

# V. The Benchmark Evidence

### Table III — HumanEval Coding Benchmark (Reported by Ng)

| Configuration | Score (%) |
| --- | --- |
| GPT-3.5 zero-shot | 48.1 |
| GPT-4 zero-shot | 67.0 |
| GPT-3.5 + agentic workflow | 95.1 |

Key insight: "the improvement from GPT-3.5 to GPT-4 is dwarfed by incorporating an iterative agent workflow." This means: invest in workflow architecture, not just model upgrades. Ng: "if you're looking forward to running your thing on GPT-5 zero-shot, you may be able to get closer to that level of performance on some applications with agentic reasoning on an earlier model."

One additional insight Ng emphasizes: fast token generation is important for agentic workflows because the LLM generates tokens for other LLMs to read, not for humans. "Being able to generate tokens way faster than any human can read is fantastic." Generating more tokens quickly from even a slightly lower quality LLM "might give good results compared to slower tokens from a better LLM — because it may let you go around this loop a lot more times." This makes fast inference a direct multiplier for agentic system performance.

The benchmark data has a second implication that is less discussed but equally important. If a weaker model with a strong process can outperform a stronger model asked to answer once, then *model selection and workflow design are not independent decisions.* The optimal system is not necessarily the strongest model in the simplest workflow; it may be a weaker, cheaper, faster model in a compound workflow that uses the savings to run more iterations, more workers, or more evaluation rounds. This is the economic argument for the staged build path: each stage's cost must be justified by measurable lift, and a cheaper model that funds more iterations may outperform an expensive model that runs once.

Ng's insight about fast inference compounds with the staged build path. At the reflection stage, fast inference lets the loop run more iterations within the same latency budget. At the multi-agent stage, fast inference lets the orchestrator dispatch and receive results from workers faster, reducing end-to-end latency. At the graph stage, fast inference lets extraction agents process larger corpora in less time, building richer graphs that benefit all downstream agents. The speed of the model is not just a cost optimization — it is a capability multiplier that enables compound architectures that would be impractical with slow inference.
