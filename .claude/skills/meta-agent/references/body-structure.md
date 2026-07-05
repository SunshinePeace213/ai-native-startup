# Subagent Body Structure

## The body IS the system prompt

The markdown after the frontmatter becomes the subagent's system prompt. A
non-fork subagent sees **only its own prompt plus the delegation message** —
plus appended environment details (cwd, and unless it's the built-in
Explore/Plan, CLAUDE.md + git status). It does **not** see the main
conversation's history, the files already read, or the skills already invoked.

Consequence: **restate any rule or context the agent depends on** — "ignore
`vendor/`", "the API client lives in `src/api/`", "we use `uv`, never `pip`". The
body recurs in context every turn the agent runs, so keep it lean: state what to
do; don't explain what Claude already knows.

## Recommended skeleton (2–3 header levels max)

```markdown
Role — one sentence: what this agent is and the lens it works through.

## What it does
The job, scoped. "Not for: <adjacent work a sibling should take>."

## Process
Goal + constraints, not a rigid script (unless order is load-bearing —
irreversible ops, regulated procedures). Let the agent find the path.

## Success looks like
Concrete, checkable criteria for a good result.

## Output
Exactly what to return to the caller, in what shape. The caller sees only
this — verbose intermediate work stays in the agent's context.

## Edge cases
What to do when inputs are missing, ambiguous, or the job can't be done.

## Boundaries
What it won't do, and how it operates (autonomous/proactive).
```

Not every agent needs every section — collapse what doesn't apply. Keep the role
line + `Output` at minimum: the return contract is what the caller depends on.
Triggering lives in the frontmatter `description`, so **don't** add a "When to
invoke" section; and skip "Inputs" unless the delegation message carries
something non-obvious. Spell the **return format** out explicitly (grouped
findings, a table, "only failing tests + error output") — 4.8 calibrates length
to perceived complexity, so anchor it.

See `examples/claude-subagent.md` for the full skeleton in a real agent, and
`examples/codex-subagent.md` for the Codex form of the same job.

## Common shapes (frontmatter only)

```yaml
# Read-only researcher — returns a summary, mutates nothing
tools: Read, Grep, Glob

# Memory specialist — accumulates conventions across runs
tools: Read, Grep, Glob, Bash
memory: project        # auto-enables Read/Write/Edit for its memory dir

# Restricted executor — a PreToolUse hook gates Bash where `tools` can't
tools: Bash
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks: [{ type: command, command: "./scripts/validate-readonly-query.sh" }]

# Skill-augmented specialist — preloads team conventions at startup
tools: Read, Edit, Write, Bash, Grep, Glob
skills: [api-conventions, error-handling-patterns]

# Hook-enforced workflow — a Stop gate verifies the job is done
tools: Read, Edit, Bash, Grep, Glob
hooks:
  Stop:
    - hooks: [{ type: command, command: "./scripts/verify-tests-green.sh" }]  # exit 2 = not done
```

## Body anti-patterns → fix

- **Assumes shared history** → restate every needed rule/path; there is none.
- **Bloated persona** ("10k PRs at a FAANG") → one sentence on the relevant lens.
- **"Think harder" / reasoning-permission prose** → thinking is off unless
  adaptive; depth comes from `effort`, not prose. Delete it.
- **Forced progress cadence** ("summarize every 3 tool calls") → 4.8 paces itself;
  cut it.
- **All-caps MUST/NEVER without a why** → sentence case + the reason; keep caps
  only where the model would otherwise do the wrong thing.
- **Lines that state what 4.8 already does** ("write clean code", "handle edge
  cases") → cut. High-signal content is what pushes the agent out of its defaults.
