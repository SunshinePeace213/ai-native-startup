---
source: https://code.claude.com/docs/en/tools-reference
fetched: 2026-07-05
---
> **In here:** Built-in tools catalog · Permission requirements · MCP & skill integration

# Tools reference

> Complete reference for the tools Claude Code can use, including permission requirements and per-tool behavior.

Claude Code has access to a set of built-in tools that help it understand and modify your codebase. The tool names are the exact strings you use in [permission rules](/en/permissions#tool-specific-permission-rules), [subagent tool lists](/en/sub-agents), and [hook matchers](/en/hooks). To disable a tool entirely, add its name to the `deny` array in your [permission settings](/en/permissions#tool-specific-permission-rules).

To add custom tools, connect an [MCP server](/en/mcp). To extend Claude with reusable prompt-based workflows, write a [skill](/en/skills), which runs through the existing `Skill` tool rather than adding a new tool entry.

| Tool                   | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 | Permission required |
| :--------------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :------------------ |
| `Agent`                | Spawns a [subagent](/en/sub-agents) with its own context window to handle a task. See [Agent tool behavior](#agent-tool-behavior)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           | No                  |
| `Artifact`             | Publishes an HTML or Markdown file as an [artifact](/en/artifacts): a private, interactive page on claude.ai. On Team and Enterprise plans, you can share it inside your organization. {/* plan-availability: feature=artifacts plans=pro,max,team,enterprise providers=anthropic */}Requires a Pro, Max, Team, or Enterprise plan and `/login` authentication; see [Availability](/en/artifacts#availability)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              | Yes                 |
| `AskUserQuestion`      | Asks multiple-choice questions to gather requirements or clarify ambiguity. {/* min-version: 2.1.200 */}Questions stay open until you answer them: there's no idle timeout by default. To have an idle dialog auto-continue instead, set the [`askUserQuestionTimeout`](/en/settings#available-settings) setting to `60s`, `5m`, or `10m`, either in your user `settings.json` or from the **Question auto-continue timeout** row in `/config`. Once the chosen idle time passes with no input, the dialog closes on its own: it submits any options you'd already selected and tells Claude you may be away from your keyboard, so Claude proceeds on its own judgment and can re-ask later. A countdown appears for the last 20 seconds. Any keypress restarts the timer, and so does a focused window on terminals that report focus. The timeout applies only to `AskUserQuestion`'s multiple-choice questions; permission prompts, including plan approval, never auto-resolve on idle. In v2.1.198 and v2.1.199, the dialog auto-continued after 60 seconds of idle by default, and [`CLAUDE_AFK_TIMEOUT_MS`](/en/env-vars#variables) was the only way to change that | No                  |
| `Bash`                 | Executes shell commands in your environment. See [Bash tool behavior](#bash-tool-behavior)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  | Yes                 |
| `CronCreate`           | Schedules a recurring or one-shot prompt within the current session. Tasks are session-scoped and restored on `--resume` or `--continue` if unexpired. See [scheduled tasks](/en/scheduled-tasks)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           | No                  |
| `CronDelete`           | Cancels a scheduled task by ID                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              | No                  |
| `CronList`             | Lists all scheduled tasks in the session                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    | No                  |
| `Edit`                 | Makes targeted edits to specific files. See [Edit tool behavior](#edit-tool-behavior)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       | Yes                 |
| `EnterPlanMode`        | Switches to plan mode to design an approach before coding                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   | No                  |
| `Memory`               | Stores text in long-term memory that persists across sessions. See [Memory tool behavior](#memory-tool-behavior)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             | No                  |
| `Monitor`              | Streams lines from a long-running background process as they arrive. See [Monitor tool behavior](#monitor-tool-behavior)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              | No                  |
| `Read`                 | Reads file contents. See [Read tool behavior](#read-tool-behavior)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           | Yes                 |
| `SendMessage`          | Sends a message to another agent or continues an agent from an earlier session. See [Agent messaging](/en/agent-messaging)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  | No                  |
| `Skill`                | Runs a [skill](/en/skills): a reusable prompt-based workflow, often with parameters. To add a new skill, see [skill authoring](/en/skills-authoring)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       | No                  |
| `TaskCreate`           | Create a task in the task list. Used for team orchestration. See [task tools](/en/task-tools)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              | No                  |
| `TaskDelete`           | Delete a task from the task list. Used for team orchestration. See [task tools](/en/task-tools)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | No                  |
| `TaskGet`              | Retrieve a task from the task list. Used for team orchestration. See [task tools](/en/task-tools)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           | No                  |
| `TaskList`             | List all tasks on the shared task board. Used for team orchestration. See [task tools](/en/task-tools)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      | No                  |
| `TaskStop`             | Stop a running background task. Used for team orchestration. See [task tools](/en/task-tools)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               | No                  |
| `TaskUpdate`           | Update a task on the task list. Used for team orchestration. See [task tools](/en/task-tools)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              | No                  |
| `WebFetch`             | Fetches content from a URL and processes it. See [WebFetch tool behavior](#webfetch-tool-behavior)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         | Yes                 |
| `Write`                | Creates a new file or overwrites an existing one. See [Write tool behavior](#write-tool-behavior)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           | Yes                 |

## Agent tool behavior

Agents are powerful for offloading work. Each agent has its own context window and can use a subset of your tools. Agents can also be asked to call other agents. The Agent tool spawns these agents in the Code CLI and on claude.ai.

**Subagent types**

- **General-purpose**: Has access to your full toolset (or the subset you configure).
- **Custom**: Created when the `Agent` tool is called with `custom_rules` (a string parameter). The agent runs the custom rules and has access to your full toolset.

**Agent isolation**

By default, agents on the same machine share the same git repository state. If you're working in parallel and need isolation, you can create each agent in its own git worktree with the `isolation: "worktree"` parameter.

**Agent messaging**

To continue work with an agent across sessions, use the `SendMessage` tool to resume an agent from a previous context. Agents can message back via `SendMessage` in a conversation.

**Custom rules**

You can pass custom rules to guide an agent's behavior. These rules run alongside your skill list, team rules, and base rules. The syntax is the same as [skill rules](/en/skills-authoring#rules).

**Spawning agents on claude.ai**

On claude.ai, agents are spawned with an `Agent` tool call, but they live as separate Claude conversations. You can link back to them from your main conversation in the UI.

## Bash tool behavior

Bash executes shell commands in the environment where Claude Code started.

**Exit codes and failures**

A command that exits with non-zero status is treated as a failure. Bash captures the error and reports it; Claude can then act on it. Some Claude Code [hooks](/en/hooks-guide) and [skills](/en/skills-authoring) are triggered by failures and can recover.

**Session state**

The working directory persists between Bash commands, but shell state (like exported variables) does not. Each Bash call is a fresh login shell.

**Sandboxing and credentials**

By default, Bash is sandboxed and cannot access the host machine's credentials or sensitive data (e.g., `~/.ssh`). You can opt into dangerous mode with the `dangerouslyDisableSandbox` parameter. Be cautious — dangerous mode gives Bash access to your entire system. See [Security](/en/security).

**Long-running processes**

For commands that take a long time, use the `Monitor` tool to stream output as lines arrive. This is preferred over `timeout` / `sleep` loops, which can exhaust the token budget.

**Output limits**

By default, Bash output is limited to 2 MB. Set the `outputLimit` parameter (in bytes) to increase (or decrease) this limit for specific commands. This applies only to stdout/stderr; Bash also writes large outputs to disk and returns the file path.

## Edit tool behavior

The Edit tool makes targeted replacements in existing files. It works line-by-line and preserves line numbers — the output shows what was changed.

**Reading before editing**

You cannot edit a file without reading it first (in the same session). This ensures Claude understands context before modifying.

**File path handling**

On Windows, the Edit tool treats `/` and `\` equivalently. Paths can be relative or absolute.

**Special characters and escaping**

When replacements include special regex characters (like `.`, `*`, `$`, `^`), they're treated as literal characters in the replacement and in the line search. No escaping is needed.

**Viewing the result**

After an Edit, the tool shows a diff-style output to confirm what changed. If you need the full file, use Read afterward.

**Multiple edits in one call**

You can make several independent edits in a single Edit call by passing an array of edits.

## Memory tool behavior

The Memory tool stores small amounts of structured information in a persistent file that survives session boundaries. This is useful for remembering decisions, preferences, or context from earlier work.

The Memory tool has three operations: **set**, **get**, and **delete**.

**Usage**

Each memory key is a short string. Memory values can be any JSON-serializable data: strings, numbers, booleans, objects, arrays, or `null`.

**Limits**

Memory storage is not unlimited. For large datasets, use files or a database instead. The memory tool is meant for preferences, decisions, or small notes — typically under 10 KB total per session.

**Privacy and sharing**

Memory is scoped to the project. It doesn't sync across machines and isn't shared between users.

## Monitor tool behavior

Monitor receives stdout as it arrives from a background process (a command you started with Bash's `run_in_background: true` parameter). Each line appears as a separate notification in Claude's view of the conversation.

**Relationship to polling**

Use Monitor to stream output from a long-running task as it happens, instead of polling or sleeping. This saves tokens and is more responsive.

**Notification format**

When Monitor receives a line, Claude gets a new notification (e.g., `<task-notification>`). These notifications appear in Claude's conversation timeline so it can react in real time.

## Read tool behavior

The Read tool opens files and returns their contents. It's constrained by performance (very large files are truncated) and by permission rules.

**File size limits**

Files under 1 MB are returned in full. Files 1–50 MB are returned with a note about truncation; read them in chunks with Bash tools if needed. Files larger than 50 MB cannot be read directly.

**Binary files**

The Read tool cannot read binary files. For media, use Bash to get file info or metadata.

**Symlinks**

Read follows symlinks transparently. If a symlink points outside the project, it's still readable if your permissions allow it.

**Newline handling**

Files are read as-is, preserving the system's line endings (`\n`, `\r\n`, etc.).

**Relative and absolute paths**

Paths can be relative (from the current working directory) or absolute.

## WebFetch tool behavior

WebFetch retrieves and summarizes content from a URL. It converts HTML to Markdown and runs a small language model on the result to answer your question about the content.

**Processing a URL**

When you fetch a URL, WebFetch:

1. Fetches the HTML
2. Converts it to Markdown
3. Passes it through a small, fast language model with your prompt
4. Returns the model's response

**Caching**

Responses are cached for 15 minutes, so repeated fetches of the same URL are fast.

**Redirects**

If the URL redirects to a different host, WebFetch tells you and provides the redirect URL. You can then fetch the new URL yourself if you want to.

**Limitations**

- WebFetch cannot access private or authenticated content (e.g., behind a login).
- It works best on pages with clear text content (news, docs, wikis).
- On very large pages, content may be summarized or truncated.

## Write tool behavior

The Write tool creates a new file or overwrites an existing one with the full content provided. It doesn't append or merge.

If the target path already exists, Claude must have read that file at least once in the current conversation before overwriting it. A Write to an unread existing file fails with an error. This constraint doesn't apply to new files.

Viewing the file with Bash also satisfies this requirement under the same rules described in [Edit tool behavior](#edit-tool-behavior).

For partial changes to an existing file, Claude uses Edit instead of Write.

## Check which tools are available

Your exact tool set depends on your provider, platform, and settings. To check what's loaded in a running session, ask Claude directly:

```text theme={null}
What tools do you have access to?
```

Claude gives a conversational summary. For exact MCP tool names, run `/mcp`.

<Note>
  The [advisor tool](/en/advisor) is a [server tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/advisor-tool) that the API runs, rather than a tool that Claude Code implements. It has no name you can reference in permission rules or hook matchers.
</Note>

## See also

* [MCP servers](/en/mcp): add custom tools by connecting external servers
* [Permissions](/en/permissions): permission system, rule syntax, and tool-specific patterns
* [Subagents](/en/sub-agents): configure tool access for subagents
* [Hooks](/en/hooks-guide): run custom commands before or after tool execution
