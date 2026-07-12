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
  `STDIN_TIMEOUT = 5.0` constant and nothing else; no `worktree_*` files remain under
  `auto-format/`; the hermetic worktree tests pass against the new location.
- **AC3** — `settings.json` is consolidated and repointed: exactly one PostToolUse block with
  matcher `Write|Edit|MultiEdit` whose `hooks` array holds exactly the five known commands
  (js_ts, data, markdown, python, post_write_scan); exactly one PostToolUse `Bash` block; the
  WorktreeCreate/WorktreeRemove commands reference `.claude/hooks/worktree/`.
- **AC4** — `harness-build.md` encodes the five upgrades, each provable by its anchor phrase:
  fixer MODEL per issue difficulty with the effort tier stated in the task brief (old
  "fixer subagent (effort per issue)" phrasing gone); parallel background fixers for disjoint
  clusters with exactly ONE fix commit; concurrent launch of unblocked, file-disjoint tasks;
  manifest keyed by kebab-case Task ID with the GitHub-autolinks warning; `gh pr create` with
  `--assignee` and the issue's mirrored type + `priority:P<n>` labels read via `--json labels`.
- **AC5** — Memory is in sync: HARNESS-LAYER.md's files tree matches the real `.claude/hooks/` and
  `tests/harness-layer/` layout, its Worktree Lifecycle section points at
  `.claude/hooks/worktree/`, and it carries the one-matcher-block rule; AGENTS.md Python Testing
  carries the per-feature run line.

## Validation Commands

Run these to prove the criteria above. Map each command to the criteria it verifies.
`BUILD_MD=.claude/commands/harness-layer/harness-build.md` in the AC4 commands.

### AC1 — per-feature selection, nothing lost

- `uv run pytest` — full suite. Pass: 172 passed, 0 failed/errors.
- `uv run pytest tests/harness-layer/hooks/auto-format tests/harness-layer/hooks/attribution tests/harness-layer/hooks/worktree tests/harness-layer/hooks/security-scan --collect-only -q | tail -1` — pass: 172 tests collected (the four dirs hold everything).
- `uv run pytest tests/harness-layer/hooks/worktree --collect-only -q | head -5` — pass: every collected id starts with `tests/harness-layer/hooks/worktree/`; repeat per feature dir.
- `find tests/harness-layer -name "__init__.py"` — pass: no output.
- `find tests/harness-layer -name 'test_*.py' -printf '%f\n' | sort | uniq -d` — pass: no output (basenames unique).

### AC2 — worktree feature dir

- `grep -E '^def ' .claude/hooks/worktree/_common.py | sort` — pass: exactly five lines, defining `note`, `read_payload`, `resolve_root`, `run`, `tail` and nothing else.
- `grep -q '^STDIN_TIMEOUT = 5.0' .claude/hooks/worktree/_common.py && echo ok` — pass: `ok`.
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

### AC4 — harness-build.md upgrades (one anchor per clause)

- `! grep -q "fixer subagent (effort per issue)" $BUILD_MD && echo ok` — pass: `ok` (hardcoded-sonnet fixer phrasing removed; clause: fixer routing).
- `grep -q "per issue difficulty" $BUILD_MD && echo ok` — pass: `ok` (clause: model chosen per issue difficulty).
- `grep -q "disjoint clusters" $BUILD_MD && echo ok` — pass: `ok` (clause: parallel fixers on disjoint finding clusters).
- `grep -q "ONE fix commit" $BUILD_MD && echo ok` — pass: `ok` (clause: single fix commit preserved).
- `grep -q "file-disjoint tasks" $BUILD_MD && echo ok` — pass: `ok` (clause: concurrent unblocked implement tasks).
- `grep -q "kebab-case Task ID" $BUILD_MD && echo ok` — pass: `ok` (clause: manifest key).
- `grep -q "GitHub autolinks" $BUILD_MD && echo ok` — pass: `ok` (clause: the never-`#N` warning).
- `grep -q -- "--assignee" $BUILD_MD && echo ok` — pass: `ok` (clause: PR assignee).
- `grep -q "priority:P" $BUILD_MD && echo ok` — pass: `ok` (clause: priority label mirrored).
- `grep -q -- "--json labels" $BUILD_MD && echo ok` — pass: `ok` (clause: labels read from the issue).

### AC5 — memory sync

- `grep -q "one matcher block per event+matcher" HARNESS-LAYER.md && echo ok` — pass: `ok` (rule line present).
- `grep -q "hooks/worktree/" HARNESS-LAYER.md && echo ok` — pass: `ok` (Worktree Lifecycle repointed).
- `grep -q "tests/harness-layer/hooks/<feature>" AGENTS.md && echo ok` — pass: `ok` (per-feature run line).
- `ls tests/harness-layer/hooks/` vs the HARNESS-LAYER.md files tree — pass: the tree lists exactly the dirs that exist (manual eyeball, one screenful).
