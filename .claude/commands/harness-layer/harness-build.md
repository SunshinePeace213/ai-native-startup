---
description: Implement a saved plan on its worktree via a draft PR, then verify it with a single Codex cross-check gate on packet-carried input — ≤2 rounds
argument-hint: [name-or-path-of-plan]
model: fable
---

# Harness Build

Follow the `Workflow` to implement the plan at `PATH_TO_PLAN` — application code or harness work, one universal path — on the worktree `/harness-layer:harness-plan` created for it, drive it through a draft PR, and verify it with a single Codex cross-check gate reading the packet input you prepare, bounded to `MAX_CROSS_CHECK_ROUNDS` rounds; finish by marking the PR ready and reporting. The KB-grounding steps run only when the plan's `Review profile` is `kb-grounded`.

## Variables

PATH_TO_PLAN: $ARGUMENTS — a plan name (resolves to `specs/<name>/`) or a path to its spec folder
REVIEW_PROFILE: `kb-grounded` | `standard`, read from `spec.md`'s `## Tracking` — gates the KB-grounding pass and the KB claim map
KNOWLEDGE_BASE: `ai-docs/` — cached official docs (catalog `ai-docs/index.md`), consulted only under `kb-grounded`
ISSUE_NUMBER: the GitHub issue `#N` read from `spec.md`'s `## Tracking` — the join key for `Closes #N`, commit footer `Refs #N`, and the `status:needs-human` escalation. Absent → Preflight STOP.
PR_NUMBER: the draft PR `#M` opened at the Open-the-draft-PR step and recorded back into `## Tracking`.
STAGES: the PR stage-table rows, ticked live as phases land — Implementation → Tidy → Codex R1 → Fixes → Codex R2 delta → Ready.
MAX_CROSS_CHECK_ROUNDS: `2` — hard cap on Codex rounds; EVERY `codex exec` invocation counts, advisory-induced included.
ROUND_INPUT: `specs/<name>/reviews/round-N-input/` — the per-round review input you prepare at freeze (`N` = round number); the contract for its files is in `Verification`.
CROSS_CHECK: `implementation-review` — the Codex cross-check skill, run via `codex exec`; the sole review gate.
HARNESS_SIMPLIFIER: `harness-simplifier` — internal-tidy subagent for harness/prompt files (`.claude/**`, `.agents/**`), deployed on `opus`
CODE_SIMPLIFIER: `code-simplifier` — internal-tidy subagent for application code (Python, TS/Next.js/React), deployed on `opus`
REQUIRED_PLUGINS: `codex@openai-codex`

## Instructions

- If no `PATH_TO_PLAN` is provided, STOP immediately and ask the user for it (AskUserQuestion).
- You are the **build lead**: you orchestrate, you do not review your own work, and you never edit files directly — with ONE narrow exception for non-implementation plan files: you create and fold `specs/<name>/implementation-notes.md`, author `specs/<name>/artifacts/ship-brief.html` in the approving round, and make the `## Tracking` / `## Locked Boundaries` ledger edits; implementation files stay builder-only. `CROSS_CHECK` (Codex) is the single read-only gate — it only reports findings, runs zero git and zero shell, and judges the input **you** prepare under `ROUND_INPUT`. YOU route every fix to a fixer subagent, picking its **model** per issue difficulty from `.claude/rules/model-selection.md` (a blocker whose earlier fix failed a round escalates a tier — never the same tier twice) and passing it via the Agent tool's `model` param; the model-selection effort tier goes in that fixer's task brief as depth guidance, since subagents inherit the session's reasoning effort. You own every `git` / `gh` call — the PR and every freeze, diff, and validation command.
- Build on the plan's existing worktree, never on `main`. Commit **and push** a checkpoint after each phase — conventional and trailer-free per `.claude/rules/git-workflow.md`, each carrying the footer `Refs #N`. An unpushed SHA cannot be linked, so every stage-table Evidence entry must be a pushed commit SHA (GitHub auto-links it) or a report-comment URL. Always push with the explicit refspec `git push origin HEAD:refs/heads/<type>/<N>-<slug>` — from the local `worktree-<slug>` branch a bare `git push` refuses (upstream name mismatch) — and check the push's exit status directly; piping it into another command hides the failure.
- **Under `kb-grounded`**, when implementing or fixing, check behavior claims (frontmatter fields, hook events, model aliases, command resolution) against the `KNOWLEDGE_BASE` docs listed in `decisions.md`'s `## KB References` — don't work from memory. Under `standard`, skip the KB checks.
- **Drive the build through a draft PR.** Once the tidy checkpoint is pushed, open the draft PR and keep its body — the `## Plan` links, stage table, and Agent Task Manifest — current with `gh pr edit --body-file` as each phase lands.
- **Post each report as an idempotent PR comment.** Tidy and every Codex round each get ONE comment keyed by a stable first-line marker — `<!-- report:tidy -->`, `<!-- report:codex-round-N -->`. Upsert it: list comments with `gh api --paginate repos/{owner}/{repo}/issues/<PR>/comments` and search for the marker; if found, update with `gh api --method PATCH repos/{owner}/{repo}/issues/comments/<comment-id> -F body=@<file>`; else create with `gh pr comment <PR> --body-file <file>`. Always write the body to a file first — never inline a body into the shell (`gh api` has no `--body-file`; file-backed `-F body=@<file>` is the update path). Every comment states the reviewed head SHA. As each report posts, replace its entry in the PR body's `## Review Reports` list with the comment URL.
- **Each builder hands off in its final message**: task ID, status, changed files, exact verification commands + observed results, **deviations from the plan** (what diverged, what forced it, the call made — "none" allowed), and notes/blockers. Fold these into the PR body's Agent Task Manifest table (`task | owner | done | verification | notes`), keying the task column by the plan's kebab-case Task ID — never `#N`, which GitHub autolinks to unrelated issues/PRs. Builders post no PR comments of their own.
- **Deviation log.** Fold each reported deviation into `specs/<name>/implementation-notes.md` at the next checkpoint commit, and publish it as the Deviations board per `.claude/rules/harness-layer/artifacts.md`, linked from the PR body. A deviation touching a locked decision or acceptance criterion STOPS for explicit user approval (AskUserQuestion) before work proceeds.

## Workflow

1. **Preflight** — Verify the reused tools, `gh` auth, and that the plan carries an Issue `#N`; STOP with guidance on any failure (see `Preflight`).
2. **Enter the worktree** — Resolve `PATH_TO_PLAN` to the spec folder, read `spec.md`'s `## Tracking` for its worktree path, Issue `#N`, and `Review profile`, and work there. If the worktree is gone, restore it from the plan's branch before building.
3. **Read the plan** — Read `spec.md`, `tasks.md`, `decisions.md`, and `acceptance-criteria.md` in full — plus the `## KB References` docs under `kb-grounded`. Think hard about the approach before touching files.
4. **Implement** — Create `specs/<name>/implementation-notes.md` from `specs/_templates/implementation-notes.md` first. Then deploy the team members named in `tasks.md` (or `general-purpose`) per `.claude/rules/task-tools.md`, each on the model and effort its task stamps in the plan: launch all currently-unblocked, file-disjoint tasks concurrently as background agents, letting `tasks.md` keep owning the dependency structure. Commit+push each checkpoint (`Refs #N`) and collect every builder's hand-off.
5. **Internal tidy** — Deploy `HARNESS_SIMPLIFIER` (`opus`) for the harness/prompt files the build touched and `CODE_SIMPLIFIER` (`opus`) for the application code it touched (both when a build spans both). Behavior-preserving only; commit+push. **Hold** their one tidy report until the PR exists.
6. **Open the draft PR** — After the tidy checkpoint is pushed: `gh pr create --draft --assignee $(gh api user -q .login) --title "<emoji> <type>(<scope>): <desc>"` with a `--body-file` filled from `.github/PULL_REQUEST_TEMPLATE/<type>.md` (fill it yourself — do NOT use `--template`, which reads the default branch). Mirror onto the PR the linked issue's type label and its `priority:P<n>` label, read via `gh issue view <N> --json labels`. Seed the body per `PR body`, record `PR #M` in `## Tracking`, and commit+push that Tracking edit (`Refs #N`) — an uncommitted Tracking line leaves `main` pointing at no PR after merge. Post the held tidy report as `<!-- report:tidy -->`, then tick **Implementation** and **Tidy** together.
7. **Codex R1** — Freeze, prepare `ROUND_INPUT`, and run Codex round 1 per `Verification`. Tick **Codex R1**.
8. **Fixes & Codex R2 delta** — When R1 is `changes-requested`, fix the blockers in one commit and run the bounded Codex R2 delta; a round-2 `changes-requested` hits the over-cap gate. Tick **Fixes** and **Codex R2 delta**. See `Verification`.
9. **Finish & report** — On approval, verify the PR head equals the approved SHA; for medium/complex plans, publish the ship brief best-effort via the Artifact tool from `specs/<name>/artifacts/ship-brief.html` (on failure keep the file and note "publish skipped" — never block) and record the `## Ship Brief` entry in the PR body (simple plans have no brief — skip straight on); tick **Ready**, run `gh pr ready`, and follow the `Report`.

## Preflight

Before any work, verify the tools this build reuses. STOP on the first failure and tell the user how to fix it — never proceed degraded.

- **Codex CLI** — `command -v codex`. Missing → STOP: install the Codex CLI, then run `/codex:setup`.
- **Required plugins** — confirm `REQUIRED_PLUGINS` is installed (`grep -q '"codex@openai-codex"' ~/.claude/plugins/installed_plugins.json`). Missing → STOP: add its marketplace and `/plugin install codex@openai-codex` (from `openai/codex-plugin-cc`), then re-run.
- **GitHub CLI** — `gh auth status`. The build always pushes and opens a PR, so `gh` is required, not optional. Missing / unauthenticated → STOP: run `gh auth login`.
- **Issue number** — `spec.md`'s `## Tracking` names an Issue `#N`. Absent → STOP: the PR needs `Closes #N` and commits need `Refs #N`; file the issue and record it in `## Tracking` first.

## Verification

One read-only gate verifies the build — Codex (cross-model), bounded to `MAX_CROSS_CHECK_ROUNDS` rounds. Codex only reports; YOU prepare its input, apply every fix, commit, and post the report comment.

**Freeze & prepare.** Ensure a clean tree, then snapshot `BASE_SHA=$(git merge-base origin/main HEAD)` and `REVIEWED_HEAD_SHA=$(git rev-parse HEAD)`, and write `ROUND_INPUT` (`round-N-input/`) per the `Review packet` contract:

- `diff.patch` / `numstat.txt` / `name-status.txt` — the round's `git diff` (+ `--numstat` / `--name-status`) over `BASE_SHA..REVIEWED_HEAD_SHA` (round 1) or `<prior-reviewed-head>..REVIEWED_HEAD_SHA` **excluding** `specs/<name>/reviews/` and `specs/<name>/artifacts/` (round N>1).
- `validation.md` — one line per plan Validation Command: exact command → PASS/FAIL keyed to `REVIEWED_HEAD_SHA`, with a trimmed excerpt (last ~20 lines) on FAIL. Run each command ONCE at this freeze and capture its real output — **never fabricate a result**. On round N>1 re-run only commands that failed last round or whose inputs changed; record every other as a carry-forward skip with its reason.
- `history-brief.md` — medium/complex plans only: a git blame/log summary of the hot files from one `haiku` utility agent. Absent for simple plans.

A round tracks `BASE_SHA`, `REVIEWED_HEAD_SHA`, the **report SHA**, and the **fix SHA**. Any push while a round runs invalidates it — re-freeze and re-run.

**Run the round.** Launch `codex exec` with `CROSS_CHECK` as a background task, injecting the `Review packet`; pick the Codex model and reasoning effort for the round from `.claude/rules/model-selection.md` by scope (full review vs fix delta) — never hardcoded. While it runs, update the PR body / stage table and pre-stage the fixer briefs. Read the verdict FROM THE REPORT FILE, not stdout: `grep -E '^### Round [0-9]+ — Verdict: (approved|changes-requested)$' specs/<name>/reviews/codex-impl-review-round-N.md` — a round that writes no verdict is re-run, never treated as approval. Post the report as `<!-- report:codex-round-N -->` stating `REVIEWED_HEAD_SHA`, then remove the round-input dir (`mv` to trash, never `rm -rf`).

**Approved (any round) → Approval finalization.** For medium/complex plans, author `specs/<name>/artifacts/ship-brief.html` FRESH after reading the `approved` verdict and BEFORE committing — it leads with what shipped, pre-answers reviewer objections with evidence links (report comments, validation results), and ends in a 3–6 question quiz whose wrong answers point at the file/section to re-read; never reuse a brief from a failed round. Then stage that round's report plus the brief as ONE commit (`Refs #N`) — that **report commit is the approved head** recorded in the stage table. Simple plans skip the brief and quiz; the report commit alone is the approved head. A **round-1** approval ticks **Codex R1**, marks **Fixes** and **Codex R2 delta** n/a → **Ready**.

**Changes-requested → fix & re-review.** Make the **report commit** (the round's report file), then apply the `Fix-design consult` and `Root-cause rule` below and run ONE fix pass: cluster the blockers by root cause + touched files (assign each root cause a stable ID that persists across rounds — the `Root-cause rule` keys on it, so a surviving cause is never renamed or reclustered), run disjoint clusters as parallel background fixer subagents in the same worktree and sequence overlapping ones, and after all fixers return make exactly **ONE fix commit** (`Refs #N`, never amend) — pushed with the report commit in one push. Tick **Fixes** with the fix SHA, then run the **Codex R2 delta**: re-freeze and prepare `round-2-input/` over `<prior-reviewed-head>..HEAD` **excluding** `specs/<name>/reviews/` and `specs/<name>/artifacts/`; the round dispositions every prior blocker.

- **`approved`** → run `Approval finalization` on the round-2 report; verify the PR head equals it and tick **Codex R2 delta**.
- **`changes-requested`** → round 2 is the last automatic round → the **Over-cap gate**.

**Fix-design consult.** Before any fixer runs, when any blocker is design-shaped — a security boundary, parser/matcher semantics, an algorithm, architecture — agree the fix APPROACH with Codex: one read-only `codex exec` (default `medium` effort; `high`/`xhigh` when it establishes new boundaries or claims soundness) listing, per blocker, the intended approach, invariants, and tests. Fold Codex's adjustments in, and record every negotiated allow/deny boundary, approved threshold, or excluded adversarial class in `specs/<name>/decisions.md` `## Locked Boundaries` — written before fixers run, shipped in the fix commit. A boundary that weakens an acceptance criterion or excludes a previously in-scope adversarial class needs explicit user approval (AskUserQuestion) before it is recorded. Reviews judge against that ledger, never re-litigating a locked boundary. Skip the consult when every blocker is mechanical.

**Root-cause rule.** A root cause that has already survived one fix round is NEVER patched again — witness-by-witness patching of a heuristic does not converge. Choose instead: an architectural redesign, a provably-conservative behavior (e.g. deny-by-default), or renegotiating the acceptance criterion with the user (AskUserQuestion). Route a redesign to an `opus` fixer, or reassign it to Codex `gpt-5.6-sol` when the work is adversarial or algorithmic; a Codex-authored fix delta must first pass an internal Claude review (`opus`) — its blockers are fixed and folded into the fix commit BEFORE the Codex delta round runs, so Codex never solely gates its own code — and its authorship is recorded in the Agent Task Manifest.

**Advisories** (any round) never spawn an in-build round and get no per-advisory AskUserQuestion — record each in the PR body's `## Follow-ups` checklist to feed a future plan.

**Over-cap gate** — `MAX_CROSS_CHECK_ROUNDS` reached and round 2 still `changes-requested` → STOP and present ONE AskUserQuestion covering why a further round is needed, what it would do, and the next steps per option:

- (a) **one redesigned round 3** — allowed ONCE, and only for a redesign-level fix under the `Root-cause rule` (never another patch of a surviving root cause): run the `Fix-design consult`, apply the redesign, re-freeze, and review the new delta; an approved round 3 finalizes per `Approval finalization`. Round 3 is the LAST review round — if it is still `changes-requested`, re-present this gate WITHOUT this option.
- (b) **`accepted-with-unverified-fixes`** — allowed ONLY when the remaining blockers are non-severe and mechanically verifiable, the plan's Validation Commands pass after the fixes, and the user explicitly picks it.
- (c) **`needs-human`** — add the label (`gh issue edit <N> --add-label status:needs-human`) and post an issue comment naming the blockers with a link to the PR and its latest `<!-- report:codex-round-N -->` comment.

The user's selection is final. Record the chosen exit status — `approved` | `accepted-with-unverified-fixes` | `needs-human` — in the PR before the build ends; a PR must never merge or stop with no recorded exit status. When a later round reaches `approved` after a `needs-human` escalation, remove the label (`gh issue edit <N> --remove-label status:needs-human`). Do NOT present the success `Report` on `needs-human`.

## Review packet

Inject into every `codex exec` prompt: `BASE_SHA`, `REVIEWED_HEAD_SHA`, the round `N`, `REVIEW_PROFILE`, the `ROUND_INPUT` directory path, and your EXPECTED lens list — Codex re-verifies lens selection independently and reports disagreement; a clean-tree attestation naming `round-N-input/` as the only allowed untracked path; a KB claim map (claim → `ai-docs/` path → excerpt → fetched date) when `REVIEW_PROFILE` is `kb-grounded`; and for `N>1` the prior reviewed head, prior finding IDs, the fix delta's author (`claude` or `codex`, keyed to the implementation code — lead-authored report/ledger edits don't count), plus pointers to `decisions.md` `## Locked Boundaries` and `specs/<name>/implementation-notes.md` when they exist. Codex runs ZERO git and ZERO build/test/shell commands: it reads the packet, the round-input files, the plan files (round 1), the `.codex/agents/*.toml` lens definitions, and — under KB grounding — `ai-docs/`, then judges and writes exactly ONE file, `specs/<name>/reviews/codex-impl-review-round-N.md`; the `-s workspace-write` grant exists solely for that report. Round-input files are ephemeral — never committed; remove the input dir after the report posts. Select the Codex model and reasoning effort per round from `.claude/rules/model-selection.md` by scope (full review vs fix delta) — never hardcoded.

`codex exec -C "<worktree root>" -s workspace-write --model <codex-model> -c model_reasoning_effort="<effort>" "Use the implementation-review skill for round <N> of the plan at specs/<name>/spec.md. <Review packet>. Round 1 is a full review of the range in round-1-input/; round N>1 reviews only the delta in round-N-input/. Judge the validation results in validation.md, write your verdict to specs/<name>/reviews/codex-impl-review-round-<N>.md, and return only the terse summary."`

## PR body

Seed at creation and keep current with `gh pr edit --body-file`:

- `## Plan` — blob URLs on the convention branch `<type>/<N>-<slug>` to `spec.md`, `tasks.md`, `decisions.md`, `acceptance-criteria.md`, and the `reviews/` folder, plus `Closes #N`.
- **Stage table** — the `STAGES` rows, each ticked with a pushed SHA or comment URL as Evidence.
- **Agent Task Manifest** — `task | owner | done | verification | notes`, folded from builder hand-offs.
- `## Review Reports` — one entry per report comment (the tidy comment and each `<!-- report:codex-round-N -->`), replaced with its comment URL as it posts.
- `## Ship Brief` — the brief's file path + published URL (or "publish skipped"); medium/complex builds only.
- `## Follow-ups` — the advisory checklist for a future plan; record the final exit status here on `accepted-with-unverified-fixes` / `needs-human`.

## Report

After the build passes the Codex gate and the PR is ready, provide a concise report:

```text
✅ Build Complete

Plan: specs/<name>/
Issue: #<N>
PR: #<M> (ready) @ <approved-sha>
Branch: <type>/<N>-<slug>
Stages: Implementation ✓ Tidy ✓ Codex R1 ✓ Fixes ✓ Codex R2 delta ✓ Ready ✓
Codex R1: <approved | changes-requested (N blockers fixed)>
Codex cross-check: <approved at round N | accepted-with-unverified-fixes | needs-human>
KB grounding: <docs checked, contradictions fixed — kb-grounded only>
Ship brief: <artifacts/ship-brief.html + published URL | publish skipped | n/a — simple plan>

Implemented:
- <what shipped, concise>

Next: take the ship-brief quiz (medium/complex plans), then /harness-layer:harness-ship <slug>.
```
