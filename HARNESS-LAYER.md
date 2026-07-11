# Harness Layer

## Hooks

Only one Claude Code hooks, registered in `.claude/settings.json`, keep the repo tidy.

### Block Claude Attribution (PreToolUse)

`.claude/hooks/block_attribution.py` denies (exit 2) any Bash command that contains a
`git` / `gh` token and carries a default Claude attribution form in the command text — the
`Co-Authored-By: Claude` trailer, the `Claude-Session:` trailer, or the
`Generated with [Claude Code]` footer — per
[GIT-COMMIT-PR-MESSAGE.md](./GIT-COMMIT-PR-MESSAGE.md). Commands without a git/gh token
that merely mention those strings pass. The `attribution` block in `.claude/settings.json`
turns attribution off at the source; this hook is the enforcement backstop.
`.codex/hooks.json` registers the same guard for Codex sessions.

### Files

```text
.claude/
├── settings.json                # registers the hooks + attribution off
├── hooks/
│   └── block_attribution.py     # attribution guard (PreToolUse)
└── commands/
    └── meta-install.md          # the /meta-install command
tests/harness-layer/hooks/       # pytest suite for the hooks
.prettierrc.json                 # Prettier config
.prettierignore
.markdownlint.jsonc              # markdownlint config
pyproject.toml                   # [tool.ruff] linter config
```
