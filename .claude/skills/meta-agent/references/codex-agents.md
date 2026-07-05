# Codex Agents

## What it is

A Codex agent is a skill launched as its own Codex process — a `SKILL.md` under
`.agents/skills/<name>/`, invoked with `codex exec`. Codex has **no** subagent
frontmatter surface: the frontmatter is just `name` + a rich `description`, and
the **body carries the whole contract** (role, inputs, process, output). Codex
picks up repo conventions from `AGENTS.md` at runtime. Full worked example:
`examples/codex-subagent.md`.

```markdown
---
name: spec-review
description: "One rich sentence-plus naming the job, what it reads, what it
  returns, when to invoke it, and its boundary."
---

# <Title>

Role line. Then the sections the job needs: `## Inputs`, `## Process`,
`## Output`. No tools/model/effort fields — capability is the Codex run config.
```

## When to build one (vs a Claude subagent)

- **Codex agent** — the job should run as a separate Codex process (a second,
  independent reviewer; a cross-check from a different model; work you launch
  with `codex exec`). This repo already ships `spec-review` and
  `implementation-review` this way.
- **Claude subagent** (`references/claude-agents.md`) — Claude should
  auto-delegate to it in-session, and it needs the tool/effort/memory surface.

## How it differs from a Claude subagent

- **Frontmatter** — only `name` + `description`. No `tools`, `model`, `effort`,
  `memory`, `permissionMode`. Put every capability constraint (read-only, scope,
  which files to touch) in the body prose.
- **Invocation** — you run it explicitly with `codex exec`; there's no
  description-based auto-delegation the way Claude routes.
- **Inputs** — because it's launched with an explicit prompt, a Codex agent
  keeps an `## Inputs` section (a Claude subagent gets its inputs from the
  delegation message instead).
- **Location** — `.agents/skills/<name>/SKILL.md`, not `.claude/agents/*.md`.
