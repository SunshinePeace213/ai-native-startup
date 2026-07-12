# Spec: Per-feature harness restructure — hooks, tests, build workflow

- **Owner:** @SunshinePeace213
- **Status:** Approved

## Task Description

Restructure the harness layer along feature lines and tighten the build workflow, in one branch:

1. **Worktree hook separation** — `worktree_create.py` and `worktree_remove.py` are lifecycle hooks
   mislocated in `.claude/hooks/auto-format/`. Move them to a new `.claude/hooks/worktree/` feature
   dir with their own trimmed `_common.py` (both scripts `import _common` from their sibling dir),
   and repoint the `WorktreeCreate`/`WorktreeRemove` registrations in `.claude/settings.json`.
2. **settings.json matcher consolidation** — the five PostToolUse entries that all carry matcher
   `Write|Edit|MultiEdit` (four formatters + `post_write_scan.py`) collapse into ONE matcher block
   whose `hooks` array holds all five commands. Behavior-equivalent: all matching hooks run in
   parallel and identical commands are deduplicated (KB: hooks-guide). This is the only mergeable
   repetition — the two `Bash` matchers sit on different events (PreToolUse vs PostToolUse).
3. **Per-feature test tree** — split `tests/harness-layer/` into
   `tests/harness-layer/hooks/{auto-format,attribution,worktree,security-scan}/` so a build can run
   only the feature under development. Distributed conftests: the shared
   `tests/harness-layer/hooks/conftest.py` keeps cross-feature helpers; each feature dir gets its
   own `conftest.py` for feature-specific fixtures.
4. **harness-build.md workflow upgrades** — each fixer subagent's model is chosen per issue
   difficulty (no hardcoded `sonnet`) via the Agent tool's `model` param, with the AGENTS.md effort
   tier stated in the fixer's task brief as depth guidance — subagents inherit the session's
   reasoning effort, so no `effort` API parameter is claimed (KB: subagents); the combined fix pass
   runs disjoint finding-clusters as parallel background fixers; the Implement phase launches
   unblocked, file-disjoint tasks concurrently; the
   Agent Task Manifest keys tasks by kebab-case Task ID (never `#N`, which GitHub autolinks to
   unrelated issues/PRs — visible on PR #22); `gh pr create` gains `--assignee` and mirrors the
   issue's type + priority labels.
5. **Memory sync** — HARNESS-LAYER.md (files tree, worktree-lifecycle paths, one-matcher-block
   rule) and AGENTS.md (per-feature pytest line) updated in the same branch.

## Objective

`uv run pytest tests/harness-layer/hooks/<feature>` runs exactly one feature's suite and the full
suite still collects and passes all 172 tests; the worktree hooks live in
`.claude/hooks/worktree/` and fire from there; `settings.json` has one `Write|Edit|MultiEdit`
block; `harness-build.md` encodes the five workflow upgrades; both memory files describe the new
reality.

## Non-Goals

- No change to the R1-concurrent review flow in harness-build.md (confirmed correct this session).
- No edits to `harness-review.md` or `harness-plan.md`.
- No rewriting of merged PR bodies (PR #22's `#N` manifest links stay as history).
- No moving of the four formatter hooks; `auto-format/_common.py` keeps its full helper set.
- No pytest import-mode change and no new plugins; test basenames stay unique instead.
- No behavior change in any hook — moves and re-registrations only.

## Problem Statement

Every feature's tests currently run together (172 tests) even when a build touches one hook
family; the worktree lifecycle scripts hide inside `auto-format/`, which misleads readers and
blocks a clean per-feature test mapping; `settings.json` repeats the same matcher five times;
`harness-build.md` hardcodes `sonnet` fixers, runs fixes serially, renders manifest task numbers
that GitHub autolinks to the wrong artifacts, and opens PRs without assignee or labels.

## Solution Approach

Mirror `.claude/hooks/` feature dirs one-to-one under `tests/harness-layer/hooks/`, following the
repo's existing per-feature `_common.py` pattern (security-scan already has its own) for the new
`worktree/` dir. Conftests distribute the same way: shared helpers stay at `hooks/conftest.py`
(`REPO_ROOT`, `UV`, a `run_hook` that resolves scripts against an overridable `hook_dir` fixture);
feature fixtures move into per-feature conftests. The alternative — one flat test dir plus pytest
marks — lost because directory selection needs no registration, mirrors the source tree, and keeps
`--collect-only` obvious. The harness-build.md edits are prompt-text changes that reuse the
existing AGENTS.md model/effort table and the existing kebab-case Task IDs from tasks.md, so no
new convention is invented.

## Requirements & Decisions

- **Consolidation is structural, not behavioral** — all matching hooks run in parallel and
  identical commands are deduplicated (hooks-guide KB line 442), so the five-into-one merge cannot
  change execution; nothing may rely on registration order.
- **`worktree/_common.py` is a trimmed sibling copy** carrying exactly the five helpers the two
  scripts use — `note`, `read_payload`, `resolve_root`, `run`, `tail` — PLUS the module constant
  `STDIN_TIMEOUT = 5.0` that `read_payload` reads, and only the imports those helpers need.
  Signatures and bodies unchanged so the scripts move without edits; sibling `import _common`
  works because Python puts the running script's dir on `sys.path` — a runtime invariant the
  hermetic worktree tests prove (the uv-scripts KB grounds only the `--script` execution mode).
  Duplication with `auto-format/_common.py` is the accepted cost of the standalone-script pattern.
- **Path-depth fixes are part of the move**: `test_block_attribution.py` `parents[3]` → `parents[4]`;
  both security-scan test files `parents[2]` → `parents[4]`; the shared conftest keeps `parents[3]`
  (it does not move). Test basenames stay unique (no `__init__.py` — pytest's default import mode
  collides on duplicates).
- **Manifest task keys are the plan's kebab-case Task IDs** — the existing join key across
  tasks.md, the task board, and builder hand-offs; `#N` is banned in the manifest.

## Tracking

- **Issue:** #23
- **Branch:** refactor/23-per-feature-harness-restructure
- **Worktree:** /home/ringo/ai-native-startup/.claude/worktrees/per-feature-harness-restructure
- **Review profile:** kb-grounded
- **PR:** #24

## Relevant Files

- `.claude/hooks/auto-format/worktree_create.py` — moves to `.claude/hooks/worktree/`; no code edits
- `.claude/hooks/auto-format/worktree_remove.py` — moves to `.claude/hooks/worktree/`; no code edits
- `.claude/hooks/auto-format/_common.py` — source of the five helpers to copy; itself unchanged
- `.claude/settings.json` — WorktreeCreate/WorktreeRemove repointed; five `Write|Edit|MultiEdit` entries → one block
- `tests/harness-layer/hooks/conftest.py` — slims to shared helpers (`REPO_ROOT`, `UV`, `run_hook` + `hook_dir` indirection); worktree fixtures move out
- `tests/harness-layer/hooks/test_js_ts.py`, `test_python.py`, `test_markdown.py`, `test_data.py`, `test_common.py` — move to `hooks/auto-format/`
- `tests/harness-layer/hooks/test_block_attribution.py` — moves to `hooks/attribution/`; `parents[3]` → `parents[4]`
- `tests/harness-layer/hooks/test_worktree_create.py`, `test_worktree_remove.py` — move to `hooks/worktree/`
- `tests/harness-layer/test_security_scan_engine.py`, `test_security_scan_hooks.py` — move to `hooks/security-scan/`; `parents[2]` → `parents[4]`
- `.claude/commands/harness-layer/harness-build.md` — the five workflow upgrades
- `HARNESS-LAYER.md` — files tree, Worktree Lifecycle paths, one-matcher-block rule
- `AGENTS.md` — Python Testing gains the per-feature run line

### New Files

- `.claude/hooks/worktree/_common.py` — trimmed helpers: `note`, `read_payload`, `resolve_root`, `run`, `tail` + the `STDIN_TIMEOUT = 5.0` constant
- `tests/harness-layer/hooks/auto-format/conftest.py` — `hook_dir` → `.claude/hooks/auto-format`; `linter_root`
- `tests/harness-layer/hooks/attribution/conftest.py` — `hook_dir` → `.claude/hooks` (script sits at hooks root)
- `tests/harness-layer/hooks/worktree/conftest.py` — `hook_dir` → `.claude/hooks/worktree`; `wt_repo`, stub helpers
- `specs/per-feature-harness-restructure/validate.py` — (already in this plan) deterministic AC2/AC4 validator: AST-asserts the trimmed module surface, checks each harness-build.md clause as a relationship

## Edge Cases

- **`import _common` resolution** — works only because the script's own dir is on `sys.path`; the
  trimmed copy MUST be a sibling of the moved scripts, and the move must carry the
  `uv run --script` shebang block untouched.
- **Stale `__pycache__`** under the old test paths — untracked and harmless; leave in place (safe-delete rule: never `rm -rf`).
- **Conftest inheritance** — security-scan tests newly inherit the shared `hooks/conftest.py`;
  harmless because fixtures are opt-in, but its module-level `assert UV` now also guards them
  (acceptable: every hook test needs uv anyway).
- **Import-time constants** — the security-scan engine test loads `_common.py` via importlib at
  module import; path constants must stay module-level (fixtures don't exist at import time).
- **Existing worktrees** — the hook re-registration affects only worktrees created after merge;
  in-flight worktrees keep functioning (their copies are self-consistent).
- **`settings.local.json`** — untracked personal overrides are out of scope; the consolidation
  touches only the tracked `settings.json`.
- **Idempotent re-run** — every step is a file move/edit; re-running a task finds the moves already
  done and verifies instead of failing.

## Red Flags

- Starting to write code without any written requirements
- Asking "should I just start building?" before clarifying what "done" means
- Implementing features not mentioned in any spec or task list
- Making architectural decisions without documenting them
- Skipping the spec because "it's obvious what to build"
- Editing the worktree scripts' logic "while we're at it" — this is a move, not a rewrite
- Adding `__init__.py` files or changing pytest import mode to "fix" the layout
- Reordering or "cleaning up" hook commands beyond the specified consolidation

## Notes

- The manifest fix is forward-looking only; this plan's own build should exercise it (its manifest
  uses the kebab Task IDs below).
- Follow-up candidate (not this plan): `run_hook`'s 120s subprocess timeout vs the 60s global
  pytest timeout — pre-existing, untouched.

## Codex Verification

- **Outcome:** approved at round 4 (rounds 3 and 4 were user-authorized delta rounds past the
  2-round cap; both over-cap gates were answered "one more delta round")
- **Rejected findings:** none — all four blocking findings across rounds 1–3 were applied; the two
  round-1 advisories are recorded as follow-ups in decisions.md, not fixed in this run

## References

```text
specs/per-feature-harness-restructure/
├── spec.md                 # this file — what & why, tracking, review record
├── decisions.md            # grilling record: resolved decisions, assumptions, out-of-scope
├── tasks.md                # how & who: phases, team, step-by-step tasks
├── acceptance-criteria.md  # done: acceptance criteria + validation commands
└── validate.py             # deterministic AC2/AC4 validator (module surface + clause checks)
```

## Self Validation

- [x] Objective, Task Description, and Non-Goals are filled in (no placeholders left)
- [x] Requirements trace to tasks in tasks.md and to checks in acceptance-criteria.md
- [x] Acceptance criteria are specific and testable
- [x] All four files exist under specs/per-feature-harness-restructure/ and are saved in the repository
- [x] Codex has reviewed the spec and Status reflects the outcome
