# Decisions: auto-format-hooks

> The grilling record for [spec.md](./spec.md) — why the plan is the way it is. Lifecycle tracking and
> the Codex review record live in spec.md, NOT here; this file is the immutable decision history.

## Summary

Rebuild format-on-save as six Python hooks under `.claude/hooks/auto-format/` (four per-language PostToolUse formatters + two worktree lifecycle hooks) with a shared helper module. ESLint joins the toolchain now, React-ready, with a flat `eslint.config.mjs`. YAML rides the JSON/data hook because Prettier — not markdownlint — is the tool that formats it. Unfixable lint errors are fed back to the agent as clean exit-2 diagnostics; infrastructure failures always fail open. Dependency install moves off SessionStart onto the worktree lifecycle, and the `/meta-install` command is deleted in favor of a `meta-install` skill for fresh clones.

## Resolved Decisions

- **Q:** How should the net-new ESLint toolchain be scoped for the JS/TS hook?
  - **A:** Install the full React-ready set now — `eslint`, `@eslint/js`, `typescript-eslint`, `eslint-config-prettier`, `eslint-plugin-react`, `eslint-plugin-react-hooks` — with a flat config in `eslint.config.mjs` (user-specified `.mjs`, not `.js`). Hook order: `eslint --fix` then `prettier --write`, `eslint-config-prettier` last in the config so the two never fight.
  - **Why:** React projects are planned; the user chose to pay the setup cost once now. Rules out the "TS-only now, React later" and "minimal @eslint/js" options.

- **Q:** Where do `.yaml`/`.yml` belong — the "markdown series" as first guessed, or elsewhere?
  - **A:** In the data hook (`data.py`), alongside `.json`/`.jsonc`, all formatted by Prettier. The markdown hook stays markdownlint-only.
  - **Why:** markdownlint cannot process YAML at all; Prettier (already configured) is the YAML formatter. Grouping follows the tool boundary, not the file vibe.

- **Q:** What happens when a formatter leaves unfixable problems?
  - **A:** Autofix what's fixable; if genuine lint/format errors remain in the edited file, print a clean, meaningful, capped diagnostic list to stderr and exit 2 so the agent understands and fixes them. Refinement recorded at the time: infrastructure failures (missing tool, malformed stdin, hook crash) stay fail-open exit 0 with a one-line note.
  - **Why:** The user explicitly wants the agent to receive actionable error feedback and self-correct. The infra refinement prevents "tool missing" nag-loops the agent cannot fix by editing code. Overrides the retired `lint.py`'s always-exit-0 posture.

- **Q:** How do linters get installed across the main checkout and worktrees?
  - **A:** Worktree hooks only — no SessionStart hook. `worktree_create.py` (WorktreeCreate) creates the worktree and runs `bun install` + `uv sync` inside it; `worktree_remove.py` (WorktreeRemove) removes the worktree and its `worktree-*` branch. Fresh-clone setup is documented/driven by a new `meta-install` skill.
  - **Why:** Worktrees are where the build pipeline works and where deps are guaranteed absent; the user declined SessionStart. Accepts the documented caveat that a WorktreeCreate hook replaces default creation entirely (hook owns `git worktree add`, prints only the path, fires for subagent isolation worktrees too).

- **Q:** What happens to `/meta-install`?
  - **A:** Delete `.claude/commands/meta-install.md`; author `.claude/skills/meta-install/SKILL.md` in its place, covering fresh-clone setup (`bun install` + `uv sync` from committed lockfiles). Stale references in `AGENTS.md`/`HARNESS-LAYER.md` are rewritten.
  - **Why:** User: "Remove the meta-install first because we won't use it anymore … we will have a meta-install skill on how we configure when user are in fresh clone repo."

## Assumptions

- Seven files in `.claude/hooks/auto-format/`: `js_ts.py`, `data.py`, `markdown.py`, `python.py`, `worktree_create.py`, `worktree_remove.py`, `_common.py`. Invalidated if the user wants different names or a dispatcher architecture.
- Registration lives in the tracked `.claude/settings.json` using the existing format: PostToolUse matcher `Write|Edit|MultiEdit`, commands via `uv run --script "$CLAUDE_PROJECT_DIR"/.claude/hooks/auto-format/<file>.py`. Each of the four format hooks registers separately and self-filters by extension (the settings.json matcher targets tool names, not file paths).
- Stdin payload is snake_case (`tool_name`, `tool_input.file_path`), as the working `block_attribution.py` proves for this config format. The KB `hooks.md` shows camelCase (`toolName`, `toolInput`) for the newer `.claude/hooks.json` format this repo does not use — conflict resolved in favor of the in-repo working code; flagged for a KB refresh.
- WorktreeCreate/WorktreeRemove stdin field names differ between sources: the KB hooks reference documents `worktreeName`/`worktreePath`, the tfriedel reference implementation reads `name`/`worktree_path`. Resolution (Codex round 1): both hooks accept **both** shapes, tests exercise both, and the build verifies against a live payload and records which shape arrived.
- Diagnostics cap: first 10 issues + "and N more", format `file:line rule message`.
- Vendored-path skip set: `node_modules`, `.venv`, `dist`, matched on the path relative to the project root (retired `lint.py` behavior).
- `worktree_create.py` bases new branches on the origin default branch, falling back to local `HEAD`; reuses an existing `worktree-<name>` branch instead of failing.
- Tests are pytest modules under `tests/harness-layer/hooks/`, matching the existing `test_block_attribution.py` conventions (subprocess invocation with synthetic payloads; temp git repos for the worktree hooks).
- `.gitignore` already covers `.claude/worktrees` and `.claude/settings.local.json` — no gitignore work needed.
- Issue metadata: type `chore` (🔧), priority `P2`, plan name `auto-format-hooks`.

## Open Questions / Out of Scope

- **Out of scope:** CSS/SCSS formatting; any extension beyond the twelve listed in spec.md.
- **Out of scope:** SessionStart install hook (explicitly declined by the user).
- **Out of scope:** Codex-side registration of format hooks in `.codex/hooks.json`.
- **Out of scope:** `worktree.baseRef` support in `worktree_create.py` — the repo does not use it. (`.worktreeinclude` was originally listed here on the premise the repo had no such file; build-R1 internal review found `.worktreeinclude` tracked at the repo root since `cbe0b5f`, so the premise was false and the copy contract is implemented in `worktree_create.py`.)
- **Out of scope:** Changes to `block_attribution.py`, `check-spec-completeness.sh`, or existing formatter configs.
- **Open question:** none blocking. Follow-ups checklist (advisory, feeds a future plan):
  - [ ] `/harness-layer:kb` refresh of `ai-docs/anthropic/hooks.md` — its WorktreeCreate section ("async, logging only") lags the current worktrees doc contract.
  - [ ] CSS support when styling work lands.
  - [ ] (Codex round 1, advisory) Consult and log `ai-docs/anthropic/skills.md`, `agent-teams.md`, and `settings.md` in KB References when the build touches those surfaces.
  - [ ] (Codex round 1, advisory) If the build session lacks the Task*/team tools, collapse the two builders into one and execute the same ordered task list solo — scope unchanged.

## KB References

Review profile: **kb-grounded**. Docs consulted (path — `fetched` date):

- `ai-docs/anthropic/hooks.md` — 2026-07-05 (event schemas, exit codes, matcher syntax, PostToolUse semantics)
- `ai-docs/anthropic/hooks-guide.md` — 2026-07-05 (settings.json hook format, auto-format-after-edit recipe, Edit|Write matcher)
- `ai-docs/anthropic/worktrees.md` — 2026-07-05 (WorktreeCreate hook replaces default creation; stdout path contract; `.worktreeinclude` and transcript caveats; subagent isolation worktrees)
- External (not KB, fetched via `gh` 2026-07-12): `tfriedel/claude-worktree-hooks` — reference WorktreeCreate/WorktreeRemove scripts and settings registration. Not mirrored into `ai-docs/` (KB is for official docs only).

No gap-fill was needed — hooks + worktrees KB docs cover every harness claim in this plan.
