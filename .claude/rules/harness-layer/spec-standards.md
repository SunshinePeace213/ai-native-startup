---
paths:
  - "specs/**/*"
---

# Spec Standards

The bar every plan under `specs/<name>/` must clear. The drafting agent self-checks
against it before requesting review; the Codex gate judges against the same list,
and findings cite these IDs (`[STD:S<n>]`) — a finding citing no standard is
advisory. `scripts/spec_lint.py` owns the mechanical halves (S7, S2's
exist-and-collect half, template completeness) and runs before any lens; the
panel judges the rest.

1. **S1 · Traceability** — every requirement in spec.md maps to a task in
   tasks.md, and every task names the `AC#` it satisfies. An objective with no
   implementing step is a defect. (AC↔task presence in both directions is
   lint-owned; requirement→task coverage is the lens's.)
2. **S2 · Testability** — every acceptance criterion is observable and backed by
   a command that fails when the change is reverted: the project's own suite, a
   checked-in validator, or a plan-local script under `specs/<name>/checks/`. A
   shape stated in `## Interfaces & Contracts` is asserted by one of them. A task
   that changes behavior names the test it adds or extends in its **Files**, at
   the tier [test-tiers.md](test-tiers.md) assigns. No "works well" or "feels
   fast". (That commands exist and collect is lint-owned; whether the command
   proves the criterion is the lens's.)
3. **S3 · Feasibility & ordering** — every step can run as written, and
   prerequisites come before their dependents.
4. **S4 · Scope fidelity** — the plan implements the locked decisions exactly:
   nothing missing, nothing beyond them, nothing marked out-of-scope or non-goal.
5. **S5 · Consistency** — no two requirements contradict, and no requirement
   contradicts a locked decision.
6. **S6 · Grounding** — under the `kb-grounded` profile, every claim about
   harness behavior (hooks, frontmatter, subagents, skills, commands, MCP, model
   aliases) cites a cached `ai-docs/` file in decisions.md `## KB References`.
7. **S7 · Tracking hygiene** — spec.md `## Tracking` records the change type,
   complexity, Issue `#N`, the convention branch `<type>/<N>-<slug>` carrying the
   same number, the worktree path, and the review profile. No placeholders.
   (Lint-owned.)
8. **S8 · Simplicity** — the simplest design that meets the objective. Collapse
   near-identical tasks; cut abstractions and steps the objective doesn't need.

IDs are stable: never renumber an existing standard — a new one takes the next
free ID. When a gate finding exposes a standard this list is missing or states
unclearly, amend this file in the same run — that is the self-improve step.
