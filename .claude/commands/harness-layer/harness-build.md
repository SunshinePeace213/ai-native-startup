---
description: Implement a saved plan (application code or harness work) on its worktree via a draft PR, then verify it — internal review ∥ Codex round 1 concurrent, Codex cross-check ≤2 rounds
argument-hint: [name-or-path-of-plan]
model: opus
---

# Harness Build

Follow the `Workflow` to implement the plan at `PATH_TO_PLAN` — application code or harness work, one universal path — on the worktree `/harness-layer:harness-plan` created for it, drive it through a draft PR, verify it with a concurrent internal review and Codex round 1 then a bounded Codex cross-check, and finish by marking the PR ready and reporting. The KB-grounding steps run only when the plan's `Review profile` is `kb-grounded`.

## Variables

PATH_TO_PLAN: $ARGUMENTS — a plan name (resolves to `specs/<name>/`) or a path to its spec folder
REVIEW_PROFILE: `kb-grounded` | `standard`, read from `spec.md`'s `## Tracking` — gates the KB-grounding pass and the KB claim map
KNOWLEDGE_BASE: `ai-docs/` — cached official docs (catalog `ai-docs/index.md`), consulted only under `kb-grounded`
ISSUE_NUMBER: the GitHub issue `#N` read from `spec.md`'s `## Tracking` — the join key for `Closes #N`, commit footer `Refs #N`, and the `status:needs-human` escalation. Absent → Preflight STOP.
PR_NUMBER: the draft PR `#M` opened at the Open-the-draft-PR step and recorded back into `## Tracking`.
STAGES: the PR stage-table rows, ticked live as phases land — Implementation → Tidy → R1 reviews (internal ∥ Codex) → Fixes → Codex R2 delta → Ready.
MAX_CROSS_CHECK_ROUNDS: `2` — hard cap on Codex rounds; EVERY `codex exec` invocation counts, advisory-induced included.
INTERNAL_CHECK: `.claude/commands/harness-layer/harness-review.md` — the internal review, executed by a dedicated read-only `sonnet` review-lead subagent that reads and follows it, returning consolidated findings.
CROSS_CHECK: `implementation-review` — the Codex cross-check skill, run via `codex exec`.
HARNESS_SIMPLIFIER: `harness-simplifier` — internal-tidy subagent for harness/prompt files (`.claude/**`, `.agents/**`), deployed on `opus`
CODE_SIMPLIFIER: `code-simplifier` — internal-tidy subagent for application code (Python, TS/Next.js/React), deployed on `opus`
REQUIRED_PLUGINS: `codex@openai-codex`

## Instructions

- If no `PATH_TO_PLAN` is provided, STOP immediately and ask the user for it (AskUserQuestion).
- You are the **build lead**: you orchestrate, you do not review your own work. The reviewers (`INTERNAL_CHECK`, `CROSS_CHECK`) are read-only and only report findings — YOU apply every fix (edit directly, or deploy a builder) and own every `git` / `gh` call, including the PR.
- Build on the plan's existing worktree, never on `main`. Commit **and push** a checkpoint after each phase — conventional and trailer-free per `GIT-COMMIT-PR-MESSAGE.md`, each carrying the footer `Refs #N`. An unpushed SHA cannot be linked, so every stage-table Evidence entry must be a pushed commit SHA (GitHub auto-links it) or a report-comment URL. Always push with the explicit refspec `git push origin HEAD:refs/heads/<type>/<N>-<slug>` — from the local `worktree-<slug>` branch a bare `git push` refuses (upstream name mismatch) — and check the push's exit status directly; piping it into another command hides the failure.
- **Under `kb-grounded`**, when implementing or fixing, check behavior claims (frontmatter fields, hook events, model aliases, command resolution) against the `KNOWLEDGE_BASE` docs listed in `decisions.md`'s `## KB References` — don't work from memory. Under `standard`, skip the KB checks.
- **Drive the build through a draft PR.** Once the first checkpoint is pushed, open the draft PR and keep its body — the `## Plan` links, stage table, and Agent Task Manifest — current with `gh pr edit --body-file` as each phase lands.
- **Post each report as an idempotent PR comment.** Tidy, internal review, and every Codex round each get ONE comment keyed by a stable first-line marker — `<!-- report:tidy -->`, `<!-- report:code-review -->`, `<!-- report:codex-round-N -->`. Upsert it: list comments with `gh api --paginate repos/{owner}/{repo}/issues/<PR>/comments` and search for the marker; if found, update with `gh api --method PATCH repos/{owner}/{repo}/issues/comments/<comment-id> -F body=@<file>`; else create with `gh pr comment <PR> --body-file <file>`. Always write the body to a file first — never inline a body into the shell (`gh api` has no `--body-file`; file-backed `-F body=@<file>` is the update path). Every review comment states the reviewed head SHA. As each report posts, replace its entry in the PR body's `## Review Reports` list with the comment URL.
- **Each builder hands off in its final message**: task ID, status, changed files, exact verification commands + observed results, and notes/blockers. Fold these into the PR body's Agent Task Manifest table (`task | owner | done | verification | notes`) — builders post no PR comments of their own.

## Workflow

1. **Preflight** — Verify the reused tools, `gh` auth, and that the plan carries an Issue `#N`; STOP with guidance on any failure (see `Preflight`).
2. **Enter the worktree** — Resolve `PATH_TO_PLAN` to the spec folder, read `spec.md`'s `## Tracking` for its worktree path, Issue `#N`, and `Review profile`, and work there. If the worktree is gone, restore it from the plan's branch before building.
3. **Read the plan** — Read `spec.md`, `tasks.md`, `decisions.md`, and `acceptance-criteria.md` in full — plus the `## KB References` docs under `kb-grounded`. Think hard about the approach before touching files.
4. **Implement** — Deploy the team members named in `tasks.md` (or `general-purpose`) to build each task in dependency order, per `.claude/rules/task-tools.md`. Commit+push each checkpoint (`Refs #N`) and collect every builder's hand-off.
5. **Open the draft PR** — After the first checkpoint is pushed: `gh pr create --draft --title "<emoji> <type>(<scope>): <desc>"` with a `--body-file` filled from `.github/PULL_REQUEST_TEMPLATE/<type>.md` (fill it yourself — do NOT use `--template`, which reads the default branch). Seed the body per `PR body`, tick **Implementation**, record `PR #M` in `## Tracking`, and commit+push that Tracking edit (`Refs #N`) — an uncommitted Tracking line leaves `main` pointing at no PR after merge.
6. **Internal tidy** — Deploy `HARNESS_SIMPLIFIER` on `opus` for the harness/prompt files the build touched; deploy `CODE_SIMPLIFIER` (also `opus`) for the application code it touched (both when a build spans both). Behavior-preserving only. Post their one report as `<!-- report:tidy -->`, commit+push, tick **Tidy**.
7. **Concurrent R1 review** — Freeze the SHA, launch `INTERNAL_CHECK` and Codex round 1 in parallel, then merge, report, fix, and push per `Verification`. Tick **R1 reviews (internal ∥ Codex)**.
8. **Codex R2 delta** — When R1 is not a clean pass, Codex reviews the fix delta and dispositions both reports, bounded by `MAX_CROSS_CHECK_ROUNDS`; a round-2 `changes-requested` hits the over-cap gate. Tick **Fixes** and **Codex R2 delta**. See `Verification`.
9. **Finish & report** — On approval, verify the PR head equals the approved SHA, tick **Ready**, run `gh pr ready`, and follow the `Report`.

## Preflight

Before any work, verify the tools this build reuses. STOP on the first failure and tell the user how to fix it — never proceed degraded.

- **Codex CLI** — `command -v codex`. Missing → STOP: install the Codex CLI, then run `/codex:setup`.
- **Required plugins** — confirm `REQUIRED_PLUGINS` is installed (`grep -q '"codex@openai-codex"' ~/.claude/plugins/installed_plugins.json`). Missing → STOP: add its marketplace and `/plugin install codex@openai-codex` (from `openai/codex-plugin-cc`), then re-run.
- **GitHub CLI** — `gh auth status`. The build always pushes and opens a PR, so `gh` is required, not optional. Missing / unauthenticated → STOP: run `gh auth login`.
- **Issue number** — `spec.md`'s `## Tracking` names an Issue `#N`. Absent → STOP: the PR needs `Closes #N` and commits need `Refs #N`; file the issue and record it in `## Tracking` first.

## Verification

Two read-only gates verify the build — internal (same model) and Codex (cross-model); YOU apply every fix, commit, and post the report comment. Round 1 runs both gates **concurrently**; a Codex round 2 delta follows only when round 1 is not a clean pass. Hard cap: `MAX_CROSS_CHECK_ROUNDS` Codex rounds.

**Freeze & tracked SHAs.** Ensure a clean tree, then snapshot `BASE_SHA=$(git merge-base origin/main HEAD)` and `REVIEWED_HEAD_SHA=$(git rev-parse HEAD)`. A round tracks four SHAs: `BASE_SHA`, `REVIEWED_HEAD_SHA` (the reviewed input), the **report SHA** (the report commit), and the **fix SHA** (the fix commit). Any push while a round is running invalidates it — re-freeze and re-run.

**Round 1 (concurrent).** On the frozen `REVIEWED_HEAD_SHA`, launch both reviews at once; neither writes to the tree until both return, and you commit afterward.

- **Internal review** — deploy one read-only review-lead subagent on `sonnet` that reads `INTERNAL_CHECK` and follows it, returning consolidated findings (it never posts or mutates, `gh` reads only — the command itself encodes draft-PR acceptance and the read-only rules). Post them verbatim as `<!-- report:code-review -->` stating `REVIEWED_HEAD_SHA`.
- **Codex round 1** — `codex exec` with `CROSS_CHECK` on the same SHA, injecting the `Review packet`. Read the verdict from the file, not stdout: `grep -E '^### Round [0-9]+ — Verdict: (approved|changes-requested)$' specs/<name>/reviews/codex-impl-review-round-1.md` — a round that writes no verdict is re-run, never treated as approval. Post the file as `<!-- report:codex-round-1 -->`.

**Both clean** — Codex `approved` AND internal review returns zero findings → commit the round-1 Codex report (`Refs #N`); that **report commit is the approved head**. Skip round 2, mark Fixes and Codex R2 delta n/a → **Ready**.

**Otherwise** → merge the two finding sets (dedup by root cause, keep source IDs), make the **report commit** (the round-1 report file), apply ONE combined fix pass over both reports' blockers, make the **fix commit** (`Refs #N`, never amend), and push both together (one push). Tick **Fixes** with the fix SHA, then run the Codex R2 delta.

**Codex R2 delta.** Re-freeze, then `codex exec` with `CROSS_CHECK` reviewing only the fix delta `<prior-reviewed-head>..<head>` **excluding** `specs/<name>/reviews/`, dispositioning findings from BOTH round-1 reports; inject the `Review packet`. Read and post the verdict as `<!-- report:codex-round-2 -->` (as above).

- **`approved`** → commit the round-2 report (`Refs #N`); that **report commit is the approved head**. Verify the PR head equals it and tick **Codex R2 delta**.
- **`changes-requested`** → round 2 is the last automatic round → the **Over-cap gate**.

**Advisories** (any round) never spawn an in-build round and get no per-advisory AskUserQuestion — record each in the PR body's `## Follow-ups` checklist to feed a future plan.

**Over-cap gate** — `MAX_CROSS_CHECK_ROUNDS` reached and round 2 still `changes-requested` → STOP and present ONE AskUserQuestion covering why a further round is needed, what it would do, and the next steps per option:

- (a) **run one more delta round** — apply fixes, re-freeze, and review the new delta.
- (b) **`accepted-with-unverified-fixes`** — allowed ONLY when the remaining blockers are non-severe and mechanically verifiable, the plan's Validation Commands pass after the fixes, and the user explicitly picks it.
- (c) **`needs-human`** — add the label (`gh issue edit <N> --add-label status:needs-human`) and post an issue comment naming the blockers with a link to the PR and its latest `<!-- report:codex-round-N -->` comment.

The user's selection is final. Record the chosen exit status — `approved` | `accepted-with-unverified-fixes` | `needs-human` — in the PR. When a later round reaches `approved` after a `needs-human` escalation, remove the label (`gh issue edit <N> --remove-label status:needs-human`). Do NOT present the success `Report` on `needs-human`.

## Review packet

Inject into every `codex exec` prompt: `BASE_SHA`, `REVIEWED_HEAD_SHA`, the round `N`; for `N>1` the prior reviewed head and prior finding IDs; a clean-tree attestation; the `git diff --numstat` and `--name-status` summary; `REVIEW_PROFILE`; the internal-review findings for dedup (`N>1`; on round 1 note they run concurrently); validation results keyed to the frozen SHA; a KB claim map (claim → `ai-docs/` path → excerpt → fetched date) when `REVIEW_PROFILE` is `kb-grounded`; and your EXPECTED lens list — Codex re-verifies lens selection independently and reports disagreement.

`codex exec -C "<worktree root>" -s workspace-write "Use the implementation-review skill for round <N> of the plan at specs/<name>/spec.md. <Review packet>. Round 1 is a full risk-tiered review; round 2 reviews only the delta <prior-reviewed-head>..<head> excluding specs/<name>/reviews/. Run its Validation Commands, write your verdict to specs/<name>/reviews/codex-impl-review-round-<N>.md, and return only the terse summary."`

## PR body

Seed at creation and keep current with `gh pr edit --body-file`:

- `## Plan` — blob URLs on the convention branch `<type>/<N>-<slug>` to `spec.md`, `tasks.md`, `decisions.md`, `acceptance-criteria.md`, and the `reviews/` folder, plus `Closes #N`.
- **Stage table** — the `STAGES` rows, each ticked with a pushed SHA or comment URL as Evidence.
- **Agent Task Manifest** — `task | owner | done | verification | notes`, folded from builder hand-offs.
- `## Review Reports` — one entry per report comment, replaced with its comment URL as it posts.
- `## Follow-ups` — the advisory checklist for a future plan; record the final exit status here on `accepted-with-unverified-fixes` / `needs-human`.

## Report

After the build passes both gates and the PR is ready, provide a concise report:

```
✅ Build Complete

Plan: specs/<name>/
Issue: #<N>
PR: #<M> (ready) @ <approved-sha>
Branch: <type>/<N>-<slug>
Stages: Implementation ✓ Tidy ✓ R1 reviews ✓ Fixes ✓ Codex R2 delta ✓ Ready ✓
Round 1: <both clean | internal N fixed / Codex changes-requested>
Codex cross-check: <approved at round N | accepted-with-unverified-fixes | needs-human>
KB grounding: <docs checked, contradictions fixed — kb-grounded only>

Implemented:
- <what shipped, concise>

Next: /harness-layer:harness-ship <slug>.
```
