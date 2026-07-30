---
paths:
  - "specs/**/*"
---

# Spec Standards

The bar every plan under `specs/<name>/` must clear. The drafting agent self-checks
against it before requesting review; the Codex gate judges against the same list.
A draft that meets every standard passes review round 1 — fix gaps here, before
review, not after.

1. **Traceability** — every requirement in spec.md maps to a task in tasks.md, and
   every task names the `AC#` it satisfies. An objective with no implementing step
   is a defect.
2. **Testability** — every acceptance criterion is observable and backed by a
   command that fails when the change is reverted: the project's own suite, a
   checked-in validator, or a plan-local script under `specs/<name>/checks/`. A
   shape stated in `## Interfaces & Contracts` is asserted by one of them. A task
   that changes behavior names the test it adds or extends in its **Files**, at the
   tier [test-tiers.md](test-tiers.md) assigns. No "works well" or "feels fast".
3. **Feasibility & ordering** — every step can run as written, and prerequisites
   come before their dependents.
4. **Scope fidelity** — the plan implements the locked decisions exactly: nothing
   missing, nothing beyond them, nothing marked out-of-scope or non-goal.
5. **Consistency** — no two requirements contradict, and no requirement contradicts
   a locked decision.
6. **Grounding** — under the `kb-grounded` profile, every claim about harness
   behavior (hooks, frontmatter, subagents, skills, commands, MCP, model aliases)
   cites a source in decisions.md `## KB References`: a cached `ai-docs/` file, or
   a checked-in authoritative reference under `.claude/skills/meta-skills/references/`
   (`frontmatter.md`, `command-format.md`, `schemas.md`) where the KB has no mirror
   for that surface. Cite the file and line; memory is never a source. When neither
   has it, say so explicitly and name the `/harness-layer:kb add` follow-up rather
   than asserting the behavior.
7. **Tracking hygiene** — spec.md `## Tracking` records the change type,
   complexity, Issue `#N`, the convention branch `<type>/<N>-<slug>` carrying the
   same number, the worktree path, and the review profile. No placeholders.
8. **Simplicity** — the simplest design that meets the objective. Collapse
   near-identical tasks; cut abstractions and steps the objective doesn't need.

When a Codex gate finding exposes a standard this list is missing or states
unclearly, amend this file in the same run — that is the self-improve step.
