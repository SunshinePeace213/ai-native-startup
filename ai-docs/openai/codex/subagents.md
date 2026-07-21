---
source: https://learn.chatgpt.com/docs/agent-configuration/subagents
fetched: 2026-07-21
---
> **In here:** Parallel agent workflows and context isolation · Custom agent definition and configuration · Batch processing and sandbox inheritance

# Subagents in ChatGPT and Codex

## Overview

Subagents enable parallel agent workflows in ChatGPT and Codex, allowing specialized agents to handle independent tasks simultaneously before consolidating results. This architecture is particularly valuable for complex, parallel-intensive work like codebase exploration or multi-step feature implementation.

## Key Benefits

The primary advantage lies in preventing "context pollution"—when intermediate outputs (logs, traces, test results) overwhelm the main conversation thread. By isolating noisy work to specialized subagents, the main agent stays focused on requirements and decisions while subagents return distilled summaries.

Subagents excel at "read-heavy tasks such as exploration, tests, triage, and summarization" but require careful coordination when handling parallel write operations that could create conflicts.

## Availability

- **Work mode**: Exposes subagent workflows by default on eligible accounts
- **Codex releases**: Enable subagent workflows automatically
- **Token consumption**: Higher than single-agent equivalents due to independent model work per subagent

## Triggering Workflows

**ChatGPT (most levels)**: Request delegation explicitly. Example: "Spawn one agent per point" for parallel review tasks.

**ChatGPT Ultra**: Can proactively delegate suitable independent work without explicit requests.

**Codex**: Delegates upon direct request or when `AGENTS.md` or skill instructions specify it.

## Model and Reasoning Configuration

| Model | Use Case |
| ------- | ---------- |
| `gpt-5.6` | Demanding multi-step work requiring planning and validation |
| `gpt-5.4` | Strong coding with robust tool use |
| `gpt-5.6-terra` | Fast, efficient read-heavy scans and exploration |
| `gpt-5.3-codex-spark` | Near-instant text iteration (ChatGPT Pro) |

**Reasoning effort levels** range from `minimal` to `ultra`, balancing response time against reasoning depth for complex problem-solving.

## Managing Subagents

The **Subagents** panel displays Active and Done lists. Users can:

- Inspect completed subagent details and results
- Use `/agent` (CLI) to switch between threads
- Ask Codex to steer, stop, or close individual subagent threads
- Expand the background-agent panel (IDE) to view status and controls

## Custom Agent Definition

Users can create custom agents via TOML files in `~/.codex/agents/` (personal) or `.codex/agents/` (project-scoped). Each requires:

- `name`: Agent identifier
- `description`: When Codex should use it
- `developer_instructions`: Core behavioral guidelines

Optional fields like `model`, `sandbox_mode`, and `mcp_servers` inherit from parent sessions when omitted.

## Global Settings

Key configuration options under `[agents]`:

| Setting | Purpose |
| --------- | --------- |
| `max_threads` | Concurrent open agent cap (default: 6) |
| `max_depth` | Spawning nesting depth (default: 1) |
| `job_max_runtime_seconds` | Worker timeout for CSV batch jobs |
| `interrupt_message` | Record interruption notifications (default: true) |

## CSV Batch Processing

The experimental `spawn_agents_on_csv` tool processes repeated tasks across multiple rows, spawning one worker per item and exporting combined results. Supports columns for templated instructions and structured JSON output schemas.

## Permissions and Sandbox Inheritance

Subagents inherit the parent session's sandbox policy and permission mode. Work mode runs subagents in its hosted environment; local Codex sessions inherit custom agent sandbox configurations, with interactive runtime overrides (like `/permissions` changes) reapplied to children.
