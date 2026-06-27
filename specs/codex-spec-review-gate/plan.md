# Plan: Codex Spec-Review Gate for plan-w-team

## Task Description

Extend the `plan-w-team` workflow with a Codex verification step. After Claude finishes
drafting a plan (`specs/<plan-name>/plan.md` + `decisions.md`) and before emitting the
final report, an automated loop hands the spec to Codex for review. Codex writes its
review into a dedicated, Codex-owned `## Codex Findings` section of `plan.md`; Claude
reads the findings, enhances the rest of the plan where warranted, and re-submits to
Codex. The cycle repeats until Codex approves or a 2-round cap is reached.

The reviewer is delivered as a **Codex Skill** named `spec-review` (OpenAI deprecated
custom prompts in favor of Skills). It lives repo-level at `.agents/skills/spec-review/`,
is version controlled, and is invoked non-interactively via `codex exec`. The gate runs
on every `plan-w-team` run but skips gracefully — with a recorded note — when the Codex
CLI is unavailable.

## Objective

When complete: a fresh `plan-w-team` run drafts the spec, automatically runs a max-2-round
Codex review loop that writes verdicts + findings into a Codex-owned `## Codex Findings`
section of `plan.md`, lets Claude refine the rest of the plan between rounds, and finishes
by reporting the verification outcome (approved at round N / proceeded without approval /
skipped) — with the loop fully documented in `plan-w-team.md` and the `spec-review` Codex
Skill checked into the repo and validated.

## Requirements & Decisions

- **Codex Skill, not a custom prompt.** Deliver `.agents/skills/spec-review/SKILL.md`
  (repo-level, version controlled) per OpenAI's current Skills format; custom prompts are
  deprecated. Full record in `decisions.md`.
- **Codex-owned findings section.** `plan.md` gains a `## Codex Findings` section that
  Claude scaffolds empty and **never edits**; only Codex writes there. Each round Codex
  appends `### Round N — Verdict: approved|changes-requested` + that round's findings.
- **Automated, capped loop.** Run via `codex exec` after the spec is drafted and before
  the report. Max 2 Codex rounds; approve-early exits; if still unapproved after Round 2,
  Claude applies a final fix pass and proceeds anyway, recording the non-approval.
- **Always-on with graceful skip.** Runs every time; if the Codex CLI is unavailable,
  skip with a warning (→ `/codex:setup`) and a note in `decisions.md`.

## Problem Statement

`plan-w-team` currently ships a plan straight from Claude's draft to the final report with
no independent review. Specs can carry missing requirements, infeasible or mis-ordered
steps, untestable acceptance criteria, or unflagged risks that only surface during
`/build`. There is no second set of eyes before execution and no recorded review trail.

## Solution Approach

Insert an automated Claude↔Codex review loop as the last planning step. A repo-level Codex
Skill (`spec-review`) encodes the review contract: read the drafted spec, judge it against
a blocking-issue finding bar, and append a per-round verdict + findings block into the
Codex-owned `## Codex Findings` section of `plan.md` (editing nothing else). `plan-w-team`
drives the loop with `codex exec`: render the invocation, run Codex, grep the latest
`Verdict:` line, and either finish (approved) or apply warranted fixes to the plan body and
re-run — capped at 2 rounds. A precondition check makes the gate skip gracefully when Codex
is absent. The file is partitioned by writer (Claude owns the plan body, Codex owns the
findings section), so the two never collide.

## Relevant Files

Use these files to complete the task:

- `.claude/commands/plan-w-team.md` — the command to modify: add the `## Codex Findings`
  template section + Codex-owned/never-edit note, insert the Codex Verification phase into
  the Workflow, add a "Codex Verification Loop" section documenting the mechanics, and add
  the verification outcome to the Decision Log Format + Report.
- `.claude/skills/meta-commands/SKILL.md` + `scripts/validate_command.py` — house standard
  and validator for the modified command (run after editing).
- `~/.codex/skills/.system/skill-creator/SKILL.md` — Codex's native skill-authoring guide
  and its `scripts/init_skill.py` / `scripts/quick_validate.py`; follow for the new skill.
- `~/.codex/config.toml` — confirms this repo is `trust_level = "trusted"` (enables
  non-interactive write-capable `codex exec`).
- `specs/grilling-into-plan-w-team/plan.md` — an existing real spec usable as the
  integration fixture (copy to scratch, add an empty Codex Findings section, run the loop).
- `.skill-lock.json` (repo root) — pre-existing skill-related state; inspect during the
  foundation task, do not delete.

### New Files

- `.agents/skills/spec-review/SKILL.md` — the Codex Skill (final path pending foundation
  verification; see Assumption A1 in `decisions.md`). Reviews a plan-w-team spec and writes
  the per-round verdict + findings into `## Codex Findings`.
- `.agents/skills/spec-review/agents/openai.yaml` — optional Codex UI metadata, if
  `init_skill.py` generates it.
- `specs/codex-spec-review-gate/runtime-notes.md` — foundation-task output: verified
  discovery path, `codex exec` write flag, and explicit-invocation syntax for tasks 2–4.

## Implementation Phases

### Phase 1: Foundation

Empirically resolve the Codex runtime unknowns (Assumptions A1–A3) before writing the
skill or the loop: the exact repo-level skill **discovery path** for Codex v0.142.3
(`.agents/skills` per docs vs `~/.codex/skills`/`$CODEX_HOME/skills` per the installed
`skill-creator`), the `codex exec` **write flag** that permits editing files in this
trusted repo, and the **explicit-invocation syntax** that reliably triggers a named skill
under `codex exec`. Inspect `.skill-lock.json`. Record findings in `runtime-notes.md`.

### Phase 2: Core Implementation

Two parallel tracks, both consuming `runtime-notes.md`:

- **Author the `spec-review` Codex Skill** at the verified path, following `skill-creator`
  conventions, encoding the finding bar, verdict contract, write-into-section rule, and
  never-touch-the-rest rule. Validate with `quick_validate.py`.
- **Modify `plan-w-team.md`**: add the Codex Findings template section + never-edit note,
  the Codex Verification workflow phase, the documented loop mechanics (codex exec,
  grep-verdict, max-2-rounds, graceful skip), and the outcome line in the Decision Log
  Format + Report. Validate with `validate_command.py`.

### Phase 3: Integration & Polish

End-to-end forward test: copy a real spec to a scratch fixture with an empty Codex Findings
section, run the actual `codex exec` loop, and verify Codex writes a greppable
`### Round N — Verdict:` block while leaving the rest of the file byte-identical (diff).
Forward-test the skill from a fresh Codex run told only "use `spec-review` on `<path>`".
Verify the graceful-skip path. Run all validators. Fix gaps.

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
  - Name: `codex-runtime-scout`
  - Role: Resolve the Codex runtime unknowns (discovery path, write flag, invocation
    syntax) and write `runtime-notes.md`. Also owns the final end-to-end validation.
  - Agent Type: `general-purpose` (no `.claude/agents/team/*.md` exists)
  - Resume: true
- Builder
  - Name: `skill-author`
  - Role: Author and validate the `spec-review` Codex Skill per Codex `skill-creator`
    conventions.
  - Agent Type: `general-purpose`
  - Resume: true
- Builder
  - Name: `command-editor`
  - Role: Modify `plan-w-team.md` (template section, verification phase, loop docs, report)
    and validate it with the meta-commands validator.
  - Agent Type: `general-purpose`
  - Resume: true

## Step by Step Tasks

- IMPORTANT: Execute every step in order, top to bottom. Each task maps directly to a `TaskCreate` call.
- Before you start, run `TaskCreate` to create the initial task list that all team members can see and execute.

### 1. Verify Codex Runtime

- **Task ID**: verify-codex-runtime
- **Depends On**: none
- **Assigned To**: codex-runtime-scout
- **Agent Type**: general-purpose
- **Parallel**: false
- Determine the repo-level skill discovery path Codex v0.142.3 actually scans: test
  `.agents/skills/` vs `~/.codex/skills/` / `$CODEX_HOME/skills`; consult `codex` help,
  `codex doctor`, and `~/.codex/skills/.system/skill-creator/SKILL.md`. If repo-level
  `.agents/skills` is unsupported, define the fallback (repo-canonical copy + user-level
  install step) and FLAG it loudly.
- Determine the minimal `codex exec` flag(s) that allow writing a file in this trusted
  repo (e.g. `--full-auto` or `-c sandbox_mode=workspace-write`), by running a throwaway
  `codex exec` that edits a scratch file and confirming the write lands.
- Determine the explicit-invocation syntax that reliably triggers a named skill under
  `codex exec` (e.g. `$spec-review` vs "use the spec-review skill on <path>").
- Inspect `.skill-lock.json` in the repo root; note its purpose, do not modify it.
- Write all findings to `specs/codex-spec-review-gate/runtime-notes.md` for tasks 2–4.

### 2. Author the spec-review Codex Skill

- **Task ID**: author-spec-review-skill
- **Depends On**: verify-codex-runtime
- **Assigned To**: skill-author
- **Agent Type**: general-purpose
- **Parallel**: true
- Initialize the skill at the verified path (prefer `init_skill.py` from
  `~/.codex/skills/.system/skill-creator/scripts/`; else hand-create
  `.agents/skills/spec-review/SKILL.md`). Skill `name: spec-review`.
- Write a tight, trigger-loaded `description` (front-load: "Review a plan-w-team
  implementation spec / plan.md before execution; write Codex Findings + verdict …").
- Write the body (imperative, concise, < 500 lines): inputs = the spec path (+ sibling
  `decisions.md` for context); a blocking-issue finding bar (missing/contradictory
  requirements, infeasible or mis-ordered steps, untestable acceptance criteria,
  security/data risks, scope drift — no style nits); grounded findings only.
- Encode the OUTPUT CONTRACT exactly: append under the spec's `## Codex Findings` section a
  block headed `### Round N — Verdict: approved` or `### Round N — Verdict: changes-requested`
  (N = highest existing round + 1; `approved` only when no blocking findings remain), with
  one bullet per finding carrying a concrete recommendation. Edit NOTHING else in `plan.md`.
- Validate with `quick_validate.py`; fix all reported issues.

### 3. Modify plan-w-team command

- **Task ID**: modify-plan-w-team
- **Depends On**: verify-codex-runtime
- **Assigned To**: command-editor
- **Agent Type**: general-purpose
- **Parallel**: true
- In the **Plan Format** template, add a final `## Codex Findings` section seeded with
  `_Pending Codex review. Codex-owned (the spec-review skill); Claude must not edit this
section._`, and add an Instructions bullet forbidding Claude from editing it.
- In the **Workflow**, insert a "Codex Verification" phase between Save Plan and Save &
  Report (renumber accordingly).
- Add a **"## Codex Verification Loop"** section documenting: precondition check
  (`command -v codex` + auth) → graceful skip (warn → `/codex:setup`, record skip in
  `decisions.md`, continue); else the `codex exec` invocation (using the verified write
  flag + skill invocation from `runtime-notes.md`); grep the latest `Verdict:` line; the
  max-2-round cadence (approve-early; on `changes-requested`, Claude edits only the plan
  body, records any rejected findings + rationale in `decisions.md`; after Round 2 still
  unapproved, apply a final pass and proceed, recording non-approval).
- Add the verification outcome (approved at round N / proceeded without approval / skipped)
  to the **Decision Log Format** and the **Report** template.
- Validate: `cd .claude/skills/meta-commands && uv run --with pyyaml python scripts/validate_command.py ../../commands/plan-w-team.md`.

### 4. Integration forward-test

- **Task ID**: integration-forward-test
- **Depends On**: author-spec-review-skill, modify-plan-w-team
- **Assigned To**: codex-runtime-scout
- **Agent Type**: general-purpose
- **Parallel**: false
- Copy `specs/grilling-into-plan-w-team/plan.md` to a scratch fixture and append an empty
  `## Codex Findings` section.
- Run the real `codex exec` loop invoking `spec-review` on the fixture. Verify: (a) a
  `### Round 1 — Verdict: <approved|changes-requested>` block is appended under
  `## Codex Findings`; (b) the verdict line matches `grep -E '^### Round [0-9]+ — Verdict: (approved|changes-requested)$'`;
  (c) the rest of the fixture is byte-identical before/after (diff only inside the section).
- Forward-test the skill from a FRESH Codex run told only "use `spec-review` on `<path>`"
  (no leaked expectations) to confirm it triggers and honors the contract.
- Verify the graceful-skip path: with `codex` masked/unavailable, confirm the documented
  loop skips and records the note (dry-run the documented steps).

### 5. Validate all

- **Task ID**: validate-all
- **Depends On**: verify-codex-runtime, author-spec-review-skill, modify-plan-w-team, integration-forward-test
- **Assigned To**: codex-runtime-scout
- **Agent Type**: general-purpose
- **Parallel**: false
- Run all validation commands below.
- Verify every Acceptance Criterion is met; report any gaps loudly (do not mark complete
  with skipped checks).

## Acceptance Criteria

- `.agents/skills/spec-review/SKILL.md` exists at the Codex-discoverable path (or the
  flagged fallback), passes `quick_validate.py`, and has `name: spec-review` + a
  trigger-loaded `description`.
- Running `codex exec` with the `spec-review` skill on a fixture spec appends a
  `### Round N — Verdict: approved|changes-requested` block under `## Codex Findings` and
  leaves the rest of the file byte-identical (verified by diff).
- `.claude/commands/plan-w-team.md` contains: the `## Codex Findings` template section with
  the Codex-owned/never-edit note + Instructions bullet; a Codex Verification phase before
  the Report; a documented max-2-round `codex exec` loop with graceful skip and verdict
  grep; and the verification outcome in the Decision Log Format + Report. It passes
  `validate_command.py`.
- The graceful-skip path is demonstrated: with Codex unavailable, the documented loop skips
  and records a note in `decisions.md`; planning still completes.
- The never-edit rule is documented in `plan-w-team.md` and enforced by the skill (Codex
  writes only the `## Codex Findings` section).
- `runtime-notes.md` records the verified discovery path, write flag, and invocation syntax.

## Validation Commands

Execute these commands to validate the task is complete:

- `cd .claude/skills/meta-commands && uv run --with pyyaml python scripts/validate_command.py ../../commands/plan-w-team.md` — modified command passes the house validator.
- `python3 "$HOME/.codex/skills/.system/skill-creator/scripts/quick_validate.py" .agents/skills/spec-review` — Codex skill frontmatter/naming valid (confirm exact script path in foundation task).
- `test -f .agents/skills/spec-review/SKILL.md && grep -q '^name: spec-review' .agents/skills/spec-review/SKILL.md` — skill exists with correct name.
- `grep -q '## Codex Findings' .claude/commands/plan-w-team.md && grep -qi 'codex verification' .claude/commands/plan-w-team.md` — template section + verification phase present.
- Fixture loop check (run in foundation/integration tasks): `codex exec` against the scratch fixture, then `grep -E '^### Round [0-9]+ — Verdict: (approved|changes-requested)$' <fixture>` and a `diff` proving only the Codex Findings section changed.
- `codex --version` — availability probe used by the graceful-skip path.

## Notes

- **Discovery-path risk (A1).** Public docs say repo-level `.agents/skills`; the installed
  v0.142.3 `skill-creator` references `$CODEX_HOME/skills` (`~/.codex/skills`). The
  foundation task resolves this empirically. If repo-level discovery is unsupported, ship a
  repo-canonical copy + a user-level install step and FLAG it — never ship an
  undiscoverable skill silently.
- **Write capability.** The repo is `trust_level = "trusted"` in `~/.codex/config.toml`;
  use the minimal `codex exec` flag (A2) that lets Codex edit only `plan.md`.
- **Safety:** never `rm -rf`; use `mv … ~/.Trash/` (AGENTS.md). Inspect, don't delete,
  `.skill-lock.json`. Python via `uv`, JS/TS via `bun`. Pass model aliases (`opus`/etc.).
- **Fail loud:** a skipped Codex round, a rejected finding, or a 2-round non-approval must
  be recorded in `decisions.md`, not silently dropped.
