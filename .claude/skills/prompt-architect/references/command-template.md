# Command Template (single-file legacy format)

Commands and skills share the same frontmatter. `.claude/commands/deploy.md` (single file) and `.claude/skills/deploy/SKILL.md` (directory) both create `/deploy`. Use the **single-file format only when**:

- Artifact is genuinely trivial (no scripts, no references, no assets)
- Maintaining backward compatibility with existing `.claude/commands/` files
- Minimum overhead, body is short

Otherwise use `skill-template.md` — directory format supports bundled resources.

## Storage

- `.claude/commands/<name>.md` — project scope
- `~/.claude/commands/<name>.md` — user-level

## Frontmatter

Same fields as skills; see `skill-template.md` for full reference. Most-used:

```yaml
---
description: What this command does and when to use it
disable-model-invocation: true        # user-triggered only (typical for /commit, /deploy)
allowed-tools: Bash(git *)            # pre-approve specific tool patterns
argument-hint: "[scope] [message]"    # autocomplete hint
arguments: [scope, message]           # named positional args
---
```

`disable-model-invocation: true` is the typical default — you want `/deploy` firing only when the user invokes it explicitly.

## Body structure (4.8-tuned)

```markdown
---
[frontmatter]
---

# /<command-name>

## Purpose
[One paragraph: what it does and the outcome.]

## Role
[One focused sentence: the lens. Skip if pure transformation.]

## Scope
**In:** [What it operates on]
**Out:** [What it explicitly doesn't touch]

## Inputs
[What the command receives — staged changes, current file, $ARGUMENTS, etc.]

## Workflow
1. [Step. Include the *why* if non-obvious.]
2. [Step.]

## Output specification
**Format:** [Markdown, code block, plain text, JSON, table]
**Length:** [Exact word/line/section count]
**Structure:** [Sections, in order]

## Success criteria
- [Specific quality 1]
- [Specific quality 2]

## Error handling
- **[Condition]:** [How to respond]
```

## What's removed vs older templates

| Removed | Why |
|---|---|
| Inflated persona ("10,000+ PRs") | 4.8 reads literally; use focused Role sentence |
| Free-floating Stakes | Fold consequence into *why* clauses on specific constraints |
| `$100 tip` incentive | 4.8 doesn't respond to fake money; use Success criteria |
| `I bet you can't` framing | Use explicit constraints with reasoning |
| `Take a deep breath` in Workflow | Adaptive thinking handles depth |
| Self-scoring 0-1 Quality rubric | Wasteful at runtime; rubric is for human review |

See `anti-patterns.md` for the full list.

## Worked example: `/commit`

```markdown
---
description: Generate a Conventional Commits message from staged git changes
disable-model-invocation: true
allowed-tools: Bash(git diff *), Bash(git log *), Bash(git status *)
---

# /commit

## Purpose
Write a single Conventional Commits message for currently staged changes, ready to paste into `git commit -m`.

## Role
You are the developer who wrote this change — close enough to explain *why*, careful enough to keep the subject scannable in `git log`.

## Scope
**In:** Staged changes (`git diff --cached`), recent commit history for tone
**Out:** Unstaged changes, branch creation, the actual `git commit` invocation

## Inputs
- Staged diff from `git diff --cached`
- Last 5-10 commit messages for tone matching

## Workflow
1. `git diff --cached --stat` — see the shape of the change
2. `git diff --cached` — read the diff
3. `git log --oneline -10` — match existing tone
4. Draft the message
5. Output as a code block ready to paste

## Output specification
**Format:** Markdown code block, plain text inside
**Length:** Subject ≤ 72 chars; body wrapped at 72; total under 25 lines
**Structure:** Subject, blank line, body explaining *why* (not *what*)

## Success criteria
- Subject follows Conventional Commits: `type(scope): description`
- Subject is action-oriented and specific (not "various improvements")
- Body explains motivation, not the diff
- No trailing period on subject; no emoji unless project commits use them

## Error handling
- **No staged changes:** Tell user to stage; suggest `git add -p`
- **Diff > 500 lines:** Ask whether to summarize at file level or split the commit
- **Unfamiliar history pattern:** Use plain Conventional Commits with neutral tone
```

## Upgrading command → skill

1. Create skill dir: `mkdir ~/.claude/skills/commit/`
2. Move: `mv ~/.claude/commands/commit.md ~/.claude/skills/commit/SKILL.md`
3. Add `references/`, `scripts/`, or `assets/` as needed
4. Reference bundled scripts via `${CLAUDE_SKILL_DIR}/...`

Skill takes precedence over command of same name → non-breaking upgrade.

## Adding hooks

Commands support the same `hooks` field as skills:

```yaml
---
description: Deploy to production
disable-model-invocation: true
hooks:
  Stop:
    - hooks:
        - type: command
          command: "curl -X POST https://hooks.slack.com/... -d '{\"text\":\"Deploy finished\"}'"
---
```

See `hooks.md` for the full hooks reference.
