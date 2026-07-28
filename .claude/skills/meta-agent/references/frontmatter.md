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
2. **If no entry in `tools` resolves, the agent won't launch.** A misspelling or
   a subagent-unavailable name in an otherwise short list fails the whole agent
   with an error naming the entries.
3. **Six tools never work in a subagent, regardless of `tools`:**
   `AskUserQuestion`, `EnterPlanMode`, `ScheduleWakeup`, `WaitForMcpServers`,
   `EndConversation`, and `ExitPlanMode` (except when `permissionMode: plan`).
   Don't design an agent that asks the user mid-run.
4. **Three fields are silently ignored for plugin-loaded subagents:** `hooks`,
   `mcpServers`, `permissionMode`. Move the agent to `.claude/agents/` if it
   needs them.
5. **`name` must be unique across the whole agents tree** (project + user +
   plugins). A duplicate is silently discarded or loses on priority.

## Field-by-field

| Field | Req | Type / constraints | Set it when |
| --- | --- | --- | --- |
| `name` | **Yes** | Lowercase letters + hyphens. Unique tree-wide; filename need not match. | Always. Descriptive of the job (`test-runner`, `db-reader`). |
| `description` | **Yes** | Plain text, third person. The trigger document. | Always. Name the phrasings and contexts that route here; add "use proactively" for auto-delegation. See below. |
| `tools` | No | Comma-separated allowlist; MCP patterns and `Agent(...)` allowed. Omitting inherits ALL. | You want least privilege — list only what the job needs. Don't list `Skill` to preload skills; use `skills`. |
| `disallowedTools` | No | Same syntax; applied before `tools`. | You want "everything except a few" (e.g. `Write, Edit`), or to strip one MCP server. |
| `model` | No (default `inherit`) | `opus`\|`sonnet`\|`haiku`\|`fable`\|full id\|`inherit`. | Always stamp it, from [model-selection.md](../../../rules/model-selection.md). Use an alias, never a dated id. |
| `effort` | No (inherits session) | `low`\|`medium`\|`high`\|`xhigh`\|`max`. | Always stamp it, from [model-selection.md](../../../rules/model-selection.md). It is the only depth control — prose is not. |
| `permissionMode` | No | `default`\|`acceptEdits`\|`auto`\|`dontAsk`\|`bypassPermissions`\|`plan`\|`manual` (alias for `default`). Ignored for plugin agents. | A non-default stance is needed (`plan` for a read-only planner; `acceptEdits` for an autonomous editor). A stricter parent mode wins. |
| `maxTurns` | No | Positive integer. | You want a hard ceiling on a loop-prone agent. |
| `skills` | No | YAML list of skill names. | The agent needs domain knowledge up front — preloads the **full content** at startup. Can't preload a `disable-model-invocation: true` skill. |
| `mcpServers` | No | YAML list; server refs or inline configs. Ignored for plugin agents. | The agent needs a server the session lacks, or you want its tool descriptions out of the main context. |
| `hooks` | No | YAML hook config. Ignored for plugin agents. | You need determinism the model shouldn't enforce (`PreToolUse` gate, `Stop` verify). `Stop` becomes `SubagentStop`. |
| `memory` | No | `user`\|`project`\|`local`. | Knowledge compounds across runs. Auto-enables Read/Write/Edit and injects `MEMORY.md`. `project` is the default; skip for one-shot work. |
| `background` | No (unset → background) | Boolean. `true` pins background even when Claude needs the result right away. | Rarely — unset already runs in the background, and Claude drops to the foreground only when it needs the result to continue. Permission prompts surface in the main session naming the agent; they are not auto-denied. |
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

## model / effort / memory / permissionMode notes

- **model and effort** come from
  [model-selection.md](../../../rules/model-selection.md) — the roster, the
  defaults, and the know-vs-try escalation heuristic all live there. Stamp both;
  don't re-derive the guidance here.
- **model resolution order:** `CLAUDE_CODE_SUBAGENT_MODEL` env → per-invocation
  `model` param → definition `model` → session model. Aliases track the current
  default; pin a full id only for reproducibility.
- **thinking** is inherited from the session and has no per-agent field.
- **memory scopes:** `user` (`~/.claude/agent-memory/<name>/`, all projects),
  `project` (`.claude/agent-memory/<name>/`, checked in — the default), `local`
  (`.claude/agent-memory-local/<name>/`, not checked in).
- **permissionMode:** a stricter **parent** mode wins — under a parent running
  `bypassPermissions`/`acceptEdits`/`auto`, the subagent's own mode is ignored.

## When the definition is reused as a teammate

Spawning an agent-team teammate from a subagent type reuses this same file, but
not all of it applies. The teammate honors `tools` and `model`, and the body is
**appended** to the teammate's system prompt rather than replacing it. Three
differences bite:

- `skills` and `mcpServers` are **not applied** — a teammate loads skills and MCP
  servers from project and user settings instead.
- `background: true` **errors** for an in-process teammate; its subagents run in
  the foreground.
- `SendMessage` and the task tools stay available even when `tools` excludes them.

Don't make an agent depend on a preloaded skill if it's also meant to run as a
teammate — restate what it needs in the body, or keep it subagent-only.

## Writing the `description` (the field that decides delegation)

Claude routes off `name` + `description`. It's a trigger document, not a human
summary: **third person**, **name the real trigger contexts and phrasings**, add
**"use proactively"** for auto-delegation, and include a **Not-for boundary** so
adjacent work routes to a sibling.

| BAD | GOOD |
| --- | --- |
| `Reviews code.` | `Read-only reviewer of the current git diff. Use proactively after code changes to check correctness and security. Reports findings only; does not edit. Not for running tests (use test-runner).` |
| `A debugging helper.` | `Debugging specialist for errors and test failures. Use proactively when a command fails or a test breaks. Isolates root cause and applies a minimal fix.` |
| `Does database stuff.` | `Runs read-only SQL and summarizes results. Use when analyzing data or generating reports. Not for migrations or writes — those go to the migration agent.` |
