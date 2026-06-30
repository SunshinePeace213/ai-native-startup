<!--
PR title convention (carry the gitmoji to match the commit):
  ⚡️ perf(<scope>): <short description in imperative mood>
Append a bypass token to the title only when warranted, e.g.
  ⚡️ perf(<scope>): <desc> [skip-drift-check]
-->

## Summary

<!-- What got faster/lighter and the headline result. 2-3 sentences. -->

## Bottleneck

<!-- The measured hotspot this PR targets (where time/memory was spent, how it was profiled). -->

## Change

<!-- What was changed to remove the bottleneck. -->

-

## Benchmark before / after

<!-- Hard numbers. Same machine, same workload. -->

| Metric | Before | After | Delta |
| --- | --- | --- | --- |
|  |  |  |  |

How the benchmark was run:

```
<command>
```

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
