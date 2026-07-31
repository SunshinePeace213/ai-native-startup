# Spec: studio-layer — design-delivery studio through signed handoff

- **Owner:** @SunshinePeace213
- **Status:** Approved

## Tracking

- **Type:** feat
- **Complexity:** complex
- **Issue:** #80
- **Branch:** feat/80-cpo-layer
- **Worktree:** /home/ringo/ai-native-startup/.claude/worktrees/cpo-layer
- **Review profile:** kb-grounded

## Task Description

Build the `studio-layer` — a design-delivery studio for Soriza (an AI startup selling
website design, software development, and agentic-layer services) that owns what gets
built and what it looks like, and stops at a signed layout handoff with no development
work.

The layer runs as eight phase commands driven by the main session acting as principal
(Maya Lindqvist, Principal/CPO — orchestrator only, never a spawned teammate). The
principal spawns nine role agents directly, one level deep. Client project data lives in
a gitignored `clients/<client>/<project>/` inside this repo, so path-scoped rules and
command-frontmatter hooks resolve against `CLAUDE_PROJECT_DIR` while nothing client-owned
enters git history.

Scope is brainstorm cards 01–09: the namespace and client-data home, the roster, the
forked client-discovery loop, the client-artifact rule, the eight phase commands, the
cold-designer test, the sign-off hook, the design-QA verifier, and the revision counter.
Cards 10 (lesson graduation), 11 (design KB mirrors), and 12 (the first real project run)
are follow-on plans.

Every **build-time** decision is already locked in
`specs/cpo-layer/discovery/decisions-draft.md` and transcribed into
[decisions.md](./decisions.md); nothing there is re-interviewed. One question is
deliberately not a build-time decision: which prototype tool P5 drives. It is a **runtime
input** to the P5 command, chosen per project against the selection rules in
`## Interfaces & Contracts`, because the answer belongs to a client engagement and its docs
are what card 11's KB mirror waits on.

### The eight phases

The authoritative phase table. Tasks and commands reference these rows rather than the
discovery pages.

| Phase | Name | Documents | Roles the principal spawns | Gate |
| --- | --- | --- | --- | --- |
| P0 | Intake and qualification | intake form, qualification note | `studio-client-partner` | Soft — internal go / no-go |
| P1 | Discovery | discovery notes, glossary, competitive audit, reference audit | `studio-discovery-lead`, `studio-research-analyst` | Soft — notes reviewed with the client |
| P2 | Definition | project brief, creative brief, sitemap, section briefs, user flows, cold-designer triage | `studio-discovery-lead`, `studio-ux-architect`, `studio-content-strategist` | **Hard** — brief + sitemap signed, triage complete |
| P3 | Structure | annotated lo-fi wireframes, content model, copy outline, component inventory | `studio-ux-architect`, `studio-content-strategist` | **Hard** — wireframes + inventory signed |
| P4 | Art direction | moodboard, style tile, 2–3 directions, direction rationale | `studio-art-director`, `studio-content-strategist` | **Hard** — one direction picked |
| P5 | Prototype | prompt pack, prototype link, revision log | `studio-prototype-engineer`, `studio-art-director` | Rounds — allowance from the signed brief |
| P6 | Design QA and handoff | QA report, accessibility check, handoff pack, sign-off | `studio-design-qa`, `studio-client-partner` | **Hard** — QA clean, final sign-off |
| P7 | Retro and lesson routing | project retro, routed lessons | `studio-retro-scribe` | Soft — lessons committed to their homes |

The handoff pack is tokens, states, breakpoints, copy deck and assets — what a builder
consumes. Producing it ends the engagement.

## Objective

`/studio-layer:p0-intake` through `/studio-layer:p7-retro` exist and run; each hard gate
(P2, P3, P4, P6) refuses to close without a signed document the hook can read; and each
countable design claim — states matrix, contrast, question coverage, revision rounds,
role model stamps — fails a check script or a test rather than passing on assertion.

## Non-Goals

- **No development work.** The layer stops at a signed layout handoff. The P6 handoff pack
  is what a builder consumes; building from it is somebody else's job.
- **No PRD.** The P2 project brief is the client agreement, not a spec. `/harness-layer:harness-plan`
  already converts intent into `spec.md` and stays the only such converter.
- **Card 10 — lesson graduation.** Promoting a repeated lesson into a skill, and the
  threshold for doing so, is a follow-on plan. P7 routes lessons; it does not graduate them.
- **Card 11 — the design KB.** No WCAG 2.2, ARIA APG, or platform accessibility mirrors this
  run; blocked on the P5 prototype-tool decision.
- **Card 12 — the first real run.** Running eight phases on a live brief is a usage run, not
  a diff, and cannot be an acceptance criterion of a prompt-file PR.
- **No question-bank write-back within a run.** A loaded skill is static for that session;
  the improvement loop is card 10's.
- **No client data committed.** `clients/` is gitignored; this plan adds the directory
  contract and the `.gitignore` entry, never a real client's files.

## Problem Statement

Soriza sells design but runs it from memory. What each phase produces, who does it, what
"signed off" means, and how many revision rounds the client actually bought are all
unwritten, so scope creep, unsigned approvals, and missing interaction states are caught by
someone noticing rather than by a check failing.

The harness layer already proved the shape that fixes this in this repo — phase commands
with a gate each, path-scoped rules, agent files whose model stamps CI pins, and Stop hooks
that refuse to let a stage close half-finished. None of it is reachable from client design
work today: `check_spec_completeness.py` walks `specs/` only, `artifacts.md` locks every page
to our internal Warm Neutral palette, and no rule or agent describes a design role.

Doing it now, before the first real engagement, is what makes card 12 a test of the layer
rather than an improvised project that later has to be reverse-engineered into one.

## Solution Approach

Fork the harness layer's proven shapes into a sibling namespace rather than generalizing
either one.

- **Namespace, not owner.** `studio-layer` names a function the way `harness-layer` does.
  The Soriza brand lives in one rule (`studio-identity.md`) that client-facing documents
  inherit, so rebranding costs one file while a namespace rename would touch every command
  path, `paths:` rule, agent name, and test.
- **Eight commands, not one parameterized command.** A Stop hook that must run inside one
  command registers in that command's own frontmatter. One parameterized command could only
  register the sign-off gate for every phase at once — firing it on soft gates too, which is
  exactly what the gate exists to prevent.
- **Roles as agent files.** Nine files under `.claude/agents/studio-layer/` make the roster's
  model and effort stamps load-bearing: a new drift test re-derives each stamp from
  `roster.md` and compares it to the agent file. Inline spawn prompts would leave every stamp
  a suggestion CI cannot check.
- **Mechanisms, split by what each is good at.** Scripts compute (WCAG ratios, matrix cells,
  question coverage, revision rounds); the design-QA agent judges (focus order, whether a
  state makes sense, whether error copy says anything). Neither is trusted for the other's job.
- **P1 runs page-first.** Each discovery round publishes an interactive artifact the client
  reacts to, forked from `harness-interview.md`'s round mechanics with client dimensions. The
  principal conducts every round because `AskUserQuestion` is unavailable to subagents — a
  spawned role cannot ask the client anything; the discovery lead prepares the question set
  and analyzes the answers.

The main alternative — a sibling repo for client work — loses because path-scoped rules and
command-frontmatter hooks resolve against `CLAUDE_PROJECT_DIR`. Client files outside that
root mean no studio rule loads and no hook sees a sign-off file, which would delete every
mechanism this plan exists to build.

## Requirements & Decisions

Ordered most-volatile first. The full record is in [decisions.md](./decisions.md).

1. **The four check scripts — and the command-eval runner — live in
   `.claude/scripts/studio-layer/`, not `.claude/hooks/`.**
   `test_wiring.py::test_every_entrypoint_is_claimed_by_a_registration_surface` treats any
   PEP 723 or shebang file under `.claude/hooks/` as a hook entrypoint that must be claimed by
   a registration surface. A check script invoked by a command body is not a hook and has no
   registration, so placing it there turns the wiring suite red.
   *Alternative still live:* a `scripts/` subdirectory inside the question-bank skill, on the
   `meta-agent/scripts/validate_agent.py` precedent — rejected because three of the four
   scripts serve commands, not that skill.

2. **`check_gate_signoff.py` takes the phase as `argv[1]`; the `run_hook` fixture grows an
   `args` parameter to match.** No hook in this repo has taken an argument before, so
   `run_hook` runs `uv run --script <path>` with no extra argv and cannot exercise the new
   hook as registered. The fixture gains `args: tuple = ()` appended to the command.
   *Alternative still live:* inferring the phase from the client folder's newest sign-off
   file, mirroring `check_spec_completeness.py`'s mtime inference — rejected because a client
   project holds all eight phase folders at once, so mtime would gate the wrong phase.

3. **Every role runs as a subagent. No agent teams anywhere, including the cold-designer
   test.** A subagent already gets its own context window and does not inherit the lead's
   conversation history, which is the entire property the cold-designer check needs — so a
   teammate buys no isolation while costing the experimental agent-teams dependency. It also
   costs correctness: a teammate does not take its effort from the agent file, so the roster's
   effort stamps would silently stop applying to exactly the roles the drift test pins.
   One spawn shape, one policy, stamps that hold.
   *Alternative still live:* teammates for P4's competing directions, if a phase ever needs
   roles talking to each other. It would require re-deriving how effort is set per teammate
   before any stamped role could run that way.

   Roles are also **one level deep**: subagents inherit the `Agent` tool by default, so each
   role file sets `disallowedTools: Agent`. Without it, "the principal spawns each role
   directly, one level deep" is a sentence rather than a property.

4. **Agent names are plain and layer-prefixed (`studio-art-director`); the person opens the
   body.** Claude routes off `name` + `description`, and `name` must be unique tree-wide. A
   hybrid name (`art-director-elena-ferraro`) would put the persona back into the routing
   document the unknowns pass deliberately kept it out of.

5. **The question bank is a skill the roles invoke via the `Skill` tool, without
   `disable-model-invocation`.** `skills:` preloading silently no-ops for teammates, and a
   skill marked `disable-model-invocation: true` cannot be invoked by the very roles meant to
   invoke it. Runtime invocation works for both spawn shapes.

6. **All build tasks stay on Claude models.** `/harness-layer:harness-build` has no Codex
   implementation path — Codex enters this pipeline at review. The check scripts are
   parser-and-arithmetic work that would otherwise be stamped `gpt-5.6-sol`; they run on
   `opus` at `high` instead, and the Codex review gate still judges the result.

## Interfaces & Contracts

### Project targeting — how the hook knows which project it is gating

The Stop payload carries no command arguments, so `argv[1]` gives the hook its phase but not
its project, and a studio may hold several projects at once. The hook resolves the project in
this order, and the order is the contract:

1. The Stop payload's `cwd`, when it resolves inside `clients/<client>/<project>/` — that
   project, at any depth below it.
2. Otherwise, when exactly one project directory exists under `clients/`, that one.
3. Otherwise — zero projects, or two or more with no `cwd` inside any of them — exit 0 and
   print the ambiguity to stderr. A gate that cannot identify its target must not guess, and
   per the repo hook contract an unresolvable configuration fails open.

A project directory is **any** directory exactly two levels below `clients/` whose name does
not begin with `.` — that is, every `clients/<client>/<project>/`. Identification must not
depend on `sign-off/` existing: a project that has never been signed is precisely the case
the gate must block, and defining it away would make a brand-new project look like zero
projects and fail open on its very first hard gate. The absence of `sign-off/<phase>.md` is a
blocking condition, never a reason to skip the project.

### Sign-off document — `clients/<client>/<project>/sign-off/<phase>.md`

```markdown
# Sign-off: P2 — Definition

- **Approver:** Jordan Reyes, Head of Marketing, Acme Co.
- **Date:** 2026-07-31

## Approved artifacts

| Artifact | SHA-256 |
| --- | --- |
| `definition/project-brief.md` | `3f9a1c4e8b27d05a6f1e93b4c7208d5e1a6b3f2c9d04e7a815c62b9f0d3e4a7b` |
| `definition/sitemap.md` | `9b21e7f0c4d83a15e6720b9fd3c81a4e7205d6b93f0a1c8e45d27b6a09f34c8a` |
```

`Approver` and `Date` must each be present and non-empty. The artifact table must carry at
least one row; every path is project-relative and must exist; every SHA is the 64-hex
`sha256sum` of that file's current content. One row per artifact — a single hash cannot
attest to two documents. The hash is of file content, never a git SHA: `clients/` is
gitignored, so no commit object exists.

### Phase documents — the machine-readable schemas

Each format below is what the phase command writes and the check script parses. A phase
command that invents its own shape fails its check.

**Handoff states matrix** — `clients/<c>/<p>/handoff/states-matrix.md`. One table per
breakpoint, `### <breakpoint>` above each. Rows are components, columns are exactly
`hover | focus | disabled | loading | empty | error`. A cell is filled when it holds
non-whitespace text other than `-` or `TBD`.

```markdown
### mobile

| Component | hover | focus | disabled | loading | empty | error |
| --- | --- | --- | --- | --- | --- | --- |
| PrimaryButton | darkens 8% | 2px ring | 40% opacity, no pointer | spinner replaces label | n/a — always has a label | inline message below |
```

**Handoff token table** — `clients/<c>/<p>/handoff/tokens.md`. Two tables. The colour-pair
table declares what is checked; `Kind` selects the threshold.

```markdown
| Foreground | Background | Kind | Used for |
| --- | --- | --- | --- |
| `#2C2825` | `#FAF8F5` | normal-text | body copy |
| `#8A837A` | `#FAF8F5` | large-text | section labels |

| Target | Width (px) | Height (px) |
| --- | --- | --- |
| PrimaryButton | 44 | 44 |
```

**Discovery notes** — `clients/<c>/<p>/discovery/notes.md`. One `## <dimension>` heading per
question-bank dimension, matching the skill's dimension headings exactly. A dimension is
answered when its section holds non-whitespace prose; the literal opener `N/A, because` also
counts as answered.

**Cold-designer triage** — `clients/<c>/<p>/definition/cold-designer-triage.md`. One row per
diff row; `Disposition` must be `brief unclear — amended` or begin `acceptable variance —`.

```markdown
| Section | Cold designer produced | Signed sitemap says | Disposition |
| --- | --- | --- | --- |
| Pricing | three tiers | two tiers plus contact | acceptable variance — tiering is a P4 call |
```

**Revision allowance** — declared once in the signed project brief as a line matching
`- **Revision rounds:** <integer> (plus polish)`. Its absence is a missing baseline, not a
zero allowance.

**Revision log** — `clients/<c>/<p>/prototype/revision-log.md`. One row per round; a round
whose number exceeds the allowance must name a change-order file that exists.

```markdown
| Round | Date | Requested | Change order |
| --- | --- | --- | --- |
| 3 | 2026-08-14 | swap hero video for a still | `change-orders/1.md` |
```

**Change order** — `clients/<c>/<p>/change-orders/<n>.md`. Four required fields; the revision
counter parses them, so an unsigned or costless change order does not buy a round.

```markdown
# Change order 1

- **Requested:** swap the hero video for a still image
- **Cost — rounds:** 1
- **Cost — time:** 3 business days
- **Approved by:** Jordan Reyes · 2026-08-14
```

`Requested`, `Cost — rounds` (an integer), `Cost — time`, and `Approved by` (a name and a
date) must each be present and non-empty. Referenced by the revision log; the signed brief is
amended by reference and never re-signed, so the P2 sign-off hashes stay valid.

**Component inventory** — `clients/<c>/<p>/structure/inventory.md`. The authoritative list of
what the handoff must cover. Without it the states matrix and contrast checks would quantify
only over whatever happens to be declared, so a one-component matrix would pass while the rest
of the design went unspecced.

It is a **P3 artifact, signed by the client**, not a P6 convenience file — that is what stops
the regress. An inventory written at P6 alongside the matrix could omit nine of ten components
and both would agree with each other; an inventory that is one of P3's deliverables is
enumerated from the signed wireframes and content model, and its SHA-256 goes in the P3
sign-off table like any other approved artifact. So the `p3` gate refuses to close until the
inventory exists and is signed.

Signing it at P3 is necessary but not sufficient: the P6 checks read the file as it stands at
P6, so a signature three phases back proves nothing about the file they actually quantify over.
Deleting nine rows between P3 and P6 would leave a one-component matrix passing against a
one-component list, with the P3 signature still sitting untouched in a sign-off file nobody
re-reads. So **the `p6` gate re-reads the P3 sign-off, recomputes the inventory's SHA-256, and
blocks on any mismatch** — that is the step that makes the denominator the signed one rather
than merely descended from it. Changing the inventory after P3 therefore requires a change
order and a re-signature, which is visible, instead of quietly shrinking what the design is
measured against.

```markdown
| Component | Breakpoints | Colour tokens used |
| --- | --- | --- |
| PrimaryButton | mobile, desktop | `--accent`, `--on-accent` |
| SearchResults | mobile, desktop | `--text`, `--bg` |
```

The inventory must be non-empty. `check_states_matrix.py` requires a matrix row for every
component × breakpoint pair listed here; `check_contrast.py` requires every colour token
named here to appear in at least one checked foreground/background pair. Both resolve the
inventory at `structure/inventory.md` and both exit 2 when it is missing or empty — a missing
baseline is never a pass. Adding a component to the design without adding it here is the one
way to defeat these checks, and after P3 that means amending a client-signed document.

**Design QA report** — `clients/<c>/<p>/handoff/qa-report.md`. One row per finding;
`Severity` is `blocking` or `advisory`, `Status` is `open` or `resolved`. The p6 gate refuses
to close while any `blocking` finding is `open`.

```markdown
| Finding | Severity | Status | Evidence |
| --- | --- | --- | --- |
| Empty state for SearchResults has no copy | blocking | resolved | states-matrix.md row 4 |
```

### P5 prototype tool — a runtime input, not a build-time decision

The P5 command takes the tool as an argument and records it in the prompt pack. Selection
rules, applied in order: a tool the client already pays for wins; otherwise the one that can
export or be re-driven from the prompt pack, so the engagement is not locked to it;
otherwise Claude Design. The chosen tool is written to
`clients/<c>/<p>/prototype/prompt-pack.md` so P7 can route a lesson about it and card 11 can
mirror its docs.

### Hook registration — P2, P3, P4, P6 command frontmatter

```yaml
hooks:
  Stop:
    - hooks:
        - type: command
          command: uv run --script "$CLAUDE_PROJECT_DIR"/.claude/hooks/check_gate_signoff.py p2
```

The phase token is the only difference between the four registrations. `HOOK_PATH_RE` in
`test_wiring.py` stops at whitespace, so the argument does not disturb the existing wiring
assertions.

### Check script CLI — all four

```bash
uv run --script .claude/scripts/studio-layer/check_states_matrix.py <handoff.md>
uv run --script .claude/scripts/studio-layer/check_contrast.py <handoff.md>
uv run --script .claude/scripts/studio-layer/check_question_coverage.py <discovery-notes.md>
uv run --script .claude/scripts/studio-layer/check_revision_count.py <project-dir>
```

Exit 0 = pass. Exit 1 = a countable failure, with `file:line` diagnostics on stdout naming
each failing cell, pair, dimension, or round. Exit 2 = the check could not run its
arithmetic: a missing or unreadable argument, an unparseable table, a malformed hex value, or
a missing revision allowance. The distinction is what makes exit 1 trustworthy — a typo must
never be reported as a contrast failure a designer would chase.

The scripts are plain CLIs, not hooks: given a target that does not exist they exit 2. Only
the Stop hook has the fail-open-when-there-is-no-client behavior, because only the hook runs
unbidden in sessions that have nothing to do with a client.

### Command-eval runner — `run_command_evals.py`

```bash
uv run --script .claude/scripts/studio-layer/run_command_evals.py \
  .claude/commands/studio-layer -k 3 --yes
```

Modeled on `.claude/skills/meta-skills/scripts/run_behavior_eval.py`, which owns the proven
shape — scratch project, `claude -p` per run, judge-graded assertions, pass rate over `k`
runs. It differs in exactly one respect, and that is why it has to exist: `run_behavior_eval`
stages its target into `<scratch>/.claude/skills/<name>` and `eval.py` refuses a directory
with no `SKILL.md`, so a command is unreachable through it — a command is only invocable as
`/studio-layer:<name>` from `.claude/commands/`.

Per case it stages the whole studio namespace into a throwaway project outside this repo —
`.claude/{commands,agents,skills,rules,scripts}/studio-layer/` **plus
`.claude/hooks/check_gate_signoff.py`** — so the command resolves, the roles it spawns exist,
the check scripts it calls are on disk, and the four hard-gate commands find the hook their
frontmatter registers, while the repo's own rules never contaminate the run. The hook is not
part of the studio namespace but is load-bearing for the evaluated commands: P2's registration
points at `"$CLAUDE_PROJECT_DIR"/.claude/hooks/check_gate_signoff.py`, so omitting it would
evaluate P2 with its gate silently absent — measuring the command without the mechanism the
eval exists to exercise. It then invokes the case's `prompt` as a slash command, collects
the files written to the scratch cwd, and grades each assertion: an assertion carrying a
`check` is graded by running it against the outputs (exit 0 = pass), and the rest go to the
judge. Exit 0 when every case clears its recorded pass rate, 1 when one does not, 2 on a
usage or parse failure. `--lint` grades nothing and only validates the suite schema, so it is
free and safe in any environment.

Evals are manual and stay out of CI: each run spends real tokens, so nothing here is wired
into `uv run pytest`.

### Roster row — `.claude/rules/studio-layer/roster.md`

```markdown
| Function | Person | Model | Effort | May escalate |
| --- | --- | --- | --- | --- |
| `studio-art-director` | Elena Ferraro | `opus` | `high` | yes |
```

The drift test parses this table and asserts `.claude/agents/studio-layer/<function>.md`
declares the same `model:` and `effort:` in its frontmatter.

### `run_hook` fixture extension — `tests/harness-layer/hooks/conftest.py`

```python
def _run(script, payload, *, args: tuple = (), env_overrides=None, unset_env=(), cwd=REPO_ROOT):
    return subprocess.run([UV, "run", "--script", str(HOOKS_ROOT / script), *args], ...)
```

Existing call sites pass no `args` and are unaffected.

## Relevant Files

- `.gitignore` — gains the `clients/` entry that keeps client work out of history.
- `AGENTS.md` — gains a `## Studio Layer` pointer to the three new rules, per `memory-series.md`.
- `.claude/rules/harness-layer/hooks.md` — the authoritative hook catalog gains the
  `check_gate_signoff.py` row; `test_wiring.py` cross-checks this table against the code.
- `tests/harness-layer/hooks/conftest.py` — `run_hook` gains `args` so the new hook can be
  launched as registered.
- `tests/harness-layer/hooks/test_wiring.py` — `CODEX_DISPOSITIONS` gains the new hook as
  `not-applicable`; `test_dispositions_cover_every_entrypoint` fails without it.
- `.claude/commands/harness-layer/harness-interview.md` — read-only reference; its Round Loop
  (lines 36–42) and Coverage Ledger (line 32) are the fork source for P1.
- `.claude/rules/harness-layer/artifacts.md` — read-only reference; `client-artifacts.md`
  inherits its craft and publish sections.

### New Files

- `.claude/rules/studio-layer/roster.md` — ten rows (principal + nine roles), each with
  function, person, model, effort, escalation.
- `.claude/rules/studio-layer/client-artifacts.md` — `paths: clients/**`; inherits craft and
  publish from `artifacts.md`, drops the palette lock, carries the four-row page-pattern table.
- `.claude/rules/studio-layer/studio-identity.md` — `paths: clients/**`; Soriza name, voice,
  letterhead, and the sign-off block every client-facing document inherits.
- `.claude/agents/studio-layer/studio-client-partner.md` — Daniel Osei, `sonnet`/`medium`.
- `.claude/agents/studio-layer/studio-discovery-lead.md` — Priya Raghavan, `opus`/`high`.
- `.claude/agents/studio-layer/studio-ux-architect.md` — Tomas Vieira, `opus`/`high`.
- `.claude/agents/studio-layer/studio-art-director.md` — Elena Ferraro, `opus`/`high`.
- `.claude/agents/studio-layer/studio-content-strategist.md` — Hana Okabe, `opus`/`high`.
- `.claude/agents/studio-layer/studio-prototype-engineer.md` — Marcus Bramley, `sonnet`/`high`.
- `.claude/agents/studio-layer/studio-design-qa.md` — Yusuf Demir, `opus`/`high`.
- `.claude/agents/studio-layer/studio-research-analyst.md` — Clara Nyberg, `sonnet`/`medium`.
- `.claude/agents/studio-layer/studio-retro-scribe.md` — Ravi Chandran, `sonnet`/`medium`.
- `.claude/commands/studio-layer/` — eight phase commands, named exactly `p0-intake.md`,
  `p1-discovery.md`, `p2-definition.md`, `p3-structure.md`, `p4-art-direction.md`,
  `p5-prototype.md`, `p6-handoff.md`, `p7-retro.md`.
- `.claude/skills/studio-layer/studio-client-questions/SKILL.md` — the invocable question
  bank. The **directory name** becomes the command, so it matches the skill's `name:` exactly.
- `.claude/skills/studio-layer/studio-client-questions/evals/evals.json` — the skill's eval
  suite, in the schema the meta-skills runner executes.
- `.claude/commands/studio-layer/evals/evals.json` — the commands' eval suite, same schema.
- `.claude/scripts/studio-layer/run_command_evals.py` — the runner that executes it. The
  meta-skills runner cannot: it stages its target into `.claude/skills/<name>` and requires a
  `SKILL.md`, so a command directory is unreachable by it.
- `.claude/hooks/check_gate_signoff.py` — the phase-argument Stop gate.
- `.claude/scripts/studio-layer/check_states_matrix.py` — every component × state cell filled.
- `.claude/scripts/studio-layer/check_contrast.py` — computed WCAG ratios and tap targets.
- `.claude/scripts/studio-layer/check_question_coverage.py` — coverage re-derived from the skill.
- `.claude/scripts/studio-layer/check_revision_count.py` — rounds re-derived from the signed brief.
- `tests/harness-layer/test_studio_roster_drift.py` — roster ↔ agent-file stamp drift.
- `tests/harness-layer/hooks/gate-signoff/test_check_gate_signoff.py` — hook contract tests.
- `tests/harness-layer/studio-layer/test_studio_checks.py` — contract tests for the four scripts.
- `clients/.gitkeep` — the directory contract; the folder itself is ignored.

## Edge Cases

- **Sign-off file missing entirely** — hook exits 2 naming the expected path, so the phase
  cannot close. This is the common case on a first run and must read as an instruction, not
  a crash.
- **Sign-off file present but a field is blank or still a template placeholder** — treated
  identically to missing: exit 2 naming the specific empty field.
- **Sign-off SHA does not match the artifact it claims to approve** — the hook reports the
  mismatch and blocks; a client approved something, and it was not this file.
- **An artifact row names a file that does not exist** — blocks, naming the row. An approval
  of a deleted or renamed document is not an approval.
- **A phase folder for a different phase is newer** — irrelevant by construction: the phase
  comes from `argv[1]`, never from mtime. A client project holds all eight phase folders at
  once, which is exactly why inference was rejected.
- **Two client projects exist and `cwd` is inside neither** — the hook exits 0 and says it
  could not identify a target. Guessing would gate the wrong engagement.
- **The registration passes an unknown or missing phase token** — exit 0. A bad registration
  is a configuration failure, and the repo's hook contract fails those open; `test_wiring.py`
  is what catches them, at CI time rather than mid-engagement.
- **Stop re-entry (`stop_hook_active: true`)** — the hook blocks on the first stop and, on
  re-entry, allows the stop while printing the unresolved gate to stderr. A client signature
  is not something Claude can produce by trying again, and Claude Code force-ends the turn
  after eight consecutive blocks, so re-blocking would burn the turn and land in the same
  place. The phase stays unsigned and visibly so.
- **No `clients/` directory at all** — the hook exits 0 and stays silent, mirroring how
  `check_spec_completeness.py` is invisible in a project with no `specs/`. The four check
  scripts are ordinary CLIs and exit 2 on a target that does not exist.
- **Handoff token table declares a colour pair with a malformed hex value** — the contrast
  script exits 2 (usage/parse) rather than 1, so a typo is never reported as a contrast
  failure the designer would chase.
- **A component row exists with no state columns at all** — counted as unfilled, not skipped;
  an empty row is the failure mode the matrix check exists to catch.
- **P3 closes with no inventory, or with one absent from its sign-off table** — the p3 gate
  blocks. Letting P3 close would leave P6 to author the list it is then measured against, which
  is the vacuous pass the inventory exists to prevent.
- **The inventory is edited between P3 and P6 — rows added or deleted** — the `p6` gate
  recomputes its SHA-256 against the hash recorded in the P3 sign-off and blocks on the
  mismatch. This is the case a P3-only check would miss entirely: deleting nine rows before P6
  would otherwise let a one-component matrix pass against a one-component list while the P3
  signature sat untouched. Changing it legitimately means a change order and a re-signature.
- **The inventory is complete but the design drifts below it** — the matrix and contrast checks
  fail naming each missing pair. Over-declaring in the inventory costs work rather than hiding
  it, which is the direction the incentive should point.
- **Revision round past the allowance with a change order present** — passes. Without one —
  fails, naming the round and the expected change-order path.
- **The signed brief declares no revision allowance** — the counter exits 2: the baseline is
  missing, which is a different defect from exceeding it.
- **Re-running any check or the hook on unchanged inputs** — same exit code, no writes. All
  five are read-only and idempotent.
- **A role's agent file is deleted but its roster row remains** — the drift test fails naming
  the missing file, rather than silently checking nothing.
- **P1 round that resolves nothing new** — the forked bounded-round condition ends discovery:
  record what is left as assumptions and go to the soft gate.

## Risk & Rollback

- **Blast radius:** six changes reach outside the new namespace; everything else is additive.
  - `tests/harness-layer/hooks/conftest.py` — `run_hook` gains `args`. This fixture launches
    every hook test, so a mistake reddens the whole hook suite; that is also what notices
    immediately. Existing callers pass nothing and are unaffected.
  - `tests/harness-layer/hooks/test_wiring.py` — a `CODEX_DISPOSITIONS` entry. Omitting it
    fails `test_dispositions_cover_every_entrypoint`.
  - `.claude/rules/harness-layer/hooks.md` — one catalog row, cross-checked against the
    dispositions in both directions.
  - `.gitignore` — the `clients/*` pair. A wrong pattern silently untracks `.gitkeep`; AC1
    catches it.
  - `AGENTS.md` — a pointer section. It is always-loaded, so it must stay short; AC5 asserts
    the pointer exists and the file stays under the ~250-line budget.
  - `clients/` — a new top-level directory. Ignored, so it cannot affect any other tooling.

  No studio rule loads during ordinary harness work: all three are scoped `paths: clients/**`.
- **Rollback:** revert the squash commit. The three rules are path-scoped and the eight
  commands are namespaced, so nothing else reads them; no migration, no data to unwind.
- **In-flight work:** none. No client project exists yet — card 12 is a follow-on plan — so
  there is no engagement mid-flight to strand and no `clients/` content to migrate.

## Guardrails

- **Fork the interview mechanics; do not import them.** P1 gets its own round loop with client
  dimensions. Do not edit `harness-interview.md`, and do not factor the two into a shared file
  — the ledgers share no rows, so the fork cannot drift in a way that matters.
- **Do not put a check script under `.claude/hooks/`.** It becomes an unclaimed entrypoint and
  reddens the wiring suite.
- **Do not hard-code the roster in the drift test.** Re-derive every stamp from `roster.md`; a
  second hard-coded copy drifts in step with the first and pins nothing.
- **Do not copy `artifacts.md`'s palette table into `client-artifacts.md`.** Naming the
  palette's *source* per phase is the whole point of forking it.
- **Do not give the question-bank skill `disable-model-invocation: true`.** It would put the
  bank out of reach of the roles meant to invoke it.
- **Do not add `skills:` frontmatter to the role agents.** Preloading is not access — a
  subagent invokes the bank through the `Skill` tool either way, and the frontmatter would be
  dead weight that also no-ops in any future teammate shape.
- **Do not spawn agent-team teammates.** Every role is a subagent, and each denies the `Agent`
  tool so the tree stays one level deep.
- **The cold-designer diff is advisory.** Gate the triage document, not a zero-diff. Two
  competent designers given one brief produce different section plans; a zero-diff gate would
  never open.
- **Do not create a real client folder.** `clients/.gitkeep` and the ignore entry only.

## Notes

No new dependencies. The check scripts and the hook are PEP 723 `# /// script` files with
empty `dependencies = []`, run through `uv run --script` like every existing hook.

The plan folder keeps the chain slug `cpo-layer` (the branch is `feat/80-cpo-layer`) because
discovery is already committed under it and the user's prompt names that path twice. The
`studio-layer` naming decision governs the harness namespace — commands, rules, agents — not
the plan folder.

## Codex Verification

- **Outcome:** **approved at the human gate** — the user chose proceed-to-build with the
  round-4 fixes unverified, knowing the build carries its own Codex review round. Four rounds
  run against `gpt-5.6-sol`, two per run — rounds 1–2 (`xhigh`, then
  `high`) in the drafting run, rounds 3–4 (`medium`) in this revision run. 52 findings total:
  32 blocking, all fixed; 20 advisory, recorded. No finding was disputed, and no round reopened
  an earlier disposition. The full record is in
  [reviews/findings-ledger.md](./reviews/findings-ledger.md).
- **The one thing the gate did not confirm:** this run's 2-round allowance was spent on rounds
  3 and 4, so the round-4 fixes — the p6 re-verification of the inventory hash (R4-F1) and
  staging the sign-off hook in the command-eval runner (R4-F2) — were not re-reviewed by a
  fifth round. Both are spec text and task instructions rather than code, and each is pinned by
  named tests the build must add (`test_p6_inventory_mutated_after_p3_signoff_blocks`, and the
  runner's staging-layout test).
- **Rejected findings:** none. R1-F35 (path scope alone does not prove rules load on a client
  project's first file) fell below the blocking confidence bar and stands as advisory; the phase
  commands read the identity rule explicitly, which covers the practical case.
- **Standards amended (self-improve):** `spec-standards.md` #6 in the drafting run, to accept
  checked-in `meta-skills/references/` sources where the KB has no mirror; `spec-standards.md`
  #2 in this run, to require verifying at draft time that a runner a criterion leans on can
  actually reach its target. R2-F4, R3-F1 and R4-F2 shared that single root cause.
- **Verified by running, not asserted:** the AC16 lint invocation (proved broken as originally
  written, then proved working in its corrected form), `eval.py`'s `SKILL.md` requirement,
  `run_behavior_eval.py`'s staging path, `HOOK_PATH_RE`'s whitespace boundary, `run_hook`'s
  argv-free launch, all seven plan-local checks failing with precise diagnostics on today's
  tree, and the full suite green at 875 passed / 2 skipped.
