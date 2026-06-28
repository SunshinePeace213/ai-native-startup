# Team Orchestration & Task Tools

This is the team-lead orchestration protocol. It loads into every session of this
repo, so any session — lead or builder — can rely on it. As the **team lead** you
NEVER write code, run builds, or edit files directly: you coordinate the work by
creating tasks, assigning owners, deploying agents, and tracking progress with the
tools below. **Builders** read this too — a builder flips its own task to
`in_progress` when it starts and to `completed` only when the work is fully done.

## Task\* tools (full schemas)

The shared task list is the single source of truth for who is doing what. Six tools
operate on it. Each schema below lists every field.

### TaskCreate — add a task to the shared list

```typescript
TaskCreate({
  subject: "Implement user authentication", // required: brief imperative title
  description: "Create login/logout endpoints with JWT. See specs/auth/spec.md.", // required: full context for the owner
  activeForm: "Implementing authentication", // optional: present-continuous, shown in the spinner while in_progress
  metadata: { phase: "core", priority: "high" }, // optional: arbitrary key/value bag
})
// Returns: taskId (e.g. "1"). Every task is created with status "pending".
```

### TaskGet — read one task before acting on it

```typescript
TaskGet({ taskId: "1" })
// Returns: { subject, description, status, blocks, blockedBy }
//   status:    "pending" | "in_progress" | "completed"
//   blocks:    task IDs waiting on THIS one to complete
//   blockedBy: task IDs that must complete before this one can start
```

Always `TaskGet` before starting work and confirm **`blockedBy` is empty**.

### TaskList — survey the whole board

```typescript
TaskList({}) // takes no arguments
// Returns: [{ id, subject, status, owner, blockedBy }, ...]
//   owner: agent name if claimed, empty if available
```

Work tasks in **ID order (lowest first)** — earlier tasks set up context for later
ones. A task is **available** when it is `pending`, has no `owner`, and its
`blockedBy` is empty.

### TaskUpdate — change status, assignment, or dependencies

```typescript
TaskUpdate({
  taskId: "1", // required
  status: "in_progress", // "pending" → "in_progress" → "completed"; "deleted" permanently removes the task
  subject: "Implement auth endpoints", // optional: new title
  description: "Updated scope: add refresh tokens.", // optional: new description
  activeForm: "Implementing auth endpoints", // optional: new spinner text
  owner: "builder-auth", // optional: (re)assign the task
  metadata: { priority: "high", scratch: null }, // optional: merges keys; set a key to null to delete it
  addBlocks: ["5"], // optional: tasks that cannot start until this one completes
  addBlockedBy: ["2", "3"], // optional: tasks that must complete before this one
})
```

`status` accepts `pending` | `in_progress` | `completed`, plus `deleted` to remove a
task created in error. `metadata` is **merged**, not replaced — set a key to `null`
to delete just that key. Because other agents mutate the board, **`TaskGet` for the
latest state before every `TaskUpdate`** (staleness).

### TaskOutput — retrieve a task's output **(DEPRECATED)**

```typescript
TaskOutput({
  task_id: "a1b2c3", // required
  block: true, // default true: wait for completion; false: non-blocking status check
  timeout: 300000, // default 30000 ms, max 600000
})
```

**Deprecated — avoid it.** Background tasks already return their **output file
path** in the launch result, and a `<task-notification>` delivers the same path when
the task finishes. Prefer that path instead:

- **bash / remote_agent tasks** → `Read` the returned output file path (it holds the
  stdout/stderr or streamed session output).
- **local_agent tasks** → use the **Agent** tool's returned result directly. Do
  **NOT** `Read` the `.output` symlink — it points at the full subagent transcript
  (JSONL) and will overflow context.

### TaskStop — terminate a running background task

```typescript
TaskStop({ task_id: "a1b2c3" }) // stop a long-running background task by ID
```

## Dependencies

Use `addBlockedBy` / `addBlocks` to sequence work — a blocked task cannot be claimed
until every task in its `blockedBy` list is `completed`.

```typescript
// Task 2 waits for Task 1; Task 4 waits for everything before it.
TaskUpdate({ taskId: "2", addBlockedBy: ["1"] })
TaskUpdate({ taskId: "4", addBlockedBy: ["1", "2", "3"] })

// Equivalent from the other direction — Task 1 blocks Task 2:
TaskUpdate({ taskId: "1", addBlocks: ["2"] })
```

Dependency-chain example:

```text
Task 1: Setup foundation   → blockedBy: []          (available immediately)
Task 2: Implement feature  → blockedBy: ["1"]
Task 3: Write tests        → blockedBy: ["2"]
Task 4: Final validation   → blockedBy: ["1","2","3"]
```

## Owner assignment

Assign each task to a named team member for clear accountability, then let members
discover their work via the board.

```typescript
TaskUpdate({ taskId: "1", owner: "builder-api" }) // assign
TaskList({}) // members scan for tasks whose owner is theirs (or unassigned + unblocked)
```

## Agent deployment

Deploy team members with the **`Agent`** tool (there is no `Task(...)` deployment
tool in this harness).

```typescript
Agent({
  description: "Implement auth endpoints", // 3-5 word label
  prompt:
    "Implement the authentication endpoints described in task 1. Mark the task in_progress when you start and completed when done.",
  subagent_type: "general-purpose", // omit → defaults to general-purpose
  model: "opus", // optional alias: opus | sonnet | haiku | fable
  run_in_background: false, // true → runs async, returns immediately (parallel work)
  isolation: "worktree", // optional: own git worktree (use when agents edit files in parallel)
})
// Returns: the agent's id and, for background runs, an output file path.
// The agent's final message comes back as the tool result.
```

Pass each owner enough context to act alone: the task ID, the plan/spec path, and
the instruction to flip their task status. The agent's final message is the result —
it is not shown to the user, so relay what matters.

## Resume / continue

To continue an agent **with its context intact**, send it a message — do **not**
re-deploy (a fresh `Agent` call starts from a clean slate).

```typescript
// Continue an active teammate by name:
SendMessage({
  to: "builder-auth",
  summary: "add validation",
  message: "Now add input validation to the endpoints you just created.",
})

// Resume a COMPLETED background agent by its agentId (format "a...-...") from its spawn result:
SendMessage({
  to: "a1b2c3-...",
  summary: "follow-up work",
  message: "Continue: wire the new endpoints into the router.",
})
```

Resume when the follow-up depends on prior context; start a fresh `Agent` for
unrelated work.

## Parallel execution

Run several builders at once with `run_in_background: true`. Each returns
immediately with an id and an output file path.

```typescript
Agent({
  description: "Build API endpoints",
  prompt: "...",
  run_in_background: true,
})
Agent({
  description: "Build frontend",
  prompt: "...",
  run_in_background: true,
})
// Both now run concurrently.
```

Monitor them via the `<task-notification>` you receive on completion and by `Read`ing
the returned output file path (for local_agent work, use the Agent result instead) —
**not** the deprecated `TaskOutput`. Track overall progress with `TaskList`, and
`TaskStop` a run you need to abort.

## Orchestration workflow

1. **Create tasks** — one `TaskCreate` per step in the plan.
2. **Set dependencies** — `TaskUpdate` + `addBlockedBy` / `addBlocks`.
3. **Assign owners** — `TaskUpdate` + `owner`.
4. **Deploy agents** — `Agent` to execute each assigned task (`run_in_background: true` for parallel work).
5. **Monitor progress** — `TaskList` plus the `<task-notification>` / output file path (not `TaskOutput`).
6. **Resume agents** — `SendMessage` to continue an owner with context intact.
7. **Mark complete** — `TaskUpdate` + `status: "completed"` (owners flip their own tasks; verify on the board).
