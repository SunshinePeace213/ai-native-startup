---
description: Squash-merges a finished build's PR into main, then removes the worktree and deletes its branches. Final pipeline step after /harness-layer:harness-review flips the PR ready — verifies the PR is ready, green, and at the approved head before merging. Pass a branch or worktree name (no arg infers from the current worktree).
argument-hint: [branch | worktree-name]
disable-model-invocation: true
allowed-tools: Read, Bash(git *), Bash(gh *)
model: sonnet
effort: medium
---

# Harness Ship

Squash-merge the finished build's PR into `main` through `gh`, then clean up its
worktree and branches. Run the whole flow end to end without asking or confirming.

## Variables

TARGET: $ARGUMENTS — the branch or worktree name to ship. Empty → infer from the current worktree.

## Instructions

- Two distinct branch names, never interchangeable: `local_branch` is the worktree's
  local `worktree-<slug>` (from `git worktree list`) — used only for local cleanup.
  `remote_branch` is the convention branch `<type>/<N>-<slug>` from the spec's
  `## Tracking` — it heads the PR; use it for `gh pr list --head` and the remote deletion.
- Never force or rewrite `main`'s history. On a merge conflict or any state mismatch,
  ABORT cleanly — never leave a half-merged state silently.
- The squash commit carries no trailers — no `Co-Authored-By`, no `Signed-off-by`.

## Workflow

1. **Resolve.** TARGET (or the current worktree) → `<slug>` by stripping any `worktree-`
   prefix. Read `specs/<slug>/spec.md` `## Tracking` for `remote_branch` and issue `#N`;
   take the worktree path and `local_branch` from `git worktree list`, and the PR from
   `gh pr list --head <remote_branch>`. Nothing resolves, or no open PR → STOP and report.
2. **Verify.** The PR is ready (not draft), `gh pr checks <PR>` passes (no checks = pass),
   and its head SHA equals the approved head recorded in the PR body's stage table — the
   approval round's report commit (Ready row Evidence; a round's `REVIEWED_HEAD_SHA` is
   that round's input, not the merge guard). Any mismatch → ABORT with the reason.
3. **Squash-merge.** `gh pr merge <PR> --squash --match-head-commit <approved-sha>
   --subject "<emoji> <type>(<scope>): <summary>" --body "Refs #N"` — subject from the
   PR title, normalized to the commit format. Merge refused (head moved) or conflicted
   → ABORT.
4. **Confirm.** `gh pr view <PR> --json state,mergedAt` until it reports `MERGED` — at
   most 5 attempts; still unmerged → report the current state and stop.
5. **Cleanup.** Only after MERGED, from the primary checkout on `main` (a worktree can't
   be removed from inside itself): `git worktree remove <path>` →
   `git branch -D <local_branch>` → `git push origin --delete <remote_branch>` →
   `git worktree prune`.

## Report

End the run with exactly one of:

```text
✅ Shipped
PR: #<M> — squash-merged, <merge sha> on main
Cleanup: worktree removed, local + remote branch deleted, pruned
```

```text
⚠️ Aborted — <not ready | failing checks | head mismatch | merge conflict | nothing resolved>
PR: #<M> — <current state> (or: nothing resolved for <TARGET>)
Blocked by: <one line — which check failed and how>
Manual: <exact command(s) to finish by hand>
```
