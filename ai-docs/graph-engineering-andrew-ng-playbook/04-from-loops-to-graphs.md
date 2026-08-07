---
source: Graph-Engineering-Andrew-Ng-Playbook.pdf
fetched: 2026-08-05
pages: 5-6
---
> **In here:** Loop → chain → network → graph stages · Three roles a knowledge graph plays · Minimal five-node schema and its failure modes

# IV. From Loops to Graphs

The combined pattern vocabulary describes a progression in how state, control, and responsibility are organized. The progression is not a maturity ladder every project must complete; many tasks should remain direct calls or fixed chains.

## A. The Loop Stage

One agent repeatedly inspects and revises its own work. Reflection is the defining mechanism, often supported by tools. The loop is compact, easy to prototype, and effective for tasks within one context window. It breaks down when the task contains too much evidence, too many independent concerns, or too much history. Every iteration may resend task, draft, critique, tool results, and prior decisions — context becomes expensive and noisy. The loop's strength is also its limitation: everything lives in one context window, which means everything must fit in one context window. When it doesn't, the options are to truncate (losing information), summarize (losing precision), or restructure — which leads to the chain.

## B. The Chain Stage

Work is divided into a fixed sequence of specialized transformations. The chain externalizes order into application code. Each stage can have its own prompt, model, tools, and validation. Compared with a reflective loop, the chain is more predictable because the path is known. The limitation: unexpected cases must be anticipated. A chain that processes documents through "extract → validate → summarize → format" works perfectly when every document fits the expected structure. When a document is in an unexpected format, the chain either fails at the extraction stage (good — the failure is visible and early) or passes garbled output forward (bad — the failure compounds silently through every subsequent stage). Programmatic gates between stages are the fix: each gate checks whether the output of the previous stage meets the input contract of the next, and routes failures to a fallback rather than letting them propagate.

## C. The Network Stage

Multiple role-specialized workers are introduced. An orchestrator delegates, workers act, results return for synthesis. The central limitation is context management. As Anthropic notes: "context grows too complex for one agent to manage effectively, creating performance bottlenecks." The orchestrator may become a conversational hub receiving every worker's full output. The context management problem scales quadratically with team size: with 5 workers, the orchestrator must hold 5 outputs; with 10 workers, 10 outputs; and each output may itself be the product of a multi-turn interaction. At some point the orchestrator's window is more summary than substance, and the summaries have lost the detail that matters. This is the moment that motivates the graph.

## D. The Graph Stage

The graph stage externalizes shared state into a durable, queryable structure (Fig. 1). Each worker reads the subgraph relevant to its task and writes new entities and relations back. The orchestrator's context stays small; the shared state lives in the graph. This is the architecture Ng's July 2026 course teaches students to build from scratch.

The course, taught by Neo4j's Andreas Kollegger and hosted on DeepLearning.AI, covers four progressions: (1) what agentic knowledge graphs are and why agents need them; (2) how to build the first agentic graph from raw data — entities as nodes, relationships as typed edges; (3) how multi-agent systems are architected on graph structures, with extraction agents feeding validated entities into a persistent store; and (4) building working implementations using Google's Agent Development Kit (ADK). The course positions knowledge graphs not as an advanced feature to add later but as a foundational component that should be designed from the beginning for any system requiring cross-session reasoning.

A knowledge graph serves multi-agent systems in three distinct roles. As **shared memory** for orchestrator-workers: workers read from and write to the graph directly, replacing the fragile alternative of passing summaries through the orchestrator's bottleneck. This is the multi-agent analogue of Anthropic's principle that "the session is not the context window." As **grounding layer** for evaluator-optimizer: the evaluator checks claims against graph edges with provenance, producing feedback like "triple (X, works_at, Y) does not exist in the graph; the graph contains (X, left, Y) from document Z" rather than "this seems off." As **persistent world model** for loops: the graph survives context-window flushes — the agent forgets, the graph does not.

## E. A Minimal Graph Schema

A useful schema begins with five node types: Entity (person, organization, product, concept), Claim (statement that may be supported or contradicted), Source (document, API response, test result), Artifact (plan, draft, code, report), and Run (execution record). Edges capture relationships: `mentions`, `supports`, `contradicts`, `derived_from`, `supersedes`. Every claim retains provenance. Every revision points to the prior version. The minimal write operation should be additive: rather than overwriting a claim silently, create a new version and link it with `supersedes`.

## F. Graph Architecture Is Not Automatic Truth

A graph can preserve errors as efficiently as facts. Entity resolution can merge distinct organizations. Extraction can attach the wrong date. A confident evaluator can mark a weak source as sufficient. Graph-grounded systems therefore require data quality mechanisms: schema validation, canonical identifiers, provenance, conflict representation, confidence calibration, and periodic review.
