---
paths:
  - "tests/**/*"
---

# Test Tiers

This repo's product is mostly prompts, so "add a test" means different work per
change. Pick the tier from what changed; a change spanning two tiers gets both.

| Tier | Guards | Lives in | Shape |
| --- | --- | --- | --- |
| **Contract** | Executable code — hooks, scripts | `tests/harness-layer/hooks/<feature>/`, mirroring the source tree | pytest over both the block and allow paths; the hook specifics are in [hooks.md](hooks.md) |
| **Drift** | Files that must stay true to reality — registrations, templates, rules, model stamps | `tests/harness-layer/` | pytest that re-derives the expectation from the source of truth and compares (`test_wiring.py`, `test_pr_templates.py`, `test_model_drift.py`) |
| **Eval** | Skills and commands — non-deterministic prose | the `meta-skills` skill's eval harness | Score output against a rubric over repeated runs |

## Rules

- A drift test re-derives its expectation from the source of truth. A second
  hard-coded copy drifts in step with the first and pins nothing.
- Parse structure, not prose — read a registration from frontmatter, JSON, or a
  parsed field, never by scanning a whole file for a substring. Documentation
  naming a path is not a registration.
- An eval's result is a pass rate over N runs; a single green run proves nothing.
- CI (`.github/workflows/ci.yml`) runs the contract and drift tiers on every PR.
  Evals stay manual — they cost tokens and need a rubric review.
