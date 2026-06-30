# Spec: Standardize /plan-w-team issue tracking

- **Owner:** @ringo
- **Status:** Approved
  <!-- Lifecycle, set by /plan-w-team: Drafted for Review → Approved (after a Codex `approved`
       verdict) → Needs Human Review (still changes-requested after 2 Codex rounds). One value only. -->

## Task Description

Today `/plan-w-team` opens one Epic/Plan GitHub issue per plan and then never touches its **body** again — only chronological `gh issue comment` verdict relays accrue. The issue body's checkboxes (`Child task checklist`, `Spec-review status`, `Acceptance criteria`) are seeded empty and stay that way, and the body's "Link to plan" points at a stale pre-rework path (`specs/<feature>/plan.md`). The result is a "write-once, then dead" issue: a reader cannot tell the plan's current state from the body and must reconstruct it from the comment thread.

This plan makes the Epic issue a **live state-mirror for the plan phase** while keeping comments as the append-only history — the standard GitHub split (body = current state, comments = how-we-got-here). It reworks the Epic issue template, wires three body-sync touchpoints into `/plan-w-team`, standardizes two canonical artifacts (the verdict relay-comment and the body state-mirror block), standardizes the issue title, and cleans up a separate post-rework drift in the eight PR Build-Status templates.

The scope is the **plan phase** (the Issue is plan-primary) plus shared template cleanup. Build-phase issue updates and any `/build` behavioral change are out of scope — the PR remains the build-primary surface.

## Objective

After this plan, a `/plan-w-team` run keeps its Epic issue body continuously truthful for the plan phase: the title is standardized, the body carries Objective / Non-Goals / a Lifecycle phase line / path-as-text plan links / a live Spec-review status / an Acceptance-criteria pointer, the Spec-review status is updated on every Codex round (state) alongside the existing relay comment (history), and all eight PR templates seed the same 7-item Build Status that `/build` actually ticks.

## Non-Goals

- **Build-phase issue ticking.** `/build` does not gain new issue-editing behavior; the PR (Agent Task Manifest + 7-item Build Status) remains the build-primary surface. The issue's Lifecycle `Build ▸ Ship ▸ Done` segments are NOT auto-advanced in this iteration (GitHub's Development panel + `Closes #N` close-on-merge cover the handoff).
- **Codex as a `git`/`gh` writer.** Claude stays the sole `git`/`gh` actor; the `spec-review` skill keeps writing findings only into `## Codex Findings` (file-write-only). No change to the skill files.
- **Any `/build` behavioral change** beyond the PR-template Build-Status text cleanup (the templates are edited; `build.md` already seeds the 7-item list and is not modified).
- **Reworking the bug / feature / chore issue templates' title prefixes** — only the Epic template is in scope.

## Problem Statement

The Epic issue is the durable spine of the plan→build→ship lifecycle (`#N` is the join key), but `/plan-w-team` treats it as create-once. Three concrete defects follow:

1. **Dead body.** Post-creation, only comments are written. The body's state fields never update, so the issue's at-a-glance state is permanently wrong/empty.
2. **Stale + redundant structure.** The template's "Link to plan" points at `specs/<feature>/plan.md` (the pre-SDD-rework name; the entry file is now `spec.md`), and its `Child task checklist` duplicates the PR's Agent Task Manifest.
3. **Un-standardized relays.** The per-round relay comment is free-form (`"<verdict + findings + fixes>"`), producing an inconsistent audit trail.

Separately, the multi-layer-review rework of `/build` added two review layers (`Internal check`, `Claude code review`) and now seeds a **7-item** Build Status, but the eight PR templates still ship the old **5-item** list — a latent drift that bites any hand-opened PR and confuses `/ship`'s "every box checked" gate.

## Solution Approach

Adopt the conventional **body = state / comments = history** split, scoped to the plan phase:

- **Rework the Epic issue template** (`git mv .github/ISSUE_TEMPLATE/epic-plan.md` → `epic-spec.md`; `name:` and `title: "📋 epic: "` preserved). New body: `Objective`, `Non-Goals` (scope fence), `Lifecycle` (macro phase line), `Link to plan` (path-as-text markdown links to **all four** plan files — `spec.md`, `tasks.md`, `acceptance-criteria.md`, `decisions.md`), `Spec-review status` (live), `Acceptance criteria` (pointer to `acceptance-criteria.md`), `Open Questions`, `How to act`. Drop `Child task checklist` (PR territory).
- **Wire three body-sync touchpoints into `/plan-w-team`:** (1) at publish, fill the body's plan links + AC pointer; (2) after each Codex round, update `## Spec-review status` (state) in addition to the relay comment (history); (3) at loop settle, set the Status line + advance the Lifecycle marker to `Approved` / `Needs Human Review`.
- **Standardize two artifacts in `/plan-w-team`:** the relay-comment format and the `## Spec-review status` state-mirror block, both derived from the skill's existing `### Round N — Verdict:` line.
- **Standardize the issue title** in the create step: `📋 epic: <descriptive core title>`.
- **Cleanup:** rewrite the Build Status block in all eight `.github/PULL_REQUEST_TEMPLATE/*.md` to the 7-item list `build.md` already uses.

Alternative considered: drive the issue checklist live from the in-session `TaskList`. Rejected — it couples GitHub state to ephemeral session tooling and re-introduces the child-task duplication this plan deliberately removes. The body mirrors plan-phase truth only.

## Requirements & Decisions

- **Body = state, comments = history.** Body fields are overwritten idempotently; the relay comment is append-only. A re-run of a round overwrites the same `## Spec-review status` block, never duplicating it.
- **Issue is plan-primary; PR is build-primary; nothing is mirrored across the line.** The Child-task checklist is dropped from the issue (it lives on the PR); the issue carries plan-phase state only.
- **Claude is the sole `git`/`gh` writer** (unchanged); every new body-sync step graceful-skips when `gh`/remote/auth is unavailable, mirroring the existing graceful-`gh` skip.
- **Plan links are path-as-text markdown links** (`[specs/<name>/spec.md](<blob-url-on-convention-branch>)`) — the raw blob URL is the href, never the display text, and resolves against the convention branch so it does not 404 pre-merge. The `## Link to plan` section lists **all four** plan files (`spec.md`, `tasks.md`, `acceptance-criteria.md`, `decisions.md`), each as its own path-as-text link.
- **The relay-comment `Full detail` pointer is a clickable link**, not plain text — it targets `spec.md`'s Codex Findings section via the heading anchor on the convention branch (`[spec.md › ## Codex Findings](<blob-url>/spec.md#codex-findings)`), so a reader jumps straight from the issue comment to the verdict detail.

## Tracking

<!-- Recorded by /plan-w-team. The Issue field is the SINGLE SOURCE OF TRUTH /build reads — /build
     NEVER re-derives #N from the mangled local branch name. spec.md is the single home for this
     block; decisions.md does not duplicate it. -->

- **Issue:** #8
- **Branch:** chore/8-plan-w-team-issue-tracking
- **Worktree:** /Users/ringo/Desktop/ai-native-startup/.claude/worktrees/chore+8-plan-w-team-issue-tracking

## Relevant Files

Use these files to complete the task:

- `.github/ISSUE_TEMPLATE/epic-plan.md` — the Epic issue template; renamed to `epic-spec.md` and its body reworked (new sections, dropped Child-task checklist, fixed links/title).
- `.claude/commands/plan-w-team.md` — the planning command; gains the three body-sync touchpoints, the two canonical snippets, the standardized issue title, and the path-as-text link instruction; updates the `epic-plan.md` reference to `epic-spec.md`.
- `.github/PULL_REQUEST_TEMPLATE/chore.md`, `docs.md`, `feat.md`, `fix.md`, `perf.md`, `refactor.md`, `style.md`, `test.md` — the eight PR templates; each Build Status block goes from the stale 5 items to the 7 items `build.md` seeds.
- `.github/ISSUE_TEMPLATE/config.yml` — read-only check: it references `feature.md`/`bug.md` only, NOT `epic-plan.md`, so the rename needs no edit here (verify in validation).
- `.claude/commands/build.md` — read-only reference: it already seeds the 7-item Build Status and keeps the legacy `plan.md` fallback (7 existing plan folders still use it); NOT modified.

### New Files

- `.github/ISSUE_TEMPLATE/epic-spec.md` — the renamed, reworked Epic template (created via `git mv` + edit, so history is preserved).

## Edge Cases

- **`gh`/remote/auth unavailable during a run** — every new body-sync step (publish fill, per-round status update, loop-settle status/lifecycle) graceful-skips with a warning and continues local-only, exactly like the existing relay skip.
- **Codex round times out / writes no verdict** — the body `## Spec-review status` is NOT advanced (no false "approved"); the round is re-run. The body only changes after a real verdict is read from the file.
- **Re-running a Codex round** — the `## Spec-review status` block is rewritten in place (idempotent `gh issue edit --body-file`), never appended, so the body never accumulates duplicate status blocks.
- **`gh issue create --template` resolution** — `--template` is matched by the `name:` field (`Epic / Plan`, unchanged) and is moot when `--body-file` is supplied; the rename of the file therefore does not break creation. The web-UI template chooser still works because `name:` is preserved. Verify no code path references the old filename `epic-plan.md`.
- **Pre-merge link 404** — plan-link hrefs point at the convention branch `chore/8-…`, not `main`, so they resolve while the work is in review.
- **Lifecycle Build/Ship segments** — left un-advanced by design (Non-Goal); the marker reflects plan-phase truth and the issue still closes via `Closes #N` at merge. This limitation is stated, not silent.

## Red Flags

- Starting to write code without any written requirements
- Asking "should I just start building?" before clarifying what "done" means
- Implementing features not mentioned in any spec or task list
- Making architectural decisions without documenting them
- Skipping the spec because "it's obvious what to build"
- Editing `build.md` or the `spec-review`/`implementation-review` skill files (all out of scope — cleanup is template-text only)
- Adding a body-sync step that calls `gh` without a graceful-skip guard
- Reintroducing a Child-task checklist on the issue (duplicates the PR)

## Notes

- No new dependencies. All edits are Markdown / prompt-harness text.
- The tracking issue (#8) was created dogfooding the new `epic-spec` body structure, so its body is a working example of the target template.
- Per repo policy: use `git mv` for the rename (preserve history); never `rm -rf` (use `mv … ~/.Trash/` if a hard delete is ever needed).

## Codex Findings

<!-- CODEX-OWNED. Written only by the spec-review skill (one `### Round N — Verdict: …` block per
     round). Claude must NEVER edit this section. -->

### Round 1 — Verdict: changes-requested

- **AC6 cannot pass as written because its grep includes the plan docs that intentionally mention `epic-plan.md`.** Acceptance criteria AC6 says no file under `.github/`, `.claude/`, `.agents/`, or `specs/` may reference the old filename, and its validation command runs `grep -rn 'epic-plan.md' .github .claude .agents specs`; however `spec.md`, `tasks.md`, and `acceptance-criteria.md` themselves use `epic-plan.md` to describe the required rename and old-filename cleanup. `/build` would either fail validation or have to edit the plan artifacts beyond the implementation scope. Recommend: in `acceptance-criteria.md` AC6 and its validation command, scope the stale-reference check to implementation/runtime files only (for example `.github`, `.claude`, and `.agents`, or explicitly exclude this plan folder), while allowing the plan documents to mention the source filename as historical context.

### Round 2 — Verdict: approved

The spec meets the blocking-review bar with no blocking findings this round.

## Codex Verification

<!-- CLAUDE-OWNED. The outcome summary Claude records after the Codex loop. -->

- **Outcome:** approved at round 2 (round 1 raised 1 blocking finding; applied; round 2 clean).
- **Rejected findings:** none — the single round-1 finding (AC6's stale-reference grep included the plan folder, which legitimately documents the rename) was applied by scoping AC6 + its validation command to the runtime surfaces `.github` / `.claude` / `.agents`.

## References

```
specs/plan-w-team-issue-tracking/
├── spec.md                 # this file — what & why, tracking, review record
├── decisions.md            # grilling record: resolved decisions, assumptions, out-of-scope
├── tasks.md                # how & who: phases, team, step-by-step tasks
└── acceptance-criteria.md  # done: acceptance criteria + validation commands
```

## Self Validation

- [ ] Objective, Task Description, and Non-Goals are filled in (no placeholders left)
- [ ] Requirements trace to tasks in tasks.md and to checks in acceptance-criteria.md
- [ ] Acceptance criteria are specific and testable
- [ ] All four files exist under specs/plan-w-team-issue-tracking/ and are saved in the repository
- [ ] Codex has reviewed the spec and Status reflects the outcome
