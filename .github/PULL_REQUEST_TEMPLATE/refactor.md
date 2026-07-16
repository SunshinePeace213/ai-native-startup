<!--
PR title convention (carry the gitmoji to match the commit):
  ♻️ refactor(<scope>): <short description in imperative mood>
Append a bypass token to the title only when warranted, e.g.
  ♻️ refactor(<scope>): <desc> [skip-drift-check]
-->

## Summary

<!-- What was restructured. 2-3 sentences. -->

## Motivation

<!-- Why this refactor is worth doing now (readability, coupling, prep for upcoming work). -->

## Changes

<!-- Bullet the structural moves: renames, extractions, file moves, dependency changes. -->

-
-

## Behavior-preservation note

<!-- State that external behavior is unchanged, and how that's verified (existing tests green, before/after parity). -->

- [ ] No change to public behavior or API surface.
- [ ] Existing tests pass unchanged.

## Test Evidence

<!-- Commands run + observed results (counts, green run, output). -->

## Risk & Rollback

<!-- What could break, how to detect it, how to roll back. "None" is allowed. -->

None.

## Linked Issue

Closes #<issue>

<!-- `Refs #<issue>` for related-but-not-closing links; `Part of #<epic>` for an epic child. -->

## Agent Task Manifest

<!-- One row per Agent Task from TaskList at build time. -->

| task | owner | done | verification | notes |
| --- | --- | --- | --- | --- |
| #<taskId> <subject> | <owner> | ☐ | <how verified> | |

## Build Status

<!-- Updated live by /harness-layer:harness-build. Status: pending / done / N/A. Evidence: commit SHA, report-comment link, or N/A. -->

| Stage | Status | Evidence |
| --- | --- | --- |
| Implementation | pending | |
| Tidy | pending | |
| Codex R1 | pending | |
| Fixes (if required) | pending | |
| Codex R2+ delta (if required) | pending | |
| Ready | pending | |

## Review Reports

<!-- Links to the marker comments on this PR (upserted, each states the reviewed head SHA). -->

- Tidy — `<!-- report:tidy -->`
- Codex R1 — `<!-- report:codex-round-1 -->`
- Codex R2+ — `<!-- report:codex-round-N -->` — one entry per delta round (if required)

## Reviewer Checklist

- [ ] Intent & scope match the linked issue
- [ ] Validation evidence present and green
- [ ] Rollback plan is plausible
- [ ] Security / data / deployment impact considered
