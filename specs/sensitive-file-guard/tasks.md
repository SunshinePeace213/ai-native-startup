# Tasks: Sensitive File Guard — block agent access to secret-bearing files

> Execution plan for [spec.md](./spec.md). Owner and scope are defined there; this file is how & who.

## Implementation Phases

### Phase 1: Foundation

The engine everything depends on: `.claude/hooks/sensitive-files/_common.py` —
catalog data (decisions.md D2 table), template allowlist, path normalization
(tilde/relative/realpath), slash-bounded fragment matching, the command-text
alternation regex, the denial-message builder with `.env`-template detection, and
the fail-open plumbing adapted from the sibling families. Unit-tested in-process.

### Phase 2: Core Implementation

The two thin guard scripts on top of the engine — `file_guard.py`
(`Read|Grep|Edit|Write|MultiEdit` payloads) and `bash_guard.py` (`Bash` payloads) —
each with its e2e test file driven through the shared `run_hook` launcher.
`_common.py` is frozen for these tasks: engine changes go back to builder-engine
via the lead, so the two guard tasks can run in parallel safely.

### Phase 3: Integration & Polish

Wiring and docs: register both guards in `.claude/settings.json` (join the existing
PreToolUse `Bash` block; add the new file-tools block), register `bash_guard.py` in
`.codex/hooks.json`, extend `test_wiring.py`'s `EXPECTED_BINDINGS`, document the
family in `HARNESS-LAYER.md`, then validate everything.

## Team Orchestration

- You operate as the team lead and orchestrate the team to execute the plan.
- IMPORTANT: You NEVER operate directly on the codebase. You use the `Task*` tools to deploy team
  members to build, validate, test, and deploy. Your job is to direct, not to build.
- Keep the shared task list (TaskCreate/TaskUpdate) as the single source of truth for who is doing
  what; verify each task on the board before marking it complete.
- Note the session id / name of each team member — that is how you reference them.

## Team Members

- **Builder**
  - **Name:** builder-engine
  - **Role:** The catalog engine (`_common.py`) and its unit tests; sole owner of
    `_common.py` for the whole build
  - **Agent Type:** general-purpose
  - **Resume:** true

- **Builder**
  - **Name:** builder-file-guard
  - **Role:** `file_guard.py` and its e2e tests
  - **Agent Type:** general-purpose
  - **Resume:** true

- **Builder**
  - **Name:** builder-bash-guard
  - **Role:** `bash_guard.py` and its e2e tests
  - **Agent Type:** general-purpose
  - **Resume:** true

- **Builder**
  - **Name:** builder-wiring
  - **Role:** settings/codex registration, wiring matrix, HARNESS-LAYER.md docs
  - **Agent Type:** general-purpose
  - **Resume:** true

- **Validator**
  - **Name:** validator
  - **Role:** Run every validation command and verify each acceptance criterion
  - **Agent Type:** general-purpose
  - **Resume:** false

## Step by Step Tasks

- Execute every step in order, top to bottom. Each task maps directly to one `TaskCreate` call.
- Before starting, run `TaskCreate` for every task below so all team members can see the board.
- Each task names the acceptance criteria (from acceptance-criteria.md) it satisfies, so work traces to "done".

### 1. Build the catalog engine

- **Task ID:** catalog-engine
- **Depends On:** none
- **Assigned To:** builder-engine
- **Agent Type:** general-purpose
- **Model / Effort:** `opus` / `high`
- **Parallel:** false
- **Satisfies:** AC5, AC6 (engine halves of AC1–AC4)
- Create `.claude/hooks/sensitive-files/_common.py`: fail-open plumbing (`note`,
  `read_payload` with bounded stdin wait) adapted from
  `security-scan/_common.py` — copied, not imported.
- Encode the decisions.md D2 catalog as data: rules of
  `(category_id, label, guidance, kind, pattern)`; compile basename patterns
  (fnmatch → case-insensitive regex) and slash-bounded fragments at import.
- Implement the template allowlist (D3 set), path normalization
  (expanduser → absolutize → normpath, checked alongside `os.path.realpath`),
  `match_path()`, `match_command_text()` (token-boundary alternation regex,
  allowlist applied to the matched token's basename), and
  `denial_lines(path_or_token, rule)` including `.env`-template detection
  (scan target dir + project root for the first existing allowlist file).
- Write `tests/harness-layer/hooks/sensitive-files/test_engine.py` via
  `load_hook_module`: at least one blocked sample per catalog category, allowlist
  passes, tilde/relative/symlink normalization (`tmp_path` symlinks), fragment
  boundary negative (`/.awsome/`), case-insensitivity, template-detection helper.
  Per HOOK-TESTING.md: parallel-safe, docstrings state WHY, no secret-shaped
  literals (filenames only).

### 2. Build the file guard

- **Task ID:** file-guard
- **Depends On:** catalog-engine
- **Assigned To:** builder-file-guard
- **Agent Type:** general-purpose
- **Model / Effort:** `sonnet` / `medium`
- **Parallel:** true (alongside bash-guard)
- **Satisfies:** AC1, AC2, AC3, AC5, AC6
- Create `.claude/hooks/sensitive-files/file_guard.py` (PEP 723 header, `import
  _common`): extract targets by tool — `file_path` for Read/Edit/Write/MultiEdit;
  `path` (path-matched) and `glob` (text-matched) for Grep — deny on match with
  the three-line message, exit 2; everything else exit 0; top-level fail-open
  wrapper.
- Write `test_file_guard.py` via `run_hook`: per-tool block cases, `.env` redirect
  message naming an existing template (and the no-template wording), allowlist and
  ordinary-file passes, Grep direct-target deny vs directory allow, symlink deny,
  malformed/empty/TTY stdin fail-open, unknown tool fail-open.
- Do NOT edit `_common.py`; route engine gaps through the lead to builder-engine.

### 3. Build the bash guard

- **Task ID:** bash-guard
- **Depends On:** catalog-engine
- **Assigned To:** builder-bash-guard
- **Agent Type:** general-purpose
- **Model / Effort:** `sonnet` / `high`
- **Parallel:** true (alongside file-guard)
- **Satisfies:** AC4, AC5, AC6
- Create `.claude/hooks/sensitive-files/bash_guard.py` (PEP 723 header, `import
  _common`): only `tool_name == "Bash"` payloads with a non-empty string command
  are examined; `match_command_text()` decides; deny prints the three-line message
  with the matched token, exit 2; fail-open wrapper.
- Write `test_bash_guard.py` via `run_hook` with the spec's Edge Cases corpus:
  denies `cat .env`, `cp .env /tmp/x`, `source .env`, `grep KEY .env`,
  `python -c "open('.env')"`, `cat $HOME/.ssh/id_rsa`, `base64 .env`, and the
  shell-operator cases `cat .env|base64`, `cat .env&&echo done`,
  `cat .env>copy`, plus a multiline command with `cat .env` on its own line;
  passes `cat .env.example`, `ls -la`, `git status`, `/.awsome/` negative;
  malformed/empty stdin fail-open.
- Do NOT edit `_common.py`; route engine gaps through the lead to builder-engine.

### 4. Wire registrations and document the family

- **Task ID:** wiring-docs
- **Depends On:** file-guard, bash-guard
- **Assigned To:** builder-wiring
- **Agent Type:** general-purpose
- **Model / Effort:** `sonnet` / `medium`
- **Parallel:** false
- **Satisfies:** AC7, AC8
- `.claude/settings.json`: add `bash_guard.py` to the existing PreToolUse `Bash`
  matcher block's `hooks` array (never a duplicate matcher block); add one new
  PreToolUse block `matcher: "Read|Grep|Edit|Write|MultiEdit"` running
  `file_guard.py`. Same `uv run --script "$CLAUDE_PROJECT_DIR"/...` command form.
- `.codex/hooks.json`: add `bash_guard.py` to the PreToolUse `Bash` block using the
  `$(git rev-parse --show-toplevel)` command form and a `statusMessage`, mirroring
  the attribution entry.
- Extend `test_wiring.py` `EXPECTED_BINDINGS` with both new registrations,
  following the matrix's existing shape (including how it covers the Codex
  registrar for `block_attribution.py`).
- `HARNESS-LAYER.md`: add a "Sensitive File Guard (PreToolUse)" section (scope,
  catalog summary, allowlist, deny/fail-open contract, Codex parity) and add the
  new files to the Files tree. Keep it in the file's existing terse style.

### 5. Validate Everything

- **Task ID:** validate-all
- **Depends On:** catalog-engine, file-guard, bash-guard, wiring-docs
- **Assigned To:** validator
- **Agent Type:** general-purpose
- **Model / Effort:** `sonnet` / `low`
- **Parallel:** false
- Run every command in acceptance-criteria.md → `## Validation Commands`.
- Verify each acceptance criterion is met.
- Report any failure back to the lead with the failing command output; do not
  mark the board complete on a red run.
