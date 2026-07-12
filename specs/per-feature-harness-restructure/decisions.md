# Decisions: Per-feature harness restructure — hooks, tests, build workflow

> The grilling record for [spec.md](./spec.md) — why the plan is the way it is. Lifecycle tracking and
> the Codex review record live in spec.md, NOT here; this file is the immutable decision history.

## Summary

The harness gets restructured along feature lines: worktree lifecycle hooks move out of
`auto-format/` into their own `.claude/hooks/worktree/` dir with a trimmed `_common.py`, the test
tree mirrors the hook features one-to-one with distributed conftests, and `settings.json` collapses
its five repeated `Write|Edit|MultiEdit` matchers into one block. In parallel, `harness-build.md`
gains difficulty-matched fixer models, parallel fix clusters, concurrent implement tasks,
autolink-safe manifest IDs, and PR assignee/labels. The grilling ran in-session (2026-07-12); the
user gave final sign-off with "start the refactor task" after a full scope replay.

## Resolved Decisions

- **Q:** Where do the security-scan tests go in the per-feature split?
  - **A:** All four features under `tests/harness-layer/hooks/` — `auto-format/`, `attribution/`,
    `worktree/`, `security-scan/`.
  - **Why:** Mirrors `.claude/hooks/` one-to-one; rules out leaving security-scan tests stranded at
    the harness-layer root.
- **Q:** Who decides parallelism during the Implement phase?
  - **A:** Plan structures, build executes: tasks.md owns dependencies; the build lead launches all
    unblocked, file-disjoint tasks concurrently. For fix rounds (no plan exists), the build lead
    clusters findings and picks each fixer's model + effort itself, running clusters in parallel.
  - **Why:** The planner already reasons about file overlap; the lead exploiting that structure
    beats it second-guessing the plan. Rules out both always-sequential and lead-overrides-plan.
- **Q:** What replaces `#1/#2/#3` in the Agent Task Manifest?
  - **A:** The plan's kebab-case Task ID (e.g. `worktree-hook-split`).
  - **Why:** Already the join key across tasks.md, the task board, and hand-offs; can never
    autolink. Rules out `T1/T2` (a second numbering scheme) and backtick-escaped `#N` (relies on
    every future writer remembering the escape).
- **Q:** What PR metadata does the draft PR get at creation?
  - **A:** `--assignee <login>` plus the linked issue's type label and `priority:P<n>` label.
  - **Why:** PR and issue stay filter-consistent on the board. Rules out assignee-only.
- **Q:** How do the moved worktree scripts keep `import _common` working?
  - **A:** A trimmed sibling `.claude/hooks/worktree/_common.py` with exactly the five helpers the
    scripts use (`note`, `read_payload`, `resolve_root`, `run`, `tail`), signatures unchanged.
  - **Why:** Follows the repo's existing per-feature `_common.py` pattern (security-scan);
    duplication of five small helpers is the accepted cost of standalone `uv run --script` hooks.
    Rules out cross-dir `sys.path` hacks and a new shared `_lib/` package.
- **Q:** Conftest architecture after the split?
  - **A:** Distributed + shared: `hooks/conftest.py` keeps cross-feature helpers (`REPO_ROOT`,
    `UV`, `run_hook` resolving against an overridable `hook_dir` fixture); each feature dir's
    conftest holds its own fixtures (`linter_root` → auto-format; `wt_repo` + stubs → worktree;
    attribution sets `hook_dir` to the hooks root).
  - **Why:** Conftests apply recursively, so shared stays shared with zero duplication while
    feature fixtures stop leaking into unrelated features.
- **Q:** Scope of the settings.json consolidation?
  - **A:** Only the five PostToolUse `Write|Edit|MultiEdit` entries merge into one block.
  - **Why:** Verified the only repetition: the two `Bash` matchers sit on different events
    (PreToolUse attribution guard vs PostToolUse bash tracker) and cannot merge. Consolidation is
    behavior-equivalent per the hooks-guide KB (parallel + dedup), so it is purely structural.
- **Q:** Where does the one-matcher-block rule live?
  - **A:** HARNESS-LAYER.md's Hooks section, one line.
  - **Why:** It's hook-registration mechanics — HARNESS-LAYER.md is that owner per the memory map;
    the build's memory-sync reviewer then enforces it on future diffs.
- **Q:** Is the R1-concurrent review workflow (internal ∥ Codex, merge, one fix pass, R2 delta) correct?
  - **A:** Yes — unchanged. Both gates review the same frozen SHA; R2 dispositions both reports.
  - **Why:** The only asymmetry (internal never re-reviews fixes) is a deliberate cost tradeoff
    under the 2-round cap.

## Assumptions

- Priority P2 and type `refactor` (♻️) — the user set neither explicitly; invalidated if they
  re-label the issue.
- The `run_hook`/`hook_dir` fixture-override mechanics are the builder's to fine-tune (e.g.
  attribution may keep its local runner); the contract is only "shared conftest holds shared
  helpers, feature conftests hold feature fixtures, all paths resolve".
- security-scan gets no per-feature conftest — its path constants must stay module-level because
  the engine test loads `_common.py` via importlib at import time; invalidated if fixture-shaped
  shared state appears there later.
- Baseline of 172 collected tests (measured 2026-07-12 pre-move) is the preservation target;
  invalidated if main moves before the build starts — re-measure then.
- Stale `__pycache__` dirs under old test paths stay in place (safe-delete rule); pytest ignores
  them.

## Open Questions / Out of Scope

- **Out of scope:** any change to the R1-concurrent review flow; edits to `harness-review.md` or
  `harness-plan.md`; rewriting merged PR bodies (PR #22 stays as-is); moving the four formatter
  hooks; pytest import-mode changes or new plugins; `settings.local.json`.
- **Open question:** should `auto-format/_common.py` and `worktree/_common.py` eventually share a
  tested single source (the duplication is five helpers today)? Owner: a future plan if a third
  copy ever appears.
- **Open question:** `run_hook`'s 120s subprocess timeout exceeds the 60s global pytest timeout —
  pre-existing oddity, untouched here. Owner: future test-hygiene chore.

## KB References

- `ai-docs/anthropic/hooks-guide.md` (fetched 2026-07-05) — "all matching hooks run in parallel,
  and identical hook commands are automatically deduplicated" (line 442); parallel-order
  non-determinism caveat (line 897). Grounds the consolidation's behavior-equivalence.
- `ai-docs/anthropic/hooks.md` (fetched 2026-07-05) — WorktreeCreate/WorktreeRemove payload fields
  (`worktreeName`, `worktreePath`, lines 503–531); event catalog. Grounds the re-registration and
  the tests' payload shapes.
- `ai-docs/anthropic/settings.md` (fetched 2026-07-06) — `hooks` key structure in settings files.
- `ai-docs/astral/uv-scripts.md` (fetched 2026-07-05) — `uv run --script` inline-metadata
  execution, which puts the script's dir on `sys.path` (grounds the sibling `_common.py` move).
