# Harness Layer

How this repo keeps code tidy automatically, using Claude Code hooks. Three hooks are
registered in `.claude/settings.local.json`.

## Format on save (PostToolUse)

Every time Claude writes or edits a file, `.claude/hooks/lint.py` formats it in place,
routed by file extension:

- `.ts .tsx .js .jsx .json .css` → Prettier (via bun)
- `.py .pyi` → `ruff format` + `ruff check --fix` (via uv)
- `.md .markdown` → markdownlint (via bun)

It never blocks the turn: it always exits 0, and if a formatter is not installed it
prints a one-line note and skips. Files under `node_modules/`, `.venv/`, and `dist/` are
left alone.

## Install the linters (SessionStart + /meta-install)

The linters are project dev-dependencies (`package.json` / `pyproject.toml`, pinned by
`bun.lock` / `uv.lock`), so a fresh checkout has to install them before they can run.

- A **SessionStart** hook runs `.claude/hooks/install_deps.py` (`bun install` + `uv sync`)
  when a session starts. It is idempotent — a fast no-op once the tools are present.
- Run **`/meta-install`** by hand on a first clone, or after entering a worktree
  mid-session (that path fires `CwdChanged`, which SessionStart does not cover).

Until the tools exist, the formatter just warns and skips — edits are never blocked.

## Block the Claude commit trailer (PreToolUse)

`.claude/hooks/block-coauthor-trailer.sh` rejects any `git` / `gh` command whose message
carries a `Co-Authored-By: Claude` trailer, per
[GIT-COMMIT-PR-MESSAGE.md](./GIT-COMMIT-PR-MESSAGE.md).

## Files

- `.claude/settings.local.json` — registers the three hooks
- `.claude/hooks/lint.py` — the format-on-save dispatcher
- `.claude/hooks/install_deps.py` — the installer (SessionStart + `/meta-install`)
- `.claude/commands/meta-install.md` — the `/meta-install` command
- `.prettierrc.json`, `.prettierignore`, `.markdownlint.jsonc`, and `[tool.ruff]` in
  `pyproject.toml` — the linter configs
