---
description: Implement a saved plan on its worktree, then verify it — internal review (1×) then Codex cross-check (≤2×)
argument-hint: [name-or-path-of-plan]
model: opus
---

# Build

Follow the `Workflow` to implement the plan at `PATH_TO_PLAN` on the branch `plan-w-team` drafted it on, verify it with an internal review then a Codex cross-check, and finish with the `Report`.

## Variables

PATH_TO_PLAN: $ARGUMENTS — a plan name (resolves to `specs/<name>/`) or a path to its spec folder
INTERNAL_CHECK_ROUNDS: `1` — internal review passes (node 5)
MAX_CROSS_CHECK_ROUNDS: `2` — max Codex cross-check rounds before flagging for a human (node 6)
INTERNAL_CHECK: `code-review` — the official code-review plugin, run on the branch diff (node 5)
CROSS_CHECK: `implementation-review` — the Codex cross-check skill, run via `codex exec` (node 6)
HARNESS_SIMPLIFIER: `harness-simplifier` — internal-tidy subagent for harness/prompt files (`.claude/**`, `.agents/**`)
CODE_SIMPLIFIER: `code-simplifier` — internal-tidy subagent for application code (Python, TS/Next.js/React)
REQUIRED_PLUGINS: `codex@openai-codex`, `code-review@claude-plugins-official`

## Instructions

- If no `PATH_TO_PLAN` is provided, STOP immediately and ask the user for it (AskUserQuestion).
- You are the **build lead**: you orchestrate, you do not review your own work. The reviewers (`INTERNAL_CHECK`, `CROSS_CHECK`) are read-only and only report findings — YOU apply every fix (edit directly, or deploy a builder) and own every `git` / `gh` call.
- Build on the plan's existing branch/worktree, never on `main`. Commit a checkpoint after each phase — conventional and trailer-free per `GIT-COMMIT-PR-MESSAGE.md`.

## Workflow

1. **Preflight** — Verify the tools this build reuses are present; STOP with guidance if any is missing (see `Preflight`).
2. **Enter the worktree** — Resolve `PATH_TO_PLAN` to the spec folder, read `spec.md`'s `## Tracking` for its branch and worktree path, and work there. If the worktree is gone, check the plan's branch out into one before building.
3. **Read the plan** — Read `spec.md`, `tasks.md`, `decisions.md`, and `acceptance-criteria.md` in full. Think hard about the approach before touching code.
4. **Implement** — Deploy the team members named in `tasks.md` (or `general-purpose`) to build each task in dependency order, per `.claude/rules/task-tools.md`. Commit each checkpoint.
5. **Internal tidy** — Deploy the tidy subagent for each layer the build touched: `HARNESS_SIMPLIFIER` for harness/prompt files, `CODE_SIMPLIFIER` for application code (run both when a build spans both). Behavior-preserving only. Commit.
6. **Internal review** — Run `INTERNAL_CHECK` (`INTERNAL_CHECK_ROUNDS` time) on the branch diff, fix every finding, then commit. See `Verification`.
7. **Cross-check** — Have Codex review the implementation against the plan, up to `MAX_CROSS_CHECK_ROUNDS`, fixing blocking findings each round. Gate the finish on the outcome. See `Verification`.
8. **Report** — Follow the `Report` section.

## Preflight

Before any work, verify the tools this build reuses. STOP on the first failure and tell the user how to fix it — never proceed degraded.

- **Codex CLI** — `command -v codex`. Missing → STOP: install the Codex CLI, then run `/codex:setup`.
- **Required plugins** — confirm each of `REQUIRED_PLUGINS` is installed (e.g. `grep -q '"codex@openai-codex"' ~/.claude/plugins/installed_plugins.json`). Missing → STOP: add its marketplace and `/plugin install <plugin>` (Codex → `openai/codex-plugin-cc`; code-review → `anthropics/claude-plugins-official`), then re-run.
- **GitHub CLI** (only if you will push or open a PR) — `gh auth status`. Missing / unauthenticated → STOP: run `gh auth login`.

## Verification

Two gates verify the build — one internal (same model), one cross-model. Both are read-only; YOU apply every fix and commit.

**Internal review — node 5 (`INTERNAL_CHECK`, ×`INTERNAL_CHECK_ROUNDS`).** Run the official `code-review` (`/code-review`) on the branch diff. It reports correctness bugs and simplification/efficiency cleanups. Apply its findings, then commit.

**Codex cross-check — node 6 (`CROSS_CHECK`, ≤ `MAX_CROSS_CHECK_ROUNDS`).** Codex runs a 6-lens review of the implementation against the plan — does it follow the plan, are the tasks done, do the Validation Commands pass, are there real bugs (standards, silent-failure, type-design, test-coverage, comment-accuracy) — and flags simpler/cleaner ideas as advisory. Loop per round N:

1. **Ask Codex.** `codex exec -C "<worktree root>" -s workspace-write "Use the implementation-review skill to review round <N> of the plan at specs/<name>/spec.md; run its Validation Commands, write your verdict to specs/<name>/reviews/codex-impl-review-round-<N>.md, and return only the terse summary."`
2. **Read the verdict from the file, not stdout:** `grep -E '^### Round [0-9]+ — Verdict: (approved|changes-requested)$' specs/<name>/reviews/codex-impl-review-round-<N>.md`. A round that writes no verdict is re-run — never treated as approval.
3. **`changes-requested`** → fix every blocking finding, commit, go to round N+1.
4. **`approved`** → gate passed. For each advisory recommendation Codex left, tell the user whether it is genuinely better and ask via AskUserQuestion whether to apply.

**Over `MAX_CROSS_CHECK_ROUNDS` and still `changes-requested`** → STOP. Report the outstanding findings and tell the user to resolve them before hand-off. Do NOT present the success `Report`.

## Report

After the build passes both gates, provide a concise report:

```
✅ Build Complete

Plan: specs/<name>/
Branch: <type>/<slug>
Internal review: <no findings | N fixed>
Codex cross-check: <approved at round N>

Implemented:
- <what shipped, concise>

Next: open a PR from <type>/<slug> when ready.
```
