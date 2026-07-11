# Tasks: auto-format-hooks

> Execution plan for [spec.md](./spec.md). Owner and scope are defined there; this file is how & who.

## Implementation Phases

### Phase 1: Foundation

ESLint toolchain (packages + `eslint.config.mjs`) and the shared `_common.py` helper — everything the six hooks depend on.

### Phase 2: Core Implementation

The four format hooks and the two worktree lifecycle hooks, built in parallel on the shared foundation, plus their pytest suites.

### Phase 3: Integration & Polish

Hook registration in `.claude/settings.json`, the `/meta-install` command → skill replacement, memory updates (`HARNESS-LAYER.md`, `AGENTS.md`), and full validation.

## Team Orchestration

- You operate as the team lead and orchestrate the team to execute the plan.
- IMPORTANT: You NEVER operate directly on the codebase. You use the `Task*` tools to deploy team
  members to build, validate, test, and deploy. Your job is to direct, not to build.
- Keep the shared task list (TaskCreate/TaskUpdate) as the single source of truth for who is doing
  what; verify each task on the board before marking it complete.
- Note the session id / name of each team member — that is how you reference them.

## Team Members

- **Builder**
  - **Name:** builder-toolchain
  - **Role:** ESLint toolchain, hook registration, meta-install skill, memory updates — everything that is config, docs, or dependencies rather than hook logic.
  - **Agent Type:** `general-purpose`
  - **Resume:** true
- **Builder**
  - **Name:** builder-hooks
  - **Role:** All Python under `.claude/hooks/auto-format/` — `_common.py`, the four format hooks, the two worktree hooks — and their pytest suites.
  - **Agent Type:** `general-purpose`
  - **Resume:** true
- **Builder**
  - **Name:** validator
  - **Role:** Final validation only — runs every command in acceptance-criteria.md and verifies each criterion against the working tree.
  - **Agent Type:** `general-purpose`
  - **Resume:** false

## Step by Step Tasks

- Execute every step in order, top to bottom. Each task maps directly to one `TaskCreate` call.
- Before starting, run `TaskCreate` for every task below so all team members can see the board.
- Each task names the acceptance criteria (from acceptance-criteria.md) it satisfies, so work traces to "done".

### 1. Add the ESLint toolchain

- **Task ID:** add-eslint-toolchain
- **Depends On:** none
- **Assigned To:** builder-toolchain
- **Agent Type:** `general-purpose`
- **Parallel:** true (alongside build-common-helper)
- **Satisfies:** AC1
- `bun add -d eslint @eslint/js typescript-eslint eslint-config-prettier eslint-plugin-react eslint-plugin-react-hooks`
- Author flat `eslint.config.mjs`: `@eslint/js` recommended for `.js/.jsx/.ts/.tsx`, `typescript-eslint` recommended for `.ts/.tsx`, `eslint-plugin-react` + `eslint-plugin-react-hooks` recommended (React version detection configured), `eslint-config-prettier` last; ignore `node_modules`, `.venv`, `dist`, `.claude/worktrees`.
- Prove it: run `node_modules/.bin/eslint --fix` on a throwaway fixture with a known auto-fixable violation and confirm the fix lands; delete the fixture.

### 2. Build the shared helper module

- **Task ID:** build-common-helper
- **Depends On:** none
- **Assigned To:** builder-hooks
- **Agent Type:** `general-purpose`
- **Parallel:** true (alongside add-eslint-toolchain)
- **Satisfies:** AC6 (foundations for AC2–AC5)
- Write `.claude/hooks/auto-format/_common.py`: bounded stdin read + snake_case payload parse returning `tool_input.file_path` (mirror `block_attribution.py`'s `select`-based fail-open read), project-root resolution (`$CLAUDE_PROJECT_DIR` → script-relative fallback), `run()` subprocess wrapper that never raises, vendored-skip check on root-relative parts (`node_modules`, `.venv`, `dist`), diagnostic formatter (cap 10 + "and N more"), `note()` stderr helper.
- Write `tests/harness-layer/hooks/test_common.py` covering payload parsing (good/empty/malformed/TTY), root resolution, and the vendored-skip relative-path rule.

### 3. Build the four format hooks

- **Task ID:** build-format-hooks
- **Depends On:** add-eslint-toolchain, build-common-helper
- **Assigned To:** builder-hooks
- **Agent Type:** `general-purpose`
- **Parallel:** true (alongside build-worktree-hooks)
- **Satisfies:** AC2, AC3, AC4, AC5, AC6
- `js_ts.py`: `.js/.jsx/.ts/.tsx` → `node_modules/.bin/eslint --fix` then `node_modules/.bin/prettier --write`; unfixable ESLint errors → capped diagnostics + exit 2; either binary missing → note naming the meta-install skill + exit 0.
- `data.py`: `.json/.jsonc/.yaml/.yml` → `prettier --write`; parse errors → diagnostics + exit 2.
- `markdown.py`: `.md/.markdown` → `markdownlint-cli2 --fix`; remaining rule violations → diagnostics + exit 2.
- `python.py`: `.py/.pyi` → `uv run --no-sync ruff format` then `uv run --no-sync ruff check --fix`; remaining violations → diagnostics + exit 2.
- Every hook: PEP 723 `uv run --script` header with no dependencies, imports `_common`, exits 0 fast on non-matching extension, missing file, vendored path, or any infrastructure failure.
- Write `tests/harness-layer/hooks/test_js_ts.py`, `test_data.py`, `test_markdown.py`, `test_python.py`: fixable input gets formatted in place (exit 0), unfixable input yields exit 2 with the offending rule in stderr, wrong extension/malformed stdin/missing tool paths exit 0 untouched.

### 4. Build the worktree lifecycle hooks

- **Task ID:** build-worktree-hooks
- **Depends On:** build-common-helper
- **Assigned To:** builder-hooks
- **Agent Type:** `general-purpose`
- **Parallel:** true (alongside build-format-hooks)
- **Satisfies:** AC7, AC8
- `worktree_create.py`: read `name` from stdin JSON; `git worktree add` at `<root>/.claude/worktrees/<name>` on branch `worktree-<name>` based on the origin default branch (fallback local `HEAD`; reuse the branch if it exists); run `bun install` then `uv sync` inside the worktree; print ONLY the absolute worktree path on stdout — all git/install output captured or sent to stderr; install failure logs and still prints the path.
- `worktree_remove.py`: read `worktree_path` from stdin JSON; exit 0 if the path is gone; `git worktree remove --force`; delete the checked-out branch only when it matches `worktree-*`; all failures → note + exit 0.
- Verify the stdin field names against a live payload (create a scratch worktree with the hook registered in `settings.local.json`, or capture via `claude --debug`) before finalizing — the names come from a reference implementation, not official docs.
- Write `tests/harness-layer/hooks/test_worktree_create.py` + `test_worktree_remove.py` using temp git repos: create → path printed alone on stdout, worktree + branch exist; remove → worktree gone, `worktree-*` branch deleted, foreign branch preserved; missing path → exit 0.

### 5. Register the hooks

- **Task ID:** register-hooks
- **Depends On:** build-format-hooks, build-worktree-hooks
- **Assigned To:** builder-toolchain
- **Agent Type:** `general-purpose`
- **Parallel:** false
- **Satisfies:** AC9
- In tracked `.claude/settings.json`: add four `PostToolUse` entries (matcher `Write|Edit|MultiEdit`) for `js_ts.py`, `data.py`, `markdown.py`, `python.py`, plus `WorktreeCreate` → `worktree_create.py` and `WorktreeRemove` → `worktree_remove.py`, all as `uv run --script "$CLAUDE_PROJECT_DIR"/.claude/hooks/auto-format/<file>.py`.
- Preserve the existing `PreToolUse` attribution entry and `attribution`/`enabledPlugins` blocks byte-for-byte.

### 6. Replace /meta-install with the skill

- **Task ID:** replace-meta-install
- **Depends On:** none
- **Assigned To:** builder-toolchain
- **Agent Type:** `general-purpose`
- **Parallel:** true (alongside build-format-hooks)
- **Satisfies:** AC10
- Delete `.claude/commands/meta-install.md`.
- Author `.claude/skills/meta-install/SKILL.md`: name `meta-install`; description keeps the old trigger phrasings ("install dev tools", "set up linters", "meta install") plus fresh-clone framing; body instructs `bun install` + `uv sync` from the committed lockfiles, idempotent, and notes that worktrees are handled automatically by the WorktreeCreate hook. Keep it KISS per AGENTS.md ("say it once, briefly, then stop").

### 7. Update the memory files

- **Task ID:** update-memory
- **Depends On:** register-hooks, replace-meta-install
- **Assigned To:** builder-toolchain
- **Agent Type:** `general-purpose`
- **Parallel:** false
- **Satisfies:** AC12
- `HARNESS-LAYER.md`: rewrite the Hooks section — attribution guard (unchanged) + the auto-format layer (four format hooks, exit-2 contract, worktree lifecycle install) — and refresh the Files tree.
- `AGENTS.md`: update the Harness Development hook line to name Prettier / ESLint / Ruff / markdownlint, worktree auto-install, and the `meta-install` skill; remove the stale `/meta-install` command reference. Imperative style, no rationale.

### 8. Validate Everything

- **Task ID:** validate-all
- **Depends On:** add-eslint-toolchain, build-common-helper, build-format-hooks, build-worktree-hooks, register-hooks, replace-meta-install, update-memory
- **Assigned To:** validator
- **Agent Type:** `general-purpose`
- **Parallel:** false
- Run every command in acceptance-criteria.md → `## Validation Commands`.
- Verify each acceptance criterion is met.
