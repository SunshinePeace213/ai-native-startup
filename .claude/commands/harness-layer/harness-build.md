---
description: Implement a saved plan on its worktree — build, tidy, publish the build brief, and open a draft PR that /harness-layer:harness-review then gates
argument-hint: [name-or-path-of-plan]
model: fable
effort: high
disable-model-invocation: true
---

# Harness Build

You are the **build lead**: orchestrate builders and never edit implementation files yourself — you own `implementation-notes.md`, `## Tracking`, and the memory-step rule edits, plus every `git`/`gh` call. Implement the plan at `PATH_TO_PLAN` on its worktree, tidy it, publish the build brief, and open a draft PR whose `## Tracking` hand-off block `/harness-layer:harness-review` reads. KB steps run only when `REVIEW_PROFILE` is `kb-grounded`.

## Variables

PATH_TO_PLAN: $ARGUMENTS — plan name (resolves to `specs/<name>/`) or a path to its spec folder
ISSUE_NUMBER: the GitHub issue `#N` from `spec.md`'s `## Tracking` — the join key for `Closes #N` and the `Refs #N` footer
PR_NUMBER: the draft PR `#M` opened here and recorded back into `## Tracking`
REVIEW_PROFILE: `kb-grounded` | `standard`, from `## Tracking` — gates the KB-grounding pass

## Instructions

- No `PATH_TO_PLAN` → STOP and ask the user for it (AskUserQuestion).
- Every commit carries the `Refs #N` footer; every push uses the explicit refspec per `git-workflow.md` — check its exit status directly.
- Under `kb-grounded`, check behavior claims (frontmatter fields, hook events, model aliases, command resolution) against the plan's `## KB References` docs — never from memory. Under `standard`, skip the KB checks.
- **Build to the bar.** `impl-standards.md` (auto-loaded on `specs/**`) is the same checklist the review gate judges the diff against — before opening the PR, self-check the full diff against every standard and fix gaps, so review rounds fix the exceptional, not the expected.
- Every builder spawn prompt carries the full task, its model/effort stamp, its acceptance criteria, and this scope guard: "Don't add features, refactor, or introduce abstractions beyond what the task requires. Do the simplest thing that works well."
- Each builder hands off in its final message: task ID, status, changed files, exact verification commands + observed results (the task's **Verify** command at minimum), deviations from the plan ("none" allowed), and notes/blockers. Builders post no PR comments of their own.
- **A hand-off is a claim.** Re-run each hand-off's **Verify** command yourself before its checkpoint commit — the notes entry records the command and YOUR observed result; a builder's reported green is never the recorded evidence.
- Append every phase, hand-off, and deviation entry to `implementation-notes.md` the moment it lands, inside the same checkpoint commit. The PR body and build brief are derived from the notes — never reconstructed.
- A deviation touching a locked decision or acceptance criterion STOPS for explicit user approval (AskUserQuestion) before work proceeds.

## Workflow

1. **Resolve the plan** — resolve `PATH_TO_PLAN` to its spec folder; read `spec.md`'s `## Tracking` for the worktree path, `ISSUE_NUMBER`, and `REVIEW_PROFILE`. No Issue `#N` → STOP and tell the user to run `/harness-layer:harness-plan` to file the issue first.
2. **Enter the worktree** — work in the recorded worktree; if it is gone, restore it from the convention branch. Never build on `main`.
3. **Read the plan** — read `spec.md`, `tasks.md`, `decisions.md`, `acceptance-criteria.md` in full, plus the `## KB References` docs under `kb-grounded`.
4. **Implement** — create `specs/<name>/implementation-notes.md` from `specs/_templates/implementation-notes.md`, then deploy one background subagent per `tasks.md` task per `orchestration.md`, each on the model/effort its task stamps — all unblocked tasks launch concurrently, with each task's **Files** field as the disjointness contract. As each hand-off lands, re-run its **Verify** command, append its notes entry with your observed result, and checkpoint commit+push.
5. **Tidy & drift check** — deploy `harness-simplifier` for the touched harness/prompt files and `code-simplifier` for the touched app code, concurrently; behavior-preserving auto-fix only. Then append a two-way drift table to `implementation-notes.md`: `BASE=$(git merge-base origin/main HEAD)`; every file in `git diff --name-only $BASE..HEAD` outside `specs/<name>/` maps to the task whose **Files** owns it (or to a tidy/memory entry already in the notes), and every task maps to its present diff. An unmapped file, or a task whose files show no diff, STOPS the build for a deviation entry before the PR opens. Append the tidy entry; commit+push.
6. **Impl lint** — `uv run scripts/impl_lint.py specs/<name>/` from the worktree root. Route each FAIL to the owning task's builder (a fresh background subagent) and re-run to green; append the entry; commit+push.
7. **Build brief** — medium/complex plans only: deploy an `opus` page author for `specs/<name>/artifacts/build-brief.html` per `artifacts.md`, derived from the notes. Commit+push.
8. **Memory** — route each memory-marked lesson per `memory-series.md`: file-scoped → the matching path-scoped rule; pipeline-process → the command or rule it corrects; plan-local stays in the notes. Commit+push — every implementation write is now done.
9. **Open the draft PR** — `gh pr create --draft` filled from `.github/PULL_REQUEST_TEMPLATE/<type>.md` per `pr-process.md` (fill it yourself; never `--template`); mirror the issue's type + `priority:P<n>` labels. Derive the body from the notes: `## Plan` links + `Closes #N`, the stage table (Implementation → Tidy → Codex R1 → Fixes → Codex R2 → Ready), the Agent Task Manifest keyed by the plan's kebab-case Task ID — never `#N`, which GitHub autolinks — and empty `## Review Reports`, `## Dev Notes`, `## Follow-ups` sections. Link the build brief under `## Dev Notes`. Post the simplifiers' findings as the `<!-- report:tidy -->` PR comment per `pr-process.md`; tick **Implementation** and **Tidy**.
10. **Record the hand-off** — `HANDOFF_SHA=$(git rev-parse HEAD)`: the last implementation push, the informational **Hand-off SHA** for the human (review derives its own review range). Write `PR: #M` and `Hand-off SHA: <sha>` (plus anything the human must know) into `## Tracking` as ONE final metadata commit; push it.
11. **Report** — end the run with the `## Report` output.

## Report

After the hand-off commit is pushed, provide a concise report:

```text
✅ Build Complete — draft PR open

Plan: specs/<name>/
Issue: #<N>
PR: #<M> (draft) <url>
Branch: <type>/<N>-<slug>
Hand-off SHA: <sha>
Stages: Implementation ✓ Tidy ✓ Drift check ✓ Impl lint ✓
Tidy report: <clean | N auto-fixes> — posted as <!-- report:tidy -->
Drift check: <every changed file mapped | deviation entries: N>
Impl lint: <clean | N FAILs fixed>
Build brief: <artifacts/build-brief.html + URL | n/a — simple plan>
Memory: <N lessons routed | none>
Tasks: <completed>/<total> — deviations: <count | none>

Implemented:
- <what shipped, concise>

Next: /harness-layer:harness-review <name>
```
