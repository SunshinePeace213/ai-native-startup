# Plan: Task Tools Orchestration Rule

## Task Description

The team-lead orchestration protocol — including the "Task Management Tools" reference — currently lives inline inside `.claude/commands/plan-w-team.md` (the `### Team Orchestration` block, ~lines 47–210). It is duplicated nowhere else, it only enters context when that one command runs, and it is both **incomplete** (it ignores many real tool fields) and **inaccurate** (it documents a fictional `Task({... resume})` deployment tool and leans on the now-deprecated `TaskOutput`).

This task extracts that protocol into a new, always-loaded project rule at `.claude/rules/task-tools.md`. Per the Claude Code memory docs, a rule file with no `paths:` frontmatter loads into context at the start of **every session** with the same priority as `.claude/CLAUDE.md`, and is re-injected after `/compact`. The new rule will document the **complete schemas of all six Task\* series tools** plus the full orchestration workflow, corrected to the real harness. The inline block is then removed from the command, with no pointer left behind.

## Objective

When complete:

- `.claude/rules/task-tools.md` exists, has **no `paths:` frontmatter**, and therefore auto-loads in every session of this repo (and propagates the same way `.claude/CLAUDE.md` does).
- The rule documents every field of all six Task\* tools (TaskCreate, TaskGet, TaskList, TaskUpdate, TaskOutput, TaskStop), task dependencies, owner assignment, agent deployment (real `Agent` tool), resume (`SendMessage`), parallel execution, and the orchestration workflow.
- The inaccuracies in the old prose are corrected: no fictional `Task({... resume})`; `TaskOutput` is flagged deprecated with the recommended alternative.
- `plan-w-team.md` no longer contains the instructional `### Team Orchestration` block and has no dangling cross-reference to it; the command still reads coherently.
- No `@import`, hook, or link couples the command to the rule.

## Requirements & Decisions

- **Load mechanism**: native `.claude/rules/` auto-loading — a file with no `paths:` frontmatter loads every session at `.claude/CLAUDE.md` priority. No `@import`/hook/command reference. (Confirmed by the memory docs.)
- **Scope**: the **whole** orchestration playbook (Task\* tools + dependencies + owners + agent deployment + resume + parallel + workflow) moves into the rule; the entire instructional `### Team Orchestration` block is removed from the command; **no pointer** left behind.
- **Fidelity**: correct + enrich against the real schemas (use every field; deprecate `TaskOutput`; replace fictional `Task(...resume)` with `Agent` + `SendMessage`).
- Full record in `decisions.md`.

## Problem Statement

The orchestration reference is in the wrong place and in the wrong shape:

1. **Wrong place** — it is buried in a single command, so it is absent from `/build` runs and ad-hoc orchestration sessions that need the same protocol.
2. **Incomplete** — it uses only a subset of each tool's fields (e.g. omits `metadata`, `addBlocks`, the `deleted` status, `TaskGet`'s `blocks`/`blockedBy` returns, `TaskStop`).
3. **Inaccurate** — it documents a `Task({... resume})` deployment tool that does not exist in this harness (deployment is the `Agent` tool; continuation is `SendMessage`), and it builds monitoring around `TaskOutput`, which is now deprecated.

The opportunity: a single, accurate, always-loaded rule that any session (lead or builder) can rely on, eliminating the duplication-and-drift risk the docs explicitly warn about.

## Solution Approach

Create one rule file and trim one command.

1. **Author `.claude/rules/task-tools.md`** with no `paths:` frontmatter. Structure it as the canonical orchestration playbook (outline below), documenting each tool's full schema and correcting the known inaccuracies.
2. **Trim `plan-w-team.md`**: delete the instructional `### Team Orchestration` block (the heading through the end of `#### Orchestration Workflow`, just before `## Grilling Protocol`), and soften the line-~45 reference so it no longer names the removed section. Preserve the `## Team Orchestration` block that is part of the `## Plan Format` template (that text is emitted into generated plans and is unrelated).
3. **Validate** the rule is present and frontmatter-free, the command no longer carries the protocol or a dangling reference, formatting is clean, and full-schema/correction coverage is present.

### Rule content outline (`.claude/rules/task-tools.md`)

```text
(no YAML frontmatter — unconditional every-session load)

# Team Orchestration & Task Tools
- One-paragraph purpose: this is the team-lead orchestration protocol; it is
  loaded every session; the lead orchestrates via these tools and never edits
  code directly; builders read it too (they flip their own task status).

## Task* tools (full schemas)
- TaskCreate({ subject, description, activeForm?, metadata? }) -> taskId
- TaskGet({ taskId }) -> { subject, description, status, blocks, blockedBy }
    (read before starting; verify blockedBy is empty)
- TaskList() -> [{ id, subject, status, owner, blockedBy }]
    (work lowest-id first; "available" = pending + no owner + not blocked)
- TaskUpdate({ taskId, status?, subject?, description?, activeForm?, owner?,
    metadata?, addBlocks?, addBlockedBy? })
    (status: pending -> in_progress -> completed; "deleted" removes it;
     metadata merges, set a key to null to delete it; TaskGet first — staleness)
- TaskOutput({ task_id, block?, timeout? })  ** DEPRECATED **
    (prefer: Read the output file path returned when the task starts, or the
     task-notification; for local_agent tasks use the Agent result, do NOT Read
     the .output symlink — it overflows context)
- TaskStop({ task_id })  (terminate a running background task)

## Dependencies   (addBlockedBy / addBlocks, with a dependency-chain example)
## Owner assignment   (assign via TaskUpdate.owner; find work via TaskList)

## Agent deployment   ** corrected **
- Use the Agent tool: Agent({ description, prompt, subagent_type, model?,
  run_in_background?, isolation? }) -> agent id   (NOT a "Task" tool)
## Resume / continue   ** corrected **
- Continue an agent with SendMessage to its id/name (context intact);
  a new Agent call starts fresh   (NOT Task({... resume}))
## Parallel execution
- run_in_background: true; monitor via task-notifications + Read on the output
  file (not the deprecated TaskOutput)
## Orchestration workflow   (the 7-step loop: create -> deps -> owners ->
  deploy -> monitor -> resume -> complete, using the corrected tools)
```

## Relevant Files

Use these files to complete the task:

- `.claude/commands/plan-w-team.md` — **edit**. Remove the instructional `### Team Orchestration` block (~lines 47–210, heading through end of `#### Orchestration Workflow`). Soften the `## Instructions` line (~45) that says "Refer to the `Team Orchestration` section for more details." **Preserve** the `## Team Orchestration` block inside `## Plan Format` (~lines 298–317) — that is template text emitted into generated plans.
- `.claude/commands/build.md` — **no change**; confirm it does not reference the protocol (it does not).
- `AGENTS.md` / `CLAUDE.md` — **no change**; explicitly do **not** add an `@import` (the rule auto-loads). Listed to make the "don't touch" decision unambiguous.
- The loaded Task\* tool schemas (TaskCreate/TaskGet/TaskList/TaskUpdate/TaskOutput/TaskStop) and the Agent tool description — the **source of truth** for field coverage and the corrections.

### New Files

- `.claude/rules/task-tools.md` — the new always-loaded orchestration rule (content per outline above). No `paths:` frontmatter.

## Implementation Phases

### Phase 1: Foundation

Confirm the load contract: a `.claude/rules/*.md` file with no `paths:` frontmatter loads every session at `.claude/CLAUDE.md` priority (memory docs). Lock the rule's section structure and the exact field list per tool from the real schemas.

### Phase 2: Core Implementation

Author `.claude/rules/task-tools.md` (full schemas + corrections) and, in parallel, trim `plan-w-team.md` (remove the instructional block; fix the dangling reference; preserve the Plan Format template block).

### Phase 3: Integration & Polish

Run validation: file present and frontmatter-free, all six tools + full-schema fields + corrections covered, command no longer carries the protocol or a dangling reference, prettier-clean. Fix any gaps.

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
  - Name: rules-author
  - Role: Author `.claude/rules/task-tools.md` — the full orchestration playbook with complete Task\* schemas and the corrections.
  - Agent Type: general-purpose
  - Resume: true
- Builder
  - Name: command-surgeon
  - Role: Trim `plan-w-team.md` — remove the instructional `### Team Orchestration` block and fix the dangling reference; preserve the Plan Format template block.
  - Agent Type: general-purpose
  - Resume: true
- Validator
  - Name: validator
  - Role: Verify the rule loads (present + no `paths:`), full-schema/correction coverage, command cleanliness, and formatting.
  - Agent Type: general-purpose
  - Resume: false

## Step by Step Tasks

- IMPORTANT: Execute every step in order, top to bottom. Each task maps directly to a `TaskCreate` call.
- Before you start, run `TaskCreate` to create the initial task list that all team members can see and execute.

### 1. Author the task-tools rule

- **Task ID**: author-task-rule
- **Depends On**: none
- **Assigned To**: rules-author
- **Agent Type**: general-purpose
- **Parallel**: true
- Create `.claude/rules/task-tools.md` with **no YAML frontmatter** (no `paths:` field) so it loads every session.
- Document all six Task\* tools using their **full** schemas: `TaskCreate` (subject, description, activeForm, metadata); `TaskGet` (returns subject, description, status, blocks, blockedBy); `TaskList` (id, subject, status, owner, blockedBy); `TaskUpdate` (status incl. `deleted`, subject, description, activeForm, owner, metadata merge/null-delete, addBlocks, addBlockedBy); `TaskOutput` (mark **deprecated**, give the Read-the-output-file / task-notification alternative); `TaskStop`.
- Include dependencies (addBlockedBy/addBlocks + chain example), owner assignment, agent deployment via the **Agent** tool, resume via **SendMessage**, parallel execution, and the 7-step orchestration workflow — corrected to the real harness (no `Task({... resume})`).
- Follow the "Rule content outline" in this plan.

### 2. Trim the plan-w-team command

- **Task ID**: trim-plan-command
- **Depends On**: none
- **Assigned To**: command-surgeon
- **Agent Type**: general-purpose
- **Parallel**: true
- In `.claude/commands/plan-w-team.md`, delete the instructional `### Team Orchestration` block: from the `### Team Orchestration` heading (~line 47) through the end of `#### Orchestration Workflow` (~line 210), immediately before `## Grilling Protocol`.
- Soften the `## Instructions` line (~45) "Understand your role as the team lead. Refer to the `Team Orchestration` section for more details." so it no longer references the removed section and adds **no** link to the rule (e.g. "Understand your role as the team lead and orchestrate the team accordingly.").
- **Do NOT** remove or alter the `## Team Orchestration` block inside `## Plan Format` (~lines 298–317) — it is template text for generated plans.
- Leave the frontmatter (including `disallowed-tools`) unchanged.

### 3. Validate loading, coverage, and cleanliness

- **Task ID**: validate-all
- **Depends On**: author-task-rule, trim-plan-command
- **Assigned To**: validator
- **Agent Type**: general-purpose
- **Parallel**: false
- Run all Validation Commands below.
- Confirm the rule has no `paths:` frontmatter (so it loads unconditionally), all six Task\* tools and the full-schema fields + corrections are present, the command no longer contains the instructional protocol or a dangling reference, and both files are prettier-clean.
- Verify acceptance criteria met; report any gaps for the relevant builder to fix.

## Acceptance Criteria

- `.claude/rules/task-tools.md` exists and contains **no `paths:` frontmatter** (ideally no YAML frontmatter at all) → loads every session, repo-wide, at `.claude/CLAUDE.md` priority.
- The rule documents all six Task\* tools, each with its complete field set, plus dependencies, owner assignment, agent deployment, resume, parallel execution, and the orchestration workflow.
- Corrections are present: `TaskOutput` is marked deprecated with the recommended alternative; deployment uses the `Agent` tool and continuation uses `SendMessage` (no `Task({... resume})`).
- `.claude/commands/plan-w-team.md` no longer contains the instructional `### Team Orchestration` block and has no dangling reference to it; the `## Plan Format` template's `## Team Orchestration` block is intact.
- No `@import`/hook/link couples the command to the rule.
- Both edited/created markdown files are prettier-clean.

## Validation Commands

Execute these commands to validate the task is complete:

- `test -f .claude/rules/task-tools.md && echo OK` — rule file exists.
- `head -1 .claude/rules/task-tools.md` — first line is **not** `---` (no frontmatter); if frontmatter exists, confirm it has no `paths:` key.
- `grep -Eq 'TaskCreate|TaskGet|TaskList|TaskUpdate|TaskOutput|TaskStop' .claude/rules/task-tools.md && grep -c -E 'TaskCreate|TaskGet|TaskList|TaskUpdate|TaskOutput|TaskStop' .claude/rules/task-tools.md` — all six Task\* tools documented.
- `grep -Eq 'addBlocks|addBlockedBy|metadata|deleted|blockedBy|SendMessage|Agent|deprecated' .claude/rules/task-tools.md && echo "schema+corrections OK"` — full-schema fields and corrections present.
- `grep -c '^### Team Orchestration' .claude/commands/plan-w-team.md` — expect `0` (instructional block removed).
- `grep -c '^## Team Orchestration' .claude/commands/plan-w-team.md` — expect `1` (Plan Format template block preserved).
- `grep -n "Refer to the .Team Orchestration. section" .claude/commands/plan-w-team.md` — expect no matches (dangling reference removed).
- `bunx prettier --check .claude/rules/task-tools.md .claude/commands/plan-w-team.md` — formatting clean.

## Notes

- Loading is confirmed by the Claude Code memory docs: _"Rules without `paths` frontmatter are loaded at launch with the same priority as `.claude/CLAUDE.md`."_ This makes the `@import`/hook/command-link approaches unnecessary.
- This is a documentation/refactor change only — no application code, no new libraries (`uv`/`bun` not required).
- `plan-w-team.md` has a `PostToolUse` hook that runs `prettier --write` on every `Edit`/`Write`, so edits self-format; the prettier `--check` in validation is the final gate.
- Out of scope (noted in `decisions.md`): the command frontmatter `disallowed-tools: Task` names a tool that differs from this harness's actual `Agent` deployment tool; left unchanged.
