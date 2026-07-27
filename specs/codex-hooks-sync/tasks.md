# Tasks: codex-hooks-sync

> Execution plan for [spec.md](./spec.md). Owner and scope are defined there; this file is how & who.

## Implementation Phases

### Phase 1: Foundation

The shared path primitive everything else consumes. `edited_paths(payload)` lands in all three family
`_common.py` modules with its parametrized contract test, and `hook_host()` lands in the
destructive-guard `_common.py`. Nothing in Phase 2 can be written correctly before the parser's
contract is fixed, so this phase is a hard barrier: **T1 must be green before T2–T5 start.**

### Phase 2: Core Implementation

The five consumers, in parallel once T1 lands: the destructive guard's ask tier, the four formatters,
`post_write_scan.py`, `file_guard.py`'s new write surface, and the `.codex/` registration itself.
Each is independently testable and touches a disjoint set of files, so they parallelize cleanly.

### Phase 3: Integration & Polish

The drift-control machinery that makes the parity permanent — the portability matrix, the offline
test, the `hooks.md` catalog column — then the live probe that produces the actual acceptance
evidence, then full-suite validation.

## Team Orchestration

- You operate as the team lead and orchestrate the team to execute the plan.
- IMPORTANT: You NEVER operate directly on the codebase. You use the `Task*` tools to deploy team
  members to build, validate, test, and deploy. Your job is to direct, not to build.
- Keep the shared task list (TaskCreate/TaskUpdate) as the single source of truth for who is doing
  what; verify each task on the board before marking it complete.
- Note the session id / name of each team member — that is how you reference them.

## Team Members

- **Builder**
  - **Name:** `builder-paths`
  - **Role:** Owns the `edited_paths()` / `hook_host()` primitives and their parametrized contract
    test — the one piece every other task depends on.
  - **Agent Type:** `general-purpose`
  - **Resume:** true

- **Builder**
  - **Name:** `builder-guards`
  - **Role:** Owns the three security surfaces: the destructive guard's ask tier, `file_guard.py`'s
    `apply_patch` surface, and `post_write_scan.py`'s multi-path scanning.
  - **Agent Type:** `general-purpose`
  - **Resume:** true

- **Builder**
  - **Name:** `builder-wiring`
  - **Role:** Owns the mechanical surfaces: the four formatters' path loop, `.codex/hooks.json`, and
    `.codex/config.toml`.
  - **Agent Type:** `general-purpose`
  - **Resume:** true

- **Builder**
  - **Name:** `builder-parity`
  - **Role:** Owns the drift-control layer — the portability matrix in `test_wiring.py`, the offline
    test, and the `hooks.md` catalog column.
  - **Agent Type:** `general-purpose`
  - **Resume:** true

- **Builder**
  - **Name:** `prober`
  - **Role:** Owns `scripts/codex-hook-probe.sh` and the live evidence run that produces
    `implementation-notes.md`.
  - **Agent Type:** `general-purpose`
  - **Resume:** true

- **Validator**
  - **Name:** `validator`
  - **Role:** Runs every validation command, confirms each AC, and confirms no Claude-side behaviour
    changed.
  - **Agent Type:** `general-purpose`
  - **Resume:** false

## Step by Step Tasks

- Execute every step in order, top to bottom. Each task maps directly to one `TaskCreate` call.
- Before starting, run `TaskCreate` for every task below so all team members can see the board.
- Each task names the acceptance criteria (from acceptance-criteria.md) it satisfies, so work traces
  to "done".
- **Read first, always:** `.claude/rules/harness-layer/hooks.md` is the authoritative hook catalog and
  testing contract. Do not re-derive hook behaviour from memory.
- The observed `apply_patch` grammar is in decisions.md `## Plan-time Verification` → Finding 2. It is
  observed output from a live session, not a guess — build the parser from it, not from the docs.

### 1. Shared path primitive and host flag

- **Task ID:** `edited-paths`
- **Depends On:** none
- **Assigned To:** `builder-paths`
- **Agent Type:** `general-purpose`
- **Model / Effort:** `opus` / `high`
- **Parallel:** false — this is the Phase 1 barrier
- **Satisfies:** AC10
- Add `edited_paths(payload) -> list[str]` to `.claude/hooks/auto-format/_common.py`,
  `.claude/hooks/security-scan/_common.py`, and `.claude/hooks/sensitive-files/_common.py`. Three
  copies, deliberately — see decisions.md; the families cannot import each other and `sys.path` tricks
  are forbidden.
- Branch on payload **shape**, not a host flag: `tool_name == "apply_patch"` → parse
  `tool_input.command`; a non-empty string `tool_input.file_path` → `[file_path]`; anything else →
  `[]`.
- Parse all four directives — `*** Add File:`, `*** Update File:`, `*** Delete File:`, and
  `*** Move to:` (a rename yields **both** the old and the new path, in that order).
- Only lines at directive position start a file; content lines (`+`, `-`, ` `, `@@`) are never parsed
  as directives, even when their text contains a literal `*** Add File:`.
- Resolve relative envelope paths against the payload's `cwd` field, never the process cwd.
- Cap the scanned envelope the way `block_destructive.py` caps a command (64 KB, encoded bytes).
- Fail open on everything: no envelope, truncated envelope, empty path, missing `tool_input`, `None`
  payload → `[]`, never an exception.
- Add `hook_host() -> str` to `.claude/hooks/destructive-guard/_common.py`, returning
  `os.environ.get("HARNESS_HOOK_HOST", "claude").strip().lower()`.
- Write **one parametrized test** that drives the full AC10 corpus through all three modules via the
  `load_hook_module` fixture, so the copies provably cannot drift.
- Leave `read_file_path()` in place for now if any caller still uses it; remove it only once T3 has
  migrated the formatters (see Rule 3 — clean up only your own orphans).

### 2. Destructive guard: ask tier denies under Codex

- **Task ID:** `ask-tier-deny`
- **Depends On:** `edited-paths`
- **Assigned To:** `builder-guards`
- **Agent Type:** `general-purpose`
- **Model / Effort:** `sonnet` / `medium`
- **Parallel:** true
- **Satisfies:** AC6, AC7, AC8, AC9, AC14
- In `block_destructive.py`, when `_common.hook_host() == "codex"` and only ask-tier rules matched,
  print the same `BLOCKED (<Category>/<rule_id>)` / `Why:` / `Fix:` block the deny path prints and
  exit 2. Never mix exit 2 with stdout JSON.
- Under any other host value, the existing `permissionDecision: "ask"` JSON path is untouched.
- Give each of the nine ask-tier rules a Codex fix line that is host-neutral: it must not mention the
  `!` prefix and must not tell the reader to "approve" anything — under Codex the stderr is read by
  the model, which cannot approve. "Ask the user to run this themselves." is the house wording.
- Deny-tier rules behave identically on both hosts.
- Cover all nine rules on both host branches. The pre-existing destructive-guard tests must pass
  **unmodified** — if one needs editing, stop and flag it; that means Claude behaviour changed.

### 3. Formatters process every edited path

- **Task ID:** `formatters-multipath`
- **Depends On:** `edited-paths`
- **Assigned To:** `builder-wiring`
- **Agent Type:** `general-purpose`
- **Model / Effort:** `sonnet` / `low`
- **Parallel:** true
- **Satisfies:** AC11, AC14
- Change `auto-format/_common.py`'s `target()` to return a **list** of `(file, root)` pairs built from
  `edited_paths()`, keeping the existing per-file guards (extension match, vendored skip, deleted-file
  note) applied to each path.
- Update `js_ts.py`, `data.py`, `markdown.py`, and `python.py` to loop over the returned pairs. A
  formatter failure on one path must not skip the remaining paths; diagnostics from all paths
  aggregate into one capped stderr report and one exit code.
- For a rename, the new path is the one that exists — the loop naturally handles this because
  `edited_paths()` returns both and the deleted-file guard drops the old one.
- Remove `read_file_path()` once no caller remains.

### 4. Scanner and file guard cover the apply_patch surface

- **Task ID:** `scan-guard-multipath`
- **Depends On:** `edited-paths`
- **Assigned To:** `builder-guards`
- **Agent Type:** `general-purpose`
- **Model / Effort:** `opus` / `medium`
- **Parallel:** true
- **Satisfies:** AC12, AC13, AC14
- `post_write_scan.py`: track **and** scan every path from `edited_paths()`. Findings across all paths
  aggregate into one capped report; any `block` finding on any path exits 2.
- `file_guard.py`: add the `apply_patch` surface. Every path in the envelope is checked with
  `_common.match_path`, **including a `*** Move to:` target** — a rename onto a cataloged sensitive
  path must be denied even when the source is innocuous. This is the security-relevant case; give it
  its own test with a docstring saying why.
- The existing Read/Grep/Edit/Write/MultiEdit behaviour is unchanged.
- Fail open throughout: an unparseable envelope denies nothing and exits 0.

### 5. Codex registration and config

- **Task ID:** `codex-registration`
- **Depends On:** `edited-paths`
- **Assigned To:** `builder-wiring`
- **Agent Type:** `general-purpose`
- **Model / Effort:** `sonnet` / `low`
- **Parallel:** true
- **Satisfies:** AC1, AC4, AC16
- Write all 13 bindings into `.codex/hooks.json` exactly as tabulated in acceptance-criteria.md AC1.
  Keep the two existing entries' shape; add the other 11.
- Every entry: `uv run --script "$(git rev-parse --show-toplevel)/.claude/hooks/…"` plus a
  `statusMessage`.
- Prefix `HARNESS_HOOK_HOST=codex` onto the `block_destructive.py` command only.
- Explicit `timeout`: 60 on each of the four formatters, 120 on `stop_sweep`. No `timeout` key
  anywhere else.
- `PostToolUseFailure` does **not** appear — Codex has no such event, and its `PostToolUse` already
  fires for Bash commands that exit non-zero. `Stop` and `SubagentStop` carry no matcher (`Stop`
  ignores matchers entirely).
- Add to `.codex/config.toml`: `sandbox_mode = "workspace-write"`, `approval_policy = "on-request"`,
  and `[features] hooks = true`. Leave network unset (off by default) and preserve the existing
  `[agents]` block.
- Copy **no** script into `.codex/`.

### 6. Portability matrix and offline proof

- **Task ID:** `parity-matrix`
- **Depends On:** `codex-registration`
- **Assigned To:** `builder-parity`
- **Agent Type:** `general-purpose`
- **Model / Effort:** `opus` / `high`
- **Parallel:** false
- **Satisfies:** AC2, AC3, AC5, AC17
- Add `CODEX_DISPOSITIONS` to `test_wiring.py` beside `EXPECTED_BINDINGS`: one entry per hook
  entrypoint (15 today), valued `mirrored` / `not-applicable` / `blocked-<reason>`. Assert
  `set(CODEX_DISPOSITIONS) == entrypoints()` so a new hook with no disposition turns the suite red.
- Replace `test_codex_bash_guard_binding_is_pinned` with a generalised `CODEX_EXPECTED_BINDINGS`
  `Counter` pinning every entry by `(script, event, normalized matcher)` — reuse the existing
  `normalized()` and `script_of()` helpers rather than writing new ones.
- Assert shape on every Codex entry: `uv run --script` prefix, `$(git rev-parse --show-toplevel)`
  present, real file, no `..`, non-empty `statusMessage`.
- Assert the timeout policy in both directions (present on exactly the five, absent elsewhere).
- Assert disposition ↔ registration agreement in both directions: every `mirrored` entrypoint appears
  ≥ 1 time in `.codex/hooks.json`; every non-`mirrored` appears 0 times.
- Add `tests/harness-layer/hooks/test_offline.py`: `uv run --offline --script <hook>` with empty stdin
  exits 0 for all 15 entrypoints. **Skip**, don't fail, when the uv cache is cold — a fresh clone must
  not go red for an environmental reason. Respect the 45 s subprocess ceiling; mark it
  `@pytest.mark.timeout(120)` if the whole-suite pass needs it.
- Every test docstring states WHY the behaviour matters, not just what it does.

### 7. Catalog and memory update

- **Task ID:** `hooks-md-codex-column`
- **Depends On:** `parity-matrix`
- **Assigned To:** `builder-parity`
- **Agent Type:** `general-purpose`
- **Model / Effort:** `sonnet` / `medium`
- **Parallel:** false
- **Satisfies:** AC18
- **Record to memory:** yes — this task edits `.claude/rules/harness-layer/hooks.md`, the
  authoritative hook catalog.
- Add a **Codex** column to the catalog table. One cell per family: `mirrored`,
  `mirrored (write surface only)` for `sensitive-files/`, or `not-applicable`.
- Extend the "ship together" bullet in `## Development` so it names `.codex/hooks.json` and
  `CODEX_DISPOSITIONS` alongside `EXPECTED_BINDINGS` — otherwise the next hook added is Claude-only by
  default, which is the drift this plan exists to close.
- Add the cross-check test to `test_wiring.py`: parse the Codex column and assert the family-level
  implication against `CODEX_DISPOSITIONS` (a cell reads `mirrored` iff every entrypoint beneath it is
  `mirrored`, `not-applicable` iff none is).
- Keep it short and imperative per AGENTS.md § Harness Development — state what to do, not why it was
  chosen.

### 8. Live probe and acceptance evidence

- **Task ID:** `codex-probe`
- **Depends On:** `ask-tier-deny`, `formatters-multipath`, `scan-guard-multipath`, `parity-matrix`
- **Assigned To:** `prober`
- **Agent Type:** `general-purpose`
- **Model / Effort:** `opus` / `high`
- **Parallel:** false
- **Satisfies:** AC19, AC20
- Write `scripts/codex-hook-probe.sh`. It must live **outside** `.claude/hooks/` — `entrypoints()`
  claims any shebang-bearing file under that tree, so a probe placed there fails
  `test_every_entrypoint_is_claimed_by_a_registration_surface`.
- One `codex exec --dangerously-bypass-hook-trust` session per mirrored hook, each driving the hook's
  real trigger: a planted secret written through `apply_patch`, a blocked destructive command, an
  ask-tier command, an attribution-carrying git command, a write to a cataloged sensitive path, a
  rename onto one, and an unformatted file.
- **Assert the block happened.** Every hook fails open, so "the session produced no error" proves
  nothing — grep the session output for the specific `BLOCKED` / `Blocked` evidence, and fail the
  probe when it is absent.
- Exit with a clear message, not a stack trace, when `codex` is not installed. Work in a scratch
  directory and clean up after; re-running must be idempotent.
- Run it by hand and paste the real output into `specs/codex-hooks-sync/implementation-notes.md`,
  recording the Codex CLI version and one pass/fail line per mirrored hook.
- Assemble any secret-shaped fixture at runtime from fragments — never commit a matchable literal.

### 9. Validate Everything

- **Task ID:** `validate-all`
- **Depends On:** `edited-paths`, `ask-tier-deny`, `formatters-multipath`, `scan-guard-multipath`,
  `codex-registration`, `parity-matrix`, `hooks-md-codex-column`, `codex-probe`
- **Assigned To:** `validator`
- **Agent Type:** `general-purpose`
- **Model / Effort:** `opus` / `high`
- **Parallel:** false
- **Satisfies:** all AC1–AC20
- Run every command in acceptance-criteria.md → `## Validation Commands`.
- Verify each acceptance criterion is met.
- Confirm AC15 specifically: `git diff` touches no pre-existing test assertion. A pre-existing test
  that had to change means Claude-side behaviour changed — that is a failure, not a fixup.
- Confirm no file was added under `.codex/hooks/` and no hook script was duplicated.
- Confirm `implementation-notes.md` carries real probe output, not a placeholder. A green pytest run
  is **not** acceptance evidence for this plan.
