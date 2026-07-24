# Spec: harness-self-improvement — Plan 1: machine-check substrate

- **Owner:** @SunshinePeace213
- **Status:** Approved
  <!-- Lifecycle, set by /harness-layer:harness-plan: Drafted for Review → Approved (on a Codex
       `approved` verdict). A cycle that ends still changes-requested — or with Codex unavailable —
       records needs-human in ## Codex Verification and keeps this status. One value only. -->

## Task Description

Plan 1 of the harness self-improvement epic (#53): ship the machine-check substrate the later
plans build on. Four deliverables, all inside the harness layer itself:

1. **Gate re-target** — `.claude/hooks/check_spec_completeness.py` currently gates the
   newest-mtime plan folder across the main `specs/` AND every worktree's `specs/`, so a
   concurrent planning session in another worktree can steal or mask the gate's target. Re-target
   it to the invoking session: read the Stop-hook stdin JSON, resolve the session root from its
   `cwd`, and scan only that root's `specs/`. Ships with concurrency regression tests — this is
   the program's proof-of-loop, shipped through the pipeline itself.
2. **Prompt-contract tests** — a new suite pinning the load-bearing structure of
   `.claude/commands/harness-layer/*.md` and the two `.agents/skills/` review skills, mirroring
   `tests/harness-layer/hooks/test_wiring.py`'s semantic-pinning style. Load-bearing = frontmatter
   keys, required `##` sections, and clauses other components parse (verdict-line grammar, CX IDs,
   marker-comment keys, push refspec, report paths). Must catch the #40/#42 regressions
   (dropped `## Report` / `## Instructions` sections in build/review commands), replayed as tests.
3. **CI** — a GitHub Actions workflow running `uv run pytest tests/harness-layer` via
   astral-sh/setup-uv on PRs touching `.claude/**`, `.agents/**`, `tests/**`, `pyproject.toml`,
   `uv.lock`, `specs/_templates/**`, or the workflow file itself, honoring the `[skip-ci]`
   PR-title token.
4. **Stop-gate lint** — extend the same hook with the soriza-chronic checks: a Validation
   Commands bullet not invoking a committed check blocks (exit 2); absolute-promise wording in
   spec.md warns only.

## Objective

A planning session's Stop gate is provably unaffected by concurrent sessions in other roots; a
dropped load-bearing clause or section in any harness-layer command or review skill fails
`uv run pytest tests/harness-layer`; and that suite runs automatically on every harness-touching PR.

## Non-Goals

- Every Plan 2 / Plan 3 item: findings ledger, PR self-learning gate, health metrics, fix
  verification, constraint retirement, constraint registry, #52 fire-drill.
- The #12 retro stage (deferred until Plan 2's metrics exist; shape pre-locked in decisions.md).
- Learning-loop machinery (Plan 2/3 ledger rows, learning-gate coverage, metrics) for the
  discovery commands (unknowns, brainstorm, prototypes, interview); their prompt files still get
  AC3's baseline contract pins like every harness-layer command file.
- Backfilling per-finding rows from the 55 pre-#52 review reports.
- Prose-fidelity checks beyond structure — Codex stays the judge of prose (locked calibration).
- Making the CI workflow a required status check (GitHub settings; human follow-up).

## Problem Statement

The pipeline's only machine gate selects its target by newest mtime across every worktree — the
same wrong-target defect class Codex blocked four rounds running in soriza's intake hook. The
prompt files the pipeline parses at runtime (verdict lines, marker keys, report paths) have no
machine check at all: #40 and #42 each restored sections that had silently vanished from
build/review commands. And nothing runs the harness test suite on PRs, so even existing tests
gate nothing. Every later self-improvement plan (ledger, learning gate, registry) wants to encode
constraints as tests — worthless until tests run in CI and the gate targets the right plan.

## Solution Approach

Extend what exists rather than adding surfaces: the one command-scoped Stop hook gains
session-scoped targeting (stdin `cwd` → git toplevel → scan only that root's `specs/`) plus the
structure lint; the contract suite copies `test_wiring.py`'s proven pattern (module-level expected
maps + small helpers, exact pins, ship-together updates) to the prompt files; CI is one workflow
file invoking the repo's standard `uv run pytest tests/harness-layer`. The main alternative — a
sibling hook for the lint and golden-file snapshots for the prompts — lost: one gate keeps one
registration (ledger-locked), and golden files churn under auto-format while structural pins
survive reformatting.

## Requirements & Decisions

- **Per-task effort deployment via pinned-effort executors** (most volatile — this cycle's
  CX2-1 redesign): five generic executor definitions
  `.claude/agents/effort-{low,medium,high,xhigh,max}.md` — each minimal and intended for
  explicit deployment (name; a Not-for-proactive-delegation description — best-effort routing
  discouragement, since subagent descriptions have no enforcement field; `effort` frontmatter;
  no `model`, no tools restriction; 2–3-line body), authored per the meta-agent standard. They ship with this plan revision, not the build: the build's first
  `Agent({subagent_type: "effort-<tier>", model: "<stamped alias>"})` call needs them to exist,
  and AC5's plan-time inventory check covers them. Definition frontmatter pins effort
  (per-invocation `model` overrides the definition; there is no per-invocation effort —
  `ai-docs/anthropic/subagents.md`). tasks.md carries concrete per-task model + effort stamps
  and the task-tools board protocol unchanged; the mechanic is documented in
  model-selection.md §Mechanics only; harness-build.md is unchanged. Rejected alternatives
  (CX2-1 interview pass): Workflow deployment (restructures the board protocol) and dropping
  per-task effort (violates model-selection.md's stamping mandate).
- **Session-scoped targeting via stdin `cwd`**: root = `git -C <cwd> rev-parse
  --show-toplevel`, falling back down a fixed single-root chain (stdin cwd itself →
  `$CLAUDE_PROJECT_DIR` → process git toplevel → process cwd); the `.claude/worktrees/*/specs`
  glob is deleted. Within the root, newest-mtime selection with the existing `_templates` /
  discovery-only exclusions stays. Live alternative: `session_id`-keyed marker files — rejected
  as new state the ledger's churn guard forbids without need.
- **Block/warn split** (locked): structure exits 2 (missing files/sections; Validation Commands
  bullet without a known stage tag or committed-check invocation; missing `[plan-time]` script);
  wording warns only (`WARN:` on stderr, exit code unchanged; missing later-stage paths also
  warn — the build creates them).
- **Exact pins, updated in the same commit** (locked, wiring-test model): the contract suite pins
  per-file frontmatter keys/values, exact `##` section tuples, and the clause lists in
  `## Load-Bearing Contract Inventory` below. An intentional prompt change lands with its
  expectation update — that is the ship-together rule, not test brittleness.
- **CI stays dependency-light** (locked): checkout + astral-sh/setup-uv + `uv run pytest
  tests/harness-layer`; `pull_request` types include `edited` so a late `[skip-ci]` title edit
  takes effect; no secrets.

## Tracking

<!-- Recorded by /harness-layer:harness-plan. The Issue field is the SINGLE SOURCE OF TRUTH
     /harness-layer:harness-build reads — it NEVER re-derives #N from the local `worktree-<slug>`
     branch name. spec.md is the single home for this block; decisions.md does not duplicate it. -->

- **Issue:** #54 (epic: #53)
- **Branch:** `chore/54-harness-self-improvement`
- **Worktree:** /Users/ringo/Desktop/ai-native-startup/.claude/worktrees/harness-self-improvement
- **Review profile:** kb-grounded
- **PR:** #55 (draft) — <https://github.com/SunshinePeace213/ai-native-startup/pull/55>
- **Hand-off SHA:** bf8c826a (last implementation push; review derives its own range)
- **Hand-off note:** full suite runs 656 passed / 2 failed — both failures pre-existing on
  `main` in `tests/harness-layer/hooks/auto-format/test_python.py` (ruff quote drift, outside
  this plan's diff; disclosed in the PR's Test Evidence). The first `harness-tests` CI run on
  PR #55 will show them.

## Load-Bearing Contract Inventory

The enumerated pin set for the prompt-contract suite (AC3) — the "parsed by something else"
criterion, locked in decisions.md. Kinds: `frontmatter` — the literal line appears in the file's
frontmatter; `sections` — the file's exact `##` heading set, in order; `clause` — the literal
appears in the file body. `checks/ac5_inventory.py` verifies every row at plan time; the build
turns the same rows into pytest expectations (plus the cross-consistency asserts listed after
the table). Exception: the `.claude/agents/effort-*.md` rows are plan-shipped deployment
scaffolding verified by AC5 only — the AC3 build-time suite pins command and skill rows,
not agent definitions.

| File | Kind | Literal |
| --- | --- | --- |
| `.claude/commands/harness-layer/harness-plan.md` | frontmatter | `model: fable` |
| `.claude/commands/harness-layer/harness-plan.md` | frontmatter | `effort: xhigh` |
| `.claude/commands/harness-layer/harness-plan.md` | frontmatter | `disable-model-invocation: true` |
| `.claude/commands/harness-layer/harness-plan.md` | frontmatter | `disallowed-tools: Task, EnterPlanMode` |
| `.claude/commands/harness-layer/harness-plan.md` | frontmatter | `check_spec_completeness.py` |
| `.claude/commands/harness-layer/harness-plan.md` | sections | Variables, Instructions, Domain Knowledge, Readiness Gate, Workflow, Output: Spec Folder, Plan Artifacts, Worktree & Handoff, Revision Mode, Codex Cross-Review, Report |
| `.claude/commands/harness-layer/harness-plan.md` | clause | `codex-spec-review-round-` |
| `.claude/commands/harness-layer/harness-plan.md` | clause | `<!-- plan-links -->` |
| `.claude/commands/harness-layer/harness-plan.md` | clause | `<!-- codex-spec-round-N -->` |
| `.claude/commands/harness-layer/harness-plan.md` | clause | `HEAD:refs/heads/` |
| `.claude/commands/harness-layer/harness-plan.md` | clause | `codex-runner` |
| `.claude/commands/harness-layer/harness-plan.md` | clause | `gh issue develop` |
| `.claude/commands/harness-layer/harness-plan.md` | clause | `--body-file` |
| `.claude/commands/harness-layer/harness-build.md` | frontmatter | `model: fable` |
| `.claude/commands/harness-layer/harness-build.md` | frontmatter | `disable-model-invocation: true` |
| `.claude/commands/harness-layer/harness-build.md` | sections | Variables, Instructions, Workflow, Report |
| `.claude/commands/harness-layer/harness-build.md` | clause | `--draft` |
| `.claude/commands/harness-layer/harness-build.md` | clause | `--body-file` |
| `.claude/commands/harness-layer/harness-build.md` | clause | `<!-- report:tidy -->` |
| `.claude/commands/harness-layer/harness-build.md` | clause | `.github/PULL_REQUEST_TEMPLATE/` |
| `.claude/commands/harness-layer/harness-review.md` | frontmatter | `model: fable` |
| `.claude/commands/harness-layer/harness-review.md` | frontmatter | `disable-model-invocation: true` |
| `.claude/commands/harness-layer/harness-review.md` | sections | Variables, Instructions, Workflow, Review runner, Back-to-planning exit (spec defects), Report |
| `.claude/commands/harness-layer/harness-review.md` | clause | `codex-impl-review-round-` |
| `.claude/commands/harness-layer/harness-review.md` | clause | `<!-- report:codex-round-N -->` |
| `.claude/commands/harness-layer/harness-review.md` | clause | `codex-runner` |
| `.claude/commands/harness-layer/harness-review.md` | clause | `implementation-review` |
| `.claude/commands/harness-layer/harness-ship.md` | frontmatter | `model: sonnet` |
| `.claude/commands/harness-layer/harness-ship.md` | frontmatter | `effort: low` |
| `.claude/commands/harness-layer/harness-ship.md` | frontmatter | `disable-model-invocation: true` |
| `.claude/commands/harness-layer/harness-ship.md` | frontmatter | `allowed-tools: Bash(git *), Bash(gh *)` |
| `.claude/commands/harness-layer/harness-ship.md` | sections | Variables, Instructions, Workflow, Report |
| `.claude/commands/harness-layer/harness-ship.md` | clause | `--squash` |
| `.claude/commands/harness-layer/harness-ship.md` | clause | `--match-head-commit` |
| `.claude/commands/harness-layer/harness-unknowns.md` | frontmatter | `model: fable` |
| `.claude/commands/harness-layer/harness-unknowns.md` | frontmatter | `effort: high` |
| `.claude/commands/harness-layer/harness-unknowns.md` | frontmatter | `disable-model-invocation: true` |
| `.claude/commands/harness-layer/harness-unknowns.md` | frontmatter | `disallowed-tools: Task, EnterPlanMode` |
| `.claude/commands/harness-layer/harness-unknowns.md` | sections | Variables, Instructions, Modes, Workflow, Improved Prompt, Report |
| `.claude/commands/harness-layer/harness-brainstorm.md` | frontmatter | `model: fable` |
| `.claude/commands/harness-layer/harness-brainstorm.md` | frontmatter | `effort: high` |
| `.claude/commands/harness-layer/harness-brainstorm.md` | frontmatter | `disable-model-invocation: true` |
| `.claude/commands/harness-layer/harness-brainstorm.md` | frontmatter | `disallowed-tools: Task, EnterPlanMode` |
| `.claude/commands/harness-layer/harness-brainstorm.md` | sections | Variables, Instructions, Workflow, Refined Prompt, Report |
| `.claude/commands/harness-layer/harness-prototypes.md` | frontmatter | `model: fable` |
| `.claude/commands/harness-layer/harness-prototypes.md` | frontmatter | `effort: high` |
| `.claude/commands/harness-layer/harness-prototypes.md` | frontmatter | `disable-model-invocation: true` |
| `.claude/commands/harness-layer/harness-prototypes.md` | frontmatter | `disallowed-tools: Task, EnterPlanMode` |
| `.claude/commands/harness-layer/harness-prototypes.md` | sections | Variables, Instructions, Modes, Workflow, Improved Prompt, Report |
| `.claude/commands/harness-layer/harness-interview.md` | frontmatter | `model: fable` |
| `.claude/commands/harness-layer/harness-interview.md` | frontmatter | `effort: high` |
| `.claude/commands/harness-layer/harness-interview.md` | frontmatter | `disable-model-invocation: true` |
| `.claude/commands/harness-layer/harness-interview.md` | frontmatter | `disallowed-tools: Task, EnterPlanMode` |
| `.claude/commands/harness-layer/harness-interview.md` | sections | Variables, Instructions, Coverage Ledger, Round Loop, Output, Report |
| `.claude/commands/harness-layer/kb.md` | frontmatter | `allowed-tools: Bash(curl *), WebFetch` |
| `.claude/commands/harness-layer/kb.md` | sections | Variables, Instructions, Workflow, Report |
| `.agents/skills/spec-review/SKILL.md` | frontmatter | `name: spec-review` |
| `.agents/skills/spec-review/SKILL.md` | clause | `### Round N — Verdict: approved` |
| `.agents/skills/spec-review/SKILL.md` | clause | `### Round N — Verdict: changes-requested` |
| `.agents/skills/spec-review/SKILL.md` | clause | `CX<N>-<i>` |
| `.agents/skills/spec-review/SKILL.md` | clause | `(repeat of` |
| `.agents/skills/spec-review/SKILL.md` | clause | `**Issue-comment digest:**` |
| `.agents/skills/spec-review/SKILL.md` | clause | `codex-spec-review-round-N.md` |
| `.agents/skills/spec-review/SKILL.md` | clause | `[plan-time]` |
| `.agents/skills/spec-review/SKILL.md` | clause | `[child-build-time]` |
| `.agents/skills/spec-review/SKILL.md` | clause | `[post-merge]` |
| `.agents/skills/spec-review/SKILL.md` | clause | `Reviewed head SHA:` |
| `.agents/skills/implementation-review/SKILL.md` | frontmatter | `name: implementation-review` |
| `.agents/skills/implementation-review/SKILL.md` | clause | `### Round N — Verdict: approved` |
| `.agents/skills/implementation-review/SKILL.md` | clause | `### Round N — Verdict: changes-requested` |
| `.agents/skills/implementation-review/SKILL.md` | clause | `CX<N>-<i>` |
| `.agents/skills/implementation-review/SKILL.md` | clause | `(repeat of` |
| `.agents/skills/implementation-review/SKILL.md` | clause | `(spec-defect)` |
| `.agents/skills/implementation-review/SKILL.md` | clause | `**Issue-comment digest:**` |
| `.agents/skills/implementation-review/SKILL.md` | clause | `codex-impl-review-round-N.md` |
| `.agents/skills/implementation-review/SKILL.md` | clause | `Base SHA:` |
| `.agents/skills/implementation-review/SKILL.md` | clause | `Reviewed head SHA:` |
| `.agents/skills/implementation-review/SKILL.md` | clause | `Mode:` |
| `.agents/skills/implementation-review/SKILL.md` | clause | `Lenses:` |
| `.claude/agents/effort-low.md` | frontmatter | `effort: low` |
| `.claude/agents/effort-medium.md` | frontmatter | `effort: medium` |
| `.claude/agents/effort-high.md` | frontmatter | `effort: high` |
| `.claude/agents/effort-xhigh.md` | frontmatter | `effort: xhigh` |
| `.claude/agents/effort-max.md` | frontmatter | `effort: max` |

Cross-consistency asserts (build-time tests, beyond the table):

- Every heading in the hook's `REQUIRED_SECTIONS` appears as a `##` heading in the matching
  `specs/_templates/` file (hook↔template coupling — a template rename cannot silently strand the gate).
- The report filename pattern in `harness-plan.md` matches `spec-review/SKILL.md`'s
  (`codex-spec-review-round-`), and `harness-review.md`'s matches
  `implementation-review/SKILL.md`'s (`codex-impl-review-round-`).
- Both skills carry the identical verdict-line grammar, including the em-dash (U+2014).
- Each skill's frontmatter `name:` equals its directory name.

## Relevant Files

Use these files to complete the task:

- `.claude/hooks/check_spec_completeness.py` — the Stop gate: re-target folder selection, add the lint checks
- `tests/harness-layer/hooks/spec-completeness/test_check_spec_completeness.py` — rewrite the two worktree-glob tests to session-scoped semantics; add concurrency + lint tests
- `tests/harness-layer/hooks/conftest.py` — `run_hook` and the git-isolation helpers stay here (use as-is); the build moves `load_hook_module` out (see New Files)
- `tests/harness-layer/hooks/test_wiring.py` — the style model; its registration pins are unchanged by this plan
- `.claude/commands/harness-layer/*.md` — contract-test subjects (9 files; registration of the hook lives in harness-plan.md frontmatter and does not change)
- `.agents/skills/spec-review/SKILL.md`, `.agents/skills/implementation-review/SKILL.md` — contract-test subjects
- `specs/_templates/spec.md`, `tasks.md`, `decisions.md`, `acceptance-criteria.md` — coupling subjects for the hook↔template assert
- `.claude/rules/harness-layer/hooks.md` — update the gate's catalog row to say session-scoped
- `specs/harness-self-improvement/checks/` — committed plan checks (ac4, ac5)
- `.claude/agents/effort-{low,medium,high,xhigh,max}.md` — pinned-effort executor definitions
  (plan-shipped with this revision; the build deploys every task through them)

### New Files

- `tests/harness-layer/conftest.py` — `load_hook_module` promoted verbatim from `hooks/conftest.py` (path constants re-derived for the new depth) so the prompts suite can import the hook without `sys.path` tricks
- `tests/harness-layer/prompts/test_command_contracts.py` — command frontmatter/section/clause pins + #40/#42 replay tests
- `tests/harness-layer/prompts/test_skill_contracts.py` — review-skill pins + cross-consistency asserts
- `.github/workflows/harness-tests.yml` — the CI workflow

## Edge Cases

- **Two concurrent plan sessions in different worktrees** — each session's gate reads its own stdin `cwd`; the other root's folders never affect the verdict (regression-tested both directions).
- **Malformed / empty stdin, or `cwd` missing from the payload** — degrade down the fallback chain; never crash, never exit 2 on plumbing (documented fail-open contract).
- **stdin `cwd` outside any git repo** — `git rev-parse` fails; the cwd path itself serves as root; no `specs/` there → exit 0 (nothing to gate).
- **Session root has no `specs/` dir** — exit 0, unchanged on-switch semantics, now per-root.
- **acceptance-criteria.md missing the `## Validation Commands` section entirely** — already blocked by the existing required-sections check; the lint runs only when the section exists.
- **A Validation Commands bullet with an unknown stage tag or an inline program** — exit 2 naming the bullet (the lint's core case).
- **A `[child-build-time]` pytest path that doesn't exist yet** — warn only; the build creates it.
- **Absolute-promise wording** — warn only, capped (≤10 lines) so a wordy spec can't flood stderr.
- **Re-run idempotency** — the hook is read-only; repeated Stop firings produce identical results.
- **CI: PR touching none of the seven path filters** — no run (intended); PR title gains `[skip-ci]` after opening — the `edited` type re-evaluates the skip.
- **CI: fork PRs** — no secrets are used, so the default token restrictions are harmless.

## Red Flags

- Starting to write code without any written requirements
- Asking "should I just start building?" before clarifying what "done" means
- Implementing features not mentioned in any spec or task list
- Making architectural decisions without documenting them
- Skipping the spec because "it's obvious what to build"
- Re-introducing any cross-root scan into the hook "for safety" — that is the defect, not a safety net
- Softening an exact contract pin to a fuzzy match "to reduce churn" — pins are the point; update them in the same commit instead
- Adding pyyaml or any third-party dep to a check script — the Codex sandbox has no network (dev-log lesson); stdlib string checks only
- Blocking on the wording heuristic — the ledger locks it warn-only

## Notes

- No new dependencies anywhere: hook and check scripts stay stdlib-only PEP 723 scripts.
- The hook's registration (harness-plan.md frontmatter) does not change, so `test_wiring.py`'s `EXPECTED_BINDINGS` is untouched; the hooks.md catalog row and the hook's contract tests ship together with the behavior change (ship-together rule).
- CI action versions: the builder pins `actions/checkout` and `astral-sh/setup-uv` against the official docs at build time — the KB lacks mirrors for them this run (see decisions.md `## KB References`).
- Follow-up for the human: make `harness-tests` a required status check once it has run green on a few PRs.

## Codex Verification

<!-- CLAUDE-OWNED. The outcome summary Claude records after the Codex loop. -->

- **Outcome:** approved at round 4 — cycle 3 (this revision, after cycle 2's needs-human) ran
  rounds 3–4 (`gpt-5.6-sol` / `xhigh`; reports under `reviews/`). Round 3 (head `4ff9f29`,
  delta vs `57cd02d`): changes-requested — CX2-1 fixed by the pinned-effort executors; CX3-1
  new. Round 4 (head `9be1c35`, delta): CX3-1 fixed; approved.
  Approved SHA: `9be1c35e537bc0b7c2a2a5b8ccaeab653476b853`.
- **History:** cycle 2 (rounds 1–2) ended needs-human on CX2-1 (repeat of CX1-4); the CX2-1
  interview pass locked the executor mechanism this revision implements.
- **Advisories (recorded as follow-ups in decisions.md, never fixed this run):** ship only the
  executor tiers plans actually stamp; defer `xhigh`/`max`.
- **Rejected findings:** none.
- **Note:** as in cycle 2, the `codex-runner` subagent could not be deployed (Agent tool denied
  in this background session); the runner contract — verbatim command, verdict-line
  verification, single retry — was executed inline via Bash, disclosed here. The
  `claude-code-guide` cross-check was likewise unavailable (see decisions.md `## KB References`).

## References

<a tree of the sibling plan files and their purpose, so the four files trace to each other:>

```text
specs/harness-self-improvement/
├── discovery/              # program-wide pre-plan passes + decisions-draft.md (reference, never copy)
├── spec.md                 # this file — what & why, tracking, review record, contract inventory
├── decisions.md            # transcribed program ledger + plan-time decisions + KB references
├── tasks.md                # how & who: phases, team, step-by-step tasks
├── acceptance-criteria.md  # done: acceptance criteria + validation commands
├── checks/                 # committed plan checks (ac4_ci_workflow.py, ac5_inventory.py)
├── artifacts/              # implementation-plan page
└── reviews/                # Codex verdicts (rounds 1–2 recorded this cycle)
```

## Self Validation

- [x] Objective, Task Description, and Non-Goals are filled in (no placeholders left)
- [x] Requirements trace to tasks in tasks.md and to checks in acceptance-criteria.md
- [x] Acceptance criteria are specific and testable
- [x] All four files exist under specs/harness-self-improvement/ and are saved in the repository
- [x] Codex has reviewed the spec and Status reflects the outcome (approved at round 4, see `## Codex Verification`)
