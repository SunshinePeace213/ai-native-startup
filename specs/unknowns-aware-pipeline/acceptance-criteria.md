# Acceptance Criteria: Unknowns-Aware Pipeline

> The definition of "done" for [spec.md](./spec.md). Every criterion is observable and testable, and
> every task in tasks.md should map to at least one criterion here.

## Acceptance Criteria

- **AC1** — `.claude/commands/harness-layer/harness-plan.md` contains a Blindspot Pass workflow step (after codebase/profile, before grilling) with complexity-scaled depth, scratchpad drafting, and recording into `decisions.md ## Blindspots`; the Grilling Protocol orders questions by architectural blast radius and defines the taste route (rendered design directions, confirmed via AskUserQuestion, recorded in decisions.md).
- **AC2** — harness-plan.md's spec-writing step copies scratchpad artifacts into `specs/<name-of-plan>/artifacts/` inside the worktree (committed with the spec), states artifact publishing is best-effort/never-blocking, and its Report block carries an `Artifacts:` line.
- **AC3** — `.claude/commands/harness-layer/harness-build.md` creates `implementation-notes.md` from the template at implement start, adds a Deviations field to the builder hand-off contract, folds deviations at each checkpoint, and gates any deviation touching a locked decision or acceptance criterion on AskUserQuestion.
- **AC4** — harness-build.md's review packet points at `implementation-notes.md`, and every `specs/<name>/reviews/` delta exclusion also excludes `specs/<name>/artifacts/`.
- **AC5** — harness-build.md's finish step authors the ship brief (+3–6-question quiz) for medium/complex plans only, commits it together with the approval-round report commit as the approved head, publishes best-effort, adds `## Ship Brief` to the PR body, includes the stale-brief re-author rule, and the Report tells the user to take the quiz before shipping.
- **AC6** — `.claude/commands/harness-layer/harness-review.md` lists a `plan-fidelity` lens: diff vs spec.md/tasks.md/implementation-notes.md; an undocumented divergence is a finding; no plan → lens reports nothing.
- **AC7** — `specs/_templates/decisions.md` carries `## Blindspots`; `specs/_templates/spec.md`'s `## Requirements & Decisions` guidance orders by volatility with alternatives (heading unchanged); `specs/_templates/implementation-notes.md` exists with `## Deviations` and `## Fold-Forward` sections.
- **AC8** — `check_spec_completeness.py` requires `Blindspots` in decisions.md; a new intent test pins that a missing `## Blindspots` blocks naming the section; the spec-completeness suite and the full test suite pass.
- **AC9** — `spec-review/SKILL.md` blocks on an undispositioned blindspot entry; `implementation-review/SKILL.md` dispositions implementation-notes deviations and excludes `specs/<plan>/artifacts/` from delta scope.
- **AC10** — AGENTS.md's pipeline section documents the artifacts home and unknowns checkpoints in ≤2 lines; `git diff origin/main --name-only` shows no change to `harness-ship.md`.

## Validation Commands

Run these to prove the criteria above. Map each command to the criteria it verifies.

- `uv run pytest tests/harness-layer/hooks/spec-completeness -q` — verifies AC8. All tests pass, including the new intent test.
- `uv run pytest` — verifies AC8 (no regression anywhere). Full suite passes.
- `grep -q '"Blindspots"' .claude/hooks/check_spec_completeness.py && grep -q '## Blindspots' specs/_templates/decisions.md && echo PASS` — verifies AC7/AC8 stay in sync. Prints PASS.
- `test -f specs/_templates/implementation-notes.md && grep -q '## Deviations' specs/_templates/implementation-notes.md && grep -q '## Fold-Forward' specs/_templates/implementation-notes.md && echo PASS` — verifies AC7. Prints PASS.
- `grep -qi 'blindspot' .claude/commands/harness-layer/harness-plan.md && grep -qi 'blast radius' .claude/commands/harness-layer/harness-plan.md && grep -q 'artifacts/' .claude/commands/harness-layer/harness-plan.md && echo PASS` — verifies AC1/AC2. Prints PASS.
- `grep -q 'implementation-notes' .claude/commands/harness-layer/harness-build.md && grep -qi 'ship brief' .claude/commands/harness-layer/harness-build.md && grep -qi 'deviation' .claude/commands/harness-layer/harness-build.md && echo PASS` — verifies AC3/AC4/AC5. Prints PASS.
- `grep -q 'plan-fidelity' .claude/commands/harness-layer/harness-review.md && echo PASS` — verifies AC6. Prints PASS.
- `grep -qi 'blindspot' .agents/skills/spec-review/SKILL.md && grep -q 'implementation-notes' .agents/skills/implementation-review/SKILL.md && grep -q 'artifacts/' .agents/skills/implementation-review/SKILL.md && echo PASS` — verifies AC9. Prints PASS.
- `grep -qi 'artifacts/' AGENTS.md && echo PASS` — verifies AC10 (memory line present). Prints PASS.
- `git diff origin/main --name-only | grep -q 'harness-ship' && echo FAIL || echo PASS` — verifies AC10 (ship untouched). Prints PASS.
