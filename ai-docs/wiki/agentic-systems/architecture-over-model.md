---
type: topic
domain: agentic-systems
status: current
created: 2026-08-09
updated: 2026-08-09
sources: ["ai-docs/graph-engineering/05-benchmark-evidence.md", "ai-docs/graph-engineering/01-abstract-and-introduction.md", "ai-docs/graph-engineering/10-limitations-adoption-conclusion.md", "ai-docs/graph-engineering/08-graphs-vs-loops-debate.md"]
related: ["[[staged-build-path]]", "[[reflection-loop]]", "[[pattern-selection]]", "[[loops-to-graphs]]", "[[multi-agent-collaboration]]"]
---

# Architecture Over Model

The empirical claim the playbook is built on: workflow architecture matters more than model
capability ([playbook §XI](../../graph-engineering/10-limitations-adoption-conclusion.md)).
The evidence is a single HumanEval comparison reported by Ng — GPT-3.5 zero-shot at 48.1%,
GPT-4 zero-shot at 67.0%, and GPT-3.5 inside an agentic workflow at 95.1%
([playbook Table III](../../graph-engineering/05-benchmark-evidence.md)). The
generation upgrade moves the score 18.9 points; the workflow moves it 47.0. Ng's summary is
that the improvement from GPT-3.5 to GPT-4 "is dwarfed by incorporating an iterative agent
workflow" ([playbook §V](../../graph-engineering/05-benchmark-evidence.md)).

The prescriptive form is that a team waiting on the next model generation may reach
comparable performance sooner by applying agentic reasoning to the model it already has
([playbook §V](../../graph-engineering/05-benchmark-evidence.md)). The
underlying argument is not that direct prompting is useless but that many tasks become
substantially more reliable when the model sits inside a workflow permitting iteration,
evidence gathering, decomposition, and role separation
([playbook §I](../../graph-engineering/01-abstract-and-introduction.md)).

## Model choice and workflow design are coupled

The less-discussed implication is that these are not independent decisions. If a weaker model
with a strong process outperforms a stronger model asked to answer once, the optimal system
is not necessarily the strongest model in the simplest workflow — it may be a cheaper, faster
model in a compound workflow that spends the savings on more iterations, more workers, or
more evaluation rounds
([playbook §V](../../graph-engineering/05-benchmark-evidence.md)). The
playbook treats this as the economic argument for the [[staged-build-path]]: each stage's cost
must be justified by measurable lift
([playbook §V](../../graph-engineering/05-benchmark-evidence.md)).

## Generation speed is a capability multiplier

Ng's stated reason is that in an agentic system the LLM generates tokens for other LLMs to
read rather than for humans, so generation speed is not bounded by reading speed
([playbook §V](../../graph-engineering/05-benchmark-evidence.md)). Faster
tokens from a slightly weaker model may beat slower tokens from a better one "because it may
let you go around this loop a lot more times"
([playbook §V](../../graph-engineering/05-benchmark-evidence.md)).

The effect compounds along the build path. At the reflection stage, speed buys more iterations
inside the same latency budget; at the multi-agent stage, faster dispatch and return from
workers cuts end-to-end latency; at the graph stage, extraction agents process larger corpora
in less time, producing richer graphs that every downstream agent reads
([playbook §V](../../graph-engineering/05-benchmark-evidence.md)). Since a
compound system running a planner, a coder, a reviewer, and a graph can consume 10–50× the
tokens of a single direct call, fast inference at acceptable quality is what makes such
architectures economically viable rather than only theoretically interesting
([playbook §VIII.A](../../graph-engineering/08-graphs-vs-loops-debate.md)).

## What the number does not establish

Three limits are stated on the claim. HumanEval is a coding benchmark, and 95.1% should not
be assumed to transfer to other domains — teams are told to build their own evaluation sets
and measure lift in their own context
([playbook §IX](../../graph-engineering/10-limitations-adoption-conclusion.md)).
Agentic workflows trade latency for quality, with Ng framing the adjustment as learning "to
delegate tasks to an AI agent and patiently wait minutes, maybe even hours, for a response"
([playbook §IX](../../graph-engineering/10-limitations-adoption-conclusion.md)).
And every iteration costs tokens, so added agents do not automatically add intelligence
([playbook §IX](../../graph-engineering/10-limitations-adoption-conclusion.md)) —
the constraint [[pattern-selection]] turns into the rule to count tokens rather than agents.

Two of the four patterns the argument depends on are also assessed as immature. Ng calls
planning and [[multi-agent-collaboration]] emerging rather than robust, and says he cannot
always get them to work reliably
([playbook §IX](../../graph-engineering/10-limitations-adoption-conclusion.md)).
The architecture-over-model result therefore rests most solidly on the patterns at the
beginning of the build path — [[reflection-loop]] and tool use — which is consistent with the
guidance not to skip stages, and with the graph sitting at the far end of [[loops-to-graphs]].
