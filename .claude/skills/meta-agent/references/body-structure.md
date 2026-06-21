# Subagent Body Structure

Live docs:
- https://code.claude.com/docs/en/sub-agents#write-subagent-files
- https://code.claude.com/docs/en/sub-agents#example-subagents
- https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-4-8

## The body IS the system prompt

The markdown after the frontmatter becomes the subagent's system prompt. The subagent sees **only its own prompt plus the delegation message Claude writes when handing off** — plus appended environment details (cwd, and unless it's the built-in Explore/Plan, CLAUDE.md + git status). It does **not** see the main conversation's history, the files Claude already read, or the skills already invoked.

Consequence: **restate any rule or context the agent depends on.** "Ignore the `vendor/` directory," "the API client lives in `src/api/`," "we use `uv`, never `pip`" — if the agent needs it, it must be in the body (or the delegation prompt). Don't assume shared history; there is none.

The body recurs in context every turn the agent runs, so keep it lean. State what to do; don't explain what Claude already knows.

## Recommended skeleton (2–3 header levels max)

```markdown
Role line — one sentence: what this agent is and the lens it works through.

## When to invoke
- The situations this agent handles.
- Not for: <the adjacent work a sibling agent should take>.

## Inputs
What the agent should expect in the delegation message / find in the repo.

## Process
Goal + constraints, not a rigid script (unless order is load-bearing —
irreversible ops, regulated procedures). Let the agent find the path.

## Success looks like
Concrete, checkable criteria for a good result.

## Output
Exactly what to return to the caller, and in what format. The caller only
sees this — verbose intermediate work stays in the agent's context.

## Edge cases
What to do when inputs are missing, ambiguous, or the job can't be done.
```

Not every agent needs every section. A read-only researcher may collapse `Inputs`/`Process` into one. Keep the role line + `When to invoke` + `Output` at minimum — the trigger and the return contract are the two things a caller depends on.

Two body conventions worth noting (both in the official examples):
- A numbered **"When invoked:"** sequence is fine for a genuinely ordered startup routine (e.g. "1. Run git diff  2. Focus on modified files  3. Begin review"). Use it where order is load-bearing, not as decoration.
- Spell out the **return format** explicitly (priority-grouped findings, a table, "only the failing tests + error output"). 4.8 calibrates length to perceived complexity — anchor it.

## Five common shapes

### 1. Read-only researcher
Investigates without mutating anything; returns a summary so verbose output stays out of the main context.
```yaml
---
name: codebase-researcher
description: Read-only codebase research. Use proactively to locate code,
  trace data flow, or map a module before changes. Not for editing.
tools: Read, Grep, Glob
effort: high
---
```

### 2. Memory specialist
Accumulates knowledge across runs (recurring patterns, conventions).
```yaml
---
name: code-reviewer
description: Reviews diffs for quality and recurring issues. Use proactively
  after code changes.
tools: Read, Grep, Glob, Bash
memory: project      # auto-enables Read/Write/Edit for its memory dir
effort: high
---
# body instructs: consult memory before reviewing, update it after.
```

### 3. Restricted executor with a PreToolUse hook gating Bash
`tools` alone can't say "Bash but only read-only SQL." A hook can.
```yaml
---
name: db-reader
description: Runs read-only database queries. Use when analyzing data or
  generating reports. Not for migrations or writes.
tools: Bash
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "./scripts/validate-readonly-query.sh"
effort: medium
---
```

### 4. Skill-augmented specialist
Preloads team conventions so the agent starts already knowing them.
```yaml
---
name: api-developer
description: Implements API endpoints following team conventions. Use when
  adding or changing an endpoint.
tools: Read, Edit, Write, Bash, Grep, Glob
skills:
  - api-conventions
  - error-handling-patterns
effort: xhigh
---
```

### 5. Hook-enforced workflow with a Stop-gate
A `Stop` hook (converted to `SubagentStop`) verifies the job is actually done before the agent returns.
```yaml
---
name: test-fixer
description: Fixes failing tests until the suite is green. Use proactively
  when tests fail.
tools: Read, Edit, Bash, Grep, Glob
hooks:
  Stop:
    - hooks:
        - type: command
          command: "./scripts/verify-tests-green.sh"   # exit 2 = not done
effort: xhigh
---
```

## One fuller worked example

A read-only code reviewer, written to the skeleton. Real frontmatter (good `name`, trigger-rich third-person `description` with a NOT-boundary, least-privilege `tools`, deliberate `effort`), real body.

```markdown
---
name: diff-reviewer
description: Read-only reviewer of the current git diff. Use proactively
  after writing or modifying code, or when the user asks for a review,
  to check correctness, security, and clarity. Reports findings only —
  it does not edit. Not for running or fixing tests (use test-runner).
tools: Read, Grep, Glob, Bash
model: inherit
effort: high
color: blue
---

You review uncommitted changes for correctness and security. You report;
you never edit.

## When to invoke
- Right after code is written or modified.
- When the user asks for a review of recent changes.
- Not for: running or fixing tests (test-runner), or writing new code.

## Inputs
The working tree with uncommitted changes. Run `git diff` (and
`git diff --staged`) yourself to see them; focus only on changed lines
and their immediate blast radius.

## Process
Read the diff, then the surrounding code needed to judge each change.
Check, in priority order:
- Correctness: logic errors, off-by-one, wrong null/empty handling,
  broken error paths.
- Security: injection, missing input validation, secrets or keys in code.
- Clarity: misleading names, dead code your changes would orphan.
Investigate enough to be confident; do not speculate about code you
haven't read.

## Success looks like
Every real issue in the diff is reported with a file:line and a concrete
fix. No style nitpicks unless they cause a bug.

## Output
Return findings grouped by severity, each as `path:line — issue — fix`:
- Critical (must fix before merge)
- Warning (should fix)
- Nit (optional)
If the diff is clean, say so in one line. Do not restate the whole diff.

## Edge cases
- No diff: report "no uncommitted changes to review" and stop.
- Diff too large to review well: review the highest-risk files, name
  what you skipped, and recommend splitting the change.
```

Note what makes it valid: `name` is lowercase-hyphen; the `description` is third person, names real trigger contexts, says "use proactively", and routes adjacent work elsewhere with a NOT-boundary; `tools` is the least set that lets it read the diff (`Bash` for `git diff`, no Write/Edit because it's read-only); `effort: high` is a deliberate reasoning-sensitive default; the body restates the read-only constraint and the cwd-relative facts it can't assume from a shared history it doesn't have.
