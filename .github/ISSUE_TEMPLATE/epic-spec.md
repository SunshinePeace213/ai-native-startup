---
name: Epic / Plan
about: Track a multi-step plan through its /plan-w-team → /build → /ship lifecycle
title: "📋 epic: "
labels: epic
---

<!-- This issue is the durable spine for one planned unit of work, created by
`/plan-w-team` after sign-off. #N is the single join key threading the branch,
commits, and PR together. The BODY mirrors plan-phase state (kept current); the
COMMENT THREAD is the append-only history of how we got here. -->

## Objective

<!-- The outcome this epic delivers, in one or two sentences. Mirror the
Objective from the plan's spec.md. -->

## Non-Goals

<!-- The scope fence — what this epic deliberately does NOT do, so /build does
not gold-plate. One bullet per non-goal. -->

-

## Lifecycle

<!-- The macro phase line. Move the ▲ marker as the work advances. The plan
phase is owned here; Build and Ship are owned by the PR (Closes #N closes this
issue on merge). -->

`Plan ▸ Spec-review ▸ Approved ▸ Build ▸ Ship ▸ Done`
▲ current phase: **Plan**

## Link to plan

<!-- Path-as-text markdown links to all four plan files: the display text is the
repo path and the href is the blob URL on the convention branch (resolves
pre-merge, never against main). Filled by /plan-w-team after the first push. -->

- Spec: [specs/<plan-name>/spec.md](<blob-url-on-convention-branch>)
- Tasks: [specs/<plan-name>/tasks.md](<blob-url-on-convention-branch>)
- Acceptance: [specs/<plan-name>/acceptance-criteria.md](<blob-url-on-convention-branch>)
- Decisions: [specs/<plan-name>/decisions.md](<blob-url-on-convention-branch>)

## Spec-review status

<!-- Live state-mirror of the Codex spec-review loop, overwritten in place each
round (never appended). The per-round detail is the append-only comment thread. -->

- Latest verdict: _pending_ <!-- approved | changes-requested -->
- Status: _Drafted for Review_ <!-- Drafted for Review | Approved ✅ | Needs Human Review ⚠️ -->
- History: see thread ↓

## Acceptance criteria

<!-- A pointer to the plan's acceptance-criteria.md — NOT a mirrored checklist
(the PR owns build-time tick-off). -->

See `specs/<plan-name>/acceptance-criteria.md`.

## Open Questions

<!-- Deferred decisions or anything still in discussion. Use this issue as the
discussion surface; resolve before /build where possible. -->

-

## How to act

<!-- The next command in the lifecycle. -->

- Build the plan: `/build <plan-name>`
- Then ship the PR: `/ship`
