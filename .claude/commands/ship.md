---
description: Ships a reviewed build by squash-merging its open PR into main and closing the linked issue, then cleaning up the branch and worktree. The final step of the plan-w-team to build to ship lifecycle, after /build opens the PR and deliberately stops. Pass a PR number, branch, or URL (no arg infers the PR from the current branch); /ship runs pre-merge guards and asks for explicit confirmation before merging. Trigger phrasings include "ship it", "merge the PR and clean up", "merge and close the build". Only runs when you invoke it.
argument-hint: [PR-number | branch | URL]
disable-model-invocation: true
allowed-tools: Bash(gh *), Bash(git worktree *), Bash(git branch *), Bash(git rev-parse *), Bash(git status *), Bash(git fetch *), Bash(git log *), Bash(git rev-list *)
---

# Ship

Resolve `TARGET` to an open PR, run the pre-merge `Guards`, get **explicit confirmation**, then
squash-merge the PR, close the linked issue, and clean up — finishing with the `Report`.
`/ship` is the final step after `/build`, which opens the PR and deliberately stops (its guard:
"never merge — the user merges"); `/ship` is that explicit, user-invoked merge + cleanup step.

## Variables

TARGET: $ARGUMENTS

## Instructions

- **Resolve the PR from `TARGET`** with `gh pr view <TARGET> --json …` — `TARGET` may be a PR
  number, a branch name, or a PR URL. With **no `TARGET`**, infer the PR from the current
  worktree's branch (`gh pr view --json …` resolves the PR for the upstream branch). Read the
  PR's number `#N`, head branch, title, body, and the linked issue. If no open PR resolves →
  STOP and report.
- The **worktree path** for cleanup comes from the plan's `## Tracking` block (the
  `specs/<name>/spec.md` whose `## Tracking` records this worktree/branch). The recorded
  **issue number is the single source of truth** — never re-derive it from the mangled local
  branch (`EnterWorktree` turns `chore/x` into `worktree-chore+x`).
- **Claude is the only actor that calls `gh`.**
- **Merge method is squash.** The squash subject/body MUST be trailer-free — no `Co-Authored-By`
  trailer (repo policy; `gh pr merge` is an API call the guard hook does NOT intercept, so keep
  it clean yourself).
- **Closing the linked issue(s) is part of shipping.** The squash body's / PR body's `Closes #N`
  closes the tracking issue on merge; `/ship` then VERIFIES it closed and explicitly closes any
  `Closes #…` issue that didn't fire. Issues referenced only via `Refs #` / `Part of #` are left
  open by design.
- **Never `--admin` / force-bypass a guard, never push to or commit on `main`.** The only write
  to `main` is the PR merge itself. Abort cleanly on any guard failure — never leave a
  half-merged state silently.
- **Graceful skip:** if `command -v gh` fails, or `gh auth status` / the remote is unavailable,
  or no open PR resolves, STOP and report — change nothing. Do not attempt a local merge.
- This command is side-effecting and `disable-model-invocation: true`: it runs only when the
  user types `/ship`.

## Workflow

1. **Resolve the PR.** `gh pr view <TARGET> --json number,url,title,body,headRefName,state,mergeable,mergeStateStatus,commits` (no `TARGET` → omit it to use the current branch). If no open PR → STOP and report.
2. **Run the pre-merge Guards.** Collect EVERY guard's result first, then decide; if ANY fails, ABORT (touch nothing) and report exactly which guard blocked and how to clear it:
   - **PR open** — `state == "OPEN"` (not already merged/closed).
   - **Mergeable** — `mergeable == "MERGEABLE"` (no conflicts with `main`). If `UNKNOWN`, wait a few seconds and re-check once (GitHub computes it async).
   - **CI not failing** — `gh pr checks <N>`: any **failing** required check → ABORT; **pending** checks → warn and ask the user whether to wait or proceed; no checks configured → pass.
   - **No unpushed commits** — the worktree's `HEAD` equals `@{upstream}` (`git rev-parse HEAD` vs `git rev-parse @{upstream}`; `git status -sb` shows nothing ahead). A squash merges the **remote** PR head, so unpushed local commits would be lost and then destroyed by worktree removal — ABORT and tell the user to push (or discard) first.
   - **Build Status complete** — the PR body's `## Build Status` checklist has every item checked (`- [x]`, no `- [ ]` left), i.e. `/build`'s Codex loop reached **Result**.
3. **Confirm.** Show a one-line summary — PR title, `#N`, commit count, target `main`, and the cleanup that will follow — and require **explicit confirmation** (AskUserQuestion). Do NOT proceed without an affirmative.
4. **Squash-merge** (only after confirmation, with every guard passed):

   ```
   gh pr merge <N> --squash --delete-branch \
     --subject "<emoji> <type>(<scope>): <PR-title description>" \
     --body "$(printf '%s\n\n%s' '<concise 1-3 sentence summary from the plan Objective / PR Summary>' 'Closes #<N>')"
   ```

   - `--squash` collapses the branch's plan + implementation commits into one conventional commit on `main`; the subject mirrors the PR title.
   - The body is a short human summary + `Closes #N`, with **no `Co-Authored-By`** trailer.
   - `--delete-branch` removes the remote `<type>/<N>-<slug>`.
5. **Close the linked issue(s).** The merge's `Closes #N` closes the tracking issue automatically; VERIFY it (`gh issue view <N> --json state,url` → `CLOSED`). If any issue named by a closing keyword in the PR body is still open, close it explicitly: `gh issue close <N> --comment "Shipped in <merge-sha>"`.
6. **Cleanup (after a confirmed merge):** switch out of the worktree FIRST (you cannot remove a worktree you are inside) — `ExitWorktree` (action: remove) if inside it, else `git worktree remove <recorded worktree path>` → delete the mangled local branch `git branch -D worktree-<slug>` → `git fetch --prune` (drops the deleted remote ref). If the worktree was already removed, skip that step.
7. Never exceed this scope — no force-push, no `--admin`, no edits to `main` beyond the merge.

## Report

- The merged PR URL, the squash **merge commit SHA**, and confirmation every linked issue (`Closes #N`) is **CLOSED** — verified after merge, and force-closed if the keyword didn't fire.
- The **Guard results** (each guard: pass/fail) — and if `/ship` aborted, exactly which guard blocked it and how to clear it.
- **Cleanup** done: remote branch deleted, worktree removed, local `worktree-<slug>` deleted, `git fetch --prune` run, shipped summary comment posted.
- On graceful skip (no `gh` / no open PR / a failed guard), say so and print the exact manual `gh pr merge <N> --squash --delete-branch` command the user can run after clearing the blocker.

## Notes

- `/ship` is the inverse of `/build`'s "leave the PR OPEN" guard: `/build` opens the PR, `/ship` merges it. Mirrors the plan's **Workstream C**.
- The guard set is open · mergeable · CI-not-failing · no-unpushed-commits · Build-Status-complete, plus explicit confirmation. PR review approval is intentionally NOT a guard (a solo repo can't self-approve, which would permanently block `/ship`).
