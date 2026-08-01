---
paths:
  - "clients/**/*"
---

# Studio Roster

Every studio seat: the principal, who runs as the main session, and the nine roles it spawns as subagents. Model and effort come from [model-selection.md](../model-selection.md) — `fable` is orchestrator-only, so a spawned role escalates effort before model. `tests/harness-layer/test_studio_roster_drift.py` re-derives each stamp from this table, so a row and its agent file change together.

Every seat denies `Agent` — no role spawns another role. `studio-research-analyst` reads third-party sites the client named, so it carries a `tools:` allowlist instead; never widen that allowlist to `Bash`.

| Function | Person | Model | Effort | May escalate |
| --- | --- | --- | --- | --- |
| `principal` | Maya Lindqvist, Principal/CPO | `fable` | `xhigh` | No agent file — the main session holds this seat and is never spawned as a subagent |
| `studio-client-partner` | Daniel Osei | `sonnet` | `medium` | Effort to `high` when qualification or handoff is contested, then model to `opus` |
| `studio-discovery-lead` | Priya Raghavan | `opus` | `high` | Effort to `xhigh` on a sprawling brief; model is already at the subagent ceiling |
| `studio-ux-architect` | Tomas Vieira | `opus` | `high` | Effort to `xhigh` for the cold-designer pass; model stays `opus` |
| `studio-art-director` | Elena Ferraro | `opus` | `high` | Effort to `xhigh`; client-facing, so never below taste ≥ 7 |
| `studio-content-strategist` | Hana Okabe | `opus` | `high` | Effort to `xhigh`; client-facing, so never below taste ≥ 7 |
| `studio-prototype-engineer` | Marcus Bramley | `sonnet` | `high` | Model to `opus` after a revision round fails on the same fault twice |
| `studio-design-qa` | Yusuf Demir | `opus` | `high` | Effort to `xhigh` on a disputed finding; never down — this seat gates handoff |
| `studio-research-analyst` | Clara Nyberg | `sonnet` | `medium` | Effort to `high` on a crowded market; model to `opus` when the read is wrong, not thin |
| `studio-retro-scribe` | Ravi Chandran | `sonnet` | `medium` | Effort to `high` when lessons span several files; no model escalation |
