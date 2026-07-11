# Tasks: Security Scan Hook

> Execution plan for [spec.md](./spec.md). Owner and scope are defined there; this file is how & who.

## Implementation Phases

### Phase 1: Foundation

The scanner engine everything else imports: rule tables (secrets → block, vulns → warn),
`scan_file()`, pragma + placeholder suppression, binary/vendored/size guards, and session-state
helpers — with unit tests proving every rule and every suppression path.

### Phase 2: Core Implementation

The four hook entry points built on the engine: the per-write gate, the SessionStart baseline
recorder, the Bash write-tracker, and the Stop/SubagentStop sweep — each an `uv run --script`
file mirroring the auto-format hooks' fail-open idioms.

### Phase 3: Integration & Polish

Registration in `.claude/settings.json`, the `.gitignore` state-dir entry, a HARNESS-LAYER.md
section documenting the family, and full validation against acceptance-criteria.md.

## Team Orchestration

- You operate as the team lead and orchestrate the team to execute the plan.
- IMPORTANT: You NEVER operate directly on the codebase. You use the `Task*` tools to deploy team
  members to build, validate, test, and deploy. Your job is to direct, not to build.
- Keep the shared task list (TaskCreate/TaskUpdate) as the single source of truth for who is doing
  what; verify each task on the board before marking it complete.
- Note the session id / name of each team member — that is how you reference them.

## Team Members

- **Builder**
  - **Name:** builder-scanner
  - **Role:** Scanner engine (`_common.py`) and its unit tests — rules, suppression, guards, state helpers
  - **Agent Type:** general-purpose
  - **Resume:** true
- **Builder**
  - **Name:** builder-hooks
  - **Role:** The four hook entry-point scripts, settings.json registration, gitignore, and docs
  - **Agent Type:** general-purpose
  - **Resume:** true
- **Builder**
  - **Name:** validator
  - **Role:** Runs every validation command and verifies each acceptance criterion end to end
  - **Agent Type:** general-purpose
  - **Resume:** false

## Step by Step Tasks

- Execute every step in order, top to bottom. Each task maps directly to one `TaskCreate` call.
- Before starting, run `TaskCreate` for every task below so all team members can see the board.
- Each task names the acceptance criteria (from acceptance-criteria.md) it satisfies, so work traces to "done".

### 1. Build the scanner engine

- **Task ID:** scanner-core
- **Depends On:** none
- **Assigned To:** builder-scanner
- **Agent Type:** general-purpose
- **Model / Effort:** `opus` / `high`
- **Parallel:** false
- **Satisfies:** AC1, AC2, AC3 (engine halves), AC7
- Create `.claude/hooks/security-scan/_common.py` mirroring the fail-open idioms of
  `.claude/hooks/auto-format/_common.py` (bounded stdin read, `note()`, vendored skip, capped
  diagnostics) — self-contained, no cross-directory import.
- Implement the table-driven **secret rules** (severity `block`): AWS access-key IDs
  (`AKIA`/`ASIA`-class), GitHub tokens (`ghp_`/`gho_`/`ghu_`/`ghs_`/`ghr_`/`github_pat_`), Slack
  (`xox[baprs]-`), OpenAI (`sk-`/`sk-proj-`), Anthropic (`sk-ant-`), Google (`AIza…`),
  PEM private-key blocks, three-part JWTs, connection-string credentials (`scheme://user:pass@`),
  and generic hardcoded credential assignments (`api_key|secret|token|password = "…"` with a
  value ≥8 chars).
- Implement the curated **vulnerability rules** (severity `warn`): `subprocess` with `shell=True`
  plus interpolation, `pickle.load(s)`, `yaml.load` without a `SafeLoader`, SQL execute on an
  f-string/concat, `eval`/`exec` on a non-literal, `innerHTML =`, `document.write(`,
  `dangerouslySetInnerHTML`, `child_process.exec` with a template literal.
- Implement suppression: inline `security-scan: allow` pragma (flagged line or the line above)
  and placeholder heuristics on the matched value (`example`, `sample`, `placeholder`,
  `changeme`, `your…`, `dummy`, `fake`, `xxx`, `redacted`, `<…>`, all-same-char).
- Implement guards: skip binary (null byte in first 8 KiB), vendored dirs, missing files; cap the
  scan at 1 MiB with a truncation note.
- Implement session-state helpers: read/write `.claude/.security-scan/<session_id>.json`
  (baseline set + tracked set, deduped), corrupt-file-as-empty, prune state files older than 7 days.
- Write `tests/harness-layer/test_security_scan_engine.py`: at least one positive and one negative
  case per rule, every suppression path, every guard — parallel-safe (`tmp_path` only).

### 2. Build the per-write gate

- **Task ID:** post-write-hook
- **Depends On:** scanner-core
- **Assigned To:** builder-hooks
- **Agent Type:** general-purpose
- **Model / Effort:** `sonnet` / `medium`
- **Parallel:** true (alongside session-tracking)
- **Satisfies:** AC1, AC2, AC6
- Create `post_write_scan.py` (`uv run --script`, `dependencies = []`): parse the PostToolUse
  payload, extract `tool_input.file_path`, scan via the engine, and append the path to the
  session tracked set.
- Secret findings → print capped `file:line rule` diagnostics to stderr, exit 2 (include vuln
  findings in the same report when both exist — never mix exit 2 with stdout JSON).
- Vuln findings only → exit 0 and print `{"hookSpecificOutput": {"hookEventName": "PostToolUse",
  "additionalContext": "…"}}` to stdout.
- Fail-open everywhere: no payload, missing file, engine error → exit 0 (stderr note for
  unexpected errors only).

### 3. Build session tracking

- **Task ID:** session-tracking
- **Depends On:** scanner-core
- **Assigned To:** builder-hooks
- **Agent Type:** general-purpose
- **Model / Effort:** `sonnet` / `medium`
- **Parallel:** true (alongside post-write-hook)
- **Satisfies:** AC4, AC6
- Create `session_baseline.py` (SessionStart): record `git status --porcelain` paths as the
  baseline set in the session state file; prune stale state files; exit 0 always (note when git
  is unavailable).
- Create `track_bash_writes.py` (PostToolUse on Bash): compute current dirty set, subtract the
  baseline, union the remainder into the tracked set; never blocks, exit 0 always.
- Honor the documented exclusion: baseline-dirty files are never added by this hook, even if a
  Bash call modifies them (see decisions.md — attribution is impossible and user-owned changes
  must never be flagged).

### 4. Build the end-of-turn sweep

- **Task ID:** stop-sweep
- **Depends On:** post-write-hook, session-tracking
- **Assigned To:** builder-hooks
- **Agent Type:** general-purpose
- **Model / Effort:** `sonnet` / `medium`
- **Parallel:** false
- **Satisfies:** AC5, AC6
- Create `stop_sweep.py` (Stop + SubagentStop): load the tracked set, re-scan each file that
  still exists, and on any secret finding print capped diagnostics to stderr and exit 2 to block
  the turn from ending; exit 0 when clean.
- Parse `stop_hook_active` per the KB contract: when true, print a final loud warning naming the
  surviving findings and exit 0 — the sweep blocks at most once per turn without progress.
- Fail-open: missing/corrupt state, git-less environment, engine error → exit 0.
- Write `tests/harness-layer/test_security_scan_hooks.py`: subprocess end-to-end tests piping
  payload JSON into all four scripts (block, warn, suppress, track, sweep-block-then-pass,
  fail-open) — parallel-safe, each test isolated in `tmp_path` with its own fake project dir.

### 5. Register hooks and document

- **Task ID:** register-and-docs
- **Depends On:** post-write-hook, session-tracking, stop-sweep
- **Assigned To:** builder-hooks
- **Agent Type:** general-purpose
- **Model / Effort:** `sonnet` / `low`
- **Parallel:** false
- **Satisfies:** AC8
- Add the five entries to `.claude/settings.json` following the existing shape: PostToolUse
  `Write|Edit|MultiEdit` → `post_write_scan.py`; PostToolUse `Bash` → `track_bash_writes.py`;
  `SessionStart` → `session_baseline.py`; `Stop` and `SubagentStop` → `stop_sweep.py`.
- Add `.claude/.security-scan/` to `.gitignore`.
- Add a brief HARNESS-LAYER.md section for the security-scan family (what fires when, exit
  semantics, the pragma) matching the doc's existing tone.

### 6. Validate Everything

- **Task ID:** validate-all
- **Depends On:** scanner-core, post-write-hook, session-tracking, stop-sweep, register-and-docs
- **Assigned To:** validator
- **Agent Type:** general-purpose
- **Model / Effort:** `sonnet` / `high`
- **Parallel:** false
- Run every command in acceptance-criteria.md → `## Validation Commands`.
- Verify each acceptance criterion is met.
