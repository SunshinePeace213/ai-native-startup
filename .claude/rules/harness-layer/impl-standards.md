---
paths:
  - "specs/**/*"
---

# Implementation Standards

The bar every implementation diff must clear before its PR leaves draft. Builders
and the build lead self-check the diff against it before opening the PR; the Codex
gate judges against the same list. A build that meets every standard passes review
round 1 — fix gaps here, before review, not after.

1. **Plan fidelity** — the diff implements the plan's tasks exactly: every task's
   change present, nothing beyond the locked decisions, non-goals untouched. An
   undocumented divergence from the plan is a defect.
2. **Acceptance evidence** — every command in acceptance-criteria.md
   `## Validation Commands` passes from the repo root, and each `manual:` check has
   its output recorded in `implementation-notes.md`. A criterion with no passing
   check is a promise, not evidence.
3. **Verification honesty** — every hand-off entry in `implementation-notes.md`
   records the exact commands run and their observed results. A claim with no
   recorded evidence fails.
4. **Harness file quality** — changed files under `.claude/` read as fluent, KISS
   prose: instructions not rationale, no stray cross-refs, no guidance duplicated
   from a rule that already loads.
5. **Grounding** — under the `kb-grounded` profile, every harness-behavior claim
   the diff relies on (frontmatter fields, hook events, model aliases, command
   resolution) traces to a `## KB References` doc, never memory.
6. **Scope hygiene** — no orphaned imports, variables, or functions the change
   made unused; no drive-by refactors or unrequested features. Every changed line
   traces to a task.
7. **Convention compliance** — commits follow git-workflow.md (emoji + type
   subject, `Refs #N` footer); the PR body matches pr-process.md (stage table,
   task manifest, `Closes #N`).
8. **Test intent** — a bug fix carries the failing test that reproduces it; no
   test or check hard-codes values or special-cases inputs to pass.

When a gate finding exposes a standard this list is missing or states unclearly,
amend this file in the same run — that is the self-improve step.
