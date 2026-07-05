---
description: Install this repo's dev linters (Prettier, markdownlint-cli2, Ruff) on first checkout. Runs the shared installer, which does bun install + uv sync from the committed lockfiles so format-on-save works. Trigger phrasings include "install dev tools", "set up linters", "meta install".
allowed-tools: Bash
---

# Meta Install

Install the project's dev linters so the format-on-save hook can run.

Run the shared installer:

```bash
uv run --script "$CLAUDE_PROJECT_DIR"/.claude/hooks/install_deps.py
```

It runs `bun install` + `uv sync` from the committed lockfiles, then warns (without
mutating any manifest) if a declared tool is still unresolvable. Safe to run twice.
