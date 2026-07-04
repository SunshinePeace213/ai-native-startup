---
name: meta-agent
description: >-
  The team's canonical standard and guided workflow for authoring subagents —
  Claude Code subagents (.claude/agents/*.md) and Codex agents
  (.agents/skills/*/SKILL.md). Use whenever the user wants to "create a new
  subagent", says "make an agent that ..." or "build a subagent for ...", asks to
  update or fix an agent's frontmatter, tools, or model, reports "my agent isn't
  triggering" / "isn't being delegated to", or wants to turn a repeated
  delegation into a reusable subagent. Fires even when the build-an-agent intent
  is buried inside a longer request. This is THE authority for subagent authoring
  — prefer it over ad-hoc advice.
when_to_use: >-
  Reach for this when choosing subagent frontmatter (tools, model, effort,
  memory, hooks, permissionMode), writing the description that controls
  delegation, structuring the agent body/system prompt, deciding Claude subagent
  vs Codex agent, or debugging why an agent over- or under-triggers. Not for
  authoring Skills (use meta-skill) or slash commands (use meta-commands).
---

# Meta-Agent: Authoring Subagents

The **standard** for what a good subagent looks like and the **workflow** for
producing one. The standard lives in `references/`; this body is the loop that
applies it. Read each reference at the phase that needs it — don't preload them.

## Operating principle

A subagent does one scoped, context-isolating job and hands a result back. Its
power comes from a tight trigger (`description`), least-privilege tools, and a
lean body that **restates the context the agent actually needs** — a non-fork
subagent sees only its prompt plus the delegation message, not the main
conversation. Apply this to the agent you build **and to your own conduct here.**
No fake incentives, no "think harder." Depth comes from `effort`, not prose — but
omit `effort` by default (the shipped team agents do) and set it only when the
job needs it.

## References — load each when its phase arrives

| Read | When |
|---|---|
| `references/claude-agents.md` | Deciding Claude subagent vs skill/command/Codex; how delegation works; where the file lives (scopes & precedence) |
| `references/codex-agents.md` | Building a Codex agent (`.agents/skills/*/SKILL.md`, `codex exec`) instead of a Claude subagent |
| `references/frontmatter.md` | Choosing/validating Claude frontmatter fields; tool resolution; the load-bearing gotchas; writing the `description` |
| `references/body-structure.md` | Writing the body/system prompt: the skeleton, common shapes, body anti-patterns |
| `examples/claude-subagent.md`, `examples/codex-subagent.md` | A full worked agent in each ecosystem |

Validate a **Claude** agent file (checks its frontmatter; not for Codex):

```
cd ${CLAUDE_SKILL_DIR} && uv run --with pyyaml python scripts/validate_agent.py <path-to-agent.md>
```

It prints `WARN:`/`FAIL:` lines and a final `PASS`, exiting non-zero on failure.

## The workflow

Phases, not a railroad. Skip what doesn't apply; loop back when a later phase
exposes a gap.

1. **Capture intent** — the one **job** and its lens, the real **triggers** (the
   contexts/phrasings that should route here), and the **return contract**.
   Confirm a subagent is even the right artifact — if the need is main-thread
   knowledge it's a skill; a repeatable prompt is a command. If unclear, ask.
2. **Route Claude vs Codex** — read `references/claude-agents.md`. Claude
   subagent for in-session auto-delegation with a tool/effort/memory surface;
   Codex agent (`references/codex-agents.md`) for a separate `codex exec` process
   or a second non-Claude reviewer.
3. **Choose frontmatter** — read `references/frontmatter.md`. Only `name` +
   `description` are required. Least-privilege `tools`; `model` an alias, not a
   dated id; omit `effort` unless the job needs it; `memory` only when knowledge
   compounds across runs.
4. **Draft the body** — read `references/body-structure.md`. The body is the
   system prompt, so restate every rule/path the agent depends on. Use the
   skeleton (Role → What it does → Process → Success looks like → Output → Edge
   cases → Boundaries), collapsing what doesn't apply. Match repo tooling in
   examples (`uv`, `bun`).
5. **Write the file** — `.claude/agents/<name>.md` (Claude) or
   `.agents/skills/<name>/SKILL.md` (Codex). Frontmatter is real YAML between
   `---` markers at the top — never fenced in a code block.
6. **Validate** (Claude only) — run `scripts/validate_agent.py`; fix every
   `FAIL`, sanity-check `WARN`s.
7. **Test vs baseline** — write 2–3 realistic delegation prompts plus one that
   should NOT route here, and judge whether Claude would delegate on each. The
   agent earns its place only if its output beats doing the same work with no
   agent.
8. **Iterate** — not triggering / over-triggering → tighten the `description`;
   right trigger but shallow work → raise `effort`; wandering → tighten `tools`
   and the body's scope.

## Pre-ship checklist

- [ ] `name` lowercase-hyphen, unique across the whole agents tree
- [ ] `description` is the trigger: third person, real contexts/phrasings, "use
      proactively" where wanted, a Not-for boundary
- [ ] Least-privilege `tools` (or a deliberate inherit / `disallowedTools`)
- [ ] No dependency on the five unavailable tools; no plugin-ignored fields
      (`hooks`, `mcpServers`, `permissionMode`) on a plugin agent
- [ ] `model` an alias; `effort` omitted unless the job needs it; `memory` only
      if knowledge compounds
- [ ] Body restates needed context; explicit `Output`; no persona bloat, no
      "think harder", no forced progress cadence
- [ ] Frontmatter is real YAML between `---` markers, not a fenced block
