### Round 1 — Verdict: changes-requested

Scope: full
Base SHA: 841e77241823ddbdfec4dab6ea8b126a55474f96
Reviewed head SHA: 470047f4fa127ba09c3efcbec663ed90aff006a8
Mode: spawn (6 lenses)
Profile: kb-grounded
Lenses: plan-adherence, review-code-standards, review-silent-failure, review-type-design, review-test-coverage, review-comment-accuracy | skipped: review-simplification — tidy pass recorded in implementation-notes.md:42-44
Findings: 4 surviving of 15 raw (floor 80)
Validation:
- `[plan-time]` `uv run --script specs/harness-self-improvement/checks/ac5_inventory.py` → PASS
- `[child-build-time]` `uv run pytest tests/harness-layer/hooks/spec-completeness` → PASS (25 passed)
- `[child-build-time]` `uv run pytest tests/harness-layer/prompts` → PASS (20 passed)
- `[child-build-time]` `uv run --script specs/harness-self-improvement/checks/ac4_ci_workflow.py` → PASS

Digest: 3 blocking — 1 plan-adherence defect in validation-command path enforcement, 1 type/contract defect in frontmatter pins, and 1 silent-failure defect in the AC5 inventory parser. The KB pass adds 1 non-blocking grounding advisory. The broader harness suite reproduced the recorded 656 passed / 2 failed baseline; both failures are pre-existing in untouched auto-format tests and are suppressed. Recorded deviations: the unavailable subagent board tools are conforming because the lead performed only the planned status updates with no deliverable impact; floating action-major pins conform to the plan's version-pin requirement.

Findings:

**Plan adherence**

- **CX1-1 (new) — The validation-command lint accepts paths outside the selected plan's committed checks.** `.claude/hooks/check_spec_completeness.py:163-202` extracts any non-space token after `uv run --script` or `uv run pytest` and checks only `(root / path).exists()`. Absolute paths discard `root`, `..` can escape it, directories count as existing, and a script from another plan is accepted. This violates acceptance-criteria.md:14-18 and tasks.md:91, which require the script form `specs/<plan>/checks/…` and a present plan-time check. Fix: reject absolute/traversing targets, require script targets to be regular files under the selected folder's `checks/`, keep pytest targets repo-relative, and add negative tests for absolute paths, `..`, directories, and another plan's script.

**review-type-design / review-test-coverage**

- **CX1-2 (new) — Frontmatter contract pins do not verify actual YAML entries.** `tests/harness-layer/prompts/test_command_contracts.py:28-54` and `tests/harness-layer/prompts/test_skill_contracts.py:23-50` use raw substring membership inside the frontmatter block. A load-bearing key can therefore be removed while a comment or renamed key such as `# model: fable`, `x-model: fable`, or `old-name: spec-review` keeps the suite green. That leaves AC3's frontmatter-key/value guarantee in acceptance-criteria.md:19-26 unmet. Fix: represent key/value pins as exact frontmatter entries (line-anchored or parsed), keep deliberate fragment pins separate, and add mutations proving commented and prefixed keys fail.

**review-silent-failure**

- **CX1-3 (new) — AC5 silently accepts malformed inventory schema.** `specs/harness-self-improvement/checks/ac5_inventory.py:20-28` skips pipe rows that do not parse to three cells, while lines 31-43 route every unknown `kind` through the generic substring branch. The check can therefore print success after omitting a malformed row or treating a misspelled kind as valid, contrary to AC5 in acceptance-criteria.md:32-36 and the three-kind contract in spec.md:124-133. Fix: fail with a diagnostic for malformed table rows and reject every kind outside `frontmatter`, `sections`, and `clause`.

**Advisory (non-blocking) — KB grounding**

- The workflow syntax, `contains()` placement, and `actions/checkout@v7` / `astral-sh/setup-uv@v8` claims in `.github/workflows/harness-tests.yml` remain ungrounded in the cached KB. `decisions.md:229-238` records the same gap, and `ai-docs/index.md` has no GitHub Actions or setup-uv mirror. Add the two official pages named there with `/harness-layer:kb add` and refresh the KB; no cached source contradicts the implementation.

**Issue-comment digest:** Round 1, changes-requested — 3 blocking: validation lint accepts out-of-scope paths, prompt frontmatter pins allow false positives, and AC5 silently accepts malformed inventory schema. Next: fix all three, rerun the required validation, then re-review.
