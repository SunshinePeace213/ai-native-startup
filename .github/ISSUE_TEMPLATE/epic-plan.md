---
name: Epic / Plan
about: Track a multi-step plan and its /plan-w-team → /build lifecycle
title: "📋 epic: "
labels: epic
---

<!-- This issue is the durable spine for one planned unit of work. It is created
by `/plan-w-team` at plan draft (after sign-off) and is the single join key
(#N) that threads the branch, commits, and PR together. -->

## Objective

<!-- The outcome this epic delivers, in one or two sentences. Mirror the
Objective from the plan. When every child task and acceptance criterion below is
satisfied, this objective is met. -->

## Link to plan

<!-- The committed planning files for this epic. -->

- Plan: `specs/<feature>/plan.md`
- Decisions: `specs/<feature>/decisions.md`

## Child task checklist

<!-- The plan's step-by-step tasks, mirrored from `TaskList`. Each item should
reference its PR with `Part of #<this-issue>`. Check items off as the builders
complete them. -->

- [ ]
- [ ]
- [ ]

## Spec-review status

<!-- Codex spec-review runs verdict-only; the orchestrator (Claude) relays each
round's verdict here as a comment on this issue. Track the latest state below. -->

- Latest verdict: _pending_  <!-- approved | changes-requested -->
- Round comments: see the issue thread below.

## Acceptance criteria

<!-- Epic-level "done" conditions — the rollup of the plan's Acceptance
Criteria. The PR that closes this epic must satisfy all of them. -->

- [ ]
- [ ]
