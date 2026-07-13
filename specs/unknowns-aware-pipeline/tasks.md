# Tasks: Unknowns-Aware Pipeline

> Execution plan for [spec.md](./spec.md). Owner and scope are defined there; this file is how & who.

## Implementation Phases

### Phase 1: Foundation

Templates and the spec-completeness gate move together (template/hook drift is a named blindspot):
`specs/_templates/` updates, the new implementation-notes template, the hook constant, and its
intent test.

### Phase 2: Core Implementation

The three command files and the two Codex skills — all file-disjoint, all parallel.

### Phase 3: Integration & Polish

AGENTS.md memory line, then full-suite validation against every acceptance criterion.

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
  - **Role:** Phase 1 — templates + spec-completeness gate + intent test (one owner so they cannot drift)
  - **Agent Type:** general-purpose
  - **Resume:** true
- **Builder**
  - **Name:** builder-plan-cmd
  - **Role:** harness-plan.md unknowns layer (blindspot pass, taste route, artifact handling)
  - **Agent Type:** general-purpose
  - **Resume:** true
- **Builder**
  - **Name:** builder-build-cmd
  - **Role:** harness-build.md unknowns layer (implementation notes, deviation gate, ship brief + quiz)
  - **Agent Type:** general-purpose
  - **Resume:** true
- **Builder**
  - **Name:** builder-review-surfaces
  - **Role:** harness-review.md plan-fidelity lens + both Codex SKILL.md extensions
  - **Agent Type:** general-purpose
  - **Resume:** true
- **Builder**
  - **Name:** builder-memory
  - **Role:** AGENTS.md pipeline memory line
  - **Agent Type:** general-purpose
  - **Resume:** true
- **Builder**
  - **Name:** validator
  - **Role:** run every validation command and check each acceptance criterion
  - **Agent Type:** general-purpose
  - **Resume:** true

## Step by Step Tasks

- Execute every step in order, top to bottom. Each task maps directly to one `TaskCreate` call.
- Before starting, run `TaskCreate` for every task below so all team members can see the board.
- Each task names the acceptance criteria (from acceptance-criteria.md) it satisfies, so work traces to "done".

### 1. Templates and Spec-Completeness Gate

- **Task ID:** templates-and-gate
- **Depends On:** none
- **Assigned To:** builder-templates
- **Agent Type:** general-purpose
- **Model / Effort:** `sonnet` / `high`
- **Parallel:** true
- **Satisfies:** AC7, AC8
- In `specs/_templates/decisions.md`: add a `## Blindspots` section (placeholder guidance: findings from the plan's blindspot pass, each with its disposition; "none material" allowed for simple chores) between `## Assumptions` and `## Locked Boundaries`.
- In `specs/_templates/spec.md`: inside `## Requirements & Decisions` (heading unchanged), extend the placeholder guidance to order entries by volatility — most-likely-to-change decisions first, each stating its live alternative; mechanical constraints last.
- Create `specs/_templates/implementation-notes.md`: title + intro ("running deviation log kept by /harness-layer:harness-build; created at implement start"), a `## Deviations` section with an entry skeleton (what diverged | what forced it | the call made | spec impact: none / locked-decision → user gate), and a `## Fold-Forward` section (bullets worth carrying into a future attempt). Keep it under ~30 lines — KISS.
- In `.claude/hooks/check_spec_completeness.py`: add `"Blindspots"` to the `decisions.md` tuple in `REQUIRED_SECTIONS`. Do NOT gate implementation-notes.md (build-time file).
- In `tests/harness-layer/hooks/spec-completeness/test_check_spec_completeness.py`: add one intent test pinning that a decisions.md without `## Blindspots` blocks with the exact section named (the existing dynamic fixtures auto-cover the happy path).
- Verify: `uv run pytest tests/harness-layer/hooks/spec-completeness -q` passes.

### 2. Harness-Plan Unknowns Layer

- **Task ID:** plan-cmd-unknowns
- **Depends On:** none
- **Assigned To:** builder-plan-cmd
- **Agent Type:** general-purpose
- **Model / Effort:** `opus` / `xhigh`
- **Parallel:** true
- **Satisfies:** AC1, AC2
- In `.claude/commands/harness-layer/harness-plan.md`, keeping the file's KISS prose style:
- Add a `Blindspot Pass` workflow step between "Understand Codebase"/"Set Review Profile" and "Grill Requirements": scan the task against the codebase and (when active) the KB; report the top unknown unknowns as cards — what / why it matters / proposed resolution. Depth scales: simple → ~3 cards inline; medium/complex → up to ~7 cards written as a self-contained HTML artifact in the session scratchpad and published best-effort via the Artifact tool. Unresolved cards seed the grilling ledger first; every card and its disposition is recorded in `decisions.md ## Blindspots`.
- In the `Grilling Protocol`: order questions by architectural blast radius (answers that would change the architecture come first); add the taste route — when a decision is one the user would recognize but can't specify (UX, output format, report layout) or the user asks, render 2–4 alternatives as a scratchpad HTML artifact (steal/skip chips, reply assembler), publish best-effort, then confirm the choice via AskUserQuestion and record it in decisions.md as usual.
- In "Write the Spec Folder": copy any scratchpad artifacts into `specs/<name-of-plan>/artifacts/` inside the worktree; they commit with the spec. Artifact publishing is best-effort — on availability failure, keep the file and note "publish skipped"; never block.
- In the `Report` block: add an `Artifacts:` line (committed paths + published URLs, or "none").
- Do not change the command's frontmatter, hooks, or any other workflow step.

### 3. Harness-Build Unknowns Layer

- **Task ID:** build-cmd-unknowns
- **Depends On:** none
- **Assigned To:** builder-build-cmd
- **Agent Type:** general-purpose
- **Model / Effort:** `opus` / `xhigh`
- **Parallel:** true
- **Satisfies:** AC3, AC4, AC5
- In `.claude/commands/harness-layer/harness-build.md`, keeping the file's KISS prose style:
- Implement step: create `specs/<name>/implementation-notes.md` from `specs/_templates/implementation-notes.md` at implement start; every builder's hand-off gains a **Deviations** field (what diverged from the plan, what forced it, the call made — "none" allowed); the lead folds entries into the notes file at each checkpoint commit. A deviation touching a locked decision or acceptance criterion STOPS for an AskUserQuestion gate before work proceeds (mirror the existing Locked Boundaries user-approval language).
- Review packet: add a pointer to `specs/<name>/implementation-notes.md` so Codex dispositions deviations rather than rediscovering them.
- Delta scope: every place that excludes `specs/<name>/reviews/` also excludes `specs/<name>/artifacts/`.
- Finish step (before `gh pr ready`): for medium/complex plans, author `specs/<name>/artifacts/ship-brief.html` — leads with what shipped, pre-answers reviewer objections with evidence links (report comments, validation results), ends in a 3–6 question quiz whose wrong answers point at the file/section to re-read. Commit it TOGETHER WITH the approval-round report commit (that single commit is the approved head recorded in the stage table); publish best-effort via the Artifact tool; add a `## Ship Brief` entry (file path + URL) to the PR body; the final Report tells the user to take the quiz before `/harness-layer:harness-ship`. Simple plans skip the brief and quiz.
- Stale-brief rule: if fixes land after the brief is authored (over-cap round 3), re-author it before the new approval commit.
- Do not change the command's frontmatter or the review round caps.

### 4. Review Surfaces

- **Task ID:** review-surfaces
- **Depends On:** none
- **Assigned To:** builder-review-surfaces
- **Agent Type:** general-purpose
- **Model / Effort:** `sonnet` / `high`
- **Parallel:** true
- **Satisfies:** AC6, AC9
- In `.claude/commands/harness-layer/harness-review.md`: add a **plan-fidelity** lens to the reviewer list — when the branch has a `specs/<name>/` plan, compare the diff against spec.md, tasks.md, and implementation-notes.md; a divergence from the plan with no implementation-notes entry is a finding (confidence-scored and filtered like every other lens). When no plan exists for the branch, the lens reports nothing.
- In `.agents/skills/spec-review/SKILL.md`: under "What to judge", add a blocking check — every entry in `decisions.md ## Blindspots` must carry a disposition (resolved, accepted-as-risk, or deferred-with-owner); an undispositioned blindspot is blocking. A missing `## Blindspots` section is already caught by the completeness gate; treat its absence in an older-format spec as advisory, not blocking.
- In `.agents/skills/implementation-review/SKILL.md`: in Inputs/Procedure, read `specs/<plan>/implementation-notes.md` when present and disposition each recorded deviation (conforming / needs-fix / contradicts-locked-decision → blocking); extend the delta-scope exclusion of `specs/<plan>/reviews/` to also exclude `specs/<plan>/artifacts/`.
- Keep all three files' existing contracts intact — additive edits only.

### 5. AGENTS.md Memory Line

- **Task ID:** agents-md-memory
- **Depends On:** none
- **Assigned To:** builder-memory
- **Agent Type:** general-purpose
- **Model / Effort:** `sonnet` / `low`
- **Parallel:** true
- **Satisfies:** AC10
- In `AGENTS.md`'s Harness-Layer Pipeline section, add one–two imperative lines: pipeline artifacts live in `specs/<name>/artifacts/` (committed) and publish best-effort as interactive pages; the unknowns checkpoints (blindspot pass, design directions, implementation notes, ship brief + quiz) fire conditionally per the pipeline commands. No rationale, no history.

### 6. Validate Everything

- **Task ID:** validate-all
- **Depends On:** templates-and-gate, plan-cmd-unknowns, build-cmd-unknowns, review-surfaces, agents-md-memory
- **Assigned To:** validator
- **Agent Type:** general-purpose
- **Model / Effort:** `sonnet` / `medium`
- **Parallel:** false
- Run every command in acceptance-criteria.md → `## Validation Commands`.
- Verify each acceptance criterion is met.
- Confirm `git diff origin/main --name-only` contains NO `harness-ship.md` (Non-Goal) and no file outside the Relevant Files list.
