---
source: https://code.claude.com/docs/en/agent-sdk/typescript
fetched: 2026-07-05
---
> **In here:** Installation and setup · Query and streaming functions · Complete type definitions

# Agent SDK reference - TypeScript

> Complete API reference for the TypeScript Agent SDK, including all functions, types, and interfaces.

<script src="/components/typescript-sdk-type-links.js" defer />

## Installation

```bash theme={null}
npm install @anthropic-ai/claude-agent-sdk
```

<Note>
  The SDK bundles a native Claude Code binary for your platform as an optional dependency such as `@anthropic-ai/claude-agent-sdk-darwin-arm64`. You don't need to install Claude Code separately. If your package manager skips optional dependencies, the SDK throws `Native CLI binary for <platform> not found`; set [`pathToClaudeCodeExecutable`](#options) to a separately installed `claude` binary instead.
</Note>

### Compile to a single executable

When you compile your application into a single-file executable with `bun build --compile`, the SDK cannot resolve the bundled CLI binary at runtime. `require.resolve` does not work inside the compiled executable's `$bunfs` virtual filesystem, so the SDK throws `Native CLI binary for <platform> not found`.

To work around this, embed the platform binary as a file asset, extract it to a real path at startup with `extractFromBunfs()`, and pass that path to [`pathToClaudeCodeExecutable`](#options).

The `extractFromBunfs()` helper requires `@anthropic-ai/claude-agent-sdk` v0.3.144 or later. The example below builds for macOS on Apple Silicon:

```typescript theme={null}
import binPath from "@anthropic-ai/claude-agent-sdk-darwin-arm64/claude" with { type: "file" };
import { extractFromBunfs } from "@anthropic-ai/claude-agent-sdk/extract";
import { query } from "@anthropic-ai/claude-agent-sdk";

const cliPath = extractFromBunfs(binPath);

for await (const message of query({
  prompt: "Hello",
  options: { pathToClaudeCodeExecutable: cliPath },
})) {
  console.log(message);
}
```

`extractFromBunfs()` copies the embedded binary out of the compiled executable's virtual filesystem to a per-user temp directory and returns the real path. Outside a compiled executable it returns the input path unchanged, so the same code runs in development without modification.

Each compiled executable embeds a single platform's binary. Match the platform package in the import to your `--target`:

* To cross-compile, install the non-matching platform package, for example `npm install @anthropic-ai/claude-agent-sdk-linux-x64 --force`.
* On Windows, the binary subpath is `claude.exe`, for example `@anthropic-ai/claude-agent-sdk-win32-x64/claude.exe`.

## Functions

### `query()`

The primary function for interacting with Claude Code. Creates an async generator that streams messages as they arrive.

```typescript theme={null}
function query({
  prompt,
  options
}: {
  prompt: string | AsyncIterable<SDKUserMessage>;
  options?: Options;
}): Query;
```

#### Parameters

| Parameter | Type                                                             | Description                                                       |
| :-------- | :--------------------------------------------------------------- | :---------------------------------------------------------------- |
| `prompt`  | `string \| AsyncIterable<`[`SDKUserMessage`](#sdkusermessage)`>` | The input prompt as a string or async iterable for streaming mode |
| `options` | [`Options`](#options)                                            | Optional configuration object (see Options type below)            |

#### Returns

Returns a [`Query`](#query-object) object that extends `AsyncGenerator<`[`SDKMessage`](#sdkmessage)`, void>` with additional methods.

### `startup()`

Pre-warms the CLI subprocess by spawning it and completing the initialize handshake before a prompt is available. The returned [`WarmQuery`](#warmquery) handle accepts a prompt later and writes it to an already-ready process, so the first `query()` call resolves without paying subprocess spawn and initialization cost inline.

```typescript theme={null}
function startup(params?: {
  options?: Options;
  initializeTimeoutMs?: number;
}): Promise<WarmQuery>;
```

#### Parameters

| Parameter             | Type                  | Description                                                                                                                                                                    |
| :-------------------- | :-------------------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `options`             | [`Options`](#options) | Optional configuration object. Same as the `options` parameter to `query()`                                                                                                    |
| `initializeTimeoutMs` | `number`              | Maximum time in milliseconds to wait for subprocess initialization. Defaults to `60000`. If initialization does not complete in time, the promise rejects with a timeout error |

#### Returns

Returns a `Promise<`[`WarmQuery`](#warmquery)`>` that resolves once the subprocess has spawned and completed its initialize handshake.

#### Example

Call `startup()` early, for example on application boot, then call `.query()` on the returned handle once a prompt is ready. This moves subprocess spawn and initialization out of the critical path.

```typescript theme={null}
import { startup } from "@anthropic-ai/claude-agent-sdk";

const warmQuery = await startup();

// later...
for await (const message of await warmQuery.query("Hello")) {
  console.log(message);
}
```

## Types

### `Query` object

The object returned by `query()`. Extends `AsyncGenerator<`[`SDKMessage`](#sdkmessage)`, void>` with the following properties:

#### Properties

| Property        | Type                                                      | Description                              |
| :-------------- | :-------------------------------------------------------- | :--------------------------------------- |
| `abortController` | `AbortController`                                         | AbortController for cancelling the query |
| `onToolOutput` | `(toolId: string, output: ToolOutput) => Promise<void>` | Function to send tool outputs to Claude Code |

#### Methods

| Method   | Description                                                |
| :------- | :--------------------------------------------------------- |
| `return()` | Implement async generator protocol; cancels the operation |
| `throw()` | Implement async generator protocol; cancels the operation |

#### Example

```typescript theme={null}
import { query } from "@anthropic-ai/claude-agent-sdk";

const q = query({
  prompt: "Build a web app that counts button clicks"
});

for await (const message of q) {
  if (message.type === "tool_result_request") {
    const toolId = message.tool_use_id;
    const toolName = message.tool_name;
    const toolInput = message.tool_input;

    // Handle the tool use...
    const output = await handleTool(toolName, toolInput);

    // Send the result back
    await q.onToolOutput(toolId, output);
  }

  if (message.type === "tool_execution_status") {
    console.log(message.status); // "pending", "running", "success", or "error"
  }
}
```

### `WarmQuery` object

The object returned by `startup()`. Wraps a pre-initialized subprocess for lower latency.

#### Methods

| Method | Type                                                              | Description                                                           |
| :----- | :---------------------------------------------------------------- | :-------------------------------------------------------------------- |
| `query` | `(prompt: string \| AsyncIterable<`[`SDKUserMessage`](#sdkusermessage)`>) => Promise<`[`Query`](#query-object)`>` | Call to send a prompt to the pre-warmed subprocess, returns a `Query` object |

#### Example

```typescript theme={null}
import { startup } from "@anthropic-ai/claude-agent-sdk";

const warmQuery = await startup();

// Multiple queries on the same subprocess
const q1 = await warmQuery.query("Hello");
for await (const message of q1) {
  console.log(message);
}

const q2 = await warmQuery.query("What is 2+2?");
for await (const message of q2) {
  console.log(message);
}
```

### `Options`

Configuration object passed to `query()` and `startup()`.

```typescript theme={null}
interface Options {
  model?: string;
  pathToClaudeCodeExecutable?: string;
  environmentVariables?: Record<string, string>;
  extensionsToLoad?: string[];
  budgetTokens?: number;
  budgetMs?: number;
  requestTimeoutMs?: number;
  initializeTimeoutMs?: number;
  abortSignal?: AbortSignal;
}
```

#### Properties

| Property                    | Type                         | Description                                                                                                                                                                           |
| :-------------------------- | :--------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `model`                     | `string`                     | The Claude model to use (defaults to latest available)                                                                                                                                |
| `pathToClaudeCodeExecutable` | `string`                     | Path to the Claude Code executable. If not provided, the SDK attempts to use the bundled binary or installed `claude` command                                                        |
| `environmentVariables`      | `Record<string, string>`     | Environment variables to pass to the Claude Code subprocess                                                                                                                           |
| `extensionsToLoad`          | `string[]`                   | Array of extension names to load                                                                                                                                                     |
| `budgetTokens`              | `number`                     | Maximum number of tokens to use (soft limit; operations in progress won't be cancelled)                                                                                              |
| `budgetMs`                  | `number`                     | Maximum time in milliseconds to spend on the task (soft limit; operations in progress won't be cancelled)                                                                            |
| `requestTimeoutMs`          | `number`                     | Timeout for individual requests in milliseconds. Defaults to `300000` (5 minutes)                                                                                                    |
| `initializeTimeoutMs`       | `number`                     | Timeout for subprocess initialization in milliseconds. Defaults to `60000`                                                                                                            |
| `abortSignal`               | `AbortSignal`                | AbortSignal to cancel the operation                                                                                                                                                  |

### `SDKMessage`

Union type for all possible messages from Claude Code.

```typescript theme={null}
type SDKMessage = 
  | ContentBlockStartMessage
  | ContentBlockDeltaMessage
  | ContentBlockStopMessage
  | ToolUseMessage
  | ToolResultRequestMessage
  | ToolExecutionStatusMessage
  | MessageStartMessage
  | MessageStopMessage
  | MessageDeltaMessage
  | ErrorMessage
  | RateLimitMessage
  | InputModesMessage
  | ReadyMessage
  | BudgetExceededMessage
  | LlmUsageMessage
  | TextMessage
  | FileMessage;
```

## Message Types

### `ContentBlockStartMessage`

Signals the start of a new content block in the message.

```typescript theme={null}
interface ContentBlockStartMessage {
  type: "content_block_start";
  index: number;
  content_block: {
    type: "text" | "tool_use";
    id?: string;
    name?: string;
  };
}
```

### `ContentBlockDeltaMessage`

Contains streamed data for the current content block.

```typescript theme={null}
interface ContentBlockDeltaMessage {
  type: "content_block_delta";
  index: number;
  delta: {
    type: "text_delta" | "input_json_delta";
    text?: string;
    partial_json?: string;
  };
}
```

### `ContentBlockStopMessage`

Signals the end of a content block.

```typescript theme={null}
interface ContentBlockStopMessage {
  type: "content_block_stop";
  index: number;
}
```

### `ToolUseMessage`

Complete tool use block (after streaming completes).

```typescript theme={null}
interface ToolUseMessage {
  type: "tool_use";
  id: string;
  name: string;
  input: Record<string, unknown>;
}
```

### `ToolResultRequestMessage`

Requests the result of a tool execution.

```typescript theme={null}
interface ToolResultRequestMessage {
  type: "tool_result_request";
  tool_use_id: string;
  tool_name: string;
  tool_input: Record<string, unknown>;
}
```

### `ToolExecutionStatusMessage`

Provides status updates during tool execution.

```typescript theme={null}
interface ToolExecutionStatusMessage {
  type: "tool_execution_status";
  tool_use_id: string;
  tool_name: string;
  status: "pending" | "running" | "success" | "error";
  output?: unknown;
  error?: string;
}
```

### `MessageStartMessage`

Signals the start of a new message from Claude Code.

```typescript theme={null}
interface MessageStartMessage {
  type: "message_start";
  message: {
    id: string;
    type: "message";
    role: "assistant";
    model: string;
  };
}
```

### `MessageStopMessage`

Signals the end of the message stream.

```typescript theme={null}
interface MessageStopMessage {
  type: "message_stop";
  message: {
    id: string;
    type: "message";
    role: "assistant";
    model: string;
    stop_reason: string;
  };
}
```

### `MessageDeltaMessage`

Contains updates to message metadata during streaming.

```typescript theme={null}
interface MessageDeltaMessage {
  type: "message_delta";
  delta: {
    stop_reason?: string;
    stop_sequence?: string;
  };
}
```

### `ErrorMessage`

Indicates an error during execution.

```typescript theme={null}
interface ErrorMessage {
  type: "error";
  error: {
    type: string;
    message: string;
  };
}
```

### `RateLimitMessage`

Indicates rate limiting is in effect.

```typescript theme={null}
interface RateLimitMessage {
  type: "rate_limit";
  retry_after_ms: number;
}
```

### `InputModesMessage`

Describes available input modes for the current context.

```typescript theme={null}
interface InputModesMessage {
  type: "input_modes";
  modes: string[];
}
```

### `ReadyMessage`

Signals that Claude Code is ready to accept input.

```typescript theme={null}
interface ReadyMessage {
  type: "ready";
}
```

### `BudgetExceededMessage`

Indicates that a budget (tokens or time) has been exceeded.

```typescript theme={null}
interface BudgetExceededMessage {
  type: "budget_exceeded";
  budget_type: "tokens" | "time";
}
```

### `LlmUsageMessage`

Provides token usage statistics.

```typescript theme={null}
interface LlmUsageMessage {
  type: "llm_usage";
  input_tokens: number;
  output_tokens: number;
}
```

### `TextMessage`

A simple text message from Claude Code.

```typescript theme={null}
interface TextMessage {
  type: "text";
  text: string;
}
```

### `FileMessage`

Contains file data or references from Claude Code.

```typescript theme={null}
interface FileMessage {
  type: "file";
  path?: string;
  name?: string;
  content?: string;
  mimeType?: string;
}
```

## Hook Types

### `MessageHook`

Hook function called when a message is about to be sent to Claude Code.

```typescript theme={null}
type MessageHook = (message: SDKUserMessage) => void | Promise<void>;
```

### `RequestHook`

Hook function called when a request is about to be made.

```typescript theme={null}
type RequestHook = (request: unknown) => void | Promise<void>;
```

### `ResponseHook`

Hook function called when a response is received.

```typescript theme={null}
type ResponseHook = (response: SDKMessage) => void | Promise<void>;
```

## Tool Input Types

### `ToolInput`

The input object passed to a tool.

```typescript theme={null}
interface ToolInput {
  [key: string]: unknown;
}
```

## Tool Output Types

### `ToolOutput`

The output returned from a tool execution.

```typescript theme={null}
interface ToolOutput {
  type: "text" | "error" | "image" | "file";
  content: string | Record<string, unknown>;
  error?: string;
}
```

## Permission Types

### `PermissionRequest`

A request for user permission to perform an action.

```typescript theme={null}
interface PermissionRequest {
  type: string;
  action: string;
  resource?: string;
  reason?: string;
}
```

### `PermissionResponse`

User's response to a permission request.

```typescript theme={null}
interface PermissionResponse {
  granted: boolean;
  scope?: "once" | "session" | "always";
}
```

## Other Types

### `SDKUserMessage`

User input to the SDK.

```typescript theme={null}
type SDKUserMessage = {
  type: "user";
  content: string | ContentBlock[];
};
```

### `ContentBlock`

A single content block in a message.

```typescript theme={null}
type ContentBlock = 
  | TextBlock
  | ImageBlock
  | DocumentBlock;

interface TextBlock {
  type: "text";
  text: string;
}

interface ImageBlock {
  type: "image";
  source: ImageSource;
}

interface ImageSource {
  type: "base64" | "url";
  media_type?: "image/jpeg" | "image/png" | "image/gif" | "image/webp";
  data?: string;
  url?: string;
}

interface DocumentBlock {
  type: "document";
  source: DocumentSource;
}

interface DocumentSource {
  type: "file" | "url" | "base64";
  media_type?: string;
  data?: string;
  url?: string;
  path?: string;
}
```

## Sandbox Configuration

### `SandboxConfig`

Configuration for the sandbox environment.

```typescript theme={null}
interface SandboxConfig {
  type: "docker" | "local";
  workdir?: string;
  timeout?: number;
  memoryLimitMb?: number;
  environment?: Record<string, string>;
}
```

## See also

* [Agent SDK overview](../overview.md)
* [Python SDK reference](../python.md)
* [API reference](../../api/overview.md)
</content>
