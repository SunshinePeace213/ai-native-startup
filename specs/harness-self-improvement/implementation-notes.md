# Implementation Notes: harness-self-improvement — Plan 1

> Chronological dev log for [spec.md](./spec.md), created from this template at
> `/harness-layer:harness-build` implement start and appended by both
> `/harness-layer:harness-build` and `/harness-layer:harness-review` as the work
> proceeds.
>
> Boundary: per-plan phases, hand-offs, deviations, fixes, and lessons live here.
> Cross-plan one-liners go to `.claude/rules/development-log.md` instead.

## Log

- **2026-07-25 · build start** — build lead entered the recorded worktree (branch
  `worktree-harness-self-improvement` → remote `chore/54-harness-self-improvement`); board
  created from tasks.md; builders deployed via pinned-effort executors per the CX2-1 mechanism.
- **2026-07-25 · phase 2 hand-off (ci-workflow)** — builder-ci (sonnet via `effort-low`):
  `.github/workflows/harness-tests.yml` created; AC4 check green. Action pins verified against
  official docs: `actions/checkout@v7`, `astral-sh/setup-uv@v8` (+`enable-cache: true`).
  Judgment call: floating major-version tags rather than SHA-pins (plan requires version pins
  only); flagged for review. Commit 673e044.
- **2026-07-25 · phase 1 hand-off (retarget-stop-gate)** — builder-hook (opus via
  `effort-medium`): gate re-targeted to stdin `cwd` with the fixed single-root fallback chain;
  cross-worktree glob deleted; concurrency regressions (both directions + decoy + fail-open)
  added; hooks.md row updated. 21 passed (15 spec-completeness + 6 wiring). Commit 5b62f53.
- **2026-07-25 · phase 2 hand-off (contract-tests)** — builder-contracts (sonnet via
  `effort-high`): `load_hook_module` promoted to `tests/harness-layer/conftest.py`; prompts
  suite (20 tests) pins every inventory row verbatim — no pin needed softening; #40/#42 replays
  cite restore commits. Surfaced 2 pre-existing full-suite failures in
  `hooks/auto-format/test_python.py` (ruff quote drift), confirmed via stash. Commit e3d6f33.
- **2026-07-25 · phase 1 hand-off (stop-gate-lint)** — builder-hook resumed (same
  `effort-medium` pin): lint added after the required-sections check; block/warn split per the
  locked decision; 10 new tests; live run on the real repo → exit 0 with warn-only wording
  lines. 31 passed. Commit 643ee48.
- **2026-07-25 · deviation (board access)** — plan said builders flip their own task status;
  the Task* board tools were unavailable in every subagent context (ToolSearch found none), so
  the build lead flipped each status from the hand-offs. No effect on deliverables.
- **2026-07-25 · phase 3 validation (validate-all)** — validator (sonnet via `effort-low`):
  AC1–AC5 all PASS (AC5: 84 inventory rows; worktree glob grep-confirmed gone; seven CI path
  filters literal). Full suite 656 passed, 2 failed — both pre-existing on `main`
  (auto-format ruff quote drift; nothing under `auto-format/` in the branch diff). Disclosed
  in PR test evidence; fix belongs to a separate plan.
- **2026-07-25 · tidy** — harness-simplifier + code-simplifier (opus): 2 behavior-preserving
  fixes (dead `kind` tuple slot in `command_target`; hooks.md row wording); all other touched
  files clean; 51 tests green post-tidy. Commit 353a7cc.
- **2026-07-25 · draft PR** — PR #55 opened (chore + priority:P2, `Closes #54`,
  `Part of #53`); tidy report posted as `<!-- report:tidy -->`; stage table ticks
  Implementation + Tidy.
- **2026-07-25 · lesson** — deploying stamped effort via `Agent({subagent_type:
  "effort-<tier>", model: <alias>})` worked first try for all five deployments, including the
  resume-keeps-pin case (builder-hook tasks 1→2).
- **2026-07-25 · review round 1** — Codex (`gpt-5.6-sol`/`xhigh`, kb-grounded, full range
  841e772..470047f): changes-requested — CX1-1 lint accepts out-of-plan/absolute/traversing
  check paths; CX1-2 frontmatter pins were substring checks (commented/renamed keys stayed
  green); CX1-3 AC5 parser silently skipped malformed rows and unknown kinds. One advisory
  (GitHub Actions KB gap) → PR Follow-ups. Report committed 6158aee.
- **2026-07-25 · round-1 fixes** — three parallel fixers, all `(new)` → default tiers:
  CX1-1 opus/`effort-medium` (hook + 4 negative tests), CX1-2 sonnet/`effort-high`
  (line-anchored entry pins, fragment pins split out, 10 mutation tests), CX1-3
  sonnet/`effort-medium` (fail-loud AC5 parser, both failure modes demonstrated). Combined
  verification: AC4/AC5 ok, suite 670 passed / 2 pre-existing failed. One fix commit d978440.
- **2026-07-25 · review round 2 (terminal)** — Codex (`gpt-5.6-sol`/`high`, delta
  470047f..d978440): changes-requested — CX1-1..CX1-3 all confirmed fixed; CX2-1 (new,
  comment-accuracy): the CX1-2 mutation-test docstrings falsely claim frontmatter `name:`
  controls skill resolution (it is directory-keyed — `ai-docs/anthropic/skills.md`). Attempt
  budget (2) spent → PR #55 left draft; the human owns CX2-1 (docstring rewrite only, the
  pins themselves are correct).
- **2026-07-25 · lesson** — a "pin" asserted by substring is not a pin: a commented or
  prefixed key keeps it green. Pin whole frontmatter entries line-anchored and replay the
  mutation as a test — and make each docstring state the real mechanism (Codex's
  comment-accuracy lens blocks false rationale even when the assert is right).
- **2026-07-25 · CX2-1 fix** — review lead (new invocation, per the round-2 hand-off
  prompt): docstring-only rewrite in `test_skill_contracts.py` — `name:` described as
  declared metadata pinned by the inventory, resolution stated as directory-keyed; five
  docstrings corrected (module, `frontmatter_lines`, pins-hold, both mutation tests),
  every assertion unchanged. 11 tests green, ruff clean. Commit a19b6ac.
- **2026-07-25 · review round 3 (terminal)** — Codex (`gpt-5.6-sol`/`medium`, delta
  d978440..a19b6ac, kb-grounded): approved — CX2-1 confirmed fixed, 0 raw findings, all
  four validation commands PASS. PR #55 flipped ready at the approved head.
