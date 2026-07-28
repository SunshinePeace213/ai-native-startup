# The Subagent Body Is a Contract

The markdown after the frontmatter becomes the subagent's system prompt. Write
the contract, then stop. Every extra line recurs in context on every turn the
agent runs, and on Claude 5 models the common extras don't just cost tokens —
they push the model off behavior it already has.

## The minimum

```markdown
Role — one sentence: what this agent is and the lens it works through.

## Output
Exactly what returns to the caller, in what shape. The caller sees only this;
verbose intermediate work stays in the agent's context.

## Not for
The adjacent work a sibling agent takes.
```

That's a complete agent. `Output` is the return interface the caller depends on,
so spell the shape out concretely — grouped findings, a table, "only failing
tests plus their error output".

Triggering lives in the frontmatter `description`, so **don't** add a "When to
invoke" section.

## Add a section only when its trigger fires

| Section | Add it only when |
| --- | --- |
| `## Process` | Order is load-bearing — irreversible operations, a regulated sequence, a handoff another system depends on. Otherwise state the goal and its constraints and let the agent find the path. |
| `## Edge cases` | The right move on missing, empty, or ambiguous input isn't inferable (no diff to review, target file absent, scope wider than the budget). |
| `## Success looks like` | "Good" isn't already implied by the `Output` contract. |
| `## Inputs` | The delegation message carries something non-obvious. Claude writes that message, so most agents don't need this. |

## What reaches the agent — and what doesn't

A non-fork subagent sees its own prompt, the delegation message, and appended
environment details. It **does** load the full CLAUDE.md hierarchy — including
this repo's `AGENTS.md` — plus git status. Only the built-in Explore and Plan
agents skip those.

So restating repo-wide conventions (`uv` not `pip`, `bun` not `npm`) is
duplication, not safety. Restate only what genuinely doesn't arrive:

- **Path-scoped rules** under `.claude/rules/` — they load only when a matching
  file is touched, which may never happen inside the agent.
- **Conversation history** — files already read, decisions already made, earlier
  tool results.
- **Auto-memory, output style, and skills already invoked** in the main session.

## Anti-patterns → fix

Every one of these is a line that made sense on earlier models and now costs
quality:

- **"Verify your work" / "double-check before responding" / a final verification
  step** → cut. Claude 5 models self-verify and self-correct; the instruction
  compounds into over-verification. If verification must be guaranteed, use a
  `Stop` hook or a separate fresh-context verifier agent.
- **Pre-filtering a finder** ("only report high-severity", "be conservative",
  "don't nitpick") → cut. The model obeys literally and drops real findings.
  Ask for full coverage with a confidence and severity per finding, and filter in
  a later pass.
- **Forced progress cadence** ("summarize every 3 tool calls") → cut; the model
  paces its own updates. A subagent's narration never reaches the user anyway —
  only its final message does.
- **"Think harder" / "be thorough" / reasoning-permission prose** → cut. Depth is
  `effort`; capability is `model`.
- **Assumes shared history** → restate only the four categories above.
- **Bloated persona** ("10k PRs at a FAANG") → one sentence on the relevant lens.
- **All-caps MUST/NEVER without a why** → sentence case plus the reason; keep
  caps only where the model would otherwise do the wrong thing.
- **Lines stating what the model already does** ("write clean code", "handle edge
  cases") → cut. High-signal content is only what pushes the agent off its
  defaults.

Then read `model-tuning.md` for the deltas specific to the model you stamped.

The example agents in the official subagent docs predate this contract — they
carry numbered "When invoked" scripts and review checklists. Follow the contract
here, not those examples.

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

The last two are how a guarantee gets built: the check runs in the harness, so
the body never has to ask for it.

See `../examples/claude-subagent.md` for the contract in a real agent, and
`../examples/codex-subagent.md` for the Codex form of the same job.
