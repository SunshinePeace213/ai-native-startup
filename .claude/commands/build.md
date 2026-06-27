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
- Read PLAN, think hard about it, and implement it into the codebase, honoring the decision log. If PLAN and DECISIONS conflict, STOP and surface the conflict instead of guessing.
- When implementation completes, run the **Codex Implementation Review Loop** (below) before reporting.

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

## Report

- Present the `## Report` section of the plan.
- Report the Codex Implementation Review outcome: the per-round verdict (approved at round N / proceeded without full approval after 2 rounds / skipped — Codex unavailable), the per-round Validation pass/fail summary, and any outstanding or Claude-rejected findings (with rationale).
