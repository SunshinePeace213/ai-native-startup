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
MAX_CROSS_CHECK_ROUNDS: `2` — hard cap on Codex rounds; EVERY `codex exec` invocation counts, advisory-induced included.
INTERNAL_CHECK: `harness-layer:harness-review` — the internal review command, invoked in-session with the Skill tool (never via a nested review-lead subagent); you follow it yourself, spawning its reviewer agents directly and consolidating the findings.
CROSS_CHECK: `implementation-review` — the Codex cross-check skill, run via `codex exec`.
HARNESS_SIMPLIFIER: `harness-simplifier` — internal-tidy subagent for harness/prompt files (`.claude/**`, `.agents/**`), deployed on `opus`
CODE_SIMPLIFIER: `code-simplifier` — internal-tidy subagent for application code (Python, TS/Next.js/React), deployed on `opus`
REQUIRED_PLUGINS: `codex@openai-codex`

## Instructions

- If no `PATH_TO_PLAN` is provided, STOP immediately and ask the user for it (AskUserQuestion).
- You are the **build lead**: you orchestrate, you do not review your own work, and you never edit files directly — with ONE narrow exception for non-implementation plan files: you create and fold `specs/<name>/implementation-notes.md`, author `specs/<name>/artifacts/ship-brief.html` in the approving round, and make the `## Tracking` / `## Locked Boundaries` ledger edits; implementation files stay builder-only. The reviewers (`INTERNAL_CHECK`, `CROSS_CHECK`) are read-only and only report findings — YOU route every fix to a fixer subagent, picking its **model** per issue difficulty from the AGENTS.md table and selection principle (`opus` for complex, security, or algorithmic blockers / `sonnet` standard; a blocker whose earlier fix failed a round escalates a tier — never the same tier twice) and passing it via the Agent tool's `model` param; the AGENTS.md effort tier goes in that fixer's task brief as depth guidance, since subagents inherit the session's reasoning effort. You own every `git` / `gh` call, including the PR.
- Build on the plan's existing worktree, never on `main`. Commit **and push** a checkpoint after each phase — conventional and trailer-free per `GIT-COMMIT-PR-MESSAGE.md`, each carrying the footer `Refs #N`. An unpushed SHA cannot be linked, so every stage-table Evidence entry must be a pushed commit SHA (GitHub auto-links it) or a report-comment URL. Always push with the explicit refspec `git push origin HEAD:refs/heads/<type>/<N>-<slug>` — from the local `worktree-<slug>` branch a bare `git push` refuses (upstream name mismatch) — and check the push's exit status directly; piping it into another command hides the failure.
- **Under `kb-grounded`**, when implementing or fixing, check behavior claims (frontmatter fields, hook events, model aliases, command resolution) against the `KNOWLEDGE_BASE` docs listed in `decisions.md`'s `## KB References` — don't work from memory. Under `standard`, skip the KB checks.
- **Drive the build through a draft PR.** Once the first checkpoint is pushed, open the draft PR and keep its body — the `## Plan` links, stage table, and Agent Task Manifest — current with `gh pr edit --body-file` as each phase lands.
- **Post each report as an idempotent PR comment.** Tidy, internal review, and every Codex round each get ONE comment keyed by a stable first-line marker — `<!-- report:tidy -->`, `<!-- report:code-review -->`, `<!-- report:codex-round-N -->`. Upsert it: list comments with `gh api --paginate repos/{owner}/{repo}/issues/<PR>/comments` and search for the marker; if found, update with `gh api --method PATCH repos/{owner}/{repo}/issues/comments/<comment-id> -F body=@<file>`; else create with `gh pr comment <PR> --body-file <file>`. Always write the body to a file first — never inline a body into the shell (`gh api` has no `--body-file`; file-backed `-F body=@<file>` is the update path). Every review comment states the reviewed head SHA. As each report posts, replace its entry in the PR body's `## Review Reports` list with the comment URL.
- **Each builder hands off in its final message**: task ID, status, changed files, exact verification commands + observed results, **deviations from the plan** (what diverged, what forced it, the call made — "none" allowed), and notes/blockers. Fold these into the PR body's Agent Task Manifest table (`task | owner | done | verification | notes`), keying the task column by the plan's kebab-case Task ID — never `#N`, which GitHub autolinks to unrelated issues/PRs. Builders post no PR comments of their own.
- **Deviation log.** Fold each reported deviation into `specs/<name>/implementation-notes.md` at the next checkpoint commit. A deviation touching a locked decision or acceptance criterion STOPS for explicit user approval (AskUserQuestion) before work proceeds.

## Workflow

1. **Preflight** — Verify the reused tools, `gh` auth, and that the plan carries an Issue `#N`; STOP with guidance on any failure (see `Preflight`).
2. **Enter the worktree** — Resolve `PATH_TO_PLAN` to the spec folder, read `spec.md`'s `## Tracking` for its worktree path, Issue `#N`, and `Review profile`, and work there. If the worktree is gone, restore it from the plan's branch before building.
3. **Read the plan** — Read `spec.md`, `tasks.md`, `decisions.md`, and `acceptance-criteria.md` in full — plus the `## KB References` docs under `kb-grounded`. Think hard about the approach before touching files.
4. **Implement** — Create `specs/<name>/implementation-notes.md` from `specs/_templates/implementation-notes.md` first. Then deploy the team members named in `tasks.md` (or `general-purpose`) per `.claude/rules/task-tools.md`, each on the model and effort its task stamps in the plan: launch all currently-unblocked, file-disjoint tasks concurrently as background agents, letting `tasks.md` keep owning the dependency structure. Commit+push each checkpoint (`Refs #N`) and collect every builder's hand-off.
5. **Open the draft PR** — After the first checkpoint is pushed: `gh pr create --draft --assignee $(gh api user -q .login) --title "<emoji> <type>(<scope>): <desc>"` with a `--body-file` filled from `.github/PULL_REQUEST_TEMPLATE/<type>.md` (fill it yourself — do NOT use `--template`, which reads the default branch). Mirror onto the PR the linked issue's type label and its `priority:P<n>` label, read via `gh issue view <N> --json labels`. Seed the body per `PR body`, tick **Implementation**, record `PR #M` in `## Tracking`, and commit+push that Tracking edit (`Refs #N`) — an uncommitted Tracking line leaves `main` pointing at no PR after merge.
6. **Internal tidy** — Deploy `HARNESS_SIMPLIFIER` on `opus` for the harness/prompt files the build touched; deploy `CODE_SIMPLIFIER` (also `opus`) for the application code it touched (both when a build spans both). Behavior-preserving only. Post their one report as `<!-- report:tidy -->`, commit+push, tick **Tidy**.
7. **Concurrent R1 review** — Freeze the SHA, start Codex round 1 in the background and run `INTERNAL_CHECK` in-session while it executes, then merge, report, fix, and push per `Verification`. Tick **R1 reviews (internal ∥ Codex)**.
8. **Codex R2 delta** — When R1 is not a clean pass, Codex reviews the fix delta and dispositions both reports, bounded by `MAX_CROSS_CHECK_ROUNDS`; a round-2 `changes-requested` hits the over-cap gate. Tick **Fixes** and **Codex R2 delta**. See `Verification`.
9. **Finish & report** — On approval, verify the PR head equals the approved SHA; for medium/complex plans, publish the ship brief best-effort via the Artifact tool from `specs/<name>/artifacts/ship-brief.html` (on failure keep the file and note "publish skipped" — never block) and record the `## Ship Brief` entry in the PR body (simple plans have no brief — skip straight on); tick **Ready**, run `gh pr ready`, and follow the `Report`.

## Preflight

Before any work, verify the tools this build reuses. STOP on the first failure and tell the user how to fix it — never proceed degraded.

- **Codex CLI** — `command -v codex`. Missing → STOP: install the Codex CLI, then run `/codex:setup`.
- **Required plugins** — confirm `REQUIRED_PLUGINS` is installed (`grep -q '"codex@openai-codex"' ~/.claude/plugins/installed_plugins.json`). Missing → STOP: add its marketplace and `/plugin install codex@openai-codex` (from `openai/codex-plugin-cc`), then re-run.
- **GitHub CLI** — `gh auth status`. The build always pushes and opens a PR, so `gh` is required, not optional. Missing / unauthenticated → STOP: run `gh auth login`.
- **Issue number** — `spec.md`'s `## Tracking` names an Issue `#N`. Absent → STOP: the PR needs `Closes #N` and commits need `Refs #N`; file the issue and record it in `## Tracking` first.

## Verification

Two read-only gates verify the build — internal (same model) and Codex (cross-model); YOU apply every fix, commit, and post the report comment. Round 1 runs both gates **concurrently**; a Codex round 2 delta follows only when round 1 is not a clean pass. Hard cap: `MAX_CROSS_CHECK_ROUNDS` Codex rounds.

**Freeze & tracked SHAs.** Ensure a clean tree, then snapshot `BASE_SHA=$(git merge-base origin/main HEAD)` and `REVIEWED_HEAD_SHA=$(git rev-parse HEAD)`. A round tracks four SHAs: `BASE_SHA`, `REVIEWED_HEAD_SHA` (the reviewed input), the **report SHA** (the report commit), and the **fix SHA** (the fix commit). Any push while a round is running invalidates it — re-freeze and re-run.

**Round 1 (concurrent).** On the frozen `REVIEWED_HEAD_SHA`, start Codex round 1 as a background task, then run the internal review in-session while it executes; nothing writes to the tree until both return, and you commit afterward.

- **Internal review** — invoke `INTERNAL_CHECK` with the Skill tool and follow it in this session: spawn its reviewer agents directly — no nested review-lead subagent — and consolidate the findings yourself (reviewers never post or mutate, `gh` reads only — the command encodes draft-PR acceptance and the read-only rules). Post the findings verbatim as `<!-- report:code-review -->` stating `REVIEWED_HEAD_SHA`.
- **Codex round 1** — `codex exec` with `CROSS_CHECK` on the same SHA, injecting the `Review packet`. Read the verdict from the file, not stdout: `grep -E '^### Round [0-9]+ — Verdict: (approved|changes-requested)$' specs/<name>/reviews/codex-impl-review-round-1.md` — a round that writes no verdict is re-run, never treated as approval. Post the file as `<!-- report:codex-round-1 -->`.

**Approval finalization.** In whichever round approves (round-1 both-clean, round-2 approved, or an approved round 3): for medium/complex plans, author `specs/<name>/artifacts/ship-brief.html` FRESH after reading the `approved` verdict and BEFORE committing — it leads with what shipped, pre-answers reviewer objections with evidence links (report comments, validation results), and ends in a 3–6 question quiz whose wrong answers point at the file/section to re-read; never reuse a brief from a failed round. Then stage that round's report plus the brief as ONE commit (`Refs #N`) — that **report commit is the approved head** recorded in the stage table. Simple plans skip the brief and quiz; the report commit alone is the approved head.

**Both clean** — Codex `approved` AND internal review returns zero findings → run `Approval finalization` on the round-1 Codex report; the resulting commit is the approved head. Skip round 2, mark Fixes and Codex R2 delta n/a → **Ready**.

**Otherwise** → merge the two finding sets (dedup by root cause, keep source IDs, and assign each root cause a stable ID that persists across rounds — the Root-cause rule keys on it, so a surviving cause is never renamed or reclustered), make the **report commit** (the round-1 report file), apply the **Fix-design consult** and **Root-cause rule** below, then run ONE combined fix pass over both reports' blockers: cluster the merged blockers by root cause + touched files, run disjoint clusters as parallel background fixer subagents in the same worktree and sequence overlapping clusters, and after all fixers return make exactly **ONE fix commit** (`Refs #N`, never amend) — pushed with the report commit in one push. Tick **Fixes** with the fix SHA, then run the Codex R2 delta.

**Fix-design consult.** Before any fixer runs, when any blocker is design-shaped — a security boundary, parser/matcher semantics, an algorithm, architecture — agree the fix APPROACH with Codex: one read-only `codex exec` (default `medium` effort; `high`/`xhigh` when it establishes new boundaries or claims soundness) listing, per blocker, the intended approach, invariants, and tests. Fold Codex's adjustments in, and record every negotiated allow/deny boundary, approved threshold, or excluded adversarial class in `specs/<name>/decisions.md` `## Locked Boundaries` — written before fixers run, shipped in the fix commit. A boundary that weakens an acceptance criterion or excludes a previously in-scope adversarial class needs explicit user approval (AskUserQuestion) before it is recorded. Reviews judge against that ledger, never re-litigating a locked boundary. Skip the consult when every blocker is mechanical.

**Root-cause rule.** A root cause that has already survived one fix round is NEVER patched again — witness-by-witness patching of a heuristic does not converge. Choose instead: an architectural redesign, a provably-conservative behavior (e.g. deny-by-default), or renegotiating the acceptance criterion with the user (AskUserQuestion). Route a redesign to an `opus` fixer, or reassign it to Codex `gpt-5.6-sol` when the work is adversarial or algorithmic; a Codex-authored fix delta must first pass an internal Claude review (`opus`) — its blockers are fixed and folded into the fix commit BEFORE the Codex delta round runs, so Codex never solely gates its own code — and its authorship is recorded in the Agent Task Manifest.

**Codex R2 delta.** Re-freeze, then `codex exec` with `CROSS_CHECK` reviewing only the fix delta `<prior-reviewed-head>..<head>` **excluding** `specs/<name>/reviews/` and `specs/<name>/artifacts/`, dispositioning findings from BOTH round-1 reports; inject the `Review packet`. Read and post the verdict as `<!-- report:codex-round-2 -->` (as above).

- **`approved`** → run `Approval finalization` on the round-2 report; the resulting commit is the approved head. Verify the PR head equals it and tick **Codex R2 delta**.
- **`changes-requested`** → round 2 is the last automatic round → the **Over-cap gate**.

**Advisories** (any round) never spawn an in-build round and get no per-advisory AskUserQuestion — record each in the PR body's `## Follow-ups` checklist to feed a future plan.

**Over-cap gate** — `MAX_CROSS_CHECK_ROUNDS` reached and round 2 still `changes-requested` → STOP and present ONE AskUserQuestion covering why a further round is needed, what it would do, and the next steps per option:

- (a) **one redesigned round 3** — allowed ONCE, and only for a redesign-level fix under the `Root-cause rule` (never another patch of a surviving root cause): run the `Fix-design consult`, apply the redesign, re-freeze, and review the new delta; an approved round 3 finalizes per `Approval finalization`. Round 3 is the LAST review round — if it is still `changes-requested`, re-present this gate WITHOUT this option.
- (b) **`accepted-with-unverified-fixes`** — allowed ONLY when the remaining blockers are non-severe and mechanically verifiable, the plan's Validation Commands pass after the fixes, and the user explicitly picks it.
- (c) **`needs-human`** — add the label (`gh issue edit <N> --add-label status:needs-human`) and post an issue comment naming the blockers with a link to the PR and its latest `<!-- report:codex-round-N -->` comment.

The user's selection is final. Record the chosen exit status — `approved` | `accepted-with-unverified-fixes` | `needs-human` — in the PR before the build ends; a PR must never merge or stop with no recorded exit status. When a later round reaches `approved` after a `needs-human` escalation, remove the label (`gh issue edit <N> --remove-label status:needs-human`). Do NOT present the success `Report` on `needs-human`.

## Review packet

Inject into every `codex exec` prompt: `BASE_SHA`, `REVIEWED_HEAD_SHA`, the round `N`; for `N>1` the prior reviewed head, prior finding IDs, the fix delta's author (`claude` or `codex`, keyed to the implementation code — lead-authored report/ledger edits don't count), and a pointer to `decisions.md` `## Locked Boundaries` when it exists; a pointer to `specs/<name>/implementation-notes.md` when it records deviations, so Codex dispositions them rather than rediscovering them; a clean-tree attestation; the `git diff --numstat` and `--name-status` summary; `REVIEW_PROFILE`; the internal-review findings for dedup (`N>1`; on round 1 note they run concurrently); validation results keyed to the frozen SHA; a KB claim map (claim → `ai-docs/` path → excerpt → fetched date) when `REVIEW_PROFILE` is `kb-grounded`; and your EXPECTED lens list — Codex re-verifies lens selection independently and reports disagreement. Select the Codex model and reasoning effort per round from the AGENTS.md Codex table based on the round's scope (full review vs fix delta) — never hardcoded.

`codex exec -C "<worktree root>" -s workspace-write --model <codex-model> -c model_reasoning_effort="<effort>" "Use the implementation-review skill for round <N> of the plan at specs/<name>/spec.md. <Review packet>. Round 1 is a full risk-tiered review; round 2 reviews only the delta <prior-reviewed-head>..<head> excluding specs/<name>/reviews/ and specs/<name>/artifacts/. Run its Validation Commands, write your verdict to specs/<name>/reviews/codex-impl-review-round-<N>.md, and return only the terse summary."`

## PR body

Seed at creation and keep current with `gh pr edit --body-file`:

- `## Plan` — blob URLs on the convention branch `<type>/<N>-<slug>` to `spec.md`, `tasks.md`, `decisions.md`, `acceptance-criteria.md`, and the `reviews/` folder, plus `Closes #N`.
- **Stage table** — the `STAGES` rows, each ticked with a pushed SHA or comment URL as Evidence.
- **Agent Task Manifest** — `task | owner | done | verification | notes`, folded from builder hand-offs.
- `## Review Reports` — one entry per report comment, replaced with its comment URL as it posts.
- `## Ship Brief` — the brief's file path + published URL (or "publish skipped"); medium/complex builds only.
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
Codex cross-check: <approved at round N | accepted-with-unverified-fixes | needs-human>
KB grounding: <docs checked, contradictions fixed — kb-grounded only>
Ship brief: <artifacts/ship-brief.html + published URL | publish skipped | n/a — simple plan>

Implemented:
- <what shipped, concise>

Next: take the ship-brief quiz (medium/complex plans), then /harness-layer:harness-ship <slug>.
```
