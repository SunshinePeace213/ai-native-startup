---
description: Implement a saved plan on its worktree — build, tidy, and open a draft PR that /harness-layer:harness-review then gates
argument-hint: [name-or-path-of-plan]
model: fable
disable-model-invocation: true
---

# Harness Build

You are the **build lead**: orchestrate builders and never edit implementation files yourself — you own only the `implementation-notes.md`, `## Tracking`, and dev-log edits plus every `git`/`gh` call. Implement the plan at `PATH_TO_PLAN` on its worktree, tidy it, and open a draft PR whose `## Tracking` hand-off block `/harness-layer:harness-review` reads. KB steps run only when `REVIEW_PROFILE` is `kb-grounded`.

## Variables

PATH_TO_PLAN: $ARGUMENTS — plan name (resolves to `specs/<name>/`) or a path to its spec folder
ISSUE_NUMBER: the GitHub issue `#N` from `spec.md`'s `## Tracking` — the join key for `Closes #N` and the `Refs #N` footer
PR_NUMBER: the draft PR `#M` opened here and recorded back into `## Tracking`
REVIEW_PROFILE: `kb-grounded` | `standard`, from `## Tracking` — gates the KB-grounding pass

## Instructions

- No `PATH_TO_PLAN` → STOP and ask the user for it (AskUserQuestion).
- Every commit carries the `Refs #N` footer; every push uses the explicit refspec per `git-workflow.md` — check its exit status directly.
- Under `kb-grounded`, check behavior claims (frontmatter fields, hook events, model aliases, command resolution) against the plan's `## KB References` docs — never from memory. Under `standard`, skip the KB checks.
- Keep the PR body — stage table, Agent Task Manifest, `## Review Reports` — current with `gh pr edit --body-file` as phases land.
- Each builder hands off in its final message: task ID, status, changed files, exact verification commands + observed results, deviations from the plan ("none" allowed), and notes/blockers. Fold these into the Agent Task Manifest keyed by the plan's kebab-case Task ID — never `#N`, which GitHub autolinks. Builders post no PR comments of their own.
- A deviation touching a locked decision or acceptance criterion STOPS for explicit user approval (AskUserQuestion) before work proceeds.

## Workflow

1. **Resolve the plan** — resolve `PATH_TO_PLAN` to its spec folder; read `spec.md`'s `## Tracking` for the worktree path, `ISSUE_NUMBER`, and `REVIEW_PROFILE`.
2. **Guard the issue** — no Issue `#N` in `## Tracking` → STOP and tell the user to run `/harness-layer:harness-plan` to file the issue first.
3. **Enter the worktree** — work in the recorded worktree; if it is gone, restore it from the convention branch. Never build on `main`.
4. **Read the plan** — read `spec.md`, `tasks.md`, `decisions.md`, `acceptance-criteria.md` in full, plus the `## KB References` docs under `kb-grounded`. Think hard before touching files.
5. **Implement** — create `specs/<name>/implementation-notes.md` from `specs/_templates/implementation-notes.md`, then deploy the `tasks.md` team members per `task-tools.md`, each on the model/effort its task stamps — all unblocked, file-disjoint tasks as concurrent background agents. Commit+push each checkpoint, and collect every hand-off.
6. **Tidy** — deploy `harness-simplifier` (`opus`) for the touched harness/prompt files and `code-simplifier` (`opus`) for the touched app code; behavior-preserving auto-fix only. Commit+push.
7. **Open the draft PR** — `gh pr create --draft` with a `--body-file` filled from `.github/PULL_REQUEST_TEMPLATE/<type>.md` (fill it yourself; never `--template`). Mirror the issue's type + `priority:P<n>` labels. Seed the body: `## Plan` links + `Closes #N`, the stage table (Implementation → Tidy → Codex R1 → Fixes → Codex R2 → Ready), the Agent Task Manifest folded from hand-offs, and empty `## Review Reports`, `## Dev Notes`, `## Follow-ups` sections.
8. **Post the tidy report** — post the simplifiers' findings directly as the `<!-- report:tidy -->` PR comment, upserted per `git-workflow.md`; link it under `## Review Reports`. Tick **Implementation** and **Tidy**.
9. **Finish the writes** — append the phase/hand-off/deviation entries to `implementation-notes.md`, then run the memory step (record each memory-marked task's outcome per `memory-series.md`). Commit+push — every implementation write is now done.
10. **Snapshot the hand-off** — `HANDOFF_SHA=$(git rev-parse HEAD)`: the last implementation push, the informational **Hand-off SHA** for the human. Review derives its own review range.
11. **Record the hand-off** — write `PR: #M` and `Hand-off SHA: <sha>` (plus anything the human must know) into `## Tracking` as ONE final metadata commit; push it.
12. **Report** — end the run with the `## Report` output.

## Report

After the hand-off commit is pushed, provide a concise report:

```text
✅ Build Complete — draft PR open

Plan: specs/<name>/
Issue: #<N>
PR: #<M> (draft) <url>
Branch: <type>/<N>-<slug>
Hand-off SHA: <sha>
Stages: Implementation ✓ Tidy ✓
Tidy report: <clean | N auto-fixes> — posted as <!-- report:tidy -->
Tasks: <completed>/<total> — deviations: <count | none>

Implemented:
- <what shipped, concise>

Next: /harness-layer:harness-review <name>
```
