# Tasks: <task name>

> Execution plan for [spec.md](./spec.md). Owner and scope are defined there; this file is
> how & who. Orchestration mechanics live in `.claude/rules/orchestration.md`.

<!-- ## Implementation Phases: include for medium/complex work; omit for simple tasks. -->

## Implementation Phases

<!-- One "### Phase N: <name>" per phase, each a one-line goal plus the Task IDs it
     contains. Name phases after the work, not a generic scaffold — a phase exists only
     because its tasks cannot start until the previous phase lands. -->

## Step by Step Tasks

<!-- One task per unit of work a single agent can finish and verify. Each maps to one
     TaskCreate call, names the acceptance criteria it satisfies, and carries the exact
     command that proves it. Two tasks marked Parallel must have disjoint Files. -->

### 1. <First Task Name>

- **Task ID:** `<unique-kebab-case-id>`
  <!-- The join key across tasks.md, the task board, hand-offs, and the PR's Agent Task
       Manifest. Never `#N` — GitHub autolinks it to unrelated issues. -->
- **Depends On:** `<task-id>`, or "none"
- **Agent Type:** <a subagent type, or `general-purpose`>
- **Model / Effort:** <model + effort stamped per `.claude/rules/model-selection.md`>
- **Files:** <the paths this task owns — no other parallel task may list any of them>
- **Parallel:** <true | false>
- **Satisfies:** <AC id(s) from acceptance-criteria.md>
- **Verify:** <the exact command the builder runs before hand-off, and the result that
  counts as a pass>
- <specific action>
- <specific action>

### 2. <Second Task Name>

- **Task ID:** `<unique-kebab-case-id>`
- **Depends On:** `<task-id>`
- **Agent Type:** <a subagent type, or `general-purpose`>
- **Model / Effort:** <model + effort stamped per `.claude/rules/model-selection.md`>
- **Files:** <the paths this task owns>
- **Parallel:** <true | false>
- **Satisfies:** <AC id(s)>
- **Verify:** <command + pass condition>
- <specific action>

### N. Validate Everything

- **Task ID:** `validate-all`
- **Depends On:** every preceding Task ID
- **Agent Type:** a validator agent, or `general-purpose`
- **Model / Effort:** model + effort stamped per `.claude/rules/model-selection.md`
- **Files:** none — read-only
- **Parallel:** false
- **Satisfies:** every AC
- **Verify:** every command in acceptance-criteria.md → `## Validation Commands` passes,
  and each criterion is met
