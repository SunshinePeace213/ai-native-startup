# Tasks: Seed the design KB group + worktree availability (child #44 of epic #43)

> Execution plan for [spec.md](./spec.md). Owner and scope are defined there; this file is how & who.
> Simple chore — no implementation phases. Builders and model/effort stamps are transcribed
> from the epic's tasks.md (task 2).

## Team Orchestration

- You operate as the team lead and orchestrate the team to execute the plan.
- IMPORTANT: You NEVER operate directly on the codebase. You use the `Task*` tools to deploy team
  members to build, validate, test, and deploy. Your job is to direct, not to build.
- Keep the shared task list (TaskCreate/TaskUpdate) as the single source of truth for who is doing
  what; verify each task on the board before marking it complete.
- Note the session id / name of each team member — that is how you reference them.

## Team Members

- **kb-builder**
  - **Name:** kb-builder
  - **Role:** the `.worktreeinclude` edit + the six `/harness-layer:kb add` runs (fetching
    fans out to `kb-fetcher` subagents per the kb command's own contract — the builder never
    writes mirror content itself); records any source swap in decisions.md.
  - **Agent Type:** general-purpose
  - **Model / Effort:** `sonnet` / `low` (guarded mechanical flow — epic stamp)
  - **Resume:** true
- **validator**
  - **Name:** validator
  - **Role:** runs every command in acceptance-criteria.md `## Validation Commands` and
    verifies each AC, including the tracked-change surface.
  - **Agent Type:** general-purpose
  - **Model / Effort:** `sonnet` / `low` (epic stamp)
  - **Resume:** false

## Step by Step Tasks

- Execute every step in order, top to bottom. Each task maps directly to one `TaskCreate` call.
- Before starting, run `TaskCreate` for every task below so all team members can see the board.
- Each task names the acceptance criteria (from acceptance-criteria.md) it satisfies, so work traces to "done".

### 1. Add the ai-docs pattern to .worktreeinclude

- **Task ID:** worktreeinclude-pattern
- **Depends On:** none
- **Assigned To:** kb-builder
- **Agent Type:** general-purpose
- **Model / Effort:** `sonnet` / `low`
- **Parallel:** false
- **Satisfies:** AC1
- **Memory:** record the worktree-include/WorktreeCreate-hook interplay as a dev-log lesson
  if it bites during the build (epic task 2's memory flag).
- Append to `.worktreeinclude`: one comment line explaining the KB copy (e.g.
  `# KB mirrors — gitignored; copied into fresh worktrees by the WorktreeCreate hook`)
  followed by the single pattern line `ai-docs/*`.
- Leave the existing env-file lines byte-for-byte untouched.
- Sanity-check with the AC1 fnmatch simulation once mirrors exist (after tasks 2–3).

### 2. Register and mirror the five design sources

- **Task ID:** kb-seed-design
- **Depends On:** worktreeinclude-pattern
- **Assigned To:** kb-builder
- **Agent Type:** general-purpose
- **Model / Effort:** `sonnet` / `low`
- **Parallel:** false
- **Satisfies:** AC2, AC4, AC5, AC6
- Run `/harness-layer:kb add <url> design` once per source, sequentially, in the spec's
  table order (1, 2, 5 as listed; pick the two NN/g canonical `articles/` URLs at this
  point — proposed homepage cornerstone first, then the writing-for-the-web article).
- After each run, confirm the kb report: OK → canonical url + today's `fetched` written to
  the manifest, mirror on disk; FAIL → leave `fetched: null`, substitute the canonical
  same-topic page per spec.md `## Edge Cases`.
- After each run, append its result verbatim to decisions.md
  `### Build addendum — kb run record`: `- OK <file> <canonical url>` on success; on a
  substitution additionally `- FAIL <original url> → swapped to <substitute url>: <reason>`.
  This record is the provenance AC2's validation parses — no OK line, no pass.
- Never hand-edit a mirror or `ai-docs/index.md`; never pass `--force`.

### 3. Register and mirror the anthropic memory page

- **Task ID:** kb-seed-memory
- **Depends On:** kb-seed-design
- **Assigned To:** kb-builder
- **Agent Type:** general-purpose
- **Model / Effort:** `sonnet` / `low`
- **Parallel:** false
- **Satisfies:** AC3, AC4, AC5
- Run `/harness-layer:kb add https://code.claude.com/docs/en/memory anthropic`.
- Confirm the manifest entry lands in the `anthropic` group with a canonical url, a
  `file` under `anthropic/`, a non-null `fetched`, and that `ai-docs/index.md` lists it.
- Append the run's `- OK <file> <canonical url>` line to decisions.md
  `### Build addendum — kb run record`.

### 4. Validate Everything

- **Task ID:** validate-all
- **Depends On:** worktreeinclude-pattern, kb-seed-design, kb-seed-memory
- **Assigned To:** validator
- **Agent Type:** general-purpose
- **Model / Effort:** `sonnet` / `low`
- **Parallel:** false
- Run every command in acceptance-criteria.md → `## Validation Commands`. They are
  sequence-independent (the AC6 surface check measures the working tree against
  `origin/main`), so run them before the build's commit and re-run after if anything moved.
- Verify each acceptance criterion is met; confirm the change surface outside `specs/` is
  exactly `.worktreeinclude` + `ai-docs/sources.yaml` (AC6) and the kb run record covers all
  six sources (AC2).
