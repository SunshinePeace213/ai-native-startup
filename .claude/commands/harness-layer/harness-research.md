---
description: Discovery research pass — turn a vague mission into 3-5 focused questions, fan out modality-diverse searchers that return typed claims, merge into a provenance-tiered claims ledger with a verify edge, and hand the plan an improved prompt. Quick tier answers a single factual question inline; deep tier (only on explicit request) adds a contrarian searcher, loop-until-dry, and a completeness critic.
argument-hint: [mission] [quick|standard|deep]
model: fable
effort: high
disable-model-invocation: true
---

# Harness Research

Turn `MISSION` into grounded claims a plan can lock decisions on. Scoping is the
load-bearing step: convert the vague mission into focused questions BEFORE any
fan-out — every downstream artifact traces to one of those questions. The plan
command's Domain Knowledge step remains the always-on narrow verifier for
harness-behavior claims; this pass is the heavier machine for new domains, vague
topics, and conflicts.

## Variables

MISSION: $1 — the research mission, however vague
TIER: $2 — `quick` | `standard` (default) | `deep`; `deep` only when the user explicitly asks

## Tiers

| Tier | When | Shape |
| --- | --- | --- |
| `quick` | A single factual question | Answer inline from the KB or one WebSearch/WebFetch — no fan-out, no ceremony, no research.md |
| `standard` | Vague mission, unfamiliar domain, or a source-vs-memory conflict | scope → 3 searchers → claims ledger → verify edge → brief; one pass |
| `deep` | Only on explicit request | standard + a contrarian searcher + loop-until-dry (stop after 2 rounds surfacing nothing new) + a completeness critic ("what modality wasn't run, what claim is unverified, what source is unread?") |

## Workflow (standard)

1. **Scope** — distill `MISSION` into 3–5 focused, answerable questions (the
   "find all X that report Y" shape, never "find something interesting").
   Check `ai-docs/wiki/index.md` for pages already covering a question.
2. **Fan out (Workflow diamond)** — one searcher per modality, each blind to the
   others, each returning TYPED claims only —
   `{claim, source_url, tier, date, confidence, quote}` — raw transcripts never
   cross the merge:
   - **KB + repo reader** — the `ai-docs/` wiki + raw sources and this repo's own code/specs
   - **Official-docs searcher** — current vendor docs and references (WebFetch)
   - **Web/community searcher** — blogs, forums, issues, with reproducible evidence
3. **Merge into the claims ledger** — one row per claim. A conflict that
   survives fetching is REPRESENTED, never averaged: both rows stay, linked
   `contradicts C<n>`, and the brief hands the choice to the user or records an
   assumption with its invalidation condition.
4. **Verify edge** — re-check every load-bearing claim (anything a plan would
   lock a decision on) against a QUOTED source line; unverifiable → downgrade to
   risk note or open question.
5. **Bridge & write** — apply the KB durability rule (below), then write
   `specs/<slug>/discovery/research.md`: the questions, the ledger, a short
   synthesis per question, and open unknowns routed to
   `/harness-layer:harness-interview` or recorded as assumptions. Commit
   `📝 docs(discovery): research pass for <slug>` (no issue footer) on the
   chain's worktree.
6. **Hand off** — end with the improved plan prompt (mission rewritten with the
   locked findings, open questions, and the research.md path), ready to paste
   into the next pass or `/harness-layer:harness-plan`.

## Conflict precedence

Authority descends; recency wins within a tier; model memory is at the bottom —
it can trigger a fetch, never win one. A memory-vs-source conflict is always
resolved by fetching, and the ledger records the correction.

| Tier | Source | Standing |
| --- | --- | --- |
| T1 | Official docs/reference, dated, fetched now | Beats everything, including stale mirrors |
| T2 | KB archive ≤ 30 days | Beats memory; loses to a fresher official page — re-archive via `source-archiver`, the fresh archive wins |
| T3 | Official blog / changelog | Beats community and memory |
| T4 | Reputable community with reproducible evidence | Beats memory only; never locks a decision alone — record as risk |
| — | Model memory | Cites nothing |

## Claims ledger format

```markdown
| # | Claim | Source (tier · date) | Conf | Status |
| C1 | <claim> | T2 KB archive · 2026-07-21 | 95 | verified |
| C2 | <claim> | T1 official docs · fetched <date> | 90 | verified — corrected model memory |
| C3 | <claim> | T4 forum · 2026-07 | 55 | risk note — not load-bearing |
| C4 | <claim> | — | — | unanswered → interview question / assumption |
```

Footer line: `Open questions carried forward: <n> · KB archives added this pass: <n>`.

## KB durability rule

Would a future, unrelated plan cite this exact page?

- Yes, and it's an official page → archive it into `ai-docs/` via a
  `source-archiver` subagent; `/wiki:ingest` crystallizes it later.
- No — synthesis, comparison, judgment → it stays in
  `specs/<slug>/discovery/research.md`, plan-scoped.
- Raw search results and transcripts → nowhere; they die with their searcher.
- Lessons about researching itself → the lessons digest.
