# Claude Code Subagents

## What it is

A Claude Code subagent is one Markdown file (`.claude/agents/<name>.md`) that
Claude **auto-delegates to** off its `description`. It runs in its own context
window with its own tool pool, does a scoped job, and hands a result back to the
caller — keeping verbose work out of the main thread. Field surface:
`references/frontmatter.md`. Full worked example: `examples/claude-subagent.md`.

## When to build one (vs a skill / command / Codex agent)

- **Claude subagent** — delegated, context-isolating work Claude should route to
  on its own: research that would flood the main thread, a scoped executor, a
  fan-out worker. It needs Claude's tool/effort/memory surface.
- **Skill** (use meta-skill) — reusable knowledge or a workflow that runs **in
  the main conversation**, not a separate context.
- **Slash command** (use meta-commands) — a repeatable user-invoked prompt.
- **Codex agent** (`references/codex-agents.md`) — the job runs as a separate
  Codex process via `codex exec`, or you want a second, non-Claude reviewer.

If unclear, ask — don't guess.

## How delegation works

Claude reads every subagent's `name` + `description` and routes to the best
match. That makes the `description` the whole triggering surface: a vague one
never fires; an over-broad one steals adjacent work. Write it third person, name
the real contexts/phrasings, add "use proactively" for auto-delegation, and put a
Not-for boundary that routes siblings' work away (see `frontmatter.md`).

## Where the file lives — scopes & precedence

| Location | Scope | Priority |
|---|---|---|
| Managed settings `.claude/agents/` | Organization | 1 (highest) |
| `--agents` CLI flag (JSON) | Session | 2 |
| `.claude/agents/` | Project | 3 |
| `~/.claude/agents/` | All your projects | 4 |
| Plugin `agents/` | Where enabled | 5 (lowest) |

Same `name` in two scopes → higher priority wins. Project scope is discovered by
walking up from the cwd; the definition closest to the cwd wins among nested
project dirs. Plugin subfolders join the id (`plugin:subfolder:name`);
project/user subfolders do **not** affect identity — only the `name` field does.

## Nested spawning

Listing `Agent` in `tools` lets a subagent spawn its own subagents (depth capped
at 5). A type list inside `Agent(...)` is only honored for a whole-session
`--agent`; inside an ordinary subagent it's ignored. To block one subagent
globally, use `permissions.deny: ["Agent(name)"]` in settings.
