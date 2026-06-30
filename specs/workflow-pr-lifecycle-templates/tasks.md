# Tasks: Unify the lifecycle on one PR + standardize workflow templates

> Execution plan for [spec.md](./spec.md). Owner and scope are defined there; this file is how & who.

## Implementation Phases

### Phase 1: Foundation

Author the canonical-template catalog (`WORKFLOW-TEMPLATES.md`). It is the keystone every
later task references, so it must define the fixed layout + a filled example for each
standardized output before any command/template is wired to it.

### Phase 2: Core Implementation

Wire the three commands (`plan-w-team.md`, `build.md`, `ship.md`) to the catalog and apply
the behavioral changes — PR-at-plan-time, resume-in-build, issue-lifecycle advance,
manifest-from-`tasks.md` — plus the light-touch skill relay-note updates.

### Phase 3: Integration & Polish

Update the 8 PR templates to the unified body skeleton, fix the stale references and the
manifest description in the standards docs, cite the catalog from `AGENTS.md`, then validate
everything structurally.

## Team Orchestration

- You operate as the team lead and orchestrate the team to execute the plan.
- IMPORTANT: You NEVER operate directly on the codebase. You use the `Task*` tools to deploy team
  members to build, validate, test, and deploy. Your job is to direct, not to build.
- Keep the shared task list (TaskCreate/TaskUpdate) as the single source of truth for who is doing
  what; verify each task on the board before marking it complete.
- Note the session id / name of each team member — that is how you reference them.

## Team Members

- **Builder — catalog author**
  - **Name:** builder-catalog
  - **Role:** Author `WORKFLOW-TEMPLATES.md` — every canonical template with layout + example.
  - **Agent Type:** general-purpose
  - **Resume:** true

- **Builder — command wiring**
  - **Name:** builder-commands
  - **Role:** Wire `plan-w-team.md`, `build.md`, `ship.md` (+ light-touch the two skills) to the catalog and apply the behavioral changes.
  - **Agent Type:** general-purpose
  - **Resume:** true

- **Builder — templates & docs**
  - **Name:** builder-templates-docs
  - **Role:** Update the 8 PR templates to the unified skeleton; fix the stale refs + manifest description; cite the catalog from `AGENTS.md`.
  - **Agent Type:** general-purpose
  - **Resume:** true

- **Validator**
  - **Name:** validator
  - **Role:** Run the structural validation commands and confirm every acceptance criterion.
  - **Agent Type:** general-purpose
  - **Resume:** true

## Step by Step Tasks

- Execute every step in order, top to bottom. Each task maps directly to one `TaskCreate` call.
- Before starting, run `TaskCreate` for every task below so all team members can see the board.
- Each task names the acceptance criteria (from acceptance-criteria.md) it satisfies, so work traces to "done".

### 1. Author the canonical-template catalog

- **Task ID:** author-catalog
- **Depends On:** none
- **Assigned To:** builder-catalog
- **Agent Type:** general-purpose
- **Parallel:** false
- **Satisfies:** AC1, AC8
- Create `WORKFLOW-TEMPLATES.md` at repo root with one section per standardized output, each carrying a fixed **layout** + a **filled example**:
  - Unified **PR body skeleton** (title · `## Lifecycle` line · `## Summary` · `## Linked Issue` `Closes #N` · `## Spec-review status` · `## Agent Task Manifest` · `## Build Status`).
  - The **`## Lifecycle` marker line** (`Plan ▸ Spec-review ▸ Approved ▸ Build ▸ Ship ▸ Done`) + the rule for who advances ▲ where (plan-w-team→Approved, build→Build, ship→Done).
  - The two **status-mirror blocks** (Spec-review status; Build Status) as idempotent, overwritten-in-place state.
  - The **Agent Task Manifest** format: sourced from `tasks.md`, grouped by phase, kebab IDs, `satisfies AC#`, **no `#<number>`**.
  - **Per-phase PR comments** (Implementation · Internal check · Claude code review · Codex review R1/R2 relay · Fixes applied · Result).
  - **Codex relay comments** in both directions: spec-review→issue (port the existing canonical snippet here) and impl-review→PR (new, at parity).
  - **Claude→Codex invocation prompts** (the verbatim `codex exec` strings for spec-review and implementation-review).
  - **Codex→Claude report/verdict formats** Claude reads (the `### Round N — Verdict: …` header shape; reference the skill contracts, do not duplicate their logic).
  - The final **`/build` report** and **`/ship` report** layouts.
  - State the cross-cutting **comment = history (appended) / body = state (overwritten)** principle once, up top.

### 2. Wire `/plan-w-team` — PR at plan time + spec-review PR mirror

- **Task ID:** wire-plan
- **Depends On:** author-catalog
- **Assigned To:** builder-commands
- **Agent Type:** general-purpose
- **Parallel:** false
- **Satisfies:** AC2, AC3, AC8
- After the first plan push, add a step that opens **one draft PR** (`gh pr create --draft --template <type>.md --base main --head <branch> --assignee @me --label <type-label> --title …`) seeded with the unified PR body skeleton from the catalog (Lifecycle ▲ at Spec-review, Spec-review status, empty Build Status).
- Add the spec-review **PR-state mirror**: each round, after the existing issue comment + issue-body status update, also overwrite the PR body's `## Spec-review status` block (state only; keep the issue authoritative for history).
- On settle, advance the **issue** Lifecycle ▲ and set Status as today; the PR mirrors the same state.
- Replace the embedded "Canonical issue snippets" block with a **reference to the catalog**.
- Honor the existing graceful `gh` skip (no PR when `gh`/remote unavailable).

### 3. Wire `/build` — resume the PR, manifest from `tasks.md`, advance the issue

- **Task ID:** wire-build
- **Depends On:** author-catalog
- **Assigned To:** builder-commands
- **Agent Type:** general-purpose
- **Parallel:** false
- **Satisfies:** AC2, AC4, AC5, AC6, AC8
- Phase 1: change "open the draft PR" to **resume the existing plan-time draft PR** (find by `#N`/head branch); **fallback-create** only when absent (gh was down at plan time / legacy). Never open a second PR.
- Seed the **Agent Task Manifest from `tasks.md`** (kebab IDs, grouped by phase, `satisfies AC#`), ticked as each matching `Task*` board item completes; for legacy flat specs with no `tasks.md`, degrade to the runtime board with non-`#` IDs.
- Advance the **issue** Lifecycle ▲ to **Build** at build start.
- Replace ad-hoc `gh pr comment` bodies with the catalog's per-phase comment references; use the catalog's **impl-review relay** comment (parity with spec-review).
- Phase 6: advance the issue ▲ to **Ship** (awaiting `/ship`) and mark the PR ready.
- **Do NOT touch** the legacy `plan.md` fallback in Phase 0 (retain verbatim).

### 4. Wire `/ship` — advance to Done + fix the dangling ref

- **Task ID:** wire-ship
- **Depends On:** author-catalog
- **Assigned To:** builder-commands
- **Agent Type:** general-purpose
- **Parallel:** false
- **Satisfies:** AC2, AC7, AC8
- On confirmed merge, advance the **issue** Lifecycle ▲ to **Done** (before/at `Closes #N` close).
- Fix the **"Workstream C"** dangling reference (`ship.md:~80`) — reword to reference the actual lifecycle, not a non-existent plan structure.
- Reference the catalog's `/ship` **final-report** layout.

### 5. Light-touch the two Codex skills

- **Task ID:** wire-skills
- **Depends On:** author-catalog
- **Assigned To:** builder-commands
- **Agent Type:** general-purpose
- **Parallel:** false
- **Satisfies:** AC8
- In `spec-review/SKILL.md` and `implementation-review/SKILL.md`, point the existing **Verdict relay (orchestrator-only)** note at the catalog as the home of the relay-comment format.
- **Do NOT change** the finding bar, verdict rule, output contract, or report format of either skill.

### 6. Update the 8 PR templates to the unified skeleton

- **Task ID:** update-pr-templates
- **Depends On:** author-catalog
- **Assigned To:** builder-templates-docs
- **Agent Type:** general-purpose
- **Parallel:** true
- **Satisfies:** AC3, AC4
- In each of `.github/PULL_REQUEST_TEMPLATE/{feat,fix,docs,style,refactor,perf,test,chore}.md`, add the `## Lifecycle` line and `## Spec-review status` block, and replace the Agent Task Manifest section with the **no-`#`, `tasks.md`-sourced** format from the catalog. Keep each template's type-specific sections (Summary/Changes/Root-cause/etc.).

### 7. Fix stale refs + manifest description + cite the catalog

- **Task ID:** update-standards-docs
- **Depends On:** author-catalog
- **Assigned To:** builder-templates-docs
- **Agent Type:** general-purpose
- **Parallel:** true
- **Satisfies:** AC1, AC7
- `GIT-COMMIT-PR-MESSAGE.md`: fix `epic-plan.md`→`epic-spec.md` and `specs/<feature>/plan.md`→`specs/<feature>/spec.md`; update the Agent Task Manifest description to the no-`#`, `tasks.md`-sourced format.
- `AGENTS.md`: add a citation to `WORKFLOW-TEMPLATES.md` (mirror the `GIT-COMMIT-PR-MESSAGE.md` citation style).

### 8. Validate Everything

- **Task ID:** validate-all
- **Depends On:** author-catalog, wire-plan, wire-build, wire-ship, wire-skills, update-pr-templates, update-standards-docs
- **Assigned To:** validator
- **Agent Type:** general-purpose
- **Parallel:** false
- Run every command in acceptance-criteria.md → `## Validation Commands`.
- Verify each acceptance criterion is met (AC1–AC8).
