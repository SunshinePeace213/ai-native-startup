---
source: raw/Graph-Engineering-Andrew-Ng-Playbook.pdf
fetched: 2026-08-05
pages: 8-9
---
> **In here:** Three criteria that make a graph necessary · Start with a loop, add graph at the failure point · The compound architecture

# VIII. The Graphs vs. Loops Debate

The July 2026 debate crystallized around a real question: when does a loop stop being sufficient and a graph become necessary? The answer maps onto three criteria. First, **session persistence**: if the work spans multiple sessions and transcript replay is no longer practical, state needs to live outside the context window — the graph. Second, **cross-agent coordination**: if multiple specialized agents must share facts without copying entire transcripts through a bottleneck, the graph is the shared blackboard. Third, **traceability**: if the system must explain why a result changed, provenance on typed edges is the infrastructure.

Loops handle the first criterion poorly (state lives in-context and is flushed), the second not at all (a loop is one agent), and the third weakly (the conversation history is the only record). Graphs handle all three structurally. But loops are simpler to build, cheaper to run, and sufficient for the vast majority of single-agent, single-session tasks. The engineering decision is not "which is better" but "when does the loop's limitation become the binding constraint."

The practical answer from the community's experience: start with a loop, measure where it fails, and add graph infrastructure at the specific failure point — not before. A loop with a state file is already partway to a graph. A graph that nobody queries is an overengineered loop.

The new DeepLearning.AI course makes the graph stage accessible. Previously, building a knowledge graph required expertise in graph databases, ontology design, and NLP extraction pipelines. The course shows that with modern tools (Google ADK for agent orchestration, Neo4j for graph storage, and an LLM for extraction), a working agentic knowledge graph can be built in under an hour. This dramatically lowers the bar for teams considering the transition from loops to graphs, while the decision framework above ensures they make the transition at the right time.

## A. The Compound Architecture

In practice, production systems rarely use one pattern in isolation. The most effective architectures compound patterns: a planning agent that uses reflection at each step, tool use for evidence gathering, multi-agent collaboration for review, and graph architecture for persistence. The compound effect is where the real performance lives — not in any single pattern, but in the specific combination tuned to the task. The build path described in Section VI is designed to make this compounding incremental and measurable rather than all-at-once and opaque.

Ng's insight about fast token generation is especially relevant for compound architectures. In a system where a planning agent generates a plan, a coder agent implements each step, a reviewer agent critiques each implementation, and a graph stores the results, the total token consumption can be 10–50× a single direct call. Fast inference at acceptable quality — "generating more tokens quickly from even a slightly lower quality LLM might give good results compared to slower tokens from a better LLM" — makes these compound systems economically viable rather than theoretically interesting.
