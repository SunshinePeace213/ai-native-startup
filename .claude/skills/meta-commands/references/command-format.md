# Command Body Format

How to draft the body of a slash command: the house template, the
flat-file-vs-skill-directory decision tree, and dynamic context injection.

## The house template (five sections)

Every team command follows this format. You are **enhancing** it, not replacing
it — keep the five sections.

```md
---
description: <front-loaded trigger document; see frontmatter.md>
argument-hint: [first arg] [second arg]
---

# Purpose

One paragraph: what the command does at a high level, and a pointer to the
sections that drive it (the Instructions/Workflow). Reference variables by name.

## Variables

(Omit this whole section if the command takes no variables.)

DYNAMIC_VAR_ONE: $1
DYNAMIC_VAR_TWO: $2
STATIC_VAR: `some/fixed/path/`

## Instructions

- A bullet list of standing rules and constraints for the command.
- These guide the Workflow but are not themselves the step-by-step.
- State what to do, not what Claude already does by default.

## Workflow

A tight numbered list of the steps to execute, top to bottom.

## Report

What the command prints back to the user when done — the output contract.
```

**Section rules:**
- **`# Purpose`** — one paragraph. What it does + which sections drive it. Not a
  sales pitch.
- **`## Variables`** — **omit entirely if there are no variables.** Order
  **dynamic-first (the `$1`/`$2` args the user passes), static-second (fixed
  paths/constants)**. Prefer `$1`/`$2` over `$ARGUMENTS` for positional args;
  use `$ARGUMENTS` only when the command genuinely takes one free-form blob.
- **`## Instructions`** — standing rules/constraints as bullets. Cut anything
  Claude does by default.
- **`## Workflow`** — the numbered steps. Keep it tight; this is where padding
  creeps in.
- **`## Report`** — the output contract: format + what to include.

**Micro-prompt style (the modernization):** the legacy template told the author
to fill `<bracketed placeholders>`. Prefer **prose micro-prompts** ("One
paragraph describing what the command does") over `<angle-bracket>` fill-ins —
clearer to read, and keeps angle brackets out of anything the validator scans.

## Decision tree — flat file vs skill directory

```
Does the command need supporting files it points at (references/),
bundled scripts it runs, or to auto-trigger via a discoverable description?
│
├─ NO  → flat file:  .claude/commands/<name>.md          ← DEFAULT
│        (matches build.md / plan-w-team.md)
│
└─ YES → skill directory:  .claude/skills/<name>/SKILL.md
         ├─ references/  for material the body loads on demand
         ├─ scripts/     for bundled executables (ref via ${CLAUDE_SKILL_DIR})
         └─ a discoverable `description` (+ optionally disable-model-invocation
            to keep it manual) so Claude can auto-load it
```

**Graduate to a skill directory when ANY holds:**
- The command points at reference docs too big for the body (`references/*.md`).
- The command runs a bundled script (`${CLAUDE_SKILL_DIR}/scripts/foo.py`).
- You want Claude to **auto-trigger** the command from a rich `description`
  (a flat command still triggers, but the directory form is where bundled
  material + auto-trigger live together cleanly).

**Stay flat otherwise.** Most commands — `build`, `commit`, `plan-w-team` — are a
single prompt with args and need nothing more. A directory for a one-file command
is overhead.

Reminder: a same-name skill beats a flat command. Don't keep both.

## Dynamic context injection

Pull live data into the prompt **before Claude sees it** (preprocessing, not
something Claude executes):

- **Inline** `` !`cmd` `` — runs `cmd`, replaces the placeholder with its
  stdout. Only recognized at line start or after whitespace (`KEY=!`cmd`` is
  left literal). Example: `` Current diff: !`git diff HEAD` ``.
- **Multi-line** — a fenced block opened with ```` ```! ````:

  ````md
  ## Environment
  ```!
  uv --version
  bun --version
  git status --short
  ```
  ````
- **`@file`** — `@path/to/file` injects that file's contents into the prompt.
  Use it to pull a spec, a config, or a template into context without Claude
  reading it as a separate step.

**Injection requires the tools be allowed.** A `` !`git ...` `` injection needs
`allowed-tools: Bash(git *)` (or broader) so it runs without a prompt; a
`` !`gh ...` `` needs `Bash(gh *)`. Output is inserted as plain text and is NOT
re-scanned, so a command can't emit a placeholder for a second pass.

## Research: fetch docs directly (the legacy mechanic is outdated)

The **legacy** `meta-commands` template said to "use one Task tool per
documentation item to gather docs in parallel." **That per-doc Task-spawn mechanic
is outdated** — don't do it. The current approach:
- **Fetch docs directly with `WebFetch`** for a known URL (one call per page; it
  returns markdown).
- **Use the `Explore` agent** for parallel, read-only research across many files
  or sources when you need breadth, not a per-doc fan-out of generic Task agents.

Add `WebFetch` (and `Explore` access) to `allowed-tools` if the command does its
own research at run time.

## Tooling in examples

Match the repo: Python via `uv` (`uv run ...`, `uv add ...`), JS/TS via `bun`
(`bun ...`), and model **aliases** (`opus`/`sonnet`/`haiku`) — never a dated id
like `claude-opus-4-8`.

## Reference Docs
- https://code.claude.com/docs/en/slash-commands
- https://github.com/shanraisshan/claude-code-best-practice/blob/main/best-practice/claude-commands.md
- https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices
