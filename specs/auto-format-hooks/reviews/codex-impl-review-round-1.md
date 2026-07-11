### Round 1 — Verdict: changes-requested

Scope: full
Base SHA: 669ceace20877c3120f39da9e5b88aae26a1a5f7
Reviewed head SHA: 1c6b8ceb8f23bd7a53f62137f1b46def45a6dc2c
Mode: spawn (6 selected lenses, 2,546 changed lines, 29 files, executable hook code)
Profile: kb-grounded
Lenses: plan-adherence, KB-grounding, review-code-standards, review-silent-failure, review-type-design, review-test-coverage, review-comment-accuracy, review-simplification | skipped: none. Expected-list disagreement: added advisory review-simplification because the packet did not state that a tidy pass already ran.
Validation:
- `bun install && ls node_modules/.bin/eslint node_modules/.bin/prettier node_modules/.bin/markdownlint-cli2` -> PASS
- `printf 'const x:number=1\nexport default x\n' > /tmp/ac1-fixture.tsx && node_modules/.bin/eslint --fix /tmp/ac1-fixture.tsx && echo ok; rm -f /tmp/ac1-fixture.tsx` -> PASS (printed `ok`; ESLint also warned the `/tmp` fixture was outside the base path)
- `uv run pytest -q` -> PASS with `UV_CACHE_DIR=/tmp/uv-cache` in the managed review sandbox (`71 passed in 15.62s`). Ambient first run failed before tests because `/home/ringo/.cache/uv` is read-only in this sandbox.
- `uv run python -c "import json; d=json.load(open('.claude/settings.json')); ks=d['hooks']; assert len(ks['PostToolUse'])>=1 and 'WorktreeCreate' in ks and 'WorktreeRemove' in ks; print('ok')"` -> PASS with `UV_CACHE_DIR=/tmp/uv-cache`. Ambient first run hit the same read-only uv cache failure.
- `test "$(grep -c 'auto-format' .claude/settings.json)" -ge 6 && echo ok` -> PASS
- `test ! -f .claude/commands/meta-install.md && test -f .claude/skills/meta-install/SKILL.md && echo ok` -> PASS
- `grep -q 'auto-format' HARNESS-LAYER.md && ! grep -q '/meta-install' AGENTS.md && ! git grep -q 'install_deps' -- ':!specs' && echo ok` -> PASS

Digest: 3 blocking findings — 2 fail-open/exit-code contract defects and 1 WorktreeCreate path contract defect. KB grounding found no documentation contradiction in the registered settings.json hook shape, matcher use, exit-2 behavior, or dual worktree payload shape.

Findings:

**Plan adherence / review-type-design / review-code-standards**
- **WorktreeCreate accepts raw path-shaped names and can escape `.claude/worktrees`.** `.claude/hooks/auto-format/worktree_create.py:56` reads `worktreeName`/`name` verbatim and `.claude/hooks/auto-format/worktree_create.py:63` joins it with `root / ".claude" / "worktrees" / name`. In Python, an absolute `name` discards the managed prefix, and traversal segments can also leave the intended directory. This violates AC7 and `tasks.md` step 4, which require creation at `<root>/.claude/worktrees/<name>` on branch `worktree-<name>`. Fix: validate the lifecycle name as a single relative worktree name before deriving both `worktree` and `branch` (reject absolute paths, separators, `.`/`..`, and traversal).

**Plan adherence / review-code-standards / review-test-coverage**
- **The Python hook does not name the `meta-install` skill when Ruff is missing from the project environment.** `.claude/hooks/auto-format/python.py:52` reports `ruff (via uv) exited 2: ... Failed to spawn: ruff ...` and exits 0, but the note does not name `meta-install`. AC6 and `spec.md` Edge Cases require missing formatter binaries to fail open with a one-line stderr note naming the `meta-install` skill. I reproduced this with a temporary project containing no Ruff dependency. Fix: treat `uv run --no-sync ruff ...` spawn failures as missing toolchain and reuse the `meta-install` guidance; add a test that asserts the note contains `meta-install` when Ruff is absent but `uv` is present.

**Plan adherence / review-comment-accuracy**
- **The data hook misclassifies Prettier configuration failures as parse errors and exits 2.** `.claude/hooks/auto-format/data.py:39` says Prettier parse errors name the offending file, then `.claude/hooks/auto-format/data.py:41` treats any stderr line containing `path.name` as a real data defect. Prettier configuration errors also name the target file; I reproduced an invalid `.prettierrc` case where a valid `sample.json` produced `Invalid configuration for file ".../sample.json"` and exit 2. This violates the fail-open decision in `decisions.md` Summary and `tasks.md` step 3, where infrastructure failures must exit 0. Fix: distinguish actual JSON/YAML parse diagnostics from Prettier configuration/tooling errors before returning exit 2; otherwise note and exit 0.

**KB grounding**
- No blocking KB-grounding findings. The implementation uses the cached `settings.json` hook shape from `ai-docs/anthropic/hooks-guide.md` (`tool_input.file_path`, tool-name matchers, exit 2 feedback), registers WorktreeCreate/WorktreeRemove without matchers per the matcher table, and accepts both documented and live/reference lifecycle payload shapes as required by the plan.

**Advisory / non-blocking**
- `tests/harness-layer/hooks/test_python.py:test_missing_toolchain_fails_open_untouched` covers fail-open but not the required `meta-install` note for the "uv present, Ruff absent" case; this is covered by the blocking Python-hook finding above.
- `.claude/hooks/auto-format/worktree_remove.py:27` accepts any registered worktree path from the payload. AC8 says to remove the supplied path and only delete `worktree-*` branches, so this is not a blocker, but constraining removal to hook-managed paths would reduce blast radius if the payload is ever malformed.
- `.claude/hooks/auto-format/data.py:49` and the other hook footers duplicate the same fail-open `try` block; a shared helper could reduce repetition without changing behavior.
- `tests/harness-layer/hooks/test_data.py:14` and sibling formatter tests duplicate `edit_payload` / `env_for` helpers; moving them to `conftest.py` would simplify the suite.
