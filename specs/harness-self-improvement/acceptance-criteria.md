# Acceptance Criteria: harness-self-improvement — Plan 1

> The definition of "done" for [spec.md](./spec.md). Every criterion is observable and testable, and
> every task in tasks.md should map to at least one criterion here.

## Acceptance Criteria

- **AC1** — Session-scoped Stop gate. `check_spec_completeness.py` resolves its gated root from
  the Stop stdin JSON `cwd` (git toplevel, then the documented single-root fallback chain) and
  scans only that root's `specs/`; the `.claude/worktrees/*/specs` glob is gone. Concurrency
  regression tests prove both directions: an incomplete plan folder in a foreign root never
  blocks the session, and a complete folder in a foreign root never masks the session's own
  incomplete plan. Malformed or empty stdin degrades down the fallback chain without crashing.
- **AC2** — Validation-command lint in the same gate. A bullet under `## Validation Commands`
  with no recognized stage tag, or invoking neither `uv run --script specs/<plan>/checks/…` nor
  `uv run pytest …`, exits 2 naming the file and bullet; a `[plan-time]` bullet whose check
  script is absent exits 2. Missing later-stage paths and absolute-promise wording in spec.md
  produce `WARN:` lines on stderr without changing the exit code (warnings capped at 10).
- **AC3** — Prompt-contract suite. `tests/harness-layer/prompts/` pins, for all 9
  `.claude/commands/harness-layer/*.md` files and both `.agents/skills/` review skills, the
  frontmatter literals, exact `##` section sets, and clause lists from spec.md's
  `## Load-Bearing Contract Inventory`, plus the cross-consistency asserts (hook
  REQUIRED_SECTIONS ⊆ template headings; command↔skill report-filename and verdict-grammar
  agreement; skill name = directory name), with the hook imported via `load_hook_module`
  resolved from the promoted `tests/harness-layer/conftest.py`. Includes #40/#42 replay tests: the suite's checker
  flags harness-build.md / harness-review.md text with `## Report` or `## Instructions` removed.
- **AC4** — CI. `.github/workflows/harness-tests.yml` runs `uv run pytest tests/harness-layer`
  via astral-sh/setup-uv on `pull_request` (types including `edited`) with exactly the seven path
  filters (`.claude/**`, `.agents/**`, `tests/**`, `pyproject.toml`, `uv.lock`,
  `specs/_templates/**`, `.github/workflows/harness-tests.yml`) and a job-level
  skip when the PR title contains `[skip-ci]`.
- **AC5** — Inventory accuracy at plan time. Every row of spec.md's
  `## Load-Bearing Contract Inventory` holds against the current tree: each named file exists and
  contains its pinned frontmatter literal, section set, or clause.

## Validation Commands

Validation logic lives in committed check scripts — one script per criterion under
`specs/<name>/checks/` (PEP 723 scripts, like hooks), or pytest files under `tests/`. Never inline
a multi-line program in this file. Each bullet below is exactly ONE line: a stage tag, the script
invocation, and the criterion it verifies.

The stage tag names the earliest point the command can pass. Reviewers run only the commands whose
stage has been reached and record later-stage commands as deferred — deferred is not a failure:

- `[plan-time]` — runnable against the spec folder alone, before any build.
- `[child-build-time]` — runnable once the implementing build (for an epic: the relevant child's
  build) has produced its changes.
- `[post-merge]` — runnable only after dependent work has merged to `main`.

- `[plan-time]` `uv run --script specs/harness-self-improvement/checks/ac5_inventory.py` — verifies AC5. Passes when every inventory row's literal is present in its file today.
- `[child-build-time]` `uv run pytest tests/harness-layer/hooks/spec-completeness` — verifies AC1 and AC2. Passes when the session-scoped targeting, concurrency regressions, lint blocks, and warn-only paths all hold.
- `[child-build-time]` `uv run pytest tests/harness-layer/prompts` — verifies AC3. Passes when every pin holds and the #40/#42 replay tests fail on the mutated text.
- `[child-build-time]` `uv run --script specs/harness-self-improvement/checks/ac4_ci_workflow.py` — verifies AC4. Passes when the workflow file carries the trigger, paths, skip condition, setup-uv step, and pytest invocation.
