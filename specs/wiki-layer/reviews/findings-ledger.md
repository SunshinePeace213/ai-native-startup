# Findings Ledger: wiki-layer

Round 1 (spec panel, gpt-5.6-sol/high, reviewed head `fcc015b`): 31 raw findings
across three lenses; evidence#8 and simplicity#5 merged into R1-F6 (same defect
class, same target). No lens substitutions. Verdict: changes-requested
(19 blocking, 10 advisory).

| ID | STD | Lens | Sev | Conf | Finding | Disposition | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| R1-F1 | S4 | fidelity | major | 98 | Lint's required checks omit the locked secret/PII scan | open | tasks.md §3 vs decisions.md privacy assumption |
| R1-F2 | S4 | fidelity | major | 98 | Status implements only the absorb trigger, not all three locked expansion triggers | open | tasks.md §4 vs decisions.md expansion policy |
| R1-F3 | S4 | fidelity | minor | 92 | Routine contract wording weakened (fresh-clone + claude/-branch PR not restated in task) | advisory | tasks.md §3 vs decisions.md |
| R1-F4 | S5 | fidelity | major | 99 | "≥1 source per claim-bearing page" contradicts locked "every claim cites ≥1 source" | open | tasks.md §2 vs decisions.md metrics |
| R1-F5 | S5 | fidelity | minor | 100 | Lint task says "run /kb"; the command is `/harness-layer:kb` | advisory | tasks.md §3 vs spec.md Edge Cases |
| R1-F6 | S5 | fidelity+evidence+simplicity | critical | 100 | AC7 completion semantics broken: manual post-ship pilot counted as done pre-ship; validate-all claims coverage it cannot perform | open | AC7 vs tasks.md §7; merged evidence#8, simplicity#5 |
| R1-F7 | S5 | fidelity | critical | 78 | Obsidian global attachment path routes personal attachments into tracked `wiki/assets` | advisory (conf<80) — resolved by R1-F18's fix | spec.md Obsidian config |
| R1-F8 | S6 | fidelity | major | 100 | Routine claims rely on an uncached page — routines mirror absent from KB | open | decisions.md KB References note |
| R1-F9 | S6 | fidelity | major | 99 | Cached skills mirror does not document `argument-hint`/`model`/`effort`; Grounds column over-claims | open | verified: pre-refresh mirror lacks the frontmatter reference |
| R1-F10 | S6 | fidelity | major | 97 | Namespaced `/<dir>:<name>` and `/harness-layer:kb add` grounded by observation, not cached docs | open | decisions.md cross-check note |
| R1-F11 | S2 | evidence | major | 99 | ac1 script samples hypothetical paths; no `git ls-files` proof the personal namespace has zero tracked files; not all domains covered | open | checks/ac1-privacy-gitignore.sh |
| R1-F12 | S2 | evidence | major | 100 | ac2 script reduces compound shapes to unscoped substrings; malformed seeds pass | open | checks/ac2-seed.py |
| R1-F13 | S2 | evidence | major | 99 | ac3 script doesn't assert exact per-command contracts; unplanned commands pass | open | checks/ac3-commands.py |
| R1-F14 | S2 | evidence | critical | 100 | No eval-tier proof for command bodies — all four operations could pass with nonfunctional prose | open | tasks.md §3–4 vs test-tiers.md |
| R1-F15 | S2 | evidence | major | 100 | ac4 script keyword-presence proves nothing about the rule's normative content | open | checks/ac4-standards-rule.py |
| R1-F16 | S2 | evidence | major | 100 | ac5 script uses global markers; no section scoping, no line-budget assertion | open | checks/ac5-memory-amendments.py |
| R1-F17 | S2 | evidence | major | 96 | Drift test derives its expected set from the directory under test — vacuous boundary | open | tasks.md §6 |
| R1-F18 | S3 | simplicity | major | 99 | Personal-domain page/op titles leak into tracked shared index.md/log.md | open | spec.md seed shapes vs privacy decision |
| R1-F19 | S3 | simplicity | major | 96 | Log vocabulary permits `query\|status` entries while query is strictly read-only | open | spec.md seed shapes vs tasks.md §4 |
| R1-F20 | S3 | simplicity | major | 97 | Status must report a backlog no state tracks (no source inventory or processed-state mapping) | open | tasks.md §4 |
| R1-F21 | S3 | simplicity | major | 94 | Duplicate-ingest idempotency lacks a stable source identity (title-only log key) | open | spec.md Edge Cases |
| R1-F22 | S3 | simplicity | minor | 90 | Empty-wiki pilot demands a wikilink its fixture can't guarantee | advisory — resolved by R1-F6's two-fixture design | AC7 |
| R1-F23 | S3 | simplicity | minor | 99 | appearance.json named in a task but has no content contract | advisory | tasks.md §1 |
| R1-F24 | S8 | simplicity | major | 97 | Same structural assertions maintained in two permanent layers (ac3/ac4 scripts + drift test) | open | checks vs tasks.md §6 |
| R1-F25 | S8 | simplicity | minor | 96 | Batch ingestion + checkpoint machinery exceed the v1 objective | advisory | tasks.md §3 |
| R1-F26 | S8 | simplicity | minor | 91 | `related` frontmatter duplicates the graph body wikilinks already express | advisory | spec.md frontmatter contract |
| R1-F27 | S8 | simplicity | minor | 96 | New AGENTS.md section repeats what the rewritten KB bullets establish | advisory | spec.md AGENTS amendments |
| R1-F28 | S8 | simplicity | minor | 96 | Dataview/Marp made normative + test-required though no v1 behavior needs them | advisory | tasks.md §2, AC4 |
| R1-F29 | S8 | simplicity | minor | 93 | Fixed retrieval numbers (3–8 pages, 2 hops) add policy without improving the objective | advisory | tasks.md §4 |
