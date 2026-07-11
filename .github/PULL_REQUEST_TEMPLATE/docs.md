<!--
PR title convention (carry the gitmoji to match the commit):
  📝 docs(<scope>): <short description in imperative mood>
Docs-only changes rarely affect runtime — append [skip-ci] to the title when no build is needed:
  📝 docs(<scope>): <desc> [skip-ci]
-->

## Summary

<!-- What documentation changed and why. 1-3 sentences. -->

## Changes

<!-- Bullet the docs added/updated/removed (files, sections). -->

-
-

## Test Evidence

<!-- Commands run + observed results (link checks, doc build, or N/A). -->

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
| Codex R2+ delta (if required) | pending | |
| Ready | pending | |

## Review Reports

<!-- Links to the marker comments on this PR (upserted, each states the reviewed head SHA). -->

- Tidy — `<!-- report:tidy -->`
- Code review — `<!-- report:code-review -->`
- Codex R1 — `<!-- report:codex-round-1 -->`
- Codex R2+ — `<!-- report:codex-round-N -->` — one entry per delta round (if required)

## Reviewer Checklist

- [ ] Intent & scope match the linked issue
- [ ] Validation evidence present and green
- [ ] Rollback plan is plausible
- [ ] Security / data / deployment impact considered
