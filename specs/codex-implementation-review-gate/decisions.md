# Decisions: Codex Implementation-Review Gate for /build

## Summary

Add a Codex verification step to the `/build` workflow. After Claude's builders finish
implementing a saved plan and before `/build` emits its final report, an automated loop
hands the **implemented code** to Codex for an independent review against the plan. Codex
reads `plan.md` + `decisions.md` + the working-tree git diff, **runs the plan's Validation
Commands**, statically checks the changes against the acceptance criteria and locked
decisions, and emits a per-round verdict + blocking findings **as its final CLI message
only** (no files written, no source edited). Claude reads the verdict, deploys builders to
fix warranted findings, and re-submits — capped at **2 Codex rounds**. The reviewer is a new
**Codex Skill** named `implementation-review`, repo-level at
`.agents/skills/implementation-review/`, sibling to the existing `spec-review` skill. The
loop lives in the `/build` command (`.claude/commands/build.md`); `plan-w-team` and the
`plan.md` template are **unchanged**. The gate runs on every build but skips gracefully (with
a recorded note) when the Codex CLI is unavailable. This feature deliberately picks up the
non-goal that `codex-spec-review-gate/decisions.md` deferred: "a Codex review of the
implemented code during the build phase."

## Resolved Decisions

### 1. Loop home: the `/build` command, not the per-plan spec

- **Question:** Where does the implementation-review loop live — baked into `/build`, or
  generated as tasks into every plan by `plan-w-team`?
- **Answer:** Bake it into `.claude/commands/build.md` as a global "Codex Implementation
  Review Loop" workflow step that runs on every build. `plan-w-team` and the `plan.md`
  template are not changed.
- **Rationale:** DRY and consistent with the existing precedent — `plan-w-team` owns the
  `spec-review` loop centrally rather than duplicating it into each artifact. Per-plan tasks
  would over-weight every spec with identical boilerplate and couple the loop to the planner.
  Keeping it in `/build` lets specs stay focused on the feature.

### 2. Reviewer artifact: a new Codex Skill `implementation-review`

- **Question:** Custom prompt or Codex Skill, and where does it live?
- **Answer:** A Codex **Skill** at `.agents/skills/implementation-review/SKILL.md`
  (repo-level, version controlled), sibling to `spec-review`. Authored to meta-skill-grade
  quality following Codex's native `skill-creator` conventions and the OpenAI Skills format
  (`name` + `description` frontmatter, progressive disclosure, front-loaded triggers).
- **Rationale:** OpenAI deprecated custom prompts in favor of Skills; repo-level placement is
  already proven to be auto-discovered by Codex 0.142.3 (see `codex-spec-review-gate/
runtime-notes.md`). Mirrors the established `spec-review` pattern.

### 3. Output channel: ephemeral CLI final message, no repo files

- **Question:** Where does Codex write its findings — a committed file, a section in
  `plan.md`, or just the CLI output?
- **Answer:** **Ephemeral.** The skill's output contract is to emit the verdict + findings as
  Codex's **final message only**; it writes no files and edits no source. The `/build` loop
  captures that message via `codex exec -o <scratch>/codex-review-round-N.md` into the
  session scratchpad (not the repo) and greps the verdict line there. No repo artifact is
  added. Because there is no persistent file to self-count from, **Claude passes the round
  number into the prompt** each round (rather than Codex scanning prior headers, as
  `spec-review` does).
- **Rationale:** Build-time review is transient — the code keeps changing as Claude fixes, so
  a committed `implementation-review.md` goes stale immediately and clutters the repo. The
  orchestrator only needs to know what to fix. `codex exec -o` writes Codex's clean last
  message (not noisy stdout), so the channel is still deterministic. The durable trail is the
  `/build` Report, not a file.

### 4. Review depth: run the plan's Validation Commands + static review

- **Question:** Does Codex execute the plan's Validation Commands, or review statically?
- **Answer:** Both. Codex reads `plan.md` (acceptance criteria, step-by-step tasks,
  validation commands), `decisions.md` (locked constraints), and the working-tree git diff,
  then **independently runs the plan's Validation Commands** and reports real pass/fail, plus
  a static check against the acceptance criteria and decisions. It runs under
  `-s workspace-write` so validation commands that compile/build/write can execute.
- **Rationale:** Independent execution is the actual value of a second reviewer — it catches a
  builder who skipped or fudged "tests pass" (AGENTS.md rule 11, fail loud), not just code
  that reads wrong. Static-only would miss runtime/test failures.

### 5. No source edits by Codex — report only, Claude fixes

- **Question:** May Codex edit code to fix the findings it raises?
- **Answer:** No. Codex runs commands and emits findings only; it **never edits source
  files**. Claude's builders apply every fix. This is a hard rule in the skill body and in the
  `/build` loop docs (workspace-write is granted only so Codex can run validation, not mutate
  source).
- **Rationale:** User-locked, and mirrors `spec-review` (Codex reviews; Claude owns the
  artifact). Keeps the review independent and the fixes auditable.

### 6. Finding bar: blocking issues only, grounded in plan + code

- **Question:** What counts as a reportable finding?
- **Answer:** Blocking only: (a) **unmet acceptance criteria**; (b) **incomplete or missing
  step-by-step tasks**; (c) **failing or not-run Validation Commands**; (d) **plan/decision
  violations or build-time scope drift** (code that contradicts a locked decision or does work
  the plan didn't call for); (e) **real bugs / regressions / security / data-loss risks**
  introduced by the implementation. Not style nits, not speculative "you could also". Every
  finding grounded in a specific plan line + code location. Verdict is `approved` only when
  zero blocking findings remain.
- **Rationale:** Parallels the `spec-review` bar but retargeted from "is the spec sound" to
  "did the build satisfy the spec". Keeps the gate from blocking on polish.

### 7. Output format: greppable verdict + validation block + findings bullets

- **Question:** What exact shape is Codex's final message?
- **Answer:**
  - First line exactly `### Round N — Verdict: approved` or
    `### Round N — Verdict: changes-requested` (literal em-dash U+2014; N injected by Claude).
  - A `Validation:` block — one line per plan Validation Command → `PASS`/`FAIL`.
  - For `changes-requested`: a `Findings:` list, one bullet per blocking finding, each stating
    the problem (anchored to the plan section / acceptance criterion + the file) AND a concrete
    fix recommendation.
  - For `approved`: `Validation: all PASS` (or noted exceptions) and a single line stating no
    blocking findings remain. No padding findings.
- **Rationale:** A machine-greppable verdict line gives Claude a deterministic loop signal;
  the validation block makes "tests pass" auditable; per-finding anchors make fixes targetable.

### 8. Loop control: max 2 Codex rounds, then proceed

- **Question:** How many rounds, and what on non-approval?
- **Answer:** Cadence: build completes → Codex Round 1 → if `approved`, done → Claude deploys
  builders to fix warranted findings → Codex Round 2 → if still `changes-requested`, Claude
  applies a best-effort final pass and **proceeds anyway**, recording "proceeded without full
  Codex approval after 2 rounds" + the outstanding findings in the Report. **Never exceed 2
  rounds.** Mirrors `plan-w-team`.
- **Rationale:** Two rounds converge most builds without an unbounded loop; the recorded
  non-approval keeps the outcome honest (fail loud).

### 9. Claude may reject a finding (with recorded rationale)

- **Question:** What if Claude disagrees with a Codex finding?
- **Answer:** Claude fixes only warranted findings. For any finding it rejects, it records the
  finding + its rationale in the `/build` Report (the loop's durable trail), rather than
  silently ignoring it.
- **Rationale:** Mirrors `spec-review`'s reject-with-rationale rule; honors AGENTS.md fail-loud.

### 10. Gate timing + fallback: always-on, graceful skip

- **Question:** Run every build? What if the Codex CLI is missing/unauthenticated?
- **Answer:** Run on every `/build`, after implementation completes and before the final
  Report. If `command -v codex` fails, skip the loop, warn (point to `/codex:setup`), record
  the skip in the Report, and finish the build normally.
- **Rationale:** Verification should be the default, but a missing local tool must not block
  shipping a build. Fail loud via the recorded skip note.

### 11. Outcome trail: the `/build` Report (no new repo files)

- **Question:** Where is the verification outcome recorded, given there is no committed file?
- **Answer:** In `/build`'s final Report — the per-round verdict, the validation pass/fail
  summary, and any outstanding or Claude-rejected findings. No new repo files are written and
  no planning artifact is mutated during the build.
- **Rationale:** Honors the user's minimal-file-footprint intent while still surfacing the full
  review trail to the user.

### 12. Review target: the working-tree diff

- **Question:** What implementation state does Codex review?
- **Answer:** The working-tree changes — `git status` + `git diff` (including untracked changed
  files). Builds in this repo leave uncommitted changes, so the working tree is the artifact.
- **Rationale:** No commit/branch range is produced by `/build`; the working tree is the
  ground truth of what the builders implemented.

### 13. Team: general-purpose builders

- **Question:** Who builds it?
- **Answer:** `general-purpose` agents — `.claude/agents/team/*.md` does not exist.
- **Rationale:** No specialized team agents are defined in this repo (confirmed by `ls`).

## Assumptions

- **A1 — Runtime already verified.** Repo-level `.agents/skills/<name>/` discovery,
  `-s workspace-write`, and the verdict-grep regex are empirically established in
  `specs/codex-spec-review-gate/runtime-notes.md` (Codex 0.142.3). This build **reuses** those
  findings rather than re-deriving them.
- **A2 — `-o` capture works for ephemeral output.** `codex exec -o <file>` writes Codex's final
  message to `<file>`; the verdict line is greppable from it. `runtime-notes.md` lists `-o` as
  available; Task 1 confirms it carries the verdict cleanly before the skill/loop depend on it.
- **A3 — `description` has no angle brackets.** Codex's `quick_validate.py` rejects `<`/`>` in
  the skill `description`; the new skill's frontmatter must avoid them.
- **A4 — Skill name** is `implementation-review`; the round-header + verdict strings are fixed
  exactly as in Decision 7 so Claude's grep is stable.
- **A5 — Removals use `mv … ~/.Trash/`**, never `rm -rf` (AGENTS.md). Python via `uv`, JS/TS via
  `bun`. Pass model aliases (`opus`/etc.).
- **A6 — `/build` orchestration is unchanged otherwise.** The loop is appended after the
  existing implement step; the plan's own Team Orchestration / Step-by-Step Tasks still drive
  the implementation itself.

## Open Questions / Out of Scope

- **Non-goal:** Changing `plan-w-team` or the `plan.md` template. The loop lives entirely in
  `/build`; the plan supplies acceptance criteria + validation commands that already exist.
- **Non-goal:** A committed per-plan review file or a `## Codex Implementation Findings` section
  in `plan.md` (ephemeral output chosen).
- **Non-goal:** Letting Codex edit/fix source code, or a third Codex round / human-in-the-loop
  approval beyond the 2-round cap.
- **Non-goal:** Re-deriving the Codex runtime facts already in `codex-spec-review-gate/
runtime-notes.md` (reused, lightly confirmed for the `-o` path).
- **Deferred:** Tuning the finding bar / round cap, and whether to optionally persist the review
  trail to `decisions.md`, after real usage.

## Codex Verification

**Outcome: approved at round 2.** The Codex `spec-review` gate ran on `plan.md`. Round 1 returned
`changes-requested` with two blocking findings, **both accepted and fixed** (none rejected); Round 2
returned `approved`.

- **R1-1 — `git diff` misses untracked files (accepted).** Phase 3, Task 4, the acceptance
  criterion, and the fixture Validation Command relied on `git diff`/`git diff --stat`, which do not
  detect newly *created* untracked files — so the "Codex writes no files / edits no source" guarantee
  was incomplete. Fixed: all four sites now compare a `git status --porcelain --untracked-files=all`
  snapshot before vs after the review run.
- **R1-2 — raw `python3` contradicts the locked `uv` rule (accepted).** Step 2 and the Validation
  Commands invoked `python3 …/quick_validate.py` directly, violating Assumption A5 / AGENTS.md
  ("Python via `uv`"). Fixed: both now use `uv run python …/quick_validate.py`.
