# Acceptance Criteria: codex-hooks-sync

> The definition of "done" for [spec.md](./spec.md). Every criterion is observable and testable, and
> every task in tasks.md should map to at least one criterion here.

## Acceptance Criteria

### Registration & parity

- **AC1** — `.codex/hooks.json` contains exactly these 13 bindings, each running a `.claude/hooks/`
  script through `uv run --script "$(git rev-parse --show-toplevel)/…"`, and no script is copied into
  `.codex/hooks/`:

  | Script | Event | Matcher |
  | --- | --- | --- |
  | `block_attribution.py` | PreToolUse | `Bash` |
  | `destructive-guard/block_destructive.py` | PreToolUse | `Bash` |
  | `sensitive-files/bash_guard.py` | PreToolUse | `Bash` |
  | `sensitive-files/file_guard.py` | PreToolUse | `apply_patch` |
  | `auto-format/js_ts.py` | PostToolUse | `apply_patch` |
  | `auto-format/data.py` | PostToolUse | `apply_patch` |
  | `auto-format/markdown.py` | PostToolUse | `apply_patch` |
  | `auto-format/python.py` | PostToolUse | `apply_patch` |
  | `security-scan/post_write_scan.py` | PostToolUse | `apply_patch` |
  | `security-scan/track_bash_writes.py` | PostToolUse | `Bash` |
  | `security-scan/session_baseline.py` | SessionStart | (none) |
  | `security-scan/stop_sweep.py` | Stop | (none) |
  | `security-scan/stop_sweep.py` | SubagentStop | (none) |

- **AC2** — `CODEX_DISPOSITIONS` in `test_wiring.py` has one entry for every one of the 15 hook
  entrypoints, valued `mirrored`, `not-applicable`, or `blocked-<reason>`. Adding a new entrypoint
  without a disposition fails the suite; the split is 12 `mirrored` + 3 `not-applicable`
  (`check_spec_completeness.py`, `worktree/worktree_create.py`, `worktree/worktree_remove.py`).

- **AC3** — A generalised test pins **every** `.codex/hooks.json` entry as a `Counter` of
  `(script, event, normalized matcher)` — the same shape as `EXPECTED_BINDINGS` — replacing the
  single-hook `test_codex_bash_guard_binding_is_pinned`. Removing, adding, duplicating, or
  re-matching any entry fails. Every entry additionally: starts with `uv run --script`, contains
  `$(git rev-parse --show-toplevel)`, resolves to a real file under `.claude/hooks/`, contains no
  `..`, and carries a non-empty `statusMessage`.

- **AC4** — Explicit `timeout` values appear on exactly five entries — the four `auto-format/*.py`
  formatters (60) and `security-scan/stop_sweep.py` (120) — and on no others. A test asserts both
  directions.

- **AC5** — Every `mirrored` entrypoint appears at least once in `.codex/hooks.json`, and every
  `not-applicable` / `blocked-*` entrypoint appears zero times. A test asserts both directions, so a
  disposition that disagrees with reality fails.

### Destructive guard — ask tier under Codex

- **AC6** — With `HARNESS_HOOK_HOST=codex` set, a Bash payload matching any of the nine ask-tier
  rules exits **2** with the rule's `BLOCKED (<Category>/<rule_id>)` / `Why:` / `Fix:` block on
  stderr and **nothing on stdout**. All nine rules are covered by test cases.

- **AC7** — With `HARNESS_HOOK_HOST` unset (or any value other than `codex`), the same payload exits
  **0** and prints the existing `permissionDecision: "ask"` JSON on stdout. The current
  destructive-guard tests pass **unmodified**.

- **AC8** — Deny-tier rules exit 2 identically on both hosts; the host flag changes nothing for them.

- **AC9** — Each of the nine ask-tier rules carries a Codex-specific fix line that is host-neutral —
  it does not mention the `!` prefix and does not instruct the reader to "approve" anything. A test
  asserts no ask rule's Codex fix text matches `/!\s*prefix|approve/i`.

### `edited_paths()` — the write surface

- **AC10** — `edited_paths(payload)` is present in all three family `_common.py` modules
  (`auto-format`, `security-scan`, `sensitive-files`) and one **parametrized** test runs the same
  corpus through all three, so the copies cannot drift. The corpus covers:

  | Input | Expected |
  | --- | --- |
  | Claude payload with `tool_input.file_path` | `[file_path]` |
  | `*** Add File: <p>` | `[p]` |
  | `*** Update File: <p>` | `[p]` |
  | `*** Delete File: <p>` | `[p]` |
  | `*** Update File: <old>` + `*** Move to: <new>` | `[old, new]` |
  | Two `*** Add File:` in one envelope | both, in order |
  | Add + Update + Delete + Move in one envelope | all paths, in order |
  | Relative path in envelope | resolved against payload `cwd` |
  | Diff body containing a literal `*** Add File:` content line | not treated as a directive |
  | No envelope / truncated / empty path / missing `tool_input` / `None` | `[]` |
  | Envelope over the size cap | truncated scan, no raise |

- **AC11** — Each of the four formatters processes **every** path returned: a two-file `apply_patch`
  payload where both files match the formatter's extensions formats both. A failure on one path does
  not skip the remaining paths.

- **AC12** — `post_write_scan.py` adds every returned path to the session tracked set and scans every
  one. A two-file envelope where the **second** file carries a planted secret exits 2 with that
  file's diagnostic.

- **AC13** — `file_guard.py` denies an `apply_patch` payload whose envelope touches a cataloged
  sensitive path via **any** directive, including a `*** Move to:` whose *target* is protected while
  its source is not. Its Read/Grep/Edit/Write/MultiEdit behaviour is unchanged.

### Host safety & fail-open

- **AC14** — Every adapted hook still fails open: empty stdin, malformed JSON, a non-dict payload, a
  missing `tool_input`, and an unparseable envelope each exit **0** on both hosts.

- **AC15** — Claude-side behaviour is unchanged. The full pre-existing hook suite passes with no test
  file edited except `test_wiring.py` (which gains the Codex matrix) and the per-family files that
  gain **new** cases.

### Config, docs, evidence

- **AC16** — `.codex/config.toml` carries `sandbox_mode = "workspace-write"`,
  `approval_policy = "on-request"`, and `[features] hooks = true`, with no `network_access` key (off
  by default). The existing `[agents]` block is preserved.

- **AC17** — A test proves every one of the 15 entrypoints runs offline from a warm uv cache:
  `uv run --offline --script <hook>` with empty stdin exits 0 for each. The test **skips** (not
  fails) when the uv cache is cold, so a fresh clone does not go red for an environmental reason.

- **AC18** — `.claude/rules/harness-layer/hooks.md`'s catalog table has a **Codex** column, and a
  test parses it and asserts family-level agreement with `CODEX_DISPOSITIONS`: a family cell reads
  `mirrored` iff every entrypoint beneath it is `mirrored`, `not-applicable` iff none is. The
  "ship together" bullet also names `.codex/hooks.json` and `CODEX_DISPOSITIONS`.

- **AC19** — `scripts/codex-hook-probe.sh` is committed, executable, and drives one
  `codex exec --dangerously-bypass-hook-trust` session per mirrored hook against its real trigger
  (planted secret, blocked command, unformatted file, sensitive-path write, ask-tier command). Each
  case asserts the block actually happened rather than accepting "no error". It exits with a clear
  message — not a stack trace — when the `codex` binary is absent, works in a scratch directory, and
  cleans up after itself.

- **AC20** — The probe's real output is pasted into
  `specs/codex-hooks-sync/implementation-notes.md`, with the Codex CLI version recorded and one line
  per mirrored hook stating observed pass/fail. This is the acceptance evidence; a green pytest run
  is not.

## Validation Commands

Run from the repo root.

- `uv run pytest tests/harness-layer/hooks/test_wiring.py -q` — verifies AC1–AC5, AC18. All wiring
  and parity pins pass; the Codex matrix is enforced.
- `uv run pytest tests/harness-layer/hooks/destructive-guard/ -q` — verifies AC6–AC9. Both host
  branches covered, pre-existing cases unmodified.
- `uv run pytest tests/harness-layer/hooks/ -q -k edited_paths` — verifies AC10. The parametrized
  corpus passes against all three `_common` modules.
- `uv run pytest tests/harness-layer/hooks/auto-format/ tests/harness-layer/hooks/security-scan/ tests/harness-layer/hooks/sensitive-files/ -q`
  — verifies AC11–AC14.
- `uv run pytest tests/harness-layer/hooks/ -q` — verifies AC15. The whole hook suite is green.
- `uv run pytest tests/harness-layer/hooks/test_offline.py -q` — verifies AC17. Passes on a warm
  cache; reports skipped, never failed, on a cold one.
- `uv run pytest -q` — verifies AC15 repo-wide. Run once before hand-off, per the Python rule.
- `uv run python -c "import json,pathlib; d=json.loads(pathlib.Path('.codex/hooks.json').read_text())['hooks']; print(sum(len(b['hooks']) for bs in d.values() for b in bs))"`
  — verifies AC1. Prints `13`.
- `test -z "$(ls -A .codex/hooks 2>/dev/null)" && echo "no duplicated scripts"` — verifies AC1. No
  hook script was copied into `.codex/`.
- `uv run python -c "import tomllib,pathlib; c=tomllib.loads(pathlib.Path('.codex/config.toml').read_text()); print(c['sandbox_mode'], c['approval_policy'], c['features']['hooks'], 'agents' in c)"`
  — verifies AC16. Prints `workspace-write on-request True True`.
- `bash scripts/codex-hook-probe.sh` — verifies AC19–AC20. Run by hand, **not** under pytest; paste
  the output into `implementation-notes.md`. A pass is every mirrored hook reporting an observed
  block, not an absence of errors.
