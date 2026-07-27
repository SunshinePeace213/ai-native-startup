# Decisions: codex-hooks-sync

> The interview record for [spec.md](./spec.md) — why the plan is the way it is. Lifecycle tracking and
> the Codex review record live in spec.md, NOT here; this file is the immutable decision history.

## Summary

Mirror this repo's Claude Code hooks into Codex without duplicating a single script.
`.codex/hooks.json` points at the existing `.claude/hooks/` files using the
`$(git rev-parse --show-toplevel)` form the Codex docs recommend; host differences are expressed as
registration differences plus one flag, never as forked scripts. Twelve of the fifteen hook
entrypoints mirror (as thirteen Codex bindings); three are not-applicable — the command-scoped spec
gate and the two worktree hooks, which have no Codex event. Two behaviours change shape at the
crossing: the destructive guard's nine `ask` rules become denies under Codex — Codex parses
`permissionDecision: "ask"` but does not support it and would run the command anyway — and every
path-taking hook moves from `tool_input.file_path` to a shared `edited_paths(payload)` helper that
parses the multi-file `apply_patch` envelope. `.codex/config.toml` gains the Auto preset with network
off, and the plan proves the hooks run offline from a warmed uv cache. The sync mechanism is a
portability matrix in `test_wiring.py`: every hook entrypoint carries an explicit Codex disposition,
and a hook with none turns the suite red. Because every hook fails open by contract, static pins are
not acceptance evidence — a committed probe script drives one real Codex session per mirrored hook
against its actual trigger.

Everything above is the interview ledger, transcribed from
[discovery/decisions-draft.md](./discovery/decisions-draft.md). Planning then ran the live
verification the ledger's assumptions asked for; the results are recorded under
`## Plan-time Verification` and refine three decisions without re-opening any.

## Resolved Decisions

Transcribed verbatim from the interview ledger. Resolved stays resolved.

- **Q:** What happens to the destructive guard's nine "ask the human" rules under Codex?
  - **A:** They deny. One script keeps both behaviours; `.codex/hooks.json` passes a host flag so the
    nine ask-tier rules exit 2 under Codex with the "ask the user to run it via the `!` prefix" fix
    line they already carry. Claude's ask tier is unchanged. No `permissions` or `.codex/rules` layer
    is added for this.
  - **Why:** Codex parses `permissionDecision: "ask"` but does not support it — it marks the hook run
    failed, reports the error, and **runs the command anyway** (`ai-docs/openai/codex/hooks.md:619-621`),
    so mirroring the script unchanged is worse than not mirroring it. A `permissions.allow` list
    cannot carry the tier either: both permission systems match a command *prefix* while the guard
    matches a regex anywhere in the line, so `prefix_rule(pattern=["git","push","--force"])` never
    sees `git push origin main --force`. The nine families are force-push, hard reset, `clean -f`,
    history rewrite, remote branch delete, `curl | bash`, LD_PRELOAD, profile writes, and recursive
    chmod 777 — all things this repo's git workflow already forbids an agent from doing unattended,
    so denying costs nothing real.
  - **Amended at plan time:** the premise (ask is unsupported, command runs anyway) is **confirmed
    live**. The *fix line* clause is corrected — see `## Plan-time Verification` → Finding 4. The nine
    ask rules do not carry a `!`-prefix hint; that wording lives on the deny tier. Each ask rule gains
    a host-neutral Codex line instead.

- **Q:** How do the six path-taking hooks find the edited file under Codex, where
  `tool_input.file_path` does not exist?
  - **A:** A shared `edited_paths(payload) -> list[str]` helper: `[tool_input.file_path]` under
    Claude, and the `*** Add File:` / `*** Update File:` / `*** Delete File:` paths parsed out of
    `tool_input.command` under Codex. Every write-surface hook — the four auto-format formatters,
    `post_write_scan.py`, and `file_guard.py`'s edit surface — loops over the returned list.
  - **Why:** Codex has no `file_path` field at all; edits arrive as `apply_patch` with the whole patch
    envelope in `tool_input.command`, and one patch can add, update, or delete **several** files
    (`ai-docs/openai/codex/hooks.md:558, 697-703`). A key-rename shim cannot bridge that — the callers
    have to become path-list consumers. Mirroring every write-surface hook (rather than only the
    security ones) is what keeps a secret written through `apply_patch` from going unscanned.
  - **Amended at plan time:** the grammar is now observed rather than inferred, and it includes a
    fourth directive the ledger did not list — `*** Move to:` for renames. The helper also needs no
    host flag: the payload shape discriminates on its own. See Findings 2 and 3.

- **Q:** When behaviour has to differ per host, does the hook branch or fork?
  - **A:** One script per hook, host-adaptive. A single catalog and a single matcher; host differences
    are registration differences (`.codex/hooks.json` matches `apply_patch`, so `file_guard` covers
    only the write surface under Codex) plus a flag where semantics must change. No per-host script
    variants.
  - **Why:** Duplicating scripts into `.codex/hooks/` creates a second thing to keep in sync — the
    exact drift the discovery pass ruled out, and the reason Codex points at `.claude/hooks/` at all.
    `.codex/hooks/` is example convention in the docs, not a requirement; `command` is arbitrary
    shell. Forking would double every catalog, regex, and test for the two hooks that actually
    diverge.

- **Q:** What does `.codex/config.toml` pin for sandbox, network, and approvals?
  - **A:** The Auto preset: `sandbox_mode = "workspace-write"`, `approval_policy = "on-request"`,
    `[features] hooks = true`, network left off. The plan proves the hooks run offline from a warmed
    uv cache (every PEP 723 header declares `dependencies = []`) and adds a check for it.
  - **Why:** `workspace-write` keeps network access off by default
    (`ai-docs/openai/codex/agent-approvals-security.md:43-48`). Every hook runs `uv run --script`, so
    a cold uv cache that needs to fetch an interpreter kills the hook — silently, because these hooks
    all fail open. Opening egress project-wide to protect one cache is the wrong trade: it widens the
    boundary for every command in the session, not just uv. `approvals_reviewer = "auto_review"` was
    considered as an unattended substitute for the lost ask tier and rejected — extra model calls per
    escalation, judged against a policy that is not ours.
  - **Amended at plan time:** the offline check stays, but its *rationale* narrows. Hooks run outside
    the sandbox (Finding 1), so the network boundary was never what threatened them; a cold cache
    still would. The check is worth keeping for that reason alone.

- **Q:** Where does each hook's Codex disposition live, so a hook with none fails the suite?
  - **A:** A `CODEX_DISPOSITIONS` dict in `tests/harness-layer/hooks/test_wiring.py`, beside
    `EXPECTED_BINDINGS`, is the source of truth; every hook entrypoint must appear in it. The catalog
    table in `.claude/rules/harness-layer/hooks.md` gains a Codex column, and a test parses that
    column and asserts it agrees with the dict.
  - **Why:** The enforcement point has to be machine-readable, and a Python dict beside the existing
    binding matrix is the natural home. But `AGENTS.md` makes `hooks.md` the authoritative hook
    catalog, so the parity fact has to be visible where an agent reads it — cross-checking the column
    against the dict gets both without letting the doc drift. Disposition vocabulary: `mirrored` /
    `not-applicable` / `blocked-<reason>`.
  - **Amended at plan time:** `hooks.md`'s catalog is one row per *family*, not per entrypoint, so the
    column carries a family-level verdict and the cross-check is a family-level implication. See
    Finding 6.

- **Q:** How is a real Codex session driven, and what counts as acceptance evidence?
  - **A:** A committed probe script — one `codex exec --dangerously-bypass-hook-trust` run per
    mirrored hook, each driving the real trigger (a planted secret, a blocked command, an unformatted
    file) and asserting the block actually happened. It runs by hand, not under pytest; its output is
    pasted into `specs/codex-hooks-sync/implementation-notes.md` as the acceptance evidence. The
    pytest suite keeps pinning registration only.
  - **Why:** Every hook fails open by contract (`.claude/rules/harness-layer/hooks.md:35-37`), so a
    session that produces no error is indistinguishable from one where the hook never ran — "no error"
    proves nothing. A pytest integration suite would need Codex auth to pass, blow past the 45s
    subprocess ceiling, and go permanently red on any machine without the CLI, turning a real signal
    into noise. Keeping the probes committed but hand-run makes them repeatable for the next hook
    change without wiring CI to a credentialed external binary.
  - **Amended at plan time:** the probe script lives at `scripts/codex-hook-probe.sh`, **not** under
    `.claude/hooks/`. `entrypoints()` claims any shebang-bearing file under that tree, so a probe
    placed there would fail `test_every_entrypoint_is_claimed_by_a_registration_surface`.

- **Q:** What should a failed `$(git rev-parse --show-toplevel)` do?
  - **A:** Nothing changes. The substitution yields an empty string, uv errors, and Codex reports a
    hook failure and continues — fail-open, which is the contract. The behaviour is stated explicitly
    in the parity record so it is not re-litigated. `resolve_root()` gains no `cwd` tier.
  - **Why:** A non-repo cwd is not a state this repo's hooks operate in, and Codex already surfaces
    the failure rather than swallowing it (`ai-docs/openai/codex/hooks.md:194-197`). A
    `${CODEX_REPO_ROOT:-…}` fallback would invent a second root convention nobody sets. Failing closed
    would put one hook against the fail-open contract every other hook follows. Inside the script,
    `$CLAUDE_PROJECT_DIR` is never set by Codex, so `resolve_root()` falls through to
    `Path(__file__).parents[3]` — which is correct under Codex and strictly more reliable than the
    payload's `cwd` (`.claude/hooks/sensitive-files/_common.py:78-89`).

- **Q:** Does the generalised pin require a `statusMessage` and a `timeout` on every Codex entry?
  - **A:** `statusMessage` on every entry, enforced by the generalised test. Explicit `timeout` values
    only where the default is wrong — the four auto-format formatters and `stop_sweep` — while the
    pure-inspection guards keep the default.
  - **Why:** Codex defaults an omitted `timeout` to 600 seconds
    (`ai-docs/openai/codex/hooks.md:184-186`), which is ten minutes of a wedged formatter before the
    turn moves on. The hooks that shell out to real formatters or sweep real files are the ones that
    can hang; guards that only inspect a command string cannot. Requiring a number on every entry
    would mean guessing values for hooks whose duration is bounded by construction.
  - **Plan-time addition:** concrete values — 60 s for each formatter (matching Claude's implicit
    60 s default) and 120 s for `stop_sweep`, which scans an unbounded tracked set.

- **Q:** Is there prior art to port from — a library, vendor folder, or existing cross-host hook?
  - **A:** None. The `apply_patch` envelope parser is written from the envelope grammar; the plan
    authors no Reference map.
  - **Why:** Asked and answered in round 1; recorded so the plan does not re-open it.

### Plan-time decisions

New decisions this plan takes, downstream of the verification below. None reverses a locked answer.

- **Q:** Does `edited_paths()` need the host flag?
  - **A:** No. It branches on payload shape — `tool_name == "apply_patch"` → parse the envelope; a
    non-empty string `tool_input.file_path` → return `[file_path]`; anything else → `[]`. The host
    flag stays, but only `block_destructive.py` reads it.
  - **Why:** The payload is already self-describing. A flag would be a second source of truth that can
    disagree with the payload actually in hand — and a flag typo would silently route a Codex payload
    down the Claude branch, returning `[]` and skipping the scan. Shape-branching cannot fail that
    way. This *narrows* the ledger's "flag where semantics must change": the ask tier is the only
    place semantics must change.

- **Q:** `edited_paths()` is needed by three hook families whose `_common.py` modules cannot import
  each other. One copy or three?
  - **A:** Three copies — one per family `_common.py` — pinned identical in behaviour by a single
    parametrized contract test that runs the same envelope corpus through all three modules.
  - **Why:** The families already duplicate `note()`, `read_payload()`, and `resolve_root()`; this is
    the established convention (Rule 11). The alternative is a shared `.claude/hooks/_hostlib.py`,
    which the hook scripts could only import via `sys.path` manipulation — `uv run --script` puts only
    the script's own directory on the path, and `hooks.md` explicitly forbids `sys.path` tricks. A
    parametrized test buys DRY's actual benefit (they cannot drift) without the import hazard.

- **Q:** Where does the host flag come from and what is it called?
  - **A:** An environment variable `HARNESS_HOOK_HOST=codex`, prefixed onto the `command` string in
    `.codex/hooks.json`. Absent or any other value means Claude.
  - **Why:** Codex `command` entries are arbitrary shell, so an env prefix needs no argument parsing
    in the script and no change to how Claude invokes it. Defaulting to Claude on an unset value keeps
    the Claude path the fallback for anything unrecognised, which is the safer of the two defaults
    (Claude's ask tier surfaces to a human; a wrong deny would only over-block).

## Assumptions

The ledger's assumptions, each now marked with its plan-time status.

- ~~**Codex hooks run outside the sandbox.**~~ **RESOLVED — true, verified live.** See Finding 1. No
  `writable_roots` change is needed and none is planned.
- **A warmed uv cache makes the hooks fully offline.** **Partially verified:** `uv run --offline
  --script` succeeds on this machine for a repo hook, and all 15 entrypoints declare
  `dependencies = []`. Still rests on a Python ≥3.12 interpreter already being cached.
  **Invalidated by:** uv attempting an interpreter download on a clean machine. **Mitigation:** the
  offline test skips rather than fails when the cache is cold.
- ~~**The `apply_patch` envelope grammar is stable enough to parse.**~~ **RESOLVED for shape —
  observed live** (Finding 2), including a directive the ledger missed. Stability across Codex
  releases is still not contractual; the parser must fail open on anything it does not recognise, and
  the probe script is what re-verifies the grammar after a Codex upgrade.
- **`--dangerously-bypass-hook-trust` faithfully reproduces a trusted run.** Unchanged. The probes
  bypass the trust gate; a human still has to run `/hooks` once for real sessions. **Invalidated by:**
  a hook that passes its probe but stays silent in a normally-trusted session.
- **The nine denied families are not needed by Codex agents in this repo.** Unchanged. Codex is used
  here for review subagents and occasional implementation. **Invalidated by:** a Codex task
  legitimately blocked on `git reset --hard` or `git clean -f`.
- ~~**The KB has no Claude Code permissions/settings page.**~~ **Moot.** The ledger required mirroring
  that page only "before writing any `permissions` block", and under the locked answer to Q1 no
  `permissions` block is written on either host. No KB gap-fill is needed for this plan.
- **Codex has no `!`-prefix shell escape.** New. Neither the KB nor `codex --help` shows one.
  **Consequence:** the Codex ask-tier fix line is worded host-neutrally. **Invalidated by:** finding a
  documented Codex equivalent, in which case the line can name it.

## Plan-time Verification

Six findings from a live `codex-cli 0.145.0` session run during planning, in a throwaway git repo
outside this worktree. These are observations, not inferences.

**Finding 1 — hook subprocesses are NOT sandboxed.** With `sandbox: workspace-write [workdir, /tmp,
$TMPDIR]` active and confirmed in the session banner, the agent's own
`touch $HOME/.probe_agent_write` returned `AGENTWRITE_BLOCKED`, while in the same configuration a
`PreToolUse` hook subprocess wrote to `$HOME/.cache/uv` and to `$HOME` successfully
(`can_write_uv_cache=yes`, `can_write_home=yes`). A `uv run --script` hook resolved Python 3.13.13
from the warm cache. → The ledger's largest assumption is retired; no `writable_roots` entry needed.

**Finding 2 — the `apply_patch` envelope grammar, as observed.** `tool_input.command` is a single
string. Four directive forms were captured from live sessions:

```text
*** Begin Patch                         *** Begin Patch
*** Add File: <abs path>                *** Update File: <abs path>
+alpha                                  @@
*** Add File: <abs path>                -two
+beta                                   +TWO
*** End Patch                           *** End Patch

*** Begin Patch                         *** Begin Patch
*** Delete File: <abs path>             *** Update File: <old abs path>
*** End Patch                           *** Move to: <new abs path>
                                        *** End Patch
```

Multi-file in one envelope is confirmed (two `*** Add File:` in one call). Paths were absolute in
every observed case, but nothing documents that guarantee — resolve relative paths against the
payload's `cwd`.

**Finding 3 — `*** Move to:` is a real directive the ledger did not list.** A rename emits
`*** Update File: <old>` followed by `*** Move to: <new>`. Two consequences: a formatter keyed on the
`Update File:` path would format a file that no longer exists, and — the security-relevant one —
`file_guard.py` checking only `Update File:` would let an agent rename a file *onto* a cataloged
sensitive path unchallenged. Both paths must be checked.

**Finding 4 — the nine ask rules do not carry a `!`-prefix fix line.** Read from
`destructive-guard/_common.py`: all nine ask-tier `fix_hint`s end in some form of "approve only if X
is intended". The `"ask the user to run it themselves via the ! prefix"` wording the ledger cites
belongs to the **deny** tier. Under Codex the exit-2 stderr is read by the model, which cannot
approve anything, so reusing the ask hint verbatim would emit an uninterpretable instruction. Each
ask rule therefore gains a distinct Codex fix line.

**Finding 5 — both `PreToolUse` decision paths behave exactly as the KB documents.** In one session:
a hook returning `permissionDecision: "ask"` produced `hook: PreToolUse Failed` and the command
**ran anyway** (`ASKME-marker` was printed). A hook exiting 2 produced `hook: PreToolUse Blocked`,
the command did not run, and the stderr text — including its `Fix:` line — was surfaced to the model
verbatim. → The ask→deny decision is correct, and exit-2 diagnostics carry across intact.

**Finding 6 — counts, and the catalog's granularity.** `.claude/hooks/` holds **15** entrypoints (not
16); all 15 declare `dependencies = []`. `EXPECTED_BINDINGS` holds 16 rows because
`track_bash_writes.py` is registered on two events. Mirroring yields **13** Codex bindings and
splits dispositions 12 mirrored / 3 not-applicable. Separately, `hooks.md`'s catalog table is one row
per *family* (`auto-format/`, `security-scan/`), so its Codex column cannot be per-entrypoint; the
cross-check test asserts a family-level implication instead — a family cell reads `mirrored` iff
every entrypoint beneath it is mirrored, `not-applicable` iff none is.

## KB References

Docs consulted, with their `fetched` dates. None is older than the 30-day staleness bar (today:
2026-07-27), so no `/harness-layer:kb` refresh is due.

| Doc | Fetched | Used for |
| --- | --- | --- |
| [ai-docs/openai/codex/hooks.md](../../ai-docs/openai/codex/hooks.md) | 2026-07-27 | Event list, matcher table, tool coverage, `PreToolUse`/`PostToolUse`/`Stop`/`SubagentStop` I/O contracts, timeout defaults, trust flow |
| [ai-docs/openai/codex/sandboxing.md](../../ai-docs/openai/codex/sandboxing.md) | 2026-07-26 | Sandbox modes, the `workspace-write` + `on-request` Auto preset, `writable_roots` |
| [ai-docs/openai/codex/agent-approvals-security.md](../../ai-docs/openai/codex/agent-approvals-security.md) | 2026-07-26 | `network_access` default under `workspace-write` |
| [ai-docs/openai/codex/permissions.md](../../ai-docs/openai/codex/permissions.md) | 2026-07-26 | Checked for a hook-sandboxing statement — none present |
| [ai-docs/openai/codex/config-advanced.md](../../ai-docs/openai/codex/config-advanced.md) | 2026-07-21 | Hook config placement in `config.toml` |
| [.claude/rules/harness-layer/hooks.md](../../.claude/rules/harness-layer/hooks.md) | n/a (repo rule) | Fail-open contract, ship-together rule, testing rules |

**Live verification.** The KB is silent on whether hook subprocesses are sandboxed, and it documents
the `apply_patch` envelope as a field rather than a grammar. Both gaps were closed empirically
against `codex-cli 0.145.0` rather than by fetching more docs — see `## Plan-time Verification`. No
KB doc conflicted with observed behaviour; the `"ask"` semantics at `hooks.md:619-621` were confirmed
exactly as written.

**No gap-fill was needed.** The one page the ledger flagged as missing (Claude Code
permissions/settings) is moot under the locked decision not to write a `permissions` block.

## Open Questions / Out of Scope

- **Out of scope:** `WorktreeCreate` / `WorktreeRemove` — Codex has no such events. Disposition:
  `not-applicable`.
- **Out of scope:** `check_spec_completeness.py` — command-scoped to `/harness-layer:harness-plan`,
  and Codex has no per-command hooks. Disposition: `not-applicable`.
- **Out of scope:** `file_guard.py`'s Read/Grep surface under Codex — Codex has no `Read` or `Grep`
  tool (`ai-docs/openai/codex/hooks.md:352-359`); file reads go through Bash, which `bash_guard.py`
  already intercepts. Only the write surface is mirrored.
- **Out of scope:** a `permissions.allow` allowlist on either host. It solves prompt noise, not the
  ask tier, and nothing in this plan needs it.
- **Out of scope:** `.codex/rules/*.rules` `prefix_rule` entries. Considered as a native Codex prompt
  channel and rejected — prefix-only matching, and it governs only commands leaving the sandbox.
- **Out of scope:** duplicating hook scripts into `.codex/hooks/`.
- **Open question:** whether `PermissionRequest` (a Codex event with no Claude counterpart) is worth a
  hook of its own later. Not a parity question — it has no Claude side to mirror — so it is out of
  this plan. **Owner:** a follow-up plan.
- **Open question:** whether `SubagentStop`'s Codex matcher (applied to `agent_type`) needs a value
  once this repo runs Codex subagents that should be swept differently from the main thread. Mirrored
  with no matcher for now, which matches all. **Owner:** the build, if a probe surfaces a gap.
- **Open question (new):** Codex fires `SessionEnd`, `SubagentStart`, `PostCompact`, and
  `PermissionRequest`, none of which Claude has a counterpart for in this repo. They are not parity
  gaps, but `SessionEnd` in particular could carry a cheaper end-of-session sweep than `Stop`.
  **Owner:** a follow-up plan.
