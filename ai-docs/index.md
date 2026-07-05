# AI Documentation Index

Cached official docs for harness-layer work. Managed by `/kb` — don't edit the
table by hand; add sources to [sources.yaml](./sources.yaml) (or run `/kb add <url>`)
and run `/kb`.

## Cached official docs

| Topic | File | Fetched |
| --- | --- | --- |
| Subagents — built-in & custom, delegation, context management | [anthropic/subagents.md](./anthropic/subagents.md) | 2026-07-05 |
| Agent teams — multi-session orchestration, task coordination, inter-agent messaging | [anthropic/agent-teams.md](./anthropic/agent-teams.md) | 2026-07-05 |
| Workflows — script-based orchestration of many subagents in parallel | [anthropic/workflows.md](./anthropic/workflows.md) | 2026-07-05 |
| Git worktrees — isolate sessions for conflict-free parallel edits | [anthropic/worktrees.md](./anthropic/worktrees.md) | 2026-07-05 |
| MCP in Claude Code — server config, scopes, auth, tool usage | [anthropic/mcp.md](./anthropic/mcp.md) | 2026-07-05 |
| Skills — author, configure, and share to extend Claude | [anthropic/skills.md](./anthropic/skills.md) | 2026-07-05 |
| Artifacts — publish pages with versioning, team sharing, org controls | [anthropic/artifacts.md](./anthropic/artifacts.md) | 2026-07-05 |
| Hooks guide — lifecycle automation, notifications, enforcement recipes | [anthropic/hooks-guide.md](./anthropic/hooks-guide.md) | 2026-07-05 |
| Headless mode — non-interactive CLI (-p) for scripting and CI/CD | [anthropic/headless.md](./anthropic/headless.md) | 2026-07-05 |
| Deep links — launch sessions from URLs with cwd and prompt params | [anthropic/deep-links.md](./anthropic/deep-links.md) | 2026-07-05 |
| Large codebases — monorepos, nested settings, sparse worktrees, per-directory skills | [anthropic/large-codebases.md](./anthropic/large-codebases.md) | 2026-07-05 |
| Plugin marketplaces — create, distribute, version-manage plugins | [anthropic/plugin-marketplaces.md](./anthropic/plugin-marketplaces.md) | 2026-07-05 |
| Plugin dependencies — semver version constraints and resolution | [anthropic/plugin-dependencies.md](./anthropic/plugin-dependencies.md) | 2026-07-05 |
| Plugin hints — prompt users to install marketplace plugins | [anthropic/plugin-hints.md](./anthropic/plugin-hints.md) | 2026-07-05 |
| Plugin relevance — suggest plugins via relevance blocks and signal matching | [anthropic/plugin-relevance.md](./anthropic/plugin-relevance.md) | 2026-07-05 |
| Plugins reference — components, CLI commands, schemas, dev tools | [anthropic/plugins-reference.md](./anthropic/plugins-reference.md) | 2026-07-05 |
| Environment variables — shell setup, settings precedence, variable catalog | [anthropic/env-vars.md](./anthropic/env-vars.md) | 2026-07-05 |
| Built-in tools reference — tools, permissions, behaviors | [anthropic/tools-reference.md](./anthropic/tools-reference.md) | 2026-07-05 |
| Hooks reference — events, schemas, handlers, exit codes | [anthropic/hooks.md](./anthropic/hooks.md) | 2026-07-05 |
| Model lineup — names, capabilities, pricing, platform availability | [anthropic/models.md](./anthropic/models.md) | 2026-07-05 |
| Agent Skills via the Messages API — custom and managed skills | [anthropic/skills-api-guide.md](./anthropic/skills-api-guide.md) | 2026-07-05 |
| Agent Skills — authoring best practices for concise, effective skills | [anthropic/skills-best-practices.md](./anthropic/skills-best-practices.md) | 2026-07-05 |
| Writing tools for agents — designing tools & evals (engineering post) | [anthropic/writing-tools-for-agents.md](./anthropic/writing-tools-for-agents.md) | 2026-07-05 |
| Agent SDK — overview: build agents with tools, hooks, subagents | [anthropic/agent-sdk/overview.md](./anthropic/agent-sdk/overview.md) | 2026-07-05 |
| Agent SDK — agent loop: message types, turns, context & budget | [anthropic/agent-sdk/agent-loop.md](./anthropic/agent-sdk/agent-loop.md) | 2026-07-05 |
| Agent SDK — load Claude Code features via filesystem settings | [anthropic/agent-sdk/claude-code-features.md](./anthropic/agent-sdk/claude-code-features.md) | 2026-07-05 |
| Agent SDK — sessions: continue, resume, fork, cross-host | [anthropic/agent-sdk/sessions.md](./anthropic/agent-sdk/sessions.md) | 2026-07-05 |
| Agent SDK — session storage: mirror transcripts to S3/Redis/custom | [anthropic/agent-sdk/session-storage.md](./anthropic/agent-sdk/session-storage.md) | 2026-07-05 |
| Agent SDK — streaming vs single-message input modes | [anthropic/agent-sdk/streaming-vs-single-mode.md](./anthropic/agent-sdk/streaming-vs-single-mode.md) | 2026-07-05 |
| Agent SDK — user input: tool approvals and clarifying questions via callbacks | [anthropic/agent-sdk/user-input.md](./anthropic/agent-sdk/user-input.md) | 2026-07-05 |
| Agent SDK — streaming output: text responses and tool calls | [anthropic/agent-sdk/streaming-output.md](./anthropic/agent-sdk/streaming-output.md) | 2026-07-05 |
| Agent SDK — structured outputs via JSON Schema, Zod, or Pydantic | [anthropic/agent-sdk/structured-outputs.md](./anthropic/agent-sdk/structured-outputs.md) | 2026-07-05 |
| Agent SDK — custom tools: define, register, manage | [anthropic/agent-sdk/custom-tools.md](./anthropic/agent-sdk/custom-tools.md) | 2026-07-05 |
| Agent SDK — MCP: connect external tools, transport, auth | [anthropic/agent-sdk/mcp.md](./anthropic/agent-sdk/mcp.md) | 2026-07-05 |
| Agent SDK — tool search: dynamically load tools to save context | [anthropic/agent-sdk/tool-search.md](./anthropic/agent-sdk/tool-search.md) | 2026-07-05 |
| Agent SDK — subagents: creation, context isolation, parallelization | [anthropic/agent-sdk/subagents.md](./anthropic/agent-sdk/subagents.md) | 2026-07-05 |
| Agent SDK — modifying system prompts: presets, append, output styles | [anthropic/agent-sdk/modifying-system-prompts.md](./anthropic/agent-sdk/modifying-system-prompts.md) | 2026-07-05 |
| Agent SDK — slash commands: discovery, built-in, custom markdown | [anthropic/agent-sdk/slash-commands.md](./anthropic/agent-sdk/slash-commands.md) | 2026-07-05 |
| Agent SDK — skills: filesystem-based, discovery and invocation | [anthropic/agent-sdk/skills.md](./anthropic/agent-sdk/skills.md) | 2026-07-05 |
| Agent SDK — plugins: local loading, namespaced skills, manifest validation | [anthropic/agent-sdk/plugins.md](./anthropic/agent-sdk/plugins.md) | 2026-07-05 |
| Agent SDK — permissions: modes, rules, runtime callbacks | [anthropic/agent-sdk/permissions.md](./anthropic/agent-sdk/permissions.md) | 2026-07-05 |
| Agent SDK — hooks: intercept events, control permissions, transform tool I/O | [anthropic/agent-sdk/hooks.md](./anthropic/agent-sdk/hooks.md) | 2026-07-05 |
| Agent SDK — cost tracking: token usage, costs, caching | [anthropic/agent-sdk/cost-tracking.md](./anthropic/agent-sdk/cost-tracking.md) | 2026-07-05 |
| Agent SDK — observability: OpenTelemetry export, traces, data controls | [anthropic/agent-sdk/observability.md](./anthropic/agent-sdk/observability.md) | 2026-07-05 |
| Agent SDK — todo tracking: display task progress via todo/Task tools | [anthropic/agent-sdk/todo-tracking.md](./anthropic/agent-sdk/todo-tracking.md) | 2026-07-05 |
| Agent SDK — TypeScript API reference: query, async generators, types | [anthropic/agent-sdk/typescript.md](./anthropic/agent-sdk/typescript.md) | 2026-07-05 |
| Agent SDK — Python API reference: query() and ClaudeSDKClient | [anthropic/agent-sdk/python.md](./anthropic/agent-sdk/python.md) | 2026-07-05 |
| uv — running scripts: inline dependencies and executables | [astral/uv-scripts.md](./astral/uv-scripts.md) | 2026-07-05 |
| uv — projects: create, manage, and build Python projects | [astral/uv-projects.md](./astral/uv-projects.md) | 2026-07-05 |
| Codex — basic config: locations, precedence, common options, feature flags | [openai/codex/config-basic.md](./openai/codex/config-basic.md) | 2026-07-05 |
| Codex — advanced config: profiles, CLI overrides, precedence | [openai/codex/config-advanced.md](./openai/codex/config-advanced.md) | 2026-07-05 |
| Codex — config.toml reference: user, project, security settings | [openai/codex/config-reference.md](./openai/codex/config-reference.md) | 2026-07-05 |
| Codex — environment variables: config, install, auth, diagnostics | [openai/codex/environment-variables.md](./openai/codex/environment-variables.md) | 2026-07-05 |
| Codex — annotated sample config.toml: models, approvals, sandbox | [openai/codex/config-sample.md](./openai/codex/config-sample.md) | 2026-07-05 |
| Codex — rules: control command execution with patterns and safe shell parsing | [openai/codex/rules.md](./openai/codex/rules.md) | 2026-07-05 |
| Codex — hooks: events, discovery, trust, lifecycle config | [openai/codex/hooks.md](./openai/codex/hooks.md) | 2026-07-05 |
| Codex — AGENTS.md: discovery, global guidance, instruction layering | [openai/codex/agents-md.md](./openai/codex/agents-md.md) | 2026-07-05 |
| Codex — MCP: server configuration and integration | [openai/codex/mcp.md](./openai/codex/mcp.md) | 2026-07-05 |
| Codex — skills: create, distribute, and manage reusable skills | [openai/codex/skills.md](./openai/codex/skills.md) | 2026-07-05 |
| Codex — subagents: parallel workflows, custom TOML agents, CSV batches | [openai/codex/subagents.md](./openai/codex/subagents.md) | 2026-07-05 |
