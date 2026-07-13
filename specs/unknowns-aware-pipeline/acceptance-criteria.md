# Acceptance Criteria: Unknowns-Aware Pipeline

> The definition of "done" for [spec.md](./spec.md). Every criterion is observable and testable, and
> every task in tasks.md should map to at least one criterion here.

## Acceptance Criteria

- **AC1** — `.claude/commands/harness-layer/harness-plan.md` contains a Blindspot Pass workflow step (after codebase/profile, before grilling) with complexity-scaled inline cards whose findings and dispositions land in `decisions.md ## Blindspots` and seed the grilling ledger; the Grilling Protocol orders questions by architectural blast radius and defines the taste route (2–4 concrete alternatives via AskUserQuestion labels/descriptions, previews only where the harness supports them, provisional decisions re-confirmed against the in-worktree design-directions page before the spec commit, recorded in decisions.md).
- **AC2** — harness-plan.md's spec-writing step authors medium/complex artifacts inside the worktree under `specs/<name-of-plan>/artifacts/` (committed with the spec) and publishes each best-effort from that project-local file, stating publishing never blocks; its Report block carries an `Artifacts:` line.
- **AC3** — `.claude/commands/harness-layer/harness-build.md` creates `implementation-notes.md` from the template at implement start, adds a Deviations field to the builder hand-off contract, creates and folds deviations at each checkpoint under the explicitly scoped lead-owned non-implementation-file exception (notes creation/folding, ship-brief authoring, `## Tracking` / `## Locked Boundaries`), and gates any deviation touching a locked decision or acceptance criterion on AskUserQuestion.
- **AC4** — harness-build.md's review packet points at `implementation-notes.md`, and every `specs/<name>/reviews/` delta exclusion also excludes `specs/<name>/artifacts/`.
- **AC5** — harness-build.md has the lead author the ship brief (+3–6-question quiz) under the non-implementation-file exception for medium/complex plans in EVERY approval path — after the `approved` verdict is read and before that round's report commit, landing report + brief as ONE commit that is the approved head; the brief is authored fresh in the approving round (never reused from a failed round); the Finish step publishes best-effort, adds `## Ship Brief` to the PR body, and the Report tells the user to take the quiz before shipping; simple plans skip both.
- **AC6** — `.claude/commands/harness-layer/harness-review.md` lists a `plan-fidelity` lens: diff vs spec.md/tasks.md/implementation-notes.md; an undocumented divergence is a finding; no plan → lens reports nothing.
- **AC7** — `specs/_templates/decisions.md` carries `## Blindspots`; `specs/_templates/spec.md`'s `## Requirements & Decisions` guidance orders by volatility with alternatives (heading unchanged); `specs/_templates/implementation-notes.md` exists with `## Deviations` and `## Fold-Forward` sections.
- **AC8** — `check_spec_completeness.py` requires `Blindspots` in decisions.md; a new intent test pins that a missing `## Blindspots` blocks naming the section; the spec-completeness suite and the full test suite pass.
- **AC9** — `spec-review/SKILL.md` blocks on an undispositioned blindspot entry; `implementation-review/SKILL.md` dispositions implementation-notes deviations and excludes `specs/<plan>/artifacts/` from delta scope.
- **AC10** — AGENTS.md's pipeline section documents the artifacts home and unknowns checkpoints in ≤2 lines; `git diff origin/main --name-only` shows no change to `harness-ship.md`.

## Validation Commands

Run these to prove the criteria above. Map each command to the criteria it verifies.

These commands are necessary smoke checks, not sufficient proof — prose contracts cannot be
fully asserted by grep. The `validate-all` task ADDITIONALLY reads each changed file and
confirms every AC clause (ordering, gates, ownership, exclusions, dispositions, PR-body
behavior, brief freshness, the ≤2-line memory constraint), recording clause-by-clause results
in its hand-off; the internal and Codex review gates then re-verify the same clauses.

- `uv run pytest tests/harness-layer/hooks/spec-completeness -q` — verifies AC8. All tests pass, including the new intent test.
- `uv run pytest` — verifies AC8 (no regression anywhere). Full suite passes.
- `grep -q '"Blindspots"' .claude/hooks/check_spec_completeness.py && grep -q '## Blindspots' specs/_templates/decisions.md && echo PASS` — verifies AC7/AC8 stay in sync. Prints PASS.
- `test -f specs/_templates/implementation-notes.md && grep -q '## Deviations' specs/_templates/implementation-notes.md && grep -q '## Fold-Forward' specs/_templates/implementation-notes.md && echo PASS` — verifies AC7 (new template with both sections). Prints PASS.
- `f=.claude/commands/harness-layer/harness-plan.md; grep -qi 'blindspot' $f && grep -qi 'blast radius' $f && grep -q '## Blindspots' $f && grep -q 'artifacts/' $f && grep -qi 'best-effort' $f && grep -q 'AskUserQuestion' $f && grep -q 'Artifacts:' $f && echo PASS` — verifies AC1/AC2 clause tokens (pass step, ordering, recording home, artifact dir, non-blocking publish, taste route, report line). Prints PASS.
- `f=.claude/commands/harness-layer/harness-build.md; grep -q 'implementation-notes' $f && grep -qi 'deviation' $f && grep -qi 'ledger' $f && grep -q 'artifacts/' $f && grep -qi 'ship-brief' $f && grep -qi 'quiz' $f && grep -qi 'approved head' $f && grep -q '## Ship Brief' $f && echo PASS` — verifies AC3/AC4/AC5 clause tokens (notes, deviations contract, ledger exception, delta exclusion, brief, quiz, commit rule, PR-body entry). Prints PASS.
- `f=.claude/commands/harness-layer/harness-review.md; grep -q 'plan-fidelity' $f && grep -q 'implementation-notes' $f && echo PASS` — verifies AC6 (lens present and reading the notes). Prints PASS.
- `grep -qi 'blindspot' .agents/skills/spec-review/SKILL.md && grep -qi 'disposition' .agents/skills/spec-review/SKILL.md && grep -q 'implementation-notes' .agents/skills/implementation-review/SKILL.md && grep -qi 'disposition' .agents/skills/implementation-review/SKILL.md && grep -q 'artifacts/' .agents/skills/implementation-review/SKILL.md && echo PASS` — verifies AC9 (both skills' checks and the delta exclusion). Prints PASS.
- `grep -qi 'artifacts/' AGENTS.md && echo PASS` — verifies AC10 (memory line present; the ≤2-line constraint is checked by the validator's read). Prints PASS.
- `git diff origin/main --name-only | grep -q 'harness-ship' && echo FAIL || echo PASS` — verifies AC10 (ship untouched). Prints PASS.
- `git diff origin/main --name-only -- ':!specs/unknowns-aware-pipeline'` — verifies scope: every listed path appears in spec.md `## Relevant Files` (including New Files); the plan folder itself is baseline, not implementation. Checked by the validator against the list.
