# Tasks: Standardize /plan-w-team issue tracking

> Execution plan for [spec.md](./spec.md). Owner and scope are defined there; this file is how & who.

## Implementation Phases

### Phase 1: Foundation

Establish the canonical Epic-issue body structure (the renamed `epic-spec.md`). Everything the harness syncs to references this structure, so it is written first — though because the section names are fully specified in spec.md, the harness rework (Phase 2) does not have to wait on it.

### Phase 2: Core Implementation

Wire `/plan-w-team` to the new structure (three body-sync touchpoints, two canonical snippets, standardized title + path-as-text links, `epic-spec.md` reference) and clean up the eight PR Build-Status templates. These two work-streams are independent and run in parallel.

### Phase 3: Integration & Polish

Validate the whole change: rename integrity, body structure, harness instructions, PR-template counts, and no dangling `epic-plan.md` references.

## Team Orchestration

- You operate as the team lead and orchestrate the team to execute the plan.
- IMPORTANT: You NEVER operate directly on the codebase. You use the `Task*` tools to deploy team
  members to build, validate, test, and deploy. Your job is to direct, not to build.
- Keep the shared task list (TaskCreate/TaskUpdate) as the single source of truth for who is doing
  what; verify each task on the board before marking it complete.
- Note the session id / name of each team member — that is how you reference them.

## Team Members

- **Builder**
  - **Name:** builder-templates
  - **Role:** Owns the `.github/` templates — renames + reworks the Epic issue template, and fixes the eight PR Build-Status blocks.
  - **Agent Type:** general-purpose
  - **Resume:** true

- **Builder**
  - **Name:** builder-harness
  - **Role:** Owns `.claude/commands/plan-w-team.md` — adds the body-sync touchpoints, the two canonical snippets, the standardized title, and the path-as-text link instruction; updates the `epic-spec.md` reference.
  - **Agent Type:** general-purpose
  - **Resume:** true

- **Validator**
  - **Name:** validator
  - **Role:** Runs every Validation Command and confirms each acceptance criterion.
  - **Agent Type:** general-purpose
  - **Resume:** true

## Step by Step Tasks

- Execute every step in order, top to bottom. Each task maps directly to one `TaskCreate` call.
- Before starting, run `TaskCreate` for every task below so all team members can see the board.
- Each task names the acceptance criteria (from acceptance-criteria.md) it satisfies, so work traces to "done".

### 1. Rename + rework the Epic issue template

- **Task ID:** rework-issue-template
- **Depends On:** none
- **Assigned To:** builder-templates
- **Agent Type:** general-purpose
- **Parallel:** true
- **Satisfies:** AC1, AC2
- `git mv .github/ISSUE_TEMPLATE/epic-plan.md .github/ISSUE_TEMPLATE/epic-spec.md` (preserve history).
- Preserve the frontmatter `name: Epic / Plan` and `title: "📋 epic: "`; update `about:` to mention the plan→build→ship lifecycle.
- Rewrite the body to exactly these sections, in order: `## Objective`, `## Non-Goals`, `## Lifecycle` (the `Plan ▸ Spec-review ▸ Approved ▸ Build ▸ Ship ▸ Done` line + a "▲ current" marker), `## Link to plan` (path-as-text markdown links to **all four** plan files — `spec.md`, `tasks.md`, `acceptance-criteria.md`, `decisions.md` — NOT bare blob URLs and NOT the stale `plan.md`), `## Spec-review status` (the three lines: `Latest verdict`, `Status`, `History: see thread ↓`), `## Acceptance criteria` (a pointer to `acceptance-criteria.md`), `## Open Questions`, `## How to act` (`/build <plan-name>` then `/ship`).
- DROP the `## Child task checklist` section entirely.
- Keep all body prose as HTML-comment guidance where the original used it, so the template stays self-documenting.

### 2. Fix the eight PR Build-Status templates

- **Task ID:** fix-pr-build-status
- **Depends On:** none
- **Assigned To:** builder-templates
- **Agent Type:** general-purpose
- **Parallel:** true
- **Satisfies:** AC5
- In each of `.github/PULL_REQUEST_TEMPLATE/{chore,docs,feat,fix,perf,refactor,style,test}.md`, replace the 5-item Build Status list with the 7-item list, in this exact order: `Implementation`, `Internal check`, `Claude code review`, `Codex review R1`, `Fixes`, `Codex review R2`, `Result`.
- Change ONLY the checklist items inside `## Build Status`; leave every other section of each template untouched.

### 3. Rework /plan-w-team for body-state issue tracking

- **Task ID:** plan-w-team-harness-rework
- **Depends On:** none
- **Assigned To:** builder-harness
- **Agent Type:** general-purpose
- **Parallel:** true
- **Satisfies:** AC3, AC4, AC6
- Update every `epic-plan.md` reference to `epic-spec.md` (the `--template` name `"Epic / Plan"` stays).
- Standardize the issue title in the create step: `📋 epic: <descriptive core title>` (replace the vague "Title = the plan title").
- Change the "Update the issue's Link to plan" guidance to produce **path-as-text markdown links** (`[specs/<name>/spec.md](<convention-branch blob url>)`) for **all four** plan files (`spec.md`, `tasks.md`, `acceptance-criteria.md`, `decisions.md`), explicitly NOT bare repo-relative paths and NOT bare URLs.
- Add the **three body-sync touchpoints** (each with a graceful-`gh` skip): (1) at publish, fill the issue body's `## Link to plan` + `## Acceptance criteria` pointer; (2) after each Codex round, `gh issue edit` the `## Spec-review status` block (state) in addition to the relay comment (history); (3) at loop settle, set the `Status` line and advance the `## Lifecycle` ▲ marker to `Approved` on approval, otherwise leave it at `Spec-review` (`Needs Human Review` is a Status value, never a Lifecycle node).
- Add the **two canonical snippets** as reproduce-exactly blocks: the verdict **relay-comment** (`### 🔍 Codex spec-review — Round N · <verdict>` + blocking findings + "Claude this round" + a clickable `Full detail` pointer — a markdown link `[spec.md › ## Codex Findings](<convention-branch blob url>/spec.md#codex-findings)`, NOT plain text) and the `## Spec-review status` **state-mirror** block.
- Keep the change additive/consistent with the existing graceful-skip and per-phase commit cadence; do NOT edit `build.md` or any skill file.

### 4. Validate Everything

- **Task ID:** validate-all
- **Depends On:** rework-issue-template, fix-pr-build-status, plan-w-team-harness-rework
- **Assigned To:** validator
- **Agent Type:** general-purpose
- **Parallel:** false
- Run every command in acceptance-criteria.md → `## Validation Commands`.
- Verify each acceptance criterion (AC1–AC6) is met, and that the rename is committed/tracked per AC1's committed-state check (epic-spec.md tracked, epic-plan.md no longer tracked) — not that `git status` shows `R`, since the worktree is clean post-commit and the heavy body rework records the move as delete+add.
