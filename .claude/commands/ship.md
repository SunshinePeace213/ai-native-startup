---
description: Squash-merges a finished build's PR into main, then removes the worktree and deletes the branch. The final step of the plan-w-team → build → ship lifecycle, after /build marks the PR ready. Pass a branch or worktree name (no arg infers from the current worktree). /ship verifies the PR is ready, its checks pass, and its head matches the Codex-approved SHA before merging. Trigger phrasings include "ship it", "merge and clean up", "merge the build". Only runs when you invoke it.
argument-hint: [branch | worktree-name]
disable-model-invocation: true
allowed-tools: Bash(git *), Bash(gh *)
---

# Ship

Squash-merge the finished build's PR into `main` through `gh`, then clean up its
worktree and branch. `/ship` is the step after `/build`, which opens and readies the
PR but stops before merging; `/ship` is that explicit, user-invoked merge + cleanup step.

## Variables

TARGET: $ARGUMENTS — the branch or worktree name to ship. Empty → infer from the current worktree.

## Instructions

- **Resolve two distinct branch names.** The `local_branch` is the mangled worktree branch
  (`EnterWorktree` turns `chore/17-x` into `worktree-chore+17-x`) — take it from
  `git worktree list`. The `remote_branch` is the convention branch `<type>/<N>-<slug>` from
  the spec's `## Tracking` — it is what the PR heads. Use `remote_branch` for
  `gh pr list --head` and the remote deletion; use `local_branch` only for local cleanup.
  No open PR for `remote_branch` → STOP.
- **Merge only a green, ready PR at the approved head.** The PR must be ready (not draft),
  its required checks must pass (`gh pr checks` — treat "no checks" as pass), and its head
  SHA must equal the **approved head recorded in the PR body's stage table** (the Evidence of
  the final Codex R / Ready rows — the round comment's `REVIEWED_HEAD_SHA` is that commit's
  parent, not the merge guard). Any mismatch → ABORT.
- **Squash-merge through GitHub**: `gh pr merge <PR> --squash --match-head-commit <approved-sha>`.
  The `--match-head-commit` guard refuses the merge if the head moved. Pass a trailer-free
  squash subject — no `Co-Authored-By`.
- **Never force or rewrite `main`'s history.** On a merge conflict or any state mismatch,
  ABORT cleanly with the exact manual command — never leave a half-merged state silently.
- **Clean up only after GitHub confirms MERGED**, and from the primary checkout on `main` —
  you can't remove a worktree you are standing in.
- **Auto mode — no confirmation.** Run the whole flow end to end without asking; the guard is
  that it's `disable-model-invocation: true`, so it only ever runs when the user types `/ship`.

## Workflow

1. **Resolve.** Find the worktree path and `local_branch` (`git worktree list`), the
   `remote_branch` from the spec's `## Tracking`, and the PR
   (`gh pr list --head <remote_branch>`). Nothing resolves, or no open PR → STOP and report.
2. **Verify the PR.** It is ready (not draft), `gh pr checks <PR>` passes (no checks = pass),
   and its head equals the approved head recorded in the PR body's stage table (final
   Codex R / Ready row Evidence). Any mismatch → ABORT with the reason.
3. **Squash-merge.** `gh pr merge <PR> --squash --match-head-commit <approved-sha> --subject "<emoji> <type>(<scope>): <summary>"`. On conflict or a moved head → ABORT and report the manual command.
4. **Confirm.** Poll `gh pr view <PR> --json state,mergedAt` until GitHub reports `MERGED`. Only then proceed.
5. **Cleanup.** From the primary checkout on `main`: `git worktree remove <path>` → `git branch -D <local-branch>` → `git push origin --delete <type>/<N>-<slug>` → `git worktree prune`.
6. **Done.** Report the merge and the cleanup.

## Report

- The **PR #M** merged and its squash **merge commit SHA** on `main`.
- **Cleanup** done: worktree removed, local + remote branch deleted, `git worktree prune` run.
- On abort (not ready, failing checks, head-SHA mismatch, merge conflict, or nothing resolved),
  say which check blocked it and the exact manual command to finish.
