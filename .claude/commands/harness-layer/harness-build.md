---
description: Implement a saved plan (application code or harness work) on its worktree via a draft PR, then verify it — internal review ∥ Codex round 1 concurrent, Codex cross-check ≤2 rounds
argument-hint: [name-or-path-of-plan]
model: fable
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
MAX_CROSS_CHECK_ROUNDS: `2` — hard cap on automatic Codex review rounds; EVERY review `codex exec` counts, advisory-induced included. Co-development and role-swap writer invocations are not review rounds.
MAX_TOTAL_ROUNDS: `4` — absolute ceiling on Codex review rounds including user-gated escalation rounds; at the ceiling only stage E3 of the `Escalation ladder` (or the escape hatch) remains.
INTERNAL_CHECK: `harness-layer:harness-review` — the internal review command, invoked in-session with the Skill tool (never via a nested review-lead subagent); you follow it yourself, spawning its reviewer agents directly and consolidating the findings.
CROSS_CHECK: `implementation-review` — the Codex cross-check skill, run via `codex exec`.
HARNESS_SIMPLIFIER: `harness-simplifier` — internal-tidy subagent for harness/prompt files (`.claude/**`, `.agents/**`), deployed on `opus`
CODE_SIMPLIFIER: `code-simplifier` — internal-tidy subagent for application code (Python, TS/Next.js/React), deployed on `opus`
REQUIRED_PLUGINS: `codex@openai-codex`

## Instructions

- If no `PATH_TO_PLAN` is provided, STOP immediately and ask the user for it (AskUserQuestion).
- You are the **build lead**: you orchestrate, you do not review your own work, and you never edit files directly. The reviewers (`INTERNAL_CHECK`, `CROSS_CHECK`) are read-only and only report findings — YOU route every fix to a fixer subagent, picking its **model and effort** per issue difficulty from the AGENTS.md tables, quality-first (Quality > time > cost; the full range is live, `max` included, ceiling `opus` — `fable` is orchestrator-only; one agent, one purpose), passing the model via the Agent tool's `model` param; the effort tier goes in that fixer's task brief as depth guidance, since subagents inherit the session's reasoning effort. Brief every fixer with its findings' repair contracts, and never retry a blocker dispositioned `not fixed` at the same model/effort — escalate per the `Escalation ladder`. You own every `git` / `gh` call, including the PR.
- Build on the plan's existing worktree, never on `main`. Commit **and push** a checkpoint after each phase — conventional and trailer-free per `GIT-COMMIT-PR-MESSAGE.md`, each carrying the footer `Refs #N`. An unpushed SHA cannot be linked, so every stage-table Evidence entry must be a pushed commit SHA (GitHub auto-links it) or a report-comment URL. Always push with the explicit refspec `git push origin HEAD:refs/heads/<type>/<N>-<slug>` — from the local `worktree-<slug>` branch a bare `git push` refuses (upstream name mismatch) — and check the push's exit status directly; piping it into another command hides the failure.
- **Under `kb-grounded`**, when implementing or fixing, check behavior claims (frontmatter fields, hook events, model aliases, command resolution) against the `KNOWLEDGE_BASE` docs listed in `decisions.md`'s `## KB References` — don't work from memory. Under `standard`, skip the KB checks.
- **Drive the build through a draft PR.** Once the first checkpoint is pushed, open the draft PR and keep its body — the `## Plan` links, stage table, and Agent Task Manifest — current with `gh pr edit --body-file` as each phase lands.
- **Post each report as an idempotent PR comment.** Tidy, internal review, and every Codex round each get ONE comment keyed by a stable first-line marker — `<!-- report:tidy -->`, `<!-- report:code-review -->`, `<!-- report:codex-round-N -->`. Upsert it: list comments with `gh api --paginate repos/{owner}/{repo}/issues/<PR>/comments` and search for the marker; if found, update with `gh api --method PATCH repos/{owner}/{repo}/issues/comments/<comment-id> -F body=@<file>`; else create with `gh pr comment <PR> --body-file <file>`. Always write the body to a file first — never inline a body into the shell (`gh api` has no `--body-file`; file-backed `-F body=@<file>` is the update path). Every review comment states the reviewed head SHA. As each report posts, replace its entry in the PR body's `## Review Reports` list with the comment URL.
- **Each builder hands off in its final message**: task ID, status, changed files, exact verification commands + observed results, and notes/blockers. Fold these into the PR body's Agent Task Manifest table (`task | owner | done | verification | notes`), keying the task column by the plan's kebab-case Task ID — never `#N`, which GitHub autolinks to unrelated issues/PRs. Builders post no PR comments of their own.

## Workflow

1. **Preflight** — Verify the reused tools, `gh` auth, and that the plan carries an Issue `#N`; STOP with guidance on any failure (see `Preflight`).
2. **Enter the worktree** — Resolve `PATH_TO_PLAN` to the spec folder, read `spec.md`'s `## Tracking` for its worktree path, Issue `#N`, and `Review profile`, and work there. If the worktree is gone, restore it from the plan's branch before building.
3. **Read the plan** — Read `spec.md`, `tasks.md`, `decisions.md`, and `acceptance-criteria.md` in full — plus the `## KB References` docs under `kb-grounded`. Think hard about the approach before touching files.
4. **Implement** — Deploy the team members named in `tasks.md` (or `general-purpose`) per `.claude/rules/task-tools.md`, each on the model and effort its task stamps in the plan: launch all currently-unblocked, file-disjoint tasks concurrently as background agents, letting `tasks.md` keep owning the dependency structure. Tasks stamped implementer: `codex` run per `Codex co-development` — leased writer invocations, never concurrent with a writer whose scope intersects. Commit+push each checkpoint (`Refs #N`) and collect every builder's hand-off.
5. **Open the draft PR** — After the first checkpoint is pushed: `gh pr create --draft --assignee $(gh api user -q .login) --title "<emoji> <type>(<scope>): <desc>"` with a `--body-file` filled from `.github/PULL_REQUEST_TEMPLATE/<type>.md` (fill it yourself — do NOT use `--template`, which reads the default branch). Mirror onto the PR the linked issue's type label and its `priority:P<n>` label, read via `gh issue view <N> --json labels`. Seed the body per `PR body`, tick **Implementation**, record `PR #M` in `## Tracking`, and commit+push that Tracking edit (`Refs #N`) — an uncommitted Tracking line leaves `main` pointing at no PR after merge.
6. **Internal tidy** — Deploy `HARNESS_SIMPLIFIER` on `opus` for the harness/prompt files the build touched; deploy `CODE_SIMPLIFIER` (also `opus`) for the application code it touched (both when a build spans both). Behavior-preserving only. Post their one report as `<!-- report:tidy -->`, commit+push, tick **Tidy**.
7. **Concurrent R1 review** — Freeze the SHA, start Codex round 1 in the background and run `INTERNAL_CHECK` in-session while it executes, then merge, report, fix, and push per `Verification`. Tick **R1 reviews (internal ∥ Codex)**.
8. **Codex R2 delta** — When R1 is not a clean pass, Codex reviews the fix delta and dispositions both reports, bounded by `MAX_CROSS_CHECK_ROUNDS`; a round-2 `changes-requested` hits the `Escalation ladder`. Tick **Fixes** and **Codex R2 delta**. See `Verification`.
9. **Finish & report** — On approval, verify the PR head equals the approved SHA, tick **Ready**, run `gh pr ready`, and follow the `Report`.

## Preflight

Before any work, verify the tools this build reuses. STOP on the first failure and tell the user how to fix it — never proceed degraded.

- **Codex CLI** — `command -v codex`. Missing → STOP: install the Codex CLI, then run `/codex:setup`.
- **Required plugins** — confirm `REQUIRED_PLUGINS` is installed (`grep -q '"codex@openai-codex"' ~/.claude/plugins/installed_plugins.json`). Missing → STOP: add its marketplace and `/plugin install codex@openai-codex` (from `openai/codex-plugin-cc`), then re-run.
- **GitHub CLI** — `gh auth status`. The build always pushes and opens a PR, so `gh` is required, not optional. Missing / unauthenticated → STOP: run `gh auth login`.
- **Issue number** — `spec.md`'s `## Tracking` names an Issue `#N`. Absent → STOP: the PR needs `Closes #N` and commits need `Refs #N`; file the issue and record it in `## Tracking` first.

## Codex co-development

Tasks stamped implementer: `codex` in `tasks.md` — and every E2 role-swap fix — run as **leased Codex writer invocations**: Codex edits, you own git.

- **Lease.** Grant the task's writable files/globs from the plan; name the forbidden paths. One active writer per scope — while the lease is open, launch no other writer that intersects it; sequence overlapping tasks by dependency.
- **Invoke.** Clean tree, starting SHA pushed, then `codex exec -C "<worktree root>" -s workspace-write --model <codex-model> -c model_reasoning_effort="<effort>" "<brief>"` — model and effort quality-first from the AGENTS.md Codex table.
- **Brief** (all of): one purpose + the task ID; spec/decision excerpts and the exact acceptance criteria; the lease (writable scope + forbidden files); the starting SHA; validation commands with expected outcomes; non-goals and locked decisions; the hand-off format (changed files, commands + observed results, assumptions, residual risks). Codex runs no `git`/`gh`, ever — you commit.
- **Gate.** On return: diff against the lease (out-of-lease edits → revert them and re-brief), then deploy a fresh Claude reviewer subagent on the Codex-only delta — mandatory: neither model's code merges unreviewed by the other, and Codex never approves its own delta (the Codex review rounds still cover the integrated build). Route fixes, commit+push, fold the hand-off into the manifest.

## Verification

Two read-only gates verify the build — internal (same model) and Codex (cross-model); YOU apply every fix, commit, and post the report comment. Round 1 runs both gates **concurrently**; a Codex round 2 delta follows only when round 1 is not a clean pass. Hard cap: `MAX_CROSS_CHECK_ROUNDS` Codex rounds.

**Freeze & tracked SHAs.** Ensure a clean tree, then snapshot `BASE_SHA=$(git merge-base origin/main HEAD)` and `REVIEWED_HEAD_SHA=$(git rev-parse HEAD)`. A round tracks four SHAs: `BASE_SHA`, `REVIEWED_HEAD_SHA` (the reviewed input), the **report SHA** (the report commit), and the **fix SHA** (the fix commit). Any push while a round is running invalidates it — re-freeze and re-run.

**Round 1 (concurrent).** On the frozen `REVIEWED_HEAD_SHA`, start Codex round 1 as a background task, then run the internal review in-session while it executes; nothing writes to the tree until both return, and you commit afterward.

- **Internal review** — invoke `INTERNAL_CHECK` with the Skill tool and follow it in this session: spawn its reviewer agents directly — no nested review-lead subagent — and consolidate the findings yourself (reviewers never post or mutate, `gh` reads only — the command encodes draft-PR acceptance and the read-only rules). Post the findings verbatim as `<!-- report:code-review -->` stating `REVIEWED_HEAD_SHA`.
- **Codex round 1** — `codex exec` with `CROSS_CHECK` on the same SHA, injecting the `Review packet`. Read the verdict from the file, not stdout: `grep -E '^### Round [0-9]+ — Verdict: (approved|changes-requested)$' specs/<name>/reviews/codex-impl-review-round-1.md` — a round that writes no verdict is re-run, never treated as approval. Post the file as `<!-- report:codex-round-1 -->`.

**Both clean** — Codex `approved` AND internal review returns zero findings → commit the round-1 Codex report (`Refs #N`); that **report commit is the approved head**. Skip round 2, mark Fixes and Codex R2 delta n/a → **Ready**.

**Otherwise** → merge the two finding sets (dedup by root cause, keep source IDs), make the **report commit** (the round-1 report file), then run ONE combined fix pass over both reports' blockers: cluster the merged blockers by root cause + touched files, run disjoint clusters as parallel background fixer subagents in the same worktree and sequence overlapping clusters, and after all fixers return make exactly **ONE fix commit** (`Refs #N`, never amend) — pushed with the report commit in one push. Tick **Fixes** with the fix SHA, then run the Codex R2 delta.

**Codex R2 delta.** Re-freeze, then `codex exec` with `CROSS_CHECK` reviewing only the fix delta `<prior-reviewed-head>..<head>` **excluding** `specs/<name>/reviews/`, dispositioning findings from BOTH round-1 reports; inject the `Review packet`. Read and post the verdict as `<!-- report:codex-round-2 -->` (as above).

- **`approved`** → commit the round-2 report (`Refs #N`); that **report commit is the approved head**. Verify the PR head equals it and tick **Codex R2 delta**.
- **`changes-requested`** → round 2 is the last automatic round → the **Escalation ladder**.

**Advisories** (any round) never spawn an in-build round and get no per-advisory AskUserQuestion — record each in the PR body's `## Follow-ups` checklist to feed a future plan.

## Escalation ladder

Runs when `MAX_CROSS_CHECK_ROUNDS` is reached and the round is still `changes-requested`. Identical retries are forbidden: every further attempt must change the fixer, the approach, or the question — never re-run the same fixer tier on the same blocker.

First **classify** each open blocker. One tagged `spec-defect` in the Codex report — or matching its triggers: conflicting acceptance criteria or locked decisions, an ambiguous or untestable requirement, a fix that requires changing a locked decision or non-goal, a Validation Command testing the wrong behavior, or a dispute about what is *required* rather than what the code *does* — goes straight to **E3** as a plan problem; never burn fixers on it.

Then STOP and present ONE AskUserQuestion — why the round failed, each open blocker's disposition history, and the un-run stages as options (recommend the earliest eligible):

- **E1 — escalated fix round** (eligible only while a failed attempt sat below the top tier): route each open blocker to a **fresh-context** fixer at a strictly higher model/effort (ceiling `opus` + `max`), briefed with the blocker's repair contract plus every prior attempt and why it failed, and required to state a materially different repair hypothesis before editing. Then one more Codex delta round.
- **E2 — role swap**: Codex fixes the remaining blockers itself — a `Codex co-development` writer invocation scoped to exactly those blockers, model/effort from the AGENTS.md Codex table (persistent blockers → `gpt-5.6-sol` + `max`), briefed with each finding's ID and disposition history, the violated criterion or invariant, the exact repro command with observed vs expected output, the minimal failing case, prior patches and why each failed, and the report's fix direction. Gate: `INTERNAL_CHECK` on the Codex delta returns zero blocking findings AND all Validation Commands pass — Codex never reviews its own fix; that clean internal pass is the approval, recorded as `approved (role-swap)` with the fix commit as the approved head and the internal report comment as Evidence.
- **E3 — stop looping**: exit `spec-defect` (the blocker needs a plan amendment — hand back to `/harness-layer:harness-plan`) or `needs-human` (irreducible disagreement). Both: add the label (`gh issue edit <N> --add-label status:needs-human`) and post the **disagreement summary** as an issue comment linking the PR and its latest `<!-- report:codex-round-N -->` comment — shared facts, reviewer position, fixer position, the exact spec text at issue, evidence for each, attempted fixes, and the smallest user decision that unblocks.
- **`accepted-with-unverified-fixes`** — escape hatch, allowed ONLY when the remaining blockers are non-severe and mechanically verifiable, the plan's Validation Commands pass after the fixes, and the user explicitly picks it.

Ladder rules: each stage runs at most once, in order. A new Codex round requires a new fix SHA carrying a material blocker-related delta — unchanged code never consumes a round. `MAX_TOTAL_ROUNDS` is absolute: at the ceiling only E3 (or the escape hatch) remains.

The user's selection is final. Record the chosen exit status — `approved` | `approved (role-swap)` | `accepted-with-unverified-fixes` | `spec-defect` | `needs-human` — in the PR. When a later round reaches `approved` after a `needs-human` escalation, remove the label (`gh issue edit <N> --remove-label status:needs-human`). Do NOT present the success `Report` on `spec-defect` or `needs-human`.

## Review packet

Inject into every `codex exec` prompt: `BASE_SHA`, `REVIEWED_HEAD_SHA`, the round `N`; for `N>1` the prior reviewed head and prior finding IDs; a clean-tree attestation; the `git diff --numstat` and `--name-status` summary; `REVIEW_PROFILE`; the internal-review findings for dedup (`N>1`; on round 1 note they run concurrently); validation results keyed to the frozen SHA; a KB claim map (claim → `ai-docs/` path → excerpt → fetched date) when `REVIEW_PROFILE` is `kb-grounded`; and your EXPECTED lens list — Codex re-verifies lens selection independently and reports disagreement. Select the Codex model and reasoning effort per round from the AGENTS.md Codex table based on the round's scope (full review vs fix delta) — never hardcoded, quality-first: a round-1 review touching security, harness core, migrations, concurrency, or >20 files runs `gpt-5.6-sol` + `high` minimum; multiple such signals → `xhigh`.

`codex exec -C "<worktree root>" -s workspace-write --model <codex-model> -c model_reasoning_effort="<effort>" "Use the implementation-review skill for round <N> of the plan at specs/<name>/spec.md. <Review packet>. Round 1 is a full risk-tiered review; round 2 reviews only the delta <prior-reviewed-head>..<head> excluding specs/<name>/reviews/. Run its Validation Commands, write your verdict to specs/<name>/reviews/codex-impl-review-round-<N>.md, and return only the terse summary."`

## PR body

Seed at creation and keep current with `gh pr edit --body-file`:

- `## Plan` — blob URLs on the convention branch `<type>/<N>-<slug>` to `spec.md`, `tasks.md`, `decisions.md`, `acceptance-criteria.md`, and the `reviews/` folder, plus `Closes #N`.
- **Stage table** — the `STAGES` rows, each ticked with a pushed SHA or comment URL as Evidence.
- **Agent Task Manifest** — `task | owner | done | verification | notes`, folded from builder hand-offs.
- `## Review Reports` — one entry per report comment, replaced with its comment URL as it posts.
- `## Follow-ups` — the advisory checklist for a future plan; record the final exit status here on `accepted-with-unverified-fixes` / `needs-human`.

## Report

After the build passes both gates and the PR is ready, provide a concise report:

```text
✅ Build Complete

Plan: specs/<name>/
Issue: #<N>
PR: #<M> (ready) @ <approved-sha>
Branch: <type>/<N>-<slug>
Stages: Implementation ✓ Tidy ✓ R1 reviews ✓ Fixes ✓ Codex R2 delta ✓ Ready ✓
Round 1: <both clean | internal N fixed / Codex changes-requested>
Codex cross-check: <approved at round N | approved (role-swap) | accepted-with-unverified-fixes>
KB grounding: <docs checked, contradictions fixed — kb-grounded only>

Implemented:
- <what shipped, concise>

Next: /harness-layer:harness-ship <slug>.
```
