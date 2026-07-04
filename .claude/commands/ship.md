---
description: Squash-merges a finished worktree branch into main locally, then removes the worktree and deletes the branch. The final step of the plan-w-team to build to ship lifecycle, after /build stops. Pass a branch or worktree name (no arg infers from the current worktree). /ship asks for explicit confirmation before merging. Trigger phrasings include "ship it", "merge and clean up", "merge the build". Only runs when you invoke it.
argument-hint: [branch | worktree-name]
disable-model-invocation: true
allowed-tools: Bash(git *)
---

# Ship

Squash-merge the finished branch into `main`, then clean up its worktree and branch.
No PR — this is a purely local merge. `/ship` is the step after `/build`, which stops
before merging; `/ship` is that explicit, user-invoked merge + cleanup step.

## Variables

TARGET: $ARGUMENTS — the branch or worktree name to ship. Empty → infer from the current worktree.

## Instructions

- **Resolve the branch and worktree path** from `git worktree list`, cross-checked against
  the plan's `## Tracking` block in `specs/<name>/spec.md`. `EnterWorktree` mangles branch
  names (`chore/x` → `worktree-chore+x`), so trust `git worktree list`, not a guessed name.
- **Merge from the primary checkout on `main`** — never from inside the worktree (you can't
  remove a worktree you are standing in).
- **Squash** so the branch's internal commits collapse into one clean commit on `main`. Keep
  the message trailer-free — no `Co-Authored-By`.
- **Never force or rewrite `main`'s history.** Abort cleanly on any merge conflict — never
  leave a half-merged state silently.
- **Auto mode — no confirmation.** Run the whole flow end to end without asking; the guard is
  that it's `disable-model-invocation: true`, so it only ever runs when the user types `/ship`.

## Workflow

1. **Resolve.** Find the branch and its worktree path (`git worktree list`; cross-check the spec's `## Tracking`). If nothing resolves → STOP and report.
2. **Squash-merge.** From the primary checkout (on `main`): `git merge --squash <branch>`, then `git commit -m "<emoji> <type>(<scope>): <summary>"`. On conflict → ABORT and report.
3. **Cleanup.** `git worktree remove <path>` → `git branch -D <branch>` → `git worktree prune`.
4. **Done.** Report the merge commit SHA and the cleanup.

## Report

- The squash **merge commit SHA** on `main`.
- **Cleanup** done: worktree removed, branch deleted, `git worktree prune` run.
- On abort (merge conflict, or nothing resolved), say which step blocked it and the manual command to finish.
