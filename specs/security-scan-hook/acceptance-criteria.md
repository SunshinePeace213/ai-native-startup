# Acceptance Criteria: Security Scan Hook

> The definition of "done" for [spec.md](./spec.md). Every criterion is observable and testable, and
> every task in tasks.md should map to at least one criterion here.

## Acceptance Criteria

- **AC1** — Piping a PostToolUse payload for a file containing a known secret pattern (e.g. an
  `AKIA…` AWS key id or `sk-ant-…` Anthropic key) into `post_write_scan.py` exits 2 and prints
  `file:line rule` diagnostics to stderr; diagnostics are capped with an "and N more" tail.
- **AC2** — The same payload for a file containing only a curated vulnerability pattern (e.g.
  `yaml.load(data)` without a SafeLoader) exits 0 and prints JSON to stdout whose
  `hookSpecificOutput.additionalContext` names the finding.
- **AC3** — A placeholder credential (e.g. `api_key = "your-key-here"`) and a real-pattern line
  carrying the `security-scan: allow` pragma (on the line or the line above) both produce exit 0
  with no findings.
- **AC4** — After `session_baseline.py` runs in a repo with one pre-dirty file, and
  `track_bash_writes.py` runs after a Bash-created file appears, the session state file contains
  the new file in the tracked set and does NOT contain the pre-dirty baseline file.
- **AC5** — `stop_sweep.py` exits 2 while a tracked file contains a secret, exits 0 after the
  secret is removed, and exits 0 (fail-open) when the state file is missing or corrupt.
- **AC6** — Every one of the four scripts exits 0 on empty stdin, malformed JSON, and a payload
  referencing a nonexistent file.
- **AC7** — `uv run pytest` passes from the repo root; the new tests are parallel-safe (isolated
  via `tmp_path`/`monkeypatch`, no shared state, no order dependence, no global-timeout changes).
- **AC8** — `.claude/settings.json` registers all five hook entries (PostToolUse
  `Write|Edit|MultiEdit`, PostToolUse `Bash`, SessionStart, Stop, SubagentStop),
  `.claude/.security-scan/` is gitignored, HARNESS-LAYER.md documents the family, and
  `uv run ruff check .claude/hooks/security-scan/` reports no issues.

## Validation Commands

Run these to prove the criteria above. Map each command to the criteria it verifies.

- `uv run pytest tests/harness-layer/ -q` — verifies AC1–AC7 via the two new test modules plus
  existing suites staying green. Pass = zero failures.
- `uv run pytest -q` — verifies AC7 across the whole repo (new tests are parallel-safe under
  `-n auto`). Pass = zero failures.
- `F=$(mktemp); echo 'aws_key = "AKIAIOSFODNN7EXAMPLE"  # security-scan: allow' > "$F"; printf '{"session_id":"ac3","tool_name":"Write","tool_input":{"file_path":"%s"}}' "$F" | uv run --script .claude/hooks/security-scan/post_write_scan.py; echo "exit=$?"` —
  verifies AC3 (pragma). Pass = `exit=0`, no finding output.
- `F=$(mktemp); echo 'key = "AKIAIOSFODNN7REALKEY"' > "$F"; printf '{"session_id":"ac1","tool_name":"Write","tool_input":{"file_path":"%s"}}' "$F" | uv run --script .claude/hooks/security-scan/post_write_scan.py; echo "exit=$?"` —
  verifies AC1. Pass = `exit=2` and stderr names the file, line, and AWS rule.
- `echo '' | uv run --script .claude/hooks/security-scan/stop_sweep.py; echo "exit=$?"` —
  verifies AC6 for the sweep (empty stdin fail-open). Pass = `exit=0`.
- `jq -r '.hooks | keys[]' .claude/settings.json` — verifies AC8 registration. Pass = output
  includes `PostToolUse`, `SessionStart`, `Stop`, `SubagentStop` (Bash matcher visible under
  PostToolUse entries).
- `grep -n 'security-scan' .gitignore HARNESS-LAYER.md` — verifies AC8 gitignore + docs. Pass =
  a hit in each file.
- `uv run ruff check .claude/hooks/security-scan/` — verifies AC8 lint. Pass = "All checks passed".
