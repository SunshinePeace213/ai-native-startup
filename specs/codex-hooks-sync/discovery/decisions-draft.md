# Decisions: codex-hooks-sync

> Interview-pass draft — the locked decision record for the Claude → Codex hook parity plan.
> Transcribe verbatim into `specs/codex-hooks-sync/decisions.md` at plan time.

## Summary

Mirror this repo's Claude Code hooks into Codex without duplicating a single script. `.codex/hooks.json`
points at the existing `.claude/hooks/` files using the `$(git rev-parse --show-toplevel)` form the Codex
docs recommend; host differences are expressed as registration differences plus one flag, never as forked
scripts. Thirteen of the sixteen Claude bindings mirror; three are not-applicable (the command-scoped spec
gate and the two worktree hooks, which have no Codex event). Two behaviours change shape at the crossing:
the destructive guard's nine `ask` rules become denies under Codex — Codex parses `permissionDecision: "ask"`
but does not support it and would run the command anyway — and every path-taking hook moves from
`tool_input.file_path` to a shared `edited_paths(payload)` helper that parses the multi-file `apply_patch`
envelope. `.codex/config.toml` gains the Auto preset with network off, and the plan proves the hooks run
offline from a warmed uv cache. The sync mechanism is a portability matrix in `test_wiring.py`: every hook
entrypoint carries an explicit Codex disposition, and a hook with none turns the suite red. Because every
hook fails open by contract, static pins are not acceptance evidence — a committed probe script drives one
real Codex session per mirrored hook against its actual trigger.

## Resolved Decisions

- **Q:** What happens to the destructive guard's nine "ask the human" rules under Codex?
  - **A:** They deny. One script keeps both behaviours; `.codex/hooks.json` passes a host flag so the nine
    ask-tier rules exit 2 under Codex with the "ask the user to run it via the `!` prefix" fix line they
    already carry. Claude's ask tier is unchanged. No `permissions` or `.codex/rules` layer is added for this.
  - **Why:** Codex parses `permissionDecision: "ask"` but does not support it — it marks the hook run failed,
    reports the error, and **runs the command anyway** (`ai-docs/openai/codex/hooks.md:619-621`), so mirroring
    the script unchanged is worse than not mirroring it. A `permissions.allow` list cannot carry the tier
    either: both permission systems match a command *prefix* while the guard matches a regex anywhere in the
    line, so `prefix_rule(pattern=["git","push","--force"])` never sees `git push origin main --force`. The nine
    families are force-push, hard reset, `clean -f`, history rewrite, remote branch delete, `curl | bash`,
    LD_PRELOAD, profile writes, and recursive chmod 777 — all things this repo's git workflow already forbids
    an agent from doing unattended, so denying costs nothing real.

- **Q:** How do the six path-taking hooks find the edited file under Codex, where `tool_input.file_path`
  does not exist?
  - **A:** A shared `edited_paths(payload) -> list[str]` helper: `[tool_input.file_path]` under Claude, and the
    `*** Add File:` / `*** Update File:` / `*** Delete File:` paths parsed out of `tool_input.command` under
    Codex. Every write-surface hook — the four auto-format formatters, `post_write_scan.py`, and
    `file_guard.py`'s edit surface — loops over the returned list.
  - **Why:** Codex has no `file_path` field at all; edits arrive as `apply_patch` with the whole patch envelope
    in `tool_input.command`, and one patch can add, update, or delete **several** files
    (`ai-docs/openai/codex/hooks.md:558, 697-703`). A key-rename shim cannot bridge that — the callers have to
    become path-list consumers. Mirroring every write-surface hook (rather than only the security ones) is what
    keeps a secret written through `apply_patch` from going unscanned.

- **Q:** When behaviour has to differ per host, does the hook branch or fork?
  - **A:** One script per hook, host-adaptive. A single catalog and a single matcher; host differences are
    registration differences (`.codex/hooks.json` matches `apply_patch`, so `file_guard` covers only the write
    surface under Codex) plus a flag where semantics must change. No per-host script variants.
  - **Why:** Duplicating scripts into `.codex/hooks/` creates a second thing to keep in sync — the exact drift
    the discovery pass ruled out, and the reason Codex points at `.claude/hooks/` at all. `.codex/hooks/` is
    example convention in the docs, not a requirement; `command` is arbitrary shell. Forking would double every
    catalog, regex, and test for the two hooks that actually diverge.

- **Q:** What does `.codex/config.toml` pin for sandbox, network, and approvals?
  - **A:** The Auto preset: `sandbox_mode = "workspace-write"`, `approval_policy = "on-request"`,
    `[features] hooks = true`, network left off. The plan proves the hooks run offline from a warmed uv cache
    (every PEP 723 header declares `dependencies = []`) and adds a check for it.
  - **Why:** `workspace-write` keeps network access off by default
    (`ai-docs/openai/codex/agent-approvals-security.md:43-48`). Every hook runs `uv run --script`, so a cold uv
    cache that needs to fetch an interpreter kills the hook — silently, because these hooks all fail open.
    Opening egress project-wide to protect one cache is the wrong trade: it widens the boundary for every
    command in the session, not just uv. `approvals_reviewer = "auto_review"` was considered as an unattended
    substitute for the lost ask tier and rejected — extra model calls per escalation, judged against a policy
    that is not ours.

- **Q:** Where does each hook's Codex disposition live, so a hook with none fails the suite?
  - **A:** A `CODEX_DISPOSITIONS` dict in `tests/harness-layer/hooks/test_wiring.py`, beside
    `EXPECTED_BINDINGS`, is the source of truth; every hook entrypoint must appear in it. The catalog table in
    `.claude/rules/harness-layer/hooks.md` gains a Codex column, and a test parses that column and asserts it
    agrees with the dict.
  - **Why:** The enforcement point has to be machine-readable, and a Python dict beside the existing binding
    matrix is the natural home. But `AGENTS.md` makes `hooks.md` the authoritative hook catalog, so the parity
    fact has to be visible where an agent reads it — cross-checking the column against the dict gets both
    without letting the doc drift. Disposition vocabulary: `mirrored` / `not-applicable` / `blocked-<reason>`.

- **Q:** How is a real Codex session driven, and what counts as acceptance evidence?
  - **A:** A committed probe script — one `codex exec --dangerously-bypass-hook-trust` run per mirrored hook,
    each driving the real trigger (a planted secret, a blocked command, an unformatted file) and asserting the
    block actually happened. It runs by hand, not under pytest; its output is pasted into
    `specs/codex-hooks-sync/implementation-notes.md` as the acceptance evidence. The pytest suite keeps pinning
    registration only.
  - **Why:** Every hook fails open by contract (`.claude/rules/harness-layer/hooks.md:35-37`), so a session that
    produces no error is indistinguishable from one where the hook never ran — "no error" proves nothing. A
    pytest integration suite would need Codex auth to pass, blow past the 45s subprocess ceiling, and go
    permanently red on any machine without the CLI, turning a real signal into noise. Keeping the probes
    committed but hand-run makes them repeatable for the next hook change without wiring CI to a credentialed
    external binary.

- **Q:** What should a failed `$(git rev-parse --show-toplevel)` do?
  - **A:** Nothing changes. The substitution yields an empty string, uv errors, and Codex reports a hook failure
    and continues — fail-open, which is the contract. The behaviour is stated explicitly in the parity record so
    it is not re-litigated. `resolve_root()` gains no `cwd` tier.
  - **Why:** A non-repo cwd is not a state this repo's hooks operate in, and Codex already surfaces the failure
    rather than swallowing it (`ai-docs/openai/codex/hooks.md:194-197`). A `${CODEX_REPO_ROOT:-…}` fallback would
    invent a second root convention nobody sets. Failing closed would put one hook against the fail-open contract
    every other hook follows. Inside the script, `$CLAUDE_PROJECT_DIR` is never set by Codex, so `resolve_root()`
    falls through to `Path(__file__).parents[3]` — which is correct under Codex and strictly more reliable than
    the payload's `cwd` (`.claude/hooks/sensitive-files/_common.py:78-89`).

- **Q:** Does the generalised pin require a `statusMessage` and a `timeout` on every Codex entry?
  - **A:** `statusMessage` on every entry, enforced by the generalised test. Explicit `timeout` values only where
    the default is wrong — the four auto-format formatters and `stop_sweep` — while the pure-inspection guards
    keep the default.
  - **Why:** Codex defaults an omitted `timeout` to 600 seconds (`ai-docs/openai/codex/hooks.md:184-186`), which
    is ten minutes of a wedged formatter before the turn moves on. The hooks that shell out to real formatters or
    sweep real files are the ones that can hang; guards that only inspect a command string cannot. Requiring a
    number on every entry would mean guessing values for hooks whose duration is bounded by construction.

- **Q:** Is there prior art to port from — a library, vendor folder, or existing cross-host hook?
  - **A:** None. The `apply_patch` envelope parser is written from the envelope grammar; the plan authors no
    Reference map.
  - **Why:** Asked and answered in round 1; recorded so the plan does not re-open it.

## Assumptions

Every decision above was taken by accepting the recommendation, so each carries the recommender's reasoning
rather than an independent judgement. The build should challenge any of them. Beyond that:

- **Codex hooks run outside the sandbox.** The hooks doc never states whether hook subprocesses are sandboxed.
  If they are, `uv run --script` may be blocked from its cache under `~/.cache/uv` — outside the workspace —
  and every mirrored hook fails open silently. **Invalidated by:** the first probe run showing a hook that
  should have blocked doing nothing. **Mitigation if true:** add the uv cache dir to
  `[sandbox_workspace_write] writable_roots`.
- **A warmed uv cache makes the hooks fully offline.** Rests on every PEP 723 header declaring
  `dependencies = []` and a Python 3.12 interpreter already being present. **Invalidated by:** uv attempting an
  interpreter download on a clean machine.
- **The `apply_patch` envelope grammar is stable enough to parse.** The docs give the field but not the
  envelope's formal grammar; `transcript_path` is explicitly called out as unstable, and the patch format has no
  such guarantee either way. **Invalidated by:** a probe where a multi-file patch yields no parsed paths.
- **`--dangerously-bypass-hook-trust` faithfully reproduces a trusted run.** The probes bypass the trust gate;
  a human still has to run `/hooks` once for real sessions. **Invalidated by:** a hook that passes its probe but
  stays silent in a normally-trusted session.
- **The nine denied families are not needed by Codex agents in this repo.** Codex is used here for review
  subagents and occasional implementation. **Invalidated by:** a Codex task legitimately blocked on
  `git reset --hard` or `git clean -f`.
- **The KB has no Claude Code permissions/settings page.** Nothing in `ai-docs/anthropic/` covers
  `permissions.allow` matching semantics, so the claim that Claude's Bash rules are prefix-matched (making
  `Bash(git * main)` not behave as written) is asserted from the Codex side of the comparison only. **The plan
  must mirror the Claude Code IAM/settings page via `/harness-layer:kb add` before writing any `permissions`
  block** — though under the locked Q1 answer, no `permissions` block is written at all.

## Open Questions / Out of Scope

- **Out of scope:** `WorktreeCreate` / `WorktreeRemove` — Codex has no such events. Disposition:
  `not-applicable`.
- **Out of scope:** `check_spec_completeness.py` — command-scoped to `/harness-layer:harness-plan`, and Codex has
  no per-command hooks. Disposition: `not-applicable`.
- **Out of scope:** `file_guard.py`'s Read/Grep surface under Codex — Codex has no `Read` or `Grep` tool
  (`ai-docs/openai/codex/hooks.md:352-359`); file reads go through Bash, which `bash_guard.py` already
  intercepts. Only the write surface is mirrored.
- **Out of scope:** a `permissions.allow` allowlist on either host. It solves prompt noise, not the ask tier, and
  nothing in this plan needs it.
- **Out of scope:** `.codex/rules/*.rules` `prefix_rule` entries. Considered as a native Codex prompt channel and
  rejected — prefix-only matching, and it governs only commands leaving the sandbox.
- **Out of scope:** duplicating hook scripts into `.codex/hooks/`.
- **Open question:** whether `PermissionRequest` (a Codex event with no Claude counterpart) is worth a hook of its
  own later. Not a parity question — it has no Claude side to mirror — so it is out of this plan. **Owner:** a
  follow-up plan.
- **Open question:** whether `SubagentStop`'s Codex matcher (applied to `agent_type`) needs a value once this
  repo runs Codex subagents that should be swept differently from the main thread. Mirrored with no matcher for
  now, which matches all. **Owner:** the build, if a probe surfaces a gap.
