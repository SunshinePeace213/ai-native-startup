# Spec: codex-hooks-sync

- **Owner:** @ringo
- **Status:** Drafted for Review

## Task Description

Mirror this repo's Claude Code hooks into Codex so both hosts enforce the same guardrails, without
duplicating a single hook script.

Today `.claude/settings.json` registers 16 bindings across 14 hook entrypoints (a 15th,
`check_spec_completeness.py`, is command-scoped). `.codex/hooks.json` registers exactly two of them
— `block_attribution.py` and `sensitive-files/bash_guard.py`. Everything else is unprotected under
Codex: a Codex session can `git push --force`, write a secret through `apply_patch`, or leave a file
unformatted, and nothing intervenes.

The build points `.codex/hooks.json` at the existing `.claude/hooks/` scripts using
`$(git rev-parse --show-toplevel)`, adapts the two hooks whose behaviour genuinely differs across
hosts, and closes the drift channel with a portability matrix in the wiring test.

Discovery for this plan lives in [discovery/](./discovery/) — the unknowns pass
(`unknowns.html`), the interview pass (`interview.html`), and the locked ledger
(`decisions-draft.md`), transcribed into [decisions.md](./decisions.md).

## Objective

A Codex session in this repo fires the same 12 hook entrypoints a Claude session does, from the same
script files; the wiring test fails if any hook entrypoint lacks an explicit Codex disposition or if
any `.codex/hooks.json` entry drifts from its pin; and a committed probe script demonstrates each
mirrored hook blocking its real trigger in a live Codex session.

## Non-Goals

- `WorktreeCreate` / `WorktreeRemove` — Codex has no such events. Disposition `not-applicable`.
- `check_spec_completeness.py` — command-scoped to `/harness-layer:harness-plan`; Codex has no
  per-command hooks. Disposition `not-applicable`.
- `file_guard.py`'s Read/Grep surface under Codex — Codex has neither tool; file reads go through
  Bash, which `bash_guard.py` already intercepts. Only the write surface is mirrored.
- A `permissions.allow` allowlist on either host. It solves prompt noise, not the ask tier.
- `.codex/rules/*.rules` `prefix_rule` entries — prefix-only matching, and they govern only commands
  leaving the sandbox.
- Duplicating hook scripts into `.codex/hooks/`.
- A `PermissionRequest` hook — a Codex event with no Claude counterpart, so not a parity question.
- Any change to Claude-side behaviour. Every Claude code path must be byte-for-byte unchanged in
  effect; the Codex adaptations are additive.

## Problem Statement

Two registration surfaces exist and only one is enforced. `tests/harness-layer/hooks/test_wiring.py`
pins every `.claude/settings.json` binding as a `Counter`, so a Claude-side hook cannot be dropped,
mis-matched, or duplicated without turning the suite red. The Codex side has exactly one hand-written
test pinning exactly one hook (`test_codex_bash_guard_binding_is_pinned`) — `block_attribution.py` is
registered in `.codex/hooks.json` today with nothing pinning it at all.

The consequence is silent asymmetry. Every hook in this repo fails open by contract
(`.claude/rules/harness-layer/hooks.md`), so a Codex session where a guard never ran is
indistinguishable from one where it ran and found nothing. Nobody notices the gap until a Codex
agent does something a Claude agent would have been stopped from doing.

The drift is structural, not incidental: `hooks.md`'s "ship together" rule names `EXPECTED_BINDINGS`
and the contract tests, and says nothing about Codex, so the next hook added will be Claude-only by
default.

## Solution Approach

**One script per hook, host-adaptive; registration carries the difference.** `.codex/hooks.json`
invokes the same `.claude/hooks/*.py` files, resolved from the git root. Matcher differences do most
of the work — registering `file_guard.py` against `apply_patch` under Codex is what scopes it to the
write surface, with no code change. Only two behaviours need adapting:

1. **The destructive guard's ask tier denies under Codex.** Verified live: a hook returning
   `permissionDecision: "ask"` is marked `PreToolUse Failed` and *the command runs anyway*. A host
   flag (`HARNESS_HOOK_HOST=codex`, set in the Codex registration) makes the nine ask-tier rules
   exit 2 instead. Claude's ask tier is untouched.

2. **Path extraction becomes path-list extraction.** Codex has no `tool_input.file_path`; edits
   arrive as `apply_patch` with the whole envelope in `tool_input.command`, and one envelope can
   touch several files. A shared `edited_paths(payload) -> list[str]` helper returns
   `[tool_input.file_path]` for a Claude payload and the parsed envelope paths for a Codex one; the
   four formatters, `post_write_scan.py`, and `file_guard.py`'s write surface each loop over the
   result.

**The main alternative — duplicating the scripts into `.codex/hooks/`** — loses because it creates a
second thing to keep in sync, which is precisely the drift this plan exists to close. `.codex/hooks/`
is example convention in the Codex docs, not a requirement; `command` is arbitrary shell.

**Drift control is a portability matrix**, not a convention: `CODEX_DISPOSITIONS` sits beside
`EXPECTED_BINDINGS` in `test_wiring.py` and must name every hook entrypoint. Because `AGENTS.md`
makes `hooks.md` the authoritative hook catalog, the catalog table gains a Codex column and a test
asserts the column agrees with the dict — the fact is visible where an agent reads it and cannot
rot.

**Acceptance evidence is a live probe, not a green suite.** Every hook fails open, so a static pin
proves an entry *exists*, never that it *ran*. A committed `scripts/codex-hook-probe.sh` drives one
real `codex exec --dangerously-bypass-hook-trust` session per mirrored hook against its true trigger
and asserts the block happened. It runs by hand, not under pytest.

### Counts, stated once

Three different numbers describe this work and are easy to conflate:

| Count | Value | What it is |
| --- | --- | --- |
| Hook entrypoints | **15** | Files under `.claude/hooks/` with a PEP 723 marker or shebang (what `entrypoints()` finds and `CODEX_DISPOSITIONS` must cover) |
| Claude bindings | **16** | `EXPECTED_BINDINGS` rows — 14 entrypoints, with `track_bash_writes.py` registered on two events |
| Codex bindings | **13** | `.codex/hooks.json` entries after mirroring |

Dispositions split 15 = **12 mirrored** + **3 not-applicable**. The 16 → 13 binding drop is the two
worktree hooks plus `PostToolUseFailure` folding into `PostToolUse`.

## Requirements & Decisions

Ordered most-volatile first. The full record is in [decisions.md](./decisions.md).

- **`edited_paths()` is host-agnostic — it branches on payload shape, not on a host flag.**
  `tool_name == "apply_patch"` → parse the envelope; a string `tool_input.file_path` → return it as
  a one-item list. *Why:* the payload already discriminates, so a flag would be a second source of
  truth that can disagree with the payload in front of it. *Live alternative:* gate on
  `HARNESS_HOOK_HOST` like the destructive guard does — rejected as redundant, but it is the fallback
  if a future Codex payload stops being self-describing. This narrows the locked ledger's decision
  (which assumed the flag was needed for both changes); the ask-tier flag is unaffected.

- **The Codex deny message for an ask-tier rule is newly authored, not the existing `fix_hint`.**
  The nine ask rules' hints all read "…approve only if X is intended" — advice to a human at an
  approval prompt that does not exist under Codex. Under Codex the stderr goes to the *model*, so
  each ask-tier rule gains a second, host-neutral fix line: *"Ask the user to run this themselves."*
  *Why:* telling a Codex agent to "approve" is an instruction it cannot follow. *Live alternative:*
  reuse the deny tier's existing `"…via the ! prefix"` wording — rejected because the `!` prefix is a
  Claude Code affordance with no verified Codex equivalent.

- **The `apply_patch` parser handles `*** Move to:`.** Observed grammar, captured from a live
  session: `*** Begin Patch` … `*** End Patch` wrapping `*** Add File: <p>`, `*** Update File: <p>`,
  `*** Delete File: <p>`, and `*** Update File: <old>` + `*** Move to: <new>` for a rename. *Why:* a
  rename reports the old path only, so a formatter would act on a file that no longer exists — and
  `file_guard.py` would miss a rename *onto* a protected path. *Live alternative:* none; this is an
  observed fact, not a preference.

- **No `writable_roots` change; hooks are not sandboxed.** Verified live: with
  `sandbox: workspace-write [workdir, /tmp, $TMPDIR]` active, the agent's own
  `touch $HOME/.probe_agent_write` was **blocked** while a hook subprocess wrote to `$HOME/.cache/uv`
  successfully. `uv run --script` resolved Python 3.13.13 from the warm cache inside a hook. *Why:*
  this retires the ledger's largest assumption. *Live alternative:* if a future Codex release
  sandboxes hooks, add the uv cache to `[sandbox_workspace_write] writable_roots`.

- **`statusMessage` on every Codex entry; explicit `timeout` only on the four formatters and
  `stop_sweep`.** Codex defaults an omitted timeout to 600 s. Only hooks that shell out to real
  formatters or sweep real files can hang; pure-inspection guards are bounded by construction.

- **A failed `$(git rev-parse --show-toplevel)` fails open, loudly, and that is intended.** The
  substitution yields an empty string, uv errors, Codex reports a hook failure and continues. Stated
  here so it is not re-litigated. `resolve_root()` gains no `cwd` tier — under Codex
  `$CLAUDE_PROJECT_DIR` is unset, so it falls through to `Path(__file__).resolve().parents[3]`,
  which is correct.

## Tracking

- **Issue:** #62 — <https://github.com/SunshinePeace213/ai-native-startup/issues/62>
- **Branch:** `feat/62-codex-hooks-sync`
- **Worktree:** `/home/ringo/ai-native-startup/.claude/worktrees/codex-hooks-sync`
- **Review profile:** kb-grounded
- **PR:** <filled by /harness-layer:harness-build>

## Relevant Files

- `.codex/hooks.json` — grows from 2 entries to 13; the whole Codex registration surface.
- `.codex/config.toml` — gains the Auto preset (`workspace-write`, `on-request`,
  `[features] hooks = true`); keeps its existing `[agents]` block untouched.
- `.claude/hooks/destructive-guard/block_destructive.py` — ask tier branches on the host flag.
- `.claude/hooks/destructive-guard/_common.py` — nine ask rules gain a Codex fix line; add
  `hook_host()`.
- `.claude/hooks/auto-format/_common.py` — `read_file_path()` → `edited_paths()`; `target()` returns
  a list of files.
- `.claude/hooks/auto-format/{js_ts,data,markdown,python}.py` — loop over the returned paths.
- `.claude/hooks/security-scan/_common.py` — add `edited_paths()`.
- `.claude/hooks/security-scan/post_write_scan.py` — track and scan every returned path.
- `.claude/hooks/sensitive-files/_common.py` — add `edited_paths()`.
- `.claude/hooks/sensitive-files/file_guard.py` — add the `apply_patch` write surface; Read/Grep
  paths unchanged.
- `tests/harness-layer/hooks/test_wiring.py` — `CODEX_DISPOSITIONS`, `CODEX_EXPECTED_BINDINGS`, and
  the generalised pins replacing `test_codex_bash_guard_binding_is_pinned`.
- `tests/harness-layer/hooks/{auto-format,security-scan,sensitive-files,destructive-guard}/` —
  contract tests for the new behaviour, per family.
- `.claude/rules/harness-layer/hooks.md` — Codex column in the catalog; ship-together rule extended
  to name the Codex surface.

### New Files

- `scripts/codex-hook-probe.sh` — hand-run probe driving one live Codex session per mirrored hook.
  Deliberately **outside** `.claude/hooks/`: `entrypoints()` claims any shebang file under that tree,
  so a probe placed there would fail `test_every_entrypoint_is_claimed_by_a_registration_surface`.
- `tests/harness-layer/hooks/test_offline.py` — proves every entrypoint runs from a warm uv cache
  with no network.
- `specs/codex-hooks-sync/implementation-notes.md` — receives the probe output as acceptance
  evidence.

## Edge Cases

- **Multi-file `apply_patch`** — one envelope adding, updating, deleting, and renaming in a single
  call. Every returned path is processed; a failure on one path must not skip the rest.
- **Rename (`*** Move to:`)** — formatters and the scanner act on the **new** path; `file_guard.py`
  checks **both** old and new against the catalog, so a rename onto a protected path is denied.
- **Relative paths in the envelope** — observed absolute, but the grammar permits relative. Resolve
  against the payload's `cwd` field, not the process cwd.
- **Malformed or truncated envelope** — no `*** Begin Patch`, an unterminated envelope, or a
  directive with an empty path yields an empty list and exit 0. Fail open; never raise.
- **Envelope containing literal `*** Add File:` text inside a diff body** — only lines at directive
  position start a new file; content lines (`+`, `-`, ` `, `@@`) are never parsed as directives.
- **Oversized envelope** — reuse the destructive guard's 64 KB scan cap posture rather than parsing
  an unbounded string.
- **Empty tracked set / no findings** — unchanged: exit 0 silently.
- **`git rev-parse` fails (non-repo cwd)** — empty substitution, uv errors, Codex reports a hook
  failure and continues. Intended, documented, not fixed.
- **Codex CLI absent** — the pytest suite must stay green on a machine with no `codex` binary; the
  probe script is the only thing that needs it, and it exits with a clear message when missing.
- **Cold uv cache** — the offline test skips (not fails) when the cache has never been warmed, so
  a fresh clone does not go red for an environmental reason.
- **Concurrent hooks** — Codex launches matching hooks concurrently, same as Claude. The existing
  per-session lock in `security-scan/_common.update_state` already covers this; no new locking.
- **Re-running the probe** — idempotent: it works in a scratch directory and cleans up after itself.

## Red Flags

- Starting to write code without any written requirements
- Asking "should I just start building?" before clarifying what "done" means
- Implementing features not mentioned in any spec or task list
- Making architectural decisions without documenting them
- Skipping the spec because "it's obvious what to build"
- **A hook script copied into `.codex/hooks/`** — the one thing this plan exists to prevent.
- **A Claude-side behaviour change** that is not strictly additive; the Claude contract tests must
  pass unmodified.
- **A second one-off Codex test** instead of extending the generalised matrix.
- **`sys.path` manipulation** to share `edited_paths()` across families — see decisions.md; the
  three copies are deliberate and pinned by a parity test.
- **Claiming the work is done on a green pytest run** — every hook fails open, so the suite proves
  registration, never execution. Only the probe output is acceptance evidence.

## Notes

- No new dependencies. Every hook entrypoint declares `dependencies = []` (verified across all 15).
- The Codex CLI on this machine is `codex-cli 0.145.0`; `uv` is `0.11.21`.
- Per the invoking prompt, the Codex cross-review gate is **skipped** for this plan at the user's
  explicit instruction ("Not required to conduct any cross model review").
- Follow-up, not this plan: whether `PermissionRequest` deserves a hook of its own, and whether
  `SubagentStop`'s Codex matcher needs an `agent_type` value once this repo runs Codex subagents.

## Codex Verification

- **Outcome:** skipped — the invoking prompt explicitly waived cross-model review for this plan.
  Load-bearing Codex behaviour was instead verified empirically against a live `codex exec` session
  (see decisions.md `## KB References` → Live verification).
- **Rejected findings:** none — no review round ran.

## References

```text
specs/codex-hooks-sync/
├── discovery/              # unknowns.html, interview.html, decisions-draft.md
├── spec.md                 # this file — what & why, tracking, review record
├── decisions.md            # interview record: resolved decisions, assumptions, out-of-scope
├── tasks.md                # how & who: phases, team, step-by-step tasks
├── acceptance-criteria.md  # done: acceptance criteria + validation commands
└── artifacts/              # implementation-plan page
```

## Self Validation

- [x] Objective, Task Description, and Non-Goals are filled in (no placeholders left)
- [x] Requirements trace to tasks in tasks.md and to checks in acceptance-criteria.md
- [x] Acceptance criteria are specific and testable
- [x] All four files exist under specs/codex-hooks-sync/ and are saved in the repository
- [x] Codex review status recorded — waived by the invoking prompt, with empirical verification in
      its place
