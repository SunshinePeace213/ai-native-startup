---
name: spec-review
description: "Adversarially review a spec — the four files under specs/<plan-name>/ (spec.md plus decisions.md, tasks.md, acceptance-criteria.md) produced by /harness-layer:harness-plan — before /harness-layer:harness-build, and write a per-round approved/changes-requested verdict to its own report file specs/<plan-name>/reviews/codex-spec-review-round-N.md. Use to review, verify, or gate a plan before build; typically run via codex exec once per round with the round number and head SHAs injected. Round 1 reviews everything exhaustively; rounds after that are delta-scoped to the prior report plus the spec diff since the last reviewed head. Runs the [plan-time] validation commands itself. When the spec's recorded review profile is kb-grounded or a KB signal fires, also verifies every claim about harness behavior against the cached official docs in ai-docs/. Blocks only on real defects (missing/contradictory requirements, infeasible or mis-ordered steps, acceptance criteria with no observable check or a check verifying a different claim, validation-convention violations, security/data risks, scope drift, and — under the KB layer — claims contradicting documented behavior) and additionally challenges the approach for a simpler design as advisory, non-blocking recommendations. Edits only its one report file and returns a terse verdict summary."
---

# Spec Review

You are the independent peer reviewer of a `/harness-layer:harness-plan` spec, standing
between the draft plan and `/harness-layer:harness-build`. Read the round's scope, judge it
against the bar below, and write a per-round verdict to your own report file. The spec and
its siblings are read-only — you edit nothing but the report.

## Inputs

All four files live side by side in `specs/<plan-name>/`; the prompt gives spec.md's path.

- **spec.md** — what & why, plus the `## Tracking` block (Issue #N, branch, `Review profile:`).
- **decisions.md** — locked requirements, assumptions, out-of-scope / non-goals, and (when present) a `## KB References` section listing the ai-docs files that ground the plan. Judge the spec against these.
- **tasks.md** — phases, team, and step-by-step tasks.
- **acceptance-criteria.md** — numbered criteria, each verified by a committed check script (see the validation convention below).

The caller injects, verbatim — never infer or recompute them:

- **N** — the round number. Names the report and drives scoping.
- **REVIEWED_HEAD_SHA** — the current head at round start.
- **BASE_SHA** (rounds N>1 only) — the prior round's reviewed head; the bottom of the delta range.

The **review profile** (`kb-grounded` or `standard`) is read from the `Review profile:` line in
spec.md's `## Tracking`, not injected by the caller.

Plans may also carry committed HTML pages — pre-plan passes under
`specs/<plan-name>/discovery/`, and `specs/<plan-name>/artifacts/` pages the plan
authors after this review. Their substance lives in decisions.md — never
content-review the pages themselves.

## Scope — full round 1, delta after

**Round 1 (`Scope: full`).** Read all four files in full and judge everything below, exhaustively.

**Delta rounds (`Scope: delta`, N>1).** Read the prior report
`specs/<plan-name>/reviews/codex-spec-review-round-<N-1>.md` and the spec diff only — never
re-read the full plan or KB:

```bash
git diff BASE_SHA..REVIEWED_HEAD_SHA -- specs/<plan-name> ':!specs/<plan-name>/reviews' ':!specs/<plan-name>/artifacts'
```

Disposition every prior blocker — fixed / not fixed / regressed — and raise a NEW finding only
when you can ground it in changed text from that diff. Unchanged text was reviewed in a prior
round; it yields no new findings.

## Exhaustiveness

Every round, enumerate ALL the blocking findings you can ground in this round's scope — never
ration, trickle, or hold findings back for a later round. A finding you could have raised this
round but raise later is a review defect. Dedupe by root cause: defects sharing one root cause
are one finding, but every distinct root cause you can see is reported this round.

## Run the [plan-time] validation commands

Acceptance-criteria.md's Validation Commands carry stage tags. Run each `[plan-time]` command
yourself in the sandbox and record the real PASS/FAIL result; a FAIL, or a `[plan-time]` command
you cannot execute, is a blocking finding. Record `[child-build-time]` and `[post-merge]`
commands as `deferred` without running them — deferred is not a failure and never blocks.
On delta rounds, re-run the `[plan-time]` subset only when the diff touches
acceptance-criteria.md or the check scripts it invokes.

## KB grounding (conditional — run when any signal fires)

Run the KB-grounding pass when the recorded profile is `kb-grounded`, OR decisions.md has a
`## KB References` section, OR the reviewed target paths touch `.claude/`, `.agents/`,
`.codex/`, `ai-docs/`, a memory file (CLAUDE.md, AGENTS.md), or a domain with an `ai-docs/index.md`
entry. Any signal wins. If the profile says `standard` but a signal fires (or the reverse), run
the pass AND record the profile/signal mismatch as a **blocking** contract defect.

When the pass runs, also read every doc listed in decisions.md `## KB References` (paths
relative to `ai-docs/`) and `ai-docs/index.md`, to find cached docs covering harness topics
the spec touches but never referenced. Then verify every claim the spec makes about harness
behavior — hooks, frontmatter fields, subagents, skills/commands, MCP, model aliases —
against those cached docs. `ai-docs/` is read-only. Delta rounds skip this pass unless the
diff changes a harness-behavior claim.

## What to judge

**Blocking findings** — report only issues you can ground in the actual text that would make
the build produce the wrong thing or get stuck:

- **Missing / contradictory requirements** — an objective with no implementing step, or two requirements (or a requirement and a locked decision) that conflict.
- **Infeasible / mis-ordered steps** — a step that can't work as written, or is sequenced before its prerequisite.
- **Unverifiable acceptance criteria** — a criterion with NO observable check at all, or whose check script verifies a DIFFERENT claim than the criterion states. A check that exists and verifies the right claim but could be stricter is advisory, never blocking.
- **Validation-convention violations** — a Validation Commands bullet that is not one line invoking one committed check script (an inline multi-line program is the classic violation), a missing or unknown stage tag, or an invoked check script absent from the tree.
- **Security / data risks** — destructive ops, secret exposure, or data-loss paths.
- **Scope drift** — work beyond the locked decisions, or marked out of scope / non-goal.
- **Untracked or mismatched spec** — spec.md's `## Tracking` MUST name `Issue #N`, a branch `<type>/<N>-<slug>` carrying that SAME number, and a `Review profile:` of `kb-grounded` or `standard`. Missing, placeholder, or number-mismatched tracking is blocking.
- **Contradicts documented behavior** (KB layer only) — a spec claim about hooks, frontmatter, subagents, skills/commands, MCP, or model aliases that a cached ai-docs doc contradicts. Cite the ai-docs file and the contradicting passage.
- **Profile/signal mismatch** (KB layer only) — the recorded profile disagrees with the KB signals (see KB grounding).

**Adversarial challenge (advisory).** Also ask: is this the simplest approach that meets the
objective? Is there a cleaner design, or unnecessary complexity to cut? A validation check that
could be stricter belongs here. Under the KB layer, also flag an ungrounded load-bearing claim
(recommend `/kb add`) and stale grounding — a referenced doc fetched more than 30 days ago
(recommend a `/kb` refresh). Record all of these as non-blocking recommendations — they NEVER
change the verdict.

**Calibration.** Approve unless a serious gap would lead to a flawed build. Do NOT block on
style, wording, formatting, or "you could also" nice-to-haves. For acceptance criteria:
blocking requires a criterion with NO observable check or a check that verifies a DIFFERENT
claim — "this check could be stricter" is advisory only. Never demand regex-parsing of prose
contracts as a fix: a check script proves an artifact exists and its executable behavior;
clause-exact prose fidelity is the builder's harness-review's job, not a spec-time ratchet.
When in doubt whether a finding blocks, record it as advisory rather than dropping it.

## Output contract

Write your verdict to `specs/<plan-name>/reviews/codex-spec-review-round-N.md`, creating
`reviews/` if absent. Write only this file; the spec and its
siblings stay untouched.

The report's **first line** MUST be exactly one of (the dash is an em-dash, U+2014, one space
each side; substitute the integer N):

- `### Round N — Verdict: approved`
- `### Round N — Verdict: changes-requested`

Then, in order:

1. `Scope:` — `full` or `delta`.
2. `Reviewed head SHA:` — the injected SHA, verbatim; on delta rounds also `Base SHA:`. Mandatory.
3. `Validation:` — one line per `[plan-time]` command ending `PASS`/`FAIL`, then `deferred: <n> child-build-time, <m> post-merge` (or `Validation: none at plan-time`).
4. On delta rounds, `Prior blockers:` — every prior blocker dispositioned fixed / not fixed / regressed.
5. The findings and digest, per the rules below.

Rules:

- Use `approved` ONLY when zero blocking findings remain — advisory recommendations do not block.
- `changes-requested`: one bullet per blocking finding. Each bullet starts with a finding ID `CX<N>-<i>` (round N, i-th finding) and a tag — `(new)`, or `(repeat of CX<n>-<m>)` when it shares its root cause with a prior-round finding (not fixed, regressed, or the fix failed the same way). Then state the problem AND a concrete fix (which file / section / step). Doc-grounded findings cite the ai-docs file they rest on.
- After the blocking findings, list any advisory items — a simpler/cleaner approach, a stricter-check suggestion, plus (KB layer) ungrounded or stale grounding — under a `**Recommendations (advisory, non-blocking):**` list.
- `approved`: one short line that the spec meets the bar. Invent no findings to pad it (advisory recommendations may still follow).
- **Issue-comment digest (final element of the report).** End with `**Issue-comment digest:**` followed by exactly one short paragraph: the round number, verdict, blocking-finding count (noting how many are repeats) + headline issues, and the next action. Draw only on this round's findings — add no new claim or recommendation. The orchestrator posts it verbatim to the issue thread; you still never call `gh`.

Example:

```text
### Round 2 — Verdict: changes-requested

Scope: delta
Base SHA: a1b2c3d
Reviewed head SHA: f6e5d4c
Validation:
- [plan-time] uv run --script specs/the-plan/checks/ac1_layout.py → PASS
- deferred: 2 child-build-time, 1 post-merge
Prior blockers:
- CX1-1 fixed; CX1-2 not fixed

- **CX2-1 (repeat of CX1-2) — Step 4 still depends on the migration in Step 6.** The reorder moved Step 5, not Step 6; Step 4 still reads the new column first. Fix: sequence the migration before any reader.
- **CX2-2 (new) — AC3's check script verifies the wrong claim.** The criterion promises a retry limit; `checks/ac3_retries.py` (changed this round) only asserts the config key exists. Fix: assert the limit's enforced value.

**Recommendations (advisory, non-blocking):**

- The three near-identical builder tasks could collapse into one parameterized task — simpler team, same coverage.

**Issue-comment digest:** Round 2, changes-requested — 2 blocking (1 repeat): the Step 4/6 migration order is still wrong and AC3's new check verifies the wrong claim. Next: fix both, then re-review.
```

## Return to the caller (short)

The full detail lives in the report file — your CLI reply MUST be terse so a findings-heavy
round never floods the orchestrator:

- **Line 1** — the verdict line, verbatim.
- **Line 2** — a one-line count + the report path, e.g. `2 blocking findings (1 repeat) — specs/<plan-name>/reviews/codex-spec-review-round-2.md` or `no blocking findings — specs/<plan-name>/reviews/codex-spec-review-round-1.md`.

## Never touch

- Write ONLY this round's report at `specs/<plan-name>/reviews/codex-spec-review-round-N.md`. Edit nothing else — spec.md, decisions.md, tasks.md, acceptance-criteria.md, the check scripts, everything under `specs/<plan-name>/artifacts/`, and everything under `ai-docs/` are read-only (running check scripts is fine; editing them is not).
- Never call `gh` — the orchestrator relays every verdict.
