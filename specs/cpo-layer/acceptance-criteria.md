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
  underlying diff itself is advisory and never gates. The p3 gate additionally denies the stop
  when `structure/inventory.md` is missing or empty, or when the P3 sign-off's artifact table
  does not list it — so the inventory the P6 checks quantify over is one the client actually
  approved, and P6 cannot author its own denominator. The p6 gate additionally re-verifies that
  inventory against the SHA-256 recorded in the P3 sign-off and denies the stop on a mismatch,
  so rows deleted between P3 and P6 are caught: signing at P3 alone would leave the file P6
  actually measures against unverified.
- **AC10** — `check_gate_signoff.py` is registered in `hooks.md`'s catalog with a Codex verdict
  matching `CODEX_DISPOSITIONS`, and is claimed by a registration surface — the existing
  wiring suite passes with the new hook present.

### Design QA and revisions (cards 08–09)

- **AC11** — `check_states_matrix.py` exits non-zero naming each unfilled cell when any
  component × state (hover, focus, disabled, loading, empty, error) at any declared breakpoint
  is blank, and exits 0 on a fully-specced matrix. A component row with no state columns
  counts as unfilled, not skipped. It cannot pass vacuously: the check reads the
  client-signed `structure/inventory.md` and requires a matrix row for **every** component ×
  breakpoint pair listed there, so a one-component matrix covering a ten-component design fails
  naming each missing pair. An empty or absent inventory exits 2 — a missing baseline, not a
  pass. Because the inventory is a P3 deliverable whose hash the P3 sign-off records, P6 cannot
  shrink its own denominator: the list it is measured against was approved by the client one
  phase earlier.
- **AC12** — `check_contrast.py` computes the relative-luminance ratio for every
  foreground/background pair in the handoff token table and exits non-zero naming any pair
  below its threshold and any specced tap target below the minimum; it exits 0 on a compliant
  table. The thresholds are Soriza project thresholds, named as such — this criterion asserts
  the arithmetic, not conformance to a specification the repo has not mirrored. At least one
  hand-computed ratio is pinned in the tests so the formula itself is checked, not just the
  branching. It cannot pass vacuously either: every colour token named in the client-signed
  `structure/inventory.md` must appear in at least one checked foreground/background pair, and
  every inventory component must have a tap-target row, so declaring one compliant pair and
  omitting the rest fails. An empty pair or target table exits 2, a missing or empty inventory
  exits 2, and a malformed hex value exits 2 — never 1.
- **AC13** — `check_revision_count.py` re-derives the allowance from the signed brief — not a
  hard-coded number — and exits non-zero for a revision-log round past that allowance whose
  change order is missing **or incomplete**. Presence is not enough: the allow path requires a
  change order carrying all four required fields from spec.md `## Interfaces & Contracts` —
  `Requested`, an integer `Cost — rounds`, `Cost — time`, and an `Approved by` with a name and
  a date — so an empty or unsigned document fails rather than buying a round. It exits 2 when
  the signed brief declares no allowance at all.

### Roles, gates, and behavior

- **AC15** — `studio-design-qa` blocks handoff as a mechanism, not a claim: it writes
  `handoff/qa-report.md` in the documented schema, and the p6 gate denies the stop while any
  finding marked `blocking` is still `open`, allowing it once each is `resolved`. Every role
  agent denies the `Agent` tool, so no role can spawn its own subagents and the tree stays one
  level deep.
- **AC16** — The non-deterministic surfaces carry eval coverage per `test-tiers.md`, in the
  format the repo's existing harness already runs: an `evals/evals.json` beside the
  question-bank skill, and one beside the studio commands, each entry carrying a prompt and
  assertions with executable `check` commands where the assertion is mechanical. Each suite has
  a runner that actually executes its prompts and grades the files they produce, scored as a
  pass rate over repeated runs — a suite nothing executes cannot produce a reproducible rate.
  The **skill** suite runs on the meta-skills runner. The **commands** suite needs its own,
  `run_command_evals.py`, because `scripts/eval.py` requires a `SKILL.md` and
  `run_behavior_eval.py` stages its target into `.claude/skills/<name>`, so a command
  directory is unreachable through either; the studio runner stages the whole studio namespace
  and invokes each case as a slash command. Evals are manual and stay out of CI; the recorded
  rates are the evidence.

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

- `uv run pytest "tests/harness-layer/test_studio_roster_drift.py::test_roster_table_parses" "tests/harness-layer/test_studio_roster_drift.py::test_every_roster_row_has_an_agent_file" "tests/harness-layer/test_studio_roster_drift.py::test_every_agent_file_has_a_roster_row" "tests/harness-layer/test_studio_roster_drift.py::test_agent_model_matches_its_roster_row" "tests/harness-layer/test_studio_roster_drift.py::test_agent_effort_matches_its_roster_row" "tests/harness-layer/test_studio_roster_drift.py::test_principal_row_is_skipped"` —
  pass: 6 passed. The first guards the parser, so a reformatted roster fails loudly instead of
  silently disabling the gate.
- `uv run pytest tests/harness-layer/test_model_drift.py` — pass: green. Whole-file by design:
  it is parametrized over every declaration in the tree, so the node ids are generated and
  naming them would pin today's file set.

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

- `uv run pytest "tests/harness-layer/hooks/gate-signoff/test_check_gate_signoff.py::test_missing_signoff_file_blocks" "tests/harness-layer/hooks/gate-signoff/test_check_gate_signoff.py::test_empty_approver_blocks" "tests/harness-layer/hooks/gate-signoff/test_check_gate_signoff.py::test_placeholder_date_blocks" "tests/harness-layer/hooks/gate-signoff/test_check_gate_signoff.py::test_empty_artifact_table_blocks" "tests/harness-layer/hooks/gate-signoff/test_check_gate_signoff.py::test_artifact_path_that_does_not_exist_blocks" "tests/harness-layer/hooks/gate-signoff/test_check_gate_signoff.py::test_sha_mismatch_blocks" "tests/harness-layer/hooks/gate-signoff/test_check_gate_signoff.py::test_complete_signoff_allows" "tests/harness-layer/hooks/gate-signoff/test_check_gate_signoff.py::test_no_clients_dir_allows_silently" "tests/harness-layer/hooks/gate-signoff/test_check_gate_signoff.py::test_unknown_phase_argument_fails_open" "tests/harness-layer/hooks/gate-signoff/test_check_gate_signoff.py::test_phase_comes_from_argv_not_mtime" "tests/harness-layer/hooks/gate-signoff/test_check_gate_signoff.py::test_cwd_selects_the_project_when_two_exist" "tests/harness-layer/hooks/gate-signoff/test_check_gate_signoff.py::test_two_projects_and_outside_cwd_fails_open" "tests/harness-layer/hooks/gate-signoff/test_check_gate_signoff.py::test_project_without_signoff_dir_still_blocks" "tests/harness-layer/hooks/gate-signoff/test_check_gate_signoff.py::test_stop_hook_active_allows_with_warning" "tests/harness-layer/hooks/gate-signoff/test_check_gate_signoff.py::test_absolute_artifact_path_blocks" "tests/harness-layer/hooks/gate-signoff/test_check_gate_signoff.py::test_parent_traversal_artifact_path_blocks" "tests/harness-layer/hooks/gate-signoff/test_check_gate_signoff.py::test_symlinked_artifact_outside_the_project_blocks" "tests/harness-layer/hooks/gate-signoff/test_check_gate_signoff.py::test_signoff_missing_a_required_artifact_blocks[p2-definition/project-brief.md]" "tests/harness-layer/hooks/gate-signoff/test_check_gate_signoff.py::test_signoff_missing_a_required_artifact_blocks[p2-definition/sitemap.md]" "tests/harness-layer/hooks/gate-signoff/test_check_gate_signoff.py::test_signoff_missing_a_required_artifact_blocks[p3-structure/wireframes.md]" "tests/harness-layer/hooks/gate-signoff/test_check_gate_signoff.py::test_signoff_missing_a_required_artifact_blocks[p3-structure/inventory.md]" "tests/harness-layer/hooks/gate-signoff/test_check_gate_signoff.py::test_signoff_missing_a_required_artifact_blocks[p4-art-direction/rationale.md]" "tests/harness-layer/hooks/gate-signoff/test_check_gate_signoff.py::test_signoff_missing_a_required_artifact_blocks[p4-art-direction/style-tile.md]" "tests/harness-layer/hooks/gate-signoff/test_check_gate_signoff.py::test_signoff_missing_a_required_artifact_blocks[p6-handoff/pack.md]" "tests/harness-layer/hooks/gate-signoff/test_check_gate_signoff.py::test_signoff_missing_a_required_artifact_blocks[p6-handoff/states-matrix.md]" "tests/harness-layer/hooks/gate-signoff/test_check_gate_signoff.py::test_signoff_missing_a_required_artifact_blocks[p6-handoff/tokens.md]"` —
  pass: 26 passed. `test_project_without_signoff_dir_still_blocks` is the one that proves a
  brand-new project is gated rather than defined away as "no projects"; the three path cases
  prove a signature cannot approve a file outside the engagement it signs; and the nine
  required-artifact cases prove a gate cannot close on a signature over some unrelated file.

### AC9 — the cold-designer triage gates p2, and the QA report gates p6

- `uv run pytest "tests/harness-layer/hooks/gate-signoff/test_check_gate_signoff.py::test_p2_missing_triage_blocks" "tests/harness-layer/hooks/gate-signoff/test_check_gate_signoff.py::test_p2_untriaged_row_blocks" "tests/harness-layer/hooks/gate-signoff/test_check_gate_signoff.py::test_p2_fully_triaged_allows" "tests/harness-layer/hooks/gate-signoff/test_check_gate_signoff.py::test_p3_p4_p6_do_not_require_triage" "tests/harness-layer/hooks/gate-signoff/test_check_gate_signoff.py::test_p3_missing_inventory_blocks" "tests/harness-layer/hooks/gate-signoff/test_check_gate_signoff.py::test_p3_inventory_absent_from_signoff_table_blocks" "tests/harness-layer/hooks/gate-signoff/test_check_gate_signoff.py::test_p3_signed_inventory_allows" "tests/harness-layer/hooks/gate-signoff/test_check_gate_signoff.py::test_p6_inventory_mutated_after_p3_signoff_blocks" "tests/harness-layer/hooks/gate-signoff/test_check_gate_signoff.py::test_p6_inventory_matching_p3_sha_allows" "tests/harness-layer/hooks/gate-signoff/test_check_gate_signoff.py::test_p6_unreadable_qa_status_blocks" "tests/harness-layer/hooks/gate-signoff/test_check_gate_signoff.py::test_p6_misspelled_qa_severity_blocks" "tests/harness-layer/hooks/gate-signoff/test_check_gate_signoff.py::test_p6_blank_qa_cell_blocks"` —
  pass: 12 passed. The diff itself never gates; only the triage document does. The three p3
  cases are what make the P6 denominator client-approved rather than self-declared,
  `test_p6_inventory_mutated_after_p3_signoff_blocks` proves the signature is re-checked at P6
  rather than trusted from three phases back, and the last three prove a QA row the gate cannot
  read blocks rather than reading as resolved.

### AC10 — the new hook is registered, cataloged, and dispositioned

- `uv run pytest "tests/harness-layer/hooks/test_wiring.py::test_every_entrypoint_is_claimed_by_a_registration_surface" "tests/harness-layer/hooks/test_wiring.py::test_command_scoped_references_point_at_real_files" "tests/harness-layer/hooks/test_wiring.py::test_dispositions_cover_every_entrypoint" "tests/harness-layer/hooks/test_wiring.py::test_dispositions_agree_with_codex_registrations" "tests/harness-layer/hooks/test_wiring.py::test_hooks_md_codex_column_matches_family_dispositions"` —
  pass: 5 passed. Each fails if the new hook's registration, Codex verdict, or `hooks.md`
  catalog row is missing.

### AC11 — the states matrix counts cells and cannot pass empty

- `uv run pytest "tests/harness-layer/studio-layer/test_studio_checks.py::test_full_matrix_passes" "tests/harness-layer/studio-layer/test_studio_checks.py::test_single_blank_cell_fails_and_names_it" "tests/harness-layer/studio-layer/test_studio_checks.py::test_component_row_with_no_states_fails" "tests/harness-layer/studio-layer/test_studio_checks.py::test_matrix_with_no_component_rows_fails" "tests/harness-layer/studio-layer/test_studio_checks.py::test_matrix_with_no_breakpoints_fails" "tests/harness-layer/studio-layer/test_studio_checks.py::test_missing_state_column_fails" "tests/harness-layer/studio-layer/test_studio_checks.py::test_duplicate_matrix_row_exits_2" "tests/harness-layer/studio-layer/test_studio_checks.py::test_short_row_exits_2[matrix]" "tests/harness-layer/studio-layer/test_studio_checks.py::test_short_row_exits_2[inventory]"` —
  pass: 9 passed. Three of them stop a vacuous pass; the duplicate-row case stops a filled row
  hiding an earlier blank one, and the short-row cases prove a malformed table exits 2 rather
  than reporting a design failure a designer would chase.

### AC12 — contrast and tap targets are computed, not asserted

- `uv run pytest "tests/harness-layer/studio-layer/test_studio_checks.py::test_known_pair_matches_hand_computed_ratio" "tests/harness-layer/studio-layer/test_studio_checks.py::test_pair_below_threshold_fails" "tests/harness-layer/studio-layer/test_studio_checks.py::test_undersized_tap_target_fails" "tests/harness-layer/studio-layer/test_studio_checks.py::test_empty_pair_table_fails" "tests/harness-layer/studio-layer/test_studio_checks.py::test_empty_target_table_fails" "tests/harness-layer/studio-layer/test_studio_checks.py::test_malformed_hex_exits_2" "tests/harness-layer/studio-layer/test_studio_checks.py::test_token_named_only_in_used_for_is_not_covered"` —
  pass: 7 passed. The first pins the arithmetic against a hand-computed value; `test_malformed_hex_exits_2`
  proves a typo is never reported as a contrast failure; and the last proves a token merely
  mentioned in `Used for` is not counted as covered.

### AC13 — the revision count is arithmetic

- `uv run pytest "tests/harness-layer/studio-layer/test_studio_checks.py::test_round_within_allowance_passes" "tests/harness-layer/studio-layer/test_studio_checks.py::test_round_past_allowance_without_change_order_fails" "tests/harness-layer/studio-layer/test_studio_checks.py::test_round_past_allowance_with_complete_change_order_passes" "tests/harness-layer/studio-layer/test_studio_checks.py::test_change_order_missing_cost_rounds_fails" "tests/harness-layer/studio-layer/test_studio_checks.py::test_unsigned_change_order_fails" "tests/harness-layer/studio-layer/test_studio_checks.py::test_brief_with_no_allowance_exits_2" "tests/harness-layer/studio-layer/test_studio_checks.py::test_allowance_is_re_derived_from_the_signed_brief" "tests/harness-layer/studio-layer/test_studio_checks.py::test_brief_edited_after_signature_exits_2" "tests/harness-layer/studio-layer/test_studio_checks.py::test_unsigned_brief_exits_2" "tests/harness-layer/studio-layer/test_studio_checks.py::test_malformed_allowance_line_exits_2" "tests/harness-layer/studio-layer/test_studio_checks.py::test_change_order_buying_zero_rounds_fails" "tests/harness-layer/studio-layer/test_studio_checks.py::test_one_change_order_cannot_buy_two_rounds" "tests/harness-layer/studio-layer/test_studio_checks.py::test_change_order_buying_two_rounds_covers_both" "tests/harness-layer/studio-layer/test_studio_checks.py::test_misnumbered_rounds_exit_2[duplicate]" "tests/harness-layer/studio-layer/test_studio_checks.py::test_misnumbered_rounds_exit_2[skipped]" "tests/harness-layer/studio-layer/test_studio_checks.py::test_misnumbered_rounds_exit_2[zero]" "tests/harness-layer/studio-layer/test_studio_checks.py::test_misnumbered_rounds_exit_2[negative]"` —
  pass: 17 passed. The change-order cases stop an empty, unpaid or over-used document from
  buying a round; `test_allowance_is_re_derived_from_the_signed_brief` proves the number is read
  from the brief rather than hard-coded, while `test_brief_edited_after_signature_exits_2` proves
  editing it after the client signed buys nothing; and the four misnumbered cases prove the
  rounds are counted rather than taken on trust.

### AC15 — design QA blocks handoff, and no role spawns subagents

- `uv run pytest "tests/harness-layer/hooks/gate-signoff/test_check_gate_signoff.py::test_p6_open_blocking_qa_finding_blocks" "tests/harness-layer/hooks/gate-signoff/test_check_gate_signoff.py::test_p6_all_blocking_findings_resolved_allows" "tests/harness-layer/hooks/gate-signoff/test_check_gate_signoff.py::test_p6_advisory_finding_does_not_block"` —
  pass: 3 passed.
- `bash specs/cpo-layer/checks/ac3-role-agents.sh` — pass: exit 0; it asserts no role can
  spawn a subagent, accepting either `disallowedTools: Agent` or a `tools:` allowlist that
  omits `Agent`.

### AC16 — the non-deterministic surfaces carry runnable evals

- `(cd .claude/skills/meta-skills && uv run --with pyyaml python -m scripts.eval ../studio-layer/studio-client-questions --lint)` —
  pass: exit 0. The `cd` is load-bearing and so is the relative target: `-m scripts.eval`
  only imports with the harness directory as cwd, and `eval.py` resolves `skill_dir` against
  that same cwd — so a repo-root-relative path resolves under `meta-skills/` and exits 1
  with `No SKILL.md`. Verified during planning against an existing skill. Judge this by the
  exit code, never by grepping for `FAIL`: the path failure prints no such token.
- `manual: (cd .claude/skills/meta-skills && uv run --with pyyaml python -m scripts.eval ../studio-layer/studio-client-questions --behavior --yes)` —
  pass: every assertion in that skill's `evals/evals.json` meets its rubric on the recorded
  majority of runs; the pass rate is recorded in `implementation-notes.md`. Per
  `test-tiers.md` evals stay manual and out of CI, so the recorded rate is the evidence — a
  single green run proves nothing.
- `uv run --script .claude/scripts/studio-layer/run_command_evals.py .claude/commands/studio-layer --lint` —
  pass: exit 0. Schema-only, grades nothing, spends no tokens.
- `manual: uv run --script .claude/scripts/studio-layer/run_command_evals.py .claude/commands/studio-layer -k 3 --yes` —
  pass: every case clears its recorded pass rate over the 3 runs; the rates are recorded in
  `implementation-notes.md`. This is the runner that makes the commands suite executable
  rather than prose — the meta-skills runner cannot reach a command directory.
- `uv run pytest "tests/harness-layer/studio-layer/test_run_command_evals.py::test_every_relative_link_in_the_staged_namespace_resolves_inside_the_scratch_project" "tests/harness-layer/studio-layer/test_run_command_evals.py::test_an_errored_run_scores_zero_whatever_its_partial_files_satisfy" "tests/harness-layer/studio-layer/test_run_command_evals.py::test_a_workspace_holding_an_earlier_run_exits_two" "tests/harness-layer/studio-layer/test_run_command_evals.py::test_lint_rejects_two_cases_sharing_an_id" "tests/harness-layer/studio-layer/test_run_command_evals.py::test_lint_rejects_an_id_that_could_not_name_a_run_or_key_a_verdict" "tests/harness-layer/studio-layer/test_run_command_evals.py::test_the_staged_project_is_the_git_top_level_the_commands_anchor_on" "tests/harness-layer/studio-layer/test_run_command_evals.py::test_the_staged_repository_carries_its_own_identity" "tests/harness-layer/studio-layer/test_run_command_evals.py::test_a_commands_anchored_project_dir_resolves_inside_the_scratch_project" "tests/harness-layer/studio-layer/test_run_command_evals.py::test_lint_rejects_two_cases_whose_ids_differ_only_in_type" "tests/harness-layer/studio-layer/test_run_command_evals.py::test_an_integer_assertion_id_matches_the_verdict_the_judge_returns"` —
  pass: 11 passed — one id is parametrized over two malformed shapes. These pin the runner's
  own contract: the staged scratch project is a git repository whose top level is what the
  commands' `$(git rev-parse --show-toplevel)` anchor resolves to, it has no dangling rule
  link, a run the CLI reported as errored scores zero however many partial files it left
  behind, a reused workspace is refused rather than graded against stale output, and an id
  that could not name a run directory or key a verdict is rejected at lint time.
- `bash specs/cpo-layer/checks/ac16-evals-are-runnable.sh` — pass: exit 0. Asserts the eval
  files exist in the harness's `evals/evals.json` schema (a `skill_name`, an `evals` array,
  and every entry carrying `id`, `name`, `prompt`, and a non-empty `assertions` list), so the
  claimed pass rates are reproducible rather than prose.

### AC14 — the whole suite stays green

- `uv run pytest` — pass: exit 0, no failures.
- `uv run ruff check .` — pass: exit 0.
- `uv run ruff format --check .` — pass: exit 0.
