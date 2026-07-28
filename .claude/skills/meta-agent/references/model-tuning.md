# Model Tuning: The Subtraction Pass

Read this after stamping `model` from
[model-selection.md](../../../rules/model-selection.md). The body you write
depends on which model runs it: each Claude 5 model has behavior you must not
duplicate in prose, and a short list of deltas worth adding.

Run the pass in this order — delete first, then add. Applies to Claude agents
only; a Codex agent's prompting lives in the `codex` plugin skills.

## Per model

| Stamped model | Delete from the body | Add to the body |
| --- | --- | --- |
| **`opus`** (Opus 5) | Verification steps, "double-check", "re-verify before responding" — it self-verifies and self-corrects, and the instruction compounds into wasted turns | A scope constraint (it widens tasks and adds unrequested steps); a delegation cap if it holds `Agent`; explicit length calibration if it writes documents to disk |
| **`sonnet`** (Sonnet 5) | Forced progress cadence; any qualitative bar on a finder ("important", "significant") | The explicit scope of each instruction — it reads literally and won't generalize from one item to the rest ("apply this to every section, not just the first") |
| **`haiku`** (Haiku 4.5) | Nothing | A precise, ordered script. This is the one tier where prescriptive instructions still beat goal-and-constraints. |
| **`fable`** (Fable 5) | Step-by-step scripts — prescriptive bodies written for earlier models measurably degrade its output. **Any instruction to explain, echo, or show its own reasoning** | An explicit boundary on what it must not touch (it can take unrequested actions); "audit each progress claim against a tool result from this session" for long runs; a memory-note protocol when `memory` is set |

## Fable and the reasoning-echo hazard

A line telling the model to explain, transcribe, or show *its own* reasoning can
trigger the `reasoning_extraction` refusal on Fable 5 and silently fall back to
Opus 4.8 — you get a worse model with no error. Asking about the reasoning behind
a *finding* or a *change* is unaffected; the hazard is second-person
self-reasoning. The validator fails on this pattern.

Per the roster, `fable` is orchestrator-only — never stamp it on a worker. Its
column applies when an agent file runs as the whole session (`--agent`) or
dispatches its own subagents.

## Delegation caps

Opus 5 and Fable 5 both delegate more readily than earlier models. Any agent
holding `Agent` in `tools` needs a cap, or a small task fans out into several:

```text
Delegate only work that is genuinely independent and too large to finish here.
Don't delegate what you'd finish in a handful of tool calls, and never spawn an
agent to verify your own output. One agent beats three.
```

## When output misses the bar

Fix the prompt, the context, and the scoping first — a starved agent looks like
an under-powered one. After that, the escalation heuristic in
[model-selection.md](../../../rules/model-selection.md) applies: it didn't *know*
enough (subtle bug, unfamiliar domain, confidently wrong) → raise `model`; it
didn't *try* hard enough (skipped a file, skipped the tests, stopped early) →
raise `effort`. Never add prose to buy either one.
