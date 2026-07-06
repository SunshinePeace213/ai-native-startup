# Tasks: Attribution guard — Python hook + attribution settings

> Execution plan for [spec.md](./spec.md). Owner and scope are defined there; this file is how & who.

## Implementation Phases

### Phase 1: Foundation

The Python guard itself — `.claude/hooks/block_attribution.py` — everything else wires up to or
verifies this script.

### Phase 2: Core Implementation

Registration and cleanup: add the `attribution` block to `.claude/settings.local.json`, point the
PreToolUse hook at the new script, `git rm` the old shell hook. In parallel, the pytest suite and
its `pytest` dev dependency.

### Phase 3: Integration & Polish

HARNESS-LAYER.md documentation update, then full validation against acceptance-criteria.md.

## Team Orchestration

- You operate as the team lead and orchestrate the team to execute the plan.
- IMPORTANT: You NEVER operate directly on the codebase. You use the `Task*` tools to deploy team
  members to build, validate, test, and deploy. Your job is to direct, not to build.
- Keep the shared task list (TaskCreate/TaskUpdate) as the single source of truth for who is doing
  what; verify each task on the board before marking it complete.
- Note the session id / name of each team member — that is how you reference them.

## Team Members

- **Builder**
  - **Name:** builder-hook
  - **Role:** implements the Python guard, settings wiring, tests, and doc update
  - **Agent Type:** `general-purpose` (no `.claude/agents/team/` roster exists in this repo)
  - **Resume:** true

- **Builder**
  - **Name:** validator
  - **Role:** independently runs every validation command and checks each AC; touches no code
  - **Agent Type:** `general-purpose`
  - **Resume:** false

## Step by Step Tasks

- Execute every step in order, top to bottom. Each task maps directly to one `TaskCreate` call.
- Before starting, run `TaskCreate` for every task below so all team members can see the board.
- Each task names the acceptance criteria (from acceptance-criteria.md) it satisfies, so work traces to "done".

### 1. Write the Python guard

- **Task ID:** write-hook
- **Depends On:** none
- **Assigned To:** builder-hook
- **Agent Type:** `general-purpose`
- **Parallel:** false
- **Satisfies:** AC1, AC2, AC3, AC4, AC5
- Create `.claude/hooks/block_attribution.py` with the `#!/usr/bin/env -S uv run --script` shebang
  and a PEP 723 block (`requires-python = ">=3.12"`, `dependencies = []`).
- Read stdin JSON defensively (reuse `lint.py`'s `select`-with-timeout pattern); on any read/parse
  problem exit 0.
- Exit 0 unless `tool_name == "Bash"` and `tool_input.command` is a non-empty string.
- Exit 0 unless the command contains a word-boundary `git` or `gh` token (regex `\b(git|gh)\b`;
  must not match `github`).
- Scan the command (case-insensitive) for the three attribution patterns:
  `co-authored-by:\s*claude`, `claude-session:`, `generated with \[?claude code\]?`.
- On match: print a stderr message naming the matched form, the policy source
  (GIT-COMMIT-PR-MESSAGE.md), and the fix ("remove the attribution line and rerun"); exit 2.
  Otherwise exit 0.
- Wrap `main()` so unexpected exceptions note to stderr and exit 0 (fail-open), then
  `chmod +x` the file.

### 2. Wire settings and remove the shell hook

- **Task ID:** wire-settings
- **Depends On:** write-hook
- **Assigned To:** builder-hook
- **Agent Type:** `general-purpose`
- **Parallel:** false
- **Satisfies:** AC6
- In `.claude/settings.local.json`, add the top-level block
  `"attribution": {"commit": "", "pr": "", "sessionUrl": false}`.
- In the same file, change the `PreToolUse` → `Bash` hook command to
  `uv run --script "$CLAUDE_PROJECT_DIR"/.claude/hooks/block_attribution.py`.
- `git rm .claude/hooks/block-coauthor-trailer.sh` (never plain `rm`; git history keeps it
  recoverable).

### 3. Add the pytest suite

- **Task ID:** add-tests
- **Depends On:** write-hook
- **Assigned To:** builder-hook
- **Agent Type:** `general-purpose`
- **Parallel:** true (alongside wire-settings)
- **Satisfies:** AC7
- Add `pytest>=8` to `[dependency-groups] dev` in `pyproject.toml` (alongside `ruff`), then
  `uv sync`.
- Create `.claude/hooks/tests/test_block_attribution.py`: each test runs the script via
  `subprocess.run`, feeds a JSON payload on stdin, and asserts exit code (and stderr content for
  blocks). Cover at minimum:
  - block: `git commit -m` message with `Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>`
  - block: heredoc commit message with `Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>`
  - block: lowercase `co-authored-by: claude` variant
  - block: `git commit --amend` carrying a `Claude-Session:` trailer
  - block: `gh pr create --body` containing `🤖 Generated with [Claude Code](https://claude.com/claude-code)`
  - allow: clean `git commit -m "🔧 chore(hooks): x"` with no attribution
  - allow: `Co-Authored-By: Alice <alice@example.com>` (non-Claude co-author)
  - allow: non-git command writing the trailer text to a doc (heredoc without git/gh)
  - allow: non-Bash payload (`tool_name: "Write"`)
  - allow: empty stdin and malformed JSON
- Tests must encode intent in their names/docstrings (why the behavior matters, per the repo's
  testing rule), not just assert numbers.

### 4. Update HARNESS-LAYER.md

- **Task ID:** update-docs
- **Depends On:** wire-settings
- **Assigned To:** builder-hook
- **Agent Type:** `general-purpose`
- **Parallel:** false
- **Satisfies:** AC8
- Replace the "Block Claude Commit Trailer (PreToolUse)" section: new name (e.g. "Block Claude
  Attribution (PreToolUse)"), the Python script path, the three blocked forms, and a sentence on
  the `attribution` settings block as the prevention layer.
- Update the Files tree: `block_attribution.py` (+ `tests/`) replaces `block-coauthor-trailer.sh`.
- Note: HARNESS-LAYER.md may carry uncommitted local edits in the main checkout; reconcile against
  the branch copy, don't blindly overwrite.

### 5. Validate Everything

- **Task ID:** validate-all
- **Depends On:** write-hook, wire-settings, add-tests, update-docs
- **Assigned To:** validator
- **Agent Type:** `general-purpose`
- **Parallel:** false
- Run every command in acceptance-criteria.md → `## Validation Commands`.
- Verify each acceptance criterion is met.
- Report any failure loudly — no silent skips; a skipped check is a failed validation.
