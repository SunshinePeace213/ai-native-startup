# Plan: Codex Implementation-Review Gate for /build

## Task Description

Extend the `/build` workflow with a Codex verification step. After Claude's builders finish
implementing a saved plan and before `/build` emits its final report, an automated loop hands
the **implemented code** to Codex for an independent review against the plan. Codex reads
`plan.md` + `decisions.md` + the working-tree git diff, **runs the plan's Validation
Commands**, statically checks the changes against the acceptance criteria and locked decisions,
and emits a per-round verdict + blocking findings **as its final CLI message only** — it writes
no files and edits no source. Claude reads the verdict, deploys builders to fix the warranted
findings, and re-submits to Codex. The cycle repeats until Codex approves or a **2-round cap**
is reached.

The reviewer is delivered as a new **Codex Skill** named `implementation-review`, repo-level at
`.agents/skills/implementation-review/`, sibling to the existing `spec-review` skill. The loop
lives entirely in the `/build` command (`.claude/commands/build.md`); `plan-w-team` and the
`plan.md` template are **unchanged**. The gate runs on every build but skips gracefully — with a
recorded note in the Report — when the Codex CLI is unavailable. This feature deliberately picks
up the non-goal that `codex-spec-review-gate/decisions.md` deferred: a Codex review of the
implemented code during the build phase.

## Objective

When complete: a `/build` run implements the plan as today, then automatically runs a max-2-round
Codex implementation-review loop that (1) has Codex read the plan + working-tree diff, run the
plan's Validation Commands, and emit a greppable per-round verdict + findings as its final CLI
message (captured to the session scratchpad, no repo files); (2) lets Claude deploy builders to
fix warranted findings between rounds; and (3) finishes by reporting the verification outcome
(approved at round N / proceeded without approval after 2 rounds / skipped). The
`implementation-review` Codex Skill is checked into the repo and validated, and the loop is fully
documented in `build.md`.

## Requirements & Decisions

- **Loop lives in `/build`, specs untouched.** `build.md` gains a "Codex Implementation Review
  Loop" section that runs on every build. `plan-w-team` / `plan.md` are NOT changed. Full record
  in `decisions.md`.
- **New Codex Skill `implementation-review`** at `.agents/skills/implementation-review/SKILL.md`
  (repo-level, sibling to `spec-review`), authored to meta-skill-grade + Codex `skill-creator`
  conventions.
- **Ephemeral output, runs validation, never edits source.** Codex emits the verdict + findings
  as its FINAL MESSAGE only (no files, no source edits), captured via `codex exec -o <scratch>`.
  It runs the plan's Validation Commands under `-s workspace-write` and reports real pass/fail.
- **Max 2 Codex rounds, graceful skip.** Claude passes round N in the prompt, greps the verdict,
  fixes warranted findings, re-runs; after 2 rounds it proceeds and records non-approval. If the
  Codex CLI is unavailable, skip with a warning (→ `/codex:setup`) and a Report note.

## Problem Statement

`/build` currently implements a plan and reports completion with no independent check that the
implementation actually satisfies the plan. A builder can mark tasks done, claim "tests pass",
or drift from a locked decision, and nothing verifies it before hand-off. The existing
`spec-review` gate reviews the *plan* before building, but the *built code* gets no second pair
of eyes — `codex-spec-review-gate` explicitly deferred that as a non-goal. There is no automated,
recorded verification that the working tree matches the spec.

## Solution Approach

Insert an automated Claude↔Codex review loop as the final `/build` step, after implementation and
before the Report. A repo-level Codex Skill (`implementation-review`) encodes the review
contract: read the plan + `decisions.md` + the working-tree git diff, run the plan's Validation
Commands, judge the build against a blocking-issue finding bar, and emit a per-round verdict +
findings **as the final CLI message** (writing no files, editing no source). `build.md` drives
the loop: render the `codex exec` invocation (with `-o <scratch>` to capture Codex's final
message, `-s workspace-write`, `-C <repo>`, naming the skill + the plan path + the round number),
run Codex, grep the verdict line from the captured file, and either finish (approved) or deploy
builders to fix the warranted findings and re-run — capped at 2 rounds. A `command -v codex`
precondition makes the gate skip gracefully when Codex is absent. The review is partitioned from
the code by channel: Codex only talks (its final message), Claude's builders own every file edit.

## Relevant Files

Use these files to complete the task:

- `.claude/commands/build.md` — the command to modify: add a Workflow step that runs the loop
  after implementation, and a new "## Codex Implementation Review Loop" section documenting the
  precondition/skip, the `codex exec` invocation, verdict grep, max-2-round cadence, fix step, and
  the outcome line in the Report.
- `.agents/skills/spec-review/SKILL.md` — the sibling skill to mirror for structure, frontmatter
  style, finding-bar wording, verdict contract, and never-touch rules. The new skill is its
  build-phase analog.
- `specs/codex-spec-review-gate/runtime-notes.md` — the empirically verified Codex runtime facts
  (repo-level `.agents/skills` discovery, `-s workspace-write`, verdict-grep regex, `-o` capture,
  `quick_validate` angle-bracket rule). **Reuse these; do not re-derive.**
- `specs/codex-spec-review-gate/plan.md` + `decisions.md` — the precedent gate; this plan is its
  build-phase counterpart. Useful as the integration fixture (a real plan with acceptance criteria
  + validation commands to review against).
- `.claude/skills/meta-commands/SKILL.md` + `scripts/validate_command.py` — house standard +
  validator for the modified `build.md` (run after editing).
- `~/.codex/skills/.system/skill-creator/scripts/` — Codex's native skill tooling
  (`init_skill.py`, `quick_validate.py`, `generate_openai_yaml.py`); follow for the new skill.
- `.claude/skills/meta-skill/SKILL.md` — the team's skill-authoring bar; author to this grade.

### New Files

- `.agents/skills/implementation-review/SKILL.md` — the Codex Skill. Reviews a `/build`
  implementation against its plan and emits the per-round verdict + findings as its final message.
- `.agents/skills/implementation-review/agents/openai.yaml` — optional Codex UI metadata, if
  `init_skill.py` / `generate_openai_yaml.py` produces it.

## Implementation Phases

### Phase 1: Foundation

Confirm the one runtime unknown that differs from `spec-review`: the **ephemeral `-o` capture**.
`spec-review` reads the verdict from a file Codex writes into `plan.md`; this gate instead reads
the verdict from Codex's captured **final message**. Verify that `codex exec -o <scratch-file>`
reliably writes Codex's last message and that the `### Round N — Verdict: …` line is greppable
from it, and confirm `-s workspace-write` lets Codex run a validation command while we still
forbid source edits. All other runtime facts are reused verbatim from
`codex-spec-review-gate/runtime-notes.md` — do not re-derive them.

### Phase 2: Core Implementation

Two parallel tracks:

- **Author the `implementation-review` Codex Skill** at
  `.agents/skills/implementation-review/SKILL.md`, mirroring `spec-review` structure but
  retargeted to the build phase: inputs = plan path (+ sibling `decisions.md`) and the
  working-tree git diff; procedure = run the plan's Validation Commands + static-review the diff;
  finding bar = the five blocking categories; output contract = emit verdict + Validation block +
  findings as the FINAL MESSAGE only; never write files, never edit source. Validate with
  `quick_validate.py`.
- **Modify `build.md`**: add the Workflow step + the "## Codex Implementation Review Loop" section
  (precondition/skip, invocation, verdict grep, max-2-round fix cadence, Report outcome). Validate
  with `validate_command.py`.

### Phase 3: Integration & Polish

End-to-end forward test: use a real saved plan as the fixture, run the actual `codex exec`
invocation the loop will use, and verify (a) `-o` captures a `### Round N — Verdict: …` block as
the final message; (b) the verdict matches the grep regex; (c) Codex ran the plan's Validation
Commands and reported pass/fail; (d) Codex wrote/edited **no repo files** — a
`git status --porcelain --untracked-files=all` snapshot taken before and after the review run is
identical (this catches newly created untracked files, not just edits to tracked files).
Forward-test the skill from a fresh Codex run told only "use
`implementation-review` on `<plan>`". Verify the graceful-skip path. Run all validators. Fix gaps.

## Team Orchestration

- You operate as the team lead and orchestrate the team to execute the plan.
- You're responsible for deploying the right team members with the right context to execute the plan.
- IMPORTANT: You NEVER operate directly on the codebase. You use `Task` and `Task*` tools to deploy team members to to the building, validating, testing, deploying, and other tasks.
  - This is critical. You're job is to act as a high level director of the team, not a builder.
  - You're role is to validate all work is going well and make sure the team is on track to complete the plan.
  - You'll orchestrate this by using the Task* Tools to manage coordination between the team members.
  - Communication is paramount. You'll use the Task* Tools to communicate with the team members and ensure they're on track to complete the plan.
- Take note of the session id of each team member. This is how you'll reference them.

### Team Members

- Builder
  - Name: `runtime-scout`
  - Role: Confirm the ephemeral `-o` capture + verdict grep and the workspace-write/run-validation
    behavior (Phase 1), then own the end-to-end integration and final validation (Phase 3).
  - Agent Type: `general-purpose` (no `.claude/agents/team/*.md` exists)
  - Resume: true
- Builder
  - Name: `skill-author`
  - Role: Author and validate the `implementation-review` Codex Skill per Codex `skill-creator`
    + meta-skill conventions.
  - Agent Type: `general-purpose`
  - Resume: true
- Builder
  - Name: `command-editor`
  - Role: Modify `build.md` (Workflow step + Codex Implementation Review Loop section + Report
    outcome) and validate it with the meta-commands validator.
  - Agent Type: `general-purpose`
  - Resume: true

## Step by Step Tasks

- IMPORTANT: Execute every step in order, top to bottom. Each task maps directly to a `TaskCreate` call.
- Before you start, run `TaskCreate` to create the initial task list that all team members can see and execute.

### 1. Confirm Ephemeral Codex Runtime

- **Task ID**: confirm-ephemeral-runtime
- **Depends On**: none
- **Assigned To**: runtime-scout
- **Agent Type**: general-purpose
- **Parallel**: false
- Read `specs/codex-spec-review-gate/runtime-notes.md` and reuse its verified facts (repo-level
  `.agents/skills` discovery, `-s workspace-write`, verdict-grep regex, angle-bracket rule). Do
  NOT re-derive them.
- Verify the EPHEMERAL channel: run a throwaway `codex exec -C "$REPO_ROOT" -s read-only -o "$TMPDIR/codex-cap-test.txt" "Reply with exactly one line: ### Round 1 — Verdict: approved"` and confirm the captured file contains that line and matches `grep -E '^### Round [0-9]+ — Verdict: (approved|changes-requested)$'`. (Em-dash is U+2014.)
- Confirm `-s workspace-write` lets Codex run a validation command (e.g. a `py_compile` or a grep)
  while we still require it to edit no source — note that workspace-write is granted ONLY for
  running validation, not for mutating source.
- Record any deltas from `runtime-notes.md` in a short note for Tasks 2–3 (reuse the same
  invocation template). Clean up scratch files via `mv … ~/.Trash/`.

### 2. Author the implementation-review Codex Skill

- **Task ID**: author-implementation-review-skill
- **Depends On**: confirm-ephemeral-runtime
- **Assigned To**: skill-author
- **Agent Type**: general-purpose
- **Parallel**: true
- Initialize the skill at `.agents/skills/implementation-review/SKILL.md` (prefer
  `init_skill.py`; else hand-create). Skill `name: implementation-review`. Description must
  front-load triggers and contain NO angle brackets (quick_validate rejects `<`/`>`).
- Write the body (imperative, concise, < 500 lines), mirroring `spec-review` structure:
  - **Inputs:** the plan's `plan.md` path (given in the prompt), its sibling `decisions.md`
    (locked decisions/constraints), and the working-tree changes (`git status` + `git diff`,
    including untracked files). The round number N is given in the prompt.
  - **Procedure:** run the plan's **Validation Commands** and record each as PASS/FAIL; then
    static-review the diff against the plan's Acceptance Criteria, Step-by-Step Tasks, and locked
    decisions.
  - **Finding bar (blocking only):** unmet acceptance criteria; incomplete/missing tasks;
    failing or not-run validation commands; plan/decision violations or build-time scope drift;
    real bugs / regressions / security / data-loss risks. No style nits, no speculation; ground
    every finding in a plan line + a file/location.
- Encode the OUTPUT CONTRACT exactly (Decision 7): the FINAL MESSAGE begins with
  `### Round N — Verdict: approved` or `### Round N — Verdict: changes-requested` (literal em-dash
  U+2014; N from the prompt; `approved` only when zero blocking findings), followed by a
  `Validation:` block (one line per command → PASS/FAIL) and, for changes-requested, a
  `Findings:` list (one bullet per finding with a concrete fix + plan/file anchor).
- Encode the NEVER-TOUCH rules: emit findings as the FINAL MESSAGE only; **write no files** and
  **edit no source** (workspace-write is for running validation, not mutation); never edit
  `decisions.md`.
- Validate with `uv run python "$HOME/.codex/skills/.system/skill-creator/scripts/quick_validate.py" .agents/skills/implementation-review`; fix all reported issues.

### 3. Modify the /build command

- **Task ID**: modify-build-command
- **Depends On**: confirm-ephemeral-runtime
- **Assigned To**: command-editor
- **Agent Type**: general-purpose
- **Parallel**: true
- In `build.md` **Workflow**, after the implement step and before the Report, add a step:
  "When implementation completes, run the **Codex Implementation Review Loop** (below) before
  reporting."
- Add a new **"## Codex Implementation Review Loop"** section documenting:
  - **Precondition / graceful skip:** `command -v codex`; if unavailable, skip the loop, warn the
    user (point to `/codex:setup`), note the skip in the Report, and finish the build normally.
  - **Invocation (verbatim, substituting `<REPO_ROOT>`, `<PLAN_PATH>`, `<N>`, `<SCRATCH>`):**
    ```
    codex exec -C "<REPO_ROOT>" -s workspace-write -o "<SCRATCH>/codex-review-round-<N>.md" "Use the implementation-review skill to review the build of the plan at <PLAN_PATH> (this is review round <N>). Inspect the working-tree changes (git status/diff) against the plan's acceptance criteria, step-by-step tasks, and the locked decisions in the sibling decisions.md, and run the plan's Validation Commands. Follow the skill's output contract exactly: emit your round <N> verdict and findings as your FINAL MESSAGE only; write no files and edit no source."
    ```
    Note: `codex exec` has NO `--skill`/`--full-auto`/`-a` flag; the skill is auto-discovered and
    invoked by naming it. `<SCRATCH>` is the session scratchpad (e.g. `$CLAUDE_JOB_DIR/tmp` or
    `$TMPDIR`), never the repo. Give each round a generous timeout (~5 min).
  - **Read the verdict from the captured file:**
    `grep -E '^### Round [0-9]+ — Verdict: (approved|changes-requested)$' "<SCRATCH>/codex-review-round-<N>.md" | tail -1` (em-dash U+2014). A round that times out / captures nothing is re-run, NOT treated as approval.
  - **Loop control — max 2 rounds:** Round 1 approved → done. changes-requested → Claude deploys
    builders to fix the warranted findings (records any rejected finding + rationale in the
    Report) → Round 2. If Round 2 is still changes-requested → best-effort final pass and PROCEED,
    recording "proceeded without full Codex approval after 2 rounds" + outstanding findings.
  - **Codex never edits source** — it reports only; Claude's builders apply every fix.
- Add the verification outcome (approved at round N / proceeded without approval after 2 rounds /
  skipped — Codex unavailable), the per-round Validation pass/fail summary, and any
  outstanding/rejected findings to the **Report** section.
- Validate: `cd .claude/skills/meta-commands && uv run --with pyyaml python scripts/validate_command.py ../../commands/build.md`.

### 4. Integration forward-test

- **Task ID**: integration-forward-test
- **Depends On**: author-implementation-review-skill, modify-build-command
- **Assigned To**: runtime-scout
- **Agent Type**: general-purpose
- **Parallel**: false
- Pick a real saved plan as the fixture (e.g. `specs/codex-spec-review-gate/plan.md`, which has
  Acceptance Criteria + Validation Commands). Run the exact `codex exec` invocation from `build.md`
  with `<N>`=1 and `-o "$TMPDIR/codex-review-round-1.md"`.
- Verify: (a) the captured file's final-message block starts with
  `### Round 1 — Verdict: <approved|changes-requested>` and matches the grep regex; (b) it
  contains a `Validation:` block reflecting the plan's Validation Commands run by Codex;
  (c) a `git status --porcelain --untracked-files=all` snapshot is identical before and after the
  review run — proving Codex wrote/edited **no repo files** (detects added untracked files, not
  just edits to tracked files).
- Forward-test from a FRESH Codex run told only "use `implementation-review` on `<plan>`" (no
  leaked expectations) to confirm it triggers and honors the contract.
- Verify the graceful-skip path: with `codex` masked/unavailable, confirm the documented loop
  skips and records the note (dry-run the documented steps). Clean up scratch via `mv … ~/.Trash/`.

### 5. Validate all

- **Task ID**: validate-all
- **Depends On**: confirm-ephemeral-runtime, author-implementation-review-skill, modify-build-command, integration-forward-test
- **Assigned To**: runtime-scout
- **Agent Type**: general-purpose
- **Parallel**: false
- Run all validation commands below.
- Verify every Acceptance Criterion is met; report any gaps loudly (do not mark complete with
  skipped checks).

## Acceptance Criteria

- `.agents/skills/implementation-review/SKILL.md` exists at the Codex-discoverable repo-level
  path, passes `quick_validate.py`, has `name: implementation-review`, a trigger-loaded
  angle-bracket-free `description`, and a body encoding the inputs, the run-validation +
  static-review procedure, the five-category blocking finding bar, the final-message output
  contract, and the never-write-files / never-edit-source rules.
- Running the documented `codex exec … -o <scratch>` invocation on a fixture plan produces a final
  message captured to `<scratch>` whose first line matches
  `^### Round [0-9]+ — Verdict: (approved|changes-requested)$`, includes a `Validation:` pass/fail
  block, and leaves the repo untouched — a `git status --porcelain --untracked-files=all` snapshot
  is identical before and after the run (no edited tracked files and no added untracked files).
- `.claude/commands/build.md` contains: a Workflow step invoking the loop after implementation; a
  "## Codex Implementation Review Loop" section documenting the precondition/graceful-skip, the
  verbatim `codex exec` invocation (`-o` capture, `-s workspace-write`, `-C`, named skill, round
  N), the verdict grep, the max-2-round fix cadence, the never-edit-source rule, and the outcome +
  validation summary in the Report. It passes `validate_command.py`.
- The graceful-skip path is demonstrated: with Codex unavailable, the documented loop skips, the
  Report records the note, and the build still completes.
- The ephemeral channel is proven: the verdict is read from the `-o` captured file (not stdout),
  and no repo files are added by the review.
- `plan-w-team` and the `plan.md` template are unchanged (the loop lives only in `build.md`).

## Validation Commands

Execute these commands to validate the task is complete:

- `uv run python "$HOME/.codex/skills/.system/skill-creator/scripts/quick_validate.py" .agents/skills/implementation-review` — Codex skill frontmatter/naming valid.
- `test -f .agents/skills/implementation-review/SKILL.md && grep -q '^name: implementation-review' .agents/skills/implementation-review/SKILL.md` — skill exists with correct name.
- `cd .claude/skills/meta-commands && uv run --with pyyaml python scripts/validate_command.py ../../commands/build.md` — modified command passes the house validator.
- `grep -qi 'codex implementation review' .claude/commands/build.md && grep -q 'implementation-review' .claude/commands/build.md` — loop section + skill reference present in build.md.
- Fixture loop check (integration task): run the documented `codex exec … -o "$TMPDIR/cap.md"` on a real plan, then `grep -E '^### Round [0-9]+ — Verdict: (approved|changes-requested)$' "$TMPDIR/cap.md"`, and compare `git status --porcelain --untracked-files=all` before vs after to prove no repo files were edited or added by the review.
- `git diff --name-only -- .claude/commands/plan-w-team.md` — empty (plan-w-team unchanged).
- `command -v codex` — availability probe used by the graceful-skip path.

## Notes

- **Reuse, don't re-derive.** The Codex runtime facts (discovery path, write flag, verdict regex,
  angle-bracket rule) are already proven in `specs/codex-spec-review-gate/runtime-notes.md`. Phase
  1 only confirms the new wrinkle: the ephemeral `-o` final-message capture.
- **Ephemeral by design.** Codex writes NOTHING into the repo — its review is its final CLI
  message, captured to the session scratchpad. The durable trail is the `/build` Report.
- **Safety:** never `rm -rf`; use `mv … ~/.Trash/` (AGENTS.md). Python via `uv`, JS/TS via `bun`.
  Pass model aliases (`opus`/etc.). Full-width Rich panels if any are used.
- **Fail loud:** a skipped Codex round, a rejected finding, a failing validation command, or a
  2-round non-approval must be surfaced in the Report, never silently dropped.
- **Workspace-write is for validation only.** Codex is granted `-s workspace-write` so it can run
  the plan's Validation Commands; the skill forbids it from editing source or writing review
  files. Phase 3 verifies the repo is untouched by the review.

## Codex Findings

_Pending Codex review. Codex-owned (the spec-review skill); Claude must not edit this section._

### Round 1 — Verdict: changes-requested

- **The no-write/no-edit verification misses untracked files.** The plan requires Codex to write
  no repo files and edit no source, but Phase 3 and the fixture validation rely on `git diff` /
  `git diff --stat`, which do not detect newly created untracked files. Recommend: update Phase 3
  and the "Fixture loop check" Validation Command to capture and compare
  `git status --porcelain --untracked-files=all` before and after each review run, so added files
  as well as edits are detected.
- **The plan contradicts the locked Python tooling rule.** `decisions.md` assumption A5 and the
  plan Notes require Python via `uv`, but Step 2 and the Validation Commands invoke
  `python3 "$HOME/.codex/skills/.system/skill-creator/scripts/quick_validate.py"` directly.
  Recommend: change those quick-validate instructions to a `uv`-wrapped Python invocation in
  Step 2 and the Validation Commands section.

### Round 2 — Verdict: approved

The spec meets the blocking-issue bar with no blocking findings this round.
