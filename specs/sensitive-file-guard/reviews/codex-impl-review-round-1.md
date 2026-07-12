### Round 1 — Verdict: changes-requested

Scope: full
Base SHA: 945910a12c327e543bd041ab7939d724acb77653
Reviewed head SHA: 9a8ec50e02765a3669dac97863f8132ad592c37a
Mode: spawn (6 lenses, 2,254 changed lines, and high-risk executable guard code)
Profile: kb-grounded
Lenses: plan-adherence, review-code-standards, review-silent-failure, review-type-design, review-test-coverage, review-comment-accuracy, review-simplification, KB-grounding; expected security/guard-bypass, correctness, test-quality, harness-wiring, and docs-accuracy lenses all covered | skipped: none
Validation:
- `uv run pytest tests/harness-layer/hooks/sensitive-files` → PASS (140 passed; runner-only `UV_CACHE_DIR` redirected to `/tmp`)
- `uv run pytest tests/harness-layer/hooks/test_wiring.py` → PASS (6 passed; runner-only `UV_CACHE_DIR` redirected to `/tmp`)
- `uv run pytest` → PASS (326 passed, zero skips; runner-only `UV_CACHE_DIR` redirected to `/tmp`)
- `echo '{"tool_name":"Read","tool_input":{"file_path":"/tmp/nowhere/.env"}}' | uv run --script .claude/hooks/sensitive-files/file_guard.py; echo "exit=$?"` → PASS (three-line deny; `exit=2`)
- `echo '{"tool_name":"Read","tool_input":{"file_path":"/tmp/nowhere/.env.example"}}' | uv run --script .claude/hooks/sensitive-files/file_guard.py; echo "exit=$?"` → PASS (silent; `exit=0`)
- `echo '{"tool_name":"Bash","tool_input":{"command":"cat .env"}}' | uv run --script .claude/hooks/sensitive-files/bash_guard.py; echo "exit=$?"` → PASS (three-line deny; `exit=2`)
- `echo 'not json' | uv run --script .claude/hooks/sensitive-files/file_guard.py; echo "exit=$?"` → PASS (silent; `exit=0`)
- `grep -c "sensitive-files" .claude/settings.json .codex/hooks.json HARNESS-LAYER.md` → PASS (non-zero in all three files)

Digest: 4 blocking findings — 2 guard bypasses (Grep wildcard globs and relative Bash path fragments), 1 missing plan-required fail-open fault-injection test, and 1 misleading allowlist contract comment. Two non-blocking documentation advisories remain. All injected KB claims match the implementation and cached docs; the 2026-07-05/06 sources are current, and the resolved D5 snake_case/exit-2 convention was not re-litigated.

Findings:

**Security / correctness**

- **CX1-1 (blocker) — Grep wildcard globs can select sensitive files without being denied.** `file_guard.py:52` passes `tool_input.glob` to `_common.match_command_text()`, whose token-boundary regex matches literal catalog-shaped text rather than determining what a glob can select. Consequently `.env*`, `**/.env*`, and `secrets.*` all exit 0, although they select cataloged files. This violates AC2 and the Objective's requirement to deny Grep calls targeting cataloged files. Fix: add a dedicated conservative glob matcher that denies patterns capable of selecting a cataloged basename/path, route Grep `glob` through it, and add e2e regressions for wildcard forms.
- **CX1-2 (blocker) — relative Bash references bypass path-fragment-only catalog rules.** `_common.py:355-364` searches D2 fragments only in their leading-slash form. Plain, unobfuscated commands such as `cat .aws/credentials` and `cat .docker/config.json` therefore exit 0; these files lack a sensitive basename rule and depend on the fragment. This contradicts AC4 and the Objective's “any Bash tool call” catalog coverage; glob dodges and obfuscation are out of scope, but ordinary relative paths are not. Fix: make command-fragment matching recognize token-start relative equivalents while preserving the `/.awsome/` negative boundary, and add e2e coverage for relative fragment-only entries.

**Plan adherence / review-test-coverage**

- **CX1-3 (blocker) — AC6's required injected-exception behavior is not tested for either guard.** `acceptance-criteria.md` AC6 explicitly requires “an injected engine exception” to exit 0 for both guards, and tasks 2–3 require their fail-open wrappers to be proven. `test_file_guard.py` and `test_bash_guard.py` cover malformed inputs and normal early returns but never force `_common.match_path()`, `_common.match_command_text()`, or denial rendering to raise through the top-level wrappers at `file_guard.py:61-67` and `bash_guard.py:40-48`. A regression to exit 1 would leave all 326 tests green. Fix: inject an engine exception for each guard and assert exit 0 (not 1 or 2), with the expected diagnostic posture.

**review-comment-accuracy**

- **CX1-4 (blocker) — the allowlist contract comment states the opposite of security-relevant behavior.** `_common.py:94-96` says the seven template basenames “always pass,” but `_match_single_path()` checks fragment rules first and `match_path()` separately checks realpaths: `/home/u/.ssh/.env.example` and a template-named symlink resolving to `.env` intentionally deny, as tests pin. This is active comment rot around the only escape hatch. Fix: state that the allowlist exempts basename rules only; fragment and realpath matches still deny.

**Non-blocking advisories**

- **CX1-5 (advisory, docs-accuracy) — the HARNESS catalog summary is incomplete.** `HARNESS-LAYER.md:74-79` omits framework/app secrets, shell/REPL history, and Kerberos, and says “database credentials” although `_common.py:279-283` also blocks database data. Fix: mark the list illustrative or align it with D2, including “database credentials & data.”
- **CX1-6 (advisory, test-quality) — ordinary Bash allow tests do not prove silence.** `test_bash_guard.py:36-40` checks exit 0 and absence of `Blocked:` but not empty stderr, so noisy diagnostics on every ordinary Bash call would pass despite the suite's invisible-allow contract. Fix: assert empty stderr for normal allow cases.

No other blocking findings remain from code standards, silent-failure, type-design, wiring, simplification, KB grounding, or plan adherence.
