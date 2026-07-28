# Orchestration

How a session decides to do work itself, delegate to subagents, or spawn an agent
team — and the shared board that coordinates them.

## Pick one

| | Do it yourself | Subagent | Agent team |
| --- | --- | --- | --- |
| **Use when** | You'd finish it in a handful of tool calls | You need the result, not the search | Workers must share findings and challenge each other |
| **Context** | Yours | Own window, result returns to you | Own window, fully independent session |
| **Talks to** | — | You only, never each other | You and each other, by name |
| **Cost** | Lowest | Low — only the summary returns | Highest — each teammate is a full session |

Teams earn their cost on parallel exploration: multi-lens review, competing debug
hypotheses, separate modules with no shared files. For sequential work, same-file
edits, or long dependency chains, use subagents or stay solo.

## Subagents

- Deploy with the `Agent` tool. Background is the default — pass
  `run_in_background: false` only when the result gates your next step.
- Issue several `Agent` calls in one message to run them concurrently.
- The agent's final message is the result and is never shown to the user — relay
  what matters.
- Never `Read` a local agent's `.output` symlink; it points at the full JSONL
  transcript and overflows context. Use the returned result.
- `SendMessage` continues an agent with its context intact; a fresh `Agent` call
  starts clean.

## Agent teams

Teams require `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` (set in
`.claude/settings.json`). Without it no teammate can be spawned — use subagents.

- The main session is the lead for its lifetime and spawns every teammate; name
  each one in the spawn instruction so you can address it later.
- Teammates load `CLAUDE.md`/`AGENTS.md` but **not** your conversation history —
  put every task-specific detail in the spawn prompt.
- Teammates do **not** inherit the lead's model. Name model and effort explicitly
  per `model-selection.md`.
- Spawn a teammate from an existing subagent type to reuse its role definition; it
  honors that definition's `tools` and `model`.
- Start with 3–5 teammates and 5–6 tasks each. Give each teammate a disjoint set of
  files — two teammates editing one file overwrite each other.
- Require plan approval for risky work; the teammate stays read-only until the lead
  approves.
- Limits: no nested teams, teammates can't run background subagents, `/resume` does
  not restore them, and task status lags — verify work is done before trusting
  `completed`.

## Once you have teammates

Spawning a team makes you the coordinator: assign tasks, unblock, and synthesize
results. Don't implement tasks you assigned, and wait for teammates to finish
before moving on. A session with no teammates does the work itself.

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

- **Team**: `/harness-layer:harness-build`'s implement stage — file-disjoint tasks
  with stamped owners and dependencies.
- **Subagents**: plan's `claude-code-guide` and `kb-fetcher` helpers and its
  `opus` page author, `/kb` fan-out, the tidy simplifiers, and review's Codex
  runner and fixers.
