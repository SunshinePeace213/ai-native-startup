# Spec: Security Scan Hook

- **Owner:** @SunshinePeace213
- **Status:** Drafted for Review
  <!-- Lifecycle, set by /harness-layer:harness-plan: Drafted for Review → Approved (on a Codex
       `approved` verdict). If round 2 is still changes-requested, the over-cap gate records the exit
       status in ## Codex Verification — approved | accepted-with-unverified-fixes | needs-human. One value only. -->

## Task Description

Agents in this repo write code, markdown, and config files as part of every build. Occasionally a
finished file contains a hardcoded secret (API key, token, private key, connection-string
credential) or a well-known vulnerable pattern (SQL built by f-string, `subprocess` with
`shell=True` and interpolation, unsafe `yaml.load`, `innerHTML =`). Nothing in the harness catches
this today. Build a security-scan hook family that checks agent-written content automatically:
a per-write gate that scans each file the moment an agent saves it, plus an end-of-turn sweep
that re-checks everything the agent touched (including files created through Bash) before the
agent is allowed to finish. Secret findings block until fixed; vulnerability findings warn.

## Objective

Every file an agent writes via Write/Edit/MultiEdit is scanned at write time, and every file an
agent creates or newly dirties through Bash is scanned by an end-of-turn sweep; a high-precision
secret finding blocks the agent — immediately at write time, and once more at turn end — with
file:line:rule feedback until the secret is removed or pragma-suppressed, so no secret passes
silently. Curated vulnerability patterns surface to the agent as non-blocking warnings. Two
documented limits: Bash edits to files already dirty at session start are not attributed (see
Non-Goals), and the Stop gate blocks at most once per turn without progress (per the KB-documented
`stop_hook_active` contract) — it guarantees loud, blocking diagnostics, not impossibility.

## Non-Goals

- Full SAST or dependency (CVE) scanning — deeper analysis stays with `/security-review`
- Scanning git history, or pre-existing files the agent never touched in the session
- Scanning files the user edits outside the session (baseline-dirty files are excluded)
- Auto-remediation — the hook reports; the agent fixes
- External scanner binaries (gitleaks, trufflehog, semgrep) — the ruleset is stdlib regex only
- Blocking on vulnerability heuristics — blocking is reserved for secret matches
- Attributing Bash edits to baseline-dirty files (files already uncommitted at SessionStart) —
  such a change cannot be told apart from the user's own concurrent edits without process-level
  attribution, and never flagging user-owned work is the design cornerstone; the per-write gate
  still covers Write/Edit on those same files
- An unbypassable Stop gate — the runtime overrides Stop blocks that repeat without progress, and
  the KB contract requires exiting early on `stop_hook_active`; the sweep blocks once with full
  diagnostics, it does not make stopping impossible

## Problem Statement

A leaked key in an agent-written file can land in a commit before any human reads the diff, and
multi-agent builds multiply the number of unreviewed writes. The repo already proves the right
enforcement seam: the auto-format hooks intercept every Write/Edit and feed exit-2 diagnostics
back to the agent, which fixes them immediately. Security scanning is the missing guard at that
same seam — deterministic, per-write, and impossible for the agent to forget to run.

## Solution Approach

A new hook family at `.claude/hooks/security-scan/`, mirroring the auto-format conventions
(`uv run --script` entry points, stdlib-only, fail-open on all plumbing, exit 2 only on confirmed
findings, diagnostics capped):

1. **Per-write gate** — `PostToolUse` on `Write|Edit|MultiEdit` scans the just-written file.
   Secret findings → exit 2 with `file:line rule` diagnostics on stderr (fed back to the agent).
   Vulnerability findings alone → exit 0 with a `hookSpecificOutput.additionalContext` warning on
   stdout so the agent sees it without being blocked.
2. **Session tracking** — `SessionStart` records a baseline of already-dirty files
   (`git status --porcelain`) so the user's own uncommitted work is never flagged. The per-write
   gate records each scanned path; the Bash tracker — registered on BOTH `PostToolUse` and
   `PostToolUseFailure` for `Bash`, since a command can write a file and then exit non-zero —
   adds newly dirty files (current dirty set minus baseline) so shell-created files (`echo >`,
   heredoc) are covered. The session state also carries the last-seen git HEAD (recorded at
   SessionStart, advanced by the tracker), and the tracker unions in
   `git diff --name-only <last-head>..HEAD` whenever HEAD moved, so files written **and
   committed** within a single Bash invocation are tracked even though the tree ends clean.
   Bash edits to baseline-dirty files stay excluded by design (see Non-Goals — attribution is
   impossible and user files must never be flagged). State lives in
   `.claude/.security-scan/<session_id>.json` (gitignored).
3. **End-of-turn sweep** — `Stop` + `SubagentStop` re-scan every tracked file that still exists;
   any secret finding blocks the turn from ending (exit 2) with full diagnostics. Per the KB
   `stop_hook_active` contract, when the payload carries `stop_hook_active: true` the sweep exits
   0 after printing a final loud warning — it blocks at most once per turn without progress, so
   it never fights the runtime's block cap. Only the tracked set is swept — never the whole
   working tree.
4. **False-positive escape** — an inline `security-scan: allow` pragma on (or immediately above)
   the flagged line suppresses it, and placeholder values (`example`, `changeme`,
   `your-key-here`, `xxx…`) are auto-skipped by the scanner.

Main alternative considered: per-write gate only (simplest, matches auto-format exactly). Lost
because the owner chose full coverage — the sweep closes the Bash-created-file gap, and the
session baseline neutralizes the sweep's false-positive hazard on user-owned dirty files.

## Requirements & Decisions

- **Two-layer trigger, per-write + sweep** — immediate feedback at the moment of the mistake,
  plus a completion gate that also covers Bash-created and newly dirtied files (baseline-dirty
  paths excluded; see Non-Goals). Owner-selected over per-write-only.
- **Secrets block (exit 2), vulnerabilities warn (exit 0 + additionalContext)** — blocking is
  reserved for high-precision matches; heuristics must never wedge legitimate work.
- **Suppression = inline pragma + placeholder heuristics** — visible in diffs where it happens;
  no central allowlist file to drift.
- **Repo hook conventions are binding** — `uv run --script`, stdlib-only, fail-open plumbing,
  capped diagnostics, registered in the tracked `.claude/settings.json`.

## Tracking

<!-- Recorded by /harness-layer:harness-plan. The Issue field is the SINGLE SOURCE OF TRUTH
     /harness-layer:harness-build reads — it NEVER re-derives #N from the local `worktree-<slug>`
     branch name. spec.md is the single home for this block; decisions.md does not duplicate it. -->

- **Issue:** #21
- **Branch:** feat/21-security-scan-hook
- **Worktree:** /home/ringo/ai-native-startup/.claude/worktrees/security-scan-hook
- **Review profile:** kb-grounded
- **PR:** <#M — filled by /harness-layer:harness-build>

## Relevant Files

Use these files to complete the task:

- `.claude/settings.json` — register the six hook entries (PostToolUse ×2, PostToolUseFailure Bash, SessionStart, Stop, SubagentStop)
- `.claude/hooks/auto-format/_common.py` — the reference implementation of the repo's fail-open
  helper idioms (bounded stdin read, `note()`, vendored-dir skip, diagnostic capping) to mirror
- `.claude/hooks/block_attribution.py` — reference for the exit-2 + stderr-policy-message idiom
- `.gitignore` — add the `.claude/.security-scan/` state directory
- `HARNESS-LAYER.md` — document the new hook family alongside the auto-format hooks
- `tests/harness-layer/` — home for the new test modules

### New Files

- `.claude/hooks/security-scan/_common.py` — scanner engine: secret/vuln rule tables, `scan_file()`,
  pragma + placeholder suppression, binary/vendored/size guards, session-state read/write helpers
- `.claude/hooks/security-scan/post_write_scan.py` — PostToolUse gate for `Write|Edit|MultiEdit`
- `.claude/hooks/security-scan/session_baseline.py` — SessionStart baseline recorder (+ stale-state pruning)
- `.claude/hooks/security-scan/track_bash_writes.py` — PostToolUse Bash tracker (never blocks)
- `.claude/hooks/security-scan/stop_sweep.py` — Stop/SubagentStop sweep over the tracked set
- `tests/harness-layer/test_security_scan_engine.py` — unit tests for the engine (rules, suppression, guards)
- `tests/harness-layer/test_security_scan_hooks.py` — subprocess end-to-end tests piping hook payloads

## Edge Cases

- Empty, malformed, or timed-out stdin payload → exit 0 silently (fail-open, matching `_common.read_payload`)
- Target file deleted before the scan runs → skip with a stderr note, exit 0
- Binary file (null byte in the first 8 KiB) → skip silently
- Vendored path (`node_modules`, `.venv`, `dist`) → skip silently
- Oversized file → scan only the first 1 MiB and note the truncation; never hang on huge files
- Not a git repo, or `git` unavailable → baseline is empty and Bash tracking is skipped with a note;
  the sweep still covers Write/Edit-tracked files
- Unborn HEAD (no commits yet) or missing stored last-head → skip the commit-diff union with a
  note; dirty-set tracking still applies
- Stored last-head unreachable (history rewritten mid-session) → the commit diff fails open with
  a note and last-head resets to current HEAD
- Corrupt or missing session-state file → treated as empty (sweep passes; tracking restarts)
- Concurrent sessions/worktrees → state keyed by `session_id` under each project dir; no sharing
- Stop-loop safety → the sweep parses `stop_hook_active` per the KB guide: false/absent → block
  (exit 2) on secret findings; true → print a final loud warning and exit 0. It blocks at most
  once per turn without progress, so the runtime's 8-block override never has to engage
- Re-run idempotency → scanning is pure (same content, same findings); tracked paths are deduped

## Red Flags

<anti-patterns signalling the plan is being skipped or scope is drifting. Keep these standing examples; add task-specific ones:>

- Starting to write code without any written requirements
- Asking "should I just start building?" before clarifying what "done" means
- Implementing features not mentioned in any spec or task list
- Making architectural decisions without documenting them
- Skipping the spec because "it's obvious what to build"
- Adding an external scanner binary or a non-stdlib Python dependency
- Making vulnerability heuristics blocking, or exit 2 on a plumbing failure
- Sweeping the whole working tree (or `git status` output directly) instead of the tracked set
- Widening the global pytest timeout or adding flake-retry behavior to the new tests

## Notes

- No new libraries: the scripts are `uv run --script` with `dependencies = []`, matching the
  existing hooks.
- The vuln-warn channel (`hookSpecificOutput.additionalContext` on PostToolUse stdout, exit 0) is
  the KB-documented non-blocking path; the build's e2e task verifies the JSON shape lands on
  stdout. If a runtime version ignores it, warnings degrade silently — acceptable, since warnings
  are advisory by decision.
- Follow-up candidates live in decisions.md → Open Questions (e.g. rule-table extensions).

## Codex Verification

<!-- CLAUDE-OWNED. The outcome summary Claude records after the Codex loop. -->

- **Outcome:** <approved at round N | accepted-with-unverified-fixes | needs-human>
- **Rejected findings:** <any Codex finding Claude chose not to act on, each with a one-line rationale; "none" if all warranted findings were applied>

## References

<a tree of the sibling plan files and their purpose, so the four files trace to each other:>

```text
specs/security-scan-hook/
├── spec.md                 # this file — what & why, tracking, review record
├── decisions.md            # grilling record: resolved decisions, assumptions, out-of-scope
├── tasks.md                # how & who: phases, team, step-by-step tasks
└── acceptance-criteria.md  # done: acceptance criteria + validation commands
```

## Self Validation

- [x] Objective, Task Description, and Non-Goals are filled in (no placeholders left)
- [x] Requirements trace to tasks in tasks.md and to checks in acceptance-criteria.md
- [x] Acceptance criteria are specific and testable
- [x] All four files exist under specs/security-scan-hook/ and are saved in the repository
- [ ] Codex has reviewed the spec and Status reflects the outcome
