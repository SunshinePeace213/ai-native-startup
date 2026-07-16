---
paths:
  - ".claude/hooks/**/*"
  - "tests/harness-layer/hooks/**/*"
  - ".claude/settings.json"
---

# Harness Hooks

Catalog of every Claude Code hook in this repo, plus the development and testing
rules. One row per hook — for full behavior, read the hook's source.

## Catalog

Hooks live under `.claude/hooks/` at the path in the first column; multi-script
families share a `_common.py` engine.

| Hook | Event / matcher | What it does |
| --- | --- | --- |
| `block_attribution.py` | PreToolUse `Bash` | Denies git/gh commands carrying Claude attribution text |
| `destructive-guard/` | PreToolUse `Bash` | Denies destructive commands; risky ones print `"ask"` JSON so the human approves per call |
| `auto-format/` | PostToolUse `Write\|Edit\|MultiEdit` | Four extension-scoped formatters (`js_ts`, `data`, `markdown`, `python`) format the edited file in place; unfixable lint → exit-2 diagnostics |
| `security-scan/` | PostToolUse(+Failure) `Write\|Edit\|MultiEdit`/`Bash`, SessionStart, Stop/SubagentStop | Tracks agent-touched files, scans them for secrets (blocking) and vuln patterns (warn-only); a `security-scan: allow` comment suppresses a line |
| `sensitive-files/` | PreToolUse `Read\|Grep\|Edit\|Write\|MultiEdit` + `Bash` | Denies agent access to secret-bearing files by name/path; `bash_guard.py` is also registered in `.codex/hooks.json` |
| `check_spec_completeness.py` | Stop (command-scoped) | Blocks `/harness-layer:harness-plan` from ending on an incomplete `specs/` folder |
| `worktree/` | WorktreeCreate / WorktreeRemove | Creates dep-installed worktrees (`bun install` + `uv sync`); removes worktree + branch |

## Development

- Every hook is a PEP 723 `# /// script` file run via `uv run --script`.
- Register in `.claude/settings.json`: one matcher block per event+matcher pair —
  a new hook joins the existing block's `hooks` array. A hook that must run only
  inside one command registers in that command's frontmatter instead (the
  spec-gate pattern).
- Contract: exit 2 only for agent-fixable findings, with diagnostics on stderr;
  everything else — malformed stdin, missing files, plumbing failures — fails
  open with exit 0.
- Ship together: an added, moved, or re-matched hook lands with its
  `test_wiring.py` `EXPECTED_BINDINGS` update and its contract tests in the
  same change.

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
