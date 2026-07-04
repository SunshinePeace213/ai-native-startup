# Claude Subagent Frontmatter Reference

A Claude subagent is a Markdown file in an `agents/` directory: YAML frontmatter
between `---` markers, then a body that becomes the system prompt. Only `name`
and `description` are required; everything else is optional. The same fields are
accepted as JSON via the `--agents` CLI flag and the SDK `agents` option (there
the body is supplied as the `prompt` field).

## Read first — the load-bearing gotchas

1. **Tool resolution is `disallowedTools` FIRST, then `tools`.** Omitting `tools`
   inherits **every** tool the main conversation has, including connected MCP
   tools. `disallowedTools: Write, Edit` = "everything except Write/Edit";
   `tools: Read, Grep` = "only those two." A tool named in both is removed.
2. **Five tools never work in a subagent, regardless of `tools`:**
   `AskUserQuestion`, `EnterPlanMode`, `ScheduleWakeup`, `WaitForMcpServers`, and
   `ExitPlanMode` (except when `permissionMode: plan`). Don't design an agent
   that asks the user mid-run.
3. **Three fields are silently ignored for plugin-loaded subagents:** `hooks`,
   `mcpServers`, `permissionMode`. Move the agent to `.claude/agents/` if it
   needs them.
4. **`name` must be unique across the whole agents tree** (project + user +
   plugins). A duplicate is silently discarded or loses on priority.

## Field-by-field

| Field | Req | Type / constraints | Set it when |
|---|---|---|---|
| `name` | **Yes** | Lowercase letters + hyphens. Unique tree-wide; filename need not match. | Always. Descriptive of the job (`test-runner`, `db-reader`). |
| `description` | **Yes** | Plain text, third person. The trigger document. | Always. Name the phrasings/contexts that route here; add "use proactively" for auto-delegation. See below. |
| `tools` | No | Comma-separated allowlist; MCP patterns and `Agent(...)` allowed. Omitting inherits ALL. | You want least privilege — list only what the job needs. Don't list `Skill` to preload skills; use `skills`. |
| `disallowedTools` | No | Same syntax; applied before `tools`. | You want "everything except a few" (e.g. `Write, Edit`), or to strip one MCP server. |
| `model` | No (default `inherit`) | `opus`\|`sonnet`\|`haiku`\|`fable`\|full id\|`inherit`. | The job wants a different tier than the session. Use an alias, not a dated id. |
| `effort` | No (inherits session) | `low`\|`medium`\|`high`\|`xhigh`\|`max`. | **Omit by default** (the shipped team agents do). Set only when the job needs more/less reasoning than the session default, or the user asks — `high`/`xhigh` for hard coding/agentic work. |
| `permissionMode` | No | `default`\|`acceptEdits`\|`auto`\|`dontAsk`\|`bypassPermissions`\|`plan`. Ignored for plugin agents. | A non-default stance is needed (`plan` for a read-only planner; `acceptEdits` for an autonomous editor). A stricter parent mode wins. |
| `maxTurns` | No | Positive integer. | You want a hard ceiling on a loop-prone agent. |
| `skills` | No | YAML list of skill names. | The agent needs domain knowledge up front — preloads the **full content** at startup. Can't preload a `disable-model-invocation: true` skill. |
| `mcpServers` | No | YAML list; server refs or inline configs. Ignored for plugin agents. | The agent needs a server the session lacks, or you want its tool descriptions out of the main context. |
| `hooks` | No | YAML hook config. Ignored for plugin agents. | You need determinism the model shouldn't enforce (`PreToolUse` gate, `Stop` verify). `Stop` becomes `SubagentStop`. |
| `memory` | No | `user`\|`project`\|`local`. | Knowledge compounds across runs. Auto-enables Read/Write/Edit and injects `MEMORY.md`. `project` is the default; skip for one-shot work. |
| `background` | No (default false) | Boolean. | The work is long and the user keeps working. Background agents auto-deny prompts. |
| `isolation` | No | `worktree`. | Multiple file-mutating agents run in parallel and must not clobber each other. |
| `color` | No | `red`\|`blue`\|`green`\|`yellow`\|`purple`\|`orange`\|`pink`\|`cyan`. | Purely cosmetic identification. |

`initialPrompt` (seed message when run as a whole-session `--agent`) and `prompt`
(the body, for JSON/SDK definitions only) also exist; don't add `prompt` to a
file-based agent — the body is the prompt.

## Tool inheritance — worked ordering

Given a session with `{Read, Write, Edit, Bash, Grep, Glob, mcp__github__*, mcp__slack__*}`:

- `tools` and `disallowedTools` both omitted → inherits all of the above.
- `disallowedTools: Write, Edit` → everything minus Write/Edit.
- `tools: Read, Grep, Glob` → only those three (no MCP, no Bash).
- `disallowedTools: mcp__github` + `tools: Read, Bash, mcp__github__create_issue`
  → `{Read, Bash}` — the github tool was removed first, so it's gone.

MCP patterns (valid in both fields): `mcp__<server>` / `mcp__<server>__*` (whole
server), `mcp__<server>__<tool>` (one tool), `mcp__*` (in `disallowedTools` only,
removes all MCP). Use qualified names — a bare `tool` may not resolve.

## model / memory / permissionMode notes

- **model resolution order:** `CLAUDE_CODE_SUBAGENT_MODEL` env → per-invocation
  `model` param → definition `model` → session model. Aliases track the current
  default; pin a full id only for reproducibility.
- **memory scopes:** `user` (`~/.claude/agent-memory/<name>/`, all projects),
  `project` (`.claude/agent-memory/<name>/`, checked in — the default), `local`
  (`.claude/agent-memory-local/<name>/`, not checked in).
- **permissionMode:** a stricter **parent** mode wins — under a parent running
  `bypassPermissions`/`acceptEdits`/`auto`, the subagent's own mode is ignored.

## Writing the `description` (the field that decides delegation)

Claude routes off `name` + `description`. It's a trigger document, not a human
summary: **third person**, **name the real trigger contexts and phrasings**, add
**"use proactively"** for auto-delegation, and include a **Not-for boundary** so
adjacent work routes to a sibling.

| BAD | GOOD |
|---|---|
| `Reviews code.` | `Read-only reviewer of the current git diff. Use proactively after code changes to check correctness and security. Reports findings only; does not edit. Not for running tests (use test-runner).` |
| `A debugging helper.` | `Debugging specialist for errors and test failures. Use proactively when a command fails or a test breaks. Isolates root cause and applies a minimal fix.` |
| `Does database stuff.` | `Runs read-only SQL and summarizes results. Use when analyzing data or generating reports. Not for migrations or writes — those go to the migration agent.` |
