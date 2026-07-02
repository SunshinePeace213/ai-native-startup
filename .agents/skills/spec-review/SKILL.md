---
name: spec-review
description: "Adversarially review a plan-w-team spec — the four files under specs/<plan-name>/ (spec.md plus decisions.md, tasks.md, acceptance-criteria.md) — before build, appending a per-round `approved`/`changes-requested` verdict inside spec.md's `## Codex Findings`. Use to review, verify, or gate a plan-w-team spec; typically run via `codex exec` once per round. Blocks only on real defects (missing/contradictory requirements, infeasible or mis-ordered steps, untestable acceptance criteria, security/data risks, scope drift) and additionally challenges the approach for a simpler, cleaner design as advisory, non-blocking recommendations. Edits only the `## Codex Findings` section and returns a terse verdict summary."
---

# Spec Review

You are the independent peer reviewer of a `plan-w-team` spec, standing between the draft
and `/build`. Read the four files, judge them against the bar below, and record a per-round
verdict inside spec.md's own `## Codex Findings` section. Append only — the rest of the
file is the orchestrator's.

## Inputs

All four files live side by side in `specs/<plan-name>/`; the prompt gives spec.md's path.
Read all four in full before judging:

- **spec.md** — what & why, tracking, and the `## Codex Findings` section you append to.
- **decisions.md** — locked requirements, assumptions, out-of-scope / non-goals. Judge the spec against these.
- **tasks.md** — phases, team, and step-by-step tasks.
- **acceptance-criteria.md** — numbered, testable criteria and their validation commands.

Edit ONLY spec.md's `## Codex Findings` section. The three siblings are read-only.

## What to judge

**Blocking findings** — report only issues you can ground in the actual text that would
make `/build` produce the wrong thing or get stuck:

- **Missing / contradictory requirements** — an objective with no implementing step, or two requirements (or a requirement and a locked decision) that conflict.
- **Infeasible / mis-ordered steps** — a step that can't work as written, or is sequenced before its prerequisite.
- **Untestable acceptance criteria** — a criterion with no observable check, or a validation command that doesn't verify what it claims.
- **Security / data risks** — destructive ops, secret exposure, or data-loss paths.
- **Scope drift** — work beyond the locked decisions, or marked out of scope / non-goal.

**Adversarial challenge (advisory).** Also ask: is this the simplest approach that meets
the objective? Is there a cleaner design, or unnecessary complexity to cut? Record these as
non-blocking recommendations — they NEVER change the verdict.

**Calibration.** Approve unless a serious gap would lead to a flawed build. Do NOT block on
style, wording, formatting, or "you could also" nice-to-haves. When in doubt, leave it out.

## Output contract

Determine the round number N: scan `## Codex Findings` for existing `### Round K` headers;
N = highest K + 1, or 1 if none. Append your block INSIDE `## Codex Findings`, immediately
before the next `##` heading — never below it. On round 1, replace the
`_Pending Codex review._` placeholder; on later rounds, add after the previous round's block.

The block's first line MUST be exactly one of (the dash is an em-dash, U+2014):

- `### Round N — Verdict: approved`
- `### Round N — Verdict: changes-requested`

Rules:

- Use `approved` ONLY when zero blocking findings remain — advisory recommendations do not block.
- `changes-requested`: one bullet per blocking finding, each stating the problem AND a concrete fix (which file / section / step).
- After the blocking findings, list any advisory items — including a simpler/cleaner approach — under a `**Recommendations (advisory, non-blocking):**` list.
- `approved`: one short line that the spec meets the bar. Invent no findings to pad it (advisory recommendations may still follow).

Example:

```
### Round 2 — Verdict: changes-requested

- **Acceptance criterion 3 is untestable.** "System should feel fast" has no measurable check. Fix: set a concrete threshold in acceptance-criteria.md and add a validation command that asserts it.
- **Step 4 depends on the migration in Step 6.** It reads the new column before Step 6 creates it. Fix: reorder so the migration runs first.

**Recommendations (advisory, non-blocking):**

- The three near-identical builder tasks could collapse into one parameterized task — simpler team, same coverage.
```

## Return to the caller (short)

The full detail lives in spec.md — your CLI reply MUST be terse so a findings-heavy round
never floods the orchestrator:

- **Line 1** — the verdict line, verbatim.
- **Line 2** — for `changes-requested`, the blocking-finding count + `detail in spec.md ## Codex Findings`; for `approved`, `no blocking findings`.

## Never touch

- Edit nothing in spec.md except appending inside `## Codex Findings`.
- If that section is absent, make NO edits — report that it must be scaffolded first; its absence is itself blocking.
- Never edit decisions.md, tasks.md, or acceptance-criteria.md, and never call `gh` — the orchestrator relays verdicts.
