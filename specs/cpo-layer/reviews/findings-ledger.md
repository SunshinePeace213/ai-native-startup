# Findings Ledger: cpo-layer (studio-layer)

Spec flavor. One row per finding, IDs stable across rounds.
Blocking = severity `critical`/`major` with confidence ≥ 80. Everything else is advisory.

Round 1 — `gpt-5.6-sol` at `xhigh`, reviewed head `bf76b7e`. 35 findings: 21 blocking,
14 advisory. Fixes committed in the round-1 fix series.

| ID | Sev | Conf | Finding | Disposition | Evidence |
| --- | --- | --- | --- | --- | --- |
| R1-F1 | critical | 99 | Hook gets a phase but no client/project identifier; Stop input carries no command args, so it cannot pick among several client projects | fixed | spec.md `## Interfaces & Contracts` → "Project targeting"; three-step cwd→sole-project→exit-2 rule; AC8 adds the two-simultaneous-projects case |
| R1-F2 | major | 99 | One `Artifact SHA` cannot verify the example's two approved files; `Approves` unvalidated | fixed | sign-off schema replaced with a mandatory one-row-per-artifact table (path + sha256) |
| R1-F3 | major | 98 | States matrix, token table, tap targets, discovery notes, triage rows, revision allowance, revision log and change orders have no schemas | fixed | spec.md `## Interfaces & Contracts` now specifies each machine-readable format and its path |
| R1-F4 | major | 99 | P1 never invokes `check_question_coverage.py` — the mechanism is orphaned | fixed | tasks.md `studio-phase-commands` requires P1 to run it before its soft gate; AC6 asserts the invocation |
| R1-F5 | major | 97 | `studio-design-qa` "blocks handoff" but nothing enforces it | fixed | QA report contract added; the p6 gate blocks on unresolved blocking findings; AC15 added |
| R1-F6 | major | 99 | Skill and eight commands are non-deterministic prose with no eval tier, contrary to test-tiers.md | fixed | AC16 adds `manual:` eval cases with a rubric for the bank and the P1/P2 commands |
| R1-F7 | major | 96 | One-level-deep is unenforced — subagents inherit the Agent tool | fixed | every role sets `disallowedTools: Agent`; AC3 asserts it |
| R1-F8 | major | 98 | "Either spawn shape works" is false for effort: teammates do not take effort from the agent file | fixed | teammates dropped entirely — see R1-F9 |
| R1-F9 | info | 99 | A plain subagent already starts without the lead's conversation history, so the agent-team dependency buys no isolation | fixed | adopted — the cold-designer check is an ordinary subagent; the experimental agent-teams dependency is gone |
| R1-F10 | major | 98 | Plan contradicts itself: P2 the only teammate vs P4 the clear teammate case | fixed | one spawn policy — subagents everywhere — in spec.md Requirement 3, decisions.md, and tasks.md |
| R1-F11 | major | 99 | tasks.md cites a "phase table in spec.md" that does not exist | fixed | spec.md `## The eight phases` table added and referenced by ID |
| R1-F12 | major | 98 | Exit 2 on a bad phase argument violates the repo hook contract (config failures fail open) | fixed | unknown/missing phase → exit 0; `test_wiring.py` catches bad registrations |
| R1-F13 | major | 97 | `stop_hook_active` re-entry undefined; Claude force-ends after 8 consecutive blocks | fixed | hooks.md:2171 grounded; block on first entry, allow with a warning on re-entry; both values tested |
| R1-F14 | major | 99 | ac1 compares two runs that both already have client folders, so an always-blocking hook passes | fixed | script now takes a no-client baseline on a complete plan folder and asserts exit 0 stays 0 |
| R1-F15 | minor | 100 | ac1 used `rm -rf`, violating the repo safe-delete rule | fixed | recursive force delete removed; cleanup is non-recursive plus a `mktemp -d` trap |
| R1-F16 | major | 99 | ac4 passes with extra rows, one phase band, labels outside the table, one generic copy-as-prompt mention | fixed | table parsed structurally: exactly four rows, both phase bands, a return contract per row |
| R1-F17 | minor | 97 | ac4 silently skips the "original untouched" assertion when no base branch resolves | fixed | missing base is now a failure, not a skip |
| R1-F18 | major | 99 | ac5 scans only top-level `*.md` while rules are discovered recursively | fixed | recursive `find` over `.claude/rules/studio-layer/` |
| R1-F19 | major | 99 | ac7 only requires a top-level `hooks:` key — a PreToolUse registration would pass | fixed | YAML-parsed assertion on `hooks.Stop[*].hooks[*]` type, command and phase argument |
| R1-F20 | major | 97 | AC11–AC12 quantify only declared rows, so an empty inventory passes vacuously | fixed | both criteria now require a non-empty inventory and cross-check every component and token pair |
| R1-F21 | major | 96 | studio-identity content and the AGENTS.md pointer are untested | fixed | AC5 extended to assert name, voice, letterhead, sign-off contract and the hub pointer |
| R1-F22 | major | 82 | Skill directory name, not `name:`, becomes the command — path and intended name disagree | fixed | skills.md:120 grounded; directory renamed to `studio-client-questions/` so both agree |
| R1-F23 | major | 95 | Plan claims WCAG behavior while deferring the WCAG mirror and hard-coding "commonly published" thresholds | fixed | restated as project thresholds with their source named; card 11 will replace them with a cited mirror |
| R1-F24 | major | 97 | "Every decision is locked" contradicts the open P5 prototype-tool question | fixed | P5 tool is now an explicit runtime input with selection rules; the locked-ledger claim is scoped to build-time decisions |
| R1-F25 | minor | 99 | Exit 2 described as argument-only but also used for malformed hex and missing allowance | fixed | exit 2 defined once as usage, parse, or invalid-input failure |
| R1-F26 | minor | 99 | "Every studio check exits 0 with no clients/" contradicts the CLI contract | fixed | the fail-open-with-no-clients rule now applies to the hook only |
| R1-F27 | minor | 99 | `validate-all` declares `Files: none` then writes implementation-notes.md | fixed | the file is listed and the task marked evidence-writing |
| R1-F28 | minor | 100 | `PR:` placeholder in `## Tracking`, which forbids placeholders | fixed | row removed until a real number exists |
| R1-F29 | minor | 99 | Requires the AGENTS.md budget "unchanged" while another task adds a section | fixed | restated as remaining under the ~250-line limit |
| R1-F30 | minor | 98 | Risk section says "two changes reach outside the namespace", omitting four more | fixed | all six cross-namespace changes enumerated with rollback impact |
| R1-F31 | minor | 91 | Cited agent-teams lines do not ground "a teammate cannot prompt the user" | fixed | claim dropped with the teammate design; remaining citations narrowed to what the lines say |
| R1-F32 | minor | 84 | No cached source grounds custom-command frontmatter (`argument-hint`, `hooks:`) | fixed | KB gap recorded explicitly; those fields are grounded on the repo's own working commands, and a `/harness-layer:kb add` follow-up is flagged |
| R1-F33 | info | 98 | The HTML-artifacts article does not ground the four project-specific page-pattern rows | fixed | Grounds cell narrowed to the two-way page + copy-as-prompt pattern; the four mappings marked project decisions |
| R1-F34 | minor | 95 | Validation commands use whole files and `-k` filters rather than exact node IDs | fixed | every criterion now names exact `path::test_name` node IDs; the full-suite command stays only on AC14 |
| R1-F35 | minor | 78 | Path scope alone does not prove rules load when a client project's first file is created | advisory | below the blocking confidence bar; the phase commands read the identity rule explicitly, which covers the practical case |

Round 2 — delta on `bf76b7e..c53b35d`, `gpt-5.6-sol` at `high`. 12 findings: 6 blocking,
6 advisory. Every round-1 disposition held; no finding was reopened. Fixes committed in the
round-2 fix series. The 2-round cap is now reached, so these fixes were **not** re-verified by
a further Codex round — that is the one thing the human gate is being asked to accept.

| ID | Sev | Conf | Finding | Disposition | Evidence |
| --- | --- | --- | --- | --- | --- |
| R2-F1 | critical | 99 | A directory counted as a project only if `sign-off/` already existed, so a never-signed project looked like zero projects and failed open on its first hard gate | fixed | spec.md "Project targeting": a project is any dir two levels under `clients/`, independent of `sign-off/`; AC8 adds `test_project_without_signoff_dir_still_blocks` |
| R2-F2 | minor | 100 | The mandatory-SHA example used abbreviated `…` hashes, contradicting the 64-hex requirement | fixed | both example hashes are now full 64-character hex |
| R2-F3 | major | 98 | The change-order schema required fields that AC13 never validated — any existing file bought a round | fixed | four required fields specified; the counter parses them; AC13 adds incomplete- and unsigned-change-order cases |
| R2-F4 | major | 99 | Markdown eval files had no runner and ignored the repo's committed `evals/evals.json` harness, so the claimed pass rates were not reproducible | fixed | evals move to `evals/evals.json` beside the skill and the commands, run by the meta-skills runner; new `checks/ac16-evals-are-runnable.sh` asserts the schema and a machine-checkable assertion per case |
| R2-F5 | major | 98 | ac3's line-based check missed a multiline `tools:` list containing `Agent` | fixed | replaced with a YAML parser; verified against a multiline `- Agent` fixture that the grep passed and the parser rejects |
| R2-F6 | major | 99 | tasks.md still told the builder to "spawn one teammate" for P2, contradicting the no-teams policy | fixed | P2's cold-designer test now spawns `studio-ux-architect` as an ordinary subagent |
| R2-F7 | major | 98 | AC11–AC12 still let a one-component matrix or one token pair pass; no authoritative inventory existed | fixed | `handoff/inventory.md` added as the authoritative component/token list; both checks cross-check every component × breakpoint and every named token, and exit 2 on an empty inventory |
| R2-F8 | minor | 96 | ac4's substring label matching let one row carry two required labels while an unrelated row rode along | fixed | exact multiset comparison; verified against a two-labels-in-one-row fixture |
| R2-F9 | minor | 100 | tasks.md applied the ~250-line budget to rules + AGENTS.md (301 today) while AC5 measured rules only at 280 | fixed | the budget applies to unscoped rules only; AGENTS.md is checked separately for a concise pointer |
| R2-F10 | minor | 99 | The unsupported "a teammate cannot prompt the user" claim survived in spec.md and decisions.md | fixed | removed from both; the principal-only rule now rests solely on the documented subagent `AskUserQuestion` limitation |
| R2-F11 | minor | 99 | Admitting a KB gap for custom-command frontmatter violates spec-standard 6 | fixed, and the standard amended | The fields *are* grounded — in `.claude/skills/meta-skills/references/frontmatter.md` (`argument-hint` l.26, `disable-model-invocation` l.30, `effort` l.33, `hooks` l.37), the same reference the discovery ledger cited. Round 2 read standard 6 as `ai-docs`-only; the repo's checked-in references are equally authoritative where the KB has no mirror, so **spec-standards.md #6 was amended in this run** to accept them and to require naming the gap explicitly. `kb-fetcher` was unavailable this session, so mirroring the official page stays a follow-up. |
| R2-F12 | minor | 100 | AC2, AC8 and AC10 still ran whole pytest files; node ids listed as prose are not executable | fixed | all three now pass complete `path::test_name` arguments; `test_model_drift.py` stays whole-file by design and says why (it is parametrized, so node ids are generated) |

Round 3 — delta on `c53b35d..4ef241a`, `gpt-5.6-sol` at `medium`. This round verified the
round-2 fixes, which the prior run left unverified at its cap, plus a revision commit fixing
three defects found by self-check before the round ran (the AC16 lint command could not resolve
its target; tasks.md still named the removed `specs/cpo-layer/evals/` path; the check count was
stale). 3 findings, all blocking. Every round-1 and round-2 disposition held; nothing reopened.

| ID | Sev | Conf | Finding | Disposition | Evidence |
| --- | --- | --- | --- | --- | --- |
| R3-F1 | major | 99 | The commands eval suite had no runner — `ac16-evals-are-runnable.sh` only validates JSON, and running a case's `check` grades nothing because no step executes the prompt to produce output | fixed | confirmed: `eval.py:143` requires a `SKILL.md` and `run_behavior_eval.py:85` stages into `.claude/skills/<name>`, so a command directory is unreachable by either. Added `run_command_evals.py` (contract in spec.md `## Interfaces & Contracts`), task 10, AC16's two commands, and a runner-exists assertion in the ac16 check |
| R3-F2 | major | 98 | The component inventory was only *declared* authoritative — a one-component inventory made a one-component matrix pass, and no task derived it from or included it in the signed P3 artifacts | fixed | the inventory moves to `structure/inventory.md` as a **P3 deliverable signed by the client**: enumerated from the signed wireframes and content model, its SHA recorded in the P3 sign-off table, and the p3 gate blocks without it. P6 now quantifies over a list approved a phase earlier instead of one it authored. AC9 gains three p3 tests; AC11–AC12 point at the signed path |
| R3-F3 | major | 97 | AC13 still read "exits 0 when a change order is present", contradicting R2-F3's four-required-field contract and its own incomplete/unsigned tests | fixed | AC13 now requires a complete, parseable change order for the allow path and names the four fields; presence alone no longer buys a round |
