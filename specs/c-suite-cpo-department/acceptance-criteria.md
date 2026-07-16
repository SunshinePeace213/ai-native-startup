# Acceptance Criteria: c-suite CPO department

> The definition of "done" for [spec.md](./spec.md). Every criterion is observable and testable, and
> every task in tasks.md should map to at least one criterion here.

## Acceptance Criteria

- **AC1** — The three stage commands exist at `.claude/commands/c-suite/cpo-intake.md`, `cpo-prd.md`, `cpo-brief.md`, each with frontmatter (`description`, `argument-hint`) and the house sections (Purpose, Variables, Instructions, Workflow), and each names the knowledge skill(s) it loads.
- **AC2** — The commands resolve as `/c-suite:cpo-intake`, `/c-suite:cpo-prd`, `/c-suite:cpo-brief` in a live listing, and the three knowledge skills never auto-fire (frontmatter blocks model auto-invocation; the recorded legacy fallback applied and noted if needed).
- **AC3** — `cpo-intake.md` defines both modes (LIVE grilling; ASYNC question-list generation with send-back instructions) and re-entrancy (existing engagement detected and resumed; returned answers ingested into `discovery/client-answers.md`; downstream stages marked `stale` when late answers contradict locked requirements).
- **AC4** — `cpo-prd.md` caps Codex review at 2 rounds, reads the verdict only from the report file (silence ≠ approval), upserts the round digest as an idempotent engagement-issue comment, and carries the over-cap AskUserQuestion gate (one more round / accept-with-noted-gaps / needs-human).
- **AC5** — All nine engagement templates exist inside their owning skills: `cpo-question-bank/templates/{question-list,requirements,status}.md`, `cpo-prd-standard/templates/prd.md`, `cpo-design-standard/templates/{project-brief,sitemap-and-flows,section-briefs,copy-deck,brand-inputs}.md`.
- **AC6** — The three rules files exist under `.claude/rules/c-suite/` (`roster.md`, `cpo-operations.md`, `cpo-lessons.md`), each with `paths:` frontmatter (path-scoped, not always-loaded), and `roster.md` marks every seat human or AI including the human prototype-owner seat.
- **AC7** — The three knowledge skills pass the meta-skills validator and their frontmatter blocks auto-invocation.
- **AC8** — The five persona agents under `.claude/agents/cpo/` pass the meta-agent validator, none lists `AskUserQuestion` in `tools`, and their `model` aliases match the roster (`opus` for PM and Design Lead, `sonnet` for the rest).
- **AC9** — `.agents/skills/prd-review/SKILL.md` mirrors the spec-review contract: first-line verdict `### Round N — Verdict: approved|changes-requested` (em-dash), single report file `products/<client-slug>/prd/reviews/codex-prd-review-round-N.md`, terse two-line CLI return, closing `**Issue-comment digest:**`, judges against `requirements.md` + the cpo-prd-standard structure, and never calls `gh`.
- **AC10** — `AGENTS.md` documents `products/` in Project Structure and points to the `.claude/rules/c-suite/` family and the `/c-suite:cpo-*` pipeline.
- **AC11** — The dry-run fixture `products/_example-bluebird-bakery/` is complete: locked `discovery/requirements.md`, `prd.md` with an `approved` verdict report in `prd/reviews/`, all six design-package files with at least one wireframe page, `status.md` showing every stage `done` and the engagement `handed-off`, and no wireframe references an external URL.

## Validation Commands

Run these to prove the criteria above. Map each command to the criteria it verifies.

- `for f in cpo-intake cpo-prd cpo-brief; do for s in "## Variables" "## Instructions" "## Workflow"; do grep -q "^$s" ".claude/commands/c-suite/$f.md" || echo "FAIL $f missing $s"; done; done; echo checked` — verifies AC1. A pass prints only `checked`.
- `claude -p 'Reply with only the names of available skills that start with "c-suite:", one per line.' | grep -c "c-suite:cpo-"` — verifies AC2 (command resolution). A pass prints `3`.
- `grep -Eq "autoInvoke: *false|disable-model-invocation: *true" .claude/skills/cpo-question-bank/SKILL.md .claude/skills/cpo-prd-standard/SKILL.md .claude/skills/cpo-design-standard/SKILL.md && echo PASS` — verifies AC2/AC7 (no auto-fire).
- `grep -q "ASYNC" .claude/commands/c-suite/cpo-intake.md && grep -q "client-answers.md" .claude/commands/c-suite/cpo-intake.md && grep -q "stale" .claude/commands/c-suite/cpo-intake.md && echo PASS` — verifies AC3.
- `grep -q "2 rounds\|round 2\|MAX.*2" .claude/commands/c-suite/cpo-prd.md && grep -q "needs-human" .claude/commands/c-suite/cpo-prd.md && echo PASS` — verifies AC4.
- `for t in cpo-question-bank/templates/question-list.md cpo-question-bank/templates/requirements.md cpo-question-bank/templates/status.md cpo-prd-standard/templates/prd.md cpo-design-standard/templates/project-brief.md cpo-design-standard/templates/sitemap-and-flows.md cpo-design-standard/templates/section-briefs.md cpo-design-standard/templates/copy-deck.md cpo-design-standard/templates/brand-inputs.md; do test -f ".claude/skills/$t" || echo "FAIL $t"; done; echo checked` — verifies AC5. A pass prints only `checked`.
- `for r in roster cpo-operations cpo-lessons; do head -5 ".claude/rules/c-suite/$r.md" | grep -q "paths:" || echo "FAIL $r"; done; echo checked` — verifies AC6. A pass prints only `checked`.
- `uv run .claude/skills/meta-skills/scripts/quick_validate.py .claude/skills/cpo-question-bank .claude/skills/cpo-prd-standard .claude/skills/cpo-design-standard` — verifies AC7 (builder confirms exact invocation against the script's usage).
- `uv run .claude/skills/meta-agent/scripts/validate_agent.py .claude/agents/cpo/*.md && ! grep -l "AskUserQuestion" .claude/agents/cpo/*.md && echo PASS` — verifies AC8.
- `head -20 .agents/skills/prd-review/SKILL.md | grep -q "prd-review" && grep -q "Verdict: approved" .agents/skills/prd-review/SKILL.md && grep -q "Issue-comment digest" .agents/skills/prd-review/SKILL.md && echo PASS` — verifies AC9.
- `grep -q "products/" AGENTS.md && grep -q "c-suite" AGENTS.md && echo PASS` — verifies AC10.
- `test -f products/_example-bluebird-bakery/prd/prd.md && grep -q "Verdict: approved" products/_example-bluebird-bakery/prd/reviews/*.md && grep -q "handed-off" products/_example-bluebird-bakery/status.md && ls products/_example-bluebird-bakery/design/wireframes/*.html >/dev/null && ! grep -rE "https?://" products/_example-bluebird-bakery/design/wireframes/ && echo PASS` — verifies AC11.
