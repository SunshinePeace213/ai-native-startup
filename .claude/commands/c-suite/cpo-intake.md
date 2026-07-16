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
REQUEST: $2 — (optional) the client's opening request, free text
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
- Deliverables stay professional client-grade prose; persona names sign reports only.

## Workflow

1. **Validate the slug.** Apply the rule above. STOP on violation before touching
   anything.
2. **Detect mode and preflight tools.** Fixture (`_example-`) vs real. STOP if `codex`
   is missing (both modes); in real mode also STOP if `gh auth status` fails.
3. **Resume existing engagement** or scaffold. If `products/<client-slug>/` already
   exists, resume it — read `status.md`, keep its recorded mode and trail, and continue
   from where discovery stands. Otherwise scaffold `products/<client-slug>/` (`status.md`,
   `discovery/`, `prd/`, `design/`) from the question-bank templates: `status.md` from
   `TEMPLATE_STATUS`, and the `discovery/question-list.md` and `discovery/requirements.md`
   skeletons from `TEMPLATE_QUESTION_LIST` and `TEMPLATE_REQUIREMENTS`.
4. **Set the mode trail.**
   - **Real mode:** create the engagement issue, its linked branch
     `feat/<N>-<client-slug>`, and a worktree; fill the ledger `mode: real`, `issue: #N`,
     `branch: feat/<N>-<client-slug>`, `hosting-branch: none`. Create no comment, label,
     or PR.
   - **Fixture mode:** create no issue, comment, label, branch, worktree, or PR and run
     no `gh` action; stay on the current branch; fill `mode: fixture`, `issue: none`,
     `branch: none`, `PR: none`, and the current branch under `hosting-branch:`.
5. **Choose the discovery mode.** AskUserQuestion: **LIVE** or **ASYNC**.
   - **LIVE:** grill every question-bank dimension via AskUserQuestion — batched, the
     recommended answer first — until each dimension meets its "locked when" criterion,
     writing each into `discovery/requirements.md` as `- <dimension>: locked`.
   - **ASYNC:** deploy `UX_RESEARCHER` (Priya Nair) to generate
     `discovery/question-list.md`, then STOP with send-to-client instructions: hand the
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
   - **Fixture mode:** update the ledger state and `intake-run` log, commit on the current
     branch WITHOUT `Refs #N` and without pushing, and record that commit's SHA in the
     `intake-run` log.

## Trail contract

`Real trail: issue=create; comments=none; labels=none; commit=Refs #N; push=engagement branch; PR=none`
`Fixture trail: issue=none; comments=none; labels=none; commit=current branch + recorded SHA; push=none; PR=none`

## Report

Print: the mode (real | fixture), the engagement folder, the discovery mode taken
(LIVE | ASYNC), each dimension's locked/open state, the `intake` stage state, the recorded
`intake-run` log line, and the next step — `/c-suite:cpo-prd <client-slug>` once intake is
done, or the send-to-client wait when ASYNC stopped.
