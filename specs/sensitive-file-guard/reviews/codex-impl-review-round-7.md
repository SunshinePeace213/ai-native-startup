### Round 7 — Verdict: changes-requested

Scope: delta (`eaaac2139e13e3ca1efbea2c4b70b775dfa1c612..ceb30aede857665de15e0f79684ad47b6adf4e1c`, excluding `specs/sensitive-file-guard/reviews/`)
Base SHA: 945910a12c327e543bd041ab7939d724acb77653
Reviewed head SHA: ceb30aede857665de15e0f79684ad47b6adf4e1c
Mode: sequential (three files and 69 changed lines; below spawn threshold)
Profile: kb-grounded
Lenses: plan-adherence, security/guard-bypass, correctness, review-code-standards, review-silent-failure, review-test-coverage/test-quality, review-comment-accuracy, no-regression, KB-grounding; the expected security/guard-bypass, correctness, test-quality, and no-regression lenses all ran, with no disagreement in lens selection | skipped: review-type-design — no type, schema, or structured contract changed; review-simplification — the prior report records an earlier simplification pass and this delta targets the originating correctness/security finding
Validation:
- `uv run pytest tests/harness-layer/hooks/sensitive-files` → PASS (238 passed; runner-only `UV_CACHE_DIR` redirected to `/tmp` and sugar disabled for stable output)
- `uv run pytest tests/harness-layer/hooks/test_wiring.py` → PASS (6 passed; runner-only `UV_CACHE_DIR` redirected to `/tmp` and sugar disabled for stable output)
- `uv run pytest` → PASS (424 passed, zero skips; runner-only `UV_CACHE_DIR` redirected to `/tmp` and sugar disabled for stable output)
- `echo '{"tool_name":"Read","tool_input":{"file_path":"/tmp/nowhere/.env"}}' | uv run --script .claude/hooks/sensitive-files/file_guard.py; echo "exit=$?"` → PASS (three-line env deny; exit 2)
- `echo '{"tool_name":"Read","tool_input":{"file_path":"/tmp/nowhere/.env.example"}}' | uv run --script .claude/hooks/sensitive-files/file_guard.py; echo "exit=$?"` → PASS (silent; exit 0)
- `echo '{"tool_name":"Bash","tool_input":{"command":"cat .env"}}' | uv run --script .claude/hooks/sensitive-files/bash_guard.py; echo "exit=$?"` → PASS (three-line env deny; exit 2)
- `echo 'not json' | uv run --script .claude/hooks/sensitive-files/file_guard.py; echo "exit=$?"` → PASS (silent; exit 0)
- `grep -c "sensitive-files" .claude/settings.json .codex/hooks.json HARNESS-LAYER.md` → PASS (counts 2, 1, and 3)
- supplemental 12-case boundary smoke from the review packet → PASS (all six expected denies exited 2; all six locked allows exited 0)
Prior blockers:
- CX6-1 (both-ends `*.tfstate.*` internal-star bypass) — not fixed: the exact `terraform.*state.backup*` reproducer now denies, and the three-character threshold is reasonable for preserving the locked broad-search boundary, but the signal extractor erases singleton character-class literals and leaves an ordinary visible-family targeter allowed (CX7-1).

Digest: 1 blocking finding across security/guard-bypass, correctness, comment accuracy, and test quality — the targeting-signal gate loses visible singleton character-class literals before applying its three-character threshold, so an ordinary glob that explicitly spells the protected family through character classes selects a Terraform state backup and exits 0. All plan Validation Commands and the packet's 12 boundary smokes pass. The six additions non-vacuously exercise the intersection deny, concrete-witness deny, and locked no-signal allows, but omit this changed gate boundary. Code standards, silent-failure, no-regression, plan-adherence, and KB-grounding found nothing else. The delta changes no hook protocol/configuration claim; the unchanged claims remain consistent with the packet's cached official docs fetched 2026-07-05/06, which are not stale.

Findings:

**Security / guard-bypass, correctness, comment accuracy, and test quality**

- **CX7-1 (blocker) — singleton character classes bypass the claimed visible-family invariant.** `_common.py:601-610` computes signal only after `_rewrite_char_classes` has replaced every class with `?` at `_common.py:667`, then removes those `?` characters from the skeleton. Thus `prod.t[f]s[t]a[t]e.backup*` becomes `prod.t?s?a?e.backup*`, loses the visibly spelled `tfstate` family signal, and is skipped at `_common.py:681-684`. Independent checks show `prod.tfstate.backup` matches both that user glob and `*.tfstate.*`, while the real Grep guard exits 0. This is new evidence within the security/guard-bypass lens and the previously locked CX2 character-class semantics: singleton classes are ordinary exact glob syntax, not an obfuscated payload. The stated conjunctive implementation invariant (intersection plus a computed three-character signal) holds mechanically, and the **three-character threshold itself is approved** as a reasonable boundary against incidental one- or two-character overlap and the locked `README*`/`secret.pe*` broad-search allows. The broader docstring/packet claim at `_common.py:644-654` that unobfuscated targeters whose literals visibly reference the family are guaranteed denied is nevertheless false because signal extraction discards exact class literals before applying that sound threshold. The additions at `test_engine.py:479-486` and `test_file_guard.py:335-350` cover their two deny branches and two no-signal allow pins non-vacuously, but do not cover this gate edge. Fix: derive the targeting signal from the original glob in a way that preserves exact singleton-class literals (while keeping genuinely variable classes/wildcards signal-free), then add engine-category and real-guard exit-2 regressions for this or an equivalent singleton-class `*.tfstate.*` targeter without changing the locked broad allows.

No advisory findings.
