### Round 1 — Verdict: changes-requested

Scope: full
Base SHA: 116624f4bbe99a3a40bef9a9efd5ce85add3ce9e
Reviewed head SHA: 0c7b682b5b9bda23ba6f132edd5c3a6d167021d8
Mode: spawn (7 lenses, 2,254 changed lines, high-risk blocking hook code)
Profile: kb-grounded
Lenses: plan-adherence, review-code-standards, review-silent-failure, review-type-design, review-test-coverage, review-comment-accuracy, review-simplification, KB-grounding | skipped: none
Validation:

- `uv run pytest tests/harness-layer/ -q` → PASS (158 passed; `UV_CACHE_DIR=/tmp/uv-cache` redirected the sandbox's read-only default cache)
- `uv run pytest -q` → PASS (158 passed; same cache relocation)
- AC3 pragma shell check → PASS (`exit=0`, no finding output)
- AC1 AWS shell check → PASS (`exit=2`, file, line, and `aws-access-key` on stderr)
- empty-stdin `stop_sweep.py` shell check → PASS (`exit=0`)
- six-entry `jq -e` registration check → PASS (`true`)
- `grep -n 'security-scan' .gitignore HARNESS-LAYER.md` → PASS (hits in both files)
- `uv run ruff check .claude/hooks/security-scan/` → PASS (`All checks passed!`)

Digest: 9 blocking findings — three scanner-rule correctness defects, two concurrency races, one Git-path tracking gap, one hidden-warning hook-contract defect, one silent state-read failure, and one committed secret-shaped fixture. All validation commands pass, but the implementation does not yet meet the plan's high-precision, complete tracking, and agent-visible warning contracts.

Findings:

**Plan adherence / review-test-coverage**

- **A raw blocking fixture is committed in the validation plan.** `specs/security-scan-hook/acceptance-criteria.md:47` contains the contiguous `AKIAIOSFODNN7REALKEY` sample; the reviewed scanner itself reports `aws-access-key` when run on that file. This conflicts with the expected test-quality check that committed sources contain no raw secret-shaped literals and makes later edits to the plan self-blocking. Fix: assemble the value from shell fragments, as the Python tests already do.

**KB grounding / hook contracts**

- **The promised Stop warnings are silent on successful exit.** `stop_sweep.py:51-63` writes vuln-only findings and the `stop_hook_active: true` final secret warning only to stderr, then exits 0. `ai-docs/anthropic/hooks-guide.md:555-566,974-978` says exit 0 is silent and structured JSON on stdout is required for non-blocking control; stderr is surfaced as Claude feedback on exit 2. Consequently a Bash-only vulnerability never surfaces and the documented final loud warning is debug-log-only, contradicting the Objective, AC5, and `HARNESS-LAYER.md:48-50`. Fix: use a cached-doc-supported non-blocking Stop output channel, or narrow the specification and documentation if no such channel exists.
- **The scanner races the formatter instead of scanning a sequenced final file.** `.claude/settings.json:19-73` registers auto-format and security scan as separate matching PostToolUse groups. The KB states that all matching hooks execute in parallel (`ai-docs/anthropic/hooks-guide.md:442-488,514`), so `post_write_scan.py:39-40` can read while the formatter rewrites the same file. This violates the per-write scan of the saved/finished file promised by the Objective and `HARNESS-LAYER.md:40`. Fix: sequence formatting before scanning through one orchestrating hook or another documented ordering mechanism, and test the integrated registration behavior.
- **Session-state read/modify/write loses updates under parallel hook events.** `_common.py:424-457` loads and atomically replaces state without locking or merge-on-write, despite its single-writer comment. Parallel tool calls or subagent hook events sharing a session can read the same state and last-writer-wins, dropping tracked paths or regressing `last_head`; atomic replace prevents torn JSON but not lost updates. This contradicts the tracked-set coverage objective, while the KB explicitly documents parallel hook execution. Fix: serialize per-session updates or merge under a lock, with a concurrent-update regression test.

**review-code-standards / scanner correctness**

- **The generic credential blocker is not high precision.** `_common.py:208-215` blocks any identifier containing `api_key`, `secret`, `token`, or `password` when its quoted value is at least eight characters. Ordinary metadata such as `token_endpoint = "authorization_code"` or `password_algorithm = "pbkdf2_sha256"` therefore exits 2, contradicting the locked decision that blocking rules represent confirmed secrets. Fix: narrow the accepted credential field shapes and add realistic non-secret semantic negatives.
- **Connection-string credentials with valid punctuation are missed.** `_common.py:202-205` excludes `:` from the password group, so a URI such as `postgres://dbuser:p:ssword@host/db` does not match the required `scheme://user:pass@` rule. Fix: parse the userinfo boundary robustly or allow valid userinfo punctuation while anchoring on `@`, with punctuation-bearing password tests.
- **A comment mentioning `SafeLoader` suppresses a real unsafe YAML finding.** `_common.py:239-242` searches the entire line after `yaml.load(` for `SafeLoader`, so `yaml.load(data)  # TODO: use SafeLoader` is treated as safe even though the call has no loader. This violates the required unsafe-`yaml.load` warning rule. Fix: constrain the exemption to the call arguments (excluding comments/adjacent text) and add this regression case.
- **Git's quoted path format is parsed as if it were literal text.** `_common.py:495-515,518-531,546-555` strips surrounding quotes without decoding Git C escapes, and rename parsing splits textual ` -> ` records. Non-ASCII/control-character paths and ambiguous rename destinations can become nonexistent stored paths, so newly dirty or committed files evade the sweep. This fails the spec's Git rename/edge-case tracking requirement. Fix: request `-z` output and parse NUL-delimited status/diff records, with rename and non-ASCII end-to-end cases.

**review-silent-failure**

- **Unexpected state-read failures silently disable the Stop sweep.** `_common.py:424-430` converts every `OSError`, including permission and transient I/O errors, into empty state without a note; `stop_sweep.py:38-42` then exits cleanly and scans nothing. Missing/corrupt state is the specified fail-open case, but unexpected plumbing errors must remain diagnosable. Fix: distinguish missing/corrupt state from other I/O failures and emit a path-specific fail-open note for the latter.

**Non-blocking advisories**

- `HARNESS-LAYER.md:41-46,48` overstates that baseline files are “never flagged” and that the sweep always prevents turn end; per-write scanning intentionally still covers baseline-dirty files, and `stop_hook_active: true` allows Stop. Narrow these statements to Bash attribution/sweep behavior and document the one-block exception.
- `review-simplification`: `_common.py:78-85` contains an unused `read_file_path()` helper. `post_write_scan.py:45-49` and `track_bash_writes.py:72-75` also pre-deduplicate/sort values that `save_state()` normalizes again. Remove the unused helper and rely on the single normalization point where doing so preserves persisted output.

### Round 1 — Verdict: changes-requested
