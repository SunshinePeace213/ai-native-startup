<!--
PR title convention (carry the gitmoji to match the commit):
  [PR] ✅ test(<scope>): <short description in imperative mood>
Test-only changes may skip downstream gates — append [skip-drift-check] to the title when warranted:
  [PR] ✅ test(<scope>): <desc> [skip-drift-check]
-->

## Summary

<!-- What testing this PR adds or strengthens. 1-3 sentences. -->

## Coverage added

<!-- Bullet the new/expanded tests: units, edge cases, regressions, the behavior each one pins down. -->

-
-

## How verified

<!-- The command(s) used to run the suite and the observed result (e.g. counts, green run). -->

```
<test command>
```

- [ ] All tests pass locally.

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
