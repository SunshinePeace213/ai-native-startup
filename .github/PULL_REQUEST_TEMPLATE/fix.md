<!--
PR title convention (carry the gitmoji to match the commit):
  [PR] 🐛 fix(<scope>): <short description in imperative mood>
Append a bypass token to the title only when warranted, e.g.
  [PR] 🐛 fix(<scope>): <desc> [skip-ci]   or   [skip-drift-check]
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

## Linked Issue

Closes #<issue>

<!-- `Refs #<issue>` for related-but-not-closing links; `Part of #<epic>` for an epic child. -->

## Agent Task Manifest

<!-- Copied verbatim from TaskList at build time. Format: - [ ] #<taskId> <subject> — <owner> — <status> -->

- [ ] #<taskId> <subject> — <owner> — <status>

## Build Status

<!-- Checked off live by /build as each phase completes. -->

- [ ] Implementation
- [ ] Codex review R1
- [ ] Fixes
- [ ] Codex review R2
- [ ] Result
