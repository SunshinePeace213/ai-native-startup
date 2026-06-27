---
description: Ships a reviewed build by merging the open PR that /build left open into main with a squash, letting the PR's "Closes #N" close the tracking issue, then deleting the branch and removing the worktree. The final step of the plan-w-team to build to ship lifecycle. Use once a build's PR has been reviewed and you want to merge it and finish up — trigger phrasings include "ship it", "merge the PR and clean up", "merge and close the build". Only runs when you invoke it.
argument-hint: [feature-name | path-to-plan]
disable-model-invocation: true
allowed-tools: Bash(gh *), Bash(git worktree *), Bash(git branch *), Bash(git rev-parse *), Bash(git status *)
---

# Ship

Resolve `TARGET` to the tracking PR via the plan's `## Tracking` block, run the pre-merge
`Gates`, and — only if every gate passes — squash-merge the PR, then clean up and `Report`.
`/ship` is the final step after `/build`, which deliberately leaves the PR open; invoking
`/ship` IS your go-ahead, so it merges without a second confirmation.

## Variables

TARGET: $ARGUMENTS

## Instructions

- Resolve `TARGET` exactly as `/build` does:
  1. If `specs/<TARGET>/plan.md` exists → PLAN = `specs/<TARGET>/plan.md`.
  2. Else if `<TARGET>` is an existing file → PLAN = that file.
  3. Else STOP and report which paths were searched.
  If no `TARGET` is given, infer it from the current worktree's plan (the `specs/<name>/plan.md` whose `## Tracking` records this worktree) or from the open PR for the current branch.
- Read PLAN's `## Tracking` block: the **issue number `#N` is the single source of truth** — never re-derive it from the mangled local branch (`EnterWorktree` turns `chore/x` into `worktree-chore+x`). Take the convention branch `<type>/<N>-<slug>` and the worktree path from `## Tracking` too.
- **Claude is the only actor that calls `gh`.**
- **Merge method is squash.** The squash commit subject/body MUST be trailer-free — no `Co-Authored-By` trailer (repo policy; `gh pr merge` is an API call the guard hook does NOT intercept, so keep it clean yourself).
- **Closing the linked issue(s) is part of shipping.** The PR body's `Closes #N` closes the tracking issue on merge; `/ship` then VERIFIES it closed and explicitly closes any `Closes #…` issue that didn't fire. Issues referenced only via `Refs #` / `Part of #` are left open by design.
- **Never push to or commit on `main`.** The only write to `main` is the PR merge itself.
- **Graceful skip:** if `command -v gh` fails, or `gh auth status` / the remote is unavailable, STOP and report — `/ship` cannot merge without `gh`. Do not attempt a local merge.
- This command is side-effecting and `disable-model-invocation: true`: it runs only when the user types `/ship`.

## Workflow

1. **Find the PR.** Locate the OPEN PR for the convention branch:
   `gh pr list --head <type>/<N>-<slug> --state open --json number,url,title,body,mergeable,mergeStateStatus,reviewDecision`.
   If none is open (already merged, or never created) → STOP and report.
2. **Run the pre-merge Gates — ALL must pass.** Collect every gate's result FIRST, then decide. If ANY gate fails, ABORT the merge (touch nothing) and report exactly which gate(s) failed and how to clear them:
   - **Mergeable** — `mergeable == "MERGEABLE"` (no conflicts with `main`). If `UNKNOWN`, wait a few seconds and re-check once (GitHub computes it async).
   - **CI / status checks green** — `gh pr checks <PR>` reports all required checks passing. If the repo has NO checks configured, this gate PASSES (do not block on absent checks).
   - **Review approved** — `reviewDecision == "APPROVED"`. (See Notes: a solo repo may be unable to self-approve, which blocks this gate.)
   - **Build Status complete** — the PR body's `## Build Status` checklist has every item checked (`- [x]`, with no `- [ ]` left), i.e. `/build`'s Codex loop reached **Result**.
3. **Squash-merge** (only when every gate passed):
   `gh pr merge <PR> --squash --delete-branch --subject "<the PR title>" --body "<concise trailer-free summary>"`.
   - `--squash` collapses the branch's plan + implementation commits into one conventional commit on `main`.
   - `Closes #N` in the PR body closes the tracking issue on merge.
   - `--delete-branch` removes the remote `<type>/<N>-<slug>`.
   - Confirm the subject/body carry NO `Co-Authored-By` trailer.
4. **Cleanup:**
   - **Remote branch** — deleted by `--delete-branch`; verify it's gone (`gh api … || git ls-remote`).
   - **Worktree** — leave and remove it with `ExitWorktree` (action: remove) if you are inside it, else `git worktree remove <recorded worktree path>`.
   - **Local mangled branch** — once outside the worktree, `git branch -D worktree-<slug>`.
   - **Linked issue(s)** — the merge's `Closes #N` keyword closes the tracking issue automatically; VERIFY it (`gh issue view <N> --json state,url` → `CLOSED`). If any issue named by a closing keyword (`Closes #…`) in the PR body is still open, close it explicitly: `gh issue close <N> --comment "Shipped in <merge-sha>"`. (Issues linked only via `Refs #` / `Part of #` are NOT closed.)
   - **Shipped summary** — post one `gh issue comment <N>` (or `gh pr comment <PR>`) recording the squash merge commit SHA and that the issue closed.
5. Never exceed this scope — no force-push, no edits to `main` beyond the merge.

## Report

- The merged PR URL, the squash **merge commit SHA**, and confirmation every linked issue (`Closes #N`) is **CLOSED** — verified after merge, and force-closed if the keyword didn't fire.
- The **Gate results** (each gate: pass/fail) — and if `/ship` aborted, exactly which gate blocked it and how to clear it.
- **Cleanup** done: remote branch deleted, worktree removed, local `worktree-<slug>` deleted, shipped comment posted.
- On graceful skip (no `gh` / no open PR), say so and print the exact manual `gh pr merge <PR> --squash --delete-branch` command the user can run.

## Notes

- **Solo-repo review gate.** GitHub usually forbids approving your own PR, so the "review approved" gate can block `/ship` on a single-maintainer repo (`reviewDecision` stays `REVIEW_REQUIRED` / empty). If that is your setup, drop the review gate from the Workflow above or have a second account approve the PR.
- `/ship` is the inverse of `/build`'s "leave the PR OPEN" guard: `/build` opens the PR, `/ship` merges it.
