---
description: Install this repo's dev linters (Prettier, markdownlint-cli2, Ruff) on first checkout. Runs the shared installer, which does bun install + uv sync from the committed lockfiles so format-on-save works. Trigger phrasings include "install dev tools", "set up linters", "meta install".
allowed-tools: Bash
---

# Meta Install

Set up the project's dev linters by running the shared installer:

```bash
uv run --script "$CLAUDE_PROJECT_DIR"/.claude/hooks/install_deps.py
```

It runs `bun install` + `uv sync` from the committed lockfiles and is safe to
re-run, warning (without mutating any manifest) if a declared tool is still
unresolvable.
