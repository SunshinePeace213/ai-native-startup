# Implementation Notes: studio-layer — design-delivery studio through signed handoff

> Chronological dev log for [spec.md](./spec.md), created from this template at
> `/harness-layer:harness-build` implement start and appended by both
> `/harness-layer:harness-build` and `/harness-layer:harness-review` as the work
> proceeds. Entries land at each checkpoint commit, the moment the event happens;
> the PR body and build brief are derived from these notes — never reconstructed.
>
> Boundary: per-plan phases, hand-offs, deviations, fixes, and lessons live here.
> A lesson worth keeping beyond this plan is routed to its rule-file home by the
> memory step per memory-series.md.

## Log

<!-- Append-only; one entry per phase, hand-off, deviation, fix, or lesson — never edit or
     delete a prior entry. "No entries yet" is a valid starting body. -->

- **2026-08-01 · build start** — worktree `.claude/worktrees/cpo-layer` on branch
  `worktree-cpo-layer` (remote `feat/80-cpo-layer`), plan approved at the human gate,
  review profile `kb-grounded`.
  - `uv run pytest -q` → `875 passed, 2 skipped in 22.62s` — baseline before any build change.
- **2026-08-01 · phase 1 (ground the namespace)** — launched `studio-namespace`, `studio-roster`,
  `studio-client-artifacts`, `studio-question-bank` and `gate-signoff-hook` as concurrent
  builders; their **Files** fields are the disjointness contract.
- **2026-08-01 · hand-off `studio-namespace`** — `.gitignore`, `clients/.gitkeep`,
  `.claude/rules/studio-layer/studio-identity.md`, `AGENTS.md`
  - `git check-ignore -v clients/acme/site/brief.md` → `.gitignore:378:clients/* clients/acme/site/brief.md`
  - `git check-ignore -q clients/.gitkeep; echo $?` → `1` — the negation re-includes the contract file.
  - `bash specs/cpo-layer/checks/ac1-client-data-home.sh` → `AC1 pass: clients/ is contracted,
    ignored, and invisible to the spec gate`, exit 0. The builder's own run of this check
    returned exit 1 on two counts, both because `clients/.gitkeep` was still untracked — the
    builder is barred from `git add`, so the lead staged and committed it and the check went
    green with no file change.
  - `bash specs/cpo-layer/checks/ac5-rules-path-scoped.sh` → exit 1, reporting only
    `roster.md is missing` / `client-artifacts.md is missing` / `expected at least 3 studio
    rules, found 1`. No failure against `studio-identity.md`: it cleared the scope, name,
    voice, letterhead, sign-off and ≥400-char body assertions. Pending the two concurrent rules.
  - Deviations: none.
- **2026-08-01 · hand-off `studio-roster`** — `.claude/rules/studio-layer/roster.md`
  - Ten data rows; the principal row (Maya Lindqvist, `fable`/`xhigh`) states "No agent file"
    in its escalation cell, so the drift test can identify the row it must skip from the table
    itself rather than from a hard-coded name.
  - Every `Model` cell checked against `model-selection.md`'s Roster table and every `Effort`
    cell against its Effort table; all ten match.
  - `bash specs/cpo-layer/checks/ac5-rules-path-scoped.sh` → exit 0.
  - Deviations: none.
- **2026-08-01 · hand-off `studio-client-artifacts`** — `.claude/rules/studio-layer/client-artifacts.md`
  - `bash specs/cpo-layer/checks/ac4-client-artifacts.sh` → `AC4 pass: forks craft/publish,
    unlocks the palette, four patterns each with a return`, exit 0. That check also proves
    `.claude/rules/harness-layer/artifacts.md` is byte-identical to `origin/main` — the fork,
    not an edit, guardrail.
  - Deviations: none.
- **2026-08-01 · deviation (glob form) · `studio-namespace`, `studio-roster`, `studio-client-artifacts`**
  — plan said `paths: clients/**`; did `paths: clients/**/*` on all three studio rules.
  `studio-roster` surfaced the split (it had written `clients/**/*`, the other two the literal
  plan text). Settled on `clients/**/*` because `ai-docs/anthropic/memory.md` documents
  `src/**/*` as "All files under `src/`" and carries no bare `dir/**` row — under the
  kb-grounded profile "`clients/**` matches nested files" is a memory claim with no citable
  source — and because every path-scoped rule already in this repo uses that form
  (`specs/**/*`, `tests/**/*`, `.claude/hooks/**/*`, `**/*.py`). Had `clients/**` been wrong,
  the failure would have been silent: no studio rule would ever load on a client project.
  AC5 is satisfied either way (its assertion is the substring `clients/**`, which
  `clients/**/*` contains), so no acceptance criterion or locked decision changed — only the
  glob form the plan spelled out in prose. The two one-line edits were made by the builders
  owning each file, not by the lead.
  - `bash specs/cpo-layer/checks/ac4-client-artifacts.sh` → exit 0 after the change.
  - `bash specs/cpo-layer/checks/ac5-rules-path-scoped.sh` → exit 0 after the change.
- **2026-08-01 · hand-off `studio-question-bank`** —
  `.claude/skills/studio-layer/studio-client-questions/SKILL.md`, `…/evals/evals.json`
  - The machine-readable contract the coverage checker parses: **every `###` heading under
    `## Dimensions` is one dimension, and the heading text is its name.** The skill states this
    in its own `## Machine-readable dimension list` section, so the parser has a documented
    anchor rather than an inferred one. Eight dimensions today: the job the site does; the
    audience and their situation; brand voice; references loved and hated; the content that
    actually exists; hard constraints; budget; success at six months.
  - Frontmatter carries `name` and `description` and does **not** carry
    `disable-model-invocation`; directory name equals `name:`, which is what becomes the command.
  - `(cd .claude/skills/meta-skills && uv run --with pyyaml python -m scripts.eval ../studio-layer/studio-client-questions --lint)`
    → `PASS (0 warning(s))`, exit 0.
  - Eval suite: 2 cases, 11 assertions, 6 of them executable `check`s.
  - `bash specs/cpo-layer/checks/ac6-question-bank-skill.sh` → exit 1 on exactly two counts,
    both pending later tasks: `check_question_coverage.py is missing` and
    `p1-discovery.md is missing`. No assertion against the skill itself failed.
  - Deviations: none.
- **2026-08-01 · hand-off `studio-role-agents`** — the nine files under
  `.claude/agents/studio-layer/`
  - `bash specs/cpo-layer/checks/ac3-role-agents.sh` → `AC3 pass: nine role agents,
    function-named, person in the body`, exit 0.
  - `uv run pytest tests/harness-layer/test_model_drift.py` → `50 passed, 2 skipped in 1.37s`.
  - Lead cross-checked every stamp against `roster.md` by parsing both sides: all nine match
    (`studio-art-director opus/high`, `studio-client-partner sonnet/medium`,
    `studio-content-strategist opus/high`, `studio-design-qa opus/high`,
    `studio-discovery-lead opus/high`, `studio-prototype-engineer sonnet/high`,
    `studio-research-analyst sonnet/medium`, `studio-retro-scribe sonnet/medium`,
    `studio-ux-architect opus/high`). Every file sets `disallowedTools: Agent`; none carries
    `skills:` frontmatter. The principal has no agent file.
  - Deviations: none.
- **2026-08-01 · phase 2/3** — launched `studio-role-agents` (roster landed) and
  `studio-check-scripts` (question bank landed) as concurrent builders.
- **2026-08-01 · hand-off `studio-command-eval-runner`** —
  `.claude/scripts/studio-layer/run_command_evals.py`,
  `tests/harness-layer/studio-layer/test_run_command_evals.py`
  - `uv run --script .claude/scripts/studio-layer/run_command_evals.py .claude/commands/studio-layer --lint`
    → `…/evals/evals.json: 2 case(s), schema valid`, exit 0.
  - `bash specs/cpo-layer/checks/ac16-evals-are-runnable.sh` → `AC16 pass: both eval suites are
    present, harness-shaped, and machine-gradeable`, exit 0. This closes the last pending check
    recorded at the `studio-question-bank` and `studio-phase-commands` hand-offs.
  - `uv run pytest` → `990 passed, 2 skipped in 16.90s`.
  - `uv run ruff check .` → `All checks passed!`; `uv run ruff format --check .` → `71 files
    already formatted`.
  - Deviations: none.
- **2026-08-01 · hand-off `studio-phase-commands`** — the eight commands under
  `.claude/commands/studio-layer/`, `.claude/commands/studio-layer/evals/evals.json`
  - `bash specs/cpo-layer/checks/ac7-phase-commands.sh` → `AC7 pass: eight phase commands,
    four Stop registrations, each with its own phase`, exit 0.
  - `uv run pytest tests/harness-layer/hooks/test_wiring.py` → `13 passed in 1.70s`. **This is
    the entry that closes the pending failure recorded at the `gate-signoff-hook` hand-off**:
    the four p2/p3/p4/p6 frontmatter registrations are what claim `check_gate_signoff.py`, so
    `test_every_entrypoint_is_claimed_by_a_registration_surface` went from red to green with no
    change to the hook itself.
  - `bash specs/cpo-layer/checks/ac6-question-bank-skill.sh` → `AC6 pass: the question bank is
    invocable and its coverage is re-derived`, exit 0 — P1 names `check_question_coverage.py`
    literally, so the coverage gate is wired rather than orphaned.
  - `uv run pytest` → `971 passed, 2 skipped in 17.35s` (baseline was 875 passed, 2 skipped).
  - `uv run ruff check .` → `All checks passed!`; `uv run ruff format --check .` → `69 files
    already formatted`.
  - Deviations: none.
- **2026-08-01 · hand-off `studio-check-scripts`** — the four scripts under
  `.claude/scripts/studio-layer/`, `tests/harness-layer/studio-layer/test_studio_checks.py`
  - `uv run pytest tests/harness-layer/studio-layer/` → `25 passed in 1.91s`. All 22 node ids
    named verbatim across AC6, AC11, AC12 and AC13 are defined; none missing.
  - Lead independently recomputed the pinned contrast ratio rather than trusting the test's
    own docstring: `#8A837A` on `#FAF8F5` → `L_fg=0.230410 L_bg=0.940514 ratio=3.5324`,
    matching the asserted `3.53:1`. AC12's "the formula itself is checked, not just the
    branching" therefore holds. The script prints `Soriza project threshold`, so it never
    claims conformance to a specification this repo has not mirrored.
  - Scripts live under `.claude/scripts/studio-layer/`, not `.claude/hooks/`, so the wiring
    suite never sees them as unclaimed hook entrypoints.
  - Deviations: none.
- **2026-08-01 · hand-off `studio-roster-drift-test`** —
  `tests/harness-layer/test_studio_roster_drift.py`
  - AC2's exact six-node-id command → `6 passed in 1.64s`.
  - Builder's mutation proof (agent side): edited `studio-client-partner.md` to
    `effort: high` → `AssertionError: .claude/agents/studio-layer/studio-client-partner.md:
    roster says effort 'medium', file says 'high'`; reverted, `git diff --stat
    .claude/agents/studio-layer/` empty, suite green again.
  - Lead's independent mutation proof (roster side): edited the `studio-design-qa` row to
    `sonnet` → `AssertionError: .claude/agents/studio-layer/studio-design-qa.md: roster says
    model 'sonnet', file says 'opus'`, `1 failed, 5 passed`; restored from a backup copy,
    `git status --porcelain .claude/rules/studio-layer/` empty, `6 passed in 1.82s`.
    Both directions of AC2's "changing either side alone fails" are therefore exercised.
  - Parser re-derives from `roster.md`, mirroring `test_model_drift.py`'s shape; the principal
    row is skipped via the literal `No agent file` marker in its escalation cell rather than a
    hard-coded name; agent files are matched by frontmatter `name:` so a misnamed file is
    caught as an orphan.
  - `uv run ruff check .` → `All checks passed!`; `uv run ruff format --check .` → `68 files
    already formatted`.
  - Deviations: none.
- **2026-08-01 · hand-off `gate-signoff-hook`** — `.claude/hooks/check_gate_signoff.py`,
  `tests/harness-layer/hooks/gate-signoff/test_check_gate_signoff.py`,
  `tests/harness-layer/hooks/conftest.py`, `tests/harness-layer/hooks/test_wiring.py`,
  `.claude/rules/harness-layer/hooks.md`
  - `uv run pytest tests/harness-layer/hooks/gate-signoff/` → `30 passed in 1.39s`. All 26
    node ids named verbatim in AC8, AC9 and AC15 are defined — verified by parsing the test
    file for each `def <name>(`; none missing.
  - `uv run pytest tests/harness-layer/hooks/` → `1 failed, 806 passed in 10.38s`. The single
    failure is `test_every_entrypoint_is_claimed_by_a_registration_surface`:
    `AssertionError: hooks with no registration surface: ['check_gate_signoff.py']`. Expected
    and pending `studio-phase-commands` — the four hard-gate commands that register the hook do
    not exist yet. Tracked to green at the `validate-all` step; not a defect in this hand-off.
  - Blast radius held: `run_hook` gained only `args: tuple = ()` spliced after the script path,
    every existing call site untouched, and the other 806 hook tests stayed green.
  - `hooks.md` catalog row added (`Stop (command-scoped)`, Codex `not-applicable`) and
    `CODEX_DISPOSITIONS` gained the matching entry; the wiring suite cross-checks both directions.
  - The registration line the four gate commands must carry:
    `uv run --script "$CLAUDE_PROJECT_DIR"/.claude/hooks/check_gate_signoff.py <phase>`.
  - Deviations: none.
