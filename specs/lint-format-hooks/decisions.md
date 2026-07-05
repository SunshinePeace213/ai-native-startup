# Decisions: lint-format-hooks

> The grilling record for [spec.md](./spec.md) — why the plan is the way it is. Lifecycle tracking and
> the Codex review record live in spec.md, NOT here; this file is the immutable decision history.

## Summary

The team wants Claude-edited code auto-formatted at the harness layer: Prettier (bun) for
JS/TS, Ruff (uv) for Python, markdownlint (bun) for Markdown, each installed as a project
dev dependency. After grilling, the design is a single **PostToolUse** dispatcher
(`lint.py`) that routes by file extension and auto-fixes in place, never blocking; a
separate installer (`install_deps.py`) that the `/meta-install` command runs
(`bun install` + `uv sync`); and scaffolded manifests/config so the
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
  - **A:** Two install paths: a **`SessionStart`** hook auto-installs (`bun install` +
    `uv sync`) on a fresh session or clone (idempotent — a fast no-op once deps exist,
    stderr-only), and the **`/meta-install`** command is the manual path for a first checkout
    and for mid-session worktree entry (which fires `CwdChanged`, not `SessionStart`, so the
    hook does not cover it). NO `WorktreeCreate` hook: per `ai-docs/anthropic/worktrees.md`
    a `WorktreeCreate` hook *replaces* git's default worktree creation (it must create the
    worktree and return its path), so it is unsafe as a setup hook. The linter itself does
    not self-heal; it warns-and-skips when a tool is absent.
  - **Why:** Keeps the install off the per-edit hot path and out of git-worktree creation;
    the `SessionStart` hook plus `/meta-install` and warn-and-skip make the flow reliable
    without a footgun. Worktrees start empty (`node_modules`/`.venv` gitignored) so they need
    an explicit install trigger.

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
- **`WorktreeCreate` as a post-create install trigger** — assumed at planning time, but
  **invalidated at build time**: per `ai-docs/anthropic/worktrees.md` a `WorktreeCreate` hook
  *replaces* git's worktree creation entirely, so it cannot serve as a passive installer.
  `/meta-install` + warn-and-skip are the install paths (still functional, just not automatic
  on worktree creation).
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
  Resolved at build time: a `WorktreeCreate` hook replaces git's worktree creation entirely
  (per `ai-docs/anthropic/worktrees.md`), so the auto-install approach was dropped.
- **Post-cross-check addition:** a `SessionStart` auto-install hook was added at the owner's
  request after the Codex cross-check; mid-session worktree entry stays on `/meta-install`
  because it fires `CwdChanged`, not `SessionStart`.

## KB References

Docs the design stands on (path — fetched date):

- `ai-docs/anthropic/hooks.md` — 2026-07-05 — PostToolUse event, matcher syntax, and
  command-hook stdin/exit-code semantics. (Note: `WorktreeCreate` is a synchronous
  creation-replacer per `worktrees.md`, not an async notification.)
- `ai-docs/anthropic/hooks-guide.md` — 2026-07-05 — the **classic `settings.json` hook shape**
  this repo actually uses (`"hooks": { "PostToolUse": [{ "matcher": "Edit|Write", "hooks": [...] }] }`)
  with snake_case `.tool_input.file_path`; includes a worked PostToolUse Prettier-formatter
  example matching this design. (`hooks.md` documents the newer `.claude/hooks.json`/camelCase
  schema; the plan follows the classic settings-file convention grounded here.)
- `ai-docs/anthropic/agent-sdk/slash-commands.md` — 2026-07-05 — custom Markdown commands in
  `.claude/commands/` with frontmatter (`description`, `allowed-tools`), `!`-bash execution;
  notes `.claude/commands/` is legacy vs `.claude/skills/` (repo convention keeps commands/).
- `ai-docs/astral/uv-scripts.md` — 2026-07-05 — `uv run --script`, PEP 723 inline metadata
  (`# /// script … # ///`, empty `dependencies` required), `--no-project`, project deps
  ignored under inline metadata.
- `ai-docs/anthropic/worktrees.md` — 2026-07-05 — registering a `WorktreeCreate` hook
  **replaces git's default worktree creation entirely** (the hook must create the worktree
  and print its path). This invalidated the planned `WorktreeCreate` auto-install, which is
  why install is owned by the `SessionStart` hook + `/meta-install` (with the linter
  warn-and-skipping until deps exist).

All five were fetched 2026-07-05 (one day old at planning time) — within the 30-day
freshness window; no stale warning and no gap-fill needed.
