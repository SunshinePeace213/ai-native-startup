# Subagent Frontmatter Reference

A subagent is a Markdown file in an `agents/` directory: YAML frontmatter between `---` markers, then a body that becomes the system prompt. Only `name` and `description` are required. Everything else is optional. The same field set is accepted as JSON via the `--agents` CLI flag and the SDK `agents` option (there the markdown body is supplied as the `prompt` field).

## Read first — the load-bearing gotchas

1. **Tool resolution order is `disallowedTools` FIRST, then `tools`.** Omitting `tools` inherits **every** tool the main conversation has, including connected MCP tools. `disallowedTools` is subtracted from the pool first; `tools` (if present) then resolves against the remainder. A tool named in both is removed. So `disallowedTools: Write, Edit` on an agent with no `tools` line = "everything except Write/Edit"; `tools: Read, Grep` = "only those two." Pick one mechanism per agent unless you deliberately want the intersection.

2. **Five tools are unavailable to a subagent regardless of config** — listing them in `tools` does nothing:
   - `AskUserQuestion`
   - `EnterPlanMode`
   - `ExitPlanMode` — *except* when the subagent's `permissionMode` is `plan`
   - `ScheduleWakeup`
   - `WaitForMcpServers`

   They depend on the main conversation's UI or session state. Don't author a subagent that needs to ask the user a question mid-run; it can't.

3. **Three fields are silently IGNORED for subagents loaded from a plugin:** `hooks`, `mcpServers`, `permissionMode`. No error, no warning — they just don't apply. If a plugin agent needs them, the agent file must live in `.claude/agents/` or `~/.claude/agents/` instead. (Details and the workaround under the plugin caveat below.)

4. **`name` must be unique across the entire agents tree** — project `.claude/agents/`, user `~/.claude/agents/`, and every plugin. Identity comes only from the `name` field, not the filename or subfolder. Two files with the same `name` in one scope: one is kept, the other discarded silently.

## Field-by-field

| Field | Req | Type / constraints | Controls | Set it when |
|---|---|---|---|---|
| `name` | **Yes** | Lowercase letters + hyphens. Unique across the whole agents tree (project + user + plugins). Filename need NOT match. | The identifier. Other agents and `Agent(agent_type)` allowlists reference it; hooks receive it as `agent_type`; `@agent-<name>` invokes it. | Always. Make it descriptive of the job (`test-runner`, `db-reader`), lowercase-hyphen, and confirm nothing else in the tree uses it. |
| `description` | **Yes** | Plain text, third person. | When Claude auto-delegates here. This is the trigger document. | Always. Name the specific phrasings/contexts that should route here; add "use proactively" / `PROACTIVELY` for automatic delegation. See "Writing the description" below. |
| `tools` | No | Comma-separated allowlist of tool names; MCP patterns allowed; `Agent(...)` syntax allowed. **Omitting it inherits ALL tools** (incl. MCP). | The exact tool pool (allowlist). | You want least privilege — list only what the job needs. Omit only when the agent genuinely needs everything. Don't list `Skill` here to preload skills; use `skills`. |
| `disallowedTools` | No | Same syntax as `tools`. **Applied before `tools`.** | Removes tools from the inherited-or-specified pool (denylist). | You want "everything except a few" (e.g. `Write, Edit` for a near-full agent that must not mutate files), or to strip one MCP server with `mcp__<server>`. |
| `model` | No (default `inherit`) | `sonnet` \| `opus` \| `haiku` \| `fable` \| full model id (e.g. `claude-opus-4-8`, `claude-sonnet-4-6`) \| `inherit`. | Which model runs the subagent. | The job wants a different model than the session — `haiku` for cheap scoped lookups, `opus` for hard reasoning. Leave `inherit` to track the session. Resolution order below. |
| `effort` | No (inherits session) | `low` \| `medium` \| `high` \| `xhigh` \| `max` (available levels depend on the model). | Reasoning depth and tool-use propensity while this subagent is active; overrides session effort. | Almost always set it deliberately — **this is the dominant capability lever on 4.8**, and a subagent is the one artifact where you bake it into frontmatter. `xhigh` for hard coding/agentic; `high` as the reasoning-sensitive default; `low`/`medium` for cheap scoped helpers. |
| `permissionMode` | No | `default` \| `acceptEdits` \| `auto` \| `dontAsk` \| `bypassPermissions` \| `plan`. **Ignored for plugin agents.** | How the subagent handles permission prompts. | The agent needs a non-default stance (e.g. `plan` for a read-only planner that may `ExitPlanMode`; `acceptEdits` for an autonomous editor). A stricter *parent* mode takes precedence — see below. |
| `maxTurns` | No | Integer. | Caps the number of agentic turns before the subagent stops. | You want a hard ceiling on a loop-prone or cost-sensitive agent. |
| `skills` | No | YAML list of skill names. | **Preloads the FULL content** of each named skill into the subagent's context at startup (not just the description). | The agent needs specific domain knowledge up front (team API conventions, error-handling patterns). Cannot preload a skill with `disable-model-invocation: true` (skipped + logged). The agent can still invoke other skills via the Skill tool at runtime. |
| `mcpServers` | No | YAML list; each entry is a string referencing an already-configured server, or an inline `{name: {config}}` using `.mcp.json` schema (`stdio`/`http`/`sse`/`ws`). **Ignored for plugin agents.** | MCP servers available to this subagent. Inline servers connect at agent start, disconnect at finish. | The agent needs an MCP server the main conversation doesn't have, OR you want to keep a server's tool descriptions out of the main context (define it inline here, not in `.mcp.json`). |
| `hooks` | No | YAML hook config (event → matcher → hooks). **Ignored for plugin agents.** | Lifecycle hooks scoped to this subagent only; cleaned up when it finishes. `Stop` is converted to `SubagentStop` at runtime. | You need determinism the model shouldn't be trusted to enforce — `PreToolUse` to gate Bash, `PostToolUse` to lint after edits, `Stop` to verify completion. |
| `memory` | No | `user` \| `project` \| `local`. | Gives the agent a persistent memory directory; **auto-enables Read/Write/Edit**; injects the first ~200 lines / 25KB of `MEMORY.md` into its prompt. | Knowledge should compound across runs (recurring codebase patterns, debugging insights). `project` is the recommended default. Don't set it for one-shot work. Locations + scope table below. |
| `background` | No (default `false`) | Boolean. | `true` always runs this agent as a background (async, concurrent) task. | The work is long and the user should keep working. Background agents auto-deny anything that would prompt, so they need permissions pre-granted. |
| `isolation` | No | `worktree`. | Runs the agent in a temporary git worktree — an isolated copy of the repo, branched from your default branch (not the parent's `HEAD`). Auto-cleaned if the agent makes no changes. | Multiple file-mutating agents run in parallel and must not clobber each other's checkout. |
| `color` | No | `red` \| `blue` \| `green` \| `yellow` \| `purple` \| `orange` \| `pink` \| `cyan`. | Display color in the task list and transcript. Cosmetic. | You want visual identification when several subagent types run. Purely optional. |
| `initialPrompt` | No | String. Commands and skills in it are processed. | Auto-submitted as the first user turn **only when this agent runs as the main session agent** (via `--agent` or the `agent` setting). Prepended to any user-provided prompt. | The agent is meant to be launched as a whole-session `--agent` and should always start from a fixed seed message. No effect when spawned as an ordinary subagent. |
| `prompt` | n/a | String (JSON/CLI only). | The system prompt. **This is the `--agents`/SDK-JSON equivalent of the markdown body.** | Only when defining an agent via `--agents` JSON or the SDK `agents` option instead of a `.md` file. In a file-based agent, the body *is* the prompt — don't add a `prompt` field. |

## Tool inheritance — a worked ordering

Given a main conversation with tools `{Read, Write, Edit, Bash, Grep, Glob, mcp__github__*, mcp__slack__*}`:

```yaml
# A) tools omitted, disallowedTools omitted
#    -> inherits ALL of the above (including both MCP servers)

# B) disallowedTools: Write, Edit
disallowedTools: Write, Edit
#    -> {Read, Bash, Grep, Glob, mcp__github__*, mcp__slack__*}  (everything minus Write/Edit)

# C) tools: Read, Grep, Glob
tools: Read, Grep, Glob
#    -> {Read, Grep, Glob}  (allowlist; no MCP, no Bash)

# D) both set — disallowedTools applied FIRST, then tools resolves against remainder
disallowedTools: mcp__github
tools: Read, Bash, mcp__github__create_issue
#    -> {Read, Bash}
#       mcp__github__create_issue is requested by `tools` but was already
#       removed by `disallowedTools: mcp__github`, so it's gone. Listed in
#       both = removed.
```

**MCP tool patterns** (valid in both `tools` and `disallowedTools`):
- `mcp__<server>` or `mcp__<server>__*` — every tool from that server
- `mcp__<server>__<tool>` — one specific tool
- `mcp__*` — in `disallowedTools` only, removes every MCP tool from every server

## `Agent(agent_type)` — restricting which subagents can be spawned

Only meaningful when an agent runs as the **main thread** via `claude --agent`. In the `tools` field:

```yaml
tools: Agent(worker, researcher), Read, Bash   # allowlist: only these two types may be spawned
tools: Agent, Read, Bash                        # may spawn ANY subagent type
# (Agent omitted entirely)                       -> cannot spawn any subagent
```

Inside an ordinary **subagent** definition, listing `Agent` enables spawning nested subagents, but any type list inside the parentheses is **ignored**. Nested depth is capped at 5 levels (an agent at depth 5 doesn't receive the Agent tool); the limit is fixed. To block one specific subagent globally, use `permissions.deny: ["Agent(name)"]` in settings instead.

## Model resolution order

`model: inherit` is the default. When Claude resolves which model a subagent runs, in priority order:

1. `CLAUDE_CODE_SUBAGENT_MODEL` env var, if set
2. The per-invocation `model` parameter Claude passes when spawning
3. The subagent definition's `model` frontmatter
4. The main conversation's model

Current aliases: `sonnet`, `opus`, `haiku`, `fable`. Full ids (e.g. `claude-opus-4-8`) accept the same values as `--model`. Pin a full id only when you need a specific version; aliases track the current default and age better.

## `memory` — scopes and behavior

| Scope | Location | Use when |
|---|---|---|
| `user` | `~/.claude/agent-memory/<name>/` | Knowledge applies across all projects. |
| `project` | `.claude/agent-memory/<name>/` | Project-specific, shareable via version control. **Recommended default.** |
| `local` | `.claude/agent-memory-local/<name>/` | Project-specific, must not be checked in. |

When enabled, the agent's prompt gains read/write instructions for the directory, the first ~200 lines / 25KB of `MEMORY.md` is injected, and Read/Write/Edit are auto-enabled. Put memory-maintenance instructions in the body so the agent curates its own notes. Only worth it when learnings genuinely compound — for one-shot work it just adds tokens and grants write tools you may not want.

## `permissionMode` — modes and parent precedence

| Mode | Behavior |
|---|---|
| `default` | Standard permission checking with prompts. |
| `acceptEdits` | Auto-accept file edits and common filesystem commands within the working directory / additional dirs. |
| `auto` | A background classifier reviews commands and protected-directory writes. |
| `dontAsk` | Auto-deny permission prompts (explicitly allowed tools still work). |
| `bypassPermissions` | Skip permission prompts. Use with caution — can write to `.git`, `.claude`, etc. |
| `plan` | Read-only exploration; this is the one mode where `ExitPlanMode` becomes available. |

A stricter **parent** mode wins: if the parent runs `bypassPermissions` or `acceptEdits`, that takes precedence and the subagent's `permissionMode` can't override it. If the parent runs `auto`, the subagent inherits auto mode and its own `permissionMode` is ignored.

## Plugin caveat (call this out before shipping a plugin agent)

For subagents loaded **from a plugin**, these three fields are silently ignored:
- `hooks`
- `mcpServers`
- `permissionMode`

There is no error. If a plugin agent needs any of them, copy the agent file into `.claude/agents/` or `~/.claude/agents/` (where it loses plugin scoping but gains the fields). For permissions specifically, you can instead add rules to `permissions.allow` in `settings.json`/`settings.local.json`, but those apply to the whole session, not just the agent.

## Writing the `description` (the field that decides delegation)

Claude reads each subagent's `name` + `description` to decide when to hand off. It is a trigger document for the model, not a human summary.

- **Third person.** "Reviews…", "Runs…", "Researches…" — not "I review" or "You can use this to…".
- **Name the trigger contexts and phrasings** that should route here — the situations Claude will be in, in the words it'll see.
- **Add "use proactively" / `PROACTIVELY`** when you want automatic delegation without the user naming the agent.
- **Include a NOT-boundary** when a sibling agent should handle adjacent work, so Claude routes correctly.

```yaml
description: >-
  Runs the test suite and reports only failing tests with their error
  output. Use proactively after code changes or when the user asks to run
  tests, check the build, or verify a fix. Not for writing new tests —
  that's the test-author agent.
```

## Scopes & precedence (where the file lives)

| Location | Scope | Priority |
|---|---|---|
| Managed settings `.claude/agents/` | Organization-wide | 1 (highest) |
| `--agents` CLI flag (JSON) | Current session | 2 |
| `.claude/agents/` | Current project | 3 |
| `~/.claude/agents/` | All your projects | 4 |
| Plugin `agents/` directory | Where plugin is enabled | 5 (lowest) |

Same `name` in two scopes → higher priority wins. Project scope is discovered by walking up from the cwd; the definition closest to the working directory wins among nested project dirs (v2.1.178+). Plugin subfolders become part of the scoped id (`plugin:subfolder:name`); project/user subfolders do **not** affect identity.

## Reference Docs
- https://code.claude.com/docs/en/sub-agents
- https://github.com/shanraisshan/claude-code-best-practice/blob/main/best-practice/claude-subagents.md
- https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-4-8