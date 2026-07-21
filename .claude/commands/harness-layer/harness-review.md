---
description: Gate a /harness-layer:harness-build draft PR through Codex cross-review — apply fixes, then flip it ready or leave it draft for the human
argument-hint: [name-or-path-of-plan]
model: fable
disable-model-invocation: true
---

# Harness Review

You are the **review lead**: drive Codex over the build's PR through a `sonnet` runner, route fixes to subagents, and either flip the PR ready at the approved head or leave it draft for the human. You own every `git`/`gh` call; Codex is git read-only and never calls `gh` — you relay. KB grounding applies when `REVIEW_PROFILE` is `kb-grounded`.

## Variables

PATH_TO_PLAN: $ARGUMENTS — plan name (resolves to `specs/<name>/`) or a path to its spec folder
ISSUE_NUMBER: the GitHub issue `#N` from `spec.md`'s `## Tracking` — the `Refs #N` commit footer
PR_NUMBER: the draft PR `#M` from `## Tracking` — the PR this run gates
REVIEW_PROFILE: `kb-grounded` | `standard`, from `## Tracking` — passed to Codex for its KB claim checks

## Workflow

1. **Resolve & read** — resolve `PATH_TO_PLAN`; read `spec.md`'s `## Tracking` for `PR_NUMBER`, `ISSUE_NUMBER`, the worktree path, and `REVIEW_PROFILE`.
2. **Guard the PR** — no PR number in `## Tracking` → STOP and tell the user to run `/harness-layer:harness-build <name>` first.
3. **Enter the worktree** — work in the recorded worktree; if it is gone, restore it from the convention branch. Read `spec.md`, `tasks.md`, `decisions.md`, `acceptance-criteria.md`, and `implementation-notes.md`.
4. **Set the counters** — the **attempt counter** `A` (1–2) is invocation-local and drives control flow; each invocation performs at most 2 attempts. The **report number** `N` is global: highest existing `specs/<name>/reviews/codex-impl-review-round-*.md` + 1. `N` names the report file and picks the review range — `N=1` diffs from `git merge-base origin/main HEAD`, `N>1` from the prior report's reviewed head. Never conflate the two.
5. **Run the round** — snapshot `BASE_SHA` (per `N`) and `REVIEWED_HEAD_SHA=$(git rev-parse HEAD)`, then spawn the runner (below). Post its digest paragraph verbatim as `<!-- report:codex-round-N -->`, upserted per `git-workflow.md`.
6. **Branch on the verdict:**
   - **`A=1` + `changes-requested`** → commit the report (`Refs #N`), spawn fixer subagents per `model-selection.md` (a failed fix escalates a tier), make ONE fix commit, push both, and start attempt 2 (a fresh round at the next `N`).
   - **`approved` (any attempt), or `A=2` + `changes-requested`** → the terminal outcome (step 7).
7. **Terminal outcome** — for medium/complex plans render `specs/<name>/artifacts/dev-notes.html` from `implementation-notes.md` per `artifacts.md`, and run the memory step (record each memory-marked outcome per `memory-series.md`) — both FIRST. Then make ONE **terminal commit** (the report + `dev-notes.html` + dev-log/memory/notes edits), push it, and link the page under `## Dev Notes`. Nothing mutates the repository after it.
   - **`approved`** → verify the PR head equals the terminal commit, tick the stages with it as **Ready** evidence, and `gh pr ready`.
   - **`A=2` + `changes-requested`** → the terminal commit carries the final report; post it as the `<!-- report:codex-round-N -->` comment, leave the PR draft — the human owns the blockers.
8. **Report** — end the run with the `## Report` output.

## Review runner

Deploy the runner with the `Agent` tool (`subagent_type: "general-purpose"`, `model: "sonnet"`, `run_in_background: false`) — never run `codex exec` yourself. Pick the Codex model + reasoning effort per `model-selection.md` by scope (full review vs fix delta). Its prompt carries the round `N`, worktree root, `BASE_SHA`, `REVIEWED_HEAD_SHA`, `REVIEW_PROFILE`, the Codex model + effort, and the command below. The runner runs it via Bash, checks the exit status and whether the verdict line was written, re-runs the identical command once if Codex crashed / exited non-zero / wrote no verdict, and returns ONLY the round verdict (`approved` | `changes-requested`) and the report's `**Issue-comment digest:**` paragraph. It touches no git and no gh.

```bash
codex exec -C "<worktree root>" -s workspace-write --model <codex-model> \
  -c model_reasoning_effort="<effort>" \
  "Use the implementation-review skill for round <N> of the plan at specs/<name>/spec.md; \
   review the diff over <BASE_SHA>..<REVIEWED_HEAD_SHA> (profile <REVIEW_PROFILE>), \
   write your verdict to specs/<name>/reviews/codex-impl-review-round-<N>.md, \
   and return only the terse summary."
```

- **A push landing mid-round** — `REVIEWED_HEAD_SHA` no longer matches `HEAD` → discard the round and re-run it on the new head.
- **Empty diff or missing verdict is never an approval** — an empty review range → `changes-requested` naming it; the runner exhausting its one retry with no verdict → report the failure, leave the PR draft, end the run.

## Report

After the terminal commit is pushed, provide a concise report:

```text
✅ Review Complete — PR ready   (or: ⚠️ Review Blocked — PR left draft)

Plan: specs/<name>/
PR: #<M> — <ready @ <approved-sha> | draft, needs human>
Rounds this run: <1 | 2> — reports: specs/<name>/reviews/codex-impl-review-round-<N>.md
Verdict: <approved at round N | changes-requested after 2 attempts | no verdict — runner failed>
Fixes: <count applied after round N | none needed>
KB grounding: <checked | n/a — standard profile>
Dev notes: <artifacts/dev-notes.html + URL | n/a — simple plan>

Blockers (left draft only):
- <blocker, concise>

Next: /harness-layer:harness-ship <slug>
(or, left draft: resolve the blockers, then rerun /harness-layer:harness-review <name>)
```
