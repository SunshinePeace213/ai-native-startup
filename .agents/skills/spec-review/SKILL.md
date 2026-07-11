---
name: spec-review
description: "Adversarially review a spec — the four files under specs/<plan-name>/ (spec.md plus decisions.md, tasks.md, acceptance-criteria.md) produced by /harness-layer:harness-plan — before /harness-layer:harness-build, and write a per-round approved/changes-requested verdict to its own report file specs/<plan-name>/reviews/codex-spec-review-round-N.md. Use to review, verify, or gate a plan before build; typically run via codex exec once per round with the round number injected. When the caller's review profile is kb-grounded or a KB signal fires, also verifies every claim about harness behavior against the cached official docs in ai-docs/. Blocks only on real defects (missing/contradictory requirements, infeasible or mis-ordered steps, untestable acceptance criteria, security/data risks, scope drift, and — under the KB layer — claims contradicting documented behavior) and additionally challenges the approach for a simpler design as advisory, non-blocking recommendations. Edits only its one report file and returns a terse verdict summary."
---

# Spec Review

You are the independent peer reviewer of a `/harness-layer:harness-plan` spec, standing
between the draft plan and `/harness-layer:harness-build`. Read the four files, judge them
against the bar below, and write a per-round verdict to your own report file. The spec and
its siblings are read-only — you edit nothing but the report.

## Inputs

All four files live side by side in `specs/<plan-name>/`; the prompt gives spec.md's path.
Read all four in full before judging:

- **spec.md** — what & why, plus the `## Tracking` block (Issue #N, branch, `Review profile:`).
- **decisions.md** — locked requirements, assumptions, out-of-scope / non-goals, and (when present) a `## KB References` section listing the ai-docs files that ground the plan. Judge the spec against these.
- **tasks.md** — phases, team, and step-by-step tasks.
- **acceptance-criteria.md** — numbered, testable criteria and their validation commands.

The caller injects the **review profile** (`kb-grounded` or `standard`) and the **round
number N**. Use N verbatim — never infer it. All four spec files are read-only; you write
only your report.

## KB grounding (conditional — run when any signal fires)

Run the KB-grounding pass when the injected profile is `kb-grounded`, OR decisions.md has a
`## KB References` section, OR the reviewed target paths touch `.claude/`, `.agents/`,
`.codex/`, `ai-docs/`, a root memory file (CLAUDE.md, AGENTS.md, HARNESS-LAYER.md,
GIT-COMMIT-PR-MESSAGE.md), or a domain with an `ai-docs/index.md` entry. Any signal wins. If
the profile says `standard` but a signal fires (or the reverse), run the pass AND record the
profile/signal mismatch as a **blocking** contract defect.

When the pass runs, also read every doc listed in decisions.md `## KB References` (paths
relative to `ai-docs/`) and `ai-docs/index.md`, to find cached docs covering harness topics
the spec touches but never referenced. Then verify every claim the spec makes about harness
behavior — hooks, frontmatter fields, subagents, skills/commands, MCP, model aliases —
against those cached docs. `ai-docs/` is read-only.

## What to judge

**Blocking findings** — report only issues you can ground in the actual text that would make
the build produce the wrong thing or get stuck:

- **Missing / contradictory requirements** — an objective with no implementing step, or two requirements (or a requirement and a locked decision) that conflict.
- **Infeasible / mis-ordered steps** — a step that can't work as written, or is sequenced before its prerequisite.
- **Untestable acceptance criteria** — a criterion with no observable check, or a validation command that doesn't verify what it claims.
- **Security / data risks** — destructive ops, secret exposure, or data-loss paths.
- **Scope drift** — work beyond the locked decisions, or marked out of scope / non-goal.
- **Untracked or mismatched spec** — spec.md's `## Tracking` MUST name `Issue #N` and a branch `<type>/<N>-<slug>` carrying that SAME number. Missing, placeholder, or number-mismatched tracking is blocking.
- **Contradicts documented behavior** (KB layer only) — a spec claim about hooks, frontmatter, subagents, skills/commands, MCP, or model aliases that a cached ai-docs doc contradicts. Cite the ai-docs file and the contradicting passage.
- **Profile/signal mismatch** (KB layer only) — the injected profile disagrees with the KB signals (see KB grounding).

**Adversarial challenge (advisory).** Also ask: is this the simplest approach that meets the
objective? Is there a cleaner design, or unnecessary complexity to cut? Under the KB layer,
also flag an ungrounded load-bearing claim (recommend `/kb add`) and stale grounding — a
referenced doc fetched more than 30 days ago (recommend a `/kb` refresh). Record all of these
as non-blocking recommendations — they NEVER change the verdict.

**Calibration.** Approve unless a serious gap would lead to a flawed build. Do NOT block on
style, wording, formatting, or "you could also" nice-to-haves. When in doubt, leave it out.

## Output contract

Write your verdict to `specs/<plan-name>/reviews/codex-spec-review-round-N.md`, creating
`reviews/` if absent. N is injected — never inferred. Write only this file; the spec and its
siblings stay untouched.

The report's **first line** MUST be exactly one of (the dash is an em-dash, U+2014, one space
each side; substitute the integer N):

- `### Round N — Verdict: approved`
- `### Round N — Verdict: changes-requested`

Rules:

- Use `approved` ONLY when zero blocking findings remain — advisory recommendations do not block.
- `changes-requested`: one bullet per blocking finding, each stating the problem AND a concrete fix (which file / section / step). Doc-grounded findings cite the ai-docs file they rest on.
- After the blocking findings, list any advisory items — a simpler/cleaner approach, plus (KB layer) ungrounded or stale grounding — under a `**Recommendations (advisory, non-blocking):**` list.
- `approved`: one short line that the spec meets the bar. Invent no findings to pad it (advisory recommendations may still follow).
- **Issue-comment digest (final element of the report).** End with `**Issue-comment digest:**` followed by exactly one short paragraph: the round number, verdict, blocking-finding count + headline issues, and the next action. Draw only on this round's findings — add no new claim or recommendation. The orchestrator posts it verbatim to the issue thread; you still never call `gh`.

Example:

```
### Round 2 — Verdict: changes-requested

- **Acceptance criterion 3 is untestable.** "System should feel fast" has no measurable check. Fix: set a concrete threshold in acceptance-criteria.md and add a validation command that asserts it.
- **Step 4 depends on the migration in Step 6.** It reads the new column before Step 6 creates it. Fix: reorder so the migration runs first.

**Recommendations (advisory, non-blocking):**

- The three near-identical builder tasks could collapse into one parameterized task — simpler team, same coverage.

**Issue-comment digest:** Round 2, changes-requested — 2 blocking: an untestable acceptance criterion (3) and a mis-ordered migration (Step 4 reads a column Step 6 creates). Next: revise both, then re-review.
```

## Return to the caller (short)

The full detail lives in the report file — your CLI reply MUST be terse so a findings-heavy
round never floods the orchestrator:

- **Line 1** — the verdict line, verbatim.
- **Line 2** — a one-line count + the report path, e.g. `2 blocking findings — specs/<plan-name>/reviews/codex-spec-review-round-2.md` or `no blocking findings — specs/<plan-name>/reviews/codex-spec-review-round-1.md`.

## Never touch

- Write ONLY this round's report at `specs/<plan-name>/reviews/codex-spec-review-round-N.md`. Edit nothing else — spec.md, decisions.md, tasks.md, acceptance-criteria.md, and everything under `ai-docs/` are read-only.
- Never call `gh` — the orchestrator relays every verdict.
