# Harness Layer

## Hooks

Claude Code hooks, registered in `.claude/settings.json` and run via `uv run --script`,
keep the repo tidy.

### Block Claude Attribution (PreToolUse)

`.claude/hooks/block_attribution.py` denies (exit 2) any Bash command that contains a
`git` / `gh` token and carries a default Claude attribution form in the command text — the
`Co-Authored-By: Claude` trailer, the `Claude-Session:` trailer, or the
`Generated with [Claude Code]` footer — per
[GIT-COMMIT-PR-MESSAGE.md](./GIT-COMMIT-PR-MESSAGE.md). Commands without a git/gh token
that merely mention those strings pass. The `attribution` block in `.claude/settings.json`
turns attribution off at the source; this hook is the enforcement backstop.
`.codex/hooks.json` registers the same guard for Codex sessions.

### Auto-Format (PostToolUse)

Four hooks under `.claude/hooks/auto-format/` fire on `Write|Edit|MultiEdit`, self-filter
by extension, and format the edited file in place:

- `js_ts.py` — `.js .jsx .ts .tsx`: `eslint --fix` (flat config `eslint.config.mjs`) then `prettier --write`
- `data.py` — `.json .jsonc .yaml .yml`: `prettier --write`
- `markdown.py` — `.md .markdown`: `markdownlint-cli2 --fix`
- `python.py` — `.py .pyi`: `ruff format` then `ruff check --fix`

Unfixable lint errors exit 2 with `file:line rule message` diagnostics (capped at 10 plus
"and N more") fed back to the agent — fix them. Everything else — non-matching extension,
missing file, vendored path (`node_modules`, `.venv`, `dist`), malformed stdin, missing
formatter binary — fails open with exit 0; a missing binary notes the `meta-install`
skill. Shared boilerplate lives in `_common.py`.

### Security Scan (PostToolUse / SessionStart / Stop)

Hooks under `.claude/hooks/security-scan/` scan agent-written content for secrets and
common vulnerability patterns (stdlib regex, no external scanner):

- `post_write_scan.py` — `Write|Edit|MultiEdit`: scans the saved file
- `session_baseline.py` — SessionStart: records already-dirty files as a baseline so the
  user's own uncommitted work is never flagged
- `track_bash_writes.py` — PostToolUse + PostToolUseFailure on `Bash`: tracks files newly
  dirtied or committed by shell commands (baseline files excluded)
- `stop_sweep.py` — Stop/SubagentStop: re-scans every file tracked this session before the
  turn may end

Secret findings (API keys, tokens, private keys, credentials) exit 2 with `file:line rule
message` diagnostics — remove the secret. Vulnerability findings (unsafe `yaml.load`,
SQL string-building, `innerHTML =`, …) warn without blocking. Everything else fails open.
False positives: placeholder values (`example`, `changeme`, `<…>`) are auto-skipped; a
`security-scan: allow` comment on or immediately above the flagged line suppresses it.
Session state lives in `.claude/.security-scan/` (gitignored); the engine is
`security-scan/_common.py`.

### Worktree Lifecycle (WorktreeCreate / WorktreeRemove)

`worktree_create.py` replaces default worktree creation: `git worktree add` at
`.claude/worktrees/<name>` on branch `worktree-<name>`, then `bun install` + `uv sync`
inside it so the format hooks work there; stdout is the worktree path only.
`worktree_remove.py` removes the worktree and deletes its `worktree-*` branch. Fresh
clones use the `meta-install` skill instead: `bun install` + `uv sync` from the committed
lockfiles.

### Files

```text
.claude/
├── settings.json                  # registers all hooks + attribution off
├── hooks/
│   ├── block_attribution.py       # attribution guard (PreToolUse)
│   ├── check-spec-completeness.sh # spec gate used by /harness-layer:harness-plan
│   ├── auto-format/
│   │   ├── _common.py             # shared helpers (payload parse, run, diagnostics)
│   │   ├── js_ts.py               # .js .jsx .ts .tsx → eslint --fix + prettier
│   │   ├── data.py                # .json .jsonc .yaml .yml → prettier
│   │   ├── markdown.py            # .md .markdown → markdownlint-cli2 --fix
│   │   ├── python.py              # .py .pyi → ruff format + ruff check --fix
│   │   ├── worktree_create.py     # WorktreeCreate: create worktree + install deps
│   │   └── worktree_remove.py     # WorktreeRemove: remove worktree + branch
│   └── security-scan/
│       ├── _common.py             # scanner engine: rules, suppression, session state
│       ├── post_write_scan.py     # per-write gate (Write|Edit|MultiEdit)
│       ├── session_baseline.py    # SessionStart: dirty-file baseline + HEAD
│       ├── track_bash_writes.py   # Bash tracker (PostToolUse + PostToolUseFailure)
│       └── stop_sweep.py          # Stop/SubagentStop sweep over the tracked set
└── skills/
    └── meta-install/SKILL.md      # fresh-clone setup: bun install + uv sync
tests/harness-layer/hooks/         # pytest suite for all hooks
eslint.config.mjs                  # ESLint flat config (React-ready)
.prettierrc.json                   # Prettier config
.prettierignore
.markdownlint.jsonc                # markdownlint config
pyproject.toml                     # [tool.ruff] linter config
```
