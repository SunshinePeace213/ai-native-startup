---
name: meta-agent
description: >-
  The team's canonical standard and guided workflow for authoring subagents —
  Claude Code subagents and Codex agents. Use whenever the user wants to "create
  a new subagent", says "make an agent that ..." or "build a subagent for ...",
  asks to update or fix an agent's frontmatter, tools, or model, reports "my
  agent isn't triggering" / "isn't being delegated to", wants to turn a repeated
  delegation into a reusable subagent, or wants an older agent modernized for the
  current model generation. This is THE authority for subagent authoring — prefer
  it over ad-hoc advice.
when_to_use: >-
  Reach for this when choosing subagent frontmatter, writing the description that
  controls delegation, structuring the agent body, tuning a body to the model it
  runs on, deciding Claude subagent vs Codex agent, or debugging why an agent
  over- or under-triggers. Not for authoring Skills or slash commands — use
  meta-skills.
---

# Meta-Agent: Authoring Subagents

The **standard** for what a good subagent looks like and the **workflow** for
producing one. The standard lives in `references/`; this body is the loop that
applies it. Read each reference at the phase that needs it — don't preload them.

## Operating principle

A subagent does one scoped, context-isolating job and hands a result back. Its
power comes from a tight trigger (`description`), least-privilege tools, and a
body that says as little as possible.

Writing that body is **subtraction**. Claude 5 models already verify their work,
correct their own mistakes, pace their updates, and calibrate length to the task.
Telling them to do those things compounds with the behavior and degrades the
result. Write the contract, stamp the model, then cut every line that model
already honors. This applies to the agent you build **and to your own conduct
here.**

Three rules carry the rest:

- **Contract in, contract out.** `description` is the whole input interface,
  `Output` the whole return interface. Those two earn their place unconditionally;
  every other line has to.
- **Capability and depth are frontmatter.** `model` buys knowing, `effort` buys
  trying. Neither comes from prose — no "think harder", no "be thorough".
- **Guarantees are harness, not prose.** If the agent *must* do something, reach
  for a hook, a permission rule, or a separate verifier agent. An instruction is
  a preference; only the harness is a guarantee.

## References — load each when its phase arrives

| Read | When |
| --- | --- |
| `references/routing.md` | Deciding whether this is an agent at all — subagent vs skill, command, rule, hook, or Codex; how delegation works; where the file lives |
| `references/frontmatter.md` | Choosing and validating Claude frontmatter; tool resolution; the load-bearing gotchas; writing the `description` |
| `references/body-contract.md` | Writing the body: the minimal contract, what to add only on trigger, the universal anti-patterns |
| `references/model-tuning.md` | After the model is stamped — the lines to add and delete for that specific model |
| `references/codex-agents.md` | Building a Codex agent (`.codex/agents/*.toml`) instead |
| `examples/claude-subagent.md`, `examples/codex-subagent.md` | A full worked agent in each ecosystem |

Validate a **Claude** agent file (frontmatter and body; not for Codex):

```bash
uv run --with pyyaml python ${CLAUDE_SKILL_DIR}/scripts/validate_agent.py <path-to-agent.md>
```

It prints `WARN:`/`FAIL:` lines and a final `PASS`, exiting non-zero on failure.

## The workflow

Phases, not a railroad. Skip what doesn't apply; loop back when a later phase
exposes a gap.

1. **Capture intent** — the one **job** and its lens, the real **triggers** (the
   contexts and phrasings that should route here), and the **return contract**.
   If unclear, ask.
2. **Route** — read `references/routing.md`. Confirm a subagent is the right
   artifact before writing one; a hard guarantee and main-thread knowledge are
   both something else.
3. **Stamp the frontmatter** — read `references/frontmatter.md`. Only `name` +
   `description` are required. Take `model` and `effort` from
   [model-selection.md](../../rules/model-selection.md); keep `tools` least-privilege;
   add `memory` only when knowledge compounds across runs.
4. **Write the contract** — read `references/body-contract.md`. Role line,
   `Output`, `Not for`. Add a further section only when its trigger fires.
5. **Subtract** — read `references/model-tuning.md` for the model you stamped.
   Delete what that model already does; add only its named deltas.
6. **Write the file** — `.claude/agents/<name>.md` (Claude) or
   `.codex/agents/<name>.toml` (Codex). Claude frontmatter is real YAML between
   `---` markers at the top — never fenced in a code block.
7. **Validate** (Claude only) — run `scripts/validate_agent.py`; fix every
   `FAIL`, sanity-check the `WARN`s.
8. **Test and iterate** — write 2–3 realistic delegation prompts plus one that
   should NOT route here, and check that Claude routes each correctly. Not
   triggering or over-triggering → tighten the `description`. Wandering → tighten
   `tools` and the body's scope. Shallow or incomplete work → raise `effort`;
   confidently wrong work → raise `model`.

## Modernizing an existing agent

Agents written for earlier models are usually too prescriptive, and the excess
now costs quality rather than just tokens. Audit by deletion: read the body
against `references/body-contract.md` and `references/model-tuning.md`, cut every
line the stamped model already honors, then re-validate. Expect the file to get
substantially shorter; if it doesn't, the pass wasn't done.

## Pre-ship checklist

- [ ] `name` lowercase-hyphen, unique across the whole agents tree
- [ ] `description` is the trigger: third person, real contexts and phrasings,
      "use proactively" where wanted, a Not-for boundary
- [ ] Body carries the role line, `Output`, and `Not for` — and every remaining
      section names a trigger from `body-contract.md`
- [ ] Ran the subtraction pass for the stamped model
- [ ] Least-privilege `tools` (or a deliberate inherit / `disallowedTools`); no
      dependency on the tools unavailable to subagents
- [ ] `model` an alias, `effort` stamped, both from `model-selection.md`
- [ ] No plugin-ignored fields (`hooks`, `mcpServers`, `permissionMode`) on a
      plugin agent
- [ ] Frontmatter is real YAML between `---` markers, not a fenced block
