# Acceptance Criteria: studio-layer — design-delivery studio through signed handoff

> The definition of "done" for [spec.md](./spec.md). Every criterion is observable and
> testable, and every task in tasks.md maps to at least one criterion here.
>
> Each criterion names the brainstorm card it makes real. A card that ships as prose with no
> failing check has not shipped.

## Acceptance Criteria

### Namespace and roster (cards 01–02)

- **AC1** — `clients/` exists as a directory contract and is ignored by git: `git check-ignore`
  claims a path inside it, `git status --porcelain` reports nothing for it after writing a
  file there, and `check_spec_completeness.py` returns 0 with a client folder present and no
  plan folder change — the two catalogs cannot mix.
- **AC2** — Every role's `model` and `effort` in `.claude/agents/studio-layer/*.md` is
  re-derived from `.claude/rules/studio-layer/roster.md` and matches. Changing either side
  alone fails; a roster row with no agent file fails naming the missing file, and an agent
  file with no roster row fails naming the orphan.
- **AC3** — Nine agent files exist under `.claude/agents/studio-layer/`, each with a plain
  layer-prefixed function `name:` (`studio-<function>`, no person in the name), each naming
  its person in the body, and each passing the meta-agent validator. The principal has no
  agent file.

### Discovery, artifacts, and identity (cards 03–04)

- **AC4** — `.claude/rules/studio-layer/client-artifacts.md` is scoped `paths: clients/**`,
  references `artifacts.md` for craft and publish, declares no palette hex table, names the
  palette source per phase (studio default P0–P3, picked-direction tokens P4+), and carries a
  four-row page-pattern table whose rows are brief review, sitemap, art direction, and
  feedback triage — each stating what its copy-as-prompt returns.
- **AC5** — Every markdown file under `.claude/rules/studio-layer/`, at any depth, is scoped
  `paths:` including `clients/**`, so no studio rule loads during ordinary harness work.
  `studio-identity.md` carries actual content for each of the four things it exists to supply
  — studio name, client-facing voice, document letterhead, and the sign-off block — and
  `AGENTS.md` carries a pointer to the studio rules while the always-loaded set stays under
  the `memory-series.md` budget.
- **AC6** — The question-bank skill registers, is model-invocable (no
  `disable-model-invocation`), and `check_question_coverage.py` re-derives its dimension list
  from the skill's own question list — not a second hard-coded copy — and exits non-zero when
  discovery notes leave a dimension unanswered without an explicit "N/A, because".

### Phase commands and gates (cards 05–07)

- **AC7** — Eight command files exist under `.claude/commands/studio-layer/`, named
  `p0-intake` … `p7-retro`. Exactly four — p2, p3, p4, p6 — register
  `check_gate_signoff.py` in their frontmatter `hooks.Stop`, each passing its own phase token
  as the argument, and no other studio command registers it.
- **AC8** — `check_gate_signoff.py` denies a stop (exit 2, diagnostics on stderr) when the
  phase's sign-off file is missing, when Approver or Date is empty or a placeholder, when the
  artifact table is absent or empty, when a listed artifact path does not exist, or when a
  listed SHA-256 does not match that file's current content. It returns 0 when Approver and
  Date are filled and every artifact row resolves and matches. It gates the phase given in
  `argv[1]` regardless of which phase folder was modified most recently, and resolves its
  project by the documented `cwd` → sole-project → give-up order, proven with two projects
  present at once. It returns 0 without blocking when there is no `clients/` directory, when
  the phase argument is missing or unrecognized, when no project can be identified, and on
  re-entry with `stop_hook_active: true`.
- **AC9** — The p2 gate additionally denies the stop when the cold-designer triage document is
  missing or holds an untriaged row, and allows it when every row carries a disposition. The
  underlying diff itself is advisory and never gates.
- **AC10** — `check_gate_signoff.py` is registered in `hooks.md`'s catalog with a Codex verdict
  matching `CODEX_DISPOSITIONS`, and is claimed by a registration surface — the existing
  wiring suite passes with the new hook present.

### Design QA and revisions (cards 08–09)

- **AC11** — `check_states_matrix.py` exits non-zero naming each unfilled cell when any
  component × state (hover, focus, disabled, loading, empty, error) at any declared breakpoint
  is blank, and exits 0 on a fully-specced matrix. A component row with no state columns
  counts as unfilled, not skipped. An empty or absent matrix cannot pass vacuously: zero
  breakpoints, zero component rows, or a missing state column each exit non-zero, so the
  check quantifies over a required inventory rather than over whatever happens to be declared.
- **AC12** — `check_contrast.py` computes the relative-luminance ratio for every
  foreground/background pair in the handoff token table and exits non-zero naming any pair
  below its threshold and any specced tap target below the minimum; it exits 0 on a compliant
  table. The thresholds are Soriza project thresholds, named as such — this criterion asserts
  the arithmetic, not conformance to a specification the repo has not mirrored. At least one
  hand-computed ratio is pinned in the tests so the formula itself is checked, not just the
  branching. An empty pair table or an empty target table exits non-zero rather than passing
  vacuously, and a malformed hex value exits 2, never 1.
- **AC13** — `check_revision_count.py` re-derives the allowance from the signed brief — not a
  hard-coded number — and exits non-zero for a revision-log round past that allowance with no
  matching change-order document, exits 0 when a change order is present, and exits 2 when the
  signed brief declares no allowance at all.

### Roles, gates, and behavior

- **AC15** — `studio-design-qa` blocks handoff as a mechanism, not a claim: it writes
  `handoff/qa-report.md` in the documented schema, and the p6 gate denies the stop while any
  finding marked `blocking` is still `open`, allowing it once each is `resolved`. Every role
  agent denies the `Agent` tool, so no role can spawn its own subagents and the tree stays one
  level deep.
- **AC16** — The non-deterministic surfaces carry eval coverage per `test-tiers.md`: the
  question-bank skill and the P1 and P2 commands each have eval cases with a rubric under
  `specs/cpo-layer/evals/`, scored as a pass rate over repeated runs. Evals are manual and
  stay out of CI; their recorded pass rates are the evidence.

### Suite health

- **AC14** — `uv run pytest`, `uv run ruff check .` and `uv run ruff format --check .` all
  pass from the repo root with every new file present, including the existing hook, wiring,
  and model-drift suites.

## Validation Commands

Every command runs from the repo root. Plan-local scripts live in `specs/cpo-layer/checks/`
and exit 0 on pass.

### AC1 — client data home exists, is ignored, and never reaches the spec gate

- `bash specs/cpo-layer/checks/ac1-client-data-home.sh` — pass: exit 0. Fails if `clients/`
  is untracked-but-not-ignored, if a file written under it shows in `git status --porcelain`,
  or if `check_spec_completeness.py` changes its verdict when a client folder is present.

### AC2 — roster stamps are load-bearing

- `uv run pytest tests/harness-layer/test_studio_roster_drift.py` — pass: all tests green.
  Fails when an agent file's `model`/`effort` diverges from its roster row, when a roster row
  has no agent file, or when an agent file has no roster row.
- `uv run pytest tests/harness-layer/test_model_drift.py` — pass: green. Pins every new
  `model:`/`effort:` value to `model-selection.md`'s roster.

### AC3 — nine role agents, function-named, person in the body

- `bash specs/cpo-layer/checks/ac3-role-agents.sh` — pass: exit 0. Asserts exactly nine files,
  each `name:` matching `^studio-[a-z-]+$` and equal to its filename stem, each body naming its
  roster person, no `skills:` frontmatter on any of them, and `validate_agent.py` clean on each.

### AC4 — the client-artifact rule forks rather than copies

- `bash specs/cpo-layer/checks/ac4-client-artifacts.sh` — pass: exit 0. Asserts the
  `paths: clients/**` scope, a reference to `artifacts.md`, the absence of any 6-digit hex
  colour literal, a palette-source line for each phase band, and a four-row table whose row
  labels are brief review, sitemap, art direction, feedback triage.

### AC5 — every studio rule is path-scoped

- `bash specs/cpo-layer/checks/ac5-rules-path-scoped.sh` — pass: exit 0. Asserts all three
  files in `.claude/rules/studio-layer/` declare `paths:` including `clients/**`; fails if any
  studio rule would load at session start.

### AC6 — the question bank is invocable and its coverage is re-derived

- `uv run pytest "tests/harness-layer/studio-layer/test_studio_checks.py::test_unanswered_dimension_fails" "tests/harness-layer/studio-layer/test_studio_checks.py::test_explicit_na_because_passes" "tests/harness-layer/studio-layer/test_studio_checks.py::test_adding_a_skill_dimension_changes_what_is_required"` —
  pass: 3 passed. The third is the one that proves re-derivation rather than a second copy.
- `bash specs/cpo-layer/checks/ac6-question-bank-skill.sh` — pass: exit 0. Asserts `SKILL.md`
  exists at `.claude/skills/studio-layer/studio-client-questions/`, that the directory name
  matches the skill's `name:` (the directory is what becomes the command), that it carries
  `name`/`description`, that it does **not** set `disable-model-invocation`, and that P1's
  command actually invokes the coverage check.

### AC7 — eight commands, four gate registrations

- `bash specs/cpo-layer/checks/ac7-phase-commands.sh` — pass: exit 0. Asserts the eight
  filenames, and that exactly `{p2,p3,p4,p6}` reference `check_gate_signoff.py` in frontmatter,
  each with its own phase token as the trailing argument.

### AC8 — the sign-off gate blocks and allows for the right reasons

- `uv run pytest tests/harness-layer/hooks/gate-signoff/test_check_gate_signoff.py` — pass:
  green, and the file must contain at least these node ids:
  `::test_missing_signoff_file_blocks`, `::test_empty_approver_blocks`,
  `::test_placeholder_date_blocks`, `::test_empty_artifact_table_blocks`,
  `::test_artifact_path_that_does_not_exist_blocks`, `::test_sha_mismatch_blocks`,
  `::test_complete_signoff_allows`, `::test_no_clients_dir_allows_silently`,
  `::test_unknown_phase_argument_fails_open`,
  `::test_phase_comes_from_argv_not_mtime`,
  `::test_cwd_selects_the_project_when_two_exist`,
  `::test_two_projects_and_outside_cwd_fails_open`,
  `::test_stop_hook_active_allows_with_warning`.

### AC9 — the cold-designer triage gates p2, and the QA report gates p6

- `uv run pytest "tests/harness-layer/hooks/gate-signoff/test_check_gate_signoff.py::test_p2_missing_triage_blocks" "tests/harness-layer/hooks/gate-signoff/test_check_gate_signoff.py::test_p2_untriaged_row_blocks" "tests/harness-layer/hooks/gate-signoff/test_check_gate_signoff.py::test_p2_fully_triaged_allows" "tests/harness-layer/hooks/gate-signoff/test_check_gate_signoff.py::test_p3_p4_p6_do_not_require_triage"` —
  pass: 4 passed. The diff itself never gates; only the triage document does.

### AC10 — the new hook is registered, cataloged, and dispositioned

- `uv run pytest tests/harness-layer/hooks/test_wiring.py` — pass: green. The existing
  entrypoint-claim, disposition-coverage, and `hooks.md`-catalog assertions all cover the new
  hook; each fails if its row, verdict, or registration is missing.

### AC11 — the states matrix counts cells and cannot pass empty

- `uv run pytest "tests/harness-layer/studio-layer/test_studio_checks.py::test_full_matrix_passes" "tests/harness-layer/studio-layer/test_studio_checks.py::test_single_blank_cell_fails_and_names_it" "tests/harness-layer/studio-layer/test_studio_checks.py::test_component_row_with_no_states_fails" "tests/harness-layer/studio-layer/test_studio_checks.py::test_matrix_with_no_component_rows_fails" "tests/harness-layer/studio-layer/test_studio_checks.py::test_matrix_with_no_breakpoints_fails" "tests/harness-layer/studio-layer/test_studio_checks.py::test_missing_state_column_fails"` —
  pass: 6 passed. The last three are what stop a vacuous pass.

### AC12 — contrast and tap targets are computed, not asserted

- `uv run pytest "tests/harness-layer/studio-layer/test_studio_checks.py::test_known_pair_matches_hand_computed_ratio" "tests/harness-layer/studio-layer/test_studio_checks.py::test_pair_below_threshold_fails" "tests/harness-layer/studio-layer/test_studio_checks.py::test_undersized_tap_target_fails" "tests/harness-layer/studio-layer/test_studio_checks.py::test_empty_pair_table_fails" "tests/harness-layer/studio-layer/test_studio_checks.py::test_empty_target_table_fails" "tests/harness-layer/studio-layer/test_studio_checks.py::test_malformed_hex_exits_2"` —
  pass: 6 passed. The first pins the arithmetic against a hand-computed value; the last
  proves a typo is never reported as a contrast failure.

### AC13 — the revision count is arithmetic

- `uv run pytest "tests/harness-layer/studio-layer/test_studio_checks.py::test_round_within_allowance_passes" "tests/harness-layer/studio-layer/test_studio_checks.py::test_round_past_allowance_without_change_order_fails" "tests/harness-layer/studio-layer/test_studio_checks.py::test_round_past_allowance_with_change_order_passes" "tests/harness-layer/studio-layer/test_studio_checks.py::test_changing_the_brief_allowance_changes_the_verdict" "tests/harness-layer/studio-layer/test_studio_checks.py::test_brief_with_no_allowance_exits_2"` —
  pass: 5 passed. The fourth is what proves the allowance is re-derived from the brief rather
  than hard-coded.

### AC15 — design QA blocks handoff, and no role spawns subagents

- `uv run pytest "tests/harness-layer/hooks/gate-signoff/test_check_gate_signoff.py::test_p6_open_blocking_qa_finding_blocks" "tests/harness-layer/hooks/gate-signoff/test_check_gate_signoff.py::test_p6_all_blocking_findings_resolved_allows" "tests/harness-layer/hooks/gate-signoff/test_check_gate_signoff.py::test_p6_advisory_finding_does_not_block"` —
  pass: 3 passed.
- `bash specs/cpo-layer/checks/ac3-role-agents.sh` — pass: exit 0; it asserts every role sets
  `disallowedTools: Agent`.

### AC16 — the non-deterministic surfaces carry evals

- `manual: run the cases in specs/cpo-layer/evals/question-bank.md and evals/phase-commands.md` —
  pass: each case meets its rubric on the recorded majority of runs; pass rates recorded in
  `implementation-notes.md`. Per `test-tiers.md` evals stay manual and out of CI, so the
  recorded rate is the evidence — a single green run proves nothing.

### AC14 — the whole suite stays green

- `uv run pytest` — pass: exit 0, no failures.
- `uv run ruff check .` — pass: exit 0.
- `uv run ruff format --check .` — pass: exit 0.
