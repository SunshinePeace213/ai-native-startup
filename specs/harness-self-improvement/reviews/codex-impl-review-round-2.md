### Round 2 — Verdict: changes-requested

Scope: delta
Base SHA: 470047f4fa127ba09c3efcbec663ed90aff006a8
Reviewed head SHA: d97844036c870125f895dd89bf74af31f42dfe57
Mode: spawn (6 lenses)
Profile: kb-grounded
Lenses: plan-adherence, review-code-standards, review-silent-failure, review-type-design, review-test-coverage, review-comment-accuracy | skipped: review-simplification — tidy pass recorded in the prior report
Findings: 1 surviving of 3 raw (floor 80)
Validation:
- `[plan-time]` `uv run --script specs/harness-self-improvement/checks/ac5_inventory.py` → PASS
- `[child-build-time]` `uv run pytest tests/harness-layer/hooks/spec-completeness` → PASS (29 passed)
- `[child-build-time]` `uv run pytest tests/harness-layer/prompts` → PASS (30 passed)
- `[child-build-time]` `uv run --script specs/harness-self-improvement/checks/ac4_ci_workflow.py` → PASS
Prior blockers:
- CX1-1 fixed: script targets are now repo-relative regular files under the selected plan's checks directory, with the requested negative cases covered.
- CX1-2 fixed: whole frontmatter entries now use exact-line matching, deliberate fragments are separate, and commented/prefixed entry mutations are covered.
- CX1-3 fixed: malformed three-cell rows and unknown inventory kinds now produce explicit AC5 failures.

Digest: 1 blocking — a new comment-accuracy and KB-grounding contradiction misstates how skill names are resolved.

Findings:

**review-comment-accuracy / KB grounding**

- **CX2-1 (new) — New docstrings incorrectly say frontmatter `name:` controls skill resolution.** `tests/harness-layer/prompts/test_skill_contracts.py:42-47`, `:202-206`, and `:216-218` say Claude resolves a skill through the live `name:` key and cannot resolve it when that key is commented or renamed. The same contract file states at `tests/harness-layer/prompts/test_skill_contracts.py:121-125` that resolution is directory-keyed and the skill still loads when `name:` drifts; the cached official skills documentation likewise describes the name as display metadata and directory/file naming as the project-skill resolution surface (`ai-docs/anthropic/skills.md:253`, `:272-281`). The exact-entry checks may still enforce the inventory, but their runtime rationale is false. Fix: rewrite the added docstrings to describe enforcing the declared metadata/inventory contract, without claiming that `name:` controls resolution.

**Issue-comment digest:** Round 2, changes-requested — 1 blocking: new skill-contract docstrings falsely claim frontmatter `name:` controls skill resolution. Next: correct those comments to match the directory-keyed contract, then re-review.
