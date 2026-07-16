---
description: Draft the client PRD (PM draft → CPO consistency pass) and gate it through two automatic Codex prd-review rounds before the design brief; Workflow 1b of the c-suite CPO pipeline
argument-hint: <client-slug>
---

# CPO PRD

Turn the locked `discovery/requirements.md` into `prd/prd.md`, then gate it through the
Codex `prd-review` skill. Deploy `PM` (Ethan Park) to draft against the `cpo-prd-standard`
skill, run a CPO consistency pass, then two automatic review rounds reading the verdict
only from the report file. Real mode upserts each round's digest onto the engagement issue
and commits with `Refs #N`; fixture mode keeps the reports local and commits on the hosting
branch. Workflow 1b.

## Variables

CLIENT_SLUG: $1 — engagement slug; same rule as intake
PRD_STANDARD_SKILL: `${CLAUDE_PROJECT_DIR}/.claude/skills/cpo-prd-standard/SKILL.md`
TEMPLATE_PRD: `${CLAUDE_PROJECT_DIR}/.claude/skills/cpo-prd-standard/templates/prd.md`
PM: `cpo-pm` — Ethan Park
REVIEW_SKILL: `prd-review` — the Codex review skill at `.agents/skills/prd-review/`
REPORT_FILE: `products/<client-slug>/prd/reviews/codex-prd-review-round-N.md`
REQUIREMENTS: `products/<client-slug>/discovery/requirements.md`
LESSONS_FILE: `.claude/rules/c-suite/cpo-lessons.md`

## Instructions

- **Preflight the ledger.** Read `products/<client-slug>/status.md`: `intake` must be
  `done`, else STOP. If any stage is `stale`, get explicit user confirmation
  (AskUserQuestion) before proceeding — never silently resume on stale input.
- **Validate the slug** with intake's rule `^[a-z0-9][a-z0-9-]{0,38}[a-z0-9]$` (fixture
  `_example-` exception) before any side effect, and double-quote every interpolation.
- **Codex model and effort** for `REVIEW_SKILL` come from `.claude/rules/model-selection.md`
  at run time — pick per the PRD's complexity, never hardcoded.
- `Verdict source: report file only` — read each round's verdict from `REPORT_FILE` (grep
  its first line), NEVER from stdout. `Silence: not approval` — a round that writes no
  verdict line is re-run, never treated as approval.
- The `cpo-prd-standard` skill holds the structure and quality bar; the review judges
  against it. Deliverables stay professional client-grade prose; persona names sign reports
  only.

## Workflow

1. **Preflight and validate.** Ledger gate + slug validation per Instructions. STOP on any
   failure.
2. **Draft the PRD.** Deploy `PM` (Ethan Park) to draft `prd/prd.md` from `REQUIREMENTS`.
   The delegation brief carries `PRD_STANDARD_SKILL` and `TEMPLATE_PRD` and instructs Ethan
   to Read `PRD_STANDARD_SKILL` FIRST — the complete fallback when `skills:` preloading is
   unavailable, so he never drafts from a blank form.
3. **CPO consistency pass.** The CPO (this session) checks `prd/prd.md` against
   `REQUIREMENTS` — every locked dimension covered, no scope drift, metrics measurable,
   stories carrying acceptance criteria — before review.
4. **Codex gate — `Automatic rounds: 1, 2`.** For each round N in 1, 2: run `codex exec`
   with `REVIEW_SKILL`, injecting only the round number; pick the Codex model/effort from
   model-selection at run time. Read the verdict from `REPORT_FILE`
   (`grep -E '^### Round N — Verdict: (approved|changes-requested)$'`). A round with no
   verdict line is re-run.
   - Round 1 `approved` → gate passes; skip to exit.
   - Round 1 `changes-requested` → route the blocking findings to `PM` for a fix pass, then
     run round 2.
   - Round 2 `approved` → gate passes.
   - Round 2 `changes-requested` → the over-cap gate.
5. **Over-cap gate.** Round 2 still `changes-requested` → STOP and AskUserQuestion with
   exactly `Round 2 options: final-delta-round | accept-with-noted-gaps | needs-human`.
   - `final-delta-round` → run round 3, the LAST round, on the fix delta; if round 3 is
     still `changes-requested`, re-present only `Round 3 options: accept-with-noted-gaps | needs-human`.
   - `accept-with-noted-gaps` → record the noted gaps in `status.md` and pass with them.
   - `needs-human` → escalate (real mode adds the label).
6. **Exit per mode.** Run the lessons check and record `lessons=<result>` in the `prd-run`
   log (`none` allowed).
   - **Real mode:** upsert each round's `**Issue-comment digest:**` as the idempotent
     engagement-issue comment keyed `<!-- prd-review-round-N -->` — list the issue's
     comments, PATCH the existing one if the marker is found, else create it (the
     harness-build upsert pattern). Apply the `status:needs-human` label ONLY when that
     exit is selected. Update the real trail, commit with a `Refs #N` footer, and push the
     explicit engagement refspec; open no PR.
   - **Fixture mode:** create no issue comment, label, PR, or any `gh` action; retain the
     reports locally under `prd/reviews/`; record the selected gate outcome in `status.md`;
     commit on the recorded hosting branch WITHOUT `Refs #N` or push; record the commit SHA
     in the `prd-run` log.

## Trail contract

`Real trail: issue=existing; comments=upsert review digest; labels=needs-human only; commit=Refs #N; push=engagement branch; PR=none`
`Fixture trail: issue=none; comments=none; labels=none; commit=current branch + recorded SHA; push=none; PR=none`

## Report

Print: the mode, the engagement folder, each round's verdict and report path, the final
gate outcome (approved at round N | accept-with-noted-gaps | needs-human), the `prd` stage
state, the recorded `prd-run` log line, and the next step — `/c-suite:cpo-brief <client-slug>`
once the PRD is approved.
