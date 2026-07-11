# Acceptance Criteria: auto-format-hooks

> The definition of "done" for [spec.md](./spec.md). Every criterion is observable and testable, and
> every task in tasks.md should map to at least one criterion here.

## Acceptance Criteria

- **AC1** — ESLint toolchain present: `package.json` lists `eslint`, `@eslint/js`, `typescript-eslint`, `eslint-config-prettier`, `eslint-plugin-react`, `eslint-plugin-react-hooks` as devDependencies; `bun.lock` is updated; `eslint.config.mjs` exists at the repo root and `node_modules/.bin/eslint` lints a `.tsx` fixture without config errors.
- **AC2** — JS/TS hook works end-to-end: feeding `js_ts.py` a PostToolUse payload for a `.ts` file with an auto-fixable violation rewrites the file (ESLint fix + Prettier style) and exits 0; a payload for a file with an unfixable ESLint error exits 2 with `file:line rule message` diagnostics on stderr.
- **AC3** — Data hook works: `.json` and `.yaml` payloads get Prettier-formatted in place with exit 0; a syntactically invalid JSON file exits 2 with the parse error on stderr.
- **AC4** — Markdown hook works: a `.md` payload with a fixable violation is fixed in place with exit 0; an unfixable markdownlint violation exits 2 with the rule id on stderr.
- **AC5** — Python hook works: a `.py` payload gets `ruff format` + `ruff check --fix` applied with exit 0; an unfixable ruff violation exits 2 with the rule code on stderr.
- **AC6** — Fail-open plumbing: every format hook exits 0 and leaves the file untouched for: non-matching extension, empty/malformed/TTY stdin, missing file, path under `node_modules`/`.venv`/`dist` (relative to the project root), and missing formatter binary — the last with a one-line stderr note naming the `meta-install` skill. Diagnostics on exit-2 paths are capped at 10 lines plus an "and N more" tail.
- **AC7** — WorktreeCreate contract: given `{"name": "<x>"}` on stdin in a git repo, `worktree_create.py` creates `.claude/worktrees/<x>` on branch `worktree-<x>`, runs `bun install` + `uv sync` inside it, and its stdout is exactly the absolute worktree path (one line, nothing else) — including when the install step fails.
- **AC8** — WorktreeRemove contract: given `{"worktree_path": "<p>"}`, `worktree_remove.py` removes the worktree and deletes its branch only when the branch matches `worktree-*`; a non-existent path and git failures exit 0.
- **AC9** — Registration: tracked `.claude/settings.json` is valid JSON containing four `PostToolUse` entries (matcher `Write|Edit|MultiEdit`) for the format hooks plus `WorktreeCreate` and `WorktreeRemove` entries, all via `uv run --script`; the pre-existing `PreToolUse` attribution entry, `attribution`, and `enabledPlugins` blocks are unchanged.
- **AC10** — meta-install migration: `.claude/commands/meta-install.md` no longer exists; `.claude/skills/meta-install/SKILL.md` exists with `name` + `description` frontmatter and instructs `bun install` + `uv sync`.
- **AC11** — Test suite green: the full pytest run passes with zero failures and zero skips, covering AC2–AC8.
- **AC12** — Memory updated: `HARNESS-LAYER.md` documents the auto-format layer (all six hooks + exit-2 contract) and its Files tree matches the working tree; `AGENTS.md` references the `meta-install` skill and contains no `/meta-install` command reference; `git grep -l "install_deps"` over tracked files returns nothing.

## Validation Commands

Run these to prove the criteria above. Map each command to the criteria it verifies.

- `bun install && ls node_modules/.bin/eslint node_modules/.bin/prettier node_modules/.bin/markdownlint-cli2` — verifies AC1 (binaries resolve). Pass: all three paths print.
- `printf 'const x:number=1\nexport default x\n' > /tmp/ac1-fixture.tsx && node_modules/.bin/eslint --fix /tmp/ac1-fixture.tsx; rm -f /tmp/ac1-fixture.tsx` — verifies AC1 (config loads and lints a `.tsx` without config errors).
- `uv run pytest tests/harness-layer/hooks/ -q` — verifies AC2, AC3, AC4, AC5, AC6, AC7, AC8, AC11. Pass: all tests green, zero skips.
- `uv run python -c "import json; d=json.load(open('.claude/settings.json')); ks=d['hooks']; assert len(ks['PostToolUse'])>=1 and 'WorktreeCreate' in ks and 'WorktreeRemove' in ks; print('ok')"` — verifies AC9 (valid JSON, events registered). Pass: prints `ok`.
- `grep -c 'auto-format' .claude/settings.json` — verifies AC9 (six hook commands point into `.claude/hooks/auto-format/`). Pass: ≥ 6.
- `test ! -f .claude/commands/meta-install.md && test -f .claude/skills/meta-install/SKILL.md && echo ok` — verifies AC10. Pass: prints `ok`.
- `grep -q 'auto-format' HARNESS-LAYER.md && ! grep -q '/meta-install' AGENTS.md && ! git grep -q 'install_deps' -- ':!specs' && echo ok` — verifies AC12. Pass: prints `ok`.
