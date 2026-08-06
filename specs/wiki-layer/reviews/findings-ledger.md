# Findings Ledger: wiki-layer

Round 1 (spec panel, gpt-5.6-sol/high, reviewed head `fcc015b`): 31 raw findings
across three lenses; evidence#8 and simplicity#5 merged into R1-F6 (same defect
class, same target). No lens substitutions. Verdict: changes-requested
(19 blocking, 10 advisory). All 19 fixed in commit `b613a24`.

Round 2 (delta, gpt-5.6-sol/medium, range `fcc015b..b613a24`): all round-1
dispositions verified; 8 new findings inside the fix diff — 6 blocking, 2
advisory. The 6 blocking fixed in the cycle-2 fix commit — **Codex-unverified**
(cycle cap reached); the deterministic floor (spec lint) re-ran green.

| ID | STD | Lens | Sev | Conf | Finding | Disposition | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| R1-F1 | S4 | fidelity | major | 98 | Lint's required checks omit the locked secret/PII scan | fixed — lint task now requires the secret/PII scan across every domain (tasks.md §3) | tasks.md §3 vs decisions.md privacy assumption |
| R1-F2 | S4 | fidelity | major | 98 | Status implements only the absorb trigger, not all three locked expansion triggers | fixed — status derives all three triggers from tracked state (tasks.md §4) | tasks.md §4 vs decisions.md expansion policy |
| R1-F3 | S4 | fidelity | minor | 92 | Routine contract wording weakened (fresh-clone + claude/-branch PR not restated in task) | advisory | tasks.md §3 vs decisions.md |
| R1-F4 | S5 | fidelity | major | 99 | "≥1 source per claim-bearing page" contradicts locked "every claim cites ≥1 source" | fixed — standards-rule task states every claim traces to ≥1 source (tasks.md §2) | tasks.md §2 vs decisions.md metrics |
| R1-F5 | S5 | fidelity | minor | 100 | Lint task says "run /kb"; the command is `/harness-layer:kb` | advisory | tasks.md §3 vs spec.md Edge Cases |
| R1-F6 | S5 | fidelity+evidence+simplicity | critical | 100 | AC7 completion semantics broken: manual post-ship pilot counted as done pre-ship; validate-all claims coverage it cannot perform | fixed — AC7 is a pre-ship fixture eval (checks/fixtures/ + rubric); user migration moved to post-ship follow-up; validate-all reads recorded evidence | AC7 vs tasks.md §7; merged evidence#8, simplicity#5 |
| R1-F7 | S5 | fidelity | critical | 78 | Obsidian global attachment path routes personal attachments into tracked `wiki/assets` | advisory (conf<80) — resolved by R1-F18's fix | spec.md Obsidian config |
| R1-F8 | S6 | fidelity | major | 100 | Routine claims rely on an uncached page — routines mirror absent from KB | fixed — routines mirrored to ai-docs/anthropic/routines.md, registered, cited in KB References | decisions.md KB References note |
| R1-F9 | S6 | fidelity | major | 99 | Cached skills mirror does not document `argument-hint`/`model`/`effort`; Grounds column over-claims | fixed — skills mirror refreshed 2026-08-07 (contains the frontmatter reference); Grounds corrected | verified: pre-refresh mirror lacks the frontmatter reference |
| R1-F10 | S6 | fidelity | major | 97 | Namespaced `/<dir>:<name>` and `/harness-layer:kb add` grounded by observation, not cached docs | fixed — grounding reworded: skills naming table + repo-convention scope note (decisions.md) | decisions.md cross-check note |
| R1-F11 | S2 | evidence | major | 99 | ac1 script samples hypothetical paths; no `git ls-files` proof the personal namespace has zero tracked files; not all domains covered | fixed — ac1 adds git ls-files zero-tracked proof, all six domains, workspace variants, personal index/log/assets | checks/ac1-privacy-gitignore.sh |
| R1-F12 | S2 | evidence | major | 100 | ac2 script reduces compound shapes to unscoped substrings; malformed seeds pass | fixed — ac2 parses sections/tables, personal pointer, log contract incl. source path, both app.json keys | checks/ac2-seed.py |
| R1-F13 | S2 | evidence | major | 99 | ac3 script doesn't assert exact per-command contracts; unplanned commands pass | fixed — exact contracts consolidated into test_wiki_layer.py (registry + frontmatter vs roster; unplanned files rejected); ac3 script dropped | checks/ac3-commands.py |
| R1-F14 | S2 | evidence | critical | 100 | No eval-tier proof for command bodies — all four operations could pass with nonfunctional prose | fixed — eval-tier pilot: committed fixtures + rubric, pilot-eval task pre-ship, evidence in implementation-notes.md | tasks.md §3–4 vs test-tiers.md |
| R1-F15 | S2 | evidence | major | 100 | ac4 script keyword-presence proves nothing about the rule's normative content | fixed — structured assertions moved to test_standards_rule in the drift test; ac4 script dropped | checks/ac4-standards-rule.py |
| R1-F16 | S2 | evidence | major | 100 | ac5 script uses global markers; no section scoping, no line-budget assertion | fixed — ac5 asserts section-scoped ordering/obligations, all four command pointers, size budget | checks/ac5-memory-amendments.py |
| R1-F17 | S2 | evidence | major | 96 | Drift test derives its expected set from the directory under test — vacuous boundary | fixed — expected set re-derived from AGENTS.md registration; roster parsed from model-selection.md; non-empty required | tasks.md §6 |
| R1-F18 | S3 | simplicity | major | 99 | Personal-domain page/op titles leak into tracked shared index.md/log.md | fixed — personal keeps local-only personal/index.md + personal/log.md; shared index holds only a pointer (spec seed shapes, tasks §1–3, rule contract) | spec.md seed shapes vs privacy decision |
| R1-F19 | S3 | simplicity | major | 96 | Log vocabulary permits `query\|status` entries while query is strictly read-only | fixed — log vocabulary restricted to ingest\|lint; query/status never write (spec seed shapes, tasks §4) | spec.md seed shapes vs tasks.md §4 |
| R1-F20 | S3 | simplicity | major | 97 | Status must report a backlog no state tracks (no source inventory or processed-state mapping) | fixed — triggers redefined over derivable state: sources.yaml vs page sources, lint-log flags (tasks.md §4) | tasks.md §4 |
| R1-F21 | S3 | simplicity | major | 94 | Duplicate-ingest idempotency lacks a stable source identity (title-only log key) | fixed — identity = canonical source path in page sources: and log entries (spec Edge Cases, tasks §3) | spec.md Edge Cases |
| R1-F22 | S3 | simplicity | minor | 90 | Empty-wiki pilot demands a wikilink its fixture can't guarantee | advisory — resolved by R1-F6's two-fixture design | AC7 |
| R1-F23 | S3 | simplicity | minor | 99 | appearance.json named in a task but has no content contract | advisory | tasks.md §1 |
| R1-F24 | S8 | simplicity | major | 97 | Same structural assertions maintained in two permanent layers (ac3/ac4 scripts + drift test) | fixed — single durable home: drift test owns structural assertions; ac3/ac4 scripts removed; AC3/AC4 point at pytest nodes | checks vs tasks.md §6 |
| R1-F25 | S8 | simplicity | minor | 96 | Batch ingestion + checkpoint machinery exceed the v1 objective | advisory | tasks.md §3 |
| R1-F26 | S8 | simplicity | minor | 91 | `related` frontmatter duplicates the graph body wikilinks already express | advisory | spec.md frontmatter contract |
| R1-F27 | S8 | simplicity | minor | 96 | New AGENTS.md section repeats what the rewritten KB bullets establish | advisory | spec.md AGENTS amendments |
| R1-F28 | S8 | simplicity | minor | 96 | Dataview/Marp made normative + test-required though no v1 behavior needs them | advisory | tasks.md §2, AC4 |
| R1-F29 | S8 | simplicity | minor | 93 | Fixed retrieval numbers (3–8 pages, 2 hops) add policy without improving the objective | advisory | tasks.md §4 |
| R2-F1 | S2 | delta | major | 99 | ac2 Personal section allowed extra content beyond the pointer; partial regex matches | fixed (unverified) — Personal body asserted to be exactly one pointer line; exact table header + separator rows; complete writer-op set asserted | checks/ac2-seed.py |
| R2-F2 | S2 | delta | major | 99 | Drift test asserted roster membership, not each command's exact model/effort | fixed (unverified) — operations table added to the standards rule as source of truth; test compares command frontmatter to it exactly, plus legality vs model-selection.md | tasks.md §2, §6 |
| R2-F3 | S2 | delta | major | 99 | test_standards_rule omitted most AC4 obligations | fixed (unverified) — §6 enumerates section-scoped assertions for every AC4 obligation | tasks.md §6 |
| R2-F4 | S2 | delta | major | 100 | ac5 budget measured only the Wiki Layer section, not the ≤14-line total | fixed (unverified) — ac5 asserts the exact prescribed fragments (replacements net 0) and computes the full added-line budget | checks/ac5-memory-amendments.py |
| R2-F5 | S3 | delta | major | 98 | Status consumed lint-log fields no contract defined | fixed (unverified) — log contract defines the lint entry form + payload line; lint writes it, status reads it | spec.md seed shapes, tasks.md §3–4 |
| R2-F6 | S2 | delta | critical | 100 | Single pilot run claimed the eval tier; test-tiers requires a pass rate over repeated runs | fixed (unverified) — AC7 is three fresh-session runs, 3/3 rubric pass rate, per-run evidence | tasks.md §7, AC7, pilot-rubric.md |
| R2-F7 | S5 | delta | minor | 100 | spec.md Objective still says "five plan-local checks" (three remain) | advisory | spec.md Objective |
| R2-F8 | S5 | delta | minor | 100 | spec.md still calls sources.yaml untouched / routines a KB gap after the gap-fill | advisory | spec.md Relevant Files, Notes |
