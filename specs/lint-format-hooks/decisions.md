# Decisions: lint-format-hooks

> The grilling record for [spec.md](./spec.md) — why the plan is the way it is. Lifecycle tracking and
> the Codex review record live in spec.md, NOT here; this file is the immutable decision history.

## Summary

The team wants Claude-edited code auto-formatted at the harness layer: Prettier (bun) for
JS/TS, Ruff (uv) for Python, markdownlint (bun) for Markdown, each installed as a project
dev dependency. After grilling, the design is a single **PostToolUse** dispatcher
(`lint.py`) that routes by file extension and auto-fixes in place, never blocking; a
separate installer (`install_deps.py`) that a `WorktreeCreate` hook and a `/meta-install`
command both reuse to `bun install` + `uv sync`; and scaffolded manifests/config so the
linters are declared and pinned. Both scripts are stdlib-only Python run via
`uv run --script`. The owner overrode the Bash recommendation in favor of Python for
readability, accepting the per-edit cold-start.

## Resolved Decisions

- **Q:** Where does the hook live and apply — project, user, or plugin?
  - **A:** Project-level — register in this repo's tracked `.claude/settings.local.json`,
    scripts under `.claude/hooks/`.
  - **Why:** Version-controlled, Codex-reviewed, travels via plan→build→ship; matches the
    existing `PreToolUse` hook. Rules out user-level/plugin distribution.

- **Q:** When should the formatter run?
  - **A:** `PostToolUse` on `Write|Edit|MultiEdit`, one dispatcher that formats the edited file.
  - **Why:** Immediate, targeted format-on-save; a Stop-based batch would leave files
    unformatted mid-turn and need git to enumerate changes.

- **Q:** Format/fix in place, check-only, or block on lint errors?
  - **A:** Auto-fix in place; **never block**; surface leftover unfixable issues as a
    non-blocking note.
  - **Why:** No stalls or retry loops; the edit loop is never denied.

- **Q:** How do the linters get installed, given they must live in the repo?
  - **A:** A `WorktreeCreate` hook auto-installs into new worktrees, and a `/meta-install`
    command installs on first contributor checkout — both via `install_deps.py`. The linter
    itself does NOT self-heal; it warns-and-skips when a tool is absent.
  - **Why:** Keeps manifest mutation off the per-edit hot path; worktrees start empty
    (`node_modules`/`.venv` gitignored) so they need an explicit install trigger.

- **Q:** What does the install step run?
  - **A:** Sync from lockfile (`bun install`, `uv sync`); warn (do not mutate) if a tool is
    undeclared.
  - **Why:** Reproducible, pinned; the linters are declared once in this repo's manifests.

- **Q:** How aggressively should markdownlint touch hand-tuned harness Markdown?
  - **A:** Repo-wide with a lenient config: `default:true`, disable MD013 (line length),
    MD033 (inline HTML), MD041 (first-line H1); MD024 `siblings_only`.
  - **Why:** Consistent Markdown without churning carefully-written skill/agent/command prose.

- **Q:** Single dispatcher script, one script per language, or a combined script?
  - **A:** One dispatcher (`lint.py`) that routes by extension, plus a separate installer.
  - **Why:** The classic settings hook `matcher` keys on tool name, not extension — three
    registered scripts would all fire on every edit and triple the Python cold-start. The
    installer is a different event/job and is reused by `/meta-install`, so it stays separate.

- **Q:** What language for the hook scripts?
  - **A:** Python, run via `uv run --script` (PEP 723, stdlib-only).
  - **Why:** Owner's choice for readability/maintainability and uv-native tooling, accepting
    the ~100–300 ms per-edit interpreter cold-start over Bash's near-instant exec.

- **Q:** Linter rule sets?
  - **A:** Prettier `printWidth 100, singleQuote:false (double quotes), semi, trailingComma:all,
tabWidth 2`; Ruff `line-length 100, target py312, select E/F/I/UP/B/SIM` + `ruff format`;
    markdownlint lenient (above).
  - **Why:** Common-practice TS overrides with double quotes per owner; a balanced,
    mostly-auto-fixable Ruff set; lenient Markdown to protect harness prose.

## Assumptions

- **This plan scaffolds the dev tooling** (`package.json`, `pyproject.toml`, lockfiles,
  config files) because the repo has none today. Invalidated if the owner intends to add
  these separately — then Phase 1 collapses to config-only.
- **`WorktreeCreate` fires for the harness's internal `EnterWorktree`** and its stdin payload
  carries the new worktree path. Unverified; the build must confirm the event and field name.
  Invalidated if the event does not fire — then `/meta-install` + warn-and-skip are the only
  install paths (still functional, just not automatic on worktree creation).
- **`uv` and `bun` are on PATH** in the hook execution environment. Invalidated if not — the
  scripts warn-and-skip.
- **Prettier extension set** = `.ts/.tsx/.js/.jsx/.json/.css`; **Ruff** = `.py/.pyi`;
  **markdownlint** = `.md/.markdown`. Adjust the routing table if the owner wants more
  (e.g. `.scss`, `.yaml`).
- **`target-version = "py312"`** for Ruff. Adjust if the project targets another Python.

## Open Questions / Out of Scope

- **Out of scope:** user-level / plugin distribution; CI, pre-commit, and editor integration.
- **Out of scope:** monorepo / nested-package resolution — formatters run from the repo root.
- **Out of scope:** Prettier formatting of Markdown (markdownlint owns `.md`).
- **Out of scope:** lazy self-heal install inside the linter hook.
- **Open question:** does internal `EnterWorktree` emit `WorktreeCreate`, and with which
  path field? Owner: build/validation step to determine empirically.

## KB References

Docs the design stands on (path — fetched date):

- `ai-docs/anthropic/hooks.md` — 2026-07-05 — PostToolUse & WorktreeCreate events, matcher
  syntax, command-hook stdin/exit-code semantics, `WorktreeCreate` being async (cannot block).
- `ai-docs/anthropic/agent-sdk/slash-commands.md` — 2026-07-05 — custom Markdown commands in
  `.claude/commands/` with frontmatter (`description`, `allowed-tools`), `!`-bash execution;
  notes `.claude/commands/` is legacy vs `.claude/skills/` (repo convention keeps commands/).
- `ai-docs/astral/uv-scripts.md` — 2026-07-05 — `uv run --script`, PEP 723 inline metadata
  (`# /// script … # ///`, empty `dependencies` required), `--no-project`, project deps
  ignored under inline metadata.

All three were fetched 2026-07-05 (one day old at planning time) — within the 30-day
freshness window; no stale warning and no gap-fill needed.
