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

## Behavior-preservation note / Test Plan

<!-- State that external behavior is unchanged, and how that's verified (existing tests green, before/after parity). -->

- [ ] No change to public behavior or API surface.
- [ ] Existing tests pass unchanged.

## Linked Issue

Closes #<issue>

<!-- `Refs #<issue>` for related-but-not-closing links; `Part of #<epic>` for an epic child. -->

## Agent Task Manifest

<!-- Copied verbatim from TaskList at build time. Format: - [ ] #<taskId> <subject> — <owner> — <status> -->

- [ ] #<taskId> <subject> — <owner> — <status>

## Build Status

<!-- Checked off live by /build as each phase completes. -->

- [ ] Implementation
- [ ] Internal check
- [ ] Claude code review
- [ ] Codex review R1
- [ ] Fixes
- [ ] Codex review R2
- [ ] Result
