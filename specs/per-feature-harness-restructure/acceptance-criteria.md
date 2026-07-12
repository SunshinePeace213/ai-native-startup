# Acceptance Criteria: Per-feature harness restructure — hooks, tests, build workflow

> The definition of "done" for [spec.md](./spec.md). Every criterion is observable and testable, and
> every task in tasks.md should map to at least one criterion here.

## Acceptance Criteria

- **AC1** — Per-feature test selection works and nothing is lost: each of
  `tests/harness-layer/hooks/{auto-format,attribution,worktree,security-scan}/` collects only its
  own feature's tests, the four dirs together collect all 172 tests, and the full suite passes.
  No `__init__.py` files; every test basename unique.
- **AC2** — Worktree is a real hook feature: `worktree_create.py` and `worktree_remove.py` move
  byte-identical (rename-only) to `.claude/hooks/worktree/`; the new `_common.py` there exposes
  exactly the five helpers `note`, `read_payload`, `resolve_root`, `run`, `tail` plus the
  `STDIN_TIMEOUT = 5.0` constant and nothing else — the exact surface is AST-asserted by
  [validate.py](./validate.py), which rejects any extra function, constant, or class; no
  `worktree_*` files remain under `auto-format/`; the hermetic worktree tests pass against the
  new location.
- **AC3** — `settings.json` is consolidated and repointed: exactly one PostToolUse block with
  matcher `Write|Edit|MultiEdit` whose `hooks` array holds exactly the five known commands
  (js_ts, data, markdown, python, post_write_scan); exactly one PostToolUse `Bash` block; the
  WorktreeCreate/WorktreeRemove commands reference `.claude/hooks/worktree/`.
- **AC4** — `harness-build.md` encodes the five upgrades as complete clause relationships,
  asserted by [validate.py](./validate.py): fixer MODEL per issue difficulty via the Agent tool's
  `model` param with the effort tier stated in the task brief and inherited session reasoning
  effort (old "fixer subagent (effort per issue)" phrasing gone; no effort key on any Agent
  deployment); parallel background fixers for disjoint clusters with exactly ONE fix commit;
  concurrent launch of unblocked, file-disjoint tasks; manifest keyed by kebab-case Task ID with
  the GitHub-autolinks warning; `gh pr create` with `--assignee` and the issue's mirrored type +
  `priority:P<n>` labels read via `--json labels`.
- **AC5** — Memory is in sync: HARNESS-LAYER.md's files tree matches the real `.claude/hooks/` and
  `tests/harness-layer/` layout, its Worktree Lifecycle section points at
  `.claude/hooks/worktree/`, and it carries the one-matcher-block rule; AGENTS.md Python Testing
  carries the per-feature run line.

## Validation Commands

Run these to prove the criteria above from the repo root. Every command is self-contained. The
prose-heavy contracts (AC2 module surface, AC4 clause relationships) are asserted by the
checked-in validator, which reports each missing clause by name.

### AC1 — per-feature selection, nothing lost

- `uv run pytest` — full suite. Pass: 172 passed, 0 failed/errors.
- `uv run pytest tests/harness-layer/hooks/auto-format tests/harness-layer/hooks/attribution tests/harness-layer/hooks/worktree tests/harness-layer/hooks/security-scan --collect-only -q | tail -1` — pass: 172 tests collected (the four dirs hold everything).
- `uv run pytest tests/harness-layer/hooks/worktree --collect-only -q | head -5` — pass: every collected id starts with `tests/harness-layer/hooks/worktree/`; repeat per feature dir.
- `find tests/harness-layer -name "__init__.py"` — pass: no output.
- `find tests/harness-layer -name 'test_*.py' -printf '%f\n' | sort | uniq -d` — pass: no output (basenames unique).

### AC2 — worktree feature dir

- `uv run python specs/per-feature-harness-restructure/validate.py` — pass: exit 0 with "spec validation OK". Asserts (via AST) that `.claude/hooks/worktree/_common.py` defines exactly `note`, `read_payload`, `resolve_root`, `run`, `tail`, exactly the constant `STDIN_TIMEOUT = 5.0`, and no classes — any extra symbol fails with a named message. (Also asserts all AC4 clauses; listed once more below.)
- `git diff --name-status -M100% origin/main...HEAD -- .claude/hooks | grep -E '^R100'` — pass: exactly two lines, the R100 (byte-identical) renames of `worktree_create.py` and `worktree_remove.py`.
- `ls .claude/hooks/worktree/` — pass: exactly `_common.py worktree_create.py worktree_remove.py`.
- `ls .claude/hooks/auto-format/ | grep worktree` — pass: no output (grep exit 1).
- `uv run pytest tests/harness-layer/hooks/worktree` — pass: all worktree tests green against the new paths.

### AC3 — settings.json consolidated and repointed

- `jq -e '[.hooks.PostToolUse[] | select(.matcher == "Write|Edit|MultiEdit")] | length == 1' .claude/settings.json` — pass: `true` (one consolidated block).
- `jq -r '[.hooks.PostToolUse[] | select(.matcher == "Write|Edit|MultiEdit")][0].hooks[].command' .claude/settings.json` — pass: exactly five lines, one ending in each of `auto-format/js_ts.py`, `auto-format/data.py`, `auto-format/markdown.py`, `auto-format/python.py`, `security-scan/post_write_scan.py`.
- `jq -e '[.hooks.PostToolUse[] | select(.matcher == "Bash")] | length == 1' .claude/settings.json` — pass: `true` (the bash tracker stays its own block).
- `jq -e '.hooks.WorktreeCreate[0].hooks[0].command | contains("hooks/worktree/worktree_create.py")' .claude/settings.json` — pass: `true`.
- `jq -e '.hooks.WorktreeRemove[0].hooks[0].command | contains("hooks/worktree/worktree_remove.py")' .claude/settings.json` — pass: `true`.

### AC4 — harness-build.md upgrades (validator-asserted relationships)

- `uv run python specs/per-feature-harness-restructure/validate.py` — pass: exit 0. One check per
  clause; ALL of a clause's required terms must co-occur inside a SINGLE markdown block (one
  bullet, heading, or paragraph — wrapped continuation lines stay in their block), so fragments
  scattered across unrelated sections never pass. Forbidden patterns are document-wide. The
  failing clause is named on miss:
  1. **fixer model routing** — one block containing "model", "per issue difficulty", and
     "`model` param"; "fixer subagent(s) (effort per issue)" forbidden anywhere.
  2. **effort mechanism** — one block containing "effort tier", "task brief", "inherit…", and
     "reasoning effort"; an `effort:`/`effort=` key within 80 chars after "Agent" forbidden
     anywhere (Codex's `model_reasoning_effort=` config line stays legitimate).
  3. **parallel fix clusters** — one block containing "disjoint clusters", "parallel",
     "background fixer", and "ONE fix commit".
  4. **concurrent implement** — one block containing "unblocked", "file-disjoint tasks", and
     "concurrent*".
  5. **manifest key** — one block containing "kebab-case Task ID" and "GitHub autolinks".
  6. **PR metadata** — one block containing "gh pr create", "--assignee", "type label",
     "priority:P", and "--json labels" — assignee and both labels tied to the same
     `gh pr create` instruction.

### AC5 — memory sync

- `grep -q "one matcher block per event+matcher" HARNESS-LAYER.md && echo ok` — pass: `ok` (rule line present).
- `grep -q "hooks/worktree/" HARNESS-LAYER.md && echo ok` — pass: `ok` (Worktree Lifecycle repointed).
- `grep -q "tests/harness-layer/hooks/<feature>" AGENTS.md && echo ok` — pass: `ok` (per-feature run line).
- `ls tests/harness-layer/hooks/` vs the HARNESS-LAYER.md files tree — pass: the tree lists exactly the dirs that exist (manual eyeball, one screenful).
