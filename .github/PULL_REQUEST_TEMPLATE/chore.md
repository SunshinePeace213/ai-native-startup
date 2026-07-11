<!--
PR title convention (carry the gitmoji to match the commit):
  🔧 chore(<scope>): <short description in imperative mood>
Chores (deps, config, tooling) often need no CI run — append a bypass token when warranted:
  🔧 chore(<scope>): <desc> [skip-ci]   or   [skip-drift-check]
-->

## Summary

<!-- The maintenance change and why it's needed now. 1-3 sentences. -->

## Scope

<!-- What this touches: dependency bumps, config, build tooling, CI, housekeeping. Bullet the files/areas. -->

-
-

## Rationale

<!-- Why this chore matters (security, upkeep, unblocking other work). -->

## Test Evidence

<!-- Commands run + observed results (build/CI green, or N/A). -->

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
