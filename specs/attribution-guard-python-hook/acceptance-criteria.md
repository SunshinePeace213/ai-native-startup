# Acceptance Criteria: Attribution guard — Python hook + attribution settings

> The definition of "done" for [spec.md](./spec.md). Every criterion is observable and testable, and
> every task in tasks.md should map to at least one criterion here.

## Acceptance Criteria

- **AC1** — A `git commit` payload whose message carries `Co-Authored-By: Claude <any model name>
  <noreply@anthropic.com>` (any case) makes `block_attribution.py` exit 2 with a stderr message
  that names the violation and tells Claude to remove the line and rerun.
- **AC2** — A `git`/`gh` payload carrying a `Claude-Session:` trailer, or a `gh pr` payload whose
  body carries `🤖 Generated with [Claude Code](https://claude.com/claude-code)`, exits 2 the same
  way.
- **AC3** — A clean `git commit` payload (no Claude attribution), including one with a non-Claude
  `Co-Authored-By:` trailer, exits 0 with no stderr complaint.
- **AC4** — A Bash payload that mentions an attribution string but invokes no `git`/`gh` command
  (e.g. a heredoc writing documentation) exits 0 — the current shell hook's false positive is gone.
- **AC5** — A non-Bash payload, empty stdin, or malformed JSON exits 0 (fail-open; the guard never
  wedges unrelated tool calls).
- **AC6** — The tracked `.claude/settings.json` carries the shared config: `enabledPlugins`, the
  `hooks` block (whose `PreToolUse` → `Bash` hook runs `block_attribution.py` via
  `uv run --script`), and `"attribution": {"commit": "", "pr": "", "sessionUrl": false}`; the file
  is valid JSON; `block-coauthor-trailer.sh` is no longer tracked.
- **AC7** — `uv run pytest tests/harness-layer/hooks/ -q` passes with zero failures and zero skips, and
  the suite covers every block/allow case listed in tasks.md task 3.
- **AC8** — HARNESS-LAYER.md describes the Python guard (path, three blocked forms, attribution
  settings as the prevention layer), says hooks are registered in `.claude/settings.json`, and its
  Files tree no longer mentions the shell hook.
- **AC9** — `.claude/settings.local.json` is untracked (out of the index, listed in `.gitignore`)
  with its on-disk copy reset to `{}`, and AGENTS.md carries the settings-sync rule: experiment in
  `settings.local.json`, fold shippable changes into `settings.json` before merging to main.

## Validation Commands

Run these to prove the criteria above. Map each command to the criteria it verifies.

- `printf '{"tool_name":"Bash","tool_input":{"command":"git commit -m \\"fix: x\\n\\nCo-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>\\""}}' | uv run --script .claude/hooks/block_attribution.py; echo "exit=$?"` —
  verifies AC1. Pass: prints a policy message to stderr and `exit=2`.
- `printf '{"tool_name":"Bash","tool_input":{"command":"gh pr create --body \\"🤖 Generated with [Claude Code](https://claude.com/claude-code)\\""}}' | uv run --script .claude/hooks/block_attribution.py; echo "exit=$?"` —
  verifies AC2. Pass: `exit=2`.
- `printf '{"tool_name":"Bash","tool_input":{"command":"git commit -m \\"🔧 chore(hooks): rewrite guard\\""}}' | uv run --script .claude/hooks/block_attribution.py; echo "exit=$?"` —
  verifies AC3. Pass: no stderr, `exit=0`.
- `printf '{"tool_name":"Bash","tool_input":{"command":"cat > notes.md <<EOF\\nNever add Co-Authored-By: Claude trailers\\nEOF"}}' | uv run --script .claude/hooks/block_attribution.py; echo "exit=$?"` —
  verifies AC4. Pass: `exit=0`.
- `printf '{"tool_name":"Write","tool_input":{"file_path":"x.md"}}' | uv run --script .claude/hooks/block_attribution.py; echo "exit=$?"` and
  `printf 'not json' | uv run --script .claude/hooks/block_attribution.py; echo "exit=$?"` —
  verify AC5. Pass: both `exit=0`.
- `uv run python -c "import json,sys; s=json.load(open('.claude/settings.json')); a=s['attribution']; assert a=={'commit':'','pr':'','sessionUrl':False}, a; cmds=[h['command'] for m in s['hooks']['PreToolUse'] for h in m['hooks']]; assert any('block_attribution.py' in c for c in cmds), cmds; assert s['enabledPlugins'], 'plugins missing'; print('settings OK')"` —
  verifies AC6 (attribution block + hook registration + plugins + valid JSON). Pass: `settings OK`.
- `! git ls-files --error-unmatch .claude/settings.local.json 2>/dev/null && grep -q "settings.local.json" .gitignore && test "$(cat .claude/settings.local.json)" = "{}" && echo "scratchpad OK"` —
  verifies AC9 (untracked, ignored, reset). Pass: `scratchpad OK`.
- `grep -n "settings.local.json" AGENTS.md` — verifies AC9 (sync rule present in project memory).
  Pass: the rule line prints.
- `! git ls-files --error-unmatch .claude/hooks/block-coauthor-trailer.sh 2>/dev/null && echo "old hook gone"` —
  verifies AC6 (old hook gone). Pass: prints `old hook gone`, exit 0. (Not `grep -c`, which exits 1
  on zero matches and would fail a correct build.)
- `uv run pytest tests/harness-layer/hooks/ -q` — verifies AC7. Pass: all tests pass, none skipped.
- `grep -n "block_attribution.py" HARNESS-LAYER.md && grep -q "settings.json" HARNESS-LAYER.md && ! grep -q "block-coauthor-trailer.sh" HARNESS-LAYER.md && echo "docs OK"` —
  verifies AC8. Pass: match lines then `docs OK`.
