# Acceptance Criteria: Sensitive File Guard — block agent access to secret-bearing files

> The definition of "done" for [spec.md](./spec.md). Every criterion is observable and testable, and
> every task in tasks.md should map to at least one criterion here.

## Acceptance Criteria

- **AC1** — `file_guard.py` denies Read/Edit/Write/MultiEdit payloads targeting any
  cataloged file (at least one test per catalog category in decisions.md D2): exit
  code 2, stderr contains `Blocked:`, the matched path, the category label, and the
  standing policy line.
- **AC2** — A `.env`-family denial redirects concretely: when a template from the
  allowlist exists in the target's directory or the project root, the message names
  that exact file; when none exists, the message says to ask the user. Grep
  payloads whose `path` or `glob` names a cataloged file are denied the same way.
- **AC3** — Allow paths stay open: the seven allowlist template names, ordinary
  project files, Grep over a directory with no direct sensitive target, and
  payloads from tools outside the matcher set all exit 0 with no deny output.
- **AC4** — `bash_guard.py` denies commands referencing cataloged paths (the spec
  Edge-Cases corpus: `cat .env`, `cp .env /tmp/x`, `source .env`, `grep KEY .env`,
  `python -c "open('.env')"`, `cat $HOME/.ssh/id_rsa`, `base64 .env`), denies the
  shell-operator boundary cases (`cat .env|base64`, `cat .env&&echo done`,
  `cat .env>copy`, and a multiline command with `cat .env` on its own line), and
  passes `cat .env.example`, `ls -la`, `git status`, and a `/.awsome/` boundary
  negative.
- **AC5** — Normalization defeats path dodges in tests: tilde paths, relative/
  traversal paths, and a symlink whose realpath is a cataloged file are all denied;
  a symlink named like a template resolving to a real `.env` is denied.
- **AC6** — Fail-open contract holds for both guards: empty stdin, non-JSON stdin,
  missing `tool_name`/`tool_input`, non-string path/command, and an injected
  engine exception all exit 0; no code path exits 1.
- **AC7** — Wiring is pinned: `.claude/settings.json` runs `bash_guard.py` inside
  the existing PreToolUse `Bash` block and `file_guard.py` in one new
  `Read|Grep|Edit|Write|MultiEdit` block; `.codex/hooks.json` runs `bash_guard.py`
  in its PreToolUse `Bash` block. `test_wiring.py` proves all of it: the
  `EXPECTED_BINDINGS` matrix covers both new Claude registrations, and a new
  assertion loads `.codex/hooks.json` and checks the `bash_guard.py` binding's
  event (`PreToolUse`), matcher (`Bash`), command path
  (`.claude/hooks/sensitive-files/bash_guard.py` via the
  `$(git rev-parse --show-toplevel)` form), and non-empty `statusMessage` —
  removing or malforming the Codex binding fails the test.
- **AC8** — `HARNESS-LAYER.md` documents the family (new section + Files-tree
  entries) in the file's existing style.
- **AC9** — The full test suite is green from the repo root with no skips
  introduced by this change.

## Validation Commands

Run these to prove the criteria above. Map each command to the criteria it verifies.

- `uv run pytest tests/harness-layer/hooks/sensitive-files` — verifies AC1–AC6. A
  pass is all tests green (parallel by default; no timeout overrides).
- `uv run pytest tests/harness-layer/hooks/test_wiring.py` — verifies AC7. A pass
  means both new bindings are present and every registered hook resolves.
- `uv run pytest` — verifies AC9. Full suite green from the repo root.
- `echo '{"tool_name":"Read","tool_input":{"file_path":"/tmp/nowhere/.env"}}' | uv run --script .claude/hooks/sensitive-files/file_guard.py; echo "exit=$?"` —
  smoke-verifies AC1/AC2: prints a three-line deny naming the env category and
  `exit=2`.
- `echo '{"tool_name":"Read","tool_input":{"file_path":"/tmp/nowhere/.env.example"}}' | uv run --script .claude/hooks/sensitive-files/file_guard.py; echo "exit=$?"` —
  smoke-verifies AC3: no deny output, `exit=0`.
- `echo '{"tool_name":"Bash","tool_input":{"command":"cat .env"}}' | uv run --script .claude/hooks/sensitive-files/bash_guard.py; echo "exit=$?"` —
  smoke-verifies AC4: three-line deny, `exit=2`.
- `echo 'not json' | uv run --script .claude/hooks/sensitive-files/file_guard.py; echo "exit=$?"` —
  smoke-verifies AC6: `exit=0`.
- `grep -c "sensitive-files" .claude/settings.json .codex/hooks.json HARNESS-LAYER.md` —
  spot-checks AC7/AC8: non-zero counts in all three files.
