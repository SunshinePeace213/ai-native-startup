# Command Anti-Patterns & Pre-Ship Checklist

What to cut from a command, how to rewrite a weak `description`, how to fix
over/under-triggering, and a runnable checklist before you ship.

## What to cut from the body

The body is a recurring per-turn cost once the command loads. Cut anything that
wouldn't change the output if deleted.

- **Don't restate what Claude already does.** "Read the file carefully", "think
  about the user's intent", "be thorough" — Claude does this by default. State
  the command-specific rules, not generic competence.
- **No speculative sections.** Omit `## Variables` when there are no variables.
  Don't add a `## Report` that just says "report back to the user" — that's the
  default; only include it when the output has a specific shape.
- **Keep the Workflow tight.** A numbered list of the actual steps, not a prose
  essay. If a step is "do the obvious next thing," drop it.
- **Don't re-teach tools.** "Use the Edit tool to change files" is noise. Name
  the tool only when the choice is load-bearing (e.g. "use `AskUserQuestion` to
  stop and ask").
- **No "ultrathink" / "think harder" padding.** If the work needs depth, set
  `effort: high`/`xhigh` in frontmatter — that's the real lever on 4.8.
- **Don't inline giant reference blocks.** If the body is pushing past ~150–200
  lines of standing material, graduate to a skill directory and move the bulk to
  `references/` (see `command-format.md`).
- **Don't duplicate the plan/spec.** A command like `/build` should point at the
  artifact (`PATH_TO_PLAN`), not restate what a plan contains.

## BAD → GOOD descriptions

The `description` decides discovery and auto-invocation. It's a trigger document,
not a summary.

**1. Vague / first-person → concrete trigger phrasings, third person**

```
BAD:  description: I help you make plans for your projects.
GOOD: description: Creates a concise engineering implementation plan from the
      user's requirements and saves it to the specs directory. Use when the
      user asks to "plan", "spec out", or "write an implementation plan for ..."
```

**2. Restates the name, no triggers → names the real phrasings**

```
BAD:  description: The build command. Builds things.
GOOD: description: Implements an existing plan file in the codebase. Use when
      the user says "build the plan", "implement this spec", or passes a path
      to a plan to execute.
```

**3. Over-broad, will fire on everything → scoped, with a boundary**

```
BAD:  description: Commits and manages all your git work and history and
      branches and remotes and tags and stashes.
GOOD: description: Stages and commits the current changes with a generated
      message. Use when the user asks to "commit", "save my changes", or "make
      a commit". Not for pushing or opening PRs — that's the commit-push-pr
      command.
```

(Boundary phrasing like the last sentence belongs in `when_to_use` when it would
push `description` over budget.)

## Over-trigger / under-trigger fixes

**Under-triggering (command doesn't fire when it should):**
- The `description` is missing the words users actually type — add the real
  phrasings.
- The command relies only on manual `/name` invocation — that's fine if
  intended, but if you want auto-load, the `description` must be discoverable
  (and `disable-model-invocation` must NOT be set).
- The trigger surface is too narrow — broaden `when_to_use` with example
  requests, not by inflating `description` past its useful length.
- Descriptions are being **truncated** because you have many commands — run
  `/doctor`; trim low-priority entries or shorten this one. A longer description
  does not trigger better.

**Over-triggering (command fires when it shouldn't):**
- The `description` is too broad — make it specific, add a `Not for: …` boundary
  routing adjacent work to a sibling.
- The command has side effects and Claude is auto-running it — set
  `disable-model-invocation: true` so only the user can invoke it.
- Two commands compete — sharpen both descriptions so their trigger sets don't
  overlap.

## Pre-ship checklist

Run before finishing. Every box must be checked.

- [ ] **Decision gate applied** — confirmed this is a command (user-invoked by
      name), not a skill (auto-triggering knowledge → meta-skill) or a subagent
      (delegated/isolated work → meta-agent).
- [ ] **Correct output location** — flat `.claude/commands/<name>.md` by
      default, or `.claude/skills/<name>/SKILL.md` only when it needs supporting
      files, bundled scripts, or model auto-trigger (per the decision tree).
- [ ] **No same-name duplicate** — there isn't both a flat command and a skill
      with this name (the skill would silently win).
- [ ] **`description` is a trigger document** — third person, front-loaded, names
      the real phrasings users type.
- [ ] **Caps respected** — `description` ≤ 1,024 chars; `description` +
      `when_to_use` ≤ 1,536 combined.
- [ ] **No angle brackets in `description`** — plain text and ellipses only.
- [ ] **Frontmatter validates against the field surface** — only documented
      fields used; no subagent-only fields (`tools`, `permissionMode`, `memory`,
      etc.); `model` is an alias not a dated id.
- [ ] **`argument-hint` present** when the command takes arguments, mirroring the
      positional order.
- [ ] **Variables ordered dynamic-first, static-second**; `$1`/`$2` used for
      positional args over `$ARGUMENTS` (or `$ARGUMENTS` only for a single
      free-form blob); `## Variables` omitted entirely if there are none.
- [ ] **`disable-model-invocation: true` set for side-effecting commands**
      (`/commit`, `/deploy`, `/send-*`) so Claude doesn't auto-run them.
- [ ] **Injection tools allowed** — any `` !`cmd` `` / ```` ```! ```` block has the
      matching `allowed-tools` (e.g. `Bash(git *)`); `${CLAUDE_SKILL_DIR}` used
      for bundled refs.
- [ ] **Body is lean** — no restating Claude's defaults, no speculative
      sections, Workflow is tight; over ~150–200 lines → split to `references/`.
- [ ] **Tooling matches the repo** in examples — `uv`, `bun`, model aliases.
- [ ] **Validator passes** —
      `cd ${CLAUDE_SKILL_DIR} && uv run --with pyyaml python scripts/validate_command.py <path>`
      exits cleanly.

## Reference Docs
- https://code.claude.com/docs/en/slash-commands
- https://github.com/shanraisshan/claude-code-best-practice/blob/main/best-practice/claude-commands.md
- https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices
