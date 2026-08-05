# Codex Agents

## What it is

A Codex custom agent is a TOML file under `.codex/agents/` (project-scoped;
`~/.codex/agents/` for personal), spawned as a subagent thread by a Codex
session. Three required keys carry the whole contract; `model`, `sandbox_mode`,
and `mcp_servers` are optional and inherit from the parent session when omitted.
Source: `ai-docs/openai/codex/subagents.md`.

```toml
name = "spec-review"
description = "One rich sentence-plus naming the job, what it reads, what it returns, when to invoke it, and its boundary."
developer_instructions = """
Role line. Then the sections the job needs: inputs, process, output.
Put every capability constraint (read-only, scope, which files to touch) here.
"""
```

## When to build one (vs a Claude subagent)

- **Codex agent** — the job should run inside a Codex session as a parallel
  thread: read-heavy exploration, triage, or summarization that Codex delegates
  to per `AGENTS.md` or on request.
- **Claude subagent** (`routing.md`) — Claude should auto-delegate to it
  in-session, and it needs the tool/effort/memory surface.
- **Neither** — a one-shot cross-model review is a plain `codex exec` call with
  an inline prompt; it needs no agent file.

## How it differs from a Claude subagent

- **Format** — TOML keys, not markdown frontmatter + body. No `tools`, `effort`,
  `memory`, or `permissionMode` surface; capability constraints live in
  `developer_instructions` prose, and sandbox/permissions inherit from the
  parent session.
- **Invocation** — spawned by a Codex session (on request, or when `AGENTS.md`
  or a skill says to); there's no description-based auto-delegation the way
  Claude routes.
- **Model/effort** — declared in the TOML (`model` plus
  `model_reasoning_effort`) per the model-selection roster;
  `tests/harness-layer/test_model_drift.py` pins both to it.
- **Location** — `.codex/agents/<name>.toml`, not `.claude/agents/*.md`.
