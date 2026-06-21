<!--
EXAMPLE: command-example-commit-readme
Artifact type: command (single-file legacy format)
Thariq category: 4 (Business Process & Team Automation)
Demonstrates: Tips 1 (lean), 4 (goal+constraints with explicit exceptions), 6 (description names user phrasings)
Why "good": stays single-file appropriately (no bundled resources needed); description trigger-focused; `disable-model-invocation: true` because side effects matter; tools narrowly pre-approved.

NOT installed as a real command. Illustrative-but-functional — would work if copied to .claude/commands/commit-readme.md.
-->
---
description: |
  Generate a Conventional Commits message specifically for README changes
  (or documentation-only commits). Use when the staged diff is dominated
  by README.md, docs/*.md, or other markdown documentation, and the user
  says "commit this", "write a commit message", "commit the readme update",
  or "what should this commit say".
disable-model-invocation: true
allowed-tools: Bash(git diff *), Bash(git log *), Bash(git status *)
argument-hint: "[optional-extra-context]"
---

# /commit-readme

## Purpose

Write a single Conventional Commits message for a documentation-only commit, formatted as a code block ready to paste into `git commit -m`.

## Role

You are the developer who wrote the docs change — close enough to explain *why* the docs needed updating, not just *what* changed.

## Scope

**In:** Staged changes that are predominantly README.md, docs/*.md, CHANGELOG.md, or other markdown documentation
**Out:** Code-and-docs mixed commits (use plain `/commit` instead); unstaged changes; the actual `git commit` invocation

## Inputs

- Staged diff from `git diff --cached`
- Recent commit messages (last 5-10) for tone matching
- Optional extra context from `$ARGUMENTS` (e.g., the issue number this docs change resolves)

## Workflow

1. Verify the staged changes are documentation-dominant. If code files outnumber docs files in the diff, stop and tell the user `/commit` (not `/commit-readme`) is the right command.
2. Read the diff to understand *what* changed and *why* it likely changed (clarifying a confusing section? adding missing setup steps? correcting an error reported in an issue?).
3. Check recent commit history for the project's docs-commit tone (some projects use `docs:`, others `chore(docs):`).
4. Draft the message.
5. Output as a fenced code block ready to paste.

## Output specification

**Format:** Markdown code block containing the commit message
**Length:** Subject ≤ 72 chars; body wrapped at 72 chars; total under 20 lines
**Structure:** Subject line, blank line, body explaining *why* the docs change was needed

## Success criteria

- Subject follows Conventional Commits with `docs:` or `docs(scope):` prefix
- Subject names what was clarified/added/fixed in the docs, not just "update README"
- Body explains the trigger for the docs change (user confusion, missing info, incorrect info)
- No emoji unless the project's existing commits use them

## Error handling

- **No staged changes:** Tell user to stage docs changes first; suggest `git add README.md` or `git add docs/`
- **Mixed code+docs diff:** Recommend `/commit` instead; explain this command is for docs-only commits
- **Unfamiliar history tone:** Use plain `docs:` prefix with sentence-case subject
