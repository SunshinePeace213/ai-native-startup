---
name: meta-commands
description: >-
  The team's canonical standard and guided workflow for authoring Claude Code
  slash commands (the .claude/commands/*.md prompts and their SKILL.md
  equivalents). Use whenever the user wants to "create a command", says "make a
  new slash command" or "build a /command for ...", asks to "turn this prompt
  into a command", wants to "update this command's frontmatter" or args, or
  reports "my command isn't triggering" / "my slash command does nothing".
  Fires even when the build-a-command intent is buried inside a longer request.
  This is THE authority for authoring slash commands — prefer it over ad-hoc
  advice.
when_to_use: >-
  Reach for this when choosing command frontmatter (description, argument-hint,
  allowed-tools, model, disable-model-invocation), writing the body in the house
  template, deciding flat-file vs skill-directory layout, wiring up arguments or
  dynamic context injection, or debugging why a command over- or under-triggers.
  Not for authoring Skills as knowledge/auto-triggering capabilities (use
  meta-skill) or subagents (use meta-agent).
---

# Meta-Commands: Authoring Claude Code Slash Commands

This skill is both the **standard** for what a good slash command looks like and
a **workflow** for producing one. The standard lives in `references/`; this body
is the loop that applies it. Read each reference at the phase that needs it —
don't preload them all.

## Operating principle

A slash command is a **reusable prompt invoked by name** (`/build`, `/commit`) in
the main thread. In current Claude Code, **commands are skills**: a flat file at
`.claude/commands/deploy.md` and a skill at `.claude/skills/deploy/SKILL.md` both
produce `/deploy` and run identically. Flat `.md` files still work and are the
simpler default; the skill directory is the richer form. **When a skill and a
command share a name, the skill wins.** The `description` (plus the rest of the
frontmatter) controls discovery and model-invocation; the body is the prompt
Claude runs. Keep bodies lean — every body line is a recurring per-turn cost once
the command loads.

Apply these principles to the command you build **and to your own conduct here.**
No fake incentives, no "think harder," no forced progress cadence. If quality
needs depth, advise raising `effort` (`high`/`xhigh`) rather than padding the
body with prose — that is the dominant capability lever on Opus 4.8.

## References — load each when its phase arrives

| Read | When |
|---|---|
| `references/frontmatter.md` | Choosing/validating frontmatter fields; char caps; the angle-bracket ban; substitutions; command-name resolution; the commands-are-skills note |
| `references/command-format.md` | Drafting the body in the house template; the flat-file-vs-skill-dir decision tree; dynamic `!`cmd`` + `@file` injection |
| `references/anti-patterns.md` | What to cut; BAD→GOOD descriptions; over/under-trigger fixes; the pre-ship checklist |

Validate any command file or `SKILL.md` (needs PyYAML):

```
cd ${CLAUDE_SKILL_DIR} && uv run --with pyyaml python scripts/validate_command.py <path-to-command-or-SKILL.md>
```

It checks the frontmatter against the documented surface, the char caps, and the
angle-bracket ban, and exits non-zero on any hard failure.

## The workflow

Phases, not a railroad. Skip what doesn't apply; loop back when a later phase
exposes a gap. The goal: a command that fires on the right requests and produces
materially better output than typing the request by hand.

### 1. Capture intent

Pin down before writing:
- **Job** — what does this command do when invoked? (a workflow, a transform, a
  scaffold, a report.)
- **Triggers** — the real phrasings a user would type, including when they don't
  name the command. These become the `description`.
- **Args** — what does it take? Positional? Optional? These become the
  `argument-hint` and the `$1`/`$ARGUMENTS` wiring.
- **Output contract** — what the command produces and how it reports back.

If any is unclear, ask — don't guess. State assumptions explicitly.

### 2. Decision gate — is this even a command?

Confirm the artifact before building. Model this on meta-agent's gate:
- A **command** is a reusable prompt/workflow **invoked by name in the main
  thread** — the user drives it (`/build path`, `/commit`).
- A **skill** is **auto-triggering knowledge or capability** Claude reaches for
  on its own. If the value is "Claude should know/do this when relevant" rather
  than "I will type `/x`", that's a skill → **use meta-skill**.
- A **subagent** is **delegated, context-isolating work** (research that floods
  the thread, a scoped executor, a fan-out worker) → **use meta-agent**.

These overlap (a command can be a skill that auto-triggers; a command can fork to
a subagent). Pick by the **primary** interaction: user-invoked-by-name → command.
If unclear, ask.

### 3. Choose form (decision tree)

Default to a **flat `.claude/commands/<name>.md`** file (matches the team's
`build.md` / `plan-w-team.md`). Graduate to a **`.claude/skills/<name>/SKILL.md`
directory** ONLY when the command needs:
- supporting files it points at (`references/`),
- bundled `scripts/` it runs,
- or model auto-trigger (a discoverable `description` so Claude loads it without
  the user typing `/x`).

See `references/command-format.md` for the full tree and graduation triggers.

### 4. Choose frontmatter

Read `references/frontmatter.md`. The only field that decides triggering/discovery
is `description`. Honor the caps (`description` ≤ 1,024 chars, no `<`/`>`;
`description` + `when_to_use` ≤ 1,536 combined). Add `argument-hint` when the
command takes args; `model`/`effort` only when quality depends on it (model as an
**alias** — `opus`/`sonnet`/`haiku` — never a dated id); `disable-model-invocation:
true` for side-effecting commands so Claude doesn't auto-run them.

### 5. Draft the body in the house template

Read `references/command-format.md`. Use the five-section house format:
`# Purpose` → `## Variables` (omit if none) → `## Instructions` → `## Workflow` →
`## Report`. Order variables **dynamic-first, static-second**, and prefer
`$1`/`$2` over `$ARGUMENTS` for positional args. Match repo tooling in examples
(Python via `uv`, JS/TS via `bun`, model aliases).

### 6. Add dynamic context / args if needed

Inline `` !`cmd` `` injects a shell command's output into the prompt before
Claude sees it; a ```` ```! ```` fenced block does the same for multi-line; `@file`
injects file contents. These require the relevant tools be allowed (e.g.
`allowed-tools: Bash(git *)` for a `` !`git ...` `` injection). See
`references/command-format.md`.

### 7. Validate

Run `scripts/validate_command.py` on the file (invocation above). Fix every hard
failure; treat warnings as prompts to double-check intent.

### 8. Test vs baseline

Use the `evals/` suite (`trigger-eval.json` for should/should-not-trigger
queries, `evals.json` for output-quality prompts + assertions). The test is a
comparison: would Claude fire this command on each trigger phrase, and does
invoking it beat typing the request by hand? The delta is what earns its place.

### 9. Iterate

Fix the highest-leverage gap against `references/anti-patterns.md`:
- **Not triggering / over-triggering** → tighten the `description` (real
  phrasings; `disable-model-invocation` to stop auto-fire).
- **Right trigger, weak output** → tighten the body; raise `effort`; don't add
  "think harder".
- **Wrong scope** → tighten `allowed-tools` / `disallowed-tools` and the
  Workflow.

### 10. Deprecate-or-ship

Run the pre-ship checklist at the bottom of `references/anti-patterns.md`. If this
command replaces an older one, point the old one at the new path or delete it —
don't leave two same-named artifacts (the skill would silently win over the flat
command).

## Gotchas

- **Commands are skills.** A same-name skill beats a flat command; don't ship
  both. Flat `.md` is fully supported and is the simpler default.
- **`description` decides model-invocation and discovery.** It's the trigger
  document, not a human summary. Without a discoverable `description`, the
  command only fires when the user types `/name`.
- **The validator rejects angle brackets** anywhere in `description`. Use plain
  text and ellipses, never `[bracketed]` placeholders with angle brackets.
- **Set `disable-model-invocation: true` for side-effecting commands**
  (`/commit`, `/deploy`, `/send-*`) so Claude doesn't auto-run them because the
  code "looks ready." The user controls the timing.
- **Use `${CLAUDE_SKILL_DIR}`** for bundled file/script refs so paths resolve
  regardless of install location or cwd. Forward slashes only.
- **`$N` is 0-based in the docs** (`$0` = first arg) but the team's house
  template uses `$1`/`$2` as first/second — see `references/frontmatter.md` for
  the substitution table and this discrepancy.
- **`validate_command.py` needs PyYAML** (`--with pyyaml`).

## Reference Docs
- https://code.claude.com/docs/en/slash-commands
- https://github.com/shanraisshan/claude-code-best-practice/blob/main/best-practice/claude-commands.md
- https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices
