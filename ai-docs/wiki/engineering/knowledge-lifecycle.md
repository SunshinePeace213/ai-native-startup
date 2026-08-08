---
type: pattern
domain: engineering
status: current
created: 2026-08-08
updated: 2026-08-08
sources: ["ai-docs/llm-wiki/rohitg00/llm-wiki.md", "ai-docs/llm-wiki/lucianfialho/graphwiki-pattern.md", ".claude/rules/wiki-layer/wiki-standards.md"]
related: ["[[llm-wiki-pattern]]", "[[graph-wiki-variant]]", "[[wiki-drift]]", "[[wiki-governance]]"]
---

# Knowledge Lifecycle

The base [[llm-wiki-pattern]] treats every page in the maintained layer as equally valid
for as long as it exists. The counter-position is that knowledge has a lifecycle: a bug
found last week matters more than one from six months ago, a pattern seen twelve times is
more reliable than one seen once, and a claim from a newer source should weaken an older
one automatically ([LLM Wiki v2](../../llm-wiki/rohitg00/llm-wiki.md)). The machinery proposed for
that consists of four separable pieces — confidence, supersession, forgetting, and
consolidation tiers — drawn from running the pattern across thousands of sessions in a
persistent memory engine for coding agents
([LLM Wiki v2](../../llm-wiki/rohitg00/llm-wiki.md)).

## Confidence as a stored field

The proposal is that every fact carries a confidence score derived from how many sources
support it, how recently it was confirmed, and whether anything contradicts it — so a
claim such as "Project X uses Redis for caching" knows it came from two sources, was last
confirmed three weeks ago, and sits at 0.85
([LLM Wiki v2](../../llm-wiki/rohitg00/llm-wiki.md)). Confidence decays with time and strengthens
with reinforcement ([LLM Wiki v2](../../llm-wiki/rohitg00/llm-wiki.md)). The stated payoff is a
change in what the wiki can express: a flat collection of equally weighted claims becomes
a model in which the reader can be told the wiki is fairly sure about one thing and less
sure about another ([LLM Wiki v2](../../llm-wiki/rohitg00/llm-wiki.md)).

## Supersession keeps the loser

Both variant sources reject deletion as the resolution for a conflict, and they converge
on nearly the same state machine. New information that contradicts an existing claim should
explicitly supersede it, linked and timestamped, with the old version preserved and marked
stale — version control for knowledge rather than for files
([LLM Wiki v2](../../llm-wiki/rohitg00/llm-wiki.md)). The graph variant states the same rule as a
`status` field of `current | superseded | disputed`: two claims joined by an unresolved
contradiction are both `disputed`, and when a later source resolves it the losing claim
flips to `superseded` and is never deleted, so the store keeps its own history instead of
quietly rewriting the past ([graphwiki](../../llm-wiki/lucianfialho/graphwiki-pattern.md)).

Status only pays off if it survives to the point of use. The graph variant requires that
any cited claim or concept whose status is not `current` be flagged inline in the answer
rather than presented as settled ([graphwiki](../../llm-wiki/lucianfialho/graphwiki-pattern.md)).
Its author attributes that requirement to a comment on the original gist arguing that trust
should be graded and made to travel, so a stale or disputed page degrades honestly instead
of silently ([graphwiki](../../llm-wiki/lucianfialho/graphwiki-pattern.md)). This repository
implements exactly that pair of rules: the same three status values, both sides of a
contradiction flagged, and inline propagation wherever a non-`current` claim is cited
([wiki-standards.md](../../../.claude/rules/wiki-layer/wiki-standards.md)).

## Forgetting is deprioritization, not deletion

A wiki that never forgets is described as becoming noisy, and the proposed remedy is a
retention curve under which facts that were important once but have not been accessed or
reinforced in months gradually fade rather than being deleted
([LLM Wiki v2](../../llm-wiki/rohitg00/llm-wiki.md)). The named model is Ebbinghaus's forgetting
curve: retention decays exponentially with time, and each reinforcement — an access, or
confirmation from a new source — resets the curve
([LLM Wiki v2](../../llm-wiki/rohitg00/llm-wiki.md)). Decay rate is expected to vary by content
type, with architecture decisions decaying slowly and transient bugs decaying fast
([LLM Wiki v2](../../llm-wiki/rohitg00/llm-wiki.md)).

## Consolidation tiers

The fourth piece separates raw observation from established fact through a four-tier
pipeline: working memory for recent unprocessed observations, episodic memory for session
summaries compressed from them, semantic memory for cross-session facts consolidated from
episodes, and procedural memory for workflows and patterns extracted from repeated
semantics ([LLM Wiki v2](../../llm-wiki/rohitg00/llm-wiki.md)). Each tier is more compressed, more
confident, and longer-lived than the one below, and the LLM promotes information upward as
evidence accumulates — the mechanism by which "I saw this once" becomes "this is how things
work" ([LLM Wiki v2](../../llm-wiki/rohitg00/llm-wiki.md)).

## What this repository implements

Of the four pieces, this wiki implements supersession only. Its pages carry `status` with
the same three values and the same disputed-then-superseded transition, and status
propagates inline to every point of use
([wiki-standards.md](../../../.claude/rules/wiki-layer/wiki-standards.md)). There is no
confidence score, no decay, and no tiering; the only recency signal is the `updated:` field
each edit bumps ([wiki-standards.md](../../../.claude/rules/wiki-layer/wiki-standards.md)).
That matches the source's own staging advice, which places lifecycle as the first increment
after a minimal wiki and specifically credits it with preventing the wiki from becoming a
junk drawer ([LLM Wiki v2](../../llm-wiki/rohitg00/llm-wiki.md)). The junk-drawer failure and its
other forms are covered in [[wiki-drift]].
