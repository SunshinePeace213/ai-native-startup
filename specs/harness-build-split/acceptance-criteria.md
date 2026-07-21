# Acceptance Criteria: Split harness-build into build + review commands

> The definition of "done" for [spec.md](./spec.md). Every criterion is observable and testable, and
> every task in tasks.md should map to at least one criterion here.

## Acceptance Criteria

- **AC1** — `.claude/commands/harness-layer/harness-build.md` and `.claude/commands/harness-layer/harness-review.md` both exist and their combined `wc -l` is under 132.
- **AC2** — Each command's `## Variables` declares exactly `PATH_TO_PLAN`, `ISSUE_NUMBER`, `PR_NUMBER`, `REVIEW_PROFILE`; neither file contains a Preflight section nor the strings `STAGES:`, `CROSS_CHECK:`, `ROUND_INPUT`, `REQUIRED_PLUGINS`, or `round-N-input`.
- **AC3** — harness-build.md sequences tidy (harness-simplifier / code-simplifier, behavior-preserving) BEFORE opening the draft PR, posts the tidy findings directly as the `<!-- report:tidy -->` PR comment, and contains no held-report rule.
- **AC4** — harness-build.md ends by recording `PR #M` and the last pushed SHA in spec.md `## Tracking` and STOPs when `## Tracking` has no Issue `#N`; harness-review.md STOPs when `## Tracking` has no PR number. These are the only STOPs in either file.
- **AC5** — harness-review.md drives Codex via a `sonnet` runner (retry-once, verdict-line grep, digest relay), spawns fixers per model-selection, caps at 2 rounds; a round-2 `changes-requested` posts the final report comment and leaves the PR draft; an `approved` verdict flips the PR ready only at the approved head (stage-table Ready evidence). No `status:needs-human`, over-cap gate, root-cause rule, Locked Boundaries, or fix-design consult appears in either command.
- **AC6** — `.agents/skills/implementation-review/SKILL.md` contains no Review packet / attestation / `round-N-input` / zero-git machinery; instead Codex runs its own `git diff` over injected SHAs and runs the plan's Validation Commands itself (unexecutable → recorded with reason, blocking; never fabricated); the report keeps the `### Round N — Verdict:` first line and ends with an `**Issue-comment digest:**` paragraph; lens selection, KB grounding, and the confidence filter survive.
- **AC7** — `specs/_templates/implementation-notes.md` is a chronological dev log (a `## Log` of dated entries covering phases, hand-offs, deviations, fixes, lessons) and `.claude/rules/development-log.md` exists flat with no `paths:` frontmatter, a `date · plan · lesson` line format, a ≈40-line cap with distill-on-overflow, and both files state the per-plan vs cross-plan boundary.
- **AC8** — `.claude/rules/harness-layer/artifacts.md` no longer lists the Deviations board row; its inventory has a Dev notes row rendered by harness-review on any verdict; harness-review.md renders `artifacts/dev-notes.html` from implementation-notes.md and links it from the PR; no file under `.claude/` or `.agents/` still references the ship brief.
- **AC9** — harness-plan.md's Define Team & Tasks step requires marking tasks whose outcomes must be recorded to memory; both new commands end with a memory step referencing memory-series.md conventions.
- **AC10** — Memory-truth edits landed: AGENTS.md's Core pipeline line includes `/harness-layer:harness-review` and a dev-log pointer bullet exists; git-workflow.md says the draft PR opens after the tidy checkpoint. `REVIEW_PROFILE` gating appears in both commands; harness-ship.md, spec-review/SKILL.md, and `.claude/hooks/` are untouched.

## Validation Commands

Run these to prove the criteria above. Map each command to the criteria it verifies.

- `wc -l .claude/commands/harness-layer/harness-build.md .claude/commands/harness-layer/harness-review.md` — verifies AC1. Both files listed; total < 132.
- `for f in .claude/commands/harness-layer/harness-build.md .claude/commands/harness-layer/harness-review.md; do echo "== $f"; sed -n '/^## Variables/,/^## /p' "$f" | grep -E '^[A-Z_]+:'; done` — verifies AC2. Exactly PATH_TO_PLAN, ISSUE_NUMBER, PR_NUMBER, REVIEW_PROFILE per file.
- `grep -lE 'Preflight|ROUND_INPUT|round-N-input|REQUIRED_PLUGINS|needs-human|Locked Boundaries|over-cap|[Rr]oot-cause|fix-design' .claude/commands/harness-layer/harness-build.md .claude/commands/harness-layer/harness-review.md; echo "exit=$?"` — verifies AC2, AC5. A pass prints no file (exit=1).
- `grep -n 'report:tidy' .claude/commands/harness-layer/harness-build.md && ! grep -qi 'hold' .claude/commands/harness-layer/harness-build.md` — verifies AC3. Tidy comment present, no held-report language.
- `grep -n 'Last pushed SHA' .claude/commands/harness-layer/harness-build.md && grep -n 'STOP' .claude/commands/harness-layer/harness-build.md .claude/commands/harness-layer/harness-review.md` — verifies AC4. SHA recording present; STOPs only on the two Tracking refusals.
- `grep -n 'sonnet' .claude/commands/harness-layer/harness-review.md && grep -n 'gh pr ready' .claude/commands/harness-layer/harness-review.md` — verifies AC5. Runner + ready-flip present.
- `grep -cE 'round-N-input|Review packet|attestation|zero git|no git' .agents/skills/implementation-review/SKILL.md; grep -n 'Issue-comment digest' .agents/skills/implementation-review/SKILL.md; grep -n 'git diff' .agents/skills/implementation-review/SKILL.md` — verifies AC6. Count 0; digest and self-serve diff present.
- `grep -n '## Log' specs/_templates/implementation-notes.md && test -f .claude/rules/development-log.md && ! head -1 .claude/rules/development-log.md | grep -q -- '---' && grep -q 'development-log' specs/_templates/implementation-notes.md` — verifies AC7. Log section, rule file without frontmatter, boundary cross-reference.
- `! grep -q 'Deviations board' .claude/rules/harness-layer/artifacts.md && grep -q 'Dev notes' .claude/rules/harness-layer/artifacts.md && grep -q 'dev-notes.html' .claude/commands/harness-layer/harness-review.md && ! grep -rqi 'ship.brief' .claude .agents` — verifies AC8.
- `grep -qi 'memory' .claude/commands/harness-layer/harness-plan.md && grep -qi 'memory' .claude/commands/harness-layer/harness-build.md && grep -qi 'memory' .claude/commands/harness-layer/harness-review.md && echo PASS` — verifies AC9.
- `grep -q 'harness-review' AGENTS.md && grep -q 'development-log' AGENTS.md && grep -q 'tidy checkpoint' .claude/rules/git-workflow.md && grep -q 'REVIEW_PROFILE' .claude/commands/harness-layer/harness-build.md && grep -q 'REVIEW_PROFILE' .claude/commands/harness-layer/harness-review.md && echo PASS` — verifies AC10.
- `git diff origin/main --name-only -- ':!specs/harness-build-split' ':!ai-docs'` — verifies AC10 (blast radius). Output lists ONLY the files named in spec.md `## Relevant Files` / `### New Files`.
