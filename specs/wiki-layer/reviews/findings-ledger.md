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

Impl round 1 (panel, gpt-5.6-sol/high, reviewed head `2400a83`, range
`b62cf9a..2400a83`): impl lint clean (0 findings). 26 raw lens findings; four
cross-lens merges (fidelity#4+simplicity#2 → I1-F4; fidelity#6+simplicity#3 →
I1-F6; fidelity#10+evidence#5 → I1-F10). No lens substitutions. Security pass:
full (claude-security agent over the same range) — its findings join this
sequence from I1-F24: 1 surviving finding (26 candidates, 24 refuted, 1 below
the vote threshold), plus two validation-script facts entered as findings —
both lead-verified (the check-ignore behavior reproduced in a scratch repo).
The surviving security finding exposed a missing standard; I9 added to
impl-standards.md this run (self-improve). Verdict: changes-requested
(13 blocking, 9 advisory, 4 disputed — disputes carry this run to the human
gate per the gate contract).

| ID | STD | Lens | Sev | Conf | Finding | Disposition | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| I1-F1 | I6 | fidelity | major | 100 | harness-build.md mirror-copy edit flagged as drive-by beyond the wiki-layer boundary | disputed — the edit is the memory step's routing per AGENTS.md ## Lessons / memory-series.md (pipeline-process lesson → the file it corrects), documented in implementation-notes.md's memory-step entry; reverting would break the standing memory contract | notes memory-step entry; AGENTS.md ## Lessons |
| I1-F2 | I5 | fidelity | major | 96 | Nested `.claude/commands/wiki/` → `/wiki:*` resolution not traced to a cited official doc | disputed — settled at spec gate R1-F10 and approved at the spec human gate: grounded by the skills mirror's namespaced-invocation table plus the repo's own working `/harness-layer:*` convention (decisions.md cross-check scope note); no new evidence | decisions.md ## KB References cross-check |
| I1-F3 | I5 | fidelity | minor | 98 | `opus`/`sonnet`/`haiku` alias values not enumerated by any cited KB doc (skills.md defers to /model) | advisory | skills.md:269; KB References table |
| I1-F4 | I1 | fidelity+simplicity | major | 99 | Ingest idempotency branches incoherent: KEY matched against INDEX which never stores source paths; "update in place + bump `updated:`" vs "identical run leaves tree unchanged" undistinguished; workflow step 6 appends the log entry unconditionally | fixed — KEY matched only in page sources:/LOG; three explicit branches (first / changed-source / identical no-op); workflow steps branch-conditional (81059eb) | ingest.md:22-36,51-59 |
| I1-F5 | I1 | fidelity | major | 100 | Lint contradiction handling has two outcomes: Checks says flag both sides `disputed`; Fix-or-report lists contradictions as report-only "without rewriting the pages" | fixed — disputed flags + cross-link listed as mechanical fixes; only resolution stays judgment (81059eb) | lint.md:33-34,46-50 |
| I1-F6 | I1 | fidelity+simplicity | major | 98 | Seed-only lint "report clean and stop" exits before the mandatory Log-the-pass append | fixed — seed-only run skips checks but appends the clean log entry and reports (81059eb) | lint.md:18-20 vs 52-60 |
| I1-F7 | I1 | fidelity | major | 100 | Status seed-only branch reports "no triggers fired" though absorb (backlog >10, ~53 uncited manifest entries) must fire from tracked state | fixed — absorb computed on every run from MANIFEST + page sources:; seed/no-history exceptions scoped to breakdown/cleanup (81059eb) | status.md:26,31 |
| I1-F8 | I1 | fidelity | major | 96 | Orphan defined differently in lint (no index row AND no inbound wikilink) and status (`related:`-based incl. outgoing) | fixed — one definition in both files: no inbound [[wikilink]]; missing index row stays index-drift (81059eb) | lint.md:24 vs status.md:22 |
| I1-F9 | I1 | fidelity | minor | 100 | Four empty seed domain tables carry a literal `\| --- \|` data row after the delimiter | advisory | ai-docs/wiki/index.md:16,22,28,34 |
| I1-F10 | I1 | fidelity+evidence | major | 100 | AC7 runs 2–3 recorded without per-run query answer/citation targets or lint output; run 2 says "page count 4 → 4" against a two-page pilot | fixed — appended review-fix evidence entry: names what was summary-only, clarifies 4→4 as tracked files (git ls-files), corroborates AC7 residue with literal commands/output; past entries untouched (81059eb) | implementation-notes.md:117-177 |
| I1-F11 | I2 | evidence | major | 99 | AC7 validation command is a `manual:` narrative, not a runnable identifier | disputed — I2 explicitly provides for `manual:` checks with output recorded in implementation-notes.md; AC7 is eval-tier by locked spec design (R2-F6, approved at the spec human gate) and its output is recorded (impl lint notes-evidence PASS) | impl-standards.md I2; test-tiers.md eval row |
| I1-F12 | I2 | evidence | major | 98 | Drift test never asserts non-empty `description`/`argument-hint` (AC3 requires non-empty description); read-only check is an unanchored substring match | fixed — non-empty description/argument-hint asserted; read-only check anchored to the declaration line (81059eb) | test_wiki_layer.py:140-186 |
| I1-F13 | I2 | evidence | major | 95 | test_standards_rule asserts isolated keywords, omitting flat tone/quote discipline/length bounds | disputed — the test implements exactly the section-scoped assertion set tasks.md §6 enumerates (locked at spec gate R2-F3) and covers every obligation AC4 states; the privacy claim is factually wrong (assertions are section-scoped, four distinct obligations) | tasks.md §6; acceptance-criteria.md AC4 |
| I1-F14 | I2 | evidence | major | 100 | ac5 budget check measures its own hardcoded list (`added = len(WIKI_SECTION_LINES)`), never the real AGENTS.md diff | fixed — budget measured from the real ## Wiki Layer section in AGENTS.md; replaced bullets asserted single-line; negative cases demonstrated on temp copies (15-line section FAILs) (81059eb) | ac5-memory-amendments.py:96 |
| I1-F15 | I3 | evidence | major | 100 | Hand-off entries abbreviate commands with ellipses (`python -c "…split('---')[1]…"`); validate-all records label-level results only | fixed — same evidence entry re-runs every re-runnable command verbatim with literal outputs; unrecoverable transcripts stated as not captured (81059eb) | implementation-notes.md:42-98,178-185 |
| I1-F16 | I8 | evidence | major | 100 | ac5 check derives its budget result from hard-coded expected data; cannot fail on a 15-line amendment | fixed — same change as I1-F14; result now derives from the subject under test (81059eb) | ac5-memory-amendments.py:94-98 |
| I1-F17 | I8 | evidence | major | 99 | MD024 log fix landed with no committed regression assertion (verification was an uncommitted scratch-copy proof) | fixed — ac2-seed.py asserts the seed log carries the MD024 file-local disable (81059eb) | commit 992587f; log.md |
| I1-F18 | I4 | simplicity | major | 98 | Command bodies restate schema/citation/status/privacy/writing rules wiki-standards.md owns (which loads on any wiki read) | fixed — genuine restatement trimmed to STANDARDS pointers; every plan-prescribed behavior kept (check classes, URL refusal, index/log split, gate, checkpoints, redact-then-report) (81059eb) | ingest.md:29-43, lint.md:28-42, query.md:23, status.md:20,32 |
| I1-F19 | I4 | simplicity | minor | 100 | lint.md log prose requires a blank line the fenced example omits | advisory | lint.md:54-60 |
| I1-F20 | I4 | simplicity | minor | 97 | Commands repeat the same procedure across Instructions and Workflow sections | advisory | query.md, status.md, ingest.md |
| I1-F21 | I4 | simplicity | minor | 96 | Personal lint split-logging expressed colloquially; shared-scope handling under-specified | advisory | lint.md:65-66 |
| I1-F22 | I4 | simplicity | minor | 94 | Rationale-heavy prose in changed harness text (motivations/history instead of instructions) | advisory | wiki-standards.md, ingest.md, lint.md, harness-build.md |
| I1-F23 | I4 | simplicity | info | 96 | Non-fluent shorthand ("pages no index row…", "logs that half") | advisory | lint.md:24,65 |
| I1-F24 | I9 | sec | major | 90 | Ingest has a write-capable agent read third-party source content (mirrors, clipped captures, local files) with no treat-as-data instruction and no write confinement — a poisoned source persistently poisons the wiki every session reads first | fixed — data-not-directives + writes-confined-to-ai-docs/wiki/ in ingest.md; matching obligation in wiki-standards.md Privacy; lint gains the report-not-follow guard (81059eb) | ingest.md:51; CLAUDE-SECURITY-20260807-050658 F1, 3-verifier unanimous (impact MEDIUM → major: wiki-first reads propagate the poisoning) |
| I1-F25 | I6 | sec | minor | 100 | ac2-seed.py carries a dead `if … : pass` branch (the writer-op contract is enforced by the surrounding checks) | advisory | ac2-seed.py:84-85 |
| I1-F26 | I2 | sec | minor | 100 | ac1's four `&& fail` probes on tracked paths are inert — `git check-ignore` exits 1 for tracked files regardless of patterns, so a removed negation can't fire them (untracked-path probes and the personal-domain direction still hold) | advisory | ac1-privacy-gitignore.sh:34,38-41; lead scratch-repo repro |
