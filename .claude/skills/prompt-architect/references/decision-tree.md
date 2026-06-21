# Decision Tree: Skill vs Command vs Subagent

Commands and skills have been merged. `.claude/commands/deploy.md` (single file) and `.claude/skills/deploy/SKILL.md` (directory) both create `/deploy` and use the **same frontmatter**. The real distinction is **directory format with bundled resources** (recommended) vs **single-file legacy format** (use only for trivial cases).

## Quick decision matrix

| Property | Skill (directory) | Command (legacy single file) | Subagent |
|---|---|---|---|
| **Invocation** | Auto-discovered by description OR `/name` | Auto-discovered OR `/name` | Delegated by description, OR `@name` |
| **File structure** | Directory with `SKILL.md` + optional resources | Single `.md` file | Single `.md` file |
| **Bundled resources** | Yes (`references/`, `scripts/`, `assets/`) | No | No (but can preload skills via `skills:` field) |
| **Context** | Same as main conversation | Same as main conversation | Fresh, isolated context window |
| **Tools** | Inherits Claude's; `allowed-tools` pre-approves | Same | Configurable allowlist/denylist |
| **Model override** | `model:` field | `model:` field | `model:` field |
| **Persistent memory** | No | No | Yes (`memory: user|project|local`) |
| **Hooks** | Yes (`hooks:` frontmatter) | Yes (`hooks:` frontmatter) | Yes (`hooks:` frontmatter) |
| **Best for** | Most reusable artifacts (~80%) | Trivial single-file cases | Context isolation + tool restrictions + memory |

## Decision flow

```
What does the user want?
│
├─ Is the CORE of the work ORCHESTRATION? (deterministic fan-out, multi-stage
│  pipeline, adversarial verification, scale beyond one context, loop-until-dry)
│  └─ A DYNAMIC WORKFLOW is in play — but as an orchestration LAYER, usually
│     fronted by a thin skill, NOT instead of one. See dynamic-workflows.md for the
│     conservative bar + which shape, then pick the fronting artifact below.
│
├─ Reusable expertise / workflow invoked many times
│  ├─ Needs context isolation, tool restrictions, or persistent memory?
│  │  ├─ Yes → SUBAGENT
│  │  └─ No  → SKILL (directory format)
│  └─ Genuinely trivial, no bundled resources ever?
│     └─ COMMAND (legacy single-file format) — but skill is still safer
│
├─ One-off task right now
│  └─ Don't build an artifact — just do the task
│
└─ Upgrade existing prompt for 4.8
   └─ Same artifact type; apply anti-pattern review + add hooks if warranted
```

## Dynamic workflow — the orthogonal axis

The first branch above is **orthogonal** to skill/command/subagent, not a fifth mutually
exclusive box. A dynamic workflow (`Workflow` tool) writes a JS harness that fans out subagents
deterministically; it runs headless and returns a value, so it's almost never what the user
invokes directly. The build target is normally *a saved workflow plus a thin trigger skill*
(the `/artifact-eval` → `artifact-eval.js` pattern), or a skill that emits an ad-hoc
workflow at runtime.

Reach for one **only when fan-out is load-bearing** — a correctness requirement, not "there's
some parallelism." 4.8 spawns fewer subagents by default and the `Workflow` tool requires
explicit opt-in (it can spawn dozens of agents), so the bar is high. `dynamic-workflows.md`
carries the full bar, the guardrails, and the shape ladder (inline-spawn → ad-hoc emit →
skill-fronts-saved → standalone).

## When to pick skill (directory format) — the default

Pick skill (directory) when **any** is true:

1. Should auto-trigger from user phrasing (no slash trigger required)
2. Same expertise applies across many phrasings
3. Benefits from bundled resources (scripts, references, assets)
4. May span multiple turns within the same conversation
5. Invoked via `/name` AND benefits from `allowed-tools`, `model`, `effort`, `paths`, or hooks

Storage: `.claude/skills/<name>/SKILL.md` (project) or `~/.claude/skills/<name>/SKILL.md` (user).

### Skill subtypes

| Subtype | Frontmatter | When |
|---|---|---|
| Reference content | Default | Knowledge applied inline ("API conventions", "team style guide") |
| Task content | `disable-model-invocation: true` | User-triggered workflows with side effects (`/deploy`, `/commit`) |
| Forked task | `context: fork`, `agent:` | Heavy work that should run isolated (research that floods main context) |

## When to pick command (legacy single-file)

Pick command only when **all** are true:

1. Artifact is genuinely trivial — body is short, no bundled resources needed ever
2. You're maintaining an existing `.claude/commands/` file
3. You don't anticipate scripts, references, or assets in the future

Even trivial artifacts often benefit from directory format because upgrading later is cheaper. Default to skill format unless you have a specific reason. Storage: `.claude/commands/<name>.md`.

Non-breaking upgrade path: move to `.claude/skills/<name>/SKILL.md`; the skill takes precedence over a same-named command.

## When to pick subagent

Pick subagent when **any** is true:

1. High-volume output (logs, search results, file contents) shouldn't pollute main context
2. Need tool restrictions (read-only, no-internet, restricted paths)
3. Should run on a different model (Haiku for cheap exploration, Opus for hard reasoning)
4. Needs persistent memory across conversations (`memory: user|project|local`)
5. Should run in parallel with other tasks (`background: true`)
6. Has its own permission mode requirements (plan mode, accept-edits within scope)

Classic examples: `code-reviewer`, `db-reader`, `security-auditor`. Storage: `.claude/agents/<name>.md`.

## Hooks — cross-cutting decision (see `hooks.md`)

| Scenario | Suggested hook |
|---|---|
| Artifact that edits code | `PostToolUse: Edit|Write` → linter |
| Artifact that deploys | `Stop` → notification |
| Artifact that runs Bash | `PreToolUse: Bash` → deny-unsafe-commands |
| Hard completion criteria | `Stop` → verify done |

Hooks in artifact frontmatter only fire while the artifact is active.

## Combination patterns (short)

| Pattern | Shape | When |
|---|---|---|
| **Skill forks into Explore subagent** | Skill frontmatter has `context: fork`, `agent: Explore` | Heavy work that should run isolated; no separate subagent file needed |
| **Skill delegates to named subagent** | Skill's body says "invoke `code-reviewer` subagent for X" | Pre-existing subagent does part of the work |
| **Subagent preloads skills** | Subagent frontmatter has `skills: [...]` | Subagent's work needs existing skill content baked in at startup |
| **Skill + subagent + hooks** (full stack) | All three combined | Sophisticated workflows (rare but real). Build bottom-up: skills → subagent → orchestrating skill. |

4.8 spawns fewer subagents by default. If an orchestrating artifact genuinely needs parallel fan-out, say so explicitly — *"spawn subagents in parallel when fanning out across multiple files or independent items; do single-file work inline."* Otherwise leave it; the conservative default is usually right (4-8-principles §5).

## Edge cases

- **"Skill that's also a slash command"** — Every skill IS a slash command. `/skill-name` invokes it.
- **"Subagent the user can invoke directly"** — Subagents are invoked via natural language or `@name`. For a slash trigger that runs a subagent's work, build a skill with `context: fork` and `agent: <subagent-name>`.
- **"Persistent memory in my skill"** — Skills don't support `memory:`. Use a subagent, or a skill that delegates to a memory-enabled subagent.
- **"Different model for my skill"** — Skills support `model:` frontmatter. For longer-running overrides across many turns, use a subagent.
- **"Conditional hooks"** — Frontmatter hooks fire whenever the artifact is active. For conditional firing, define in `settings.json` with a narrow matcher.

## When to push back

- User asks for a command but the artifact clearly needs bundled resources → recommend skill (directory). Don't silently substitute.
- User asks for a subagent for trivial work → suggest a skill. Subagent overhead isn't worth it.
- User wants to skip hooks where enforcement clearly matters (CI deploy with no test gate) → surface the risk explicitly: *"Without a Stop hook to verify tests, this declares success even when tests fail. Want to add one?"*
