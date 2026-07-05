# Tasks: lint-format-hooks

> Execution plan for [spec.md](./spec.md). Owner and scope are defined there; this file is how & who.

## Implementation Phases

### Phase 1: Foundation

Scaffold the dev-tool manifests and config so the linters are declared, pinned, and
runnable: `package.json` (prettier, markdownlint-cli2), `pyproject.toml` (ruff + config),
`.prettierrc.json`, `.prettierignore`, `.markdownlint.jsonc`, and generated `bun.lock` /
`uv.lock`. Everything downstream depends on these existing.

### Phase 2: Core Implementation

Write the two Python scripts — `install_deps.py` (installer) and `lint.py` (per-edit
dispatcher) — and the `/meta-install` command that reuses the installer.

### Phase 3: Integration & Polish

Register the `PostToolUse` and `WorktreeCreate` hooks in `.claude/settings.local.json`
(preserving the existing `PreToolUse` hook), then validate every acceptance criterion
end to end.

## Team Orchestration

- You operate as the team lead and orchestrate the team to execute the plan.
- IMPORTANT: You NEVER operate directly on the codebase. You use the `Task*` tools to deploy team
  members to build, validate, test, and deploy. Your job is to direct, not to build.
- Keep the shared task list (TaskCreate/TaskUpdate) as the single source of truth for who is doing
  what; verify each task on the board before marking it complete.
- Note the session id / name of each team member — that is how you reference them.

## Team Members

- **Builder**
  - **Name:** linter-hook-builder
  - **Role:** Scaffold the manifests/config, write both Python scripts, add the
    `/meta-install` command, and wire the hooks into `settings.local.json`.
  - **Agent Type:** general-purpose
  - **Resume:** true

- **Validator**
  - **Name:** linter-hook-validator
  - **Role:** Run every command in acceptance-criteria.md and confirm each criterion,
    including the sample-stdin dispatcher tests and idempotency checks.
  - **Agent Type:** general-purpose
  - **Resume:** true

## Step by Step Tasks

- Execute every step in order, top to bottom. Each task maps directly to one `TaskCreate` call.
- Before starting, run `TaskCreate` for every task below so all team members can see the board.
- Each task names the acceptance criteria (from acceptance-criteria.md) it satisfies, so work traces to "done".

### 1. Scaffold dev-tool manifests and linter configs

- **Task ID:** scaffold-configs
- **Depends On:** none
- **Assigned To:** linter-hook-builder
- **Agent Type:** general-purpose
- **Parallel:** false
- **Satisfies:** AC1
- `bun add -d prettier markdownlint-cli2` to create `package.json` + `bun.lock`.
- `uv init` (or a minimal `pyproject.toml` with a `[project]` table) then `uv add --dev ruff`
  to create/extend `pyproject.toml` + `uv.lock`.
- Add `[tool.ruff]` (`line-length = 100`, `target-version = "py312"`) and
  `[tool.ruff.lint]` (`select = ["E","F","I","UP","B","SIM"]`) to `pyproject.toml`.
- Write `.prettierrc.json`: `printWidth 100, singleQuote false, semi true,
trailingComma "all", tabWidth 2`.
- Write `.prettierignore`: `*.md`, `node_modules`, `dist`, `.venv`.
- Write `.markdownlint.jsonc`: `{ "default": true, "MD013": false, "MD033": false,
"MD041": false, "MD024": { "siblings_only": true } }`.

### 2. Write the installer script

- **Task ID:** write-installer
- **Depends On:** scaffold-configs
- **Assigned To:** linter-hook-builder
- **Agent Type:** general-purpose
- **Parallel:** true
- **Satisfies:** AC2
- Create `.claude/hooks/install_deps.py` with a PEP 723 header
  (`requires-python`, `dependencies = []`), stdlib-only.
- On run: `bun install` then `uv sync` in the target directory (the new worktree path from
  the `WorktreeCreate` stdin payload if present, else cwd / `$CLAUDE_PROJECT_DIR`).
- After install, verify `prettier`, `markdownlint-cli2`, and `ruff` resolve; **warn** (do
  not mutate manifests) if any declared tool is missing. Never crash the caller.
- Make it importable/callable so `/meta-install` reuses the same logic.

### 3. Write the linter dispatcher

- **Task ID:** write-dispatcher
- **Depends On:** scaffold-configs
- **Assigned To:** linter-hook-builder
- **Agent Type:** general-purpose
- **Parallel:** true
- **Satisfies:** AC3
- Create `.claude/hooks/lint.py` with a PEP 723 header, stdlib-only.
- Read stdin JSON; extract `tool_input.file_path`; on malformed/empty input, exit 0.
- Guard: skip paths under `node_modules/`, `.venv/`, `dist/`.
- Route by extension: `.ts/.tsx/.js/.jsx/.json/.css` → `bun x prettier --write`;
  `.py/.pyi` → `uv run --no-sync ruff format` then `uv run --no-sync ruff check --fix`;
  `.md/.markdown` → `bun x markdownlint-cli2 --fix`. Unknown ext → no-op.
- Detect a missing tool WITHOUT installing (`uv run --no-sync …`; direct
  `node_modules/.bin/<tool>` for JS); on absence print a one-line stderr note and exit 0.
- Never `exit 2`; surface unfixable lint as a non-blocking stderr note; always exit 0.

### 4. Add the /meta-install command

- **Task ID:** add-meta-install
- **Depends On:** write-installer
- **Assigned To:** linter-hook-builder
- **Agent Type:** general-purpose
- **Parallel:** false
- **Satisfies:** AC5
- Create `.claude/commands/meta-install.md` with YAML frontmatter (`description`,
  optional `allowed-tools: Bash`).
- Body instructs running the installer (`uv run --script "$CLAUDE_PROJECT_DIR"/.claude/hooks/install_deps.py`,
  or `bun install` + `uv sync`) so a new contributor installs all dev libraries on first checkout.

### 5. Register the hooks

- **Task ID:** register-hooks
- **Depends On:** write-installer, write-dispatcher
- **Assigned To:** linter-hook-builder
- **Agent Type:** general-purpose
- **Parallel:** false
- **Satisfies:** AC4
- Edit `.claude/settings.local.json`, preserving the existing `PreToolUse` Bash hook and
  `enabledPlugins`.
- Add `PostToolUse`: matcher `Write|Edit|MultiEdit` →
  `uv run --script "$CLAUDE_PROJECT_DIR"/.claude/hooks/lint.py`.
- Add `WorktreeCreate` →
  `uv run --script "$CLAUDE_PROJECT_DIR"/.claude/hooks/install_deps.py`.
- Confirm the file is valid JSON.

### 6. Validate Everything

- **Task ID:** validate-all
- **Depends On:** scaffold-configs, write-installer, write-dispatcher, add-meta-install, register-hooks
- **Assigned To:** linter-hook-validator
- **Agent Type:** general-purpose
- **Parallel:** false
- **Satisfies:** AC1, AC2, AC3, AC4, AC5, AC6
- Run every command in acceptance-criteria.md → `## Validation Commands`.
- Verify each acceptance criterion is met, including the per-extension stdin dispatcher
  tests, the warn-and-skip path, and install idempotency.
- Verify whether `WorktreeCreate` fires for an internal `EnterWorktree`; record the finding.
