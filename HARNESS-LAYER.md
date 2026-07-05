# Harness Layer

## Hooks

Three Claude Code hooks, registered in `.claude/settings.local.json`, keep the repo tidy.

### Auto Lint (PostToolUse)

`.claude/hooks/lint.py` formats every file Claude writes or edits, routed by extension:

- `.ts .tsx .js .jsx .json .css` → Prettier (bun)
- `.py .pyi` → `ruff format` + `ruff check --fix` (uv)
- `.md .markdown` → markdownlint (bun)

It never blocks a turn: it always exits 0, warns and skips when a formatter is missing,
and leaves `node_modules/`, `.venv/`, and `dist/` alone.

### Install Deps (SessionStart + /meta-install)

The linters are dev-dependencies pinned by `bun.lock` / `uv.lock`. A SessionStart hook
runs `.claude/hooks/install_deps.py` (`bun install` + `uv sync`) — idempotent, a fast
no-op once the tools exist. Run `/meta-install` by hand on a first clone or after
entering a worktree mid-session (SessionStart doesn't fire there).

### Block Claude Commit Trailer (PreToolUse)

`.claude/hooks/block-coauthor-trailer.sh` rejects any `git` / `gh` command whose message
carries a `Co-Authored-By: Claude` trailer, per
[GIT-COMMIT-PR-MESSAGE.md](./GIT-COMMIT-PR-MESSAGE.md).

### Files

```text
.claude/
├── settings.local.json          # registers the hooks
├── hooks/
│   ├── lint.py                  # format-on-save dispatcher
│   ├── install_deps.py          # installer (SessionStart + /meta-install)
│   └── block-coauthor-trailer.sh  # commit-trailer guard
└── commands/
    └── meta-install.md          # the /meta-install command
.prettierrc.json                 # Prettier config
.prettierignore
.markdownlint.jsonc              # markdownlint config
pyproject.toml                   # [tool.ruff] linter config
```
