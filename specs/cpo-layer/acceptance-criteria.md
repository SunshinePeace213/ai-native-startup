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
- **AC5** — `.claude/rules/studio-layer/studio-identity.md` and `roster.md` are both scoped
  `paths: clients/**`, so no studio rule loads during ordinary harness work.
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
  phase's sign-off file is missing, or present with an empty or placeholder Approver, Date, or
  Artifact SHA, or with a SHA that does not match the artifact it claims to approve. It
  returns 0 when all three fields are filled and the SHA matches. With no `clients/` directory
  it returns 0 silently, and it gates the phase given in `argv[1]` regardless of which phase
  folder was modified most recently.
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
  counts as unfilled, not skipped.
- **AC12** — `check_contrast.py` computes the WCAG relative-luminance ratio for every
  foreground/background pair declared in the handoff token table and exits non-zero naming any
  pair below its threshold and any specced tap target below the minimum; it exits 0 on a
  compliant table. A malformed hex value exits 2 (parse error), never 1, so a typo is never
  reported as a contrast failure.
- **AC13** — `check_revision_count.py` re-derives the allowance from the signed brief — not a
  hard-coded number — and exits non-zero for a revision-log round past that allowance with no
  matching change-order document, exits 0 when a change order is present, and exits 2 when the
  signed brief declares no allowance at all.

### Suite health

- **AC14** — `uv run pytest` and `uv run ruff check .` both pass from the repo root with every
  new file present, including the existing hook, wiring, and model-drift suites.

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

- `uv run pytest tests/harness-layer/studio-layer/test_studio_checks.py -k question` — pass:
  green. Covers the unanswered-dimension failure, the explicit "N/A, because" pass, and that
  adding a question to the skill changes what the checker requires.
- `bash specs/cpo-layer/checks/ac6-question-bank-skill.sh` — pass: exit 0. Asserts `SKILL.md`
  exists at the studio-layer path, carries `name`/`description`, and does **not** set
  `disable-model-invocation`.

### AC7 — eight commands, four gate registrations

- `bash specs/cpo-layer/checks/ac7-phase-commands.sh` — pass: exit 0. Asserts the eight
  filenames, and that exactly `{p2,p3,p4,p6}` reference `check_gate_signoff.py` in frontmatter,
  each with its own phase token as the trailing argument.

### AC8 — the sign-off gate blocks and allows for the right reasons

- `uv run pytest tests/harness-layer/hooks/gate-signoff/test_check_gate_signoff.py` — pass:
  green. Covers missing file, each empty field, placeholder field, SHA mismatch, the happy
  path, the no-`clients/` silent pass, and phase-from-argv independence from folder mtime.

### AC9 — the cold-designer triage gates p2 only

- `uv run pytest tests/harness-layer/hooks/gate-signoff/test_check_gate_signoff.py -k triage` —
  pass: green. Covers missing triage doc, an untriaged row, a fully-triaged doc, and that p3,
  p4 and p6 do not require one.

### AC10 — the new hook is registered, cataloged, and dispositioned

- `uv run pytest tests/harness-layer/hooks/test_wiring.py` — pass: green. The existing
  entrypoint-claim, disposition-coverage, and `hooks.md`-catalog assertions all cover the new
  hook; each fails if its row, verdict, or registration is missing.

### AC11 — the states matrix counts cells

- `uv run pytest tests/harness-layer/studio-layer/test_studio_checks.py -k states` — pass:
  green. Covers a full matrix (exit 0), a single blank cell (exit 1, cell named), a
  state-less component row (exit 1), and a missing breakpoint.

### AC12 — contrast and tap targets are computed, not asserted

- `uv run pytest tests/harness-layer/studio-layer/test_studio_checks.py -k contrast` — pass:
  green. Covers a known-ratio pair checked against the hand-computed WCAG value, a pair below
  threshold (exit 1), an undersized tap target (exit 1), and a malformed hex (exit 2).

### AC13 — the revision count is arithmetic

- `uv run pytest tests/harness-layer/studio-layer/test_studio_checks.py -k revision` — pass:
  green. Covers a round within allowance (exit 0), a round past it with no change order
  (exit 1), the same round with a change order (exit 0), an allowance changed in the brief
  changing the verdict, and a brief with no allowance (exit 2).

### AC14 — the whole suite stays green

- `uv run pytest` — pass: exit 0, no failures.
- `uv run ruff check .` — pass: exit 0.
- `uv run ruff format --check .` — pass: exit 0.
