<!--
PR title convention (carry the gitmoji to match the commit):
  🎨 style(<scope>): <short description in imperative mood>
Formatting-only changes don't alter behavior — append [skip-ci] to the title when no build is needed:
  🎨 style(<scope>): <desc> [skip-ci]
-->

## Summary

<!-- What was restyled and why (formatting, whitespace, import order, etc.). 1-3 sentences. -->

## Changes

<!-- Bullet the formatting changes. NOTE: style PRs must contain NO logic changes. -->

- Formatting only — no logic, behavior, or API changes.
-

## Test Evidence

<!-- Commands run + observed results (formatter/linter clean, or N/A). -->

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
