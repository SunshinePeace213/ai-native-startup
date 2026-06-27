---
description: Grills the user to lock requirements, then creates a concise engineering implementation plan and a decision log, saved to a per-plan specs folder
argument-hint: [user prompt] [orchestration prompt]
model: opus
disallowed-tools: Task, EnterPlanMode
hooks:
  PostToolUse:
    - matcher: "Edit|Write"
      hooks:
        - type: command
          command: "jq -r '.tool_input.file_path' | xargs bunx prettier --write"
---

# Plan With Team

First grill the user to lock requirements via the `Grilling Protocol`, then create a detailed implementation plan based on those locked requirements provided through the `USER_PROMPT` variable. Analyze the request, think through the implementation approach, and save two files to the per-plan folder `specs/<plan-name>/`: the implementation plan (`plan.md`) and a decision log (`decisions.md`) recording the grilling outcome. Follow the `Instructions` and work through the `Workflow` to create the plan.

## Variables

USER_PROMPT: $1
ORCHESTRATION_PROMPT: $2 - (Optional) Guidance for team assembly, task structure, and execution strategy
PLAN_OUTPUT_DIRECTORY: `specs/<plan-name>/` - per-plan folder; `<plan-name>` is the descriptive kebab-case topic
PLAN_FILE: `specs/<plan-name>/plan.md` - the implementation plan
DECISION_LOG: `specs/<plan-name>/decisions.md` - grilling decision log + assumptions
TEAM_MEMBERS: `.claude/agents/team/*.md`
GENERAL_PURPOSE_AGENT: `general-purpose`

## Instructions

- **PLANNING ONLY**: Do NOT build, write code, or deploy agents. Your only output is a plan document saved to `PLAN_OUTPUT_DIRECTORY`.
- The PLANNING ONLY rule still permits the tracking/setup this plan explicitly calls for: creating the single Epic/Plan tracking issue (`gh issue create`), entering the shared worktree (`EnterWorktree`), and relaying Codex spec-review verdicts to that issue (`gh issue comment`). These record and stage the plan — they are NOT building, writing product code, or deploying agents. See `GitHub Issue Tracking`.
- If no `USER_PROMPT` is provided, stop and ask the user to provide it.
- If `ORCHESTRATION_PROMPT` is provided, use it to guide team composition, task granularity, dependency structure, and parallel/sequential decisions.
- Carefully analyze the user's requirements provided in the USER_PROMPT variable
- Before designing or writing any files, run the `Grilling Protocol` to lock requirements. Explore the codebase to self-answer questions; ask the user only what the code cannot answer.
- Determine the task type (chore|feature|refactor|fix|enhancement) and complexity (simple|medium|complex)
- Think deeply (ultrathink) about the best approach to implement the requested functionality or solve the problem
- Understand the codebase directly without subagents to understand existing patterns and architecture
- Follow the Plan Format below to create a comprehensive implementation plan
- Include all required sections and conditional sections based on task type and complexity
- Generate a descriptive kebab-case `<plan-name>` and create the per-plan folder `specs/<plan-name>/`.
- Save the implementation plan to `PLAN_FILE` and the grilling decision log to `DECISION_LOG`.
- Ensure the plan is detailed enough that another developer could follow it to implement the solution
- Include code examples or pseudo-code where appropriate to clarify complex concepts
- Consider edge cases, error handling, and scalability concerns
- Understand your role as the team lead and orchestrate the team accordingly.
- The `## Codex Findings` section of `plan.md` is Codex-owned (written only by the `spec-review` skill). NEVER write to or edit that section. Claude refines only the rest of the plan body between Codex rounds.

## Grilling Protocol

Before designing the plan, interview the user relentlessly until every decision
needed to build is resolved. The goal is a shared, written understanding, not a guess.

- **Explore first.** If a question can be answered by reading the codebase, answer
  it yourself. Ask the user only what the code cannot tell you.
- **One question at a time.** Ask exactly one question per turn using the
  AskUserQuestion tool. Provide 2-4 concrete options, put your recommended answer
  first and append " (Recommended)" to its label; the tool's automatic "Other"
  choice lets the user type a free-form answer. Wait for the answer before the
  next question.
- **Coverage ledger.** Track a checklist of decision dimensions as resolved or
  open; keep grilling until none are open. Cover, as applicable: scope & non-goals,
  target users, success criteria & acceptance tests, data model, interfaces/APIs,
  edge cases & error handling, performance & scale, security & authz,
  observability, rollout/migration, dependencies, testing strategy. Mark
  genuinely-irrelevant dimensions N/A.
- **Adaptive depth.** Grill in proportion to complexity: a light pass for simple
  chores, a deep pass for complex features. Do not interrogate trivial tasks.
- **Accept-all escape hatch.** Offer a standing way to stop early. If the user
  chooses "Accept all recommendations", close every open item with your
  recommended answers, record them as assumptions, and move on.
- **Record every decision.** Capture each answer, and every deferred "you decide"
  as an explicit assumption, for the decision log (see `Decision Log Format`).
- **Final confirmation.** When the ledger is clear, replay all decisions in a
  single AskUserQuestion for sign-off (Approve / revise a specific decision / add
  more). Proceed to design only after approval.

## Workflow

IMPORTANT: **PLANNING ONLY** - Do not execute, build, or deploy. Output is a plan document.

1. Analyze Requirements - Parse the USER_PROMPT to understand the core problem and desired outcome
2. Understand Codebase - Without subagents, directly understand existing patterns, architecture, and relevant files
3. Grill Requirements - Run the `Grilling Protocol`: interview the user one question at a time via AskUserQuestion until the coverage ledger is clear, then get final sign-off. Do NOT design or write files before this completes.
4. Design Solution - Develop technical approach including architecture decisions and implementation strategy
5. Create Tracking Issue - After sign-off, with the plan title and objective known and BEFORE entering the worktree (so the intended branch carries `#N`), create ONE Epic/Plan GitHub issue via `gh issue create` (see `GitHub Issue Tracking`). Skips gracefully if `gh`/remote/auth is unavailable.
6. Enter Worktree - `EnterWorktree` by default so the plan→build lifecycle shares one worktree; the plan folder, `plan.md`, and `decisions.md` are all written INSIDE the worktree.
7. Define Team Members - Use `ORCHESTRATION_PROMPT` (if provided) to guide team composition. Identify from `.claude/agents/team/*.md` or use `general-purpose`. Document in plan.
8. Define Step by Step Tasks - Use `ORCHESTRATION_PROMPT` (if provided) to guide task granularity and parallel/sequential structure. Write out tasks with IDs, dependencies, assignments. Document in plan.
9. Generate Plan Folder - Create a descriptive kebab-case `<plan-name>` and the per-plan folder `specs/<plan-name>/`
10. Save Plan - Write the grilling decision log to `DECISION_LOG` and the implementation plan to `PLAN_FILE`
11. Record Tracking - Record the `## Tracking` block in BOTH `plan.md` and `decisions.md` (issue number, intended convention branch name, worktree path) per `GitHub Issue Tracking`, then update the issue body to link the saved `plan.md` (only when an issue exists).
12. Codex Verification - Run the `Codex Verification Loop` to hand the saved spec to Codex for review (skips gracefully if the Codex CLI is unavailable)
13. Save & Report - Follow the `Report` section to summarize key components and emit the new file paths

## GitHub Issue Tracking

The plan→build lifecycle is threaded by a single GitHub issue. `/plan-w-team` opens that issue, enters a shared worktree, and records both in a `## Tracking` block that `/build` later reads to resume. Codex stays verdict-only — Claude is the only actor that calls `gh`.

### Create the Epic/Plan issue (Workflow step 5)

After the Grilling Protocol sign-off, once the plan title and objective are known and BEFORE entering the worktree (so the intended branch can carry `#N`), create ONE Epic/Plan issue with `gh issue create`:

```
gh issue create --template epic-plan.md --title "<plan title>" --body "<objective + a placeholder link to specs/<plan-name>/plan.md>"
```

- Title = the plan title. Body = the objective plus a placeholder link to `specs/<plan-name>/plan.md`; the link is updated to the real path once `plan.md` is written (Workflow step 11).
- Create exactly one issue per plan — its number `#N` is the durable join key for the whole workflow.

### Enter the worktree (Workflow step 6)

After issue creation, `EnterWorktree` by default. Write the per-plan folder, `plan.md`, and `decisions.md` INSIDE the worktree so `/build` can resume the same working directory.

### Record the `## Tracking` block (Workflow step 11)

Record into BOTH `plan.md` (the `## Tracking` section of the Plan Format) and `decisions.md` (the `## Tracking` note of the Decision Log Format):

- **Issue**: the issue number `#N`, or the literal `none — gh unavailable` when no issue was created.
- **Branch**: the intended convention branch name `<type>/<N>-<slug>`, or `<type>/<slug>` (no `#N`) when there is no issue.
- **Worktree**: the worktree path.

IMPORTANT: the recorded **Issue** field is the SINGLE SOURCE OF TRUTH that `/build` reads — `/build` NEVER re-derives `#N` (e.g. by parsing the mangled local branch name).

### Graceful `gh` skip

If `gh`/remote/auth is unavailable (gh not installed, not authenticated, or no remote), SKIP issue creation and ALL issue comments: record `Issue: none — gh unavailable` in the `## Tracking` block (so the branch falls back to `<type>/<slug>`), warn the user, and continue local-only. A missing `gh` must NEVER block planning. (Mirrors the Codex graceful-skip pattern in the Codex Verification Loop below.)

## Codex Verification Loop

After the plan and `decisions.md` are saved (Workflow step 12) and before the report, hand the drafted spec to Codex for an independent review. Codex writes its verdict + findings into the Codex-owned `## Codex Findings` section of `plan.md`; Claude reads the verdict, refines the rest of the plan body where warranted, and re-submits — capped at 2 Codex rounds.

### Precondition / graceful skip

- Check Codex availability with `command -v codex`. If Codex is unavailable, SKIP the loop: warn the user (point them to `/codex:setup`), record the skip as a note in `decisions.md`, and continue to the report normally. Never block planning on a missing Codex.

### Scaffold

- `plan.md` already contains the `## Codex Findings` section seeded with the `_Pending Codex review. …_` note (from the Plan Format template). Do NOT write into that section — it is Codex-owned. Claude refines only the rest of the plan body between rounds.

### Invocation (verbatim)

Run the following, substituting `<REPO_ROOT>` (the repo cwd that contains `.agents/skills/spec-review/`) and `<SPEC_PATH>` = `specs/<plan-name>/plan.md`:

```
codex exec -C "<REPO_ROOT>" -s workspace-write "Use the spec-review skill to review the plan-w-team implementation spec at <SPEC_PATH>. Follow the skill's output contract exactly: append your per-round verdict and findings ONLY under the '## Codex Findings' section of that file, and edit nothing else in the file."
```

- `codex exec` has NO `--skill` / `--full-auto` / `-a` flag — use `-s workspace-write` (the skill is auto-discovered and invoked by naming it in the prompt).
- Give each review round a generous timeout (~5 minutes): a findings-heavy round can run past the default 2-minute window, and a round that times out writes no verdict block — re-run it rather than treating the empty result as approval.

### Read the verdict from the FILE (not stdout)

```
grep -E '^### Round [0-9]+ — Verdict: (approved|changes-requested)$' specs/<plan-name>/plan.md | tail -1
```

(The dash is a literal em-dash, U+2014.)

### Relay the verdict to the issue

After reading each round's verdict, relay it to the tracking issue with `gh issue comment` — ONLY when an issue number exists in the `## Tracking` block (skip entirely when it reads `Issue: none — gh unavailable`):

```
gh issue comment <N> --body "<the round verdict + Codex findings + the fixes Claude applied this round>"
```

- This builds a single chronological spec-review audit trail on the issue.
- Never block the loop on a failed or unavailable `gh` call — warn and continue (mirrors the graceful `gh` skip in `GitHub Issue Tracking`).

### Loop control — max 2 Codex rounds

- **Round 1** → if the verdict is `approved`, the loop is done. If `changes-requested`, Claude applies the warranted fixes to the plan BODY ONLY (never the `## Codex Findings` section); for any finding Claude rejects, it records the finding + its rationale in `decisions.md`. Then run **Round 2**.
- **Round 2** → if still `changes-requested`, Claude applies a best-effort final pass and PROCEEDS anyway, recording "proceeded without full Codex approval after 2 rounds" + the outstanding findings in `decisions.md`.
- Never exceed 2 Codex rounds.

## Plan Format

- IMPORTANT: Replace <requested content> with the requested content. It's been templated for you to replace. Consider it a micro prompt to replace the requested content.
- IMPORTANT: Anything that's NOT in <requested content> should be written EXACTLY as it appears in the format below.
- IMPORTANT: Follow this EXACT format when creating implementation plans:

```md
# Plan: <task name>

## Task Description

<describe the task in detail based on the prompt>

## Objective

<clearly state what will be accomplished when this plan is complete>

## Requirements & Decisions

<2-4 most important locked decisions and assumptions; full record in decisions.md>

## Tracking

<!-- Recorded by /plan-w-team. The Issue field is the SINGLE SOURCE OF TRUTH /build reads — /build NEVER re-derives #N (e.g. by parsing the mangled local branch name). -->

- Issue: <#N, or the literal `none — gh unavailable` when no issue was created>
- Branch: <intended convention branch `<type>/<N>-<slug>`, or `<type>/<slug>` with no #N when there is no issue>
- Worktree: <absolute worktree path>

<if task_type is feature or complexity is medium/complex, include these sections:>

## Problem Statement

<clearly define the specific problem or opportunity this task addresses>

## Solution Approach

<describe the proposed solution approach and how it addresses the objective>
</if>

## Relevant Files

Use these files to complete the task:

<list files relevant to the task with bullet points explaining why. Include new files to be created under an h3 'New Files' section if needed>

<if complexity is medium/complex, include this section:>

## Implementation Phases

### Phase 1: Foundation

<describe any foundational work needed>

### Phase 2: Core Implementation

<describe the main implementation work>

### Phase 3: Integration & Polish

<describe integration, testing, and final touches>
</if>

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

<list the team members you'll use to execute the plan>

- Builder
  - Name: <unique name for this builder - this allows you and other team members to reference THIS builder by name. Take note there may be multiple builders, the name make them unique.>
  - Role: <the single role and focus of this builder will play>
  - Agent Type: <the subagent type of this builder, you'll specify based on the name in TEAM_MEMBERS file or GENERAL_PURPOSE_AGENT if you want to use a general-purpose agent>
  - Resume: <default true. This lets the agent continue working with the same context. Pass false if you want to start fresh with a new context.>
- <continue with additional team members as needed in the same format as above>

## Step by Step Tasks

- IMPORTANT: Execute every step in order, top to bottom. Each task maps directly to a `TaskCreate` call.
- Before you start, run `TaskCreate` to create the initial task list that all team members can see and execute.

<list step by step tasks as h3 headers. Start with foundational work, then core implementation, then validation.>

### 1. <First Task Name>

- **Task ID**: <unique kebab-case identifier, e.g., "setup-database">
- **Depends On**: <Task ID(s) this depends on, or "none" if no dependencies>
- **Assigned To**: <team member name from Team Members section>
- **Agent Type**: <subagent from TEAM_MEMBERS file or GENERAL_PURPOSE_AGENT if you want to use a general-purpose agent>
- **Parallel**: <true if can run alongside other tasks, false if must be sequential>
- <specific action to complete>
- <specific action to complete>

### 2. <Second Task Name>

- **Task ID**: <unique-id>
- **Depends On**: <previous Task ID, e.g., "setup-database">
- **Assigned To**: <team member name>
- **Agent Type**: <subagent type from TEAM_MEMBERS file or GENERAL_PURPOSE_AGENT if you want to use a general-purpose agent>
- **Parallel**: <true/false>
- <specific action>
- <specific action>

### 3. <Continue Pattern>

### N. <Final Validation Task>

- **Task ID**: validate-all
- **Depends On**: <all previous Task IDs>
- **Assigned To**: <validator team member>
- **Agent Type**: <validator agent>
- **Parallel**: false
- Run all validation commands
- Verify acceptance criteria met

<continue with additional tasks as needed. Agent types must exist in .claude/agents/team/*.md>

## Acceptance Criteria

<list specific, measurable criteria that must be met for the task to be considered complete>

## Validation Commands

Execute these commands to validate the task is complete:

<list specific commands to validate the work. Be precise about what to run>
- Example: `uv run python -m py_compile apps/*.py` - Test to ensure the code compiles

## Notes

<optional additional context, considerations, or dependencies. If new libraries are needed, specify using `uv add`>

## Codex Findings

_Pending Codex review. Codex-owned (the spec-review skill); Claude must not edit this section._
```

## Decision Log Format

Write the full grilling record to `DECISION_LOG`. Use this structure:

```md
# Decisions: <task name>

## Summary — one paragraph: agreed scope + key choices

## Tracking — issue (#N, or `none — gh unavailable`), intended convention branch name (`<type>/<N>-<slug>`, or `<type>/<slug>` with no #N), and worktree path. Mirrors `plan.md`'s `## Tracking`; the issue field is the single source of truth /build reads.

## Resolved Decisions — per decision: Question / Answer / Rationale

## Assumptions — every deferred "you decide" / accept-all item, explicitly

## Open Questions / Out of Scope — deferred or excluded items (non-goals)

## Codex Verification — outcome (one of: approved at round N / proceeded without approval after 2 rounds / skipped — Codex unavailable), plus any Codex findings Claude rejected with rationale
```

## Report

After creating and saving the implementation plan, provide a concise report with the following format:

```
✅ Implementation Plan Created

Plan: specs/<plan-name>/plan.md
Decisions: specs/<plan-name>/decisions.md
Topic: <brief description of what the plan covers>
Codex Verification: <approved at round N | proceeded without approval after 2 rounds | skipped (Codex unavailable)>
Key Components:
- <main component 1>
- <main component 2>
- <main component 3>

Key Decisions (from grilling):
- <most important locked decision or assumption 1>
- <decision 2>
- <decision 3>

Team Task List:
- <list of tasks, and owner (concise)>

Team members:
- <list of team members and their roles (concise)>

When you're ready, you can execute the plan in a new agent by running:
/build <plan-name>
```
