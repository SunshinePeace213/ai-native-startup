# Command Body Format

The house template for slash command bodies, the flat-file-vs-directory
decision tree, and dynamic context injection.

## The house template (five sections)

Every team command follows this format:

```md
---
description: front-loaded trigger document; see frontmatter.md
argument-hint: [first arg] [second arg]
---

# Purpose

One paragraph: what the command does at a high level, referencing its
variables by name. Not a sales pitch.

## Variables

DYNAMIC_VAR_ONE: $1
DYNAMIC_VAR_TWO: $2
STATIC_VAR: `some/fixed/path/`

## Instructions

- Standing rules and constraints, as bullets.
- Command-specific rules only — cut anything Claude does by default.

## Workflow

A tight numbered list of the steps to execute, top to bottom.

## Report

The output contract: what the command prints back when done.
```

Section rules:

- **`## Variables`** — omit the whole section if there are none. Order
  dynamic-first (the `$1`/`$2` args), static-second (fixed paths/constants).
  Prefer `$1`/`$2` for positional args; use `$ARGUMENTS` only for a single
  free-form blob.
- **`## Report`** — include only when the output has a specific shape;
  "report back to the user" is the default and doesn't need saying.
- Write section prompts as prose micro-prompts, not bracketed placeholders —
  angle brackets in the wrong place fail validation.

## Flat file vs skill directory

```
Does it need supporting files (references/), bundled scripts, or
auto-triggering via a discoverable description?
│
├─ NO  → flat file: .claude/commands/<name>.md          ← DEFAULT
│
└─ YES → skill directory: .claude/skills/<name>/SKILL.md
         with references/, scripts/, and a discoverable description
         (+ disable-model-invocation to keep a side-effecting one manual)
```

Most commands — `build`, `commit`, `plan-w-team` — are a single prompt with
args; a directory for a one-file command is overhead. And a same-name skill
silently beats a flat command, so never keep both.

## Dynamic context injection

Pulls live data into the prompt **before Claude sees it**:

- **Inline** `` !`cmd` `` — runs `cmd`, replaces the placeholder with its
  stdout. Recognized only at line start or after whitespace.
  Example: `` Current diff: !`git diff HEAD` ``
- **Multi-line** — a fenced block whose info string is a single `!`:

  ````md
  ```!
  git status --short
  git log --oneline -5
  ```
  ````
- **`@file`** — injects that file's contents into the prompt.

Injection requires the tool be allowed: a `` !`git ...` `` needs
`allowed-tools: Bash(git *)`. Output is inserted as plain text and not
re-scanned for further placeholders.

## Runtime research

When a command fetches docs at run time, use `WebFetch` for known URLs and
the `Explore` agent for breadth across many files or sources, and add the
tools to `allowed-tools`.
