---
type: pattern
domain: agentic-systems
status: current
created: 2026-08-09
updated: 2026-08-09
sources: ["ai-docs/graph-engineering/02-four-design-patterns.md", "ai-docs/graph-engineering/03-anthropic-five-workflows.md", "ai-docs/graph-engineering/06-implementation-guide.md", "ai-docs/graph-engineering/09-appendices-b-and-c.md"]
related: ["[[reflection-loop]]", "[[planning-agents]]", "[[workflow-patterns]]", "[[loops-to-graphs]]", "[[staged-build-path]]", "[[architecture-over-model]]"]
---

# Tool Use

Tool use lets an LLM select and call external capabilities — web search, code execution,
databases, APIs. The division of labor is stated plainly: the model contributes language
understanding and decision making, the tool contributes grounded data or deterministic
action ([playbook §II.B](../../graph-engineering/02-four-design-patterns.md)).
The consequence is that a model which can execute code can verify its own logic, and a
model which can search can ground its claims; the pattern converts a closed system into one
that can check its work against reality
([playbook §II.B](../../graph-engineering/02-four-design-patterns.md)).

Ng attributes the origin of the technique to the computer vision community, on the grounds
that language models could not manipulate images directly, so "the only option was that the
LLM generate a function call"
([playbook §II.B](../../graph-engineering/02-four-design-patterns.md)). Like
[[reflection-loop]], tool use is assessed as robust and widely deployed rather than emerging
([playbook §II.D](../../graph-engineering/02-four-design-patterns.md)).

## Four failure modes

Wrong tool selection: calling a search when a database query is the correct instrument.
Invalid arguments: passing malformed inputs the tool cannot process. Trusting tool output
blindly: incorporating a search result without checking relevance, or code execution output
without checking the returned type. Tool overuse: calling a tool when the context window
already holds sufficient information, spending tokens and latency for nothing
([playbook §II.B](../../graph-engineering/02-four-design-patterns.md)).

The named controls map one to one. Typed tool schemas with validated arguments catch the
first two. Result confirmation before incorporation catches the third. Retry limits bound
the cost of a tool-call loop that will not converge
([playbook §II.B](../../graph-engineering/02-four-design-patterns.md)).

## Permission boundaries and the read-first order

Separating read access from write access is treated as a schema property of the toolset
rather than a deployment detail
([playbook §II.B](../../graph-engineering/02-four-design-patterns.md)). The
build guidance makes the order explicit: start with read-only tools before adding write
access, on the analogy that a tool reading a database is safe to experiment with while a
tool modifying production data warrants the same permission controls applied to a junior
engineer ([playbook §VI.B](../../graph-engineering/06-implementation-guide.md)).

The production-readiness checklist adds a third question beside schema validation and
permission separation: what happens when the tool fails or rate-limits
([playbook App. B](../../graph-engineering/09-appendices-b-and-c.md)). That
fallback path is not only defensive. Ng's live demo has a research agent hit a rate-limit
error on its web search API and pivot to a Wikipedia tool he had forgotten he provided
([playbook §II.C](../../graph-engineering/02-four-design-patterns.md)); the
build guide names that rerouting moment as one of the clearest signals the agentic
architecture is adding value a fixed script could not
([playbook §VI.B](../../graph-engineering/06-implementation-guide.md)).

## Position in the stack

Anthropic's mapping treats tool use not as one workflow among five but as the augmented LLM
— the building block all five workflows are assembled from
([playbook §III](../../graph-engineering/03-anthropic-five-workflows.md)). This
is why it sits at day two of the [[staged-build-path]], immediately after reflection and
before any decomposition: [[planning-agents]] select among tools, and the graph stage in
[[loops-to-graphs]] is reached by giving agents a tool that reads and writes durable state.

In the worked code-review example, granting the reviewer agent the ability to execute the
test suite and read linter output moves measured accuracy from 72% to 84%, and changes the
character of the output — reviews cite concrete test failures instead of hypothetical bugs
([playbook App. C](../../graph-engineering/09-appendices-b-and-c.md)).
