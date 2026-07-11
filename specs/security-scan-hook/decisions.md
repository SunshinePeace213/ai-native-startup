# Decisions: Security Scan Hook

> The grilling record for [spec.md](./spec.md) — why the plan is the way it is. Lifecycle tracking and
> the Codex review record live in spec.md, NOT here; this file is the immutable decision history.

## Summary

The owner wants agent-written files automatically checked for secrets, API keys, tokens, and
common vulnerability patterns after agents finish their work. Agreed scope: a security-scan hook
family following the repo's existing hook conventions — a per-write PostToolUse gate **and** a
Stop/SubagentStop sweep over a session-tracked file set (full coverage, including Bash-created
files, was chosen over the simpler per-write-only design). Secret findings block with exit 2;
curated vulnerability findings warn without blocking. False positives are suppressed by an inline
pragma and built-in placeholder heuristics. Everything is stdlib-only regex — no external scanner.

## Resolved Decisions

- **Q:** When should the scan fire — per write (PostToolUse), at turn end (Stop sweep), or both?
  - **A:** Both. PostToolUse on `Write|Edit|MultiEdit` for immediate feedback, plus a
    `Stop` + `SubagentStop` sweep over a session-tracked file list.
  - **Why:** Owner chose full coverage after weighing the tradeoff (asked twice for explanation
    first). Per-write alone misses files created via Bash; a naive sweep would flag the user's
    own uncommitted files, so the sweep is scoped by session tracking with a SessionStart
    baseline. Rules out: per-write-only (coverage gap accepted → rejected), unscoped
    whole-tree sweep (false-positive hazard).

- **Q:** What does the scanner detect, and how strictly is each category enforced?
  - **A:** Secrets/keys/tokens block with exit 2; a curated set of vulnerability patterns is
    reported as non-blocking warnings.
  - **Why:** Secret patterns match with very high precision — when they fire it's almost always
    real, so blocking is safe. Vulnerability patterns are heuristics that fire on legitimate
    code; a blocking false positive interrupts the agent for nothing. Rules out: both-blocking
    (owner offered, declined) and secrets-only (would drop the vulnerability half of the ask).

- **Q:** How are false positives suppressed?
  - **A:** An inline `security-scan: allow` pragma on (or immediately above) the flagged line,
    plus built-in placeholder heuristics (`example`, `changeme`, `your-key-here`, `xxx…`, etc.).
  - **Why:** Suppression stays visible in the diff exactly where it happens and is reviewable;
    placeholder heuristics keep docs/test fixtures from ever needing pragmas. Rules out: a
    central allowlist file (drifts, over-matches far from the code) and no-escape strict mode
    (a stuck false positive would need a scanner-rule edit to resolve).

- **Q:** (design, lead-resolved) How does the sweep know which files the agent touched?
  - **A:** `SessionStart` records the already-dirty set from `git status --porcelain` as a
    baseline; the per-write gate records each scanned path; a PostToolUse Bash hook adds
    (current dirty set − baseline) after each Bash call. State: `.claude/.security-scan/<session_id>.json`.
  - **Why:** This is the KB-documented recipe for full-coverage compliance scanning
    (hooks-guide: match Bash and list modified/untracked files via `git status --porcelain`),
    extended with a baseline so pre-existing user changes are never swept.
  - **Amended (Codex round 1):** the baseline subtraction means a Bash edit to a file that was
    already dirty at SessionStart is NOT tracked. This is a genuine conflict between two goals —
    full Bash coverage vs never flagging user-owned changes — and they cannot both hold without
    process-level attribution (pre/post snapshots would flag the user's own mid-session edits).
    Resolution: the never-flag-user-files principle wins; the coverage guarantee is explicitly
    narrowed in spec.md Objective/Non-Goals and AC4 asserts the exclusion. The per-write gate
    still covers Write/Edit on those files.
  - **Amended (Codex round 2):** two Bash coverage gaps closed. (1) The tracker is registered on
    `PostToolUseFailure` as well as `PostToolUse` for Bash — a command can write a file and then
    exit non-zero, and only the failure event fires. (2) The session state carries a last-seen
    git HEAD; the tracker unions `git diff --name-only <last-head>..HEAD` when HEAD moved, so a
    file written and committed inside one Bash invocation (clean tree afterwards) is still
    tracked. Mid-session commits are treated as agent-era: in this workflow commits during an
    agent session are agent commits, and a committed secret is precisely the highest-value
    finding to surface.

- **Q:** (design, lead-resolved) External scanner (gitleaks/trufflehog) or own ruleset?
  - **A:** Own curated stdlib-regex ruleset in a table-driven module.
  - **Why:** Every existing hook is a zero-dependency `uv run --script`; an external binary adds
    an install step (meta-install wiring) and version drift for marginal gain at this scale.

- **Q:** (design, lead-resolved) Stop-loop posture when findings persist?
  - **A (revised, Codex round 1):** The sweep parses `stop_hook_active` exactly as the KB guide
    prescribes: when false/absent, block (exit 2) on secret findings with full diagnostics; when
    true, print a final loud warning and exit 0. It blocks at most once per turn without
    progress.
  - **Why:** The original posture (keep blocking to the 8-cap) contradicted the cached guidance
    ("parse `stop_hook_active` and exit early if true") and could not deliver a hard gate anyway
    — the runtime overrides repeated blocks, so a secret would survive the override regardless.
    The revised contract is achievable and documented: the agent gets one forced continuation
    with diagnostics; the per-write gate remains the primary blocking layer.

## Assumptions

- Agents in this repo write files via Write/Edit/MultiEdit in the common case; Bash-created files
  are the minority path covered by tracking. Invalidated if a workflow writes primarily via Bash —
  the per-write gate would then rarely fire and the sweep becomes the primary gate (still works).
- Scan targets are text files of any extension; binary files (null-byte sniff) and vendored dirs
  (`node_modules`, `.venv`, `dist`) are skipped. Invalidated if secrets need to be caught inside
  binaries — out of scope by design.
- A 1 MiB per-file scan cap is enough for agent-written files. Invalidated by legitimately huge
  generated files — the cap notes truncation rather than failing.
- New hook family lives in the tracked `.claude/settings.json` (project scope, ships with the
  repo), not `settings.local.json`. Invalidated only if the owner wants it personal-only.
- Hooks fire identically inside subagent sessions, so per-write scanning covers builder agents;
  `SubagentStop` covers their completion sweep.
- Tests live under `tests/harness-layer/` and follow AGENTS.md pytest rules (parallel-safe,
  `tmp_path`/`monkeypatch`, no order dependence, no timeout raises).
- The non-blocking warn channel is `hookSpecificOutput.additionalContext` JSON on stdout with
  exit 0. If the running Claude Code version ignores it for PostToolUse, warnings degrade to
  invisible — acceptable because warnings are advisory by decision; the build verifies the JSON
  shape is emitted.

## Open Questions / Out of Scope

- **Out of scope:** full SAST / dependency (CVE) scanning — `/security-review` owns deep analysis
- **Out of scope:** scanning git history or files the agent never touched in the session
- **Out of scope:** auto-remediation (rewriting the offending content)
- **Out of scope:** external scanner binaries or non-stdlib Python dependencies
- **Open question:** should the secret rule table later absorb provider-specific additions
  (Stripe live keys, npm tokens, HuggingFace, Azure SAS)? Owner decides post-ship; the table is
  designed to take one-line additions.
- **Open question:** whether a PreToolUse variant (block the write before it lands) is worth a
  follow-up for `.env`-style paths. Deferred — PostToolUse + sweep satisfies the current ask.

## Follow-ups (from review advisories)

- [ ] Evaluate whether the `SubagentStop` sweep registration is redundant once the per-write gate
  and Bash tracking are live, and drop it if so — keeping a single `Stop` registration would
  simplify state ownership (Codex round 1, advisory).
- [ ] Refresh `ai-docs/anthropic/hooks.md` via `/harness-layer:kb` — the cached mirror's
  `.claude/hooks.json` config format, camelCase payloads, and exit-code table conflict with the
  hooks guide and the repo's working `.claude/settings.json` conventions (Codex round 2,
  advisory).

## KB References

- `ai-docs/anthropic/hooks-guide.md` (fetched 2026-07-05) — settings-style hook configuration,
  matcher table, exit-code semantics (exit 2 blocks PostToolUse/Stop and feeds stderr to Claude),
  fail-open guidance, `stop_hook_active` / 8-block cap, `additionalContext` injection, and the
  compliance-scanning recipe (Stop sweep + Bash matching with `git status --porcelain`).
- `ai-docs/anthropic/hooks.md` (fetched 2026-07-05) — event catalog and matcher availability
  (PostToolUse, PostToolUseFailure, Stop, SubagentStop, SessionStart), event payload schemas,
  timeout defaults. Caveat: where this mirror's config format or payload casing conflicts with
  the hooks guide, the guide and the repo's working `.claude/settings.json` conventions are the
  operative grounding (refresh queued in Follow-ups).
