# Summary: cpo-layer — studio-layer, design delivery through signed handoff

> What this plan actually shipped, for the next agent or developer who needs to know
> without reading [spec.md](./spec.md). Written by `/harness-layer:harness-review` at
> its terminal step, from the implementation notes and the findings ledger. Outcome,
> not intent — if the build diverged from the plan, this file records what was built.

**Issue** #80 · **PR** #81 · **Status** approved (override) — ready to merge

## What Shipped

The `studio-layer` namespace: eight phase commands (`/studio-layer:p0-intake` …
`p7-retro`) run by the main session as principal, which spawns nine role agents one level
deep, plus a client question-bank skill, four check scripts, a sign-off Stop hook, and a
command-eval runner. Client work lives in a gitignored `clients/<client>/<project>/`, so
path-scoped rules resolve there while nothing client-owned enters git history.

The point of the layer is that design claims stop being assertions. Four hard gates
(P2, P3, P4, P6) refuse to close until the client has signed the phase's *named*
deliverables, each verified by SHA-256 against the file it approves, and every countable
claim — state coverage, contrast ratios, question coverage, revision rounds, role model
stamps — fails a check script or a test rather than passing on someone's say-so.

**AC16's rate is established.** `eval-0` 1.0 and `eval-1` 1.0, each needing 1.0, over 6
`claude -p` runs with the runner exiting 0 — measured against a scratch project that is a real
git repository, so it exercises the path anchor every command carries. Everything else is
green.

## Acceptance Criteria → Evidence

| AC | What it proves | Command | Result |
| --- | --- | --- | --- |
| AC1 | `clients/` is a tracked contract whose contents are ignored, invisible to the spec gate | `specs/cpo-layer/checks/ac1-client-data-home.sh` | exit 0 |
| AC2 | Roster and agent stamps are load-bearing — changing either side alone fails | `tests/harness-layer/test_studio_roster_drift.py` (6 node ids) | 6 passed |
| AC3 | Nine role agents, function-named, person in the body, none able to spawn a subagent | `specs/cpo-layer/checks/ac3-role-agents.sh` | exit 0 |
| AC4 | The client-artifact rule forks `artifacts.md` rather than copying it | `specs/cpo-layer/checks/ac4-client-artifacts.sh` | exit 0 |
| AC5 | Every studio rule is path-scoped, so none loads during ordinary harness work | `specs/cpo-layer/checks/ac5-rules-path-scoped.sh` | exit 0 |
| AC6 | The question bank is invocable and its coverage is re-derived, not re-copied | `test_studio_checks.py` (3 node ids) + `ac6-question-bank-skill.sh` | 3 passed · exit 0 |
| AC7 | Eight commands; exactly p2/p3/p4/p6 register the gate, each with its own phase | `specs/cpo-layer/checks/ac7-phase-commands.sh` | exit 0 |
| AC8 | The gate blocks and allows for the right reasons, including path containment and each phase's required artifacts | `test_check_gate_signoff.py` (26 node ids) | 26 passed |
| AC9 | The triage gates p2; the QA report and the re-hashed inventory gate p6 | `test_check_gate_signoff.py` (12 node ids) | 12 passed |
| AC10 | The hook is registered, cataloged and dispositioned | `test_wiring.py` (5 node ids) | 5 passed |
| AC11 | The states matrix counts cells against the signed inventory and cannot pass empty | `test_studio_checks.py` (9 node ids) | 9 passed |
| AC12 | Contrast and tap targets are computed, with one ratio hand-pinned | `test_studio_checks.py` (7 node ids) | 7 passed |
| AC13 | The revision count is arithmetic over a signed brief, counted rounds and per-order capacity | `test_studio_checks.py` (17 node ids) | 17 passed |
| AC14 | The whole suite stays green | `uv run pytest` · `ruff check` · `ruff format --check` | 1040 passed, 2 skipped · clean · 71 formatted |
| AC15 | Design QA blocks handoff as a mechanism, and no role spawns subagents | `test_check_gate_signoff.py` (3 node ids) + `ac3-role-agents.sh` | 3 passed · exit 0 |
| AC16 | Both non-deterministic surfaces carry evals a runner actually executes | `run_command_evals.py --lint` · `ac16-evals-are-runnable.sh` · runner contract tests | exit 0 · exit 0 · 11 passed |
| AC16 | …and those evals clear their bar | `manual:` commands eval, 3 repeats | **`eval-0` 1.0 · `eval-1` 1.0 · runner exit 0** |

The two skips are pre-existing empty parametrizations in `test_model_drift.py`, in a file
this branch does not touch.

## Decisions Locked

- **The principal is the orchestrator, never a spawned agent.** Only the main session
  talks to the client; a subagent cannot prompt the user.
- **One spawn shape: ordinary subagents, one level deep.** No role can spawn another:
  eight seats set `disallowedTools: Agent`, and `studio-research-analyst` — the one seat that
  reads third-party sites — carries a `tools:` allowlist that omits both `Agent` and `Bash`.
  The agent-teams dependency was dropped — a plain subagent already starts without the lead's
  conversation history.
- **Client data never enters git.** `clients/*` is ignored with `!clients/.gitkeep`
  re-including the contract file; studio rules are scoped `clients/**/*`.
- **A signature covers named deliverables, not "some file".** Each gated phase declares
  the rows its sign-off must list; each is hash-verified. The set is a floor, not a ceiling.
- **The component inventory is a P3 deliverable the client signs**, and P6 re-hashes it
  against the P3 signature — so P6 cannot shrink its own denominator.
- **Counted, not asserted.** Round numbers must be positive, unique and contiguous; a
  change order buys exactly the rounds it declares; the allowance is refused unless the
  brief still hashes to what P2 signed.
- **P5's prototype tool is a runtime input**, chosen per engagement against the selection
  rules — not a build-time decision.

## Interfaces

- `.claude/hooks/check_gate_signoff.py <phase>` — Stop hook, phase from `argv[1]`,
  registered in p2/p3/p4/p6 frontmatter as
  `uv run --script "$CLAUDE_PROJECT_DIR"/.claude/hooks/check_gate_signoff.py <phase>`.
- `.claude/scripts/studio-layer/check_{states_matrix,contrast,question_coverage,revision_count}.py`
  — plain CLIs: exit 0 pass, 1 a countable failure with `file:line`, 2 could not run.
- `.claude/scripts/studio-layer/run_command_evals.py <command-dir>` — stages the studio
  namespace into a scratch **git repository** and runs each case as a slash command.
- `clients/<client>/<project>/` — the document schemas in spec.md `## Interfaces & Contracts`
  are the contract every check parses.
- Command bodies anchor paths on `$(git rev-parse --show-toplevel)`; only hook
  registrations use `"$CLAUDE_PROJECT_DIR"`.

## Follow-ups

- [x] ~~Re-establish AC16's rate~~ — done: `eval-0` 1.0, `eval-1` 1.0, runner exit 0.
- [x] ~~The runner reports `run errored (success)`~~ — done. A clean envelope carries
      `is_error: false` beside `subtype: "success"`, so `is_error` was already the right
      trigger and no passing run was ever zeroed; only the label was wrong, and it now comes
      from `api_error_status` then `result`.
- [x] ~~`studio-research-analyst` inherits every tool~~ — done: a `tools:` allowlist that
      omits `Agent` and `Bash`, on the one seat that reads third-party sites.
- [x] ~~`p7-retro.md`'s write waiver~~ — narrowed to the three `studio-layer` directories its
      routing step actually writes to, with client-supplied text barred from `.claude/`.
- [x] ~~16 of 29 security candidates never paneled~~ — the scan's candidate list was not
      preserved, so an independent pass over the same surface was run instead and found no
      new blocking issue (`S-F3`). Recorded as a fresh pass, not a resumption.
- [ ] **Issue #82** — `destructive-guard` denies a confirmation flag followed by a redirect,
      reading the flag as the stream generator of the same name. Hit three times this run.
- [ ] P6's gate does not itself run the states and contrast checks (`I1-F21`, advisory).
- [ ] AC5 accepts invalid scopes such as `clients/**bogus` via substring grep (`I1-F20`).
- [ ] Mirror the official custom-slash-command documentation via `/harness-layer:kb add`.

## Lessons Routed

- **A check is evidence only if its harness reproduces the runtime environment** →
  `.claude/rules/harness-layer/impl-standards.md`, new standard 3 ("Faithful harness").
  The eval staged a scratch project that was not a git repository while the commands had
  just been re-anchored on `git rev-parse --show-toplevel`, so a 1.0 measured the harness
  rather than the change.
- **Judge a command by its own exit status** → same file, standard 4. A pipe into `tail`
  reports the pipe's status and a trailing `echo` replaces it; this run hit the second
  form after the build had already hit the first.
- **`CLAUDE_PROJECT_DIR` is hook-scoped** → `.claude/rules/harness-layer/hooks.md`, beside
  the registration idiom that uses it. It resolves in a hook, an stdio MCP server and a
  plugin LSP server only; in a command body it is empty and an anchored path silently
  becomes `/<path>` at the filesystem root.
- **The `paths:` glob form is `<dir>/**/*`** → `.claude/rules/memory-series.md` (routed by
  the build, retained here for traceability).
