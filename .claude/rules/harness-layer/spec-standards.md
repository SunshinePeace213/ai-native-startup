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
2. **Testability** — every acceptance criterion is observable and backed by an
   executable script in `specs/<name>/checks/`. No "works well" or "feels fast".
3. **Feasibility & ordering** — every step can run as written, and prerequisites
   come before their dependents.
4. **Scope fidelity** — the plan implements the locked decisions exactly: nothing
   missing, nothing beyond them, nothing marked out-of-scope or non-goal.
5. **Consistency** — no two requirements contradict, and no requirement contradicts
   a locked decision.
6. **Grounding** — under the `kb-grounded` profile, every claim about harness
   behavior (hooks, frontmatter, subagents, skills, commands, MCP, model aliases)
   cites a cached `ai-docs/` file in decisions.md `## KB References`.
7. **Tracking hygiene** — spec.md `## Tracking` records Issue `#N`, the convention
   branch `<type>/<N>-<slug>` carrying the same number, the worktree path, and the
   review profile. No placeholders.
8. **Simplicity** — the simplest design that meets the objective. Collapse
   near-identical tasks; cut abstractions and steps the objective doesn't need.

When a Codex gate finding exposes a standard this list is missing or states
unclearly, amend this file in the same run — that is the self-improve step.
