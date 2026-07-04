---
source: https://code.claude.com/docs/en/hooks
fetched: 2026-07-05
---
> **In here:** Hook events & lifecycle · Configuration schemas & formats · Async, HTTP & MCP hooks

# Hooks reference

> Reference for Claude Code hook events, configuration schema, JSON input/output formats, exit codes, async hooks, HTTP hooks, prompt hooks, and MCP tool hooks.

<Tip>
  For a quickstart guide with examples, see [Automate actions with hooks](/en/hooks-guide).
</Tip>

Hooks are user-defined shell commands, HTTP endpoints, or LLM prompts that execute automatically at specific points in Claude Code's lifecycle. Use this reference to look up event schemas, configuration options, JSON input/output formats, and advanced features like async hooks, HTTP hooks, and MCP tool hooks. If you're setting up hooks for the first time, start with the [guide](/en/hooks-guide) instead.

## Hook lifecycle

Hooks fire at specific points during a Claude Code session. When an event fires and a matcher matches, Claude Code passes JSON context about the event to your hook handler. For command hooks, input arrives on stdin. For HTTP hooks, it arrives as the POST request body. Your handler can then inspect the input, take action, and optionally return a decision.

Events fall into three cadences:

* once per session: `SessionStart` and `SessionEnd`
* once per turn: `UserPromptSubmit`, `Stop`, and `StopFailure`
* on every tool call inside the agentic loop: `PreToolUse` and `PostToolUse`

<div style={{maxWidth: "500px", margin: "0 auto"}}>
  <Frame>
    <img src="https://mintcdn.com/claude-code/uLsR38F1U_5zPppm/images/hooks-lifecycle.svg?fit=max&auto=format&n=uLsR38F1U_5zPppm&q=85&s=fbdbd78ad9f474da7d344879341341f0" alt="Hook lifecycle diagram showing optional Setup feeding into SessionStart, then a per-turn loop containing UserPromptSubmit, UserPromptExpansion for slash commands, the nested agentic loop (PreToolUse, PermissionRequest, PostToolUse, PostToolUseFailure, PostToolBatch, SubagentStart/Stop, TaskCreated, TaskCompleted), and Stop or StopFailure, followed by TeammateIdle, PreCompact, PostCompact, and SessionEnd, with Elicitation and ElicitationResult nested inside MCP tool execution, PermissionDenied as a side branch from PermissionRequest for auto-mode denials, WorktreeCreate, WorktreeRemove, Notification, ConfigChange, InstructionsLoaded, CwdChanged, and FileChanged as standalone async events, and MessageDisplay as a display-only event that runs while assistant message text streams" width="520" height="1228" data-path="images/hooks-lifecycle.svg" />
  </Frame>
</div>

## Event schemas

Every hook event follows this structure:

```typescript
{
  type: "SessionStart" | "SessionEnd" | "UserPromptSubmit" | /* ... */,
  timestamp: "2024-12-01T12:34:56Z",
  projectDir: "/path/to/project",
  sessionId: "1234abcd",
  /* event-specific fields */
}
```

### SessionStart

Fires once at the start of a Claude Code session. Use this to check preconditions, prepare logging, or initialize project-specific resources.

```typescript
{
  type: "SessionStart",
  timestamp: "2024-12-01T12:34:56Z",
  projectDir: "/path/to/project",
  sessionId: "1234abcd",
  version: "0.42.0",  // Claude Code version
  workingDirectory: "/path/to/project/src",
  instructions: "You are a helpful assistant...",
  skills: ["@anthropic/web-lookup"],
  model: "claude-opus-4-1-20250729",
  preferencePath: "/path/to/.claude/preferences.json",
  preferencesVersion: 1,
}
```

**Matcher fields:** `type`, `version`

**Example use cases:**
- Validate required tools, environment variables, or configuration files
- Trigger CI/CD pipelines or notifications
- Initialize per-project logging or monitoring

### UserPromptSubmit

Fires once per user turn, right after the user submits their prompt. Access the raw user input, modify prompts before they are expanded with slash commands, or implement custom input validation.

```typescript
{
  type: "UserPromptSubmit",
  timestamp: "2024-12-01T12:34:56Z",
  projectDir: "/path/to/project",
  sessionId: "1234abcd",
  text: "What does this function do?",
  mode: "default" | "always-allow",
}
```

**Matcher fields:** `type`, `mode`

**Return object** (command or HTTP hook only):

```typescript
{
  approved: true,  // false to block; absent / null = no change
  text: "What does this function do?",  // modified prompt text; null/absent = no change
}
```

**Example use cases:**
- Block prompts matching a pattern (e.g., requests to commit without approval)
- Rewrite prompts dynamically
- Implement custom access control

**Note:** If your handler blocks with `approved: false`, the hook immediately prevents the user prompt from reaching Claude, and no agentic loop runs.

### UserPromptExpansion

Fires after slash commands (e.g., `/search`, `/chat`) are parsed from the user prompt. Inspect and modify the expanded prompt before it reaches Claude.

```typescript
{
  type: "UserPromptExpansion",
  timestamp: "2024-12-01T12:34:56Z",
  projectDir: "/path/to/project",
  sessionId: "1234abcd",
  text: "...",  // The full expanded prompt
  slashCommands: ["search"],  // List of slash commands found
}
```

**Matcher fields:** `type`, `slashCommands`

**Return object** (command or HTTP hook only):

```typescript
{
  text: "...",  // Modified prompt text; null/absent = no change
}
```

### PreToolUse

Fires before Claude Code executes every tool (Read, Write, Bash, WebFetch, etc.) during the agentic loop. Inspect tool calls before execution, optionally blocking or modifying them.

```typescript
{
  type: "PreToolUse",
  timestamp: "2024-12-01T12:34:56Z",
  projectDir: "/path/to/project",
  sessionId: "1234abcd",
  toolName: "Write",
  toolInput: {
    file_path: "/path/to/file.txt",
    content: "Hello, world!",
  },
  toolUseId: "tool-use-12345",
}
```

**Matcher fields:** `type`, `toolName`

**Return object** (command or HTTP hook only):

```typescript
{
  approved: true,  // false to block; absent = no change
  modifiedInput: {  // Modified input; absent / null = no change
    content: "Hello, world! (modified)"
  },
}
```

**Example use cases:**
- Block writes to protected files
- Audit all Bash commands before execution
- Inject additional context or constraints into tool calls
- Route file operations through a custom system
- Block external network requests

### PostToolUse

Fires after a tool execution completes successfully. Inspect and optionally modify the tool output before Claude sees it.

```typescript
{
  type: "PostToolUse",
  timestamp: "2024-12-01T12:34:56Z",
  projectDir: "/path/to/project",
  sessionId: "1234abcd",
  toolName: "Read",
  toolInput: {
    file_path: "/path/to/file.txt",
  },
  toolOutput: "File contents here",
  toolUseId: "tool-use-12345",
}
```

**Matcher fields:** `type`, `toolName`

**Return object** (command or HTTP hook only):

```typescript
{
  modifiedOutput: "Modified file contents",  // null/absent = no change
}
```

**Example use cases:**
- Filter sensitive data from tool outputs
- Inject computed or cached results
- Log tool execution for audit trails

### PostToolUseFailure

Fires after a tool execution fails (e.g., file not found, bash command returns non-zero exit code).

```typescript
{
  type: "PostToolUseFailure",
  timestamp: "2024-12-01T12:34:56Z",
  projectDir: "/path/to/project",
  sessionId: "1234abcd",
  toolName: "Bash",
  toolInput: {
    command: "cargo build",
  },
  exitCode: 1,
  stdout: "...",
  stderr: "error: build failed",
  toolUseId: "tool-use-12345",
}
```

**Matcher fields:** `type`, `toolName`, `exitCode`

**Return object** (command or HTTP hook only):

```typescript
{
  modifiedOutput: "Retry message or custom error",  // null/absent = no change
}
```

**Example use cases:**
- Log tool failures for monitoring
- Suggest recovery strategies
- Implement automatic retries

### PostToolBatch

Fires after a batch of tool calls completes (e.g., multiple Reads in one turn).

```typescript
{
  type: "PostToolBatch",
  timestamp: "2024-12-01T12:34:56Z",
  projectDir: "/path/to/project",
  sessionId: "1234abcd",
  tools: [
    {
      toolName: "Read",
      toolInput: { file_path: "..." },
      output: "file contents",
    },
    // ...
  ],
}
```

**Matcher fields:** `type`

**Example use cases:**
- Batch logging or monitoring
- Cross-tool validation

### Stop

Fires once per turn after Claude finishes its response and before the loop restarts. Use this to implement turn-level guardrails or cleanup.

```typescript
{
  type: "Stop",
  timestamp: "2024-12-01T12:34:56Z",
  projectDir: "/path/to/project",
  sessionId: "1234abcd",
  text: "I've made the requested changes...",  // Claude's response text
}
```

**Matcher fields:** `type`

**Return object** (command or HTTP hook only):

```typescript
{
  approved: true,  // false to block Claude's response and restart the loop
  text: "Modified response",  // null/absent = no change
}
```

**Example use cases:**
- Block or modify Claude's responses before they reach the user
- Implement safety checks
- Apply custom filtering or transformation

### StopFailure

Fires if a `Stop` hook returns `approved: false`, indicating Claude's response was rejected and the loop will restart.

```typescript
{
  type: "StopFailure",
  timestamp: "2024-12-01T12:34:56Z",
  projectDir: "/path/to/project",
  sessionId: "1234abcd",
  text: "I've made the requested changes...",  // Claude's rejected response
  hookName: "safety-check",  // Name of the hook that rejected it
}
```

**Matcher fields:** `type`

**Example use cases:**
- Log rejections for auditing
- Trigger notifications
- Update metrics

### SubagentStart

Fires when a subagent is launched (background agent task).

```typescript
{
  type: "SubagentStart",
  timestamp: "2024-12-01T12:34:56Z",
  projectDir: "/path/to/project",
  sessionId: "1234abcd",
  subagentId: "abc-123",
  description: "Build API endpoints",
  model: "claude-opus-4-1-20250729",
  tasksEnabled: false,
}
```

**Matcher fields:** `type`

### SubagentStop

Fires when a subagent completes.

```typescript
{
  type: "SubagentStop",
  timestamp: "2024-12-01T12:34:56Z",
  projectDir: "/path/to/project",
  sessionId: "1234abcd",
  subagentId: "abc-123",
  description: "Build API endpoints",
  exitStatus: "success" | "error" | "cancelled",
}
```

**Matcher fields:** `type`, `exitStatus`

### TaskCreated

Fires when a task is created via the `TaskCreate` tool.

```typescript
{
  type: "TaskCreated",
  timestamp: "2024-12-01T12:34:56Z",
  projectDir: "/path/to/project",
  sessionId: "1234abcd",
  taskId: "5",
  subject: "Implement auth endpoints",
  description: "Create login/logout endpoints with JWT.",
}
```

**Matcher fields:** `type`

### TaskCompleted

Fires when a task is marked completed via the `TaskUpdate` tool.

```typescript
{
  type: "TaskCompleted",
  timestamp: "2024-12-01T12:34:56Z",
  projectDir: "/path/to/project",
  sessionId: "1234abcd",
  taskId: "5",
  subject: "Implement auth endpoints",
  description: "Create login/logout endpoints with JWT.",
}
```

**Matcher fields:** `type`

### TeammateIdle

Fires when a teammate is idle after a background task completes.

```typescript
{
  type: "TeammateIdle",
  timestamp: "2024-12-01T12:34:56Z",
  projectDir: "/path/to/project",
  sessionId: "1234abcd",
  subagentId: "abc-123",
  description: "Build API endpoints",
}
```

**Matcher fields:** `type`

### PreCompact

Fires before Claude Code compacts (removes old messages from) context to make room for new content.

```typescript
{
  type: "PreCompact",
  timestamp: "2024-12-01T12:34:56Z",
  projectDir: "/path/to/project",
  sessionId: "1234abcd",
  compactingFrom: 50000,  // tokens before compacting
  compactingTo: 25000,  // tokens after compacting
}
```

**Matcher fields:** `type`

### PostCompact

Fires after compacting completes.

```typescript
{
  type: "PostCompact",
  timestamp: "2024-12-01T12:34:56Z",
  projectDir: "/path/to/project",
  sessionId: "1234abcd",
  compactedFrom: 50000,  // tokens before compacting
  compactedTo: 25000,  // tokens after compacting
}
```

**Matcher fields:** `type`

### SessionEnd

Fires once at the end of a Claude Code session. Use this for cleanup, final logging, or post-session actions.

```typescript
{
  type: "SessionEnd",
  timestamp: "2024-12-01T12:34:56Z",
  projectDir: "/path/to/project",
  sessionId: "1234abcd",
  exitReason: "user-quit" | "error" | "timeout",
  exitMessage: "User quit",
}
```

**Matcher fields:** `type`, `exitReason`

**Example use cases:**
- Clean up resources
- Archive logs
- Notify external systems

### Async Events

These events fire asynchronously and cannot block or return values. They are for logging and notifications only.

#### PermissionRequest

Fires when Claude Code requests permission for an action (e.g., running a tool in auto mode).

```typescript
{
  type: "PermissionRequest",
  timestamp: "2024-12-01T12:34:56Z",
  projectDir: "/path/to/project",
  sessionId: "1234abcd",
  prompt: "Allow Claude Code to run: bash --version?",
  mode: "always-allow",  // The current mode (auto mode context)
}
```

**Matcher fields:** `type`, `mode`

#### PermissionDenied

Fires when Claude Code denies a permission request.

```typescript
{
  type: "PermissionDenied",
  timestamp: "2024-12-01T12:34:56Z",
  projectDir: "/path/to/project",
  sessionId: "1234abcd",
  reason: "User denied permission",
}
```

**Matcher fields:** `type`

#### WorktreeCreate

Fires when a worktree is created.

```typescript
{
  type: "WorktreeCreate",
  timestamp: "2024-12-01T12:34:56Z",
  projectDir: "/path/to/project",
  sessionId: "1234abcd",
  worktreeName: "feature-branch",
  worktreePath: "/path/to/worktree",
}
```

**Matcher fields:** `type`, `worktreeName`

#### WorktreeRemove

Fires when a worktree is removed.

```typescript
{
  type: "WorktreeRemove",
  timestamp: "2024-12-01T12:34:56Z",
  projectDir: "/path/to/project",
  sessionId: "1234abcd",
  worktreeName: "feature-branch",
  worktreePath: "/path/to/worktree",
}
```

**Matcher fields:** `type`, `worktreeName`

#### Notification

Fires when a notification is displayed to the user (async event, cannot be blocked).

```typescript
{
  type: "Notification",
  timestamp: "2024-12-01T12:34:56Z",
  projectDir: "/path/to/project",
  sessionId: "1234abcd",
  text: "Build completed successfully",
  level: "info" | "warning" | "error",
}
```

**Matcher fields:** `type`, `level`

#### ConfigChange

Fires when Claude Code settings or preferences are changed.

```typescript
{
  type: "ConfigChange",
  timestamp: "2024-12-01T12:34:56Z",
  projectDir: "/path/to/project",
  sessionId: "1234abcd",
  setting: "autoCompactEnabled",
  oldValue: true,
  newValue: false,
}
```

**Matcher fields:** `type`

#### InstructionsLoaded

Fires when instructions are loaded from `.claude/instructions.md` or via `/instructions`.

```typescript
{
  type: "InstructionsLoaded",
  timestamp: "2024-12-01T12:34:56Z",
  projectDir: "/path/to/project",
  sessionId: "1234abcd",
  instructions: "You are a helpful assistant...",
}
```

**Matcher fields:** `type`

#### CwdChanged

Fires when the working directory changes.

```typescript
{
  type: "CwdChanged",
  timestamp: "2024-12-01T12:34:56Z",
  projectDir: "/path/to/project",
  sessionId: "1234abcd",
  oldCwd: "/path/to/project",
  newCwd: "/path/to/project/src",
}
```

**Matcher fields:** `type`

#### FileChanged

Fires when a file is created or changed externally (not by Claude Code).

```typescript
{
  type: "FileChanged",
  timestamp: "2024-12-01T12:34:56Z",
  projectDir: "/path/to/project",
  sessionId: "1234abcd",
  filePath: "/path/to/file.txt",
  changeType: "created" | "modified" | "deleted",
}
```

**Matcher fields:** `type`, `changeType`

#### MessageDisplay

Fires when Claude Code is displaying an assistant message (for display-only hooks).

```typescript
{
  type: "MessageDisplay",
  timestamp: "2024-12-01T12:34:56Z",
  projectDir: "/path/to/project",
  sessionId: "1234abcd",
  text: "I've completed the requested changes...",
}
```

**Matcher fields:** `type`

#### Elicitation

Fires when Claude Code needs to ask for clarification or additional input (nested inside MCP tool execution).

```typescript
{
  type: "Elicitation",
  timestamp: "2024-12-01T12:34:56Z",
  projectDir: "/path/to/project",
  sessionId: "1234abcd",
  toolName: "ExampleTool",
  prompt: "Which branch would you like to use?",
  options: ["main", "develop"],
}
```

**Matcher fields:** `type`, `toolName`

#### ElicitationResult

Fires when the user responds to an elicitation prompt (nested inside MCP tool execution).

```typescript
{
  type: "ElicitationResult",
  timestamp: "2024-12-01T12:34:56Z",
  projectDir: "/path/to/project",
  sessionId: "1234abcd",
  toolName: "ExampleTool",
  selectedOption: "main",
}
```

**Matcher fields:** `type`, `toolName`

## Configuration

Hooks are configured in `.claude/hooks.json`. Each hook object specifies:

1. **Type** (`command`, `http`, or `prompt`)
2. **Event matcher** (which event to fire on)
3. **Handler** (the command, URL, or prompt template)

### Command hooks

```json
{
  "type": "command",
  "on": "PostToolUse",
  "match": {
    "toolName": "Write"
  },
  "command": "~/.claude/hooks/audit-writes.sh",
  "timeout": 600000,
  "shell": "bash"
}
```

**Fields:**

- `type`: Always `"command"`
- `on`: Event name (e.g., `"PreToolUse"`)
- `match`: Optional matcher fields to narrow which events trigger this hook
- `command`: Path to the executable (can be relative to project root or absolute)
- `timeout`: Max execution time in milliseconds (default: 600000)
- `shell`: `"bash"`, `"zsh"`, `"powershell"`, `"cmd"` (default: system default, auto-detected from environment)

**Input/Output:**

- Input arrives on stdin as JSON
- Output (if needed) must be returned on stdout as JSON
- Exit code 0 = success; non-zero = failure
- Timeout = hook ignored (no return value, execution continues)

### HTTP hooks

```json
{
  "type": "http",
  "on": "PreToolUse",
  "match": {
    "toolName": "Bash"
  },
  "url": "http://localhost:3000/hooks",
  "timeout": 600000
}
```

**Fields:**

- `type`: Always `"http"`
- `on`: Event name (e.g., `"PreToolUse"`)
- `match`: Optional matcher fields to narrow which events trigger this hook
- `url`: HTTP endpoint URL
- `timeout`: Max execution time in milliseconds (default: 600000)

**Input/Output:**

- Input arrives as POST request body (JSON)
- Output (if needed) must be returned as JSON response body
- HTTP status 200 = success; other status codes = failure
- Timeout = hook ignored (no return value, execution continues)

### Prompt hooks

Prompt hooks let you inject hooks into Claude Code's LLM prompt. They are useful for complex rules that are easier to express in natural language.

```json
{
  "type": "prompt",
  "on": "UserPromptSubmit",
  "match": {},
  "template": "You must ensure the user's request is safe. If it asks to delete files or run destructive commands, reject it with: 'That operation is too risky.'"
}
```

**Fields:**

- `type`: Always `"prompt"`
- `on`: Event name (e.g., `"UserPromptSubmit"`)
- `match`: Optional matcher fields (rarely used with prompt hooks)
- `template`: The instruction to inject into Claude Code's system prompt

**Behavior:**

Prompt hooks are injected into Claude Code's system prompt at the relevant event. They are never async and are evaluated by Claude as part of normal reasoning, not as separate rule enforcement.

**Example use cases:**

- Embed project-specific safety policies
- Enforce coding standards or naming conventions
- Guide Claude toward specific solution patterns
- Remind Claude of project context

## Event matcher syntax

Use matchers to narrow which events trigger a hook. Matchers are optional; if omitted, the hook fires for all events of that type.

### Basic matchers

```json
{
  "match": {
    "toolName": "Bash",
    "mode": "always-allow"
  }
}
```

Matchers support:

- **Exact match:** `"toolName": "Bash"` → fires only for `Bash` tool calls
- **Array (OR):** `"toolName": ["Read", "Write"]` → fires for `Read` or `Write`
- **Regex:** `"toolName": "/(Read|Write)/"` → regex patterns in `/.../` syntax
- **Negation:** `"toolName": "!Bash"` → all tools except `Bash`

### Complex matchers

For `PreToolUse` and `PostToolUse`, match on nested `toolInput` fields:

```json
{
  "match": {
    "toolName": "Bash",
    "toolInput.command": "/rm.*-rf/"
  }
}
```

This fires when a `Bash` tool call contains a command matching the regex `rm.*-rf`.

### Matcher field availability by event

| Event | Matcher fields |
|-------|-----------------|
| SessionStart | type, version |
| UserPromptSubmit | type, mode |
| UserPromptExpansion | type, slashCommands |
| PreToolUse | type, toolName, toolInput.* |
| PostToolUse | type, toolName |
| PostToolUseFailure | type, toolName, exitCode |
| PostToolBatch | type |
| Stop | type |
| StopFailure | type |
| SubagentStart | type |
| SubagentStop | type, exitStatus |
| TaskCreated | type |
| TaskCompleted | type |
| TeammateIdle | type |
| PreCompact | type |
| PostCompact | type |
| SessionEnd | type, exitReason |
| PermissionRequest | type, mode |
| PermissionDenied | type |
| WorktreeCreate | type, worktreeName |
| WorktreeRemove | type, worktreeName |
| Notification | type, level |
| ConfigChange | type |
| InstructionsLoaded | type |
| CwdChanged | type |
| FileChanged | type, changeType |
| MessageDisplay | type |
| Elicitation | type, toolName |
| ElicitationResult | type, toolName |

## Exit codes

Command hooks use exit codes to communicate the result:

| Exit code | Meaning | Notes |
|-----------|---------|-------|
| 0 | Success | The hook ran successfully. Return a value on stdout if this is a blocking hook (e.g., `PreToolUse`). |
| 1 | General error | Hook logic encountered an error. Execution continues without a return value. |
| 2 | Validation error | Hook validation failed (e.g., invalid JSON input). Execution continues. |
| Other | Reserved | Reserved for future use. Treat like exit code 1. |

## Async hooks

Async hooks fire in the background and cannot block or return values. They are perfect for logging, monitoring, or triggering external actions. All async events (e.g., `PermissionRequest`, `WorktreeCreate`, `FileChanged`) use async hooks.

For synchronous events like `PreToolUse`, `Stop`, or `SessionStart`, you can also run a hook asynchronously:

```json
{
  "type": "command",
  "on": "PostToolUse",
  "async": true,
  "command": "~/.claude/hooks/log-tool-usage.sh"
}
```

**Fields:**

- `async`: Set to `true` to run this hook in the background without blocking

**Behavior:**

- Async hooks execute in parallel with Claude Code's main loop
- They cannot return a value (any return value is ignored)
- They cannot block execution
- Timeout still applies

**Example use cases:**

- Log tool executions for audit trails
- Send metrics to a monitoring service
- Trigger notifications or webhooks
- Archive session data

## HTTP hooks

HTTP hooks send events to a remote server. The server can inspect the event and return a decision (for synchronous hooks) or just acknowledge receipt (for async hooks).

### HTTP request format

```http
POST /hooks HTTP/1.1
Host: example.com
Content-Type: application/json
Content-Length: ...

{
  "type": "PreToolUse",
  "timestamp": "2024-12-01T12:34:56Z",
  "projectDir": "/path/to/project",
  "sessionId": "1234abcd",
  "toolName": "Bash",
  "toolInput": { ... }
}
```

### HTTP response format

For synchronous events (`PreToolUse`, `PostToolUse`, etc.):

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "approved": true,
  "modifiedInput": { ... }
}
```

For async events, any 2xx response is considered success:

```http
HTTP/1.1 200 OK

{}
```

### HTTP timeout and retry

- Default timeout: 600000ms (10 minutes)
- No automatic retries; timeout = hook ignored
- Timeouts do not block Claude Code from continuing

### Example HTTP hook server

```javascript
const express = require("express");
const app = express();
app.use(express.json());

app.post("/hooks", (req, res) => {
  const event = req.body;

  if (event.type === "PreToolUse" && event.toolName === "Bash") {
    if (event.toolInput.command.includes("rm -rf")) {
      return res.json({ approved: false });
    }
  }

  res.json({});
});

app.listen(3000);
```

## MCP tool hooks

When Claude Code uses MCP tools, Elicitation and ElicitationResult events fire inside the MCP tool execution flow. Hook handlers can inspect and optionally modify elicitation prompts and responses.

### Elicitation flow

1. Claude Code calls an MCP tool
2. The tool asks a clarification question (elicitation)
3. `Elicitation` event fires → your hook can modify the prompt
4. User responds
5. `ElicitationResult` event fires → your hook can modify the response
6. MCP tool continues with the modified response

### Elicitation event

```typescript
{
  type: "Elicitation",
  timestamp: "2024-12-01T12:34:56Z",
  projectDir: "/path/to/project",
  sessionId: "1234abcd",
  toolName: "DatabaseTool",
  prompt: "Which database would you like to connect to?",
  options: ["postgres", "mysql", "sqlite"],
}
```

### ElicitationResult event

```typescript
{
  type: "ElicitationResult",
  timestamp: "2024-12-01T12:34:56Z",
  projectDir: "/path/to/project",
  sessionId: "1234abcd",
  toolName: "DatabaseTool",
  selectedOption: "postgres",
}
```

### Hook example

```json
{
  "type": "command",
  "on": "Elicitation",
  "match": {
    "toolName": "DatabaseTool"
  },
  "command": "~/.claude/hooks/mcp-elicitation.sh"
}
```

Your handler receives the elicitation JSON and can return:

```json
{
  "modifiedPrompt": "Which database would you like? (postgres or mysql only)",
  "options": ["postgres", "mysql"]
}
```

## Prompt hooks

Prompt hooks inject natural-language rules directly into Claude Code's system prompt. They are useful for complex policies that are easier to express in prose than in code.

### How they work

1. When an event fires and a prompt hook matches, the hook's `template` is injected into Claude Code's reasoning
2. Claude evaluates the rule as part of normal decision-making
3. No separate return value is needed (Claude's reasoning output is the decision)

### Example: Enforce commit message format

```json
{
  "type": "prompt",
  "on": "Stop",
  "template": "Before showing your final response, check: did you commit changes? If yes, verify the commit message follows the format 'type(scope): description'. If it doesn't, ask the user to fix it and don't proceed."
}
```

### Example: Block destructive operations

```json
{
  "type": "prompt",
  "on": "PreToolUse",
  "template": "You must NEVER run git reset --hard, git push --force, or rm -rf commands without explicit user confirmation. If the user tries, say: 'I cannot run this command without your explicit approval. Are you sure?' and wait for confirmation."
}
```

### Prompt hook best practices

- **Be specific:** "Block git reset --hard" is better than "Don't run dangerous commands"
- **Explain the why:** Include context about why the rule matters
- **Use conditionals:** "If the commit message, then check for format" is clearer than absolute rules
- **Keep it concise:** Long prompts add overhead; focus on the essentials

## Troubleshooting

### Hooks not firing

- **Check the event name:** Verify the `on` field matches the event you expect
- **Check the matcher:** Use matchers to narrow events; if no matcher matches, the hook won't fire
- **Check the event timing:** Some events fire at specific points (e.g., `PostToolUse` only after successful tool execution)
- **Enable debug logging:** Run `claude --debug` and search for `[DEBUG]` lines mentioning hooks

### Hook timeouts

- **Increase the timeout:** The default is 600000ms; set a higher value if your handler is slow
- **Optimize the handler:** If your handler is slow, optimize it or run it asynchronously

### Hook return values not applied

- **Check the return format:** Ensure your return object matches the expected schema (e.g., `{ approved: false, modifiedInput: {...} }`)
- **Check JSON validity:** Return valid JSON on stdout; invalid JSON is ignored
- **Async hooks can't return values:** Async hooks are fire-and-forget; return values are not used

### Hook command not found

- **Use absolute paths:** Use `/home/user/hooks/script.sh` instead of `~/.claude/hooks/script.sh`
- **Use project-relative paths:** Use `./hooks/script.sh` relative to the project root
- **Check file permissions:** Ensure the hook file is executable (`chmod +x`)

## Configuration file examples

### Comprehensive hooks.json

```json
{
  "hooks": [
    {
      "type": "command",
      "on": "SessionStart",
      "command": "~/.claude/hooks/validate-setup.sh"
    },
    {
      "type": "command",
      "on": "PreToolUse",
      "match": {
        "toolName": "Bash"
      },
      "command": "~/.claude/hooks/audit-bash.sh",
      "timeout": 5000
    },
    {
      "type": "command",
      "on": "PreToolUse",
      "match": {
        "toolName": "Write",
        "toolInput.file_path": "/\\.env/"
      },
      "command": "~/.claude/hooks/protect-env.sh"
    },
    {
      "type": "http",
      "on": "PostToolUse",
      "url": "http://localhost:8000/hooks/log",
      "async": true
    },
    {
      "type": "prompt",
      "on": "Stop",
      "template": "Verify that any new files follow the project's naming conventions."
    },
    {
      "type": "command",
      "on": "SessionEnd",
      "command": "~/.claude/hooks/cleanup.sh"
    }
  ]
}
```

### Platform-specific shells

```json
{
  "hooks": [
    {
      "type": "command",
      "on": "PreToolUse",
      "command": "~/.claude/hooks/check.sh",
      "shell": "bash"
    },
    {
      "type": "command",
      "on": "PreToolUse",
      "command": "~/.claude/hooks/check.ps1",
      "shell": "powershell"
    }
  ]
}
```

### Nested input matching

```json
{
  "type": "command",
  "on": "PreToolUse",
  "match": {
    "toolName": "Bash",
    "toolInput.command": "/^rm .*-rf/"
  },
  "command": "~/.claude/hooks/confirm-destructive.sh"
}
```

## Debug hooks

Hook execution details, including which hooks matched, their exit codes, and full stdout and stderr, are written to the debug log file. Start Claude Code with `claude --debug-file <path>` to write the log to a known location, or run `claude --debug` and read the log at `~/.claude/debug/<session-id>.txt`. The `--debug` flag doesn't print to the terminal.

```text theme={null}
[DEBUG] Executing hooks for PostToolUse:Write
[DEBUG] Found 1 hook commands to execute
[DEBUG] Executing hook command: <Your command> with timeout 600000ms
[DEBUG] Hook command completed with status 0: <Your stdout>
```

For more granular hook matching details, set `CLAUDE_CODE_DEBUG_LOG_LEVEL=verbose` to see additional log lines such as hook matcher counts and query matching.

For troubleshooting common issues like hooks not firing, Stop hooks that keep blocking, or configuration errors, see [Limitations and troubleshooting](/en/hooks-guide#limitations-and-troubleshooting) in the guide. For a broader diagnostic walkthrough covering `/context`, `/doctor`, and settings precedence, see [Debug your config](/en/debug-your-config).
