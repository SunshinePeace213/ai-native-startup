# Orchestration

How a session decides to do work itself or delegate to subagents — and the shared
board that coordinates them.

## Pick one

| | Do it yourself | Subagent |
| --- | --- | --- |
| **Use when** | You'd finish it in a handful of tool calls | You need the result, not the search |
| **Context** | Yours | Own window, result returns to you |
| **Cost** | Lowest | Low — only the summary returns |

Subagents earn their cost on parallel fan-out: multi-lens review, competing debug
hypotheses, separate modules with no shared files. For sequential work or long
dependency chains, stay solo — never spawn an agent to verify your own output;
verification runs at a different seat.

## Subagents

- Deploy with the `Agent` tool. Background is the default — pass
  `run_in_background: false` only when the result gates your next step.
- Issue several `Agent` calls in one message to run them concurrently.
- Subagents load `CLAUDE.md`/`AGENTS.md` but not your conversation — put every
  task-specific detail in the spawn prompt.
- Two parallel subagents editing one file overwrite each other — give each a
  disjoint file set.
- The agent's final message is the result and is never shown to the user — relay
  what matters.
- Never `Read` a local agent's `.output` symlink; it points at the full JSONL
  transcript and overflows context. Use the returned result.
- `SendMessage` continues an agent with its context intact; a fresh `Agent` call
  starts clean.

## The shared board

`TaskCreate` adds a task, `TaskGet` reads one, `TaskList` surveys all, `TaskUpdate`
changes status/owner/dependencies, `TaskStop` kills a running background task.
`TaskOutput` is deprecated — read the output path from the launch result or the
completion notification instead. Fetch full schemas with `ToolSearch` when needed.

- Work tasks in ID order. A task is available when it is `pending`, unowned, and
  its `blockedBy` is empty; claiming is file-locked, and completing a task
  auto-unblocks its dependents.
- Other agents mutate the board — `TaskGet` for current state before every
  `TaskUpdate`.
- `metadata` merges rather than replaces; set a key to `null` to delete it.

## In this pipeline

- **Builders**: `/harness-layer:harness-build`'s implement stage runs background
  subagents on file-disjoint tasks, each stamped per `model-selection.md`.
- **The review fixer**: one full-context `opus` subagent per gate cycle — the
  whole blocking set travels together, never split across fixers.
- **Helpers**: plan's `claude-code-guide` and `kb-fetcher`, the plan and build
  `opus` page authors, `/kb` fan-out, and the tidy simplifiers.
