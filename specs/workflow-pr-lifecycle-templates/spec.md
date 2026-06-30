# Spec: Unify the lifecycle on one PR + standardize workflow templates

- **Owner:** @SunshinePeace213
- **Status:** Drafted for Review
  <!-- Lifecycle, set by /plan-w-team: Drafted for Review → Approved (after a Codex `approved`
       verdict) → Needs Human Review (still changes-requested after 2 Codex rounds). One value only. -->

## Task Description

The team's `plan-w-team → build → ship` lifecycle works, but its GitHub-tracking and
template discipline are uneven. This plan enhances that lifecycle along four axes the
owner raised:

- **Q1 — workflow standard & PR timing.** The two-surface model (Epic **issue** = spec/
  intent, **PR** = implementation/diff) is sound and maps cleanly onto spec-driven
  development. But the PR is opened _late_ — `/plan-w-team` already pushes the branch +
  all four plan files to `origin`, yet the PR isn't opened until `/build` starts, leaving
  a window where a branch with commits exists on GitHub with **no PR**. And the Epic
  issue's Lifecycle marker advances `Plan ▸ Spec-review ▸ Approved` during planning then
  **freezes** — Build and Ship are invisible on the spine until `Closes #N` fires at merge.
- **Q2 — PR-tracking parity.** `/plan-w-team`'s issue tracking is rich and standardized
  (canonical snippets, body-sync touchpoints, comment=history / body=state split,
  lifecycle marker). `/build`'s PR side has only a Build-Status checklist + Agent Task
  Manifest plus **free-form** `gh pr comment`s. The PR side should reach parity.
- **Q3 — template standardization.** Every workflow output/handoff should have a canonical
  template with a fixed layout: the initial PR body, issue state-tracking, Codex review
  relay (both spec→issue and impl→PR), Claude's "fixes applied" comment, the Claude→Codex
  invocation prompts, the Codex→Claude report/verdict formats, and the final `/build` &
  `/ship` reports. Today these are partly canonical (spec-review issue snippet) and partly
  ad-hoc (everything PR-facing).
- **Q4 — cleanup.** A scan of `build` / `ship` / `implementation-review` (+ `spec-review`)
  found the "expired prompts" surface is **narrow**: two genuinely-stale doc references,
  not large dead bodies. The legacy `plan.md` fallback in `build.md` is **live** — 7
  existing `specs/*/plan.md` folders depend on it — so it is retained, not removed.

A builder needs to: create one shared **canonical-template catalog**, move PR creation to
plan time so a single PR threads the whole lifecycle, advance the issue lifecycle through
Build→Ship→Done, fix the manifest's false `#N` auto-links, and fix the two stale refs.

## Objective

When this plan is complete: `/plan-w-team` opens the draft PR at plan time as the single
lifecycle surface; the Epic issue's Lifecycle marker advances end-to-end (no freeze at
"Approved"); every canonical workflow template lives in one root `WORKFLOW-TEMPLATES.md`
that all three commands and both Codex skills reference; the Agent Task Manifest is sourced
from `tasks.md` and contains **no** bare `#<number>` (so `Closes #N` is the only GitHub
reference in the PR); and the two stale doc references are fixed while the legacy `plan.md`
fallback is retained.

## Non-Goals

- **Not** altering the Codex skills' core review logic, finding bars, or verdict rules
  (`spec-review` / `implementation-review` keep their judgement contracts; only the
  Claude-owned _relay_ formats are centralized).
- **Not** changing `/ship`'s squash-merge mechanics or its guard set.
- **Not** building CI, GitHub Actions, or any automation beyond the existing
  command/skill prompts.
- **Not** migrating the 7 historical `specs/*/plan.md` folders to the four-file layout —
  they are archival records of shipped work; the legacy fallback stays to serve them.
- **Not** changing the worktree-mangled-branch / Option-B push refspec convention.

## Problem Statement

The lifecycle has five concrete defects worth fixing now, before more plans accrete around
the current shape:

1. **PR opens late** — a branch-but-no-PR gap between `/plan-w-team` and `/build`; the plan
   is never a reviewable PR diff during planning.
2. **Issue freezes at "Approved"** — Build/Ship/Done never show on the spine until merge.
3. **PR tracking is ad-hoc** — no canonical PR comment/body formats; drift-prone.
4. **Canonical snippets are embedded & duplicated** — plan-w-team carries them inline;
   build re-invents parallel ones; they will diverge.
5. **The Agent Task Manifest false-links** — `#<taskId>` copied from the numeric `Task*`
   board renders `#1`, `#2`… which GitHub auto-links to unrelated issues/PRs; plus the
   `tasks.md` kebab IDs and the runtime numeric IDs are mismatched.

## Solution Approach

Introduce **one shared canonical-template catalog** (`WORKFLOW-TEMPLATES.md` at repo root,
cited from `AGENTS.md` exactly as `GIT-COMMIT-PR-MESSAGE.md` is) as the single source of
truth for every standardized output, then **thin the commands** to reference it instead of
embedding snippets. Make the **PR the single lifecycle surface** by opening it (draft) at
the end of `/plan-w-team` right after the first plan push; `/build` then _resumes_ that PR
rather than creating one. Advance the **issue Lifecycle marker** through Build→Ship→Done
from `/build` and `/ship`. Source the **Agent Task Manifest from `tasks.md`** (stable
kebab-case IDs, grouped by phase, each citing the AC it satisfies), ticked as the matching
`Task*` board entry completes — killing the false `#N` links and the ID mismatch together.
Finally, fix the two stale references and retain the live `plan.md` fallback.

Alternative considered — **keep PR creation at `/build` start** and only standardize
templates: rejected because it leaves the branch-but-no-PR gap and the frozen-issue defect
unaddressed, which were the owner's core Q1/Q2 concerns. Alternative considered —
**consolidate spec-review onto the PR**: rejected in favor of keeping the issue
authoritative for spec-review history (the issue _is_ the spec surface) and mirroring only
the latest verdict state onto the PR body.

## Requirements & Decisions

The full grilling record is in `decisions.md`. The locked decisions a builder must honor:

- **PR at plan time, single surface.** `/plan-w-team` opens the draft PR right after the
  first plan push; `/build` **resumes** it (creates only as a graceful fallback); the Epic
  issue stays the durable spine. _Why: closes the branch-but-no-PR gap; PR-early practice._
- **Issue lifecycle advances end-to-end.** `/build` advances the issue marker to **Build**,
  `/ship` to **Done**. _Why: the spine must mirror the whole lifecycle, not freeze._
- **Spec-review: issue authoritative, PR mirrors state.** Canonical verdict comment +
  status block stay on the issue; the PR body's Spec-review status block mirrors only the
  latest verdict (no duplicate thread). _Why: issue is the spec surface; PR shows state._
- **Agent Task Manifest from `tasks.md`, no `#`.** Seeded from `tasks.md` step-by-step
  tasks (kebab IDs, grouped by phase, citing satisfied ACs), ticked on `Task*` completion;
  **`Closes #N` is the only GitHub reference in the PR.** _Why: kills false auto-links and
  the ID mismatch._
- **One shared catalog.** `WORKFLOW-TEMPLATES.md` at root, referenced by both commands and
  both skills; commands stop embedding duplicate snippets. _Why: DRY, leaner command
  context, single edit point._
- **Narrow cleanup, keep the live fallback.** Fix `GIT-COMMIT-PR-MESSAGE.md`
  (`epic-plan.md`→`epic-spec.md`, `plan.md`→`spec.md`) and `ship.md` ("Workstream C");
  **retain** the legacy `plan.md` fallback (7 live folders). _Why: it is not dead code._

## Tracking

<!-- Recorded by /plan-w-team. The Issue field is the SINGLE SOURCE OF TRUTH /build reads — /build
     NEVER re-derives #N from the mangled local branch name. spec.md is the single home for this
     block; decisions.md does not duplicate it. -->

- **Issue:** #10
- **Branch:** chore/10-workflow-pr-lifecycle-templates
- **Worktree:** /Users/ringo/Desktop/ai-native-startup/.claude/worktrees/workflow-pr-lifecycle-templates

## Relevant Files

Use these files to complete the task:

- `AGENTS.md` — add a citation to the new catalog (mirrors how it cites `GIT-COMMIT-PR-MESSAGE.md`).
- `GIT-COMMIT-PR-MESSAGE.md` — fix the two stale refs; update the Agent Task Manifest description (no `#`, sourced from `tasks.md`).
- `.claude/commands/plan-w-team.md` — add the PR-at-plan-time step + spec-review PR-state mirror; reference the catalog instead of embedding the canonical issue snippets.
- `.claude/commands/build.md` — Phase 1 _resumes_ the existing draft PR (fallback-create only); seed the manifest from `tasks.md`; advance the issue marker to Build; replace ad-hoc comments with catalog references; impl-review relay at parity. **Keep the legacy `plan.md` fallback (lines ~84–87) unchanged.**
- `.claude/commands/ship.md` — advance the issue marker to Done; fix the "Workstream C" dangling ref; reference the catalog's final-report format.
- `.agents/skills/spec-review/SKILL.md` — light touch: point the verdict-relay note at the catalog (do **not** change the finding bar or output contract).
- `.agents/skills/implementation-review/SKILL.md` — same light touch.
- `.github/PULL_REQUEST_TEMPLATE/*.md` (8 files) — carry the unified body skeleton (Lifecycle line, Spec-review status block, new Agent Task Manifest format, Build Status).

### New Files

- `WORKFLOW-TEMPLATES.md` (repo root) — the canonical-template catalog; single source of truth for every standardized workflow output.

## Edge Cases

- **`gh` unavailable at plan time** → `/plan-w-team` skips the PR creation (records `Issue: none — gh unavailable` per its existing graceful-skip); `/build` then _creates_ the draft PR as the fallback path. Resume must degrade to create.
- **PR already exists when `/build` resumes** → `/build` finds it by `#N`/head branch and resumes; it must **never** open a second PR.
- **PR absent when `/build` resumes but issue exists** → fall back to the existing `gh pr create` path (gh was down at plan time, or this plan predates the change).
- **Codex unavailable** → both review loops graceful-skip exactly as today; catalog reports must accommodate the `skipped — Codex unavailable` outcome.
- **Legacy `plan.md` folders** → `/build`'s legacy fallback must keep resolving them; the manifest-from-`tasks.md` change must not assume a `tasks.md` exists for legacy flat specs (degrade to the runtime board with non-`#` IDs).
- **Empty/zero-task plan** → the manifest renders an explicit "no agent tasks" line, not an empty section.
- **Re-running `/plan-w-team` or `/build`** → status blocks are overwritten in place (idempotent), never appended twice.

## Red Flags

<!-- Anti-patterns signalling the plan is being skipped or scope is drifting. -->

- Starting to write code without any written requirements
- Asking "should I just start building?" before clarifying what "done" means
- Implementing features not mentioned in any spec or task list
- Making architectural decisions without documenting them
- Skipping the spec because "it's obvious what to build"
- **Removing the legacy `plan.md` fallback** (it serves 7 live folders — explicitly out of scope).
- **Adding a second PR** in `/build` instead of resuming the plan-time one.
- **Re-embedding canonical snippets** inline in a command after the catalog exists (defeats the DRY goal).
- **Touching the Codex skills' finding bar / verdict rules** (only relay formats are centralized).

## Notes

- No new runtime libraries — this is a Markdown harness-layer change (commands, skills,
  templates, standards docs). No `uv add` / `bun add`.
- The catalog should carry, for each template, a fixed **layout** + a **filled example**,
  matching the "reproduce exactly" rigor already used for the spec-review issue snippet.
- Per-template pros/cons rationale (the Q3 "list pros and cons" ask) lives in `decisions.md`.

## Codex Findings

<!-- CODEX-OWNED. Written only by the spec-review skill (one `### Round N — Verdict: …` block per
     round). Claude must NEVER edit this section. -->

### Round 1 — Verdict: changes-requested

- **AC2 does not verify the stated Ship lifecycle step.** The spec says the issue lifecycle must advance through `Build→Ship→Done`, and `tasks.md` Step 3 explicitly requires `/build` Phase 6 to advance the issue to **Ship**, but `acceptance-criteria.md` AC2 and its validation command only check `Build` in `build.md` and `Done` in `ship.md`. A build could omit the Ship transition and still pass. Recommend: update `acceptance-criteria.md` AC2 to require `/build` to advance to **Build** at start and **Ship** at handoff, and update the AC2 validation command to grep for `Ship` in `.claude/commands/build.md`.
- **AC4's validation does not prove the no-false-link manifest requirement.** AC4 requires the Agent Task Manifest to contain no bare `#<number>` in any PR template or manifest description, but its validation command checks only `.github/PULL_REQUEST_TEMPLATE/` and only the narrow patterns `#<taskId>` or `#[0-9]+ <subject>`. It would miss bare task links such as `#1` or `#12 - build`, and it does not inspect the manifest description in `GIT-COMMIT-PR-MESSAGE.md` or the new catalog. Recommend: broaden the AC4 validation command in `acceptance-criteria.md` to check the PR templates plus `GIT-COMMIT-PR-MESSAGE.md` and `WORKFLOW-TEMPLATES.md` for bare numbered task references in manifest examples/descriptions, while preserving the allowed `Closes #N` issue reference.
- **AC5's validation does not prove `/build` never opens a second PR.** AC5 requires `build.md` to resume the existing draft PR, fallback-create only when absent, and never open a second PR, but the validation command only greps for a resume phrase. A command file could still contain an unconditional `gh pr create --draft` path and pass. Recommend: strengthen the AC5 validation in `acceptance-criteria.md` to also check that any `gh pr create` in `.claude/commands/build.md` is documented as fallback-only when no existing PR is found, and that Phase 1 no longer instructs opening a new PR by default.

### Round 2 — Verdict: changes-requested

- **AC4's validation still does not prove the no-false-link manifest requirement.** AC4 requires no bare `#<number>` in any PR template or in the manifest description, but the validation command only catches checklist lines matching `^- \[[ x]\] .*#[0-9]` plus `#<taskId>`. A bare manifest reference such as `Task #1` or `task #12 - validate` in `GIT-COMMIT-PR-MESSAGE.md`, `WORKFLOW-TEMPLATES.md`, or a PR template would still pass if it is not on a checkbox line. Recommend: update `acceptance-criteria.md` AC4's validation command to inspect the Agent Task Manifest sections/descriptions in those files for bare numbered task references, while preserving the allowed `Closes #N` linked-issue line.
- **AC5's validation still does not prove `/build` never opens a second PR.** AC5 requires `build.md` to resume the plan-time PR and fallback-create only when absent, but the validation command only checks for the word `resume`, absence of the old exact phrase `Open exactly ONE draft PR`, and some fallback-create wording. It would still pass if `.claude/commands/build.md` retained an unconditional `gh pr create --draft` step under different wording. Recommend: update `acceptance-criteria.md` AC5's validation command to inspect every `gh pr create` occurrence in `.claude/commands/build.md` and fail unless it is in the documented absent-PR fallback path.

## Codex Verification

<!-- CLAUDE-OWNED. The outcome summary Claude records after the Codex loop. -->

- **Outcome:** <approved at round N | proceeded without full approval after 2 rounds | skipped — Codex unavailable>
- **Rejected findings:** <any Codex finding Claude chose not to act on, each with a one-line rationale; "none" if all warranted findings were applied>

## References

```
specs/workflow-pr-lifecycle-templates/
├── spec.md                 # this file — what & why, tracking, review record
├── decisions.md            # grilling record: resolved decisions, assumptions, out-of-scope
├── tasks.md                # how & who: phases, team, step-by-step tasks
└── acceptance-criteria.md  # done: acceptance criteria + validation commands
```

## Self Validation

- [ ] Objective, Task Description, and Non-Goals are filled in (no placeholders left)
- [ ] Requirements trace to tasks in tasks.md and to checks in acceptance-criteria.md
- [ ] Acceptance criteria are specific and testable
- [ ] All four files exist under specs/workflow-pr-lifecycle-templates/ and are saved in the repository
- [ ] Codex has reviewed the spec and Status reflects the outcome
