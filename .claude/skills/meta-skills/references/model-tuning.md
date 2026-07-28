# Model Tuning: The Subtraction Pass

A subagent stamps one model and is written for it. A skill is different: its body
loads into whatever model runs the session, so it has to survive every reader.
Run the pass against the **union** — cut what any Claude 5 model already does,
and never ship what any of them is hurt by.

Delete first, then add.

## Delete — no reader needs these

| Cut | Why |
| --- | --- |
| Verification steps, "double-check", "re-verify before responding" | Opus 5 and Sonnet 5 self-verify and self-correct. The instruction compounds into over-verification and wastes turns without improving the result |
| "Think harder", "be thorough", "take your time" | Depth is `effort`. Prose does not buy it |
| Forced progress cadence ("summarize every 3 tool calls") | All three pace their own updates; Sonnet 5's are already well-calibrated |
| A rigid numbered script, when order is not load-bearing | Prescriptive bodies measurably degrade Fable 5. State the goal and its constraints and let the model find the path |
| Any instruction to explain, echo, or show *its own* reasoning | Refusal hazard on Fable 5 — see below |
| Qualitative bars on a finder ("only report important issues", "be conservative") | Sonnet 5 and Opus 5 obey literally and silently drop real findings. Ask for full coverage with a severity and confidence per finding, and filter in a later pass |
| Lines stating what the model already does ("write clean code", "handle edge cases") | Signal is only what pushes a reader off its defaults |

## Add — the deltas worth their tokens

| Add | Because |
| --- | --- |
| The explicit scope of each instruction — "apply this to every section, not just the first" | Sonnet 5 reads literally and will not generalize from one item to the rest |
| A boundary on what the skill must not touch | Opus 5 widens task scope; Fable 5 can take unrequested actions |
| Length calibration, when the skill writes documents to disk | Opus 5's written deliverables run long by default |
| A delegation cap, when the skill spawns subagents | Opus 5 and Fable 5 both delegate readily; a small task fans out into several |
| "Audit each progress claim against a tool result from this session", for skills that drive long unattended runs | Near-eliminates fabricated status reports |

## The Fable reasoning-echo hazard

A line telling the model to explain, transcribe, or show *its own* reasoning can
trigger the `reasoning_extraction` refusal on Fable 5 and silently fall back to
Opus 4.8 — a worse model with no error surfaced. Asking about the reasoning
behind a *finding* or a *change* is unaffected; the hazard is second-person
self-reasoning. `scripts/validate.py` fails on this pattern.

## Haiku is the exception

`haiku` is the one tier where a precise, ordered script still beats goal-and-
constraints. A skill stamped `model: haiku`, or one you expect to run mostly in
cheap utility sessions, can carry the step list the other tiers don't want.

## Stamping `model` and `effort`

Both are optional and both revert on the next user prompt. Leave them unset and
inherit the session unless the skill has a floor:

- Stamp `model` when the work needs a tier the session may not be on — anything
  user-facing needs taste ≥ 7, which rules out `haiku`. Aliases only.
- Stamp `effort` when the skill's quality demonstrably depends on it, not to
  save tokens. A step that runs unattended, or whose job is verification, never
  goes below `medium`.

Both come from [model-selection.md](../../../rules/model-selection.md).

## When output misses the bar

Fix the prompt, the context, and the scoping first — a starved skill looks like
an under-powered one. After that: it didn't *know* enough (subtle bug,
unfamiliar domain, confidently wrong) → raise `model`; it didn't *try* hard
enough (skipped a file, skipped the tests, stopped early) → raise `effort`.
Never add prose to buy either one.
