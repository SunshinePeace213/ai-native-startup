<!--
PR title convention (carry the gitmoji to match the commit):
  🐛 fix(<scope>): <short description in imperative mood>
Append a bypass token to the title only when warranted, e.g.
  🐛 fix(<scope>): <desc> [skip-ci]   or   [skip-drift-check]
-->

## Summary

<!-- What was broken and what this PR fixes. 2-4 sentences. -->

## Root cause

<!-- The underlying reason for the bug, not just the symptom. -->

## Repro steps

<!-- The exact steps that triggered the bug before this fix. -->

1.
2.
3.

## Fix

<!-- What was changed to address the root cause. -->

-

## Regression test

<!-- The test that fails before the fix and passes after. Name it and show how to run it. -->

- [ ]

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

<!-- Updated live by /build. Status: pending / done / N/A. Evidence: commit SHA, report-comment link, or N/A. -->

| Stage | Status | Evidence |
| --- | --- | --- |
| Implementation | pending | |
| Tidy | pending | |
| Internal code-review | pending | |
| Codex R1 | pending | |
| Fixes (if required) | pending | |
| Codex R2 delta (if required) | pending | |
| Ready | pending | |

## Review Reports

<!-- Links to the marker comments on this PR (upserted, each states the reviewed head SHA). -->

- Tidy — `<!-- report:tidy -->`
- Code review — `<!-- report:code-review -->`
- Codex R1 — `<!-- report:codex-round-1 -->`
- Codex R2 — `<!-- report:codex-round-2 -->` (if required)

## Reviewer Checklist

- [ ] Intent & scope match the linked issue
- [ ] Validation evidence present and green
- [ ] Rollback plan is plausible
- [ ] Security / data / deployment impact considered
