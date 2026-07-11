### Round 2 — Verdict: changes-requested

Scope: delta
Base SHA: 669ceace20877c3120f39da9e5b88aae26a1a5f7
Reviewed head SHA: 6981a305e4dd421a33bfac50d88b3fdd2ed76cae
Mode: sequential (10 files, 253 changed lines; below spawn threshold)
Profile: kb-grounded
Lenses: plan-adherence, KB-grounding, review-code-standards, review-silent-failure, review-type-design, review-test-coverage, review-comment-accuracy | skipped: review-simplification — round-1 advisories are already tracked as follow-ups, no fallback needed
Validation:
- `bun install && ls node_modules/.bin/eslint node_modules/.bin/prettier node_modules/.bin/markdownlint-cli2` -> PASS
- `printf 'const x:number=1\nexport default x\n' > /tmp/ac1-fixture.tsx && node_modules/.bin/eslint --fix /tmp/ac1-fixture.tsx && echo ok; rm -f /tmp/ac1-fixture.tsx` -> PASS (printed `ok`; ESLint emitted the expected outside-base warning)
- `UV_CACHE_DIR=/tmp/uv-cache uv run pytest -q` -> PASS (`83 passed in 12.91s`)
- `UV_CACHE_DIR=/tmp/uv-cache uv run python -c "import json; d=json.load(open('.claude/settings.json')); ks=d['hooks']; assert len(ks['PostToolUse'])>=1 and 'WorktreeCreate' in ks and 'WorktreeRemove' in ks; print('ok')"` -> PASS
- `test "$(grep -c 'auto-format' .claude/settings.json)" -ge 6 && echo ok` -> PASS
- `test ! -f .claude/commands/meta-install.md && test -f .claude/skills/meta-install/SKILL.md && echo ok` -> PASS
- `grep -q 'auto-format' HARNESS-LAYER.md && ! grep -q '/meta-install' AGENTS.md && ! git grep -q 'install_deps' -- ':!specs' && echo ok` -> PASS
- `UV_CACHE_DIR=/tmp/uv-cache uv run ruff format --check .claude/hooks/auto-format tests/harness-layer/hooks && UV_CACHE_DIR=/tmp/uv-cache uv run ruff check .claude/hooks/auto-format tests/harness-layer/hooks` -> PASS
Prior blockers:
- CX-1 worktree_create path-shaped names escaping `.claude/worktrees` — fixed by rejecting absolute/path-separator/dot-segment names before deriving the path or branch, with regression coverage.
- CX-2 python.py missing `meta-install` note when uv cannot spawn ruff — fixed by treating uv exit 2 + `Failed to spawn` as missing toolchain, with regression coverage.
- CX-3 data.py misclassifying Prettier config failures as parse errors — fixed by requiring the filename and `SyntaxError` on the same stderr line, with regression coverage.
- INT-1 `.worktreeinclude` copy contract dropped — fixed in hook behavior by copying gitignored pattern matches after `git worktree add`, but the decisions prose still has one stale follow-up; see finding below.
- INT-2 worktree_remove.py leaks `worktree-*` branches when `$CLAUDE_PROJECT_DIR` is the removed worktree — fixed by resolving a durable repo cwd before removal, with regression coverage.

Prior advisory dispositions:
- CX-A1 meta-install-note test gap — fixed as part of CX-2.
- CX-A2 worktree_remove blast radius — not fixed; advisory follow-up only.
- CX-A3 duplicated fail-open footer — not fixed; advisory follow-up only.
- CX-A4 duplicated test helpers — not fixed; advisory follow-up only.
- INT-A3 KB async-vs-sync conflict on Worktree events — not fixed in code; KB refresh follow-up remains.
- INT-A4 commit subject length — not fixed in this delta.
- INT-A5 HARNESS-LAYER.md missing worktree-hook fail-open clause — not fixed in this delta.
- INT-A6 snake_case/dual-shape convention not promoted to HARNESS-LAYER.md — not fixed in this delta.

Digest: 1 blocking finding — the code fixes and tests cover the round-1 blockers, and validation is clean, but the decisions prose correction is incomplete: one follow-up still says `.worktreeinclude` handling is future work even though this delta implements it.

Findings:

**Plan adherence / review-comment-accuracy**
- **The `.worktreeinclude` prose correction is incomplete.** `specs/auto-format-hooks/decisions.md:50` now correctly says `.worktreeinclude` exists and the copy contract is implemented in `worktree_create.py`, but `specs/auto-format-hooks/decisions.md:55` still lists "`.worktreeinclude` handling in `worktree_create.py` if the file is ever added" as a future follow-up. That contradicts the delta's own correction and the KB-grounded WorktreeCreate claim in the packet that custom creation hooks must copy local configuration files themselves. Fix: remove the stale checklist item or replace it with a different unresolved follow-up.

**KB grounding**
- No blocking KB-grounding findings in the hook behavior. The delta remains consistent with the packet's cached-doc claims: WorktreeCreate owns default creation and `.worktreeinclude` copying; exit 2 is reserved for blocking diagnostics; worktree payload parsing retains documented and live/reference shapes.

**review-code-standards / review-silent-failure / review-type-design / review-test-coverage**
- No additional blocking findings. Name validation, missing Ruff handling, Prettier config classification, `.worktreeinclude` copying, durable-cwd removal, and their regression tests are consistent with the fixed blocker contracts.
