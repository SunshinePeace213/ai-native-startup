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
- Add a `Blindspot Pass` workflow step between "Understand Codebase"/"Set Review Profile" and "Grill Requirements": scan the task against the codebase and (when active) the KB; report the top unknown unknowns as inline cards — what / why it matters / proposed resolution (simple → ~3, medium/complex → up to ~7). Unresolved cards seed the grilling ledger first; every card and its disposition is recorded in `decisions.md ## Blindspots`.
- In the `Grilling Protocol`: order questions by architectural blast radius (answers that would change the architecture come first); add the taste route — when a decision is one the user would recognize but can't specify (UX, output format, report layout) or the user asks, present 2–4 concrete alternatives inline via AskUserQuestion labels and rich descriptions, using option previews only where the running harness supports them (best-effort, never a required contract); a decision that truly needs a rendered comparison is recorded as PROVISIONAL in the ledger; record every choice in decisions.md as usual.
- In "Write the Spec Folder": for medium/complex plans, author the durable artifacts inside the worktree under `specs/<name-of-plan>/artifacts/` — a blindspot-cards page and, when the taste route fired, a design-directions page rendering the alternatives and the chosen one — then publish each best-effort via the Artifact tool FROM those project-local files (per `ai-docs/anthropic/artifacts.md`: the page is written to a project file, then published). Re-confirm any PROVISIONAL taste decision with one AskUserQuestion against the design-directions page before the spec commit. On availability failure, keep the file and note "publish skipped"; never block. They commit with the spec.
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
- Implement step: create `specs/<name>/implementation-notes.md` from `specs/_templates/implementation-notes.md` at implement start; every builder's hand-off gains a **Deviations** field (what diverged from the plan, what forced it, the call made — "none" allowed); the lead folds entries into the notes file at each checkpoint commit. Scope ONE explicit **lead-owned non-implementation-file exception** in the Instructions covering exactly: creating and folding implementation-notes.md, authoring `specs/<name>/artifacts/ship-brief.html` in the approving round, and the existing `## Tracking` / `## Locked Boundaries` edits — plan bookkeeping and presentation, never implementation files. A deviation touching a locked decision or acceptance criterion STOPS for an AskUserQuestion gate before work proceeds (mirror the existing Locked Boundaries user-approval language).
- Review packet: add a pointer to `specs/<name>/implementation-notes.md` so Codex dispositions deviations rather than rediscovering them.
- Delta scope: every place that excludes `specs/<name>/reviews/` also excludes `specs/<name>/artifacts/`.
- Ship brief (every approval path — round-1 both-clean, round-2 approved, approved round 3): for medium/complex plans, after reading the `approved` verdict and BEFORE making that round's report commit, author `specs/<name>/artifacts/ship-brief.html` — leads with what shipped, pre-answers reviewer objections with evidence links (report comments, validation results), ends in a 3–6 question quiz whose wrong answers point at the file/section to re-read. Stage report + brief as ONE commit — the approved head recorded in the stage table. The brief is authored fresh in whichever round approves; never reuse one from a failed round. Simple plans skip the brief and quiz.
- Finish step: publish the brief best-effort via the Artifact tool from the project file; add a `## Ship Brief` entry (file path + URL, or "publish skipped") to the PR body; verify the PR head equals the report+brief commit; the final Report tells the user to take the quiz before `/harness-layer:harness-ship`.
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
- Read each changed file against every AC clause (ordering, gates, ownership, exclusions, dispositions, PR-body behavior, brief freshness, the ≤2-line memory constraint) and record clause-by-clause results in the hand-off — the grep commands are smoke checks, not the proof.
- Confirm `git diff origin/main --name-only -- ':!specs/unknowns-aware-pipeline'` lists only files named in spec.md `## Relevant Files` (including New Files) and contains NO `harness-ship.md` (Non-Goal). The plan folder itself (spec files, reviews/, artifacts/, implementation-notes.md) is baseline, not implementation.
