# Summary: <plan name>

> What this plan actually shipped, for the next agent or developer who needs to know
> without reading [spec.md](./spec.md). Written by `/harness-layer:harness-review` at
> its terminal step, from the implementation notes and the findings ledger. Outcome,
> not intent — if the build diverged from the plan, this file records what was built.

**Issue** #<N> · **PR** #<M> · **Status** <shipped | blocked>

## What Shipped

<!-- 2-4 sentences in plain prose. What exists now that did not before, and what a
     reader can do with it. No task-by-task replay. -->

## Acceptance Criteria → Evidence

<!-- One row per AC. Command is the runnable identifier from acceptance-criteria.md
     (pytest node id or checks/ script). Result is what was observed, not "passes". -->

| AC | What it proves | Command | Result |
| --- | --- | --- | --- |
| AC1 | <…> | `<node id or script>` | <observed> |

## Decisions Locked

<!-- One line per decision a future change must not silently reverse, with its reason.
     Pull from decisions.md, keeping only what still constrains the code. -->

-

## Interfaces

<!-- Anything another component now depends on: file paths, hook events, commands,
     config keys, function signatures. Omit the section when nothing is exposed. -->

-

## Follow-ups

<!-- Advisories and deferred work, each as its own line with its issue number if filed.
     "None" is a valid answer. -->

-

## Lessons Routed

<!-- Where each memory-marked lesson landed (rule file or command), one line each, so a
     later reader can trace a convention back to the run that created it. -->

-

## Metrics

<!-- The run's process telemetry, read by the lessons pass and mirrored into
     specs/lessons/digest.md at ship time. Every number comes from the findings
     ledger, the lint output, and the round reports — never memory. Keep the
     labels exactly as written. -->

- **Lane:** <full | direct>
- **Spec gate:** <N> cycles (<X> blocking, <Y> advisory) · **Impl gate:** <N> cycles (<X> blocking, <Y> advisory)
- **Findings by standard:** <`S1×1 I2×2 …`, or "none">
- **Uncited→advisory:** <count of findings recorded advisory for citing no standard>
- **Fix commits:** <count> · **Unverified tail:** <yes | no> · **Disputed:** <count> · **Overridden:** <count>
- **Lint catches (pre-Codex):** spec <count>, impl <count>
