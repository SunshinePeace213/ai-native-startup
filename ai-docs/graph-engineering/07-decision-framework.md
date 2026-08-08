---
source: raw/Graph-Engineering-Andrew-Ng-Playbook.pdf
fetched: 2026-08-05
pages: 7-8
---
> **In here:** When to use each pattern (Table V) · Five decision rules · Seven anti-patterns to avoid

# VII. Decision Framework

### Table V — When to Use Each Pattern

| Situation | Start With | Why |
| --- | --- | --- |
| Better output quality | Reflection | Cheapest, most reliable improvement |
| Need external data | Tool Use | Grounds answers in real information |
| Complex multi-step | Planning | Decomposes into manageable steps |
| Multiple perspectives | Multi-Agent | Different roles catch different errors |
| Cross-session state | Graph arch. | Survives context window flushes |
| Simple single QA | Zero-shot | Don't over-engineer |

The rule of thumb: if the current pattern's failure mode is understood and the next pattern addresses that specific failure, add it. If the failure mode is unclear, measure before adding complexity. Each pattern adds cost, latency, and debugging surface. The cheapest pattern that satisfies the task is usually the right one.

## A. Five Decision Rules

Five rules formalize the decision framework for practitioners.

*Rule 1: Start with the cheapest pattern.* A reflection loop is cheaper than a multi-agent system, and a multi-agent system is cheaper than a graph architecture. Start with the cheapest and add complexity only when a specific, measured failure demands it.

*Rule 2: Measure before promoting.* Before adding the next pattern, establish a baseline with the current pattern and measure the failure rate you expect the new pattern to address. If the failure rate is below 5%, the new pattern's complexity cost likely exceeds its benefit.

*Rule 3: Match control to risk.* High-stakes tasks (financial transactions, safety-critical operations) should use predictable patterns (chains, evaluation loops) with explicit gates. Low-stakes tasks (brainstorming, research drafts) can tolerate the unpredictability of planning and multi-agent systems.

*Rule 4: Count tokens, not agents.* The cost of an agentic system is proportional to tokens consumed, not to the number of conceptual agents. A three-agent system where each agent runs for 20,000 tokens costs the same as one agent running for 60,000 tokens. Design for token efficiency, not conceptual elegance.

*Rule 5: The graph earns itself.* A knowledge graph is justified when the same entity or relationship is queried by more than one agent or across more than one session. A graph that is written to once and never queried is a database table with extra overhead.

## B. Anti-Patterns to Avoid

Seven anti-patterns recur in production agentic systems.

**The everything-agent:** one agent with every tool, every role, and a 50-page system prompt that tries to handle all cases — this agent has no clear responsibility and no clear failure mode, making it impossible to debug.

**The echo chamber:** multiple agents with identical prompts and identical evidence producing identical outputs at higher cost — more agents does not mean more intelligence.

**The infinite loop:** a reflection or planning agent without a stopping rule that iterates until the token budget is exhausted, producing marginal stylistic changes rather than substantive improvements.

**The phantom graph:** a knowledge graph with an elaborate ontology that no agent ever queries — infrastructure cost without value.

**The conversational bottleneck:** an orchestrator that receives every worker's full conversation transcript, growing its context linearly with team size until it exceeds the window.

**The missing baseline:** deploying an agentic system without first measuring the performance of a zero-shot call, so the team cannot tell whether the agentic overhead is producing lift or just cost.

**The premature agent:** building a multi-agent system for a task that a single well-prompted call handles perfectly, motivated by the architectural pattern rather than the task's requirements.
