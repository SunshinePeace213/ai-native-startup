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
5. Define Team Members - Use `ORCHESTRATION_PROMPT` (if provided) to guide team composition. Identify from `.claude/agents/team/*.md` or use `general-purpose`. Document in plan.
6. Define Step by Step Tasks - Use `ORCHESTRATION_PROMPT` (if provided) to guide task granularity and parallel/sequential structure. Write out tasks with IDs, dependencies, assignments. Document in plan.
7. Generate Plan Folder - Create a descriptive kebab-case `<plan-name>` and the per-plan folder `specs/<plan-name>/`
8. Save Plan - Write the grilling decision log to `DECISION_LOG` and the implementation plan to `PLAN_FILE`
9. Save & Report - Follow the `Report` section to summarize key components and emit the new file paths

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
```

## Decision Log Format

Write the full grilling record to `DECISION_LOG`. Use this structure:

```md
# Decisions: <task name>

## Summary — one paragraph: agreed scope + key choices

## Resolved Decisions — per decision: Question / Answer / Rationale

## Assumptions — every deferred "you decide" / accept-all item, explicitly

## Open Questions / Out of Scope — deferred or excluded items (non-goals)
```

## Report

After creating and saving the implementation plan, provide a concise report with the following format:

```
✅ Implementation Plan Created

Plan: specs/<plan-name>/plan.md
Decisions: specs/<plan-name>/decisions.md
Topic: <brief description of what the plan covers>
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
