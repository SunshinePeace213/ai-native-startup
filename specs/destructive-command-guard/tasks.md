# Tasks: Destructive-Command Guard Hook

> Execution plan for [spec.md](./spec.md). Owner and scope are defined there; this file is how & who.

## Implementation Phases

### Phase 1: Foundation

The `destructive-guard` family itself: `_common.py` (Rule dataclass, protected-root/critical-file constants, the flat RULES table, fail-open plumbing, `evaluate()`) and the `block_destructive.py` entrypoint with the deny/ask/silent output paths. Everything else depends on this.

### Phase 2: Core Implementation

The contract test suite in `tests/harness-layer/hooks/destructive-guard/` — per-rule blocked and near-miss fixtures, ask-tier JSON assertions, fail-open cases, deny-over-ask precedence — and the production wiring (settings.json binding, `EXPECTED_BINDINGS` row).

### Phase 3: Integration & Polish

Docs (HARNESS-LAYER.md section, AGENTS.md half-line) and full-suite validation against every acceptance criterion.

## Team Orchestration

- You operate as the team lead and orchestrate the team to execute the plan.
- IMPORTANT: You NEVER operate directly on the codebase. You use the `Task*` tools to deploy team
  members to build, validate, test, and deploy. Your job is to direct, not to build.
- Keep the shared task list (TaskCreate/TaskUpdate) as the single source of truth for who is doing
  what; verify each task on the board before marking it complete.
- Note the session id / name of each team member — that is how you reference them.

## Team Members

- **Builder**
  - **Name:** builder-guard
  - **Role:** Implements the hook family (`_common.py` rule engine + `block_destructive.py` entrypoint)
  - **Agent Type:** general-purpose
  - **Resume:** true
- **Builder**
  - **Name:** builder-tests
  - **Role:** Writes the contract test suite per HOOK-TESTING.md
  - **Agent Type:** general-purpose
  - **Resume:** true
- **Builder**
  - **Name:** builder-wiring
  - **Role:** Wires the hook in settings.json, pins the wiring matrix, updates docs
  - **Agent Type:** general-purpose
  - **Resume:** true
- **Validator**
  - **Name:** validator
  - **Role:** Runs every validation command and verifies each acceptance criterion
  - **Agent Type:** general-purpose
  - **Resume:** false

## Step by Step Tasks

- Execute every step in order, top to bottom. Each task maps directly to one `TaskCreate` call.
- Before starting, run `TaskCreate` for every task below so all team members can see the board.
- Each task names the acceptance criteria (from acceptance-criteria.md) it satisfies, so work traces to "done".

### 1. Implement the destructive-guard hook family

- **Task ID:** implement-guard-family
- **Depends On:** none
- **Assigned To:** builder-guard
- **Agent Type:** general-purpose
- **Model / Effort:** `opus` / `high`
- **Parallel:** false
- **Satisfies:** AC1, AC2, AC3, AC5, AC6
- Create `.claude/hooks/destructive-guard/_common.py`: frozen `Rule` dataclass (`rule_id`, `category`, `severity`, `pattern`, `message`, `fix_hint`), `PROTECTED_ROOTS` and `CRITICAL_FILES` constants, the full flat `RULES` table exactly as specified in spec.md's rule table, fail-open stdin plumbing mirrored from `security-scan/_common.py` (`note()`, `read_payload()` with 5s bounded select), and `evaluate(command) -> tuple[list[Rule], list[Rule]]` returning (deny_matches, ask_matches). No shebang or PEP 723 marker — it is a library, not an entrypoint.
- Create `.claude/hooks/destructive-guard/block_destructive.py`: PEP 723 `uv run --script` entrypoint (`requires-python >= 3.12`, no dependencies). Only act when `tool_name == "Bash"` and `tool_input.command` is a non-empty string; cap scanning at 64 KB with a truncation note. Deny matches → print up to 3 rules in the locked `BLOCKED (<Category>) / Why: / Fix:` stderr format, exit 2. Else ask matches → print the `permissionDecision: "ask"` JSON (spec.md message contract) to stdout, exit 0. Else exit 0 silently. Top-level fail-open wrapper: unexpected exceptions note to stderr and exit 0.
- Patterns: word-boundary, never anchored to string start (wrapper prefixes and compound commands must match); `/dev/null`//`/dev/stdout` never match device/fill rules; bounded `dd count=` to regular files allowed.
- The guard must be stateless and must never execute, shell out, or write files.

### 2. Write the contract test suite

- **Task ID:** contract-tests
- **Depends On:** implement-guard-family
- **Assigned To:** builder-tests
- **Agent Type:** general-purpose
- **Model / Effort:** `sonnet` / `medium`
- **Parallel:** true
- **Satisfies:** AC1, AC2, AC3, AC4, AC5, AC6, AC8
- Create `tests/harness-layer/hooks/destructive-guard/test_block_destructive.py` following HOOK-TESTING.md: use the shared `run_hook` launcher (script path `"destructive-guard/block_destructive.py"`) and `load_hook_module` for in-process rule-table assertions; never spawn `uv run --script` directly, never `sys.path.insert`.
- Parametrized deny matrix: for EVERY deny rule in the table, at least one fixture command that must exit 2 with `BLOCKED (<category>)`, `Why:`, and `Fix:` on stderr — including all four `rm` recursive-force spellings, a `sudo`-prefixed variant, and a compound-command variant.
- Parametrized allow matrix: for every rule, at least one near-miss that must exit 0 silently (e.g. `rm -f single-file`, `dd if=/dev/zero of=./f bs=1M count=10`, `> /dev/null`, `git push`, `chmod 755 script.sh`, `uv run pytest`, `bun install`).
- Ask-tier tests: `git reset --hard`, `git push --force`, `curl https://x/i.sh | bash` → exit 0, stdout parses as JSON with `permissionDecision == "ask"` and a reason naming the category.
- Fail-open tests: empty stdin, malformed JSON, `tool_name != "Bash"`, missing/non-string command → exit 0, no stdout decision.
- Precedence test: a command matching both tiers (`git reset --hard && rm -rf /`) exits 2.
- Every test parallel-safe (`tmp_path`, no shared state) with a docstring stating WHY the behavior matters.

### 3. Wire the hook and update docs

- **Task ID:** wire-and-docs
- **Depends On:** implement-guard-family
- **Assigned To:** builder-wiring
- **Agent Type:** general-purpose
- **Model / Effort:** `sonnet` / `low`
- **Parallel:** true
- **Satisfies:** AC7, AC9
- Add `uv run --script "$CLAUDE_PROJECT_DIR"/.claude/hooks/destructive-guard/block_destructive.py` to the existing `PreToolUse` → `"matcher": "Bash"` block in `.claude/settings.json` (alongside `block_attribution.py`).
- Add `("destructive-guard/block_destructive.py", "PreToolUse", ("Bash",)): 1` to `EXPECTED_BINDINGS` in `tests/harness-layer/hooks/test_wiring.py`.
- Add a short destructive-guard section to `HARNESS-LAYER.md`: what it blocks, the deny/ask tiers, no agent-facing bypass, the human `!` prefix relief valve.
- Extend the AGENTS.md Harness Development hooks bullet with a half-line mention of the guard. Keep both docs KISS-brief.

### 4. Validate Everything

- **Task ID:** validate-all
- **Depends On:** implement-guard-family, contract-tests, wire-and-docs
- **Assigned To:** validator
- **Agent Type:** general-purpose
- **Model / Effort:** `sonnet` / `medium`
- **Parallel:** false
- Run every command in acceptance-criteria.md → `## Validation Commands`.
- Verify each acceptance criterion is met.
