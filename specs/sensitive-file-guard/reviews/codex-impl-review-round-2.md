### Round 2 — Verdict: changes-requested

Scope: delta (`9a8ec50e02765a3669dac97863f8132ad592c37a..f2e3d556af1e42e6aa8295c3d5b0e59d648eff6e`, excluding `specs/sensitive-file-guard/reviews/`)
Base SHA: 945910a12c327e543bd041ab7939d724acb77653
Reviewed head SHA: f2e3d556af1e42e6aa8295c3d5b0e59d648eff6e
Mode: spawn (high-risk executable guard code; 7 files and 385 changed lines)
Profile: kb-grounded
Lenses: plan-adherence, security/guard-bypass, correctness, review-code-standards, review-silent-failure, review-type-design, review-test-coverage, review-comment-accuracy, no-regression, KB-grounding; the expected four delta lenses all ran, and review-type-design additionally ran because `Rule` gained the `cmd_re` contract | skipped: review-simplification — round 1 already ran it and delta rounds invoke only originating lenses when judgment is needed
Validation:
- `uv run pytest tests/harness-layer/hooks/sensitive-files` → PASS (175 passed; runner-only `UV_CACHE_DIR` redirected to `/tmp`)
- `uv run pytest tests/harness-layer/hooks/test_wiring.py` → PASS (6 passed; runner-only `UV_CACHE_DIR` redirected to `/tmp`)
- `uv run pytest` → PASS (361 passed, zero skips; runner-only `UV_CACHE_DIR` redirected to `/tmp`)
- `echo '{"tool_name":"Read","tool_input":{"file_path":"/tmp/nowhere/.env"}}' | uv run --script .claude/hooks/sensitive-files/file_guard.py; echo "exit=$?"` → PASS (three-line deny; `exit=2`)
- `echo '{"tool_name":"Read","tool_input":{"file_path":"/tmp/nowhere/.env.example"}}' | uv run --script .claude/hooks/sensitive-files/file_guard.py; echo "exit=$?"` → PASS (silent; `exit=0`)
- `echo '{"tool_name":"Bash","tool_input":{"command":"cat .env"}}' | uv run --script .claude/hooks/sensitive-files/bash_guard.py; echo "exit=$?"` → PASS (three-line deny; `exit=2`)
- `echo 'not json' | uv run --script .claude/hooks/sensitive-files/file_guard.py; echo "exit=$?"` → PASS (silent; `exit=0`)
- `grep -c "sensitive-files" .claude/settings.json .codex/hooks.json HARNESS-LAYER.md` → PASS (counts 2, 1, and 3)

Prior blockers:
- CX1-1 (Grep wildcard glob bypass) — not fixed: the common trailing-wildcard cases are fixed, but ordinary character-class globs still bypass the new matcher (CX2-1).
- CX1-2 (relative Bash fragment bypass) — fixed: `cmd_re` recognizes token-start relative home-dot-directory fragments while preserving absolute-only system fragments and the tested `data.aws/file` / `/.awsome/` negatives.
- CX1-3 (AC6 injected-exception test gap) — fixed: both guards expose `run()`, and the in-process tests use real-file stdin, force the bound engine matcher to raise, and assert the visible exit-0 fail-open result.
- CX1-4 (allowlist comment rot) — fixed: the comment now accurately limits the exemption to basename rules and preserves fragment/realpath denials.

Prior advisory/internal findings:
- CX1-5 (HARNESS catalog summary) — deferred-by-design to the PR Follow-ups checklist.
- CX1-6 (ordinary Bash allow tests do not prove silence) — deferred-by-design to the PR Follow-ups checklist.
- I-1 (guard-family docstring accuracy) — fixed: both docstrings now distinguish access blocking from output-content scanning.
- I-3 (HOOK-TESTING bespoke Codex pin convention) — deferred-by-design to the PR Follow-ups checklist.
- I-2 (three-line denial versus file:line wording) — dropped remains sound: the behavior is pre-existing on `origin/main`, and this delta neither introduces nor worsens it.

Digest: 1 blocking security/guard-bypass finding. The delta fixes CX1-2, CX1-3, CX1-4, and I-1 without loosening existing denies or weakening tests, but CX1-1 remains partially unresolved because `match_glob()` does not model standard character classes. All validation commands pass. The unchanged hook protocol claims remain consistent with the packet's current cached official docs; no KB contradiction, ungrounded load-bearing claim, or stale source was found.

Findings:

**Security / guard-bypass**

- **CX2-1 (blocker) — standard character-class Grep globs bypass catalog matching.** `_common.py:511-558` recognizes `[` as a glob metacharacter, but its overlap heuristic constructs witnesses by replacing only `*` and `?`; it therefore does not determine whether a character-class pattern intersects a catalog rule. At the reviewed head, `.env[.]local`, `id_r[s]a[0-9]*`, and `service-[a]ccount[0-9]*.json` all exit 0 through the real `file_guard.py`, although ripgrep treats character classes as glob syntax (independently demonstrated by `rg --files -g 'pyproject[.]toml'`) and those patterns select names covered by `.env.*`, `id_rsa*`, and `service-account*.json`. These basename segments do not open with a wildcard, so this bypass is outside the documented broad-glob allow boundary and leaves AC2/CX1-1 unresolved. Fix: replace the sample/witness heuristic with a deterministic overlap check that handles the supported glob grammar (including character classes), or conservatively deny non-leading metacharacter patterns whose literal/catalog relationship cannot be proven safe; add engine and real-guard regressions for these cases.

No other blocking findings remain across plan adherence, correctness, code standards, silent failure, type design, test quality, comment accuracy, no-regression, or KB grounding.
