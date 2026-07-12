# Tasks: Per-feature harness restructure — hooks, tests, build workflow

> Execution plan for [spec.md](./spec.md). Owner and scope are defined there; this file is how & who.

## Implementation Phases

### Phase 1: Foundation

Hook feature separation and command upgrades — two file-disjoint tasks that run in parallel:
the worktree hook move + settings.json consolidation, and the harness-build.md workflow edits.

### Phase 2: Core Implementation

Test tree restructure with distributed conftests — depends on Phase 1's new hook paths.

### Phase 3: Integration & Polish

Memory sync (HARNESS-LAYER.md, AGENTS.md) documenting the final state, then full validation.

## Team Orchestration

- You operate as the team lead and orchestrate the team to execute the plan.
- IMPORTANT: You NEVER operate directly on the codebase. You use the `Task*` tools to deploy team
  members to build, validate, test, and deploy. Your job is to direct, not to build.
- Keep the shared task list (TaskCreate/TaskUpdate) as the single source of truth for who is doing
  what; verify each task on the board before marking it complete.
- Note the session id / name of each team member — that is how you reference them.

## Team Members

- **Builder**
  - **Name:** builder-hooks
  - **Role:** worktree hook move, trimmed `_common.py`, settings.json repoint + consolidation
  - **Agent Type:** `general-purpose`
  - **Resume:** true
- **Builder**
  - **Name:** builder-commands
  - **Role:** the five harness-build.md workflow upgrades
  - **Agent Type:** `general-purpose`
  - **Resume:** true
- **Builder**
  - **Name:** builder-tests
  - **Role:** per-feature test tree, distributed conftests, path-depth fixes
  - **Agent Type:** `general-purpose`
  - **Resume:** true
- **Builder**
  - **Name:** builder-docs
  - **Role:** memory sync in HARNESS-LAYER.md and AGENTS.md
  - **Agent Type:** `general-purpose`
  - **Resume:** true
- **Builder**
  - **Name:** builder-validate
  - **Role:** run every validation command, verify each acceptance criterion
  - **Agent Type:** `general-purpose`
  - **Resume:** true

## Step by Step Tasks

- Execute every step in order, top to bottom. Each task maps directly to one `TaskCreate` call.
- Before starting, run `TaskCreate` for every task below so all team members can see the board.
- Each task names the acceptance criteria (from acceptance-criteria.md) it satisfies, so work traces to "done".

### 1. Worktree hook split + settings consolidation

- **Task ID:** `worktree-hook-split`
- **Depends On:** none
- **Assigned To:** builder-hooks
- **Agent Type:** `general-purpose`
- **Model / Effort:** `sonnet` / `medium`
- **Parallel:** true (file-disjoint from `build-command-upgrades`)
- **Satisfies:** AC2, AC3
- `git mv .claude/hooks/auto-format/worktree_create.py .claude/hooks/worktree/worktree_create.py`
  and likewise `worktree_remove.py` — no code edits; shebang blocks untouched.
- Create `.claude/hooks/worktree/_common.py`: copy exactly `note`, `read_payload`, `resolve_root`,
  `run`, `tail` PLUS the module constant `STDIN_TIMEOUT = 5.0` (read by `read_payload`) from
  `auto-format/_common.py`, with only the imports those helpers need and the module docstring
  adapted; signatures and bodies unchanged. Nothing else — no `VENDORED_DIRS`, no
  `DIAGNOSTIC_CAP`, none of the other helpers. The exact surface is AST-asserted by
  `specs/per-feature-harness-restructure/validate.py` — run it before hand-off.
- `.claude/settings.json`: repoint the `WorktreeCreate` and `WorktreeRemove` commands to
  `.claude/hooks/worktree/…`; replace the five PostToolUse `Write|Edit|MultiEdit` entries with ONE
  block whose `hooks` array lists the five commands in order js_ts, data, markdown, python,
  post_write_scan (order carries no execution semantics — hooks run in parallel).
- Smoke: `echo '{"worktreeName":"smoketest"}' | uv run --script .claude/hooks/worktree/worktree_create.py`
  in a throwaway temp git repo (not this worktree), then remove via the remove hook.

### 2. harness-build.md workflow upgrades

- **Task ID:** `build-command-upgrades`
- **Depends On:** none
- **Assigned To:** builder-commands
- **Agent Type:** `general-purpose`
- **Model / Effort:** `opus` / `high`
- **Parallel:** true (file-disjoint from `worktree-hook-split`)
- **Satisfies:** AC4
- Fixer routing (Instructions bullet + Verification "Otherwise" paragraph): the build lead picks
  each fixer's MODEL per issue difficulty from the AGENTS.md table (`opus` complex / `sonnet`
  standard), passed via the Agent tool's `model` param, and states the AGENTS.md EFFORT tier in
  the fixer's task brief as depth guidance — subagents inherit the session's reasoning effort
  (KB: subagents), so the command must not claim an `effort` parameter. Remove both hardcoded
  "fixer subagent (effort per issue)" phrasings.
- Combined fix pass: cluster merged blockers by root cause + touched files; disjoint clusters run
  as parallel background fixer subagents in the same worktree, overlapping clusters sequenced;
  still exactly ONE fix commit after all fixers return (report-commit/fix-commit/single-push
  protocol unchanged).
- Implement step: the lead launches all currently-unblocked, file-disjoint tasks concurrently as
  background agents; tasks.md keeps owning the dependency structure.
- Agent Task Manifest (Instructions bullet + PR body section): the task column is keyed by the
  plan's kebab-case Task ID; state explicitly "never `#N` — GitHub autolinks it to unrelated
  issues/PRs".
- Open-the-draft-PR step: `gh pr create` gains `--assignee $(gh api user -q .login)` and mirrors
  the linked issue's type label and `priority:P<n>` label (read via
  `gh issue view <N> --json labels`).
- Keep the command's KISS prose style; no other sections touched (R1-concurrency flow unchanged).
- `specs/per-feature-harness-restructure/validate.py` is the executable contract for these edits —
  its six AC4 clause checks (relationships, not fragments) must all pass; run it before hand-off.

### 3. Per-feature test tree + distributed conftests

- **Task ID:** `tests-per-feature`
- **Depends On:** `worktree-hook-split`
- **Assigned To:** builder-tests
- **Agent Type:** `general-purpose`
- **Model / Effort:** `sonnet` / `medium`
- **Parallel:** false (needs the new hook paths)
- **Satisfies:** AC1, AC2
- `git mv` per the spec's Relevant Files map: five auto-format test files → `hooks/auto-format/`;
  `test_block_attribution.py` → `hooks/attribution/`; the two worktree test files →
  `hooks/worktree/`; the two security-scan test files → `hooks/security-scan/`.
- Slim the shared `hooks/conftest.py` to cross-feature helpers: `REPO_ROOT` (`parents[3]`,
  unchanged), `UV`, and `run_hook` resolving `script_name` against a `hook_dir` fixture the shared
  file declares (no default — each feature overrides it).
- New `hooks/auto-format/conftest.py`: `hook_dir` → `.claude/hooks/auto-format`; `linter_root`
  moves here.
- New `hooks/attribution/conftest.py`: `hook_dir` → `.claude/hooks`; adapt
  `test_block_attribution.py` to the shared `run_hook` or keep its local runner — either way fix
  `parents[3]` → `parents[4]`.
- New `hooks/worktree/conftest.py`: `hook_dir` → `.claude/hooks/worktree`; `wt_repo`,
  `STUB_TEMPLATE`, `_write_stubs`, `_git` move here.
- Security-scan files keep module-level importlib loading (import-time constants); fix
  `parents[2]` → `parents[4]` in both. No security-scan conftest (nothing fixture-shaped to host).
- No `__init__.py` anywhere; all basenames stay unique.

### 4. Memory sync

- **Task ID:** `memory-sync`
- **Depends On:** `worktree-hook-split`, `build-command-upgrades`, `tests-per-feature`
- **Assigned To:** builder-docs
- **Agent Type:** `general-purpose`
- **Model / Effort:** `sonnet` / `low`
- **Parallel:** false
- **Satisfies:** AC5
- HARNESS-LAYER.md: move the worktree bullets out of the Auto-Format section into their own
  Worktree Lifecycle paths (`.claude/hooks/worktree/…`); redraw the Files tree (hooks dirs + new
  test tree); add the rule line: "Register hooks with one matcher block per event+matcher pair —
  additional hooks join that block's `hooks` array, never a repeated matcher entry."
- AGENTS.md Python Testing: add one line — during feature work run
  `uv run pytest tests/harness-layer/hooks/<feature>`; run the full suite before hand-off.

### 5. Validate Everything

- **Task ID:** validate-all
- **Depends On:** `worktree-hook-split`, `build-command-upgrades`, `tests-per-feature`, `memory-sync`
- **Assigned To:** builder-validate
- **Agent Type:** `general-purpose`
- **Model / Effort:** `sonnet` / `low`
- **Parallel:** false
- Run every command in acceptance-criteria.md → `## Validation Commands`.
- Verify each acceptance criterion is met.
