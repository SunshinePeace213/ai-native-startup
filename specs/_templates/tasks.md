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
- **Model / Effort:** <`opus` complex / `sonnet` otherwise; `low`|`medium`|`high`|`xhigh`>
- **Parallel:** <true if it can run alongside others, false if sequential>
- **Satisfies:** <acceptance criteria id(s) from acceptance-criteria.md, e.g. AC1, AC2>
- <specific action>
- <specific action>

### 2. <Second Task Name>

- **Task ID:** <unique-id>
- **Depends On:** <previous Task ID>
- **Assigned To:** <team member name>
- **Agent Type:** <subagent type, or `general-purpose`>
- **Model / Effort:** <`opus` complex / `sonnet` otherwise; `low`|`medium`|`high`|`xhigh`>
- **Parallel:** <true/false>
- **Satisfies:** <acceptance criteria id(s)>
- <specific action>

### N. Validate Everything

- **Task ID:** validate-all
- **Depends On:** <all previous Task IDs>
- **Assigned To:** <validator team member>
- **Agent Type:** <validator agent, or `general-purpose`>
- **Model / Effort:** <`opus` complex / `sonnet` otherwise; `low`|`medium`|`high`|`xhigh`>
- **Parallel:** false
- Run every command in acceptance-criteria.md → `## Validation Commands`.
- Verify each acceptance criterion is met.
