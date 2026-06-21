---
name: meta-agent
description: >-
  The team's canonical standard and guided workflow for authoring Claude Code
  subagents (the .claude/agents/*.md files). Use whenever the user wants to
  "create a new subagent", says "make an agent that ..." or "build a subagent
  for ...", asks to update or fix an agent's frontmatter, tools, or model,
  reports "my agent isn't triggering" / "isn't being delegated to", or wants to
  turn a repeated delegation into a reusable subagent. Fires even when the
  build-an-agent intent is buried inside a longer request. This is THE authority
  for subagent authoring — prefer it over ad-hoc advice.
when_to_use: >-
  Reach for this when choosing subagent frontmatter (tools, model, effort,
  memory, hooks, permissionMode), writing the description that controls
  delegation, structuring the agent body/system prompt, or debugging why an
  agent over- or under-triggers. Not for authoring Skills (use meta-skill) or
  slash commands (use meta-commands).
---

# Meta-Agent: Authoring Claude Code Subagents

This skill is both the **standard** for what a good subagent looks like and a
**workflow** for producing one. The standard lives in `references/`; this body
is the loop that applies it. Read each reference at the phase that needs it —
don't preload them all.

## Operating principle

A subagent is one Markdown file: YAML frontmatter (the trigger + capabilities)
and a body that **becomes its system prompt**. A non-fork subagent sees only
that prompt plus the delegation message Claude writes when handing off — not the
main conversation, not the files already read. Its power comes from a tight
trigger (`description`), least-privilege `tools`, a deliberately chosen `effort`,
and a lean body that restates the context the agent actually needs.

Apply these principles to the agent you build **and to your own conduct here.**
No fake incentives, no "think harder," no forced progress cadence. If quality
needs depth, raise `effort` (`high`/`xhigh`) rather than adding prose — that is
the dominant capability lever on Opus 4.8, and a subagent is the one artifact
where you set it in frontmatter.

## References — load each when its phase arrives

| Read | When |
|---|---|
| `references/frontmatter.md` | Choosing/validating fields; tool-inheritance order; tools unavailable to subagents; model resolution; the `effort` lever; memory; the plugin-ignored fields; writing the `description` |
| `references/body-structure.md` | Writing the body/system prompt: the skeleton, the five common shapes, and one fuller worked example |
| `references/authoring-principles.md` | The subagent-scoped Opus 4.8 deltas (effort, literal instruction-following, conservative fan-out, lean body, least privilege) |
| `references/anti-patterns.md` | What to cut, BAD→GOOD descriptions, and the **pre-ship checklist** (run before finishing) |

Validate any agent file (needs PyYAML):

```
cd ${CLAUDE_SKILL_DIR} && uv run --with pyyaml python scripts/validate_agent.py <path-to-agent.md>
```

It checks the frontmatter against the documented surface, prints `WARN:`/`FAIL:`
lines and a final `PASS`, and exits non-zero on any hard failure.

## The workflow

Phases, not a railroad. Skip what doesn't apply; loop back when a later phase
exposes a gap. The goal: an agent that delegates on the right requests and does
its scoped job better than no agent would.

### 1. Capture intent

Pin down before writing:
- **Job** — the one thing this agent does, and the lens it works through.
- **Triggers** — the actual contexts/phrasings that should route to it
  (including when the user doesn't name it). These become the `description`.
- **Return contract** — what the agent hands back to the caller, in what shape.

Confirm a subagent is even the right artifact. A subagent is for **delegated,
context-isolating work** (research that would flood the main thread, a scoped
executor, a fan-out worker). If the need is a reusable prompt/knowledge in the
main conversation, that's a **skill** (use meta-skill); a repeatable command is
a **slash command** (use meta-commands). If unclear, ask — don't guess.

### 2. Choose form & frontmatter

Read `references/frontmatter.md`. Only `name` and `description` are required.
- **`name`** — lowercase-hyphen, descriptive of the job, unique across the whole
  agents tree (project + user + plugins).
- **`description`** — the trigger document. Third person, front-loaded, names the
  real contexts/phrasings, "use proactively" for auto-delegation, a `Not for: …`
  boundary that routes adjacent work to a sibling.
- **`tools`** — least privilege; list only what the job needs (omitting `tools`
  inherits everything, including all MCP tools). `disallowedTools` is applied
  first, then `tools`.
- **`effort`** — set it deliberately: `xhigh` for hard coding/agentic work,
  `high` as the reasoning-sensitive default, `low`/`medium` for cheap scoped
  helpers.
- **`model`** — `inherit` unless the job wants a specific tier.
- **`memory`** — only when knowledge compounds across runs. Other fields
  (`permissionMode`, `hooks`, `skills`, `isolation`, `background`, `maxTurns`,
  `color`) only when the job needs them — see the reference.

### 3. Draft the body

Read `references/body-structure.md`. The body is the system prompt, so **restate
every rule, path, and convention the agent depends on** — it has no shared
history. Use the skeleton (role line → `When to invoke` with a `Not for`
boundary → `Inputs` → `Process` → `Success looks like` → `Output` → `Edge
cases`), pick the closest of the five shapes, and keep it lean: cut anything
that wouldn't change the output if deleted. Match repo tooling in examples
(`uv`, `bun`).

### 4. Write the file

Write to `.claude/agents/<name>.md` (project) or `~/.claude/agents/<name>.md`
(personal). Frontmatter is **real YAML between `---` markers at the top** — never
fenced in a ```` ``` ```` block. Use comma-separated tool lists, not the old
`prompt` field (the body is the prompt).

### 5. Validate

Run `scripts/validate_agent.py` on the file (invocation above). Fix every
`FAIL`; treat `WARN`s (unknown tool names, plugin-ignored fields) as prompts to
double-check intent.

### 6. Test vs baseline

There's no automated runner; the test is a comparison.
- Write 2–3 **realistic delegation prompts** the agent should handle, plus one
  that should NOT route to it (to catch over-triggering).
- Judge whether Claude would delegate to this agent on each — read the
  `description` cold, or spawn the agent on a real prompt and compare its output
  to doing the same work with no agent. The delta is what proves the agent earns
  its place.

### 7. Iterate

Fix the highest-leverage gap and re-check:
- **Not triggering / over-triggering** → tighten the `description` (real
  phrasings, "use proactively", a `Not for` boundary). See `anti-patterns.md`.
- **Right trigger, shallow work** → raise `effort`; don't add "think harder".
- **Wrong scope / wandering** → tighten `tools` and the body's scope statements.

Before finishing, run the pre-ship checklist at the bottom of
`references/anti-patterns.md`.

## Gotchas

- **The body is the system prompt.** A non-fork subagent sees only its prompt +
  the delegation message. Restate needed context; don't rely on shared history.
- **Tool resolution: `disallowedTools` first, then `tools`.** Omitting `tools`
  inherits every tool incl. all connected MCP servers (and their context cost).
- **Five tools never work in a subagent:** `AskUserQuestion`, `EnterPlanMode`,
  `ExitPlanMode` (unless `permissionMode: plan`), `ScheduleWakeup`,
  `WaitForMcpServers`. Don't design an agent that needs to ask the user mid-run.
- **Plugin agents silently ignore `hooks`, `mcpServers`, `permissionMode`.** Put
  the agent in `.claude/agents/` if it needs them.
- **`name` must be unique tree-wide** — a duplicate is silently discarded or
  loses on priority.
- **`skills:` preloads skill content; `tools: Skill` does not.** Use `skills:`
  to inject conventions at startup.
- **`validate_agent.py` needs PyYAML** (`--with pyyaml`) and takes the agent
  **file** path, not a directory.
