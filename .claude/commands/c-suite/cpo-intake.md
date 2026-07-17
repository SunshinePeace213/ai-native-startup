---
description: Scaffold a client engagement and run dual-mode discovery — LIVE grilling or ASYNC question list — until every requirements dimension locks; Workflow 1a of the c-suite CPO pipeline
argument-hint: <client-slug> [request…]
---

# CPO Intake

Stand up the `products/<client-slug>/` engagement, then drive discovery until every
question-bank dimension locks into `discovery/requirements.md`. Validate `CLIENT_SLUG`
first, pick real or fixture mode, scaffold or resume the engagement, then run LIVE or
ASYNC discovery against the `cpo-question-bank` skill. Re-entrant runs ingest returned
answers, re-lock changed dimensions, and stale downstream stages. This is Workflow 1a:
the CPO (this session) orchestrates and deploys `UX_RESEARCHER` — it never interviews as
a persona itself.

## Variables

CLIENT_SLUG: $1 — engagement slug; must match `^[a-z0-9][a-z0-9-]{0,38}[a-z0-9]$`
REQUEST: the remainder of `$ARGUMENTS` after CLIENT_SLUG — (optional) the client's
  opening request, free text. Bind it from `$ARGUMENTS` (the full argument text), not `$2`,
  which captures only the first token; an omitted request stays valid.
QUESTION_BANK_SKILL: `${CLAUDE_PROJECT_DIR}/.claude/skills/cpo-question-bank/SKILL.md`
TEMPLATE_QUESTION_LIST: `${CLAUDE_PROJECT_DIR}/.claude/skills/cpo-question-bank/templates/question-list.md`
TEMPLATE_REQUIREMENTS: `${CLAUDE_PROJECT_DIR}/.claude/skills/cpo-question-bank/templates/requirements.md`
TEMPLATE_STATUS: `${CLAUDE_PROJECT_DIR}/.claude/skills/cpo-question-bank/templates/status.md`
ENGAGEMENT_DIR: `products/<client-slug>/`
UX_RESEARCHER: `cpo-ux-researcher` — Priya Nair
LESSONS_FILE: `.claude/rules/c-suite/cpo-lessons.md`

## Instructions

- **Validate the slug before any side effect.** `CLIENT_SLUG` must match
  `^[a-z0-9][a-z0-9-]{0,38}[a-z0-9]$`; a fixture slug is `_example-` followed by an
  otherwise-valid slug (e.g. `_example-bluebird-bakery`). Run this check BEFORE any
  filesystem, branch, worktree, or `gh` action — no scaffolding, no `gh auth`, nothing.
  On violation STOP, show the rule and the offending value, and create nothing.
- **Quote every interpolation.** Every shell use of the slug is double-quoted
  (`"$CLIENT_SLUG"`, `products/"$CLIENT_SLUG"/`) so a hostile value can never break out.
- **Mode detection.** A leading `_example-` means fixture mode; any other valid slug
  means real mode. Missing `codex` STOPs in both modes; missing `gh` (or a failed
  `gh auth status`) STOPs real mode only — fixture mode performs no `gh` action at all.
- **Load the knowledge skill.** Load `QUESTION_BANK_SKILL` (the `cpo-question-bank`
  skill) before discovery — it holds the twelve dimensions, their questions, and each
  "locked when" criterion.
- **Never invent answers.** An unanswered dimension stays `open`; when the client owes
  it, the stage is `blocked-on-client`.
- **Consume the opening request.** When `REQUEST` is present, record it into the
  engagement's discovery record and use it to seed or pre-answer dimensions in both LIVE
  grilling and the ASYNC question list; an omitted request stays valid.
- Deliverables stay professional client-grade prose; persona names sign reports only.

## Workflow

1. **Validate the slug.** Apply the rule above. STOP on violation before touching
   anything.
2. **Detect mode and preflight tools.** Fixture (`_example-`) vs real. STOP if `codex`
   is missing (both modes); in real mode also STOP if `gh auth status` fails.
3. **Resume existing engagement** — mode-aware resume lookup, run BEFORE any creation.
   - **Fixture:** if `products/<client-slug>/` exists on the current branch, resume it —
     read `status.md`, keep its recorded mode and trail, and continue from where discovery
     stands.
   - **Real:** resume only when exactly ONE matching engagement surface exists — an existing
     engagement worktree, or a local/remote `feat/*-<client-slug>` branch; enter that
     worktree and continue from its `status.md`. A real `products/<client-slug>/` found
     outside its engagement worktree is never resumable → STOP for reconciliation. More than
     one match → STOP.
4. **Scaffold a new engagement and set the mode trail.** Only when step 3 found nothing to
   resume.
   - **Real mode:** create the engagement issue, its linked branch `feat/<N>-<client-slug>`,
     and its worktree; ENTER that worktree; only THEN scaffold `products/<client-slug>/`
     there. Fill the ledger `mode: real`, `issue: #N`, `branch: feat/<N>-<client-slug>`,
     `hosting-branch: none`. Create no comment, label, or PR.
   - **Fixture mode:** stay on the current branch — create no issue, comment, label, branch,
     worktree, or PR and run no `gh` action — then scaffold `products/<client-slug>/` on the
     current branch. Fill `mode: fixture`, `issue: none`, `branch: none`, `PR: none`, and the
     current branch under `hosting-branch:`.
   Scaffold `products/<client-slug>/` (`status.md`, `discovery/`, `prd/`, `design/`) from the
   question-bank templates: `status.md` from `TEMPLATE_STATUS`, and the
   `discovery/question-list.md` and `discovery/requirements.md` skeletons from
   `TEMPLATE_QUESTION_LIST` and `TEMPLATE_REQUIREMENTS`. Record `REQUEST` (when present) into
   the discovery record as the client's opening request, so both discovery modes seed from it.
5. **Choose the discovery mode.** AskUserQuestion: **LIVE** or **ASYNC**. Seed both from
   `REQUEST` when present — pre-answer or narrow any dimension the opening request already
   speaks to, and never re-ask what it settles.
   - **LIVE:** grill every question-bank dimension via AskUserQuestion — batched, the
     recommended answer first, `REQUEST`-seeded dimensions pre-filled for confirmation —
     until each dimension meets its "locked when" criterion, writing each into
     `discovery/requirements.md` as `- <dimension>: locked`.
   - **ASYNC:** deploy `UX_RESEARCHER` (Priya Nair) to generate
     `discovery/question-list.md` — seeded from `REQUEST` so it omits or pre-answers what the
     opening request already covers — then STOP with send-to-client instructions: hand the
     client the question list and wait for `discovery/client-answers.md`.
6. **Ingest returned answers: discovery/client-answers.md.** On a re-entrant run with a
   `discovery/client-answers.md` present, deploy `UX_RESEARCHER` for gap analysis against
   the twelve dimensions, re-lock every changed dimension, and grill any that are still
   open. When a late answer contradicts an already-locked requirement, mark the downstream
   stages stale in `status.md`:
   - **Late-answer transition: prd -> stale**
   - **Late-answer transition: brief -> stale**
7. **Exit.** Set `intake: done` once all twelve dimensions lock (else the accurate
   `in-progress` / `blocked-on-client` state). Run the lessons check: if a pitfall hit
   this run, append its prevention rule to `LESSONS_FILE`; record the outcome in the run
   log as `lessons=<result>` (`none` allowed). Then per mode:
   - **Real mode:** update the ledger state and `intake-run` log, commit with a `Refs #N`
     footer, and push the explicit engagement refspec
     `git push origin HEAD:refs/heads/feat/<N>-<client-slug>`; create no comment, label,
     or PR.
   - **Fixture mode:** two commits on the current branch, neither pushed and both WITHOUT
     `Refs #N` — first the deliverable commit carrying this run's discovery artifacts, then
     the ledger commit carrying the state and `intake-run` log update. The `intake-run`
     `sha=` names the DELIVERABLE commit, never the ledger commit.

## Trail contract

`Real trail: issue=create; comments=none; labels=none; commit=Refs #N; push=engagement branch; PR=none`
`Fixture trail: issue=none; comments=none; labels=none; commit=current branch + recorded SHA; push=none; PR=none`

## Report

Print: the mode (real | fixture), the engagement folder, the discovery mode taken
(LIVE | ASYNC), each dimension's locked/open state, the `intake` stage state, the recorded
`intake-run` log line, and the next step — `/c-suite:cpo-prd <client-slug>` once intake is
done, or the send-to-client wait when ASYNC stopped.
