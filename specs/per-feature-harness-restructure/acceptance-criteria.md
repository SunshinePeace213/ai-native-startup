# Acceptance Criteria: Per-feature harness restructure — hooks, tests, build workflow

> The definition of "done" for [spec.md](./spec.md). Every criterion is observable and testable, and
> every task in tasks.md should map to at least one criterion here.

## Acceptance Criteria

- **AC1** — Per-feature test selection works and nothing is lost: each of
  `tests/harness-layer/hooks/{auto-format,attribution,worktree,security-scan}/` collects only its
  own feature's tests, the full suite still collects 172 tests, and all pass. No `__init__.py`
  files; every test basename unique.
- **AC2** — Worktree is a real hook feature: `worktree_create.py`, `worktree_remove.py`, and a
  trimmed `_common.py` (exactly `note`, `read_payload`, `resolve_root`, `run`, `tail`) live under
  `.claude/hooks/worktree/`; no `worktree_*` files remain under `auto-format/`; the hermetic
  worktree tests pass against the new location with the scripts' code unchanged.
- **AC3** — `settings.json` is consolidated and repointed: exactly one PostToolUse block with
  matcher `Write|Edit|MultiEdit` holding all five commands, exactly one PostToolUse `Bash` block,
  and the WorktreeCreate/WorktreeRemove commands referencing `.claude/hooks/worktree/`.
- **AC4** — `harness-build.md` encodes the five upgrades: no hardcoded `sonnet` fixer (model +
  effort per issue difficulty via the AGENTS.md table); parallel background fixers for
  file-disjoint finding clusters with exactly one fix commit; concurrent launch of unblocked,
  file-disjoint implement tasks; manifest keyed by kebab-case Task ID with an explicit "never
  `#N`" note; `gh pr create` with `--assignee` and the issue's mirrored type + priority labels.
- **AC5** — Memory is in sync: HARNESS-LAYER.md's files tree matches the real `.claude/hooks/` and
  `tests/harness-layer/` layout, its Worktree Lifecycle section points at
  `.claude/hooks/worktree/`, and it carries the one-matcher-block rule; AGENTS.md Python Testing
  carries the per-feature run line.

## Validation Commands

Run these to prove the criteria above. Map each command to the criteria it verifies.

- `uv run pytest` — verifies AC1/AC2. Pass: 172 passed, 0 failed, 0 errors.
- `uv run pytest tests/harness-layer/hooks/worktree --collect-only -q | tail -1` — verifies AC1.
  Pass: only the worktree test count (no other features); repeat per feature dir.
- `find tests/harness-layer -name "__init__.py" | wc -l` — verifies AC1. Pass: `0`.
- `ls .claude/hooks/worktree/` — verifies AC2. Pass: exactly `_common.py worktree_create.py worktree_remove.py`.
- `ls .claude/hooks/auto-format/ | grep -c worktree` — verifies AC2. Pass: `0` (exit 1 from grep is the pass signal).
- `jq -e '[.hooks.PostToolUse[] | select(.matcher == "Write|Edit|MultiEdit")] | length == 1' .claude/settings.json` — verifies AC3. Pass: `true`.
- `jq -e '[.hooks.PostToolUse[] | select(.matcher == "Write|Edit|MultiEdit")][0].hooks | length == 5' .claude/settings.json` — verifies AC3. Pass: `true`.
- `jq -e '.hooks.WorktreeCreate[0].hooks[0].command | contains("hooks/worktree/worktree_create.py")' .claude/settings.json` — verifies AC3. Pass: `true`.
- `jq -e '.hooks.WorktreeRemove[0].hooks[0].command | contains("hooks/worktree/worktree_remove.py")' .claude/settings.json` — verifies AC3. Pass: `true`.
- `grep -c "sonnet\` fixer" .claude/commands/harness-layer/harness-build.md` — verifies AC4. Pass: `0` (no hardcoded sonnet fixer phrasing remains).
- `grep -q "never \`#N\`" .claude/commands/harness-layer/harness-build.md && echo ok` — verifies AC4. Pass: `ok`.
- `grep -q -- "--assignee" .claude/commands/harness-layer/harness-build.md && echo ok` — verifies AC4. Pass: `ok`.
- `grep -q "one matcher block per event+matcher" HARNESS-LAYER.md && echo ok` — verifies AC5. Pass: `ok`.
- `grep -q "tests/harness-layer/hooks/<feature>" AGENTS.md && echo ok` — verifies AC5. Pass: `ok`.
- `grep -q "hooks/worktree/" HARNESS-LAYER.md && echo ok` — verifies AC5. Pass: `ok`.
