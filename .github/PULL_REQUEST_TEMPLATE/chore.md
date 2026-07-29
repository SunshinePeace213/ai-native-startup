<!-- PR title: 🔧 chore(<scope>): <short description in imperative mood> -->

## Summary

<!-- The maintenance change and why it is needed now. 1-3 sentences. -->

## Plan

<!-- Blob links to the plan's spec.md / tasks.md / decisions.md / acceptance-criteria.md. -->

Closes #<issue>

<!-- `Refs #<issue>` links without closing; `Part of #<epic>` for an epic child. -->

## Scope

<!-- What this touches: dependency bumps, config, build tooling, CI, housekeeping. -->

-
-

## Rationale

<!-- Why this chore matters (security, upkeep, unblocking other work). -->

## Test Evidence

<!-- Commands run + observed results. "N/A" with a reason when nothing is runnable. -->

## Risk & Rollback

<!-- What could break, how to detect it, how to roll back. "None" is allowed. -->

None.

## Agent Task Manifest

<!-- One row per Agent Task from TaskList at build time. Task IDs stay bare kebab-case —
     never `#N`, which GitHub autolinks to an unrelated issue. -->

| task | owner | done | verification | notes |
| --- | --- | --- | --- | --- |
| `<kebab-case-task-id>` <subject> | <owner> | ☐ | <how verified> | |

## Build Status

<!-- Updated live by /harness-layer:harness-build and /harness-layer:harness-review.
     Status: pending / done / N/A. The Ready row's Evidence is the approved head SHA —
     /harness-layer:harness-ship passes it to `gh pr merge --match-head-commit`, so a
     wrong value aborts the merge. -->

| Stage | Status | Evidence |
| --- | --- | --- |
| Implementation | pending | |
| Tidy | pending | |
| Codex R1 | pending | |
| Fixes (if required) | pending | |
| Codex R2+ delta (if required) | pending | |
| Ready | pending | |

## Review Reports

<!-- One link per marker comment as it lands (tidy, then each Codex round). Each comment
     states the head SHA it reviewed. -->

## Dev Notes

<!-- Links to the build brief and dev report pages under specs/<name>/artifacts/. -->

## Follow-ups

<!-- Review advisories, one unchecked box each. Each is filed as its own issue or dropped. -->
