---
description: Implement a saved plan through a worktree-first, draft-PR-early, multi-layer review pipeline (internal check → Claude code review → Codex cross-review). Pass a feature name (e.g. build-multi-layer-review) or a direct path to a plan file, plus an optional worktree.
argument-hint: [feature-name | path-to-plan] [worktree]
---

# Build

`/build` is a thin **orchestrating command**: it sequences the build phases, owns every
`git` and `gh` call, and delegates the review work to focused skills/agents. It enters
the plan's **worktree first**, opens a **draft PR** early, implements the plan, then
gates the result through three review layers — an internal check (`code-simplifier`),
a Claude code review (`claude-code-review` skill, vs **AGENTS.md**), and a Codex
cross-review loop (the `implementation-review` orchestrator, max 2 rounds) — committing
a checkpoint and ticking a Build-Status item at each phase, and finally marking the PR
**ready** for `/ship`. It never merges the PR and never touches `main`.

## Variables

- **TARGET**: the first token of `$ARGUMENTS` — a plan feature-name (e.g.
  `build-multi-layer-review`) or a direct path to a plan file. **Required.**
- **WORKTREE**: the optional second token of `$ARGUMENTS` — an explicit worktree path or
  branch. When given it overrides autodiscover.

## Instructions

- If no **TARGET** is provided, STOP immediately and ask the user to provide it
  (AskUserQuestion).
- Claude is the **only** actor that calls `git` and `gh`. The review skills/agents
  produce findings, comments, and reports; `/build` applies fixes, commits, pushes, and
  posts.
- Run the phases below in order. Each phase ends with up to one trailer-free checkpoint
  commit + push (none when the phase produced no changes) and always one Build-Status tick
  (see **Commit & push cadence**). Re-running `/build` on a partially-built worktree
  resumes from the Build-Status ticks already present.

## Workflow

### Commit & push cadence (every checkpoint, trailer-free `Refs #N`)

Each phase closes with **at most ONE** conventional commit, then a push to the feature
ref. A phase that legitimately produces no changes (e.g. the `code-simplifier` finds
nothing, the Claude review is `skipped — trivial diff`, or a Codex round is approved with
no fixes) makes **no empty commit** — never `--allow-empty` a no-op; just tick its
Build-Status item and move on.

- **Trailer-free.** Use the `<emoji> <type>(<scope>): <description>` subject with a
  `Refs #N` footer and **no `Co-Authored-By` trailer** (a message without it is correct;
  trailer-free is the rule — never append `Co-Authored-By` or `Signed-off-by`). `<N>` is
  the recorded issue number; for an issue-less legacy/local plan, omit the `Refs #N`
  footer.
- **Scoped `git add`.** Stage only the files that phase changed — never `git add -A` the
  whole tree blindly.
- **Push to the feature ref only:** `git push -u origin HEAD:refs/heads/<type>/<N>-<slug>`
  (the convention is enforced on the remote ref; the local worktree branch name is
  cosmetic). Never push to `main`.
- **The checkpoints are:** implementation, internal check, Claude-review fixes, each
  Codex round's report (`specs/<plan>/reviews/codex-impl-review-round-N.md`), and each
  fix round.

### Phase 0 — Bootstrap (worktree-first via arg-or-autodiscover, then resolve the spec)

**Enter the worktree BEFORE resolving any plan file — this ordering is load-bearing.**
`specs/<TARGET>/` lives only on the feature branch inside the worktree, never on `main`
where `/build` is invoked, so resolving a plan from the main checkout would fail. The
worktree step MUST precede spec resolution.

1. **Resolve and enter the worktree (arg, else autodiscover).**
   - If **WORKTREE** (the optional second arg) is given, treat it as the worktree path
     (or branch) and use it directly.
   - Else **autodiscover**: glob `.claude/worktrees/*/specs/<TARGET>/spec.md` and match by
     `<TARGET>`:
     - **exactly one match** → that worktree is the build worktree.
     - **multiple matches** → do NOT guess; ask the user which worktree to use
       (AskUserQuestion), or tell them to re-run with the explicit `[worktree]` arg.
     - **zero matches** → fall back to the **current working directory** and treat the
       run as a **legacy / local-only plan** (there is no worktree to enter); skip
       `EnterWorktree` and resolve the plan in the current tree (step 2).
   - For a resolved worktree (the arg, or a single autodiscover match), call
     `EnterWorktree(path=<worktree path>)` and run the ENTIRE build inside it.
2. **Resolve the plan (PLAN) + decision log (DECISIONS) from inside the resolved tree**,
   in order:
   1. `specs/<TARGET>/spec.md` exists → PLAN = `specs/<TARGET>/spec.md`,
      DECISIONS = `specs/<TARGET>/decisions.md` (feature-name form).
   2. Else `specs/<TARGET>/plan.md` exists → PLAN = `specs/<TARGET>/plan.md`,
      DECISIONS = `specs/<TARGET>/decisions.md` (**LEGACY FALLBACK** — a pre-rename folder
      that still uses the old `plan.md` name; its `## Tracking` block is read from this
      legacy `plan.md`).
   3. Else if `<TARGET>` is an existing file → PLAN = `<TARGET>`, DECISIONS = a
      `decisions.md` sibling in the same folder if present (direct path / legacy flat spec).
   4. Else STOP and report which paths were searched (both the worktree glob and the
      current-dir paths above).
3. **Read PLAN + DECISIONS, then the `## Tracking` block.** If DECISIONS exists, read it
   first — it holds the requirements, locked decisions, assumptions, and out-of-scope
   items that constrain the build; treat it as binding. From PLAN's `## Tracking` block
   read the issue number (or `none — gh unavailable`), the intended convention branch
   name (`<type>/<N>-<slug>`), and the worktree path. The recorded **issue number `#N` is
   the SINGLE SOURCE OF TRUTH** — NEVER re-derive it from the local branch
   (`EnterWorktree` mangles `feat/x` into `worktree-feat+x`). If PLAN has no `## Tracking`
   block (a legacy / local-only plan), treat the run as issue-less (see **Graceful skips**).
   If PLAN and DECISIONS conflict, STOP and surface the conflict instead of guessing.

### Phase 1 — Open the draft PR + seed Build Status

Immediately after entering the worktree (and resolving the plan), open **one** draft PR
from the recorded `## Tracking` block, tracked live through the phases below.

> **Handoff from `/plan-w-team`.** The convention branch `<type>/<N>-<slug>` ALREADY
> exists on `origin` carrying the plan commits, so the draft PR opens directly against it
> — **no push is needed yet**; `/build`'s first push is the Implementation commit in
> Phase 2. `/build` MUST NOT create a second branch, and it opens exactly ONE PR
> (`Closes #N`) whose diff therefore includes BOTH the plan and the implementation. Any
> file path `/build` writes into the PR body or a comment MUST be an accessible GitHub
> URL (a head-branch blob URL or a commit-pinned permalink), NEVER a bare repo-relative
> path (those resolve against `main` and 404 pre-merge).

When `## Tracking` carries an issue number `#N`:

1. **Open exactly ONE draft PR** with the type-matched template, mirroring the issue's
   metadata config:

   ```
   gh label create <type-label> --color … --description … --force
   gh pr create --draft --template <type>.md --base main --head <type>/<N>-<slug> --assignee @me --label <type-label> --title "<emoji> <type>(<scope>): <description>"
   ```

   - `<emoji>` is the gitmoji for `<type>` (✨ feat, 🐛 fix, 📝 docs, 🎨 style,
     ♻️ refactor, ⚡️ perf, ✅ test, 🔧 chore) — e.g. `✨ feat(api): add login endpoint`.
   - **Mirror the issue's metadata on the PR.** Using the SAME `<type>`→label mapping as
     `/plan-w-team` (`feat→enhancement`, `fix→bug`, `docs→documentation`;
     `chore`/`refactor`/`perf`/`style`/`test` same-named), set `--assignee @me` +
     `--label <type-label>`. Create the type label on demand FIRST with the idempotent
     `gh label create <type-label> --color … --description … --force` so build self-heals
     a missing/deleted label. `epic` stays on the tracking issue, NOT the PR. `Closes #N`
     (in the body) links the PR in the issue's **Development** panel and closes the issue
     on merge.
   - Fill the template body: the `Closes #N` line under **Linked Issue**, the **Agent
     Task Manifest** copied from `TaskList` (one line per task:
     `- [ ] #<taskId> <subject> — <owner> — <status>`), and the **Build Status**
     checklist seeded below. The PR is opened **draft** (`--draft`); it is marked ready
     only in Phase 6.

2. **Seed the 7-item Build Status checklist** in the PR body (none ticked yet — they are
   ticked live with `gh pr edit --body` as each phase completes), EXACTLY these items in
   order:

   ```
   ## Build Status

   - [ ] Implementation
   - [ ] Internal check
   - [ ] Claude code review
   - [ ] Codex review R1
   - [ ] Fixes
   - [ ] Codex review R2
   - [ ] Result
   ```

### Phase 2 — Implement (builders)

Read PLAN, think hard about it, and implement it into the codebase honoring DECISIONS.
Deploy builders as needed. When implementation is complete:

- Checkpoint commit + push (scoped `git add`, trailer-free `Refs #N`) per **Commit & push
  cadence**. This is `/build`'s first push onto the pre-existing convention branch ref
  (fast-forwards the implementation commits on top of the plan commits).
- Tick **Implementation** in the Build Status (`gh pr edit --body`) and post one
  `gh pr comment` noting implementation is done.

### Phase 3 — Internal check (code-simplifier)

Run the **`code-simplifier`** agent on the recently-modified code (it scopes to the
branch diff, applies the AGENTS.md standard across Python / TS-Next-React / the Markdown
harness layer, and makes only behavior-preserving edits — never weakening prompt
semantics). Apply its simplifications, then:

- Checkpoint commit + push per **Commit & push cadence**.
- Tick **Internal check** and post one `gh pr comment` summarizing the simplifications.

### Phase 4 — Claude code review (vs AGENTS.md)

Run the **`claude-code-review`** skill. It reviews `git diff origin/main...HEAD` against
**AGENTS.md** (+ `~/.codex/AGENTS.md`, `.claude/rules/*`, `GIT-COMMIT-PR-MESSAGE.md`),
runs its eligibility gate → 5 parallel Sonnet lenses → per-finding Haiku confidence
0-100 → keeps only findings **≥ 80**, and returns two sinks: a permalink-cited PR comment
body and the filtered ≥ 80 findings. The skill edits no source.

- **Fix the warranted findings** (Claude's builders apply them); for any finding Claude
  rejects, record it + the rationale for the Report.
- Checkpoint commit + push per **Commit & push cadence**.
- Post the skill's PR comment body via `gh pr comment`, then tick **Claude code review**.
- If the eligibility gate skipped the review (`skipped — trivial diff`), record it, tick
  the item, and proceed.

### Phase 5 — Codex cross-review loop (max 2 rounds)

Hand the implemented working tree to Codex for an independent cross-model review via the
**`implementation-review`** orchestrator skill. The skill spawns the 6 read-only
`.codex/agents/*.toml` review subagents (or runs their lenses as sequential passes if
headless spawn is unavailable), runs the plan's Validation Commands, folds in its own
plan-adherence findings, and **writes ONE consolidated report** to
`specs/<plan>/reviews/codex-impl-review-round-N.md`, returning only a terse summary.
`/build` reads the verdict **from that report file**, never from stdout.

**Precondition / graceful skip.** Check Codex availability with `command -v codex`. If
Codex is unavailable, SKIP the loop: warn the user (point them to `/codex:setup`), record
"skipped — Codex unavailable" in the Report, and finish with the Claude-side phases only.
Never block a build on a missing Codex.

**Per round N (N = 1, then 2 if needed):**

1. **Invoke the skill via `codex exec`** (substitute `<REPO_ROOT>` = the worktree root
   containing `.agents/skills/implementation-review/`, `<PLAN_PATH>` = PLAN, `<plan>` =
   the plan folder name, and `<N>` = the current round):

   ```
   codex exec -C "<REPO_ROOT>" -s workspace-write "Use the implementation-review skill to review build round <N> of the plan at <PLAN_PATH>. Inspect the branch changes vs base via git diff origin/main...HEAD (plus git status and git diff for any not-yet-committed work) against the plan's acceptance criteria, step-by-step tasks, and the locked decisions in the sibling decisions.md; run the plan's Validation Commands; spawn the 6 .codex/agents review subagents (or run their lenses as sequential passes if headless spawn is unavailable). Follow the skill's contract: write ONE consolidated report to specs/<plan>/reviews/codex-impl-review-round-<N>.md with the verdict header, and return only the terse summary."
   ```

   - `codex exec` has **NO** `--skill` / `--full-auto` / `-a` flag — the skill is
     auto-discovered from repo-level `.agents/skills/` and invoked by **NAMING it in the
     prompt**.
   - `-s workspace-write` is granted SOLELY so Codex can run the Validation Commands and
     write its one report; Codex edits NO source.
   - Give each round a generous timeout (~5 minutes): a findings-heavy round can run past
     the default window.

2. **Commit the report.** The skill wrote
   `specs/<plan>/reviews/codex-impl-review-round-<N>.md`. Stage just that file and make a
   trailer-free `Refs #N` checkpoint commit + push per **Commit & push cadence** — the
   report is a committed PR audit artifact.

3. **Read the verdict FROM the report file** (not stdout) — grep the `### Round N —
   Verdict: …` header (the dash is a literal em-dash, U+2014):

   ```
   grep -E '^### Round [0-9]+ — Verdict: (approved|changes-requested)$' "specs/<plan>/reviews/codex-impl-review-round-<N>.md" | tail -1
   ```

   A round that times out, writes no report, or whose file lacks a verdict header is
   **RE-RUN** — never treated as approval. Never let an empty/incomplete run look like a
   pass.

4. **Relay to the PR + tick.** Post one `gh pr comment` relaying the round's verdict +
   headline findings (read from the report file) and tick the matching Build-Status item:
   round 1 → **Codex review R1**; round 2 → **Codex review R2**.

5. **On `changes-requested`:** Claude's builders fix the WARRANTED findings (for any
   finding Claude rejects, record the finding + rationale for the Report); checkpoint
   commit + push per **Commit & push cadence**; post a `gh pr comment` listing the fixes
   and tick **Fixes**. Then proceed to round 2.

**Loop control:**

- **Round 1** `approved` → the loop is done (skip to Phase 6). Because no
  `changes-requested` round ran and round 2 never runs, **tick the unreached conditional
  items as N/A** so the final body has zero unchecked boxes:
  `- [x] Fixes — N/A (no changes-requested round)` and
  `- [x] Codex review R2 — N/A (approved at R1)`.
  `changes-requested` → apply fixes (step 5, which ticks **Fixes**), then run **Round 2**.
- **Round 2** `approved` → done. Still `changes-requested` → Claude applies a best-effort
  final pass and **PROCEEDS anyway**, recording "proceeded without full Codex approval
  after 2 rounds" + the outstanding findings in the Report.
- **Never exceed 2 Codex rounds.**

### Phase 6 — Mark the PR ready + Result

After the final Codex verdict:

- **Sweep the Build Status to zero unchecked boxes.** `/ship` gates on EVERY checklist
  item being checked (`- [x]`, no `- [ ]` left), so the final PR body MUST have no
  unchecked box. Any item NOT reached by this run — `Fixes` when no round was
  `changes-requested`, `Codex review R2` when round 2 never ran, or
  `Codex review R1` / `Codex review R2` / `Fixes` when the Codex loop was
  `skipped — Codex unavailable` — gets ticked with an explicit N/A annotation, e.g.
  `- [x] Codex review R1 — N/A (Codex unavailable)`. Every conditional item is either
  genuinely completed or ticked `N/A (…reason…)`; none is left as `- [ ]`.
- Mark the PR **ready** with `gh pr ready`.
- Tick **Result** in the Build Status and post a final `gh pr comment` with the outcome
  (approved at round N / proceeded after 2 rounds / skipped — Codex unavailable).
- Proceed to the **Report**. The PR is left OPEN for the user to merge via `/ship`.

## Graceful skips (no issue / no `gh` / no Codex)

If `## Tracking` has **no issue number** (a local-only plan, recorded as
`none — gh unavailable`) OR `gh` / the remote / auth is unavailable (`command -v gh`
fails, or `gh auth status` / a push errors):

- **SKIP** the draft-PR creation, the `gh pr ready`, every `gh pr comment`, all
  Build-Status edits, and the `Closes #N` line.
- **STILL** implement the plan and **STILL** run every review phase locally — the
  internal check, the Claude code review, and the Codex cross-review loop.
- Leave the branch in the worktree untouched, and print the exact commands the user can
  run later to open the PR by hand. **Use the branch name recorded VERBATIM in
  `## Tracking`** (the single source of truth) — do not re-derive it — and pick the
  matching sub-case:

  **(a) No issue number** (local-only plan; branch recorded as `<type>/<slug>`, no `#N`).
  Omit any `Closes #N` line — there is no issue to close:

  ```
  git push -u origin HEAD:refs/heads/<type>/<slug>
  gh pr create --draft --template <type>.md --base main --head <type>/<slug> --title "<emoji> <type>(<scope>): <description>"
  ```

  **(b) Issue exists but `gh` / remote / auth / push failed** (branch recorded as
  `<type>/<N>-<slug>`). Keep the `<N>` segment and keep the `Closes #N` line in the body:

  ```
  git push -u origin HEAD:refs/heads/<type>/<N>-<slug>
  gh pr create --draft --template <type>.md --base main --head <type>/<N>-<slug> --title "<emoji> <type>(<scope>): <description>"
  ```

A missing issue number, a missing `gh`, or a missing `codex` MUST NEVER block the build —
warn the user and continue local-only.

## Guards — leave the PR OPEN for the user

- **Never merge the PR.** `/build` opens the PR, runs the review pipeline, marks it ready,
  and stops; the user reviews and merges it themselves (via `/ship`). Do not run any merge
  command against the PR via `gh`.
- **Never push to the `main` branch** and never commit on top of `main`. The ONLY branch
  `/build` pushes is the feature ref `refs/heads/<type>/<N>-<slug>`.
- **The review layers edit no source through their own hands** — the `code-simplifier`
  agent edits only behavior-preserving simplifications it applies under Claude's
  orchestration; the `claude-code-review` skill and the Codex `implementation-review`
  skill (and its 6 subagents) report only. Claude's builders apply every cross-review fix.

## Report

- Present the `## Report` section of the plan.
- Report each review phase's outcome: the internal-check summary, the Claude code-review
  result (findings fixed / rejected with rationale, or `skipped — trivial diff`), and the
  Codex Implementation Review outcome — the per-round verdict (approved at round N /
  proceeded without full approval after 2 rounds / skipped — Codex unavailable), the
  per-round Validation pass/fail summary, and any outstanding or Claude-rejected findings.
- Report the PR lifecycle outcome: the opened PR's URL (with `Closes #N`) and its final
  Build Status — or, when PR creation was skipped (no issue number / `gh` unavailable),
  say so and include the exact `gh pr create` command the user can run to open it
  manually. The PR is left OPEN for the user to merge.
