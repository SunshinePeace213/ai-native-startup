---
type: failure-mode
domain: engineering
status: current
created: 2026-08-08
updated: 2026-08-08
sources: ["ai-docs/llm-wiki/lucianfialho/graphwiki-pattern.md", "ai-docs/llm-wiki/rohitg00/llm-wiki.md", "ai-docs/llm-wiki/farzaa/wiki-gen-skill.md", "ai-docs/llm-wiki/karpathy/llm-wiki.md"]
related: ["[[llm-wiki-pattern]]", "[[knowledge-lifecycle]]", "[[page-writing-standards]]", "[[wiki-index-and-log]]"]
---

# Wiki Drift

Drift is the maintaining agent under-updating cross-references or status during ingest, and
it is reported as the most common failure mode for the [[llm-wiki-pattern]] in either
storage form, markdown or graph
([graphwiki](../../llm-wiki/lucianfialho/graphwiki-pattern.md)). It is the specific way the pattern
fails, and it is the mirror image of the pattern's own argument: the case for an LLM
maintainer rests on bookkeeping being the burden that kills human wikis
([Karpathy](../../llm-wiki/karpathy/llm-wiki.md)), so bookkeeping the agent quietly skips is the
thing that returns the wiki to the state the pattern promised to fix.

The failure is silent by construction. An ingest that writes a good page but forgets to
update the two pages that should now link to it produces no error, no broken link, and no
visible symptom on the page just written. It shows up only in aggregate, which is why every
variant of the pattern pairs ingest with a separate sweep.

## Symptoms

The checks each variant runs name the observable forms. The base pattern's health check
looks for contradictions between pages, stale claims newer sources have superseded, orphan
pages with no inbound links, concepts mentioned without a page of their own, missing
cross-references, and data gaps a web search could fill
([Karpathy](../../llm-wiki/karpathy/llm-wiki.md)). The graph variant checks orphaned concept nodes
with no relationships at all, unresolved contradiction pairs, entity-resolution judgments a
human has not spot-checked, and staleness measured as sources or concepts untouched by a
re-ingest in N days ([graphwiki](../../llm-wiki/lucianfialho/graphwiki-pattern.md)).

One of those is framed differently from the rest. Unresolved contradictions are described
as not necessarily a problem to fix, but every one should be a deliberate state rather than
a forgotten one ([graphwiki](../../llm-wiki/lucianfialho/graphwiki-pattern.md)). That distinction —
between a wiki that holds an open dispute on purpose and one that merely never resolved it
— is what the status field in [[knowledge-lifecycle]] exists to record.

## Scheduled beats remembered

The strongest claim about remedies is about when the sweep runs rather than what it checks.
Lint should run on a schedule through cron or CI rather than only when someone remembers to
ask, and the graph stays healthy in proportion to how automatic that check is
([graphwiki](../../llm-wiki/lucianfialho/graphwiki-pattern.md)). The same conclusion arrives from the
production side as a general complaint that everything in the original is manual — the human
drops a source and tells the LLM to process it, remembers to run lint periodically, and
decides when to file an answer back — with periodic lint, consolidation, and retention decay
listed among the events that should fire on a schedule
([LLM Wiki v2](../../llm-wiki/rohitg00/llm-wiki.md)).

## Self-healing rather than reporting

A second remedy changes what lint does when it finds something. The proposal is that lint
should be more than a suggestion and should automatically fix what it can: orphan pages get
linked or flagged, stale claims get marked, and broken cross-references get repaired, so the
wiki tends toward health on its own ([LLM Wiki v2](../../llm-wiki/rohitg00/llm-wiki.md)).
Contradiction handling is pushed a step further than flagging. The LLM should propose which
claim is more likely correct based on source recency, source authority, and the number of
supporting observations, with the human able to override but the default expected to be
right ([LLM Wiki v2](../../llm-wiki/rohitg00/llm-wiki.md)).

Quality scoring is offered as the preventive counterpart. Every piece of content the LLM
writes gets a score for whether it is well structured, cites sources, and is consistent with
the rest of the wiki — self-evaluated or judged by a second pass with a different prompt —
and content below a threshold is flagged for review or rewritten
([LLM Wiki v2](../../llm-wiki/rohitg00/llm-wiki.md)). Without such controls the stated outcome is that
the wiki accumulates noise ([LLM Wiki v2](../../llm-wiki/rohitg00/llm-wiki.md)), the same junk-drawer
failure that lifecycle management is meant to prevent.

## Drift inside the pages

Not all degradation is in the link graph. The page-level form is structural: articles that
started as synthesis decay into chronological dumps as entries are appended, which is why
the most prescriptive instantiation makes a periodic re-read part of the loop rather than a
separate cleanup ([wiki skill](../../llm-wiki/farzaa/wiki-gen-skill.md)). Its audit picks the three
most-updated articles and asks whether each still tells a coherent story, has theme-based
sections, and teaches a reader something non-obvious, with the instruction to rewrite any
that reads like an event log ([wiki skill](../../llm-wiki/farzaa/wiki-gen-skill.md)).

That audit is aimed at the most-updated articles specifically, which is the population most
exposed to the failure. Cramming is measured the same way: zero new articles across the last
15 entries is read as evidence the maintainer has been appending rather than creating
([wiki skill](../../llm-wiki/farzaa/wiki-gen-skill.md)). Both checks and the standards they enforce
are in [[page-writing-standards]]. A per-article sweep run by parallel subagents also
assesses tone, quote density, line count, narrative coherence, and broken or missing
wikilinks, and restructures rather than reports
([wiki skill](../../llm-wiki/farzaa/wiki-gen-skill.md)).

## The human counterpart

A visual check runs alongside the automated one. The graph view of a vault is described as
the best way to see the shape of a wiki — what is connected to what, which pages are hubs,
and which are orphans ([Karpathy](../../llm-wiki/karpathy/llm-wiki.md)) — which makes orphan
detection something a reader notices at a glance and a linter counts. That pairing is why
the pattern's two programs, the maintainer and the reading surface, both bear on drift.
