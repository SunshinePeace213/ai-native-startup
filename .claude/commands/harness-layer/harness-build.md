---
description: Implement a saved harness-layer plan on its worktree via a draft PR, then verify it — internal review (1×) then a KB-grounded Codex cross-check (≤2×)
argument-hint: [name-or-path-of-plan]
model: opus
---

# Harness Build

Follow the `Workflow` to implement the plan at `PATH_TO_PLAN` on the branch `/harness-layer:harness-plan` drafted it on, drive it through a draft PR, verify it with an internal review then a Codex cross-check, and finish by marking the PR ready and reporting.

## Variables

PATH_TO_PLAN: $ARGUMENTS — a plan name (resolves to `specs/<name>/`) or a path to its spec folder
KNOWLEDGE_BASE: `ai-docs/` — cached official docs; catalog in `ai-docs/index.md`
ISSUE_NUMBER: the GitHub issue `#N` read from `spec.md`'s `## Tracking` — the join key for `Closes #N`, commit footer `Refs #N`, and the `status:needs-human` escalation. Absent → Preflight STOP.
PR_NUMBER: the draft PR `#M` opened in node 5 and recorded back into `## Tracking`.
STAGES: the PR stage-table rows, ticked live as phases land — Implementation → Tidy → Internal code-review → Codex R1 → Fixes (if required) → Codex R2 delta (if required) → Ready.
INTERNAL_CHECK_ROUNDS: `1` — internal review passes (node 7)
MAX_CROSS_CHECK_ROUNDS: `2` — max Codex cross-check rounds before flagging for a human (node 8)
INTERNAL_CHECK: `code-review` — the official code-review plugin, run on the branch diff (node 7)
CROSS_CHECK: `harness-implementation-review` — the KB-grounded Codex cross-check skill, run via `codex exec` (node 8)
HARNESS_SIMPLIFIER: `harness-simplifier` — internal-tidy subagent for harness/prompt files (`.claude/**`, `.agents/**`), deployed on `opus`
CODE_SIMPLIFIER: `code-simplifier` — internal-tidy subagent for application code (Python, TS/Next.js/React), deployed on `opus`
REQUIRED_PLUGINS: `codex@openai-codex`, `code-review@claude-plugins-official`

## Instructions

- If no `PATH_TO_PLAN` is provided, STOP immediately and ask the user for it (AskUserQuestion).
- You are the **build lead**: you orchestrate, you do not review your own work. The reviewers (`INTERNAL_CHECK`, `CROSS_CHECK`) are read-only and only report findings — YOU apply every fix (edit directly, or deploy a builder) and own every `git` / `gh` call, including the PR.
- Build on the plan's existing branch/worktree, never on `main`. Commit a checkpoint after each phase — conventional and trailer-free per `GIT-COMMIT-PR-MESSAGE.md`, each carrying the footer `Refs #N`.
- The diff is harness material: when implementing or fixing, check behavior claims (frontmatter fields, hook events, model aliases, command resolution) against the `KNOWLEDGE_BASE` docs listed in `decisions.md`'s `## KB References` — don't work from memory.
- **Drive the build through a draft PR.** Once the first checkpoint is pushed, open the draft PR (node 5) and keep its body — the stage table and Agent Task Manifest — current with `gh pr edit --body-file` as each phase lands.
- **Post each report as an idempotent PR comment.** Tidy, internal review, and every Codex round each get ONE comment keyed by a stable first-line marker — `<!-- report:tidy -->`, `<!-- report:code-review -->`, `<!-- report:codex-round-N -->`. Upsert it: find the existing comment by its marker (`gh api repos/{owner}/{repo}/issues/<PR>/comments`), PATCH that comment if present, else create it. Always write the body to a file and upload with `--body-file` — never inline a body into the shell. Every review comment states the reviewed head SHA.
- **Each builder hands off in its final message**: task ID, status, changed files, exact verification commands + observed results, and notes/blockers. Fold these into the PR body's Agent Task Manifest table (`task | owner | done | verification | notes`) — builders post no PR comments of their own.

## Workflow

1. **Preflight** — Verify the reused tools, `gh` auth, and that the plan carries an Issue `#N`; STOP with guidance on any failure (see `Preflight`).
2. **Enter the worktree** — Resolve `PATH_TO_PLAN` to the spec folder, read `spec.md`'s `## Tracking` for its branch, worktree path, and Issue `#N`, and work there. If the worktree is gone, check the plan's branch out into one before building.
3. **Read the plan** — Read `spec.md`, `tasks.md`, `decisions.md`, and `acceptance-criteria.md` in full, plus the KB docs listed in `## KB References`. Think hard about the approach before touching files.
4. **Implement** — Deploy the team members named in `tasks.md` (or `general-purpose`) to build each task in dependency order, per `.claude/rules/task-tools.md`. Commit each checkpoint (`Refs #N`) and collect every builder's hand-off.
5. **Open the draft PR** — After the first checkpoint is pushed: `gh pr create --draft --title "<emoji> <type>(<scope>): <desc>"` with a `--body-file` filled from `.github/PULL_REQUEST_TEMPLATE/<type>.md` (fill it yourself — do NOT use `--template`, which reads the default branch). Carry `Closes #N`, seed the stage table and the Agent Task Manifest table, tick **Implementation**, and record `PR #M` in `spec.md`'s `## Tracking`.
6. **Internal tidy** — Deploy `HARNESS_SIMPLIFIER` on `opus` for the harness/prompt files the build touched; deploy `CODE_SIMPLIFIER` (also `opus`) only if the build also touched application code. Behavior-preserving only. Post their one report as the `<!-- report:tidy -->` comment, commit, tick **Tidy**.
7. **Internal review** — Run `INTERNAL_CHECK` (`INTERNAL_CHECK_ROUNDS` time) on the branch diff, post its consolidated findings as `<!-- report:code-review -->`, fix every finding, commit, tick **Internal code-review**. See `Verification`.
8. **Cross-check** — Have Codex review the implementation against the plan and the KB under a SHA freeze, up to `MAX_CROSS_CHECK_ROUNDS`, posting `<!-- report:codex-round-N -->` and fixing blockers each round. Tick **Codex R1**, **Fixes**, and **Codex R2 delta** as they occur. Gate the finish on the outcome. See `Verification`.
9. **Finish & report** — On Codex approval, verify the PR head equals the approved SHA, tick **Ready**, run `gh pr ready`, and follow the `Report`.

## Preflight

Before any work, verify the tools this build reuses. STOP on the first failure and tell the user how to fix it — never proceed degraded.

- **Codex CLI** — `command -v codex`. Missing → STOP: install the Codex CLI, then run `/codex:setup`.
- **Required plugins** — confirm each of `REQUIRED_PLUGINS` is installed (e.g. `grep -q '"codex@openai-codex"' ~/.claude/plugins/installed_plugins.json`). Missing → STOP: add its marketplace and `/plugin install <plugin>` (Codex → `openai/codex-plugin-cc`; code-review → `anthropics/claude-plugins-official`), then re-run.
- **GitHub CLI** — `gh auth status`. The build always pushes and opens a PR, so `gh` is required, not optional. Missing / unauthenticated → STOP: run `gh auth login`.
- **Issue number** — `spec.md`'s `## Tracking` names an Issue `#N`. Absent → STOP: the PR needs `Closes #N` and commits need `Refs #N`; file the issue and record it in `## Tracking` first.

## Verification

Two gates verify the build — one internal (same model), one cross-model. Both are read-only; YOU apply every fix, commit, and post the report comment.

**Internal review — node 7 (`INTERNAL_CHECK`, ×`INTERNAL_CHECK_ROUNDS`).** Run the official `code-review` (`/code-review`) on the branch diff. It reports correctness bugs and simplification/efficiency cleanups. Its lead runs at most `sonnet` and its finder subagents on `haiku` — no `opus`- or `fable`-level model is spawned for internal review; the tidy simplifiers (`opus`) are the sole exception above Sonnet. Post the consolidated findings as `<!-- report:code-review -->` (stating the reviewed head SHA), apply every finding, then commit.

**Codex cross-check — node 8 (`CROSS_CHECK`, ≤ `MAX_CROSS_CHECK_ROUNDS`).** Codex reviews the implementation against the plan with the harness lens set (standards, comment-accuracy, silent-failure for hook scripts, simplification as advisory), runs the plan's Validation Commands, and verifies every harness-behavior claim against the `KNOWLEDGE_BASE` — contradictions with the cached official docs are blocking. Each round runs under a **SHA freeze**: implementation writes are frozen while the round runs, and any push invalidates the round (re-run it).

Before each round: ensure a clean tree, then snapshot `BASE_SHA=$(git merge-base origin/main HEAD)` and `REVIEWED_HEAD_SHA=$(git rev-parse HEAD)`. Loop per round N:

1. **Ask Codex.** Pass `BASE_SHA`, `REVIEWED_HEAD_SHA`, the round number `N`, and (for N>1) the prior round's reviewed-head SHA explicitly:
   `codex exec -C "<worktree root>" -s workspace-write "Use the harness-implementation-review skill to review round <N> of the plan at specs/<name>/spec.md. BASE_SHA=<base>, REVIEWED_HEAD_SHA=<head>, PRIOR_REVIEWED_HEAD=<prior-or-none>. Round 1 is a full risk-tiered review; round 2+ reviews only the delta <prior-reviewed-head>..<current-head>. Run its Validation Commands, verify harness claims against the KB, write your verdict to specs/<name>/reviews/codex-impl-review-round-<N>.md, and return only the terse summary."`
2. **Read the verdict from the file, not stdout:** `grep -E '^### Round [0-9]+ — Verdict: (approved|changes-requested)$' specs/<name>/reviews/codex-impl-review-round-<N>.md`. A round that writes no verdict is re-run — never treated as approval.
3. **Post the report** — upload the report file's content as the `<!-- report:codex-round-N -->` comment, stating `REVIEWED_HEAD_SHA`.
4. **`changes-requested`** → fix every blocking finding (route each fix to its original builder where practical). Then make **exactly one commit+push** for the round — the review report plus any fixes, `Refs #N`, **never amend** — tick **Fixes**, and go to round N+1 with fresh SHAs.
5. **`approved`** → commit+push the round's review report in that same single commit (the approved head), verify the PR head equals it, tick **Codex R{N}**. For each advisory recommendation, tell the user whether it is genuinely better and ask via AskUserQuestion whether to apply.

**Over `MAX_CROSS_CHECK_ROUNDS` and still `changes-requested`** → STOP. Add the `status:needs-human` label to the issue (`gh issue edit <N> --add-label status:needs-human`), report the outstanding findings, and tell the user to resolve them before hand-off. Do NOT present the success `Report`.

## Report

After the build passes both gates and the PR is ready, provide a concise report:

```
✅ Harness Build Complete

Plan: specs/<name>/
Issue: #<N>
PR: #<M> (ready) @ <approved-sha>
Branch: <type>/<slug>
Stages: Implementation ✓ Tidy ✓ Internal code-review ✓ Codex R<n> ✓ Ready ✓
Internal review: <no findings | N fixed>
Codex cross-check: <approved at round N>
KB grounding: <docs checked, contradictions fixed if any>

Implemented:
- <what shipped, concise>

Next: /ship <type>/<slug>.
```
