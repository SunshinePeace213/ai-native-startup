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
