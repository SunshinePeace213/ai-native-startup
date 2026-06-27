# Claude Code Hooks — Authoritative Reference

> **Source**: Official docs at <https://code.claude.com/docs/en/hooks> (fetched 2026-06-28).
> This file supplements that reference with project-specific rationale for the
> `PreToolUse` guard hook that enforces the no-`Co-Authored-By` trailer policy.

---

## Table of Contents

1. [What Are Hooks?](#1-what-are-hooks)
2. [Configuration Structure](#2-configuration-structure)
3. [Settings Locations and Precedence](#3-settings-locations-and-precedence)
4. [Matchers](#4-matchers)
5. [Hook Handler Types](#5-hook-handler-types)
6. [Lifecycle Events](#6-lifecycle-events)
7. [Stdin JSON Payload Schema](#7-stdin-json-payload-schema)
8. [Exit-Code Semantics](#8-exit-code-semantics)
9. [JSON Output and Decision Fields](#9-json-output-and-decision-fields)
10. [Environment Variables and Path Placeholders](#10-environment-variables-and-path-placeholders)
11. [Why PreToolUse Is the Correct Lifecycle for the Guard Hook](#11-why-pretooluse-is-the-correct-lifecycle-for-the-guard-hook)
12. [Reference: Guard Hook for This Repo](#12-reference-guard-hook-for-this-repo)

---

## 1. What Are Hooks?

Hooks are user-defined shell commands, HTTP endpoints, or LLM prompts that Claude
Code executes automatically at specific points in a session lifecycle. They let you:

- Block dangerous or policy-violating tool calls **before** they execute (`PreToolUse`).
- Validate or transform tool inputs and outputs (`PostToolUse`).
- Inject environment context at session start (`SessionStart`).
- Run side-effects like logging or cleanup (`SessionEnd`, `PostToolUse`).
- Escalate decisions to users via permission dialogs (`PermissionRequest`).

Hooks are deterministic entry points into the harness; unlike instructions in
`CLAUDE.md`, they run as external processes and are therefore not subject to Claude's
discretion or forgetfulness.

---

## 2. Configuration Structure

Hooks are declared in JSON under the `"hooks"` key in any settings file:

```json
{
  "hooks": {
    "EventName": [
      {
        "matcher": "ToolName",
        "hooks": [
          {
            "type": "command",
            "command": "${CLAUDE_PROJECT_DIR}/.claude/hooks/my-script.sh"
          }
        ]
      }
    ]
  }
}
```

Three nesting levels:

| Level | Key | Purpose |
|-------|-----|---------|
| 1 | `EventName` | Which lifecycle event triggers this group |
| 2 | matcher object | Filters which tool calls / events enter this group |
| 3 | hook definition | The actual handler (command, http, mcp_tool, prompt, agent) |

One event can have multiple matcher groups; each matcher group can have multiple
handler hooks; each runs in the order listed.

---

## 3. Settings Locations and Precedence

Claude Code merges hook configuration from several files. More-specific settings
layers take precedence; user-level settings apply across all projects.

| File | Scope | Committed to repo? | Typical use |
|------|-------|--------------------|-------------|
| `~/.claude/settings.json` | All projects for this user | No | Personal defaults, global hooks |
| `.claude/settings.json` | This project only | **Yes** | Team-wide hooks and permissions |
| `.claude/settings.local.json` | This project only | No (gitignored) | Machine-local overrides, secrets |
| Plugin `hooks/hooks.json` | When the plugin is enabled | Via plugin | Plugin-provided automation |
| Skill / agent frontmatter | While that skill/agent is active | Via skill file | Ephemeral, scoped hooks |

**Precedence (highest to lowest)**: `settings.local.json` > `.claude/settings.json`
> `~/.claude/settings.json` > plugin hooks.

For this repo the `PreToolUse` guard hook lives in `.claude/settings.local.json`
because it references a machine-local path via `$CLAUDE_PROJECT_DIR` and must not
be committed unilaterally.

---

## 4. Matchers

A matcher is a string that filters the events delivered to a hook group. Its meaning
depends on the event type.

### Tool events (PreToolUse, PostToolUse, PostToolUseFailure, PermissionRequest)

Matchers are compared against `tool_name`:

```json
{ "matcher": "Bash" }            // exact match — only the Bash tool
{ "matcher": "Edit|Write" }      // pipe-separated alternatives
{ "matcher": "^Notebook" }       // regex — any tool whose name starts with Notebook
{ "matcher": "mcp__memory__.*" } // regex — any tool on the memory MCP server
{ "matcher": "" }                // empty string — matches ALL tools
```

Built-in tool names used as matchers:

| Matcher string | Matches |
|----------------|---------|
| `Bash` | Shell command execution |
| `Edit` | In-place file edits |
| `Write` | File creation / overwrite |
| `Read` | File reads |
| `Glob` | File pattern search |
| `Grep` | Content search |
| `Agent` | Subagent spawning |
| `WebFetch` | HTTP fetches |
| `mcp__<server>__<tool>` | Any MCP-provided tool |

### SessionStart matchers

Match on the reason the session started:

- `startup` — brand-new session
- `resume` — resuming a paused session
- `clear` — session cleared (`/clear`)
- `compact` — post-compaction resume

### Notification matchers

Match on the notification category:

- `permission_prompt` — a permission dialog is about to appear
- `idle_prompt` — Claude is waiting for user input
- `auth_success` — authentication completed
- (and others)

---

## 5. Hook Handler Types

### 5.1 Command hooks (most common)

```json
{
  "type": "command",
  "command": "${CLAUDE_PROJECT_DIR}/.claude/hooks/validate.sh",
  "timeout": 30,
  "async": false
}
```

- **Shell form** (no `args`): the string is passed to the shell, so variables,
  pipes, and redirects are expanded.
- **Exec form** (with `args`): the command is exec'd directly — no shell
  interpretation, paths are safe literals.

The harness writes the event payload as JSON to the hook's stdin. The hook's stdout
and exit code drive the harness decision (see §8 and §9).

### 5.2 HTTP hooks

```json
{
  "type": "http",
  "url": "http://localhost:8080/hooks/pre-tool-use",
  "headers": { "Authorization": "Bearer $MY_TOKEN" },
  "allowedEnvVars": ["MY_TOKEN"],
  "timeout": 30
}
```

The payload is POSTed as JSON. The response body is interpreted the same way as
command stdout (see §9).

### 5.3 MCP tool hooks

```json
{
  "type": "mcp_tool",
  "server": "my_server",
  "tool": "security_scan",
  "input": { "file_path": "${tool_input.file_path}" }
}
```

Calls a tool on a connected MCP server. The tool's output is treated as the hook
response.

### 5.4 Prompt hooks

```json
{
  "type": "prompt",
  "prompt": "Is this command safe? $ARGUMENTS",
  "model": "fast-model"
}
```

Asks Claude to evaluate the event. Useful for nuanced policy checks where regex is
insufficient. Default timeout: 30 s.

### 5.5 Agent hooks (experimental)

Spawns a subagent to perform verification. Use sparingly; adds latency to every
matched tool call.

---

## 6. Lifecycle Events

### Overview table

| Event | Fires | Blockable? | Typical use |
|-------|-------|------------|-------------|
| `SessionStart` | Once, when a session begins or resumes | No | Load context, set env vars |
| `UserPromptSubmit` | Every time the user submits a prompt | Yes | Validate / enrich prompt |
| `PreToolUse` | Before each tool call | **Yes** | Block policy-violating commands |
| `PermissionRequest` | When a permission dialog would appear | Yes | Auto-approve/deny permissions |
| `PostToolUse` | After each tool call succeeds | Partial* | Log, validate output |
| `PostToolUseFailure` | After each tool call fails | No | Error handling, alerting |
| `Stop` | When Claude finishes a turn | Yes (with feedback) | Run tests, inject follow-up |
| `SubagentStop` | When a subagent finishes its turn | Yes (with feedback) | Same as Stop but for subagents |
| `Notification` | On various notification events | Varies | Routing, custom notification |
| `PreCompact` | Before context compaction | No | Save state before compaction |
| `PostCompact` | After context compaction | No | Restore state |
| `SessionEnd` | When the session terminates | No | Cleanup, final logging |

*PostToolUse can set `decision: "block"` to inject an error into the conversation,
but the tool already ran — the side-effect is not reversed.

---

### 6.1 SessionStart

Fires once when Claude Code starts or resumes a session. Use it to:

- Populate environment variables via `CLAUDE_ENV_FILE`.
- Log session metadata.
- Load project state into context.

Matchers: `startup`, `resume`, `clear`, `compact`.

No stdin tool payload; only the common session fields (§7.1).

---

### 6.2 UserPromptSubmit

Fires after the user submits a prompt but before Claude processes it.

**Blockable**: yes — exit 2 prevents Claude from seeing the prompt; stderr is shown
to the user.

Use cases: rate limiting, content filtering, automatically appending context (e.g.,
current git branch).

JSON decision: `{ "decision": "block", "reason": "..." }` or
`{ "hookSpecificOutput": { "hookEventName": "UserPromptSubmit", "additionalContext": "..." } }`.

---

### 6.3 PreToolUse

Fires immediately **before** a tool call is dispatched to the execution layer. The
tool has not run yet.

**Blockable**: yes — this is the only lifecycle event that can prevent a tool from
executing.

**Stdin payload** includes the common fields plus `tool_name` and `tool_input`
(§7.2). For the Bash tool, `tool_input.command` is the shell command string.

Decision options (via `hookSpecificOutput.permissionDecision`):

| Value | Effect |
|-------|--------|
| `"deny"` | Block the tool call; `permissionDecisionReason` is fed back to Claude |
| `"allow"` | Approve unconditionally (skips further permission checks) |
| `"ask"` | Escalate to the user via a permission dialog |
| `"defer"` | Pass to the normal permission system |

Alternatively, exit 2 with a message on stderr — Claude receives the message and
retries.

---

### 6.4 PostToolUse

Fires after a tool call **succeeds**. The tool has already run; its output is
available in the payload.

**Not blockable in the undo sense**: the tool already executed. You can set
`decision: "block"` to inject an error context back to Claude (e.g., "output
contains secrets"), and you can rewrite `updatedToolOutput` to mask sensitive data.

Use cases: output validation, secret redaction, logging, test execution after file
edits.

```json
{
  "decision": "block",
  "reason": "Tool output contains an API key",
  "hookSpecificOutput": {
    "hookEventName": "PostToolUse",
    "updatedToolOutput": "[REDACTED]",
    "additionalContext": "Never include secrets in tool output."
  }
}
```

---

### 6.5 Stop

Fires when Claude finishes a response turn (i.e., Claude stops and awaits user
input).

**Blockable**: yes, with feedback — return `{ "hookSpecificOutput": { "hookEventName": "Stop", "additionalContext": "..." } }` to inject follow-up context and prevent the stop (Claude continues with that context).

Use cases: automatically run tests after code edits, enforce checklist completion,
add a summary to the transcript.

---

### 6.6 SubagentStop

Same semantics as `Stop`, but fires when a spawned subagent finishes its turn rather
than the main session. Useful for orchestrator-level validation of subagent work.

---

### 6.7 Notification

Fires for harness-generated notification events. The matcher selects specific
notification types (`permission_prompt`, `idle_prompt`, `auth_success`, etc.).

Use cases: custom desktop notifications, Slack alerts, audit logs.

---

### 6.8 PreCompact

Fires before Claude Code compacts the conversation context. No blockable decision;
use for snapshotting state you want to preserve across compaction.

---

### 6.9 SessionEnd

Fires once when the session terminates (user exits, `/exit`, or process kill). No
blockable decision — only side-effects are meaningful here (audit logs, cleanup
scripts).

---

## 7. Stdin JSON Payload Schema

Every hook receives a JSON object on stdin. The schema has a common base plus
event-specific fields.

### 7.1 Common fields (all events)

```json
{
  "session_id": "abc123def456",
  "transcript_path": "/home/user/.claude/projects/.../transcript.jsonl",
  "cwd": "/home/user/my-project",
  "permission_mode": "auto",
  "hook_event_name": "PreToolUse",
  "effort": {
    "level": "xhigh"
  },
  "agent_id": "subagent-xyz",
  "agent_type": "general-purpose"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `session_id` | string | Unique ID for the current Claude Code session |
| `transcript_path` | string | Absolute path to the JSONL conversation transcript |
| `cwd` | string | Working directory of the Claude Code process |
| `permission_mode` | string | Active permission mode: `default`, `plan`, `auto`, `dontAsk`, `bypassPermissions` |
| `hook_event_name` | string | The event that fired (e.g., `"PreToolUse"`) |
| `effort` | object | Current effort level (`level`: `low`, `medium`, `high`, `xhigh`, `max`) |
| `agent_id` | string | ID of the active agent or subagent (empty for main session) |
| `agent_type` | string | Type of agent (e.g., `"general-purpose"`, `"Explore"`) |

### 7.2 Tool event fields (PreToolUse, PostToolUse, etc.)

In addition to the common fields:

```json
{
  "tool_name": "Bash",
  "tool_input": {
    "command": "git commit -m \"fix: something\""
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `tool_name` | string | Exact name of the tool being called (e.g., `"Bash"`, `"Edit"`, `"Write"`) |
| `tool_input` | object | Tool-specific parameters |
| `tool_input.command` | string | (Bash only) The shell command string passed to the Bash tool |
| `tool_input.file_path` | string | (Edit/Write/Read) The file path being operated on |
| `tool_input.old_string` | string | (Edit) The string being replaced |
| `tool_input.new_string` | string | (Edit) The replacement string |

For MCP tools the `tool_name` is `mcp__<server>__<tool>` and `tool_input` matches
the tool's parameter schema.

### 7.3 PostToolUse additional fields

```json
{
  "tool_output": "$ git commit ...\n[main abc1234] fix: something\n",
  "tool_success": true
}
```

| Field | Type | Description |
|-------|------|-------------|
| `tool_output` | string | The stdout/result from the tool call |
| `tool_success` | boolean | Whether the tool call succeeded |

---

## 8. Exit-Code Semantics

When a hook is a shell command, its exit code tells the harness how to proceed.

| Exit code | Harness interpretation | What Claude sees |
|-----------|----------------------|------------------|
| `0` | Success | Harness parses stdout for a JSON decision (§9); if stdout is empty or not JSON, the tool call proceeds normally |
| `2` | **Blocking error** | Tool call is **blocked** (if the event is blockable); stderr content is fed back to Claude as an error message so it can retry or adjust |
| Any other non-zero | Non-blocking error | Stderr is shown in the terminal / logs but the tool call **continues** |

**Key rule**: only exit code `2` blocks. Exit code `1` (or any other non-zero
except `2`) is advisory — execution continues.

This means a hook that exits `1` on an unexpected error (e.g., a bash `set -e`
failure) will NOT accidentally block tool calls. To intentionally block you must
exit exactly `2`.

---

## 9. JSON Output and Decision Fields

A command hook may write JSON to stdout to influence harness behavior. If stdout is
empty or unparseable, the exit code alone governs.

### 9.1 Universal fields (any event)

```json
{
  "continue": false,
  "stopReason": "Build failed",
  "suppressOutput": false,
  "systemMessage": "Warning: running in production mode",
  "terminalSequence": "\033]0;My Title\007"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `continue` | boolean | `false` → stop Claude's current turn after this hook |
| `stopReason` | string | Message shown when `continue` is `false` |
| `suppressOutput` | boolean | Suppress hook's own output from the terminal |
| `systemMessage` | string | Inject a system message into Claude's context |
| `terminalSequence` | string | Emit an allowed terminal escape sequence |

### 9.2 PreToolUse decisions

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "deny",
    "permissionDecisionReason": "Blocked: commit contains forbidden trailer.",
    "updatedInput": {
      "command": "git commit -m 'clean message'"
    }
  }
}
```

| Field | Values | Description |
|-------|--------|-------------|
| `permissionDecision` | `"deny"`, `"allow"`, `"ask"`, `"defer"` | `deny` blocks the call; `allow` approves; `ask` escalates to user; `defer` hands off to normal permission system |
| `permissionDecisionReason` | string | Reason shown to Claude (or user on `ask`) |
| `updatedInput` | object | Optional replacement for `tool_input` — rewrite the command before execution |

Alternatively, exiting `2` with a message on stderr is equivalent to
`permissionDecision: "deny"` with the stderr text as the reason. Exit 2 is simpler
for most guard hooks.

### 9.3 PostToolUse decisions

```json
{
  "decision": "block",
  "reason": "Output contains an API key",
  "hookSpecificOutput": {
    "hookEventName": "PostToolUse",
    "updatedToolOutput": "[REDACTED]",
    "additionalContext": "Never include secrets in tool output."
  }
}
```

| Field | Values | Description |
|-------|--------|-------------|
| `decision` | `"block"` | Inject an error context into Claude's turn |
| `reason` | string | Why the output is blocked |
| `updatedToolOutput` | string | Replace the tool's output in Claude's view |
| `additionalContext` | string | Extra context injected after the tool response |

### 9.4 Stop / SubagentStop decisions

```json
{
  "hookSpecificOutput": {
    "hookEventName": "Stop",
    "additionalContext": "All tests passed (1234/1234). You may proceed."
  }
}
```

Returning `additionalContext` prevents the stop and continues Claude's turn with
that context appended.

### 9.5 UserPromptSubmit decisions

```json
{
  "decision": "block",
  "reason": "Prompt references a deleted file.",
  "hookSpecificOutput": {
    "hookEventName": "UserPromptSubmit",
    "additionalContext": "Available files: src/index.ts, src/utils.ts"
  }
}
```

---

## 10. Environment Variables and Path Placeholders

Hook commands receive a copy of the Claude Code process environment plus these
additions:

| Variable | Value | Usage |
|----------|-------|-------|
| `$CLAUDE_PROJECT_DIR` | Absolute path to the project root | Reference project files in hook commands regardless of `cwd` |
| `$CLAUDE_PLUGIN_ROOT` | Plugin installation directory | Used inside plugin-provided hooks |
| `$CLAUDE_PLUGIN_DATA` | Plugin persistent data directory | Plugin data storage |

These variables are also available as `${...}` placeholders in the `command` field
of JSON hook definitions:

```json
{
  "command": "\"${CLAUDE_PROJECT_DIR}\"/.claude/hooks/block-coauthor-trailer.sh"
}
```

The quotes around the placeholder guard against paths with spaces.

`$CLAUDE_PROJECT_DIR` is particularly important for hooks wired via
`settings.local.json` because the hook command is evaluated at the project root
regardless of which subdirectory Claude is working in when the tool call fires.

---

## 11. Why PreToolUse Is the Correct Lifecycle for the Guard Hook

This section justifies the lifecycle choice for the hook that enforces the
no-`Co-Authored-By` trailer policy.

### The goal

Block any `git commit`, `git push`, or `gh pr create` command that carries the
string `Co-Authored-By: Claude` **before the command runs**, so the trailer never
reaches the git history or a GitHub PR.

### Lifecycle analysis

| Event | When it fires | Can it prevent the command? |
|-------|--------------|----------------------------|
| `PreToolUse` | Before the tool call executes | **Yes** — exit 2 blocks the call |
| `PostToolUse` | After the tool call succeeds | No — the commit/push already happened |
| `PostToolUseFailure` | After the tool call fails | No — only fires on failure, not on success |
| `Stop` | After Claude finishes a response turn | No — fires at turn boundary, not per-tool-call |
| `SubagentStop` | After a subagent's turn | No — same as Stop |
| `SessionEnd` | When the session exits | No — fires at session teardown, not per-tool-call |
| `UserPromptSubmit` | Before Claude processes a user prompt | No — fires before Claude acts, not before each tool call |
| `PreCompact` | Before context compaction | No — unrelated to tool execution |

**Conclusion**: `PreToolUse` is the only event that:
1. Fires for every individual tool call.
2. Fires **before** the tool executes (so the git command has not yet run).
3. Supports a blocking decision (exit 2 / `permissionDecision: "deny"`).

Every other candidate either fires too late (PostToolUse — the commit is done) or
fires at the wrong granularity (Stop, SessionEnd — these fire at turn/session
boundaries, not per-tool-call, and they cannot intercept an individual Bash
invocation).

### The retry loop

When the hook exits 2, its stderr is fed back to Claude as an error message in the
conversation. Claude sees something like:

```
Blocked: this git/gh command includes a 'Co-Authored-By: Claude ...' trailer.
Repo policy (GIT-COMMIT-PR-MESSAGE.md): commit/PR messages must NOT carry the Claude attribution trailer.
Remove the 'Co-Authored-By: Claude ...' line from the message and run the command again.
```

Claude retries the tool call with a clean commit message. This is the intended
behaviour: the hook is not just a hard stop but a corrective feedback loop.

### Why the matcher targets "Bash" specifically

The `matcher: "Bash"` ensures the hook only fires on Bash tool calls. Git and gh
commands always flow through the Bash tool in Claude Code, so this matcher
correctly captures them. A broader matcher (empty string) would run the script on
every tool call (file reads, writes, etc.), adding unnecessary overhead.

---

## 12. Reference: Guard Hook for This Repo

### Hook script: `.claude/hooks/block-coauthor-trailer.sh`

```bash
#!/usr/bin/env bash
# PreToolUse guard: block git/gh commands that carry the Claude Co-Authored-By trailer.
# Exit 2 => deny the tool call; stderr is fed back to Claude so it retries clean.
set -euo pipefail
payload="$(cat)"

# Act only on Bash tool calls that invoke git or gh.
printf '%s' "$payload" | grep -Eq '"tool_name"[[:space:]]*:[[:space:]]*"Bash"' || exit 0
printf '%s' "$payload" | grep -Eq '\b(git|gh)\b' || exit 0

# Block when the forbidden trailer is present.
if printf '%s' "$payload" | grep -q 'Co-Authored-By: Claude'; then
  {
    echo "Blocked: this git/gh command includes a 'Co-Authored-By: Claude ...' trailer."
    echo "Repo policy (GIT-COMMIT-PR-MESSAGE.md): commit/PR messages must NOT carry the Claude attribution trailer."
    echo "Remove the 'Co-Authored-By: Claude ...' line from the message and run the command again."
  } >&2
  exit 2
fi
exit 0
```

The script reads the full payload from stdin, checks `tool_name == "Bash"` and
that the command contains `git` or `gh` (fast-exits on anything else), then blocks
on the forbidden trailer string with a corrective message.

### settings.local.json hook configuration

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/block-coauthor-trailer.sh"
          }
        ]
      }
    ]
  }
}
```

### Verification

Simulate `PreToolUse` payloads directly:

```bash
# Should exit 2 (blocked):
printf '{"tool_name":"Bash","tool_input":{"command":"git commit -m \"x\n\nCo-Authored-By: Claude <noreply@anthropic.com>\""}}' \
  | .claude/hooks/block-coauthor-trailer.sh; echo "exit=$?"

# Should exit 0 (clean message, no trailer):
printf '{"tool_name":"Bash","tool_input":{"command":"git commit -m \"fix: clean message\""}}' \
  | .claude/hooks/block-coauthor-trailer.sh; echo "exit=$?"

# Should exit 0 (not a git/gh command):
printf '{"tool_name":"Bash","tool_input":{"command":"echo Co-Authored-By: Claude"}}' \
  | .claude/hooks/block-coauthor-trailer.sh; echo "exit=$?"
```

---

*Last updated: 2026-06-28. Source: <https://code.claude.com/docs/en/hooks>.*
