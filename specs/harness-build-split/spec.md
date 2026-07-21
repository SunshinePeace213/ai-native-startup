# Spec: Split harness-build into build + review commands

- **Owner:** @SunshinePeace213
- **Status:** Drafted for Review
  <!-- Lifecycle, set by /harness-layer:harness-plan: Drafted for Review → Approved (on a Codex
       `approved` verdict). A cycle that ends still changes-requested — or with Codex unavailable —
       records needs-human in ## Codex Verification and keeps this status. One value only. -->

## Task Description

Split `.claude/commands/harness-layer/harness-build.md` (132 lines) into two commands —
`harness-build` (implement → tidy → draft PR) and `harness-review` (Codex cross-check gate →
fixes → PR ready) — both files together under 132 lines, instructions-not-rationale
throughout. The review gate drops the frozen-packet machinery: a `sonnet` runner drives
Codex, which runs its own `git diff` over the review range and its own validation; the
`.agents/skills/implementation-review` skill is rewritten to match. Failure hand-off is the
PR itself (round-2 `changes-requested` leaves it draft) — no gates, no labels.
`specs/_templates/implementation-notes.md` expands into a chronological per-plan dev log
rendered as `artifacts/dev-notes.html`, replacing both the Deviations board and the ship
brief. A new every-session rule `.claude/rules/development-log.md` collects cross-plan
lessons, and both commands end with a memory step per `memory-series.md`.

## Objective

`/harness-layer:harness-build` ends at a draft PR with `PR #M` + its hand-off SHA (the
last implementation push, snapshotted before the metadata commit)
recorded in spec.md `## Tracking`; `/harness-layer:harness-review` reads only that block,
gates via Codex, and either flips the PR ready at the approved head or leaves it draft for
the human — with the two command files totalling fewer than 132 lines.

## Non-Goals

- No changes to `harness-ship.md` (its "after harness-build marks the PR ready" wording goes stale — flagged as a follow-up, not fixed here), the `spec-review` skill, the discovery commands, issue/PR templates, or `.claude/hooks/`.
- No Preflight checks (codex/plugin/gh probes) in either command; no over-cap gate, root-cause rule, Locked Boundaries, fix-design consult, or `status:needs-human` label in the review path.
- No second completion page: the ship brief and its quiz are dropped, not relocated.
- `git-workflow.md` mechanics (refspec pushes, marker-comment upserts, PR templates, labels), `REVIEW_PROFILE` gating, and the worktree rule carry over unchanged — one timing line updated, nothing else.

## Problem Statement

harness-build.md packs implementation, PR management, and a review protocol with
frozen-packet preparation (`round-N-input/`, attestations, validation.md, root-cause
machinery) into one 132-line command. Packet preparation is the single most expensive and
drift-prone part; the review escalation ladder (over-cap gate, needs-human label, consult)
rarely fires and bloats every session that loads the command. Splitting build from review
and letting Codex self-serve its input removes that cost while the PR itself becomes the
human hand-off surface.

## Solution Approach

Two thin commands sharing exactly one piece of state — spec.md's `## Tracking`. Build
implements, tidies, opens the draft PR, and records `PR #M` + the hand-off SHA. Review
refuses without a PR number, drives Codex through a `sonnet` runner copied from
harness-plan.md § Codex Cross-Review (retry-once, verdict-grep, digest-relay), spawns
fixers per model-selection, and on approval flips the PR ready at the approved head —
preserving harness-ship's merge guard. The alternative (keeping one command with a slimmer
packet) lost: the packet contract itself is the drift source, and one command can't drop
Preflight/escalation without re-tangling build and review concerns.

## Requirements & Decisions

Volatile first; the full record is in [decisions.md](./decisions.md).

- **Hand-off contract** — `## Tracking` is the sole shared state. Build's terminal sequence: finish EVERY repository write first (implementation, tidy, dev-log/notes appends, memory edits), commit + push, and snapshot that head as the **hand-off SHA** (`git rev-parse HEAD` — the last implementation push, NOT the metadata commit that follows); then record `PR: #M` and `Hand-off SHA: <sha>` (plus anything the human must know) in `## Tracking` as ONE final metadata commit and push it. The recorded SHA is informational for the human; review derives its own review range. Review's first act: read `## Tracking`; no PR number → STOP (tell the user to run harness-build). Build's own STOP: no Issue `#N` in `## Tracking`. These two refusals are the only STOPs in either command. Alternative (a hand-off file or PR-derived state) rejected — one block, already read by ship.
- **Runner-prompt contract** (command and skill implement against this, verbatim): the `sonnet` runner's `codex exec` prompt injects the round number `N`, the plan path, `BASE_SHA` (round 1: `git merge-base origin/main HEAD`; round N>1: the prior reviewed head), `REVIEWED_HEAD_SHA` (current head at round start), and `REVIEW_PROFILE`. Codex itself runs `git diff` (+ `--name-status`/`--numstat`) over that range excluding `specs/<name>/reviews/` and `specs/<name>/artifacts/`, reads the plan files and `implementation-notes.md` (round 1), runs the plan's Validation Commands recording real results (a command it cannot execute is recorded as unexecuted-with-reason and blocks; results are never fabricated), writes `specs/<name>/reviews/codex-impl-review-round-N.md` — verdict first line, `**Issue-comment digest:**` paragraph last — and returns the two-line terse summary. Git read-only; no commits, no `gh`. The runner retries the identical command once on crash/non-zero/no-verdict, then returns ONLY the verdict + digest.
- **Review loop** — two counters, never conflated: the **report number `N`** is global (highest existing `codex-impl-review-round-*.md` + 1 at each round; it names the report file and picks the review range — N=1 diffs from `merge-base origin/main HEAD`, N>1 from the prior report's reviewed head); the **attempt counter `A`** (1–2) is invocation-local and drives control flow — each run performs at most 2 attempts. A=1 `changes-requested` → commit the report, spawn fixer subagents per model-selection (a failed fix escalates a tier), ONE fix commit, push, attempt 2. A=2 `changes-requested` → render dev-notes.html and run the memory step, commit them with the final report, push, post the final `<!-- report:codex-round-N -->` comment, leave the PR draft, end the run — the human owns the blockers. `approved` (any attempt) → **terminal-commit rule**: render dev-notes.html and run the memory step FIRST, then make ONE terminal commit (report + dev-notes.html + dev-log/memory/notes edits), push, verify the PR head equals it, record it as the stage-table Ready evidence, and `gh pr ready`. NOTHING mutates the repository after the terminal commit — it is the approved head harness-ship merges at.
- **Dev log** — build creates `specs/<name>/implementation-notes.md` from the expanded template and both commands append chronological entries (phases, hand-offs, deviations, fixes, lessons). harness-review renders `artifacts/dev-notes.html` from it at the end on ANY verdict (medium/complex plans; thariq-style timeline per artifacts.md), links it from the PR, replacing the Deviations board row and the ship brief. Cross-plan one-liners go to `.claude/rules/development-log.md` (flat, no `paths:`, ≈40-line cap with overflow distilled into the proper rule file); the per-plan vs cross-plan boundary is stated in both files.
- **Command surface** — each command declares only `PATH_TO_PLAN`, `ISSUE_NUMBER`, `PR_NUMBER`, `REVIEW_PROFILE`; `STAGES`, simplifier names, `CROSS_CHECK`, `ROUND_INPUT`, `REQUIRED_PLUGINS` are inlined into the sections that use them. Build order: implement → tidy (`harness-simplifier`/`code-simplifier` on `opus`, auto-fix, behavior-preserving) → draft PR → post tidy findings directly as `<!-- report:tidy -->` (held-report rule deleted). Both commands keep `model: fable` + `disable-model-invocation: true` frontmatter and end with a memory step per memory-series.md. Combined `wc -l` of the two files < 132.

## Tracking

<!-- Recorded by /harness-layer:harness-plan. The Issue field is the SINGLE SOURCE OF TRUTH
     /harness-layer:harness-build reads — it NEVER re-derives #N from the local `worktree-<slug>`
     branch name. spec.md is the single home for this block; decisions.md does not duplicate it. -->

- **Issue:** #37
- **Branch:** refactor/37-harness-build-split
- **Worktree:** /Users/ringo/Desktop/ai-native-startup/.claude/worktrees/harness-build-split
- **Review profile:** kb-grounded
- **PR:** <#M — filled by /harness-layer:harness-build>

## Relevant Files

Use these files to complete the task:

- `.claude/commands/harness-layer/harness-build.md` — rewritten to implement → tidy → draft PR; sheds Preflight, Verification, Review packet, over-cap machinery.
- `.agents/skills/implementation-review/SKILL.md` — rewritten to the runner-prompt contract; frozen-packet / zero-git / `round-N-input/` machinery deleted; gains the `**Issue-comment digest:**` closer (mirror spec-review's).
- `specs/_templates/implementation-notes.md` — expands from deviations-only into the chronological `## Log` template with the per-plan vs cross-plan boundary note.
- `.claude/rules/harness-layer/artifacts.md` — the Deviations board inventory row becomes the Dev notes row (rendered by harness-review on any verdict, linked from the PR).
- `.claude/commands/harness-layer/harness-plan.md` — gains one line: plans mark tasks whose outcomes must be recorded to memory.
- `.claude/rules/git-workflow.md` — one timing line: the draft PR opens after the tidy checkpoint (was "first implementation checkpoint"); everything else untouched.
- `AGENTS.md` — Core pipeline line gains `/harness-layer:harness-review`; Harness Development gains the dev-log pointer (per memory-series.md's new-rule contract).

### New Files

- `.claude/commands/harness-layer/harness-review.md` — the Codex gate → fixes → PR ready command.
- `.claude/rules/development-log.md` — every-session cross-plan lesson log (flat, no `paths:`, ≈40-line cap, distill-on-overflow).

## Edge Cases

- **Line budget overflow while authoring** — cut prose, never contract items; the validator's `wc -l` sum is the gate. If the contract genuinely cannot fit, surface it — don't silently drop behavior.
- **Review run with no PR in `## Tracking`** — STOP with "run /harness-layer:harness-build <name> first"; the designed refusal, not an error path.
- **Build run with no Issue in `## Tracking`** — STOP; file the issue via /harness-layer:harness-plan first.
- **Worktree missing at build/review time** — restore it from the convention branch before working.
- **Codex crashes / writes no verdict line** — the runner re-runs once; still nothing → report the failure, leave the PR draft, end the run (no label, no gate). Never treat a missing verdict as approval.
- **Empty diff over the review range** — `changes-requested` naming it; nothing-to-review is never an approval.
- **A validation command Codex cannot execute** (sandbox/network) — recorded as unexecuted with the reason; blocks approval; never fabricated.
- **Push lands mid-round** — the round's `REVIEWED_HEAD_SHA` snapshot no longer matches HEAD → discard and re-run the round on the new head.
- **Re-runs** — marker comments upsert in place; dev-notes.html re-renders to the same path/URL; report `N` = highest existing report + 1 while the attempt counter restarts at 1 (a resumed run after a human hand-off may start at N=3 — its attempt-1 fix path and attempt-2 hand-off work unchanged).
- **Simple plans** — no dev-notes.html page (per artifacts.md); implementation-notes.md is still kept and appended.

## Red Flags

- Starting to write code without any written requirements
- Asking "should I just start building?" before clarifying what "done" means
- Implementing features not mentioned in any spec or task list
- Making architectural decisions without documenting them
- Skipping the spec because "it's obvious what to build"
- Re-adding rationale, decision logs, or Preflight probes to the command files — instructions only
- A fifth Variables entry, a held tidy report, or any `round-N-input/` reference surviving the rewrite
- The review command growing an escalation path (label, gate, consult) beyond "leave the PR draft"

## Notes

- The two commands lean on always-loaded rules instead of restating them: git-workflow.md (refspec pushes, marker upserts, templates), model-selection.md (fixer/runner models), task-tools.md (deployment) all load every session.
- Follow-up (out of scope): harness-ship.md's description still says "after harness-build marks the PR ready" — a future docs pass should say harness-review.

## Codex Verification

<!-- CLAUDE-OWNED. The outcome summary Claude records after the Codex loop. -->

- **Outcome:** needs-human (blockers) — round 1: 4 blocking, fixed and verified in round 2; round 2: 2 blocking (attempt-counter vs report-number conflation; AC1 validator missing file-existence guards), both fixed in the post-cycle commit but unverified by Codex — the 2-round cycle cap expired before a verifying round.
- **Rejected findings:** none — all warranted findings were applied.

## References

```text
specs/harness-build-split/
├── discovery/              # unknowns + interview passes; decisions-draft.md is the ledger
├── spec.md                 # this file — what & why, tracking, review record
├── decisions.md            # interview record + KB references
├── tasks.md                # how & who: phases, team, step-by-step tasks
├── acceptance-criteria.md  # done: acceptance criteria + validation commands
└── artifacts/              # implementation-plan page
```

## Self Validation

- [ ] Objective, Task Description, and Non-Goals are filled in (no placeholders left)
- [ ] Requirements trace to tasks in tasks.md and to checks in acceptance-criteria.md
- [ ] Acceptance criteria are specific and testable
- [ ] All four files exist under specs/harness-build-split/ and are saved in the repository
- [ ] Codex has reviewed the spec and Status reflects the outcome
