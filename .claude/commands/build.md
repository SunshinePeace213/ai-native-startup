---
description: Implement a saved plan. Pass a feature name (e.g. grilling-into-plan-w-team) to load its specs folder, or a direct path to a plan file.
argument-hint: [feature-name | path-to-plan]
---

# Build

Resolve `TARGET` to a plan, read the plan and its decision log, then follow the
`Workflow` to implement it and `Report` the completed work.

## Variables

TARGET: $ARGUMENTS

## Instructions

- If no `TARGET` is provided, STOP immediately and ask the user to provide it (AskUserQuestion).
- Resolve `TARGET` to a plan file (PLAN) and an optional decision log (DECISIONS), in order:
  1. If `specs/<TARGET>/plan.md` exists → PLAN = `specs/<TARGET>/plan.md`, DECISIONS = `specs/<TARGET>/decisions.md` (feature-name form).
  2. Else if `<TARGET>` is an existing file → PLAN = `<TARGET>`, DECISIONS = a `decisions.md` sibling in the same folder if present (direct path / legacy flat spec).
  3. Else STOP and report which paths were searched.

## Workflow

- If DECISIONS exists, read it first: it holds the requirements, locked decisions, assumptions, and out-of-scope items that constrain the build. Treat it as binding context.
- **Resume the shared worktree.** Read the `## Tracking` block from PLAN — `/plan-w-team` records there the issue number (or `none — gh unavailable`), the intended convention branch name (`<type>/<N>-<slug>`), and the worktree path. Resume that worktree with `EnterWorktree(path=<recorded path>)` and run the ENTIRE build inside it. The recorded **issue number is the single source of truth**; never re-derive it from the local branch (`EnterWorktree` mangles `feat/x` into `worktree-feat+x`). If PLAN has no `## Tracking` block (a legacy / local-only plan), build in the current working tree and treat the run as issue-less (see **PR Lifecycle Tracking → No-issue / graceful-skip fallback**).
- Read PLAN, think hard about it, and implement it into the codebase, honoring the decision log. If PLAN and DECISIONS conflict, STOP and surface the conflict instead of guessing.
- When implementation completes, open the tracking PR per **PR Lifecycle Tracking** (below), then run the **Codex Implementation Review Loop** (below) before reporting.

## PR Lifecycle Tracking

When implementation completes, surface the build as **one** GitHub PR opened from the recorded `## Tracking` block. Claude is the only actor that calls `gh`. The PR is opened **after** implementation and is tracked live through the Codex review phases below.

### Open the single PR (issue number present)

When `## Tracking` carries an issue number `#N`:

> **Handoff from `/plan-w-team`.** The convention branch `<type>/<N>-<slug>` ALREADY exists on `origin` carrying the plan commits (`/plan-w-team` created + pushed it). The push below adds the implementation commits ON TOP (a fast-forward) — `/build` MUST NOT create a second branch, and it opens exactly ONE PR (`Closes #N`) whose diff therefore includes BOTH the plan and the implementation. Any file path `/build` writes into the PR body or an issue comment MUST be an accessible GitHub URL (a blob URL on the head branch, or a commit-pinned permalink), NEVER a bare repo-relative path (those resolve against `main` and 404 pre-merge) — the same rule as the issue's "Link to plan".

1. **Push onto the pre-existing convention branch.** The branch already exists on `origin` with the plan commits, so this push fast-forwards the implementation commits onto it (do NOT create a new branch). The local worktree branch name is cosmetic, so the convention is enforced on the remote ref:

   ```
   git push -u origin HEAD:refs/heads/<type>/<N>-<slug>
   ```

   `<type>` / `<N>` / `<slug>` come from the recorded branch name in `## Tracking`.

2. **Open exactly ONE PR** with the type-matched template, mirroring the issue's metadata config:

   ```
   gh label create <type-label> --color … --description … --force   # ensure the label exists first (idempotent; build self-heals)
   gh pr create --template <type>.md --base main --head <type>/<N>-<slug> --assignee @me --label <type-label> --title "<emoji> <type>(<scope>): <description>"
   ```

   - `<emoji>` is the gitmoji for `<type>` (✨ feat, 🐛 fix, 📝 docs, 🎨 style, ♻️ refactor, ⚡️ perf, ✅ test, 🔧 chore) — e.g. `✨ feat(api): add login endpoint`.
   - **Mirror the issue's metadata on the PR.** Using the SAME `<type>`→label mapping as `/plan-w-team` (`feat→enhancement`, `fix→bug`, `docs→documentation`; `chore`/`refactor`/`perf`/`style`/`test` same-named), set `--assignee @me` + `--label <type-label>`. Create the type label on demand FIRST with the idempotent `gh label create <type-label> --color … --description … --force` so build self-heals a missing/deleted label. `epic` stays on the tracking issue, NOT the PR. `Closes #N` (in the body) links the PR in the issue's **Development** panel and closes the issue on merge — no `createLinkedBranch` is needed for the PR.
   - Fill the template body: the `Closes #N` line under **Linked Issue**, and the **Agent Task Manifest** copied from `TaskList` (one line per task: `- [ ] #<taskId> <subject> — <owner> — <status>`). Any file path in the body must be an accessible GitHub URL (head-branch blob URL or commit-pinned permalink), not a bare repo-relative path.
   - Open the PR **ready** (not draft).

### Build Status checklist (live, in the PR body)

The PR body carries a **Build Status** checklist that you tick as each phase completes:

- [ ] Implementation
- [ ] Codex review R1
- [ ] Fixes
- [ ] Codex review R2
- [ ] Result

Edit the PR body (`gh pr edit --body`) to check each item as you reach it, and post one comment per phase via `gh pr comment` (the round comments are woven into the Codex Implementation Review Loop below). Immediately after opening the PR, tick **Implementation** and post a `gh pr comment` noting implementation is done.

### No-issue / graceful-skip fallback

If `## Tracking` has **no issue number** (a local-only plan, recorded as `none — gh unavailable`) OR `gh` / the remote / auth is unavailable (`command -v gh` fails, or `gh auth status` / the push errors):

- **SKIP** PR creation, every `gh pr comment`, all Build-Status updates, and the `Closes #N` line.
- **STILL** implement the plan and **STILL** run the Codex Implementation Review Loop locally.
- Leave the branch in the worktree untouched.
- Print the exact commands the user can run later to open the PR by hand. **Use the branch name recorded VERBATIM in `## Tracking`** (the single source of truth) — do not re-derive it — and pick the matching sub-case:

  **(a) No issue number** (local-only plan; branch recorded as `<type>/<slug>`, no `#N`). Omit any `Closes #N` line — there is no issue to close:

  ```
  git push -u origin HEAD:refs/heads/<type>/<slug>
  gh pr create --template <type>.md --base main --head <type>/<slug> --title "<emoji> <type>(<scope>): <description>"
  ```

  **(b) Issue exists but `gh` / remote / auth / push failed** (branch recorded as `<type>/<N>-<slug>`). Keep the `<N>` segment and keep the `Closes #N` line in the PR body:

  ```
  git push -u origin HEAD:refs/heads/<type>/<N>-<slug>
  gh pr create --template <type>.md --base main --head <type>/<N>-<slug> --title "<emoji> <type>(<scope>): <description>"
  ```

A missing issue number or a missing `gh` MUST NEVER block the build — mirror the existing Codex graceful-skip pattern, warn the user, and continue local-only.

### Guards — leave the PR OPEN for the user

- **Never merge the PR.** `/build` opens the PR and stops; the user reviews and merges it themselves. Do not run any merge command against the PR via `gh`.
- **Never push to the `main` branch** and never commit on top of `main`. The ONLY branch `/build` pushes is the feature ref `refs/heads/<type>/<N>-<slug>` shown above.

## Codex Implementation Review Loop

After implementation completes (Workflow) and before the Report, hand the **implemented working tree** to Codex for an independent review against the plan. Codex reads PLAN + the sibling `decisions.md` + the working-tree git diff, runs the plan's Validation Commands, and emits a per-round verdict + blocking findings **as its final CLI message only** — it writes no files and edits no source. Claude reads the verdict, deploys builders to fix the warranted findings, and re-submits — capped at 2 Codex rounds.

### Precondition / graceful skip

- Check Codex availability with `command -v codex`. If Codex is unavailable, SKIP the loop: warn the user (point them to `/codex:setup`), record the skip in the Report ("skipped — Codex unavailable"), and finish the build normally. Never block shipping a build on a missing Codex.

### Invocation (verbatim)

Run the following, substituting `<REPO_ROOT>` (the repo cwd that contains `.agents/skills/implementation-review/`), `<PLAN_PATH>` (= PLAN), `<N>` (the current round number), and `<SCRATCH>` (the session scratchpad):

```
codex exec -C "<REPO_ROOT>" -s workspace-write -o "<SCRATCH>/codex-review-round-<N>.md" "Use the implementation-review skill to review the build of the plan at <PLAN_PATH> (this is review round <N>). Inspect the working-tree changes (git status/diff) against the plan's acceptance criteria, step-by-step tasks, and the locked decisions in the sibling decisions.md, and run the plan's Validation Commands. Follow the skill's output contract exactly: emit your round <N> verdict and findings as your FINAL MESSAGE only; write no files and edit no source."
```

- `codex exec` has NO `--skill` / `--full-auto` / `-a` flag — the skill is auto-discovered (repo-level `.agents/skills/`) and invoked by NAMING it in the prompt.
- `<SCRATCH>` is the session scratchpad (e.g. `$CLAUDE_JOB_DIR/tmp` or `$TMPDIR`), NEVER the repo. `-o` captures Codex's FINAL MESSAGE only — the verdict is read FROM that file, not stdout.
- Give each round a generous timeout (~5 minutes): a findings-heavy round can run past the default window, and a round that times out / captures nothing writes no verdict block — re-run it rather than treating the empty result as approval.

### Read the verdict from the captured FILE (not stdout)

```
grep -E '^### Round [0-9]+ — Verdict: (approved|changes-requested)$' "<SCRATCH>/codex-review-round-<N>.md" | tail -1
```

(The dash is a literal em-dash, U+2014.) A round that times out or captures nothing is RE-RUN, never treated as approval.

### Loop control — max 2 Codex rounds

- **Round 1** → if the verdict is `approved`, the loop is done. If `changes-requested`, Claude deploys builders to fix the WARRANTED findings — for any finding Claude REJECTS, record the finding + its rationale in the Report. Then run **Round 2**.
- **Round 2** → if still `changes-requested`, Claude applies a best-effort final pass and PROCEEDS anyway, recording "proceeded without full Codex approval after 2 rounds" + the outstanding findings in the Report.
- Never exceed 2 Codex rounds.
- **Codex never edits source** — it reports only; Claude's builders apply every fix (`-s workspace-write` is granted solely so Codex can run the plan's Validation Commands).
- **Relay each phase to the tracking PR (when one was opened).** After reading each round's verdict, post one `gh pr comment` relaying it and tick the matching **Build Status** item via `gh pr edit --body`:
  - Round 1 verdict → comment + tick **Codex review R1**.
  - Fixes applied after a `changes-requested` round → comment listing the builders' fixes + tick **Fixes**.
  - Round 2 verdict → comment + tick **Codex review R2**.
  - Final outcome (approved at round N / proceeded after 2 rounds) → comment + tick **Result**.
  Each comment is relayed from the implementation-review verdict + findings; Claude is the only actor that calls `gh`. When no tracking PR exists (no issue number, or graceful `gh` skip), run the loop exactly as above and skip every `gh pr comment` / Build-Status update.

## Report

- Present the `## Report` section of the plan.
- Report the Codex Implementation Review outcome: the per-round verdict (approved at round N / proceeded without full approval after 2 rounds / skipped — Codex unavailable), the per-round Validation pass/fail summary, and any outstanding or Claude-rejected findings (with rationale).
- Report the PR lifecycle outcome: the opened PR's URL (with `Closes #N`) and its final Build Status — or, when PR creation was skipped (no issue number / `gh` unavailable), say so and include the exact `gh pr create` command the user can run to open it manually. The PR is left OPEN for the user to merge.
