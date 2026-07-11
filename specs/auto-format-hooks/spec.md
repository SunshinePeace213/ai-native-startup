# Spec: auto-format-hooks

- **Owner:** @SunshinePeace213
- **Status:** Approved
  <!-- Lifecycle, set by /harness-layer:harness-plan: Drafted for Review → Approved (on a Codex
       `approved` verdict). If round 2 is still changes-requested, the over-cap gate records the exit
       status in ## Codex Verification — approved | accepted-with-unverified-fixes | needs-human. One value only. -->

## Task Description

Rebuild the repo's format-on-save layer as per-language Python hooks under `.claude/hooks/auto-format/`. The previous layer (`lint.py` + `install_deps.py`, spec `lint-format-hooks`) was retired in commit `e5ff658`; since then nothing formats files Claude edits, `/meta-install` points at a deleted script, and the memory files describe behavior that no longer exists.

The rebuild delivers:

- **Four PostToolUse format hooks**, one file per language family, each run via `uv run --script` and self-filtering by extension:
  - `js_ts.py` — `.js`, `.jsx`, `.ts`, `.tsx`: `eslint --fix` then `prettier --write`. ESLint is net-new: install `eslint`, `@eslint/js`, `typescript-eslint`, `eslint-config-prettier`, `eslint-plugin-react`, `eslint-plugin-react-hooks` and author a flat `eslint.config.mjs` (React-ready now, per user decision).
  - `data.py` — `.json`, `.jsonc`, `.yaml`, `.yml`: `prettier --write` (YAML routes here because markdownlint cannot process YAML; Prettier is the tool that formats it).
  - `markdown.py` — `.md`, `.markdown`: `markdownlint-cli2 --fix`.
  - `python.py` — `.py`, `.pyi`: `ruff format` then `ruff check --fix`.
- **Two worktree lifecycle hooks**: `worktree_create.py` (WorktreeCreate — creates the git worktree and installs dependencies inside it) and `worktree_remove.py` (WorktreeRemove — removes the worktree and its `worktree-*` branch). These exist so fresh worktrees — including subagent isolation worktrees used by the build pipeline — have `node_modules`/`.venv` and the format hooks actually work there.
- **A shared `_common.py`** helper module (stdin payload parsing, project-root resolution, subprocess wrapper, vendored-path skip, diagnostic formatting) imported by the six hooks.
- **`/meta-install` replacement**: delete `.claude/commands/meta-install.md`; author a `meta-install` skill at `.claude/skills/meta-install/SKILL.md` covering fresh-clone setup (`bun install` + `uv sync`).
- **Registration** in the tracked `.claude/settings.json`, **pytest coverage** in `tests/harness-layer/hooks/`, and **memory updates** to `HARNESS-LAYER.md` and `AGENTS.md`.

## Objective

Every file Claude writes or edits in the four language families is auto-formatted in place immediately after the edit; genuine unfixable lint errors are fed back to the agent as clean exit-2 diagnostics it can act on; and every newly created worktree has its formatter toolchain installed automatically — all verified by a passing pytest suite.

## Non-Goals

- No CSS/SCSS or any extension beyond the ten listed (`.js .jsx .ts .tsx .json .jsonc .yaml .yml .md .markdown .py .pyi`).
- No SessionStart install hook — fresh-clone setup is the `meta-install` skill's job (user decision).
- No Codex-side (`.codex/hooks.json`) registration of the format hooks; only Claude Code sessions are in scope.
- No `.worktreeinclude` processing and no `worktree.baseRef` setting support in `worktree_create.py` — the repo uses neither (recorded limitation; revisit if either appears).
- No changes to `block_attribution.py`, `check-spec-completeness.sh`, or the existing Prettier/markdownlint/Ruff config files.
- No CI wiring; the hooks are the enforcement layer.

## Problem Statement

`AGENTS.md` promises "files Claude edits are auto-formatted in place (Prettier / Ruff / markdownlint)" but the implementation was deliberately retired to make room for this redesign. Meanwhile the pipeline has moved to worktree-based builds (`.claude/worktrees/`), where a fresh checkout has no `node_modules` or `.venv` — so even the old design would have silently skipped formatting exactly where builds happen. The repo also has no JS/TS linting at all, while React work is planned. This chore closes all three gaps at once.

## Solution Approach

Per-language single-file hooks (the user's explicit structure) registered on `PostToolUse` with matcher `Write|Edit|MultiEdit`; since the tracked `settings.json` matcher targets tool names only, each hook self-filters by file extension and exits 0 fast on non-matches. All hooks are `uv run --script` single-file Python scripts (PEP 723 header, no dependencies) matching the proven `block_attribution.py` pattern, sharing boilerplate through `_common.py` (importable because Python puts the script's directory on `sys.path`).

Failure posture (user decision): **autofix first, then report what's left**. If unfixable lint/format errors remain in the edited file, the hook prints a clean, capped diagnostic list (`file:line rule message`, first 10 + "and N more") to stderr and exits 2 — Claude Code feeds stderr back to the agent, which understands and fixes the errors. Infrastructure failures — missing tool, malformed/empty stdin, file outside the project, hook crash — always fail open with exit 0 and a one-line stderr note, so the agent loop can never be wedged by plumbing.

Dependency install rides the worktree lifecycle instead of SessionStart. `worktree_create.py` implements the documented WorktreeCreate contract (it **replaces** default creation): read the worktree name from stdin JSON, `git worktree add` at `.claude/worktrees/<name>` on branch `worktree-<name>` based on the origin default branch (fallback: local `HEAD`), run `bun install` + `uv sync` inside it, and print **only** the absolute worktree path on stdout (all logging elsewhere). Install failures never abort creation — the path is still printed and format hooks skip with a note. `worktree_remove.py` mirrors the reference implementation: `git worktree remove --force`, then delete the branch only if it matches `worktree-*`. The alternative — SessionStart install, as the retired design did — lost because it leaves worktrees bare and the user removed it from scope.

## Requirements & Decisions

- **Exit-code contract:** exit 2 + curated capped diagnostics only for genuine unfixable lint errors in the file just edited; every infrastructure failure exits 0 fail-open with a stderr note. Why: the agent should fix real defects, but plumbing problems must never nag-loop it.
- **One Python file per language family** under `.claude/hooks/auto-format/`, run via `uv run --script`, boilerplate shared in `_common.py`. Why: the user's mandated structure; matches the repo's proven hook pattern.
- **Payload shape is snake_case** (`tool_name`, `tool_input.file_path`) as proven by the in-repo `block_attribution.py` — not the camelCase shapes shown in the KB hooks reference, which describe the newer `hooks.json` format this repo does not use. Why: follow working code over a doc for a different config format (conflict surfaced in decisions.md). The worktree lifecycle payloads have no in-repo precedent, so those two hooks accept **both** field shapes — `worktreeName`/`worktreePath` (KB hooks reference) and `name`/`worktree_path` (reference implementation) — and the build verifies against a live payload.
- **WorktreeCreate replaces default creation** — the hook owns `git worktree add`, prints only the path on stdout, and fires for subagent isolation worktrees too (each pays a warm-cache `bun install` + `uv sync`). Why: it's the documented contract; accepted at sign-off.

## Tracking

<!-- Recorded by /harness-layer:harness-plan. The Issue field is the SINGLE SOURCE OF TRUTH
     /harness-layer:harness-build reads — it NEVER re-derives #N from the local `worktree-<slug>`
     branch name. spec.md is the single home for this block; decisions.md does not duplicate it. -->

- **Issue:** #19
- **Branch:** chore/19-auto-format-hooks
- **Worktree:** /home/ringo/ai-native-startup/.claude/worktrees/auto-format-hooks
- **Review profile:** kb-grounded
- **PR:** <#M — filled by /harness-layer:harness-build>

## Relevant Files

Use these files to complete the task:

- `.claude/settings.json` — register the four PostToolUse hooks plus WorktreeCreate/WorktreeRemove; keep the existing PreToolUse attribution entry untouched.
- `.claude/hooks/block_attribution.py` — the style reference for every new hook: PEP 723 `uv run --script` header, `note()` stderr helper, bounded `select`-based stdin read, fail-open `__main__` wrapper. Do not modify.
- `package.json` — add the six ESLint packages as devDependencies via `bun add -d`; `bun.lock` updates alongside.
- `pyproject.toml`, `.prettierrc.json`, `.markdownlint.jsonc` — existing formatter configs the hooks rely on. Do not modify.
- `.claude/commands/meta-install.md` — delete; superseded by the skill.
- `AGENTS.md` — update the Harness Development hook line (mention ESLint, worktree install, the skill) and remove the stale `/meta-install` command reference.
- `HARNESS-LAYER.md` — rewrite the Hooks section and Files tree to document the auto-format layer.
- `tests/harness-layer/hooks/test_block_attribution.py` — existing pytest conventions to match.

### New Files

- `.claude/hooks/auto-format/_common.py` — shared helpers: stdin payload parse (`tool_input.file_path`), project-root resolution (`$CLAUDE_PROJECT_DIR` → script-relative fallback), `run()` subprocess wrapper, vendored-path skip (`node_modules`, `.venv`, `dist` relative to root), diagnostic capping/formatting, `note()`.
- `.claude/hooks/auto-format/js_ts.py` — ESLint --fix → Prettier --write on `.js/.jsx/.ts/.tsx`; unfixable ESLint errors → exit 2.
- `.claude/hooks/auto-format/data.py` — Prettier --write on `.json/.jsonc/.yaml/.yml`; parse errors → exit 2.
- `.claude/hooks/auto-format/markdown.py` — markdownlint-cli2 --fix on `.md/.markdown`; unfixable rules → exit 2.
- `.claude/hooks/auto-format/python.py` — ruff format → ruff check --fix on `.py/.pyi`; unfixable rules → exit 2.
- `.claude/hooks/auto-format/worktree_create.py` — WorktreeCreate hook: create worktree + install deps; reads the worktree name from `worktreeName` or `name`; stdout = path only.
- `.claude/hooks/auto-format/worktree_remove.py` — WorktreeRemove hook: remove worktree, delete `worktree-*` branch; reads the path from `worktreePath` or `worktree_path`.
- `eslint.config.mjs` — flat config: `@eslint/js` recommended + `typescript-eslint` for `.ts/.tsx` + `eslint-plugin-react`/`eslint-plugin-react-hooks` recommended + `eslint-config-prettier` last.
- `.claude/skills/meta-install/SKILL.md` — fresh-clone setup skill: run `bun install` + `uv sync` from the committed lockfiles; idempotent; triggering phrasings mirror the old command's.
- `tests/harness-layer/hooks/test_js_ts.py`, `test_data.py`, `test_markdown.py`, `test_python.py`, `test_worktree_create.py`, `test_worktree_remove.py`, `test_common.py` — pytest coverage per hook.

## Edge Cases

- Empty, malformed, or non-JSON stdin; payload missing `tool_input.file_path`; TTY stdin → exit 0 silently (fail-open).
- Edited file deleted or renamed before the hook runs → exit 0 with a note; never a crash.
- File outside the project root (e.g. scratchpad) → format hooks still run on it only if its extension matches and it exists; vendored-skip logic applies to in-repo paths only (mirror the retired `lint.py` relative-to-root check so an ancestor dir named `dist` can't skip everything).
- Path containing `node_modules`, `.venv`, or `dist` relative to the project root → exit 0, untouched.
- Formatter binary missing (fresh clone, `node_modules` absent) → exit 0, one-line note naming the `meta-install` skill.
- Formatter exits non-zero with autofix applied but unfixable errors remaining → exit 2, diagnostics capped at 10 lines + "and N more".
- Formatter crashes on valid input (segfault, OOM) → treated as infrastructure: exit 0 + note.
- `worktree_create.py`: payload carries the name as `worktreeName` or `name` (accept either; neither present → exit 0 with a note); branch `worktree-<name>` already exists → reuse it (`git worktree add <path> <branch>`); origin fetch fails or no remote → base on local `HEAD`; `bun install`/`uv sync` failure → log, still print the path; stdout must contain the path and nothing else (all git/install output redirected).
- `worktree_remove.py`: payload carries the path as `worktreePath` or `worktree_path` (accept either); worktree path missing → exit 0; branch not matching `worktree-*` → remove worktree but keep the branch; git errors → note + exit 0.
- Concurrent edits to different files → hooks are per-file and independent; no shared state, no locks needed.
- Re-running any hook on an already-formatted file → no-op, exit 0 (idempotent).

## Red Flags

- Starting to write code without any written requirements
- Asking "should I just start building?" before clarifying what "done" means
- Implementing features not mentioned in any spec or task list
- Making architectural decisions without documenting them
- Skipping the spec because "it's obvious what to build"
- Adopting the KB's camelCase payload fields or `.claude/hooks.json` config format — this repo uses the `settings.json` format with snake_case payloads (see Requirements & Decisions)
- Printing anything besides the worktree path on `worktree_create.py`'s stdout
- Exit 2 for a missing tool or bad stdin — that posture belongs only to real lint errors

## Notes

- New JS deps: `bun add -d eslint @eslint/js typescript-eslint eslint-config-prettier eslint-plugin-react eslint-plugin-react-hooks`. No new Python deps (hooks are stdlib-only).
- The KB `hooks.md` lists WorktreeCreate under "Async Events … logging and notifications only", while `worktrees.md` (and the current official docs the user quoted) define the create-and-print-path contract that replaces default creation. The worktrees doc wins; a `/harness-layer:kb` refresh of `hooks.md` is flagged as a follow-up.
- Reference implementation studied via `gh`: [tfriedel/claude-worktree-hooks](https://github.com/tfriedel/claude-worktree-hooks) — stdin `name` field on create, `worktree_path` on remove, stdout purity, `worktree-*` branch cleanup. Its port-hashing and env-copy features are intentionally not adopted. Because the KB hooks reference documents `worktreeName`/`worktreePath` instead, the hooks accept both shapes (see Requirements & Decisions).
- Follow-ups (advisory, not in this plan): CSS support if styling work lands; `.worktreeinclude` handling in `worktree_create.py` if the file ever appears; KB refresh above.

## Codex Verification

<!-- CLAUDE-OWNED. The outcome summary Claude records after the Codex loop. -->

- **Outcome:** approved at round 2
- **Rejected findings:** none — both round-1 blocking findings were applied (dual worktree payload shapes; tightened AC1/AC9/AC11 validation commands). Round-1/2 advisories (extra KB references, single-builder fallback) are recorded as follow-ups in decisions.md, not fixed in this run per the review protocol.

## References

```
specs/auto-format-hooks/
├── spec.md                 # this file — what & why, tracking, review record
├── decisions.md            # grilling record: resolved decisions, assumptions, out-of-scope
├── tasks.md                # how & who: phases, team, step-by-step tasks
└── acceptance-criteria.md  # done: acceptance criteria + validation commands
```

## Self Validation

- [x] Objective, Task Description, and Non-Goals are filled in (no placeholders left)
- [x] Requirements trace to tasks in tasks.md and to checks in acceptance-criteria.md
- [x] Acceptance criteria are specific and testable
- [x] All four files exist under specs/auto-format-hooks/ and are saved in the repository
- [x] Codex has reviewed the spec and Status reflects the outcome
