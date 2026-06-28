# Plan: Refactor plan-w-team to SDD four-file templates + enhance spec-review

## Task Description

`/plan-w-team` today is a ~450-line flat command (`.claude/commands/plan-w-team.md`) that
hard-codes its entire **Plan Format** and **Decision Log Format** inline and emits **two**
files per run (`plan.md` + `decisions.md`). Four spec-driven templates have already been
drafted under `specs/_templates/` but are not yet wired into anything.

This plan does five things:

1. **Finalize the four SDD templates** in `specs/_templates/` (`spec.md`, `decisions.md`,
   `tasks.md`, `acceptance-criteria.md` — the last renamed from the typo'd
   `accepance-criteria.md`), filling the placeholder sections and normalizing structure.
2. **Refactor `/plan-w-team`** to delete the hard-coded formats, reference the templates,
   carry four output-file variables, write four files per run, retarget the Codex loop at
   `spec.md`, and flip `Status:` to `Approved` after a Codex `approved` verdict.
3. **Add a blocking Stop hook** (bash, exit 2) that verifies the four files exist and that
   each contains its required `##` sections, wired in the command's frontmatter.
4. **Enhance the `spec-review` skill** to read all four files, fold in a five-category review
   lens + calibration + advisory recommendations, while **keeping** its load-bearing
   `### Round N — Verdict:` / `## Codex Findings` output contract.
5. **Rename `plan.md` → `spec.md`** across every downstream consumer (`build.md`, `ship.md`,
   `implementation-review` skill, `task-tools.md`) so `/build` and the build-phase review
   keep working.

## Objective

When this plan is complete, `/plan-w-team` produces a four-file spec-driven plan folder
(`spec.md` / `decisions.md` / `tasks.md` / `acceptance-criteria.md`) sourced entirely from
`specs/_templates/` with **zero** hard-coded format in the command; a blocking Stop hook
guarantees every run leaves a complete folder; `spec-review` reviews all four files and still
emits a `Round N` verdict the Codex loop can read; and `/build` resolves and reads `spec.md`
with no dangling `plan.md` references anywhere in the workflow.

## Requirements & Decisions

Full record in `decisions.md`. The load-bearing ones:

- **Full rename, no half-measures**: `spec.md` becomes canonical across `plan-w-team`,
  `spec-review`, `build`, `ship`, `implementation-review`, and `task-tools` in this same plan
  — `/build` must never break.
- **Stays a Command**: `/plan-w-team` remains a slash command; the Stop hook lives in its
  frontmatter (never auto-fires).
- **Review contract preserved**: `spec-review` keeps `### Round N — Verdict: approved|changes-requested`
  under `## Codex Findings`; the five-category lens is folded _into_ the finding bar, not
  swapped for the reference's `Status:` format (which would break the loop's grep).
- **spec.md is the single lifecycle record**: it owns `## Tracking`, `## Codex Findings`
  (Codex-owned) and `## Codex Verification` (Claude-owned outcome). `decisions.md` stays the
  lean, immutable grilling record (no Tracking, no Codex Verification).

## Tracking

<!-- Recorded by /plan-w-team. The Issue field is the SINGLE SOURCE OF TRUTH /build reads — /build NEVER re-derives #N (e.g. by parsing the mangled local branch name). -->

- Issue: #4
- Branch: chore/4-plan-w-team-sdd-refactor
- Worktree: /Users/ringo/Desktop/ai-native-startup/.claude/worktrees/chore+4-plan-w-team-sdd-refactor

## Problem Statement

The hard-coded formats inside `plan-w-team.md` make the command long, brittle, and the single
source of truth for plan structure — so structure can't evolve without editing the command,
and the freshly-drafted `specs/_templates/` files are dead weight. The output is also flat
(everything in `plan.md`), which mixes the _what/why_, the _how/who_, the _done definition_,
and the _grilling record_ into one document, working against spec-driven development and making
targeted review (e.g. "is the acceptance criteria testable?") harder. There is no automated
guarantee that a planning run actually produced a complete folder, and `spec-review` only reads
two of the four artifacts.

## Solution Approach

Externalize structure into `specs/_templates/` and make the command a thin orchestrator that
_copies + fills_ those templates. Split the plan into four spec-driven files so each artifact
has one concern, with `spec.md` as the master lifecycle record. Add a command-scoped Stop hook
as a completeness gate. Teach `spec-review` to read the whole folder and apply a richer review
lens without changing the machine-readable verdict the Codex loop depends on. Do the
`plan.md → spec.md` rename everywhere in one pass so nothing downstream breaks.

Alternative considered and rejected: keep `plan.md` as the canonical name and only add the two
new sibling files. Rejected because it contradicts the explicit `spec.md` rename and leaves the
filename semantically wrong (it's a spec, not a plan).

## Relevant Files

Use these files to complete the task:

- `.claude/commands/plan-w-team.md` — the command to refactor: delete the hard-coded Plan
  Format + Decision Log Format, add four output variables, reference `specs/_templates/`,
  retarget the Codex loop at `spec.md`, add the Status flip, wire the Stop hook in frontmatter.
- `specs/_templates/spec.md` — finalize (Status enum, `## Non-Goals`, `## Codex Verification`,
  fleshed Edge Cases/References, fixed Self Validation checkboxes).
- `specs/_templates/tasks.md` — finalize (back-link, `Satisfies:` traceability field).
- `specs/_templates/decisions.md` — finalize (lean: keep Summary/Resolved/Assumptions/Open;
  add per-entry structure; explicitly NO Tracking / NO Codex Verification).
- `specs/_templates/accepance-criteria.md` — **rename** to `acceptance-criteria.md` and
  finalize (AC ids, per-command→AC mapping).
- `.agents/skills/spec-review/SKILL.md` — enhance: read four files, five-category lens,
  advisory recommendations, keep the Round-N contract.
- `.claude/commands/build.md` — rename `plan.md`→`spec.md` in resolution + Tracking read.
- `.claude/commands/ship.md` — rename `plan.md`→`spec.md` references.
- `.agents/skills/implementation-review/SKILL.md` — rename `plan.md`→`spec.md` references.
- `.claude/rules/task-tools.md` — rename `plan.md`→`spec.md` references.
- `.claude/settings.local.json` — reference for hook-wiring pattern (Stop hook is wired in the
  command frontmatter, not here; this file shows the existing PreToolUse pattern).
- `.claude/hooks/block-coauthor-trailer.sh` — bash hook pattern to mirror (exit-2 deny).

### New Files

- `.claude/hooks/check-spec-completeness.sh` — the blocking Stop hook (bash, exit 2). Full
  content in Task 3.
- `specs/_templates/acceptance-criteria.md` — created via `git mv` from the typo'd file.

## Implementation Phases

### Phase 1: Foundation

Finalize the four templates (Task 1). Every other change references the templates' canonical
section names, so they are locked first.

### Phase 2: Core Implementation

Refactor the command (Task 2), add the Stop hook (Task 3), enhance `spec-review` (Task 4) — the
three behavioral changes — and rename downstream consumers (Task 5). Tasks 3/4/5 are independent
and parallel; Task 2 wires the hook so it waits on Task 3.

### Phase 3: Integration & Polish

Run the validation suite (Task 6): confirm no `plan.md` references remain, the hook blocks on a
deliberately-incomplete folder, the command references the templates, and `spec-review` reads
all four files while keeping the Round-N line.

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
  - Name: `builder-templates`
  - Role: Finalize the four SDD templates in `specs/_templates/` (incl. the `git mv` rename)
  - Agent Type: `general-purpose`
  - Resume: true
- Builder
  - Name: `builder-command`
  - Role: Refactor `.claude/commands/plan-w-team.md` (de-hardcode, four variables, Codex loop →
    spec.md, Status flip, wire the Stop hook in frontmatter)
  - Agent Type: `general-purpose`
  - Resume: true
- Builder
  - Name: `builder-hook`
  - Role: Author + wire the blocking Stop hook `check-spec-completeness.sh`
  - Agent Type: `general-purpose`
  - Resume: true
- Builder
  - Name: `builder-skill`
  - Role: Enhance `.agents/skills/spec-review/SKILL.md` (four-file input, five-category lens,
    keep Round-N contract)
  - Agent Type: `general-purpose`
  - Resume: true
- Builder
  - Name: `builder-downstream`
  - Role: Rename `plan.md`→`spec.md` across `build.md`, `ship.md`, `implementation-review`,
    `task-tools.md`
  - Agent Type: `general-purpose`
  - Resume: true
- Validator
  - Name: `validator`
  - Role: Run all Validation Commands and verify every acceptance criterion
  - Agent Type: `general-purpose`
  - Resume: true

## Step by Step Tasks

- IMPORTANT: Execute every step in order, top to bottom. Each task maps directly to a `TaskCreate` call.
- Before you start, run `TaskCreate` to create the initial task list that all team members can see and execute.

### 1. Finalize the four SDD templates

- **Task ID**: finalize-templates
- **Depends On**: none
- **Assigned To**: builder-templates
- **Agent Type**: general-purpose
- **Parallel**: false
- **Satisfies**: AC1, AC2
- `git mv specs/_templates/accepance-criteria.md specs/_templates/acceptance-criteria.md` (fix the typo via rename, preserving history).
- Overwrite each of the four template files with the **final content** below (verbatim).
- Confirm every file ends with a trailing newline and that the conditional-section HTML comments are preserved.

**`specs/_templates/spec.md` (final):**

````md
# Spec: <task name>

- **Owner:** <github handle of the human owner, e.g. @ringo>
- **Status:** Drafted for Review
  <!-- Lifecycle, set by /plan-w-team: Drafted for Review → Approved (after a Codex `approved`
       verdict) → Needs Human Review (still changes-requested after 2 Codex rounds). One value only. -->

## Task Description

<describe the task in detail, in plain language, based on the prompt — what is being asked and the context a builder needs>

## Objective

<one or two sentences stating what is true when this plan is complete — the definition of success, observable not aspirational>

## Non-Goals

<bullet list of what this plan explicitly will NOT do — the scope fence. Pull the out-of-scope items from decisions.md so scope drift is visible in the spec itself. Write "None" only if genuinely none.>

<!-- Include ## Problem Statement and ## Solution Approach only when task_type is feature OR complexity is medium/complex; omit for simple chores. -->

## Problem Statement

<define the specific problem or opportunity this addresses — why it's worth doing now>

## Solution Approach

<the chosen technical approach at a high level and how it satisfies the Objective; note the main alternative considered and why it lost>

## Requirements & Decisions

<the 2-4 most important LOCKED decisions/constraints a builder must honor, as bullets. A summary — the full grilling record lives in decisions.md. Each bullet: the decision + a short why.>

## Tracking

<!-- Recorded by /plan-w-team. The Issue field is the SINGLE SOURCE OF TRUTH /build reads — /build
     NEVER re-derives #N from the mangled local branch name. spec.md is the single home for this
     block; decisions.md does not duplicate it. -->

- **Issue:** <#N, or the literal `none — gh unavailable` when no issue was created>
- **Branch:** <intended convention branch `<type>/<N>-<slug>`, or `<type>/<slug>` with no #N>
- **Worktree:** <absolute worktree path>

## Relevant Files

Use these files to complete the task:

<bullet list of existing files the build will touch, each with a one-line why. Add an h3 "### New Files" subsection for files to be created, each with its purpose.>

## Edge Cases

<enumerate the boundary/failure conditions the build must handle: empty or missing input, oversized input, concurrent/duplicate runs, partial failure, an unavailable dependency (gh/codex/network), idempotency on re-run. One bullet each, stating the expected behavior.>

## Red Flags

<anti-patterns signalling the plan is being skipped or scope is drifting. Keep these standing examples; add task-specific ones:>

- Starting to write code without any written requirements
- Asking "should I just start building?" before clarifying what "done" means
- Implementing features not mentioned in any spec or task list
- Making architectural decisions without documenting them
- Skipping the spec because "it's obvious what to build"

## Notes

<optional: extra context, dependencies, follow-ups. New libs: specify with `uv add <pkg>` (Python) or `bun add <pkg>` (JS/TS).>

## Codex Findings

<!-- CODEX-OWNED. Written only by the spec-review skill (one `### Round N — Verdict: …` block per
     round). Claude must NEVER edit this section. -->

_Pending Codex review._

## Codex Verification

<!-- CLAUDE-OWNED. The outcome summary Claude records after the Codex loop. -->

- **Outcome:** <approved at round N | proceeded without full approval after 2 rounds | skipped — Codex unavailable>
- **Rejected findings:** <any Codex finding Claude chose not to act on, each with a one-line rationale; "none" if all warranted findings were applied>

## References

<a tree of the sibling plan files and their purpose, so the four files trace to each other:>

```
specs/<plan-name>/
├── spec.md                 # this file — what & why, tracking, review record
├── decisions.md            # grilling record: resolved decisions, assumptions, out-of-scope
├── tasks.md                # how & who: phases, team, step-by-step tasks
└── acceptance-criteria.md  # done: acceptance criteria + validation commands
```

## Self Validation

- [ ] Objective, Task Description, and Non-Goals are filled in (no placeholders left)
- [ ] Requirements trace to tasks in tasks.md and to checks in acceptance-criteria.md
- [ ] Acceptance criteria are specific and testable
- [ ] All four files exist under specs/<plan-name>/ and are saved in the repository
- [ ] Codex has reviewed the spec and Status reflects the outcome
````

**`specs/_templates/tasks.md` (final):**

```md
# Tasks: <task name>

> Execution plan for [spec.md](./spec.md). Owner and scope are defined there; this file is how & who.

<!-- Include ## Implementation Phases only when complexity is medium/complex; omit for simple tasks. -->

## Implementation Phases

### Phase 1: Foundation

<foundational work everything else depends on — scaffolding, shared types, config>

### Phase 2: Core Implementation

<the main implementation work that delivers the Objective>

### Phase 3: Integration & Polish

<wiring, end-to-end tests, docs, and final cleanup>

## Team Orchestration

- You operate as the team lead and orchestrate the team to execute the plan.
- IMPORTANT: You NEVER operate directly on the codebase. You use the `Task*` tools to deploy team
  members to build, validate, test, and deploy. Your job is to direct, not to build.
- Keep the shared task list (TaskCreate/TaskUpdate) as the single source of truth for who is doing
  what; verify each task on the board before marking it complete.
- Note the session id / name of each team member — that is how you reference them.

## Team Members

<one entry per member you'll deploy:>

- **Builder**
  - **Name:** <unique name so you and others can reference THIS builder; multiple builders each get a distinct name>
  - **Role:** <the single focus this builder owns>
  - **Agent Type:** <a subagent from .claude/agents/team/*.md, or `general-purpose`>
  - **Resume:** <default true — continue with the same context; false to start fresh>

## Step by Step Tasks

- Execute every step in order, top to bottom. Each task maps directly to one `TaskCreate` call.
- Before starting, run `TaskCreate` for every task below so all team members can see the board.
- Each task names the acceptance criteria (from acceptance-criteria.md) it satisfies, so work traces to "done".

### 1. <First Task Name>

- **Task ID:** <unique kebab-case id, e.g. `setup-templates`>
- **Depends On:** <Task ID(s), or "none">
- **Assigned To:** <team member name>
- **Agent Type:** <subagent type, or `general-purpose`>
- **Parallel:** <true if it can run alongside others, false if sequential>
- **Satisfies:** <acceptance criteria id(s) from acceptance-criteria.md, e.g. AC1, AC2>
- <specific action>
- <specific action>

### 2. <Second Task Name>

- **Task ID:** <unique-id>
- **Depends On:** <previous Task ID>
- **Assigned To:** <team member name>
- **Agent Type:** <subagent type, or `general-purpose`>
- **Parallel:** <true/false>
- **Satisfies:** <acceptance criteria id(s)>
- <specific action>

### N. Validate Everything

- **Task ID:** validate-all
- **Depends On:** <all previous Task IDs>
- **Assigned To:** <validator team member>
- **Agent Type:** <validator agent, or `general-purpose`>
- **Parallel:** false
- Run every command in acceptance-criteria.md → `## Validation Commands`.
- Verify each acceptance criterion is met.
```

**`specs/_templates/acceptance-criteria.md` (final):**

```md
# Acceptance Criteria: <task name>

> The definition of "done" for [spec.md](./spec.md). Every criterion is observable and testable, and
> every task in tasks.md should map to at least one criterion here.

## Acceptance Criteria

<numbered, testable criteria. Give each a stable id (AC1, AC2 …) so tasks.md can reference it. Each
must be checkable by a human or a command — no "feels fast", no "works well".>

- **AC1** — <specific, measurable outcome; what is true and how you'd observe it>
- **AC2** — <…>
- **AC3** — <…>

## Validation Commands

Run these to prove the criteria above. Map each command to the criteria it verifies.

<precise, copy-pasteable commands. Use `uv run …` for Python and `bun …` for JS/TS.>

- `<command>` — verifies <AC#>. <what a pass looks like>
- `<command>` — verifies <AC#>.
```

**`specs/_templates/decisions.md` (final):**

```md
# Decisions: <task name>

> The grilling record for [spec.md](./spec.md) — why the plan is the way it is. Lifecycle tracking and
> the Codex review record live in spec.md, NOT here; this file is the immutable decision history.

## Summary

<one paragraph: the agreed scope and the key choices, in plain language>

## Resolved Decisions

<one entry per locked decision from the grilling:>

- **Q:** <the question that was open>
  - **A:** <the decision>
  - **Why:** <the rationale / what it rules out>

## Assumptions

<every deferred "you decide" / accept-all item, made explicit so the build can challenge it:>

- <assumption — and what would invalidate it>

## Open Questions / Out of Scope

<deferred questions and explicit non-goals. The Non-Goals here feed spec.md's `## Non-Goals` section.>

- **Out of scope:** <excluded item>
- **Open question:** <unresolved item to revisit, and who owns it>
```

### 2. Refactor the /plan-w-team command

- **Task ID**: refactor-command
- **Depends On**: finalize-templates, add-stop-hook
- **Assigned To**: builder-command
- **Agent Type**: general-purpose
- **Parallel**: false
- **Satisfies**: AC3, AC4, AC7
- **Variables**: replace the two output variables with four, keeping `<plan-name>` kebab-case:
  - `SPEC_FILE: specs/<plan-name>/spec.md`
  - `DECISION_LOG: specs/<plan-name>/decisions.md`
  - `TASKS_FILE: specs/<plan-name>/tasks.md`
  - `ACCEPTANCE_FILE: specs/<plan-name>/acceptance-criteria.md`
  - add `TEMPLATES_DIR: specs/_templates/`
- **Delete the hard-coded formats**: remove the entire `## Plan Format` fenced block and the
  `## Decision Log Format` fenced block. Replace with a short `## Output Files` section that
  instructs: "Copy each template from `TEMPLATES_DIR`, fill every `<…>` micro-prompt and the
  required `##` sections, and save to the matching per-plan path. Do not invent structure — the
  templates are the single source of truth for section layout."
- **Map content to files** (so the planner knows what goes where): spec.md = what/why + Tracking
  - Codex records; tasks.md = phases/team/step-by-step tasks; acceptance-criteria.md = criteria +
    validation commands; decisions.md = grilling record only.
- **Retarget the Codex loop at `spec.md`**: in the `Codex Verification Loop` section, change
  `<SPEC_PATH>` from `specs/<plan-name>/plan.md` to `specs/<plan-name>/spec.md`; update the
  verdict grep to read `specs/<plan-name>/spec.md`; update the spec-review invocation prompt to
  say "review the four-file plan-w-team spec under `specs/<plan-name>/` (spec.md is the entry
  point)". The `## Codex Findings` section it appends to now lives in `spec.md`.
- **Add the Status flip**: after a Codex `approved` verdict, edit `spec.md`'s `Status:` line to
  `Approved`; if still `changes-requested` after 2 rounds, set it to `Needs Human Review`. Record
  this as a step in the loop. This honors the "update the status to approved" requirement.
- **Move the Codex Verification outcome to spec.md**: the loop writes the outcome summary +
  rejected findings into spec.md's Claude-owned `## Codex Verification` section (NOT decisions.md,
  NOT the Codex-owned `## Codex Findings`).
- **Wire the Stop hook** in the command frontmatter `hooks:` block (alongside the existing
  `PostToolUse` prettier hook):
  ```yaml
  Stop:
    - hooks:
        - type: command
          command: '"$CLAUDE_PROJECT_DIR"/.claude/hooks/check-spec-completeness.sh'
  ```
- **Update Workflow step 10** ("Save Plan") to write all four files, and update the `Report`
  block to list all four paths.
- Leave the Grilling Protocol, GitHub Issue Tracking, Publish & Per-Phase Tracking, and Skill
  Contracts sections intact except where they name `plan.md` (→ `spec.md`).

### 3. Add the blocking Stop hook

- **Task ID**: add-stop-hook
- **Depends On**: finalize-templates
- **Assigned To**: builder-hook
- **Agent Type**: general-purpose
- **Parallel**: true
- **Satisfies**: AC5, AC6
- Create `.claude/hooks/check-spec-completeness.sh`, `chmod +x` it, mirror the `set -euo pipefail`
  - exit-2-to-deny pattern from `block-coauthor-trailer.sh`.
- Behavior: identify the newest-modified `specs/*/` folder excluding `_templates`; verify the four
  files exist; verify each file contains its **required (unconditional)** `##` sections; on any
  gap print the specifics to stderr and `exit 2` (block). The hook is command-scoped, so a
  completed `/plan-w-team` run always has a target folder.
- Required (unconditional) sections per file — conditional sections are deliberately excluded so
  simple chores don't false-fail:
  - `spec.md`: Task Description, Objective, Non-Goals, Requirements & Decisions, Tracking,
    Relevant Files, Edge Cases, Red Flags, Codex Findings, Codex Verification, References,
    Self Validation. _(Excluded: Problem Statement, Solution Approach, Notes.)_
  - `tasks.md`: Team Orchestration, Team Members, Step by Step Tasks. _(Excluded: Implementation Phases.)_
  - `acceptance-criteria.md`: Acceptance Criteria, Validation Commands.
  - `decisions.md`: Summary, Resolved Decisions, Assumptions, Open Questions / Out of Scope.

**`.claude/hooks/check-spec-completeness.sh` (reference implementation):**

```bash
#!/usr/bin/env bash
# Stop hook for /plan-w-team: block the run from ending until the per-plan spec folder is complete.
# Two checks only: (1) all four files exist, (2) each file has its required '##' sections.
# Exit 2 => deny stop; stderr is fed back to Claude so it completes the gaps.
set -euo pipefail

root="${CLAUDE_PROJECT_DIR:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}"
specs="$root/specs"
[ -d "$specs" ] || exit 0   # no specs dir at all → nothing to gate

# Newest-modified plan folder, excluding the templates dir.
folder="$(find "$specs" -mindepth 1 -maxdepth 1 -type d ! -name '_templates' -exec stat -f '%m %N' {} + \
  | sort -rn | head -1 | cut -d' ' -f2-)"
[ -n "$folder" ] || { echo "Stop blocked: no plan folder found under specs/." >&2; exit 2; }

missing=""
check() {  # $1=file  $2=newline-separated required section headers
  local f="$folder/$1"
  if [ ! -f "$f" ]; then missing+=$'\n'"  - MISSING FILE: $1"; return; fi
  while IFS= read -r h; do
    [ -z "$h" ] && continue
    grep -qF "## $h" "$f" || missing+=$'\n'"  - $1: missing section '## $h'"
  done <<< "$2"
}

check spec.md "Task Description
Objective
Non-Goals
Requirements & Decisions
Tracking
Relevant Files
Edge Cases
Red Flags
Codex Findings
Codex Verification
References
Self Validation"

check tasks.md "Team Orchestration
Team Members
Step by Step Tasks"

check acceptance-criteria.md "Acceptance Criteria
Validation Commands"

check decisions.md "Summary
Resolved Decisions
Assumptions
Open Questions / Out of Scope"

if [ -n "$missing" ]; then
  { echo "Stop blocked: spec folder '$folder' is incomplete:"; echo "$missing";
    echo ""; echo "Complete the missing files/sections (compare against specs/_templates/), then stop again."; } >&2
  exit 2
fi
exit 0
```

> NOTE: `stat -f '%m %N'` is the BSD/macOS form (matches the `darwin` runtime). If portability to
> Linux is ever needed, swap to `stat -c '%Y %n'`. The builder should keep the macOS form to match
> the environment unless told otherwise.

### 4. Enhance the spec-review skill

- **Task ID**: enhance-spec-review
- **Depends On**: finalize-templates
- **Assigned To**: builder-skill
- **Agent Type**: general-purpose
- **Parallel**: true
- **Satisfies**: AC8, AC9
- Edit `.agents/skills/spec-review/SKILL.md`. **Keep the entire output contract unchanged**: the
  `### Round N — Verdict: approved|changes-requested` first line, the `## Codex Findings`
  append-only target, round-numbering, never-touch rule, and the orchestrator-only `gh` relay.
- **Inputs**: expand from `{plan.md, decisions.md}` to all four files. The entry point is
  `spec.md` (path given in the prompt); read the siblings `decisions.md`, `tasks.md`, and
  `acceptance-criteria.md` from the same folder. Append the verdict to `spec.md`'s `## Codex Findings`.
- **Finding bar**: keep the existing five blocking categories AND fold in the five-category review
  lens as the framing for _what to look for_ (do not replace the blocking bar):

  | Category     | What to look for                                                                                                                                     |
  | ------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
  | Completeness | TODOs, placeholders, unfilled `<…>` micro-prompts, "TBD", empty required sections across the four files                                              |
  | Consistency  | Internal contradictions; a step in tasks.md that conflicts with a locked decision in decisions.md; an acceptance criterion with no implementing task |
  | Clarity      | Requirements ambiguous enough to build the wrong thing                                                                                               |
  | Scope        | Focused on one plan; work that exceeds or contradicts decisions.md's Non-Goals / Out of Scope                                                        |
  | YAGNI        | Unrequested features, speculative over-engineering past the locked decisions                                                                         |

- **Calibration** (add verbatim, adapted): "Only flag issues that would cause real problems during
  implementation. A missing required section, a contradiction, or a two-way-ambiguous requirement
  are issues. Minor wording, stylistic preference, and 'this section is less detailed than that
  one' are not. Approve unless there are serious gaps that would lead to a flawed build."
- **Advisory recommendations**: under each `changes-requested` block, allow an optional
  `**Recommendations (advisory, non-blocking):**` bullet list — these never change the verdict and
  never block approval. Keep `approved` blocks to a single confirming line (no padded findings).
- Update the frontmatter `description` to mention it reviews the **four-file** spec (entry
  `spec.md`) rather than a single `plan.md`.

### 5. Rename plan.md → spec.md across downstream consumers

- **Task ID**: rename-downstream
- **Depends On**: finalize-templates
- **Assigned To**: builder-downstream
- **Agent Type**: general-purpose
- **Parallel**: true
- **Satisfies**: AC7
- `.claude/commands/build.md`: in the resolution order, change `specs/<TARGET>/plan.md` →
  `specs/<TARGET>/spec.md` (keep a fallback to legacy `plan.md` if a folder still has the old name,
  so old plans still build); update all `PLAN`/`plan.md` mentions and the `## Tracking` read to
  point at `spec.md`. Tracking is read from `spec.md` (consistent with the new single-home model).
- `.claude/commands/ship.md`: rename `plan.md` references to `spec.md`.
- `.agents/skills/implementation-review/SKILL.md`: rename `plan.md` references to `spec.md`
  (it reads `<PLAN_PATH>` + sibling `decisions.md`; the entry is now `spec.md`).
- `.claude/rules/task-tools.md`: rename the `plan.md` example references to `spec.md`.
- Do NOT touch historical `specs/*/plan.md` files from past plans (including THIS plan's own
  `plan.md`) — only the workflow docs/commands/skills change.

### 6. Validate everything

- **Task ID**: validate-all
- **Depends On**: finalize-templates, refactor-command, add-stop-hook, enhance-spec-review, rename-downstream
- **Assigned To**: validator
- **Agent Type**: general-purpose
- **Parallel**: false
- Run every command in the `Validation Commands` section below.
- Verify each acceptance criterion (AC1–AC9) is met; report any failure loudly (do not mark
  complete on a partial pass).

## Acceptance Criteria

- **AC1** — The four template files exist with correct names: `specs/_templates/{spec,decisions,tasks,acceptance-criteria}.md`, and the typo'd `accepance-criteria.md` is gone.
- **AC2** — `spec.md` template contains the Status enum, `## Non-Goals`, `## Codex Findings`, and `## Codex Verification`; `decisions.md` template contains **no** `## Tracking` and **no** `## Codex Verification`.
- **AC3** — `.claude/commands/plan-w-team.md` contains **no** hard-coded `## Plan Format` or `## Decision Log Format` fenced block, and references `specs/_templates/`.
- **AC4** — `plan-w-team.md` defines four output-file variables (`SPEC_FILE`, `DECISION_LOG`, `TASKS_FILE`, `ACCEPTANCE_FILE`) and the Codex loop + verdict grep target `spec.md`.
- **AC5** — `.claude/hooks/check-spec-completeness.sh` exists, is executable, and passes `bash -n`.
- **AC6** — The Stop hook exits 2 on a folder missing a file or a required section, and exits 0 on a complete folder (proven by the fixture test below).
- **AC7** — No `plan.md` reference remains in `plan-w-team.md`, `build.md`, `ship.md`, `spec-review/SKILL.md`, `implementation-review/SKILL.md`, or `task-tools.md` (legacy fallback string in build.md excepted and explicitly commented).
- **AC8** — `spec-review/SKILL.md` reads all four files (mentions `tasks.md` and `acceptance-criteria.md`) and includes the five-category lens table.
- **AC9** — `spec-review/SKILL.md` still defines the `### Round N — Verdict: approved|changes-requested` contract under `## Codex Findings`.

## Validation Commands

Execute these commands to validate the task is complete (run from the repo/worktree root):

- `ls specs/_templates/acceptance-criteria.md && ! ls specs/_templates/accepance-criteria.md 2>/dev/null` — AC1: renamed file present, typo gone.
- `for f in spec decisions tasks acceptance-criteria; do test -f "specs/_templates/$f.md" || echo "MISSING $f"; done` — AC1: all four exist.
- `grep -q '## Non-Goals' specs/_templates/spec.md && grep -q '## Codex Verification' specs/_templates/spec.md && ! grep -q '## Tracking' specs/_templates/decisions.md && ! grep -q '## Codex Verification' specs/_templates/decisions.md && echo OK` — AC2.
- `! grep -qE '^## (Plan Format|Decision Log Format)' .claude/commands/plan-w-team.md && grep -q 'specs/_templates' .claude/commands/plan-w-team.md && echo OK` — AC3.
- `grep -q 'SPEC_FILE' .claude/commands/plan-w-team.md && grep -q 'TASKS_FILE' .claude/commands/plan-w-team.md && grep -q 'ACCEPTANCE_FILE' .claude/commands/plan-w-team.md && grep -q 'spec.md' .claude/commands/plan-w-team.md && echo OK` — AC4.
- `test -x .claude/hooks/check-spec-completeness.sh && bash -n .claude/hooks/check-spec-completeness.sh && echo OK` — AC5.
- Fixture test (AC6):
  ```bash
  tmp=$(mktemp -d); mkdir -p "$tmp/specs/broken"; echo "# Spec" > "$tmp/specs/broken/spec.md"
  CLAUDE_PROJECT_DIR="$tmp" .claude/hooks/check-spec-completeness.sh; echo "exit=$?  # expect 2"
  ```
  Then build a complete folder (all four files with all required `##` headers) and assert `exit=0`.
- `for f in plan-w-team build ship; do grep -n 'plan\.md' ".claude/commands/$f.md"; done; grep -n 'plan\.md' .agents/skills/spec-review/SKILL.md .agents/skills/implementation-review/SKILL.md .claude/rules/task-tools.md` — AC7: should print nothing except any explicitly-commented legacy fallback in build.md.
- `grep -q 'tasks.md' .agents/skills/spec-review/SKILL.md && grep -q 'acceptance-criteria.md' .agents/skills/spec-review/SKILL.md && grep -qi 'YAGNI' .agents/skills/spec-review/SKILL.md && echo OK` — AC8.
- `grep -q 'Round N — Verdict' .agents/skills/spec-review/SKILL.md && echo OK` — AC9.

## Notes

- **Dogfooding caveat**: this plan itself was produced under the _old_ two-file contract
  (`plan.md` + `decisions.md`) because the four-file format doesn't exist until this plan ships.
  The very next `/plan-w-team` run after merge will use the four-file format. `/build` must read
  THIS plan from `specs/plan-w-team-sdd-refactor/plan.md` (Task 5's build.md legacy fallback is
  what keeps that working).
- **Prettier hook interaction**: the command's existing `PostToolUse` prettier hook will reformat
  edited markdown; builders should expect prettier to normalize the templates and re-check the
  required-section greps after formatting (heading text is preserved, so greps stay valid).
- **macOS `stat`**: the hook uses BSD `stat -f` to match the `darwin` runtime; do not switch to the
  GNU form without testing.
- No new libraries required (`uv`/`bun` untouched).

## Codex Findings

_Pending Codex review. Codex-owned (the spec-review skill); Claude must not edit this section._
