# Routing: Is This an Agent at All?

A Claude Code subagent is one Markdown file (`.claude/agents/<name>.md`) that
Claude **auto-delegates to** off its `description`. It runs in its own context
window with its own tool pool, does a scoped job, and hands a result back —
keeping verbose work out of the main thread. Field surface: `frontmatter.md`.
Full worked example: `../examples/claude-subagent.md`.

## Pick the artifact

| Build | When | Author with |
| --- | --- | --- |
| **Claude subagent** | Delegated, context-isolating work Claude should route to on its own: research that would flood the main thread, a scoped executor, a fan-out worker. Needs Claude's tool/effort/memory surface. | this skill |
| **Skill** | Reusable knowledge or a procedure that runs **in the main conversation**, where the user can watch and steer each step. | meta-skills |
| **Slash command** | A repeatable user-invoked prompt. | meta-skills |
| **Path-scoped rule** | A constraint that applies whenever certain files are touched. Loads only on those paths, costs nothing elsewhere. | `.claude/rules/` |
| **Hook or permission rule** | Anything that must always happen, or must never happen. Deterministic — it doesn't depend on the model choosing to comply. | [hooks.md](../../../rules/harness-layer/hooks.md) |
| **Codex agent** | The job runs as a separate `codex exec` process, or you want a second non-Claude reviewer. | `codex-agents.md` |

Three failure modes are worth naming. An instruction is a preference, so "always
do X" and "never do Y" belong in a hook or a permission rule, not in an agent
body. Work the main thread needs to reason over step by step is a skill —
isolation is the reason to delegate and equally the cost. And a one-off side task
that would need the whole conversation restated to be useful wants a fork
(`/subtask`), which inherits the full history and shares the prompt cache — no
file to author at all.

If unclear, ask — don't guess.

## How delegation works

Claude reads every subagent's `name` + `description` and routes to the best
match. That makes the `description` the whole triggering surface: a vague one
never fires; an over-broad one steals adjacent work. Write it third person, name
the real contexts and phrasings, add "use proactively" for auto-delegation, and
give it a Not-for boundary that routes siblings' work away (see
`frontmatter.md`).

## Where the file lives — scopes & precedence

| Location | Scope | Priority |
| --- | --- | --- |
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

An agent that can spawn needs a delegation cap in its body — see
`model-tuning.md`.
