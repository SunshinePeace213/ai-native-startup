# Subagent Template

A subagent is a single markdown file with YAML frontmatter. The body is the system prompt. Frontmatter controls how and where it runs.

Reference: https://code.claude.com/docs/en/sub-agents

## Storage

- `.claude/agents/<name>.md` — project scope
- `~/.claude/agents/<name>.md` — user scope (all projects)

The frontmatter `name` must be unique. Filename should match by convention.

## Frontmatter fields

Two required: `name` and `description`. The rest are optional — most subagents need 4-6 fields total.

### Required

| Field | Purpose |
|---|---|
| `name` | Unique identifier; kebab-case; appears in `@-mentions` |
| `description` | When Claude should delegate. Triggering mechanism — name specific phrasings and contexts. |

### Tool control

| Field | Purpose |
|---|---|
| `tools` | Allowlist of tools the subagent can use |
| `disallowedTools` | Denylist removed from inherited/specified list. Both applied: `disallowedTools` first, then `tools` from remaining pool. |

### Model & effort

| Field | Values |
|---|---|
| `model` | `sonnet`, `opus`, `haiku`, full ID like `claude-opus-4-8`, or `inherit` (default) |
| `effort` | `low` / `medium` / `high` / `xhigh` / `max` |

Non-default model: `haiku` for cheap exploration; `opus` for hard reasoning regardless of session.

**Effort is the dominant lever on 4.8** — more so than on any prior Opus, and the subagent is the one artifact type where you set it explicitly. Reach for `effort` before reaching for "think harder" prose. Choose deliberately per agent — a fleet that is uniformly `high` is a sign nobody actually made the call:

- `xhigh` — hard coding/agentic subagents (default for an implementer), and any agent doing hard adversarial or multi-deliverable reasoning (red-teamers, deep market/competitor analysis).
- `high` — reasoning-sensitive subagents (reviewers, planners). The floor for intelligence-sensitive work — but don't stop here by reflex; escalate to `xhigh` when the task is genuinely hard.
- `medium` / `low` — only for scoped, latency-sensitive helpers (e.g. a cheap, broad, read-only researcher fanned out in parallel). 4.8 scopes work tightly at these levels, so don't use them for anything that needs depth.

Thinking is off by default on 4.8; reasoning depth follows from `effort`, not from prompt prose. At `high`/`xhigh`/`max`, give the subagent a large output budget (`maxTurns` and the harness's token budget) so it has room to think and act.

### Permissions / isolation / preloading

| Field | Purpose |
|---|---|
| `permissionMode` | `default`, `acceptEdits`, `auto`, `dontAsk`, `bypassPermissions`, `plan` |
| `isolation` | Set to `worktree` for a separate git worktree |
| `skills` | List of skill names injected into the subagent's context at startup |
| `mcpServers` | MCP servers available to this subagent (by name or inline) |

### Memory

| Field | Purpose | Scopes |
|---|---|---|
| `memory` | Persistent directory across conversations | `user` (cross-project), `project` (per-project, shareable), `local` (per-project, not VC) |

Only enable when knowledge compounds (patterns, debugging insights, recurring issues).

### Hooks

| Field | Purpose |
|---|---|
| `hooks` | PreToolUse, PostToolUse, Stop, SubagentStop hooks scoped to this subagent. See `hooks.md`. |

Common subagent patterns: `PreToolUse` to block dangerous commands; `PostToolUse` linter after edits; `Stop` (auto → `SubagentStop`) for verification before returning.

### Other

| Field | Purpose |
|---|---|
| `maxTurns` | Cap on agentic turns |
| `background` | `true` → always run as background task |
| `color` | Display color (red/blue/green/yellow/purple/orange/pink/cyan) |
| `initialPrompt` | Auto-submitted first user turn when running via `--agent` |

## Body (system prompt)

The body IS the system prompt — keep it focused and self-contained. The subagent doesn't see main conversation history, only its prompt + the delegation message, so restate any rule it depends on.

Use a few `##` headers for structure (2-3 levels max — Pattern 9). The section set maps 1:1 to `command-template.md` (Role, Scope→When to invoke, Output specification→Output, Success criteria→Success looks like, Error handling→Edge cases) so the two artifact types stay in sync. Keep headers only where they earn their place — a very short agent can stay flat.

```markdown
[Role: 1-2 sentences — who this agent is and the ONE job it owns. A focused lens, not a résumé (no inflated persona — Pattern 5). Second person.]

## When to invoke
- **<scenario>** — <one-line condition, third person>.
- **<scenario>** — <…>.
- **Not for:** <the adjacent job this agent should refuse or hand back — the negative boundary the description can't carry>.

## Inputs
Your delegation prompt gives you:
- **<input>** — <what it is / where to read it>.

## Process
When invoked:
1. <action — state the goal; keep strict order only where order is load-bearing (Tip 4)>
2. <…>

## Success looks like
<The Success Brief: concrete, checkable criteria for a good result — NOT "be thorough" (Pattern 8). Before returning, check the output against these and fix any gap rather than returning a partial result.>
<Review/finding agents only: tag each finding with confidence + severity for a downstream filter — don't self-filter or loop on an arbitrary score (4-8-principles §10). Runtime self-scoring rubrics are wasteful; they're for human review, not the agent.>

## Output
<Exact format/headings — inline them here so the agent degrades gracefully if an external brief can't be found. State where output is written (path) and the single line returned to the main conversation.>

## Edge cases
- <failure / ambiguity / missing input> → <what to do>.
```

Apply 4.8 anti-pattern rules throughout (see `anti-patterns.md`). The Five Shapes below illustrate **frontmatter** variety; for body structure, use the skeleton above.

**Worked example (full body skeleton, end-to-end):** `assets/examples/subagent-example-security-reviewer.md` renders this skeleton completely — role line, `## When to invoke` with a "Not for" boundary, `## Success looks like` (with the finding-vs-filtering split for a review agent), a concrete `## Output`, and `## Edge cases` — with a deliberate `effort` and a least-privilege toolset. Clone it (not the terse Shapes) when you want the current body shape. This is the subagent parity for `command-template.md`'s "Worked example: /commit".

## Five common shapes

### Shape A — Read-only researcher

```yaml
---
name: codebase-explorer
description: Explore the codebase to answer questions about architecture, find specific files, or trace how code paths work. Use when the user asks "how does X work", "where is Y", or wants a code map.
tools: Read, Grep, Glob, Bash
model: haiku
---

You explore codebases efficiently and return concise summaries.

When invoked:
1. Understand the question
2. Use Grep and Glob to find relevant files
3. Read the files that look load-bearing
4. Return a focused summary with file paths and key snippets

Don't return verbose dumps. The main conversation needs the answer, not raw material.
When you can't find what you're looking for, say so plainly.
```

### Shape B — Specialist with persistent memory

```yaml
---
name: code-reviewer
description: Review code changes for quality, security, and consistency with this project's patterns. Use after significant edits, before PRs, or when the user asks for a review.
tools: Read, Grep, Glob, Bash
memory: project
---

You review code with persistent memory of this project's patterns and recurring issues.

When invoked:
1. Read MEMORY.md for past reviews and project conventions
2. `git diff` for recent changes (or files the user named)
3. Review against: clarity, security, project-specific patterns from MEMORY.md
4. Return findings by severity: critical / warnings / suggestions

After the review: update MEMORY.md with new patterns or recurring issues.
Keep MEMORY.md focused — patterns and decisions, not blow-by-blow logs.
```

### Shape C — Restricted executor (read-only SQL)

```yaml
---
name: db-reader
description: Run read-only SQL queries against the project database. Use when the user asks to query data, run reports, or check database state. Refuses writes.
tools: Bash
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "./scripts/validate-readonly-query.sh"
---

You run read-only database queries via the project's CLI.

When invoked:
1. Understand the question
2. Write a SELECT query (writes are blocked at hook level)
3. Run via Bash
4. Return results as a markdown table

If the user asks for a write, explain you only have read access; suggest they run it themselves.
```

### Shape D — Skill-augmented specialist

```yaml
---
name: api-developer
description: Implement REST API endpoints following team conventions. Use when the user asks to add a new endpoint, modify endpoint behavior, or scaffold an API resource.
tools: Read, Write, Edit, Bash, Grep, Glob
skills:
  - api-conventions
  - error-handling-patterns
---

You implement API endpoints following preloaded team conventions.

When invoked:
1. Understand purpose, inputs, outputs
2. Follow the preloaded skills' conventions
3. Write tests alongside implementation
4. Return summary of files changed and how to test
```

### Shape E — Hook-enforced workflow with verification

```yaml
---
name: feature-implementer
description: Implement a feature end-to-end, including tests. Use when the user describes a new feature or asks to add functionality with quality gates.
tools: Read, Write, Edit, Bash, Grep, Glob
effort: xhigh
hooks:
  PreToolUse:
    - matcher: "Edit|Write"
      hooks:
        - type: command
          command: "${CLAUDE_PROJECT_DIR}/.claude/hooks/protect-files.sh"
  PostToolUse:
    - matcher: "Edit|Write"
      hooks:
        - type: command
          command: "npx prettier --write \"$CLAUDE_PROJECT_DIR\""
  Stop:
    - hooks:
        - type: prompt
          prompt: "Verify all requested functionality is implemented and tests pass. If not, respond {\"ok\": false, \"reason\": \"...\"}."
---

You implement features end-to-end with quality enforced via hooks.

When invoked:
1. Understand requirements
2. Plan implementation across files
3. Write code alongside tests
4. Run the test suite
5. Return a summary

PreToolUse blocks edits to protected files. PostToolUse formats every write. Stop verifies completeness. You focus on implementation.
```

This shape demonstrates the value of hooks: the model focuses on work because hooks handle verification. See `hooks.md`.

**Interactive / multi-turn coding subagents (Shapes D & E):** capture task, intent, and constraints upfront and minimize required back-and-forth (auto-proceed on sensible defaults rather than stopping to ask). 4.8 reasons more after each user turn, so fewer, well-specified turns cost fewer tokens and perform better. Pair with `effort: xhigh`/`high`. (4-8-principles §11)

## Anti-patterns

- Too many tools — start minimum, add as needed
- Vague description — be specific; description IS the trigger
- Long unfocused prompt — body tight; no life story
- Memory enabled for one-shot work — only when knowledge compounds
- Capital-letter MUSTs without *why* clauses (P4 in `anti-patterns.md`)
- Inflated persona ("10,000+ reviews") — focused sentence or invoke `tech-company-personas`

## After drafting

Test with realistic queries before declaring done. Does it stay in scope? Return summaries not dumps? Handle missing inputs gracefully?

If memory is enabled: run twice on related tasks; verify the second run benefits from the first.

For quantitative validation, run prompt-architect's bundled `scripts/aggregate_benchmark.py` over a workspace with multiple iterations.
