---
name: meta-install
description: Install this repo's dev toolchain (Prettier, ESLint, markdownlint-cli2, Ruff) on a fresh clone so format-on-save works. Trigger phrasings include "install dev tools", "set up linters", "meta install".
---

# Meta Install

Set up a fresh clone's formatter toolchain from the committed lockfiles:

```bash
bun install
uv sync
```

Both commands are idempotent — safe to re-run anytime. Worktrees need no manual
step: the WorktreeCreate hook installs dependencies in each new worktree
automatically.
