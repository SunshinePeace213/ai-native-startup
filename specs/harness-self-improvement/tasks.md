# Tasks: harness-self-improvement — Plan 1

> Execution plan for [spec.md](./spec.md). Owner and scope are defined there; this file is how & who.

## Implementation Phases

### Phase 1: Foundation

The gate rework — session-scoped targeting first (everything about the gate's correctness rests
on it), then the lint extension on top of the re-targeted selection. Sequential: both edit
`check_spec_completeness.py` and its test file.

### Phase 2: Core Implementation

The two independent deliverables in parallel: the prompt-contract suite (new `tests/harness-layer/prompts/`)
and the CI workflow. Neither touches the hook or each other's files.

### Phase 3: Integration & Polish

Full-suite validation: run every validation command, the whole `tests/harness-layer` suite, and
verify each acceptance criterion.

## Team Orchestration

- You operate as the team lead and orchestrate the team to execute the plan.
- IMPORTANT: You NEVER operate directly on the codebase. You use the `Task*` tools to deploy team
  members to build, validate, test, and deploy. Your job is to direct, not to build.
- Keep the shared task list (TaskCreate/TaskUpdate) as the single source of truth for who is doing
  what; verify each task on the board before marking it complete.
- Note the session id / name of each team member — that is how you reference them.
- **Deployment mechanics:** deploy each task through the Agent tool passing its stamped `model`
  alias. The Agent tool exposes no per-invocation effort and `general-purpose` carries no
  definition frontmatter, so every deployment runs at session-inherited effort (subagent `effort`
  is a definition-level field defaulting to session inheritance — `ai-docs/anthropic/subagents.md`).

## Team Members

- **Builder**
  - **Name:** builder-hook
  - **Role:** the Stop gate — session-scoped re-target, then the lint extension, with their tests
  - **Agent Type:** `general-purpose`
  - **Resume:** true (task 2 continues task 1's context in the same files)
- **Builder**
  - **Name:** builder-contracts
  - **Role:** the prompt-contract suite under `tests/harness-layer/prompts/`
  - **Agent Type:** `general-purpose`
  - **Resume:** true
- **Builder**
  - **Name:** builder-ci
  - **Role:** the GitHub Actions workflow
  - **Agent Type:** `general-purpose`
  - **Resume:** true
- **Validator**
  - **Name:** validator
  - **Role:** run every validation command and confirm each acceptance criterion
  - **Agent Type:** `general-purpose`
  - **Resume:** false

## Step by Step Tasks

- Execute every step in order, top to bottom. Each task maps directly to one `TaskCreate` call.
- Before starting, run `TaskCreate` for every task below so all team members can see the board.
- Each task names the acceptance criteria (from acceptance-criteria.md) it satisfies, so work traces to "done".

### 1. Re-target the Stop gate to the invoking session

- **Task ID:** retarget-stop-gate
- **Depends On:** none
- **Assigned To:** builder-hook
- **Agent Type:** `general-purpose`
- **Model / Effort:** `opus` / session-inherited (Agent tool passes `model` only)
- **Parallel:** false
- **Satisfies:** AC1
- Rework `check_spec_completeness.py`: parse stdin JSON; resolve root as `git -C <cwd> rev-parse --show-toplevel` → stdin `cwd` itself (if a directory) → `$CLAUDE_PROJECT_DIR` → process git toplevel → `Path.cwd()`; scan only `<root>/specs/*`; delete the `.claude/worktrees/*/specs` glob. Keep the `_templates` / discovery-only exclusions and newest-mtime selection within the root. Malformed stdin degrades down the chain — never crash, never exit 2 on plumbing.
- Rewrite `tests/harness-layer/hooks/spec-completeness/test_check_spec_completeness.py`: the Stop payload now carries `cwd`; replace `test_worktree_specs_are_discovered` and `test_no_main_specs_dir_skips_even_with_worktree_specs` with session-scoped equivalents.
- Add the concurrency regression tests (the would-have-caught replay of the soriza wrong-target class): (a) session root's plan incomplete + foreign root's plan complete and newer → exit 2 naming the session's folder; (b) session root's plan complete + foreign root's plan incomplete and newer → exit 0; (c) mtime decoy in a foreign root never changes the selected folder; (d) malformed/empty stdin and cwd-outside-git fall back without crashing.
- Update the `check_spec_completeness.py` row in `.claude/rules/harness-layer/hooks.md` to say the gate is session-scoped via stdin `cwd` (ship-together rule). Registration is unchanged — `test_wiring.py` needs no edit; confirm it still passes.
- **Memory-flagged:** the session-scoped-stdin targeting pattern is a candidate cross-plan lesson for the build/review memory step.

### 2. Extend the gate with the validation-command lint

- **Task ID:** stop-gate-lint
- **Depends On:** retarget-stop-gate
- **Assigned To:** builder-hook
- **Agent Type:** `general-purpose`
- **Model / Effort:** `opus` / session-inherited (Agent tool passes `model` only)
- **Parallel:** false
- **Satisfies:** AC2
- In the same hook, after the required-sections check on the selected folder: parse `## Validation Commands` bullets (lines starting `-` in that section) of acceptance-criteria.md. Block (exit 2, naming file + offending bullet): no recognized stage tag (`[plan-time]`, `[child-build-time]`, `[post-merge]`); invoking neither `uv run --script specs/<plan>/checks/…` nor `uv run pytest …`; a `[plan-time]` script path that does not exist under the root.
- Warn only (`WARN:` prefix on stderr, exit code unchanged, ≤10 warnings total): later-stage (`[child-build-time]`/`[post-merge]`) paths that do not exist yet; absolute-promise wording in the folder's spec.md (case-insensitive word match on `always`, `never`, `guaranteed`/`guarantees`, `under no circumstances`, `in all cases`), each warning citing file:line.
- Contract tests in the same test file: block and allow paths for each rule; warn lines present without exit-code change; the template's own prose paragraph (non-bullet lines) is ignored; a compliant folder (like this plan's) passes end to end.
- Stdlib only — no pyyaml, no third-party deps (Codex sandbox has no network).

### 3. Build the prompt-contract suite

- **Task ID:** contract-tests
- **Depends On:** none
- **Assigned To:** builder-contracts
- **Agent Type:** `general-purpose`
- **Model / Effort:** `sonnet` / session-inherited (Agent tool passes `model` only)
- **Parallel:** true (alongside tasks 1–2 and 4)
- **Satisfies:** AC3
- First promote the `load_hook_module` fixture: move it verbatim from
  `tests/harness-layer/hooks/conftest.py` to a new `tests/harness-layer/conftest.py`, re-deriving
  its `REPO_ROOT`/`HOOKS_ROOT` constants for the new depth; leave `run_hook`, `base_env`, and the
  git-isolation constants in `hooks/conftest.py`. Hooks tests keep resolving the fixture from the
  parent conftest; removing the fixture from `hooks/conftest.py` is the only edit this task makes
  under `hooks/`.
- Create `tests/harness-layer/prompts/test_command_contracts.py` and `test_skill_contracts.py` in `test_wiring.py`'s style: module-level per-file expectation maps (frontmatter literals, exact `##` section tuples, clause lists) taken verbatim from spec.md's `## Load-Bearing Contract Inventory`, checked by small pure helpers (frontmatter extractor, section lister, `missing_pins(text, expectations)`), each test docstring stating WHY the pin matters.
- Add the cross-consistency tests: every `REQUIRED_SECTIONS` heading (via `load_hook_module`) appears in its `specs/_templates/` file; `harness-plan.md` and `spec-review/SKILL.md` agree on `codex-spec-review-round-`; `harness-review.md` and `implementation-review/SKILL.md` agree on `codex-impl-review-round-`; both skills carry the identical em-dash verdict grammar; each skill's `name:` equals its directory name.
- Add the #40/#42 replay tests: feed `missing_pins` the real harness-build.md / harness-review.md text with `## Report` (3ce40db, #40) and `## Instructions` (c4bf3fa, #42) stripped, and assert the loss is flagged — docstrings cite the restore commits.
- Section-set asserts are exact (missing AND unexpected headings fail) — the ship-together rule, not brittleness.

### 4. Add the CI workflow

- **Task ID:** ci-workflow
- **Depends On:** none
- **Assigned To:** builder-ci
- **Agent Type:** `general-purpose`
- **Model / Effort:** `sonnet` / session-inherited (Agent tool passes `model` only)
- **Parallel:** true (alongside tasks 1–3)
- **Satisfies:** AC4
- Create `.github/workflows/harness-tests.yml`: `on: pull_request` with `types: [opened, synchronize, reopened, edited]` and `paths: ['.claude/**', '.agents/**', 'tests/**', 'pyproject.toml', 'uv.lock', 'specs/_templates/**', '.github/workflows/harness-tests.yml']`; one job with `if: ${{ !contains(github.event.pull_request.title, '[skip-ci]') }}`, running checkout → astral-sh/setup-uv (cache enabled) → `uv run pytest tests/harness-layer`.
- Pin both action versions against the official docs (the KB has no mirror this run — verify, don't guess; record the verified versions in the PR body's test evidence).
- Run `uv run --script specs/harness-self-improvement/checks/ac4_ci_workflow.py` and make it pass.

### 5. Validate Everything

- **Task ID:** validate-all
- **Depends On:** retarget-stop-gate, stop-gate-lint, contract-tests, ci-workflow
- **Assigned To:** validator
- **Agent Type:** `general-purpose`
- **Model / Effort:** `sonnet` / session-inherited (Agent tool passes `model` only)
- **Parallel:** false
- Run every command in acceptance-criteria.md → `## Validation Commands`.
- Run the full `uv run pytest tests/harness-layer` suite (pre-hand-off rule) and report exact results — no skips glossed over.
- Verify each acceptance criterion is met; report per-AC PASS/FAIL with evidence.
