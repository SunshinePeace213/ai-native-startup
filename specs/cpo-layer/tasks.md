# Tasks: studio-layer — design-delivery studio through signed handoff

> Execution plan for [spec.md](./spec.md). Owner and scope are defined there; this file is
> how & who. Orchestration mechanics live in `.claude/rules/orchestration.md`.

## Implementation Phases

### Phase 1: Ground the namespace

The roster is the source of truth every later stamp is re-derived from, and the rules are
path-scoped, so nothing that reads them can be written until they exist.

- `studio-namespace`, `studio-roster`, `studio-client-artifacts`

### Phase 2: Roles and the question bank

Nine agent files stamp themselves from the roster; the skill is what the client-facing roles
invoke. Both are prerequisites for the commands that spawn and invoke them.

- `studio-role-agents`, `studio-question-bank`

### Phase 3: Mechanisms that can fail

The hook and the four check scripts, each landing with its tests. These are independent of
each other and of the commands that will call them, so they run in parallel.

- `gate-signoff-hook`, `studio-check-scripts`, `studio-roster-drift-test`

### Phase 4: The eight phase commands

Commands name the roles they spawn, the scripts they run, and — for the four hard gates —
register the hook. Every referent must already exist.

- `studio-phase-commands`

### Phase 5: Evidence

- `studio-command-eval-runner`, then `validate-all`

The seven plan-local checks under `specs/cpo-layer/checks/` are already written and committed
with this plan — they fail on today's tree and pass once the build lands. The build runs them;
it does not author them.

## Step by Step Tasks

### 1. Claim the namespace, the client-data home, and the studio identity

- **Task ID:** `studio-namespace`
- **Depends On:** none
- **Agent Type:** `general-purpose`
- **Model / Effort:** `sonnet` / `medium` per `.claude/rules/model-selection.md` — a scoped
  config edit plus one short rule, precisely specified.
- **Files:** `.gitignore`, `clients/.gitkeep`, `.claude/rules/studio-layer/studio-identity.md`,
  `AGENTS.md`
- **Parallel:** true
- **Satisfies:** AC1, AC5
- **Verify:** `git check-ignore -v clients/acme/site/brief.md` names the new rule, and
  `git status --porcelain clients/` is empty after writing a scratch file there.
- Add a `clients/` section to `.gitignore` with a comment stating the boundary: client project
  data lives here so path-scoped rules and command hooks resolve, and never enters history.
  Use exactly this pattern pair — verified during planning:

  ```gitignore
  clients/*
  !clients/.gitkeep
  ```

  `clients/` (the whole directory) instead of `clients/*` makes `.gitkeep` **untrackable**:
  git never descends into an excluded directory, so the negation cannot re-include it and
  `git add clients/.gitkeep` fails silently. AC1 asserts the file is tracked, so the wrong
  pattern fails the check rather than shipping a directory contract that vanishes on a clean
  checkout.
- Write `studio-identity.md` with `paths: clients/**` frontmatter: the Soriza name and what the
  studio sells, the client-facing voice, the document letterhead, and the sign-off block shape
  from spec.md `## Interfaces & Contracts` that every client-facing document inherits.
- Add a `## Studio Layer` section to `AGENTS.md` pointing at the three new rules, per
  `memory-series.md`'s "add a pointer from the matching AGENTS.md section". Keep it to the
  pointer — no duplicated guidance.

### 2. Cast the roster from the model table

- **Task ID:** `studio-roster`
- **Depends On:** none
- **Agent Type:** `general-purpose`
- **Model / Effort:** `opus` / `high` per `.claude/rules/model-selection.md` — the roster is
  the source of truth a drift test re-derives from, and it encodes taste requirements.
- **Files:** `.claude/rules/studio-layer/roster.md`
- **Parallel:** true
- **Satisfies:** AC2, AC5
- **Verify:** the file parses as one markdown table with ten rows; every `Model` cell is an
  alias listed in `model-selection.md`'s Roster and every `Effort` cell appears in its Effort
  table.
- Write `roster.md` with `paths: clients/**` frontmatter and the exact column set from spec.md
  `## Interfaces & Contracts`: Function, Person, Model, Effort, May escalate.
- Ten rows. The principal first — Maya Lindqvist, Principal/CPO, main session, `fable`,
  `xhigh`, orchestrator only, **no agent file** (state this in the row, since it is the one
  row the drift test must skip). Then the nine roles exactly as stamped in spec.md
  `## Relevant Files → New Files`.
- State the escalation rule per role and mark the client-facing roles (art director, content
  strategist) as requiring taste ≥ 7, matching `model-selection.md`.
- No prose beyond one short intro paragraph — this file is read by a parser as well as a
  person.

### 3. Fork the artifact rules for client work

- **Task ID:** `studio-client-artifacts`
- **Depends On:** none
- **Agent Type:** `general-purpose`
- **Model / Effort:** `opus` / `high` per `.claude/rules/model-selection.md` — client-facing
  artifact direction, taste ≥ 7.
- **Files:** `.claude/rules/studio-layer/client-artifacts.md`
- **Parallel:** true
- **Satisfies:** AC4, AC5
- **Verify:** the file contains no 6-digit hex literal, references `artifacts.md`, and its
  page-pattern table has exactly four rows.
- Write `client-artifacts.md` with `paths: clients/**` frontmatter. Inherit craft and publish
  by reference to `.claude/rules/harness-layer/artifacts.md` — do not restate either.
- Replace the palette lock with a palette **source** per phase: the Soriza studio default
  through P0–P3, the picked direction's tokens from P4 onward. Name no hex values.
- Carry the four-row page-pattern table: brief review → inline suggestions; sitemap → the
  ordering board; art direction → design directions; feedback triage → disposition cards.
  Each row states what its copy-as-prompt returns.
- Guardrail: this is a fork, not an edit. Leave `artifacts.md` untouched.

### 4. Write the nine role agents

- **Task ID:** `studio-role-agents`
- **Depends On:** `studio-roster`
- **Agent Type:** `general-purpose`
- **Model / Effort:** `opus` / `high` per `.claude/rules/model-selection.md` — nine
  client-facing role definitions whose descriptions control routing; taste ≥ 7.
- **Files:** `.claude/agents/studio-layer/` (all nine files)
- **Parallel:** false
- **Satisfies:** AC2, AC3
- **Verify:** `uv run --with pyyaml python .claude/skills/meta-agent/scripts/validate_agent.py <file>`
  is clean for each of the nine.
- Follow the `meta-agent` skill for frontmatter and body shape; match the house style in
  `.claude/agents/kb-fetcher.md`.
- `name:` is the plain layer-prefixed function and equals the filename stem. The person opens
  the body — never the name, never the description.
- Stamp `model:` and `effort:` from `roster.md`. A mismatch is what `studio-roster-drift-test`
  exists to catch; do not invent a stamp.
- Withhold the `Agent` tool on every role — `disallowedTools: Agent`, or a `tools:`
  allowlist that omits it where a seat needs other tools withheld too. Subagents inherit the
  `Agent` tool by default, so without this the "one level deep" architecture is unenforced
  and a role could spawn its own subagents.
- No `skills:` frontmatter on any role — preloading is not access. Each body restates what it
  needs and, for the client-facing roles, says to invoke `studio-client-questions` via the
  `Skill` tool.
- Give each role its owned documents and phases from spec.md's `### The eight phases` table —
  that table is authoritative; do not read the discovery HTML for this.
- `studio-design-qa` (Yusuf Demir) is adversarial and blocks handoff: its body judges focus
  order, whether each state makes sense, and whether error copy says anything useful, and it
  explicitly does **not** recompute what `check_contrast.py` and `check_states_matrix.py`
  compute. It writes `handoff/qa-report.md` in the schema from spec.md
  `## Interfaces & Contracts`, marking each finding `blocking` or `advisory` — that file is
  what the p6 gate reads, so "blocks handoff" is a mechanism rather than a claim.

### 5. Build the client question bank as an invocable skill

- **Task ID:** `studio-question-bank`
- **Depends On:** none
- **Agent Type:** `general-purpose`
- **Model / Effort:** `opus` / `high` per `.claude/rules/model-selection.md` — the question
  quality is what makes discovery work; client-facing.
- **Files:** `.claude/skills/studio-layer/studio-client-questions/SKILL.md`,
  `.claude/skills/studio-layer/studio-client-questions/evals/evals.json`
- **Parallel:** true
- **Satisfies:** AC6, AC16
- **Verify:** frontmatter carries `name` and `description` and does **not** carry
  `disable-model-invocation`; the question list parses as one machine-readable section.
- Follow the `meta-skills` skill for authoring. `name: studio-client-questions`, and the
  **directory** must be `studio-client-questions/` to match: the directory name, not the
  `name:` field, becomes the command a role invokes.
- Write eval cases in
  `.claude/skills/studio-layer/studio-client-questions/evals/evals.json`, in the schema the
  repo's harness already runs (`skill_name`, an `evals` array, each entry with `id`, `name`,
  `prompt`, and `assertions` carrying an executable `check` wherever the assertion is
  mechanical). Follow `meta-skills` → `references/evaluation.md`; do not invent a markdown
  eval format, since a rubric nothing executes cannot produce a reproducible pass rate. The
  bank is prose, so only an eval shows whether its questions actually surface the dimension.
- Cover the client discovery dimensions: the job the site does, the audience and their
  situation, brand voice, references loved and hated, the content that actually exists, hard
  constraints (existing brand, CMS, deadline), budget, and what success looks like at six
  months.
- Structure the questions so `check_question_coverage.py` can re-derive the dimension list from
  this file — one stable heading or list marker per dimension. Agree the exact shape with
  `studio-check-scripts`; the checker must parse this file, never carry its own copy.
- Do **not** set `disable-model-invocation: true`. It would make the skill user-invocable only
  and put it out of reach of the roles meant to invoke it.

### 6. Build the sign-off Stop gate

- **Task ID:** `gate-signoff-hook`
- **Depends On:** none
- **Agent Type:** `general-purpose`
- **Model / Effort:** `opus` / `high` per `.claude/rules/model-selection.md` —
  verification-shaped work that also edits the fixture every hook test depends on.
- **Files:** `.claude/hooks/check_gate_signoff.py`,
  `tests/harness-layer/hooks/gate-signoff/test_check_gate_signoff.py`,
  `tests/harness-layer/hooks/conftest.py`, `tests/harness-layer/hooks/test_wiring.py`,
  `.claude/rules/harness-layer/hooks.md`
- **Parallel:** true
- **Satisfies:** AC8, AC9, AC10
- **Verify:** `uv run pytest tests/harness-layer/hooks/` — green, including the pre-existing
  wiring and contract suites.
- Write the hook as a PEP 723 `# /// script` file with `dependencies = []`, modeled on
  `check_spec_completeness.py`: resolve the root from `CLAUDE_PROJECT_DIR` with a
  `git rev-parse` fallback, exit 2 to deny the stop with repair instructions on stderr, and
  fail open (exit 0) on malformed stdin, a missing root, or any plumbing failure.
- Take the phase from `argv[1]`. Never infer it from mtime — a client project holds all eight
  phase folders at once. A missing or unrecognized phase argument is a **registration**
  mistake, so exit 0: the repo hook contract fails plumbing failures open, and
  `test_wiring.py` is what catches a bad registration, at CI time rather than mid-engagement.
- Resolve the project by the three-step rule in spec.md `## Interfaces & Contracts` →
  "Project targeting": the Stop payload's `cwd` when it is inside a project, else the sole
  project, else exit 0 reporting the ambiguity. Test it with two projects present.
- Check the phase's sign-off file for a filled Approver and Date, and for an artifact table
  with at least one row where every path exists and every SHA-256 matches that file's current
  content. Empty, whitespace-only, and template-placeholder values all count as missing.
- Handle `stop_hook_active`: block on the first stop; on re-entry allow the stop and print the
  unresolved gate to stderr. A client signature will not appear because Claude tried again,
  and Claude Code force-ends the turn after 8 consecutive blocks — so re-blocking burns the
  turn and ends in the same place. Test both values of the flag.
- For `p2`, additionally require the cold-designer triage document with no untriaged row. For
  `p3`, additionally require `structure/inventory.md` to exist, be non-empty, and appear as a
  row in that phase's sign-off artifact table — the inventory is what P6's matrix and contrast
  checks quantify over, so it has to be client-approved at P3 rather than authored at P6. For
  `p6`, additionally require `handoff/qa-report.md` with no `blocking` finding still `open`,
  **and re-verify `structure/inventory.md` against the SHA-256 recorded for it in the P3
  sign-off** — block on a mismatch or on a P3 sign-off that never listed it. A signature three
  phases back says nothing about the file P6 measures the design against; without this step,
  deleting rows between P3 and P6 shrinks the denominator silently. Test the mutation case
  directly: sign at P3, edit the inventory, confirm p6 blocks.
- No `clients/` directory → exit 0 silently, mirroring how the spec gate is invisible without
  `specs/`.
- Extend `run_hook` in `tests/harness-layer/hooks/conftest.py` with `args: tuple = ()` appended
  after the script path, per spec.md `## Interfaces & Contracts`. Existing call sites pass
  nothing and must stay untouched.
- Add `"check_gate_signoff.py": "not-applicable"` to `CODEX_DISPOSITIONS` in `test_wiring.py`
  — studio commands are Claude slash commands, like the spec gate.
- Add the catalog row to `.claude/rules/harness-layer/hooks.md`: event `Stop (command-scoped)`,
  what it does, Codex column `not-applicable`. The wiring suite cross-checks this table against
  `CODEX_DISPOSITIONS` in both directions.
- Test both the block and the allow path for every field, per `hooks.md`'s testing rules.
  Launch only through `run_hook`; every docstring states why the behavior matters.

### 7. Build the four studio check scripts

- **Task ID:** `studio-check-scripts`
- **Depends On:** `studio-question-bank`
- **Agent Type:** `general-purpose`
- **Model / Effort:** `opus` / `high` per `.claude/rules/model-selection.md` — parser and
  arithmetic work; the build stage has no Codex path, so the highest Claude tier available to
  a subagent carries it and the Codex review gate judges the result.
- **Files:** `.claude/scripts/studio-layer/` (all four scripts),
  `tests/harness-layer/studio-layer/test_studio_checks.py`
- **Parallel:** false
- **Satisfies:** AC6, AC11, AC12, AC13
- **Verify:** `uv run pytest tests/harness-layer/studio-layer/` — green.
- All four are PEP 723 scripts with `dependencies = []`, taking their target as `argv[1]`, per
  the CLI contract in spec.md. Exit 0 pass, 1 countable failure with `file:line` diagnostics,
  2 usage/parse error.
- `check_states_matrix.py`: read `structure/inventory.md` first — the client-signed,
  authoritative component list — then require a matrix row for every component × breakpoint pair it names,
  and exit 1 naming every missing pair and every unfilled cell across hover, focus, disabled,
  loading, empty and error. A component row with no state columns is unfilled, not skipped.
  An empty or absent inventory exits 2: without a baseline the check would quantify only over
  what happens to be declared, and a one-component matrix would pass a ten-component design.
- `check_contrast.py`: parse the token table, compute relative luminance and the contrast
  ratio for every declared foreground/background pair, and compare against the thresholds
  recorded in decisions.md `## Assumptions` (4.5:1 normal text, 3:1 large text and UI
  components, 24×24 CSS px minimum target). Name them **Soriza project thresholds** in the
  output — the repo has not mirrored WCAG 2.2, so the script must not claim conformance to a
  specification it cannot cite. Cross-check against `structure/inventory.md`: every colour token
  it names must appear in at least one checked pair, and every component must have a
  tap-target row, so one compliant pair cannot stand in for the rest. It reads the same
  client-signed `structure/inventory.md`. Malformed hex, an empty table, or a missing
  inventory → exit 2, never 1. Pin at least one hand-computed ratio in the
  tests so the arithmetic itself is checked, not just the branching.
- `check_question_coverage.py`: re-derive the dimension list by parsing the question-bank
  `SKILL.md`, then exit 1 for any dimension the discovery notes leave unanswered without an
  explicit "N/A, because". Never carry a second copy of the dimension list — a test must show
  that adding a question to the skill changes what the checker requires.
- `check_revision_count.py`: re-derive the allowance from the signed brief, walk the revision
  log, and exit 1 on a round past the allowance whose change order is missing **or
  incomplete**. A referenced change order must carry all four required fields from spec.md
  `## Interfaces & Contracts` — `Requested`, an integer `Cost — rounds`, `Cost — time`, and an
  `Approved by` with a name and date. Accepting any file that merely exists would let an empty
  document buy a revision round. No allowance in the brief → exit 2.
- Mirror the test layout under `tests/harness-layer/studio-layer/`, using `tmp_path` fixtures
  so the suite stays parallel-safe. These are not hooks — do not use the `run_hook` fixture and
  do not place them under `.claude/hooks/`.

### 8. Pin the roster against the agent files

- **Task ID:** `studio-roster-drift-test`
- **Depends On:** `studio-roster`, `studio-role-agents`
- **Agent Type:** `general-purpose`
- **Model / Effort:** `sonnet` / `high` per `.claude/rules/model-selection.md` — a scoped
  drift test on an established pattern, but verification-shaped, so effort stays at the default.
- **Files:** `tests/harness-layer/test_studio_roster_drift.py`
- **Parallel:** false
- **Satisfies:** AC2
- **Verify:** `uv run pytest tests/harness-layer/test_studio_roster_drift.py` — green; then
  hand-edit one agent file's `effort`, confirm the suite goes red, and revert.
- Re-derive every expectation from `roster.md`. Parse its table the way `test_model_drift.py`
  parses `model-selection.md` — structure, not prose — and reuse that file's frontmatter parser
  shape rather than inventing a second one.
- Assert per role: the agent file exists, its `model` matches the roster row, and its `effort`
  matches. Skip the principal's row, which declares no agent file by design.
- Assert both directions: a roster row with no agent file fails naming the file, and an agent
  file under `.claude/agents/studio-layer/` with no roster row fails naming the orphan.
- Guard the parser itself with a test that fails loudly if the table stops parsing, so a
  reformatted roster cannot silently disable the gate — the `test_roster_parses_into_both_provider_families`
  pattern.
- Every docstring states why the behavior matters.

### 9. Write the eight phase commands

- **Task ID:** `studio-phase-commands`
- **Depends On:** `studio-role-agents`, `studio-question-bank`, `gate-signoff-hook`,
  `studio-check-scripts`, `studio-client-artifacts`
- **Agent Type:** `general-purpose`
- **Model / Effort:** `opus` / `high` per `.claude/rules/model-selection.md` — eight
  interlocking command prompts, including the forked interview loop; user-facing, taste ≥ 7.
- **Files:** `.claude/commands/studio-layer/` (all eight files),
  `.claude/commands/studio-layer/evals/evals.json`
- **Parallel:** false
- **Satisfies:** AC7, AC9, AC15, AC16
- **Verify:** `uv run pytest tests/harness-layer/hooks/test_wiring.py` — green (every
  frontmatter registration points at a real file), and
  `bash specs/cpo-layer/checks/ac7-phase-commands.sh` — exit 0.
- Write eval cases in `.claude/commands/studio-layer/evals/evals.json`, same harness schema
  as the skill's. Commands are non-deterministic prose, which `test-tiers.md` puts in the
  **eval** tier — a structural check proves a command exists, never that it behaves. These
  two produce gradeable output, so per `meta-skills` they earn evals: P1 must produce a
  discovery-notes file that `check_question_coverage.py` passes (an executable `check`), and
  P2 must produce a triage document with a disposition on every row. Record pass rates over
  repeated runs; evals stay manual and out of CI.
- Shape each command like the harness eight: frontmatter (`description`, `argument-hint`,
  `model`, `effort`, `disable-model-invocation: true`), then the phase's documents, the roles
  the principal spawns, the gate, and the report block. Keep them short — every line loads into
  context.
- Stamp each command `model: fable`, `effort: xhigh` — the principal runs them and is the
  orchestrator, per `roster.md`.
- Phases, documents, staffing and gates come from spec.md `### The eight phases` — that table
  is authoritative; do not read the discovery HTML for this.
- **P3 writes `structure/inventory.md`** and lists it in the P3 sign-off artifact table.
  `studio-ux-architect` enumerates it from the signed wireframes and content model, one row per
  component with its breakpoints and colour tokens, in the schema from spec.md
  `## Interfaces & Contracts`. This is the list P6's matrix and contrast checks quantify over,
  so it must be complete at P3 and approved by the client — P6 never authors it.
- P2, P3, P4, P6 register the Stop hook in frontmatter with their own phase token, exactly as
  spec.md `## Interfaces & Contracts` shows. No other studio command registers it.
- **P1 is the forked interview.** Take the round mechanics from `harness-interview.md:32-42` —
  a coverage ledger, one round at a time ordered by blast radius, and the bounded stop when a
  round resolves nothing new — and swap the harness dimensions for the client ones. Each round
  publishes an interactive artifact per `client-artifacts.md` that the client reacts to. The
  principal conducts every round via `AskUserQuestion`; `studio-discovery-lead` prepares the
  question set from the bank beforehand and turns answers into written statements and glossary
  entries afterward. Do not edit `harness-interview.md`.
- P2 runs the cold-designer test with an **ordinary subagent**, not a teammate: spawn
  `studio-ux-architect` with a prompt carrying only the signed project and creative briefs —
  no other context — ask for the section-level plan, diff it against the signed sitemap, and
  triage every row. A subagent has its own context window and inherits none of the principal's
  conversation, which is the whole property the test needs. The diff is advisory; the triage
  document is what the gate requires.
- **Every check script is invoked by the phase that owns it** — a script nothing runs is an
  orphaned mechanism:
  - P1 runs `check_question_coverage.py` on the discovery notes before its soft gate, and
    reports the result.
  - P5 runs `check_revision_count.py` before closing each round, and names the change-order
    path when it fails.
  - P6 runs `check_states_matrix.py` and `check_contrast.py` on the handoff, then spawns
    `studio-design-qa`, which writes `handoff/qa-report.md`. The p6 Stop gate reads that
    report, so an unresolved blocking finding keeps the phase open.
- Each phase command writes its documents in the exact schemas from spec.md
  `## Interfaces & Contracts`. A command that invents its own table shape fails its check.
- P5 takes the prototype tool as an argument and applies the selection rules from the same
  section, recording the choice in the prompt pack.
- P7 routes each lesson to the file where it will load again, and explicitly does not graduate
  lessons into skills — that is card 10.

### 10. Build the command-eval runner

- **Task ID:** `studio-command-eval-runner`
- **Depends On:** `studio-phase-commands`
- **Agent Type:** `general-purpose`
- **Model / Effort:** `opus` / `high` per `.claude/rules/model-selection.md` — subprocess
  orchestration and grading logic, and it is what makes AC16's commands half real.
- **Files:** `.claude/scripts/studio-layer/run_command_evals.py`,
  `tests/harness-layer/studio-layer/test_run_command_evals.py`
- **Parallel:** false
- **Satisfies:** AC16
- **Verify:** `uv run --script .claude/scripts/studio-layer/run_command_evals.py .claude/commands/studio-layer --lint`
  exits 0, and `uv run pytest tests/harness-layer/studio-layer/test_run_command_evals.py` is green.
- Model it on `.claude/skills/meta-skills/scripts/run_behavior_eval.py` — scratch project,
  `claude -p` per run, judge-graded assertions, pass rate over `k` runs. Reuse that shape
  rather than inventing a second one; the CLI and behavior are in spec.md
  `## Interfaces & Contracts` → "Command-eval runner".
- It exists because the meta-skills runner cannot reach a command: `eval.py` requires a
  `SKILL.md` and `run_behavior_eval.py` stages into `<scratch>/.claude/skills/<name>`, while a
  command is only invocable as `/studio-layer:<name>` from `.claude/commands/`. Do not edit
  either meta-skills script to work around this — they serve every other skill in the repo.
- Stage the whole studio namespace per case —
  `.claude/{commands,agents,skills,rules,scripts}/studio-layer/` plus
  `.claude/hooks/check_gate_signoff.py` — into a throwaway project outside this repo, so the
  command resolves, its roles exist, its check scripts are on disk, and the four hard-gate
  commands find the hook their frontmatter registers, while the repo's own rules never
  contaminate the run. The hook sits outside the studio namespace but P2's registration points
  at `"$CLAUDE_PROJECT_DIR"/.claude/hooks/check_gate_signoff.py`; omitting it would evaluate P2
  with its gate silently missing. Assert the staged layout in a test, including that the P2
  command's registered hook path resolves to a real file inside the scratch project.
- Grade an assertion carrying a `check` by running it against the outputs (exit 0 = pass);
  send the rest to the judge. Exit 0 when every case clears its rate, 1 when one does not, 2 on
  usage or parse failure. `--lint` validates the suite schema only and spends no tokens.
- Test with `--lint` and with a stubbed runner: the token-spending path must not run under
  pytest, so inject the `claude -p` call and assert the staging layout, the `check` grading, and
  the three exit codes against fixtures. Evals stay manual and out of CI.

### 11. Validate Everything

- **Task ID:** `validate-all`
- **Depends On:** every preceding Task ID
- **Agent Type:** `general-purpose`
- **Model / Effort:** `opus` / `high` per `.claude/rules/model-selection.md` — consolidating
  judgment across every criterion.
- **Files:** `specs/cpo-layer/implementation-notes.md` (evidence only — reads everything else)
- **Parallel:** false
- **Satisfies:** AC14, and re-confirms AC1–AC13, AC15
- **Verify:** every command in acceptance-criteria.md `## Validation Commands` passes, and each
  criterion is met.
- Run the full suite and both ruff commands from the repo root, and record the observed output
  in `implementation-notes.md` per `impl-standards.md`.
- Confirm no studio rule loads outside `clients/**`. The `memory-series.md` ~250-line budget
  applies to the **unscoped rules only** (`.claude/rules/*.md`, 254 lines today); this build
  adds no unscoped rule, so that total must not grow. `AGENTS.md` is checked separately and
  only for a concise pointer section — it is not part of that budget.
- Run both manual eval suites and record their pass rates in `implementation-notes.md`. They
  are not part of the CI suite, so an unrecorded eval is an unrun one. The skill suite runs
  through the meta-skills runner; the commands suite runs through `run_command_evals.py`.
  Exact commands are in acceptance-criteria.md `### AC16`.
- Confirm the diff adds no client data, leaves `artifacts.md` and `harness-interview.md`
  untouched, and carries no orphaned files.

## Memory

`studio-phase-commands` and `gate-signoff-hook` must record their outcomes to memory per
`memory-series.md`: the hook's catalog row belongs in `.claude/rules/harness-layer/hooks.md`
(already a task step), and any lesson about the forked interview loop belongs in the studio
command it corrects — never a flat log.
