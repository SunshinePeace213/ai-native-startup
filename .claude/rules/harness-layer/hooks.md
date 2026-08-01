---
paths:
  - ".claude/hooks/**/*"
  - "tests/harness-layer/hooks/**/*"
  - ".claude/settings.json"
  - ".codex/hooks.json"
---

# Harness Hooks

Catalog of every Claude Code hook in this repo, plus the development and testing
rules. One row per hook — for full behavior, read the hook's source.

## Catalog

Hooks live under `.claude/hooks/` at the path in the first column; multi-script
families share a `_common.py` engine. The Codex column says whether the family is
mirrored into `.codex/hooks.json`.

| Hook | Event / matcher | What it does | Codex |
| --- | --- | --- | --- |
| `block_attribution.py` | PreToolUse `Bash` | Denies git/gh commands carrying Claude attribution text | mirrored |
| `destructive-guard/` | PreToolUse `Bash` | Denies destructive commands; risky ones print `"ask"` JSON so the human approves per call | mirrored (ask tier denies) |
| `auto-format/` | PostToolUse `Write\|Edit\|MultiEdit` | Four extension-scoped formatters (`js_ts`, `data`, `markdown`, `python`) format the edited file in place; unfixable lint → exit-2 diagnostics | mirrored |
| `security-scan/` | PostToolUse(+Failure) `Write\|Edit\|MultiEdit`/`Bash`, SessionStart, Stop/SubagentStop | Tracks agent-touched files, scans them for secrets (blocking) and vuln patterns (warn-only); a `security-scan: allow` comment suppresses a line | mirrored |
| `sensitive-files/` | PreToolUse `Read\|Grep\|Edit\|Write\|MultiEdit` + `Bash` | Denies agent access to secret-bearing files by name/path | mirrored (write surface only) |
| `check_spec_completeness.py` | Stop (command-scoped) | Blocks `/harness-layer:harness-plan` from ending on an incomplete `specs/` folder | not-applicable |
| `check_gate_signoff.py` | Stop (command-scoped) | Blocks a studio hard gate — phase from `argv[1]` — from closing until the client sign-off, its hashed artifacts, and that phase's extra document all check out | not-applicable |
| `worktree/` | WorktreeCreate / WorktreeRemove | Creates dep-installed worktrees (`bun install` + `uv sync`); removes worktree + branch | not-applicable |

## Development

- Every hook is a PEP 723 `# /// script` file run via `uv run --script`.
- Register in `.claude/settings.json`: one matcher block per event+matcher pair —
  a new hook joins the existing block's `hooks` array. A hook that must run only
  inside one command registers in that command's frontmatter instead (the
  spec-gate pattern).
- `"$CLAUDE_PROJECT_DIR"` is the registration idiom and resolves in a hook, an
  stdio MCP server and a plugin LSP server — nowhere else
  (`ai-docs/anthropic/hooks.md:494`). It is empty in a command body, where an
  anchored path silently becomes `/<path>` at the filesystem root; anchor those on
  `$(git rev-parse --show-toplevel)` instead.
- Contract: exit 2 only for agent-fixable findings, with diagnostics on stderr;
  everything else — malformed stdin, missing files, plumbing failures — fails
  open with exit 0.
- Ship together: an added, moved, or re-matched hook lands with its
  `test_wiring.py` `EXPECTED_BINDINGS` update, its `.codex/hooks.json` entry
  and `CODEX_DISPOSITIONS` verdict, and its contract tests in the same change.

## Testing

Tests live in `tests/harness-layer/hooks/<feature>/`, mirroring
`.claude/hooks/<feature>/`; `test_wiring.py` pins every registration.

- Launch hooks only through the shared `run_hook` fixture (root `conftest.py`),
  addressed relative to `.claude/hooks/`; set env with its `env_overrides=` /
  `unset_env=` knobs, never a hand-built environ.
- Import hook modules with the `load_hook_module` fixture — never `sys.path`
  tricks or a bare `import _common` (family `_common` names collide).
- Test block AND allow paths; malformed or empty stdin must fail open (exit 0).
  Exit 2 must carry `file:line rule` diagnostics on stderr — command-inspection
  hooks carry `(<Category>/<rule_id>)` or a plain policy message instead.
- Assemble secret-shaped fixtures at runtime from fragments; never commit a
  matchable literal.
- Subprocess timeout is 45s under pytest's global 60s; raise neither — mark a
  known-slow test `@pytest.mark.timeout(120)`.
- Every test docstring states WHY the behavior matters, not just what it does.
- Probe Codex hook behavior from a scratch repo: Codex loads `.codex/` from the
  main repo root, so a worktree's own layer never runs, and an untrusted project
  path has no hook layer at all.
- A fail-open hook is only proven by a positively observed block — a green suite
  pins registration, never execution.
