# Spec: lint-format-hooks

- **Owner:** @ringo
- **Status:** Approved

## Task Description

Add a project-level auto-format/lint system to this harness repo, driven by Claude Code
hooks, so that code Claude edits during coding tasks is formatted the moment it is
written — Prettier for JS/TS via **bun**, Ruff for Python via **uv**, and markdownlint
for Markdown via **bun**. The linters run as **project dev dependencies** (declared in
this repo's `package.json` / `pyproject.toml`, pinned by `bun.lock` / `uv.lock`), so a
fresh checkout or a fresh git worktree must install them before they can run. That
install is owned by the `/meta-install` command (`bun install` + `uv sync`), which a new
contributor runs on first checkout and which is also how a fresh worktree gets populated;
until it has run, the linter warns-and-skips. (A `WorktreeCreate` auto-install hook was
rejected: per `ai-docs/anthropic/worktrees.md`, registering one replaces git's default
worktree creation entirely, so it cannot be used just to install deps.) The dispatcher and
installer are **Python** scripts run via `uv run --script`.

Scope note: this repo has no TS/Python source of its own today (it is a harness repo of
Markdown + shell). This plan therefore also **scaffolds** the dev-tool manifests and
config files so the linters are declared and runnable; coding work done in this repo (or
its worktrees) is what the linter hook then formats.

## Objective

Editing a `.ts`/`.tsx`/`.js`/`.jsx`/`.json`/`.css`, `.py`/`.pyi`, or `.md`/`.markdown`
file in a session rooted at this repo auto-formats that file in place (never blocking the
turn), using the project-declared linters; a contributor (or a fresh worktree) gets those
linters by running `/meta-install`, and the linter warns-and-skips until they exist.

## Non-Goals

- **No lazy self-heal install inside the linter hook.** The linter warns-and-skips when a
  tool is missing; installation is owned by the `/meta-install` command.
- **No blocking / gating.** The linter never denies an edit (never `exit 2`); leftover,
  non-auto-fixable lint issues are surfaced as a non-blocking note only.
- **No user-level or plugin distribution.** Scope is this repo's `.claude/` only.
- **No monorepo / nested-package resolution.** Formatters run from the repo root against
  the edited file; multi-package layouts are out of scope.
- **No CI wiring, pre-commit hooks, or editor integration.** Claude Code hooks only.
- **No Prettier for Markdown.** markdownlint owns `.md`; Prettier's ignore excludes it.

## Problem Statement

The team runs coding tasks (`/plan-w-team → /build → /ship`) that edit application code,
but nothing enforces formatting as that code is written, and the heavy use of git
worktrees means a fresh worktree starts with no installed dev tools (`node_modules` and
`.venv` are gitignored). Without automation, formatting drifts and worktrees silently have
no linters available. The opportunity: make formatting automatic and deterministic at the
harness layer, with a one-command install path for both worktrees and new contributors.

## Solution Approach

A single **PostToolUse** hook on `Write|Edit|MultiEdit` runs one dispatcher,
`.claude/hooks/lint.py`, which reads the hook's stdin JSON, extracts
`tool_input.file_path`, routes by extension to Prettier / Ruff / markdownlint, auto-fixes
in place, and always exits 0. One dispatcher (not one script per language) is required
because the classic settings hook `matcher` keys on **tool name**, not file extension —
three separately-registered scripts would all spawn on every edit and triple the Python
cold-start. Installation is a separate concern in `.claude/hooks/install_deps.py`
(`bun install` + `uv sync`), invoked by the `/meta-install` command so the install logic
lives in one place. Both scripts are stdlib-only Python invoked with `uv run --script`
(PEP 723 inline metadata), honoring the repo's "always uv" rule while keeping cold-start
minimal.

Main alternative considered and rejected: **lazy self-heal** (install-on-demand inside the
linter). It is the most robust for correctness, but the owner chose an explicit install
trigger (the `/meta-install` command) to keep manifest mutation out of the per-edit hot
path; the linter's warn-and-skip plus `/meta-install` cover the gap. A `WorktreeCreate`
auto-install hook was also rejected — per `ai-docs/anthropic/worktrees.md`, registering
one replaces git's default worktree creation entirely, so it cannot serve as a mere
install step.

## Requirements & Decisions

- **Project-scoped, single dispatcher, never-blocking auto-fix.** Register in the repo's
  tracked `.claude/settings.local.json` (matching the existing `PreToolUse` Bash hook);
  `lint.py` routes by extension, auto-fixes, and always exits 0.
- **Python via `uv run --script`, stdlib-only.** Matches the owner's language choice and
  the "always uv" rule; PEP 723 header with empty `dependencies` so nothing resolves.
- **Install owned by `/meta-install`, sync-from-lockfile.**
  `install_deps.py` runs `bun install` + `uv sync`; if a linter is not declared in a
  manifest it **warns** rather than mutating. Linter warns-and-skips if a tool is absent.
- **Linter configs:** Prettier `printWidth 100, singleQuote:false, semi, trailingComma:all,
tabWidth 2`; Ruff `line-length 100, target py312, select E/F/I/UP/B/SIM` + `ruff format`;
  markdownlint lenient (`default:true`, disable MD013/MD033/MD041, MD024 siblings_only).

## Tracking

- **Issue:** none — deferred
- **Branch:** chore/lint-format-hooks
- **Worktree:** /home/ringo/ai-native-startup/.claude/worktrees/chore+lint-format-hooks

## Relevant Files

Use these files to complete the task:

- `.claude/settings.local.json` — tracked settings holding the existing `PreToolUse` Bash
  hook; add `PostToolUse` (Write/Edit/MultiEdit → lint.py) here, preserving the existing
  hook.
- `.claude/hooks/block-coauthor-trailer.sh` — reference for the repo's hook conventions
  (stdin payload with snake_case `tool_name`/`tool_input`, `$CLAUDE_PROJECT_DIR`).
- `AGENTS.md` — "always uv / always bun", full-width panels; the runtime rules the scripts
  must honor.

### New Files

- `.claude/hooks/lint.py` — PostToolUse dispatcher: parse stdin JSON → `tool_input.file_path`
  → route by extension → Prettier / Ruff / markdownlint auto-fix → warn-and-skip on missing
  tool → always exit 0. Stdlib-only, PEP 723 header.
- `.claude/hooks/install_deps.py` — installer: `bun install` + `uv sync` (idempotent); warn
  if a declared linter is missing from the manifests. Invoked by `/meta-install`.
  Stdlib-only, PEP 723 header.
- `.claude/commands/meta-install.md` — `/meta-install` command: run the installer so a new
  contributor installs all dev libraries on first checkout.
- `package.json` — declares `prettier` and `markdownlint-cli2` as devDependencies.
- `pyproject.toml` — declares `ruff` as a dev dependency and holds `[tool.ruff]` config.
- `bun.lock`, `uv.lock` — pinned lockfiles generated by the install.
- `.prettierrc.json` — Prettier options (see Requirements).
- `.prettierignore` — excludes `*.md`, `node_modules`, `dist`, `.venv`.
- `.markdownlint.jsonc` — lenient markdownlint rules.

## Edge Cases

- **Tool not installed** (fresh worktree before install completes, or missing manifest
  entry): linter detects absence **without triggering an install** (`uv run --no-sync ruff`
  for Python; direct `node_modules/.bin/<tool>` for JS), prints a one-line stderr note, and
  exits 0 — never blocks.
- **Unknown / unhandled extension** (e.g. `.sh`, `.yaml`, `.txt`): dispatcher no-ops
  silently, exit 0.
- **File under `node_modules/`, `.venv/`, or `dist/`**: skipped (formatter ignore files plus
  a path guard in the dispatcher).
- **Formatter reports unfixable lint** (`ruff check` violations that are not auto-fixable):
  captured and echoed to stderr as a non-blocking note; still exit 0.
- **`uv` or `bun` not on PATH**: warn to stderr and exit 0; the edit loop is never broken.
- **Fresh worktree before install**: the linter warns-and-skips until `/meta-install` is
  run in that worktree (`bun install` + `uv sync` populate `node_modules`/`.venv`).
- **Re-run idempotency**: `bun install` / `uv sync` and all formatters are safe to run
  repeatedly; `/meta-install` twice is a no-op.
- **Malformed / empty stdin JSON**: dispatcher exits 0 without acting (never crashes the turn).

## Red Flags

- Starting to write code without any written requirements
- Asking "should I just start building?" before clarifying what "done" means
- Implementing features not mentioned in any spec or task list
- Making architectural decisions without documenting them
- Skipping the spec because "it's obvious what to build"
- **Auto-installing a linter from inside `lint.py`** on the per-edit path (violates the
  never-block / install-is-separate decision).
- **Any `exit 2` from `lint.py`** — the linter must never deny or block an edit.
- **markdownlint or Prettier churning hand-tuned harness Markdown** — Prettier must not
  touch `.md`; markdownlint must use the lenient config.

## Notes

- New libs: `bun add -d prettier markdownlint-cli2` (JS/TS) and `uv add --dev ruff`
  (Python) declare the tools; the plan commits the resulting manifests + lockfiles.
- Classic vs. documented hook schema: the KB `hooks.md` reference documents a
  `.claude/hooks.json` `on`/`match`/camelCase schema, but this repo's **working** config
  uses the classic `settings.json` schema (`matcher` + `hooks[].command`, snake_case
  `tool_name`/`tool_input`). Follow the working convention; see decisions.md.
- `.claude/commands/` is the "legacy" command format (skills are the newer path) but is the
  repo's established convention for every existing command — match it.

## Codex Findings

<!-- CODEX-OWNED. Written only by the spec-review skill (one `### Round N — Verdict: …` block per
     round). Claude must NEVER edit this section. -->

### Round 1 — Verdict: changes-requested

- **AC1 validation can pass without proving AC1, and one validation command violates the repo runtime rule.** In `acceptance-criteria.md` `## Validation Commands`, replace the current manifest/config checks with assertions that parse `package.json`, `pyproject.toml`, `.prettierrc.json`, `.prettierignore`, and `.markdownlint.jsonc` and verify the exact dev dependencies and configured values named in AC1. Also replace the raw `python3 -c` hooks-registration check with a `uv run --no-project python ...` form, or a non-Python parser, so validation follows `AGENTS.md`'s "Python via uv" rule. As written, `bun pm ls | grep ...` plus `grep -q '\[tool.ruff\]'` does not prove `package.json` declares the required devDependencies, that `ruff` is a dev dependency, or that the Ruff/Prettier/markdownlint options match the spec.

**Recommendations (advisory, non-blocking):**

- Add `ai-docs/anthropic/hooks-guide.md` and/or `ai-docs/anthropic/agent-sdk/claude-code-features.md` to `decisions.md` `## KB References` for the classic `.claude/settings*.json` hook shape and snake_case `tool_input` payload. The current listed `ai-docs/anthropic/hooks.md` documents the newer `.claude/hooks.json`/camelCase schema, while the plan intentionally follows this repo's existing settings-file convention.

### Round 2 — Verdict: approved

The spec meets the bar for `/harness-build`; no blocking findings remain.

## Codex Verification

- **Outcome:** approved at round 2 (round 1 requested stronger AC1/AC4 validation; fixed).
- **Rejected findings:** none — the blocking finding (weak, non-parsing validation commands +
  a raw `python3` call) and the advisory (ground the classic settings schema in a KB doc) were
  both applied: validation now parses manifests via `uv run --no-project python`, and
  `hooks-guide.md` was added to `## KB References`.

## References

```
specs/lint-format-hooks/
├── spec.md                 # this file — what & why, tracking, review record
├── decisions.md            # grilling record: resolved decisions, assumptions, out-of-scope, KB refs
├── tasks.md                # how & who: phases, team, step-by-step tasks
└── acceptance-criteria.md  # done: acceptance criteria + validation commands
```

## Self Validation

- [x] Objective, Task Description, and Non-Goals are filled in (no placeholders left)
- [x] Requirements trace to tasks in tasks.md and to checks in acceptance-criteria.md
- [x] Acceptance criteria are specific and testable
- [x] All four files exist under specs/lint-format-hooks/ and are saved in the repository
- [x] Codex has reviewed the spec and Status reflects the outcome
