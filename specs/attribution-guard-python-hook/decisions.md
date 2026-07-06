# Decisions: Attribution guard — Python hook + attribution settings

> The grilling record for [spec.md](./spec.md) — why the plan is the way it is. Lifecycle tracking and
> the Codex review record live in spec.md, NOT here; this file is the immutable decision history.

## Summary

The user asked to upgrade `block-coauthor-trailer.sh` from shell to Python and, having discovered
Claude Code's attribution settings, asked whether the hook is still needed at all. Grilling settled
on defense in depth: attribution settings turn all Claude attribution off at the source
(`commit: ""`, `pr: ""`, `sessionUrl: false` — no custom text for now), and the hook is rewritten
as a precise Python guard that deterministically blocks any `git`/`gh` command still carrying a
default Claude attribution form. Everything else (file naming, settings location, test style, doc
updates) follows repo conventions, recorded below as assumptions.

## Resolved Decisions

- **Q:** Attribution settings can hide the trailer at the source — is the hook still required?
  - **A:** Yes — keep both. Configure attribution off in settings AND rewrite the hook in Python as
    the enforcement backstop.
  - **Why:** Settings are prevention: they stop Claude Code from auto-appending attribution. They
    cannot block a trailer that a model, subagent, or plugin command writes by hand into a message.
    The hook guarantees the policy deterministically. Rules out "settings only, delete hook" and
    "hook only, skip settings."

- **Q:** Which attribution forms must the hook block?
  - **A:** All default Claude forms: `Co-Authored-By: Claude <any model name> <noreply@anthropic.com>`
    (matched as `co-authored-by:\s*claude`, case-insensitive), the `Claude-Session:` trailer, and
    the `🤖 Generated with [Claude Code](https://claude.com/claude-code)` PR footer (matched as
    `generated with \[?claude code\]?`, case-insensitive).
  - **Why:** User explicitly listed the model-name variants and the PR footer as must-blocks. With
    `sessionUrl: false` chosen, the session trailer is also unwanted attribution and gets the same
    treatment.

- **Q:** Custom attribution text — what should replace the defaults?
  - **A:** Nothing for now: `"attribution": {"commit": "", "pr": "", "sessionUrl": false}`.
  - **Why:** User initially wanted customization ideas (neutral `Assisted-By` trailer, branded
    co-author, audit links were offered), then decided "no customize message at this moment."
    Hiding everything also matches GIT-COMMIT-PR-MESSAGE.md verbatim, so no policy-doc change is
    needed. Customization is deferred, not rejected.

- **Q:** Where do the hook tests live?
  - **A:** `tests/harness-layer/hooks/test_block_attribution.py` — a repo-level
    `tests/harness-layer/hooks/` folder as the home for harness hook suites.
  - **Why:** User directive during drafting (supersedes the initial `.claude/hooks/tests/`
    recommendation); keeps test code out of the context-loaded `.claude/` tree and gives future
    hook tests a shared, predictable location.

- **Q:** Final sign-off on the full decision set?
  - **A:** Approved ("Approve — write the spec") on 2026-07-06.
  - **Why:** All nine replayed decisions accepted without revision.

- **Q:** (post-approval) Codex's advisory — move shared config to `.claude/settings.json`?
  - **A:** Yes, extended by a user directive into a workflow rule: `.claude/settings.json` becomes
    the tracked shared truth (plugins, hooks, attribution); `.claude/settings.local.json` becomes
    an untracked personal scratchpad (`git rm --cached` + `.gitignore`, on-disk copy reset to
    `{}`); AGENTS.md gains the rule "experiment in settings.local.json; fold shippable changes
    into settings.json before merging to main."
  - **Why:** Matches the documented settings scopes (project = shared, local = personal), removes
    the tracked-local-file oddity, and keeps a fast local-experimentation loop. Asked and answered
    after the round-2 approval per the advisory-recommendation workflow; automated merge-time
    enforcement of the rule is explicitly out of scope.

## Assumptions

Accepted by the user at sign-off as my recommendations; the build can challenge any of them by
reopening the plan, not by silently deviating:

- **Settings location (SUPERSEDED):** originally the `attribution` block was to join the tracked
  `.claude/settings.local.json`. Superseded post-approval by the settings.json migration decision
  above — shared config now lives in `.claude/settings.json`.
- **Hook naming & runtime:** `.claude/hooks/block_attribution.py`, `#!/usr/bin/env -S uv run
  --script` shebang with PEP 723 inline metadata (`requires-python = ">=3.12"`, stdlib only) —
  mirrors `lint.py` / `install_deps.py`. Snake_case because it is Python, like its siblings.
- **Precision gate:** the guard only pattern-matches when `tool_name == "Bash"` and
  `tool_input.command` contains a word-boundary `git` or `gh` token. A benign command that merely
  mentions attribution text is allowed — fixing the current hook's false positive. Word-boundary
  matching may rarely over-trigger (e.g. `echo git`), which is acceptable: blocking also requires
  an attribution pattern in the same command.
- **Failure posture:** fail-open. Unreadable/malformed stdin, unexpected exceptions → exit 0. A
  guard that wedges every Bash call is worse than a missed block; the settings layer still
  prevents generation. Matches `lint.py`'s never-block posture.
- **Block mechanics:** stderr policy message + exit 2, per the settings-based hook format
  (exit 2 = deny, stderr fed back to Claude so it retries clean).
- **Tests:** subprocess-based pytest (`tests/harness-layer/hooks/test_block_attribution.py`;
  location user-directed — see Resolved Decisions) that runs
  the script with sample payloads and asserts exit code + stderr — tests the real stdin→exit-code
  contract rather than internals. `pytest>=8` added to the existing `[dependency-groups] dev`.
- **Old hook removal:** `git rm .claude/hooks/block-coauthor-trailer.sh` after the replacement is
  registered — tracked-file removal is recoverable from history, satisfying the repo's safe-delete
  rule without a `~/.Trash` copy.
- **Docs:** update HARNESS-LAYER.md's hook section + Files tree only. GIT-COMMIT-PR-MESSAGE.md
  stays untouched.

## Open Questions / Out of Scope

- **Out of scope:** custom attribution text (`attribution.commit` / `attribution.pr` wording) —
  deferred by the user; revisit when they want a replacement footer (ideas already sketched:
  neutral `Assisted-By: Claude Code` trailer, branded co-author, audit-friendly session links).
- **Out of scope:** Codex-side attribution/config — Codex sessions are not governed by Claude Code
  hooks or settings.
- **Out of scope:** any change to `lint.py`, `install_deps.py`, or `check-spec-completeness.sh`.
- **Out of scope:** automated enforcement of the settings-sync rule (a merge-time CI check or
  hook) — the rule ships as AGENTS.md prose; automation is a candidate future chore.
- ~~Open question: migrate tracked settings from `settings.local.json` to a shared
  `settings.json`?~~ **Resolved** post-approval — see the settings.json migration decision above.

## KB References

Docs consulted for every harness claim in this spec (path — fetched date — what it grounds):

- `ai-docs/anthropic/settings.md` — 2026-07-06 (gap-filled by this plan) — attribution settings
  keys (`commit`, `pr`, `sessionUrl`), empty-string-hides behavior, precedence over the deprecated
  `includeCoAuthoredBy`, configuration scopes.
- `ai-docs/anthropic/hooks-guide.md` — 2026-07-05 — settings-based hook configuration
  (`hooks.PreToolUse[].matcher/hooks[]`), snake_case `tool_input` payload, the exit-2-blocks-with-
  stderr-feedback recipe ("Block edits to protected files"), hooks-as-deterministic-enforcement
  rationale.
- `ai-docs/anthropic/hooks.md` — 2026-07-05 — hook lifecycle and event catalog. NOTE: this
  reference describes a `hooks.json` format with camelCase fields and stdout-JSON decisions that
  differs from the settings-based format the repo uses; per the surface-conflicts rule the design
  follows hooks-guide.md + the repo's working config, and flags the discrepancy for a future KB
  re-sync.
- `ai-docs/astral/uv-scripts.md` — 2026-07-05 — `uv run --script`, PEP 723 inline script metadata,
  shebang executability for the Python hook.
