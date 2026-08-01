# Findings Ledger: cpo-layer (studio-layer)

One row per finding, IDs stable across rounds and flavors. Spec-flavor rounds carry
`R<N>-F<M>` ids; implementation-flavor rounds carry `I<N>-F<M>`.
Blocking = severity `critical`/`major` with confidence ≥ 80. Everything else is advisory.

## Spec flavor

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

Round 4 — delta on `4ef241a..f15d985`, `gpt-5.6-sol` at `medium`. 2 findings, both blocking,
both genuine holes in the round-3 fixes rather than new scope. Every earlier disposition held;
nothing reopened. This run's 2-round allowance is now spent, so the round-4 fixes below were
**not** re-verified by a further Codex round — that is the one thing the human gate is being
asked to accept.

| ID | Sev | Conf | Finding | Disposition | Evidence |
| --- | --- | --- | --- | --- | --- |
| R4-F1 | major | 99 | R3-F2 was only half-fixed: the p3 gate checked the inventory's signed SHA, but P6 read the current file, so rows deleted between P3 and P6 shrank the denominator with no gate noticing | fixed | the `p6` gate now re-reads the P3 sign-off, recomputes the inventory's SHA-256, and blocks on a mismatch. spec.md "Component inventory" states why signing at P3 alone is insufficient; AC9 gains `test_p6_inventory_mutated_after_p3_signoff_blocks` and `test_p6_inventory_matching_p3_sha_allows` |
| R4-F2 | major | 97 | The command-eval runner staged the studio namespace but omitted `.claude/hooks/check_gate_signoff.py`, which the evaluated P2 command's frontmatter registers — so the eval would measure P2 with its gate silently absent | fixed | the hook joins the staged set in spec.md "Command-eval runner" and task 10, with a test asserting the P2 command's registered hook path resolves to a real file inside the scratch project |

---

## Implementation flavor

Round 1 — `gpt-5.6-sol` at `xhigh`, reviewed head `339b2c5`, diff `fb5e6ea..339b2c5`.
22 findings: 13 blocking, 9 advisory. Check scripts (7/7 exit 0) and the full suite
(990 passed, 2 skipped) contributed no findings of their own.

| ID | Sev | Conf | Finding | Disposition | Evidence |
| --- | --- | --- | --- | --- | --- |
| I1-F1 | major | 100 | AC16's commands-suite `manual:` eval scored 0.8889 against a required 1.0, so AC16 and impl-standard 2 are unmet — the build disclosed this rather than papering over it | fixed | **AC16 now meets its bar.** `eval-0` 1.0 and `eval-1` 1.0, each needing 1.0, over 6 `claude -p` runs, `EVAL_EXIT=0` — up from 0.8889 through 0.9444. Three assertion-level causes were separated rather than lumped: `a3` demanded one literal phrasing (`N/A, because`) the contract does not require and graded it through a brittle `grep -A4` window; `b4` asked a judge to confirm a **process** (a subagent saw only the briefs) from artifacts carrying no process trace; `a5` was a fair assertion the command genuinely failed. `a3` and `b4` were corrected to test what the contract and the artifacts actually support, and P2 now writes the cold designer's reply verbatim to `definition/cold-designer-plan.md` so `b4` is checkable at all. `a5` was left untouched and `p1-discovery.md`'s glossary instruction was fixed instead — the command was under-performing, not the assertion over-specifying |
| I1-F2 | major | 100 | `build-brief.html` claims "16 of 16 with evidence" while its AC16 row is pending and the recorded eval failed | fixed | `build-brief.html`'s AC16 row now carries the real rate (`eval-0 1.0 · eval-1 1.0 … exit 0`) instead of "recorded separately"; no evidence row in the page is marked pending any more, so its "16 of 16 with evidence" headline is true rather than aspirational |
| I1-F3 | major | 99 | The hard gates accept **any one** signed artifact; the tests sign `docs/<phase>-approved.md`, so P2 closes without its briefs/sitemap, P3 without wireframes, P4 without the picked direction, P6 without the handoff pack | fixed | `REQUIRED_ARTIFACTS` per gated phase in `check_gate_signoff.py`, documented as a table in spec.md `### Sign-off document` (a floor, not a ceiling); each required row is hash-verified by the existing loop. 9 parametrized tests; the fixer restored the pre-fix hook and confirmed they fail against it. P2's set is project-brief + sitemap, matching the spec's Gate column ("brief + sitemap signed") and p2-definition.md:40 — the creative brief was deliberately excluded rather than making the hook demand what no command tells the principal to sign |
| I1-F4 | major | 100 | `check_revision_count.py` reads the allowance from the mutable current brief without verifying its P2-signed SHA; editing 2→3 is tested as an *allow* path, bypassing change orders | fixed | `allowance()` now refuses the brief unless `sign-off/p2.md` lists `definition/project-brief.md` and its SHA-256 still matches; parsed on `check_gate_signoff.py`'s own table schema so the gate and the counter read one document alike. The old test that asserted mutation as an *allow* path was removed and split into `test_brief_edited_after_signature_exits_2` (exit 2) and `test_allowance_is_re_derived_from_the_signed_brief` |
| I1-F5 | major | 99 | Round numbers are trusted, never counted or validated — rows all numbered `1` never exceed the allowance, so unlimited rounds pass | fixed | `numbered()` rejects non-positive, duplicate and non-contiguous round numbers as exit 2; verified against the pre-fix script, where three rows all numbered `1` against an allowance of 2 exited 0. 4 parametrized cases |
| I1-F6 | major | 99 | `Cost — rounds: 0` passes `\d+`, and one one-round change order can be reused by unlimited excess rounds — no capacity accounting | fixed | `Cost — rounds` must be ≥ 1, and `main()` groups excess rounds by resolved change-order path and fails when `len(uses) > bought`. A 2-round order legitimately covering two rounds still exits 0, so this is capacity arithmetic rather than a ban on reuse |
| I1-F7 | major | 99 | Commands use repo-relative `clients/$1` and `.claude/…` paths while the four gate commands instruct multi-project users to run *inside* `PROJECT_DIR`, where every one of those paths misresolves | fixed | Every command-body path anchored on `$(git rev-parse --show-toplevel)`. The first attempt used `"$CLAUDE_PROJECT_DIR"` and was rejected: it is empty in a command body (`echo` prints `[]`) and `ai-docs/anthropic/hooks.md:494` documents it for hooks, stdio MCP servers and plugin LSP servers only. The four frontmatter registration lines keep it — that one *is* a hook |
| I1-F8 | major | 98 | Only a missing `PROJECT` is rejected; `../` segments, absolute paths, dot segments or extra levels redirect writes outside `clients/<client>/<project>` | fixed | Each command validates `PROJECT` as exactly two segments, neither starting with `.` nor containing another `/`, rejected the same way a missing argument is |
| I1-F9 | major | 99 | Sign-off artifact paths are unconstrained, so absolute paths, `../` traversal and escaping symlinks can satisfy a client signature with files outside the project | fixed | `contained()` rejects absolute paths and `..` segments and requires the resolved target — symlinks followed — to sit beneath the resolved project root. Tests for absolute, traversal and escaping-symlink rows |
| I1-F10 | major | 99 | QA rows with blank or malformed cells (`blocking \| TBD`, `blocker \| open`) silently allow P6 — only the exact pair `blocking`/`open` blocks | fixed | `check_qa_report` validates both cells against `QA_SEVERITIES`/`QA_STATUSES` and reports any blank or out-of-enum value as its own blocking problem, so a row the gate cannot read never reads as resolved. Tests for malformed status, misspelled severity and a blank cell |
| I1-F11 | major | 99 | `check_contrast.py` token coverage scans the whole row including `Used for`, so a token passes by being mentioned in prose outside the colour cells | fixed | `token_names()` binds tokens from the Foreground/Background columns only; coverage is exact set membership. Verified: a token named only in `Used for` exited 0 pre-fix and now exits 1 |
| I1-F12 | major | 99 | `run_command_evals.py` stages `client-artifacts.md` but not the `artifacts.md` it inherits from, so P1/P2 are evaluated with a broken dependency | fixed | `.claude/rules/harness-layer/artifacts.md` joined the staged set, with `test_every_relative_link_in_the_staged_namespace_resolves_inside_the_scratch_project` asserting no staged rule has a dangling relative link |
| I1-F13 | major | 98 | A `claude -p` run marked as an error is recorded as `run_error` but its score still contributes normally, and the runner can still exit 0 | fixed | An errored envelope now zeroes every expectation before scoring, so a crashed run cannot score like a clean one |
| I1-F14 | minor | 97 | The allowance regex accepts any line starting with an integer, not the locked `(plus polish)` schema | advisory | Below the blocking bar; folded into the I1-F4/F5 fix since the same function was being rewritten |
| I1-F15 | minor | 98 | Short rows in `check_states_matrix.py` raise `IndexError` — a traceback and exit 1 instead of the contracted exit 2 | advisory | Below the blocking bar; folded into the same file's fix |
| I1-F16 | minor | 96 | Duplicate component/breakpoint rows overwrite earlier rows, hiding a blank or contradictory specification | advisory | Below the blocking bar; folded into the same file's fix |
| I1-F17 | minor | 96 | Reusing `--workspace` leaves prior-run output, so judge-only assertions can grade stale artifacts | advisory | Below the blocking bar; folded into the eval-runner fix |
| I1-F18 | minor | 95 | Schema validation rejects neither duplicate case IDs nor non-scalar IDs | advisory | Below the blocking bar; folded into the eval-runner fix |
| I1-F19 | minor | 100 | The routed glob lesson grew the unscoped rules 254→257 against the task's "must not grow" wording | advisory | Below the blocking bar, and the growth is the pipeline's own mandated memory step: `memory-series.md` requires a build lesson to be routed to the rule where it reloads. AC5 enforces a ~280-line budget and the rules sit at 257. Recorded as a follow-up to reconcile the task's wording with the budget the check actually enforces |
| I1-F20 | minor | 99 | AC5 accepts invalid scopes such as `clients/**bogus` via substring grep and relaxes the stated budget to 280 | advisory | Below the blocking bar; recorded as a follow-up — the check is plan-local and its budget number is the one AC5 documents |
| I1-F21 | info | 94 | P6's Stop gate never runs the states and contrast checks, so a signed handoff with a failing matrix can close if the command skipped its prose instructions | advisory | Genuine design observation at `info`; recorded as a follow-up rather than a same-run redesign of the gate's responsibilities |
| I1-F22 | info | 92 | Rationale-heavy module headers in the hook and the eval runner duplicate the plan instead of stating usage and exit semantics | advisory | Recorded as a follow-up; the tidy pass already cut cross-seat rationale, and trimming module docstrings mid-review risks losing the contract text the checks are read against |

### Security pass — round 1 (full)

`claude-security` at `medium`, scan-only, over the committed range `fb5e6ea..339b2c5`. The
diff touches `.claude/hooks/`, `.claude/scripts/`, `specs/**/checks/` and eight commands, so
the full agent ran rather than the light `security-review` pass.

**No findings survived verification — nothing entered the ledger as blocking.** 19 researchers
produced 46 raw candidates, deduplicated to 29; 13 went to a three-lens adversarial panel
(reachability, impact, defenses) for 39 votes. Four votes came back TRUE_POSITIVE, spread
across four different candidates, and none reached the two-of-three keep quorum.

The verifiers converged independently on one structural fact: everything this change adds is
local, single-principal developer tooling. The gates, the acceptance checks and the eval
runner are all invoked by the operator, on the operator's machine, against a `clients/` tree
`.gitignore` keeps out of version control. For every candidate the party who would have to be
the attacker either *is* the operator or already needs repository write access — which yields
strictly more than any sink found here, since this repo's own review command executes every
script under `specs/<name>/checks/`.

Two caveats recorded rather than smoothed over:

- **16 of the 29 candidates were never paneled.** The scan stopped the panel after 13 of 13
  failed and listed the rest as unverified candidate sites. Five of those 16 are fixed by this
  round anyway — the three `check_revision_count.py` claims (`I1-F4`, `I1-F5`, `I1-F6`) and the
  `check_contrast.py` token-coverage claim (`I1-F11`) — and the `check_gate_signoff.py` path
  join was both paneled and fixed (`I1-F9`). The remainder are recorded as PR follow-ups.
- **The working tree was dirty while the scan ran**, because the fix round was landing
  concurrently. The panel verified against the committed revision via `git show` and corrected
  the mis-anchored line numbers; the report states this explicitly and notes that the
  uncommitted `contained()` helper already fixes one flagged item.

Closest calls, both voted down 1-of-3 and carried to follow-ups: `studio-research-analyst.md`
grants every inherited tool to the one role that audits client-named third-party sites, and
`p7-retro.md` is the only phase waiving the write-only-under-`PROJECT_DIR` rule.

### Implementation round 2 — delta on `339b2c5..88530d1`

`gpt-5.6-sol` at `high` (one effort step down from round 1, per the gate). 5 findings:
4 blocking, 1 advisory. **Every round-1 disposition held; nothing was reopened without new
evidence.** Two findings are regressions the round-1 fixes introduced, and one is the review
lead's own editing error — all three are recorded as such rather than attributed elsewhere.

| ID | Sev | Conf | Finding | Disposition | Evidence |
| --- | --- | --- | --- | --- | --- |
| I2-F1 | major | 99 | The eval scratch project is not a git repository, but every command now anchors on `git rev-parse --show-toplevel`, so the recorded AC16 runs never exercised the commands in a valid environment — reopening `I1-F1` and `I1-F7` | fixed | `init_git_repo()` makes each staged scratch root a real git repository — hermetic (`GIT_CONFIG_GLOBAL`/`GIT_CONFIG_SYSTEM` → devnull, local identity), so nothing depends on the host's git config — and `collect_outputs` excludes `.git` and `.claude` so the new tree is not handed to the judge as "files the run produced". Three guards added, the sharpest being `test_a_commands_anchored_project_dir_resolves_inside_the_scratch_project`, which parses the literal `PROJECT_DIR:` line out of `p1-discovery.md` and expands it in the staged root; with the init removed it fails with the reported symptom, `PosixPath('/clients/acme/site')` |
| I2-F2 | major | 99 | The replacement `b4` check accepts three arbitrary headings, a sitemap copy one character long, and a single matching word from one triage row, so it can still award a false pass | fixed | `b4` rebuilt around two discriminating tests: a normalized section set from the plan and the sitemap requiring ≥ 3 sections the plan names and the sitemap does not (so byte-inequality no longer helps), and a traceability test requiring *every* significant word of a triage row's Section cell to appear in the plan, for at least half the rows and no fewer than 2. A missing `sitemap.md` now fails loudly instead of silently skipping. Proven against nine fixtures: the old check false-passed a one-character-different sitemap copy, three arbitrary headings sharing one word with a row, and a triage with one incidentally-matching row; the new one rejects all three and still passes a genuine plan against a prose sitemap |
| I2-F3 | major | 100 | Five AC blocks carry both the new and the stale pass counts (26/14, 12/9, 9/6, 7/6, 17/7), so the same command is recorded as two different results | fixed | **The review lead's own error** — the edit that rewrote each block's node ids inserted the new evidence paragraph without removing the old one. Both were verified present, the five stale paragraphs were removed, and every AC command was re-run to confirm the surviving count is the true one |
| I2-F4 | major | 98 | The counter now demands a hash-matching P2 sign-off, contiguous round numbers and per-order capacity, while spec.md still says an existing change order suffices and omits the new exit-2 cases | fixed | spec.md's revision contract rewritten to match what `check_revision_count.py` enforces — the signed-and-hash-verified brief, positive/unique/contiguous round numbers, `Cost — rounds` ≥ 1, per-order capacity, the exact allowance line, the enlarged exit-2 set, and two new edge-case rows. Written as specification rather than changelog |
| I2-F5 | minor | 100 | Case ids `0` and `"0"` both lint but collide on one run directory, and integer judge-assertion ids are written as strings then looked up as integers | advisory | Below the blocking bar; folded into the `I2-F1` fix since the same validation path was being rewritten |

`I2-F1` is the consequential one and it was confirmed directly rather than taken on report:
`cd /tmp/studio-command-evals-ybuu5ny6/eval-1/run-3 && git rev-parse --show-toplevel` returns
`fatal: not a git repository`. The suite nonetheless scored 1.0, which means the graded agent
used relative paths rather than the literal anchor — so the 1.0 was real as a measure of the
commands' *output* but did not validate the anchoring. The anchor itself stays correct for a
real session, where the worktree is a git repository; the eval environment was the unfaithful
part, so the runner is fixed rather than the commands.

**The round-2 fixes were not re-verified by a further Codex round** — this run's 2-round
allowance is spent. That is one of the two things the human gate is being asked to accept.

**The other is AC16's evidence.** `I2-F1` was fixed, and fixing it *invalidated the 1.0 that
closed `I1-F1`*: that rate was measured in a scratch project which was not a git repository, so
the graded agent used relative paths rather than the anchor the commands now carry. A re-run is
required for the rate of record, and it could not be produced — all six `claude -p` invocations
returned `You've hit your session limit · resets 6:10am (Asia/Singapore)`, scoring 0.0 with the
runner correctly marking every run errored. That 0.0 is an artifact of the account limit, not a
regression: every deterministic `check` in those runs still exited 0. **So AC16 currently has no
valid recorded rate — neither the 1.0 nor the 0.0 stands** — and the PR is left draft for that
reason.

One follow-up the failed run surfaced: the runner's diagnostic reads `run errored (success)`,
because the envelope field it treats as an error carries the literal string `success`. The
zeroing behavior was right here, but the field it keys on wants checking against a genuinely
clean run before the next eval is trusted.

### Security follow-ups — closing the round-1 scan's coverage gap

The six items the studio-layer review left open, worked in this run. IDs `S-F1`–`S-F3` continue
the security pass; `E-F1` is the eval-runner follow-up quoted above.

| ID | Sev | Finding | Disposition | Evidence |
| --- | --- | --- | --- | --- |
| E-F1 | minor | The runner's failed-run diagnostic reads `run errored (success)`; the field it labels from carries the literal string `success` | fixed | A clean `claude -p --output-format json` envelope was captured and read directly: it carries `is_error: false` beside `subtype: "success"`, `api_error_status: null`, `terminal_reason: "completed"`. So **`is_error` is the field that signals failure, and the runner already keyed the zeroing on it** — a successful run was never zeroed, and the reported symptom was a labelling defect only. `subtype` records how the turn ended, not whether it worked, and reads `success` on a session-limit abort too, which is why the label was nonsense on exactly the failure that mattered. `claude_headless` now labels from `api_error_status` then `result`, never `subtype`. Two contract tests added over recorded envelopes: `test_a_clean_envelope_is_never_treated_as_an_errored_run` and `test_an_aborted_run_is_labelled_with_why_rather_than_its_subtype` |
| S-F1 | minor | `studio-research-analyst.md` denies only `Agent`, so the one role that reads client-named third-party sites inherits every other tool — the scan's closest call, 1 of 3 votes to keep | fixed | `disallowedTools: Agent` replaced with `tools: Read, Grep, Glob, Write, Edit, WebFetch, WebSearch` — what a research pass needs to reach the sites, read the engagement, and author its two audits, and nothing more. `Bash` is the capability actually removed: this seat is the only one that ingests untrusted third-party content, so it is the only one where an injected instruction reaches a tool the operator did not intend. AC3 already accepted the allowlist form (`if not allowed and "Agent" not in denied`), so the deny property still holds and `ac3-role-agents.sh` exits 0 unchanged. `roster.md` records the exception so the next author does not normalize it back to match its eight siblings |
| S-F2 | minor | `p7-retro.md` is the only phase waiving write-only-under-`PROJECT_DIR`, routing engagement-derived lessons into auto-loading `.claude/` prompt files — voted down 1 of 3 on the grounds that `.claude/` edits are git-tracked and reviewable | fixed, waiver narrowed | The waiver was wider than the routing it existed for: the instruction read "edits to files under `.claude/`" while step 2 only ever routes to three `studio-layer` directories. Narrowed to exactly those three, with hooks, settings files, other namespaces and `AGENTS.md` named as out of bounds — so the stated permission now matches the actual behavior instead of licensing more than P7 does. A second instruction closes the vector the finding was really about: a routed lesson is the studio's own conclusion in its own words, never client-supplied or third-party text carried into a file that loads in every later session. The refuters' reasoning is preserved and made explicit rather than assumed — `.claude/` is reviewed, `clients/` is gitignored |
| S-F3 | info | 16 of 29 consolidated candidates were never paneled; 5 are fixed by the review round anyway | closed as no new blocking finding, by independent pass | **The scan run's candidate list was not preserved** — the ledger records the count and the categories, and the `.claude/.security-scan/*.json` files are the post-write hook's file-tracking state, not the scan's candidates. The 16 could not be resumed row by row, so an independent pass was run over the same surface instead: the 6 changed executables (`check_gate_signoff.py`, the four `check_*.py` studio scripts, `run_command_evals.py`) and the 7 `specs/cpo-layer/checks/*.sh`. Lenses: injection sinks, path containment, symlink and traversal handling, ReDoS over client-controlled markdown, and fail-open behavior. Found: no `shell=True`, no `eval`/`exec`, no `os.system`; the single subprocess is `["git", "rev-parse", "--show-toplevel"]` with list argv. Every regex is anchored or linear — no nested quantifiers, so no ReDoS on the client-written files these parse. `contained()` holds under absolute paths, `..` segments and escaping symlinks, and correctly rejects `target == root` since `root in target.parents` is false there. The hook's `__main__` wraps `main()` in a blanket handler exiting 0, so plumbing failures fail open as `hooks.md` requires. The `.sh` checks quote their expansions and use bounded deletes. **The two named closest calls are `S-F1` and `S-F2` above, both now fixed.** This is a fresh independent pass, not a resumption of the original 16 — recorded that way so the coverage claim is not overstated |

The `destructive-guard` false positive the review hit twice is filed as **issue #82** rather than
fixed here: `_common.py:369` matches `--yes` because `\b` holds between `-` and `y`, so any
`--yes` flag followed by a redirect denies as an unbounded fill. Reproduced directly against the
hook. It is a PreToolUse guard on every `Bash` call in every session and is mirrored into
`.codex/hooks.json`, so narrowing it belongs in its own change with its own contract tests, not
in-flight in an unrelated review branch.

### Implementation round 3 — delta on `88530d1..febd6e4`

`gpt-5.6-sol` at `high`, reviewed head `febd6e4`. 3 findings, **all 3 blocking**. Effort was
held at `high` rather than stepped down to `medium`, because this round carries more than a
normal delta: it is also the first verification of the round-2 fix series, which the prior run
left unverified when its 2-round allowance ran out.

Fix note: the skill's implementation flavor assigns fixes to fixer subagents. This run had a
standing session constraint against spawning agents, so the orchestrator fixed all three
directly. Recorded rather than smoothed over.

| ID | Sev | Conf | Finding | Disposition | Evidence |
| --- | --- | --- | --- | --- | --- |
| I3-F1 | major | 99 | `b4` still awards a false pass: `sections()` counts the document title and arbitrary metadata bullets as sections, so `# Cold Designer Plan` plus `- Audience` and `- Constraints` clears the three-novel-sections bar with no section-level plan at all — reopening `I2-F2` | fixed | **Reopened with new evidence and confirmed by running it**: the committed check exited 0 on exactly that document. Two defects, both fixed. The document title is no longer a section — the first level-1 heading is skipped, and only that one, so a plan with no `#` title loses nothing. Where any heading survives, headings alone are the inventory, so preamble bullets can no longer top up a thin restatement of the sitemap. Traceability now matches triage rows against that inventory rather than the raw document body, so a row can only trace to something the plan declared as a section. Proven against six fixtures: the committed check passes 4 and false-passes 2; the replacement passes all 6, still refusing a sitemap near-copy and three arbitrary headings sharing one word, and still admitting both a heading-based and a bulleted plan that genuinely diverge. Four regression tests added (`test_b4_*` in `test_studio_checks.py`), which read the check out of the committed suite so they cannot drift from it; the two negative ones were confirmed to fail against the pre-fix check with `assert 0 == 1` |
| I3-F2 | major | 99 | `check_revision_count.py:263` joins change-order references without containment, so an absolute path, a `..` segment, or an escaping symlink lets one engagement's excess rounds be paid for by another project's signed order | fixed | **Confirmed by direct exploitation before fixing**: a project whose log named `../../globex/shop/change-orders/1.md` for a round past its allowance exited **0** — acme's excess round paid for by globex's order. This is `I1-F9`'s class (fixed in `check_gate_signoff.py` via `contained()`) never applied to the counter. Added `contained()` here in the same shape and for the same reason, rejecting absolute paths and `..` before resolution and requiring the resolved target beneath the resolved project root, so an escaping symlink fails too. The same repro now exits 1. Three tests — traversal, absolute, escaping symlink — each confirmed to fail against the pre-fix script, all three reporting `3 rounds logged … all accounted for` |
| I3-F3 | major | 100 | `summary.md`, `artifacts/dev-report.html` and `spec.md` still say AC16 has no valid rate and list the closed follow-ups as open, while `implementation-notes.md` records the 1.0/1.0 run; `spec.md` also retains the obsolete 0.8889 gap and the suite count is stale | fixed | Every outcome document regenerated from the ledger and notes. `summary.md`: status `ready for review`, AC16 row carries the rate, the five closed follow-ups struck through, suite count corrected. `spec.md`: the "Known gap for review" block replaced by the rate of record. `dev-report.html`: header banner, AC16 evidence row and the AC16 note rewritten, the follow-up picker rebuilt around what is actually still open, footer updated for the third round. Suite count landed at **1039** — the figure moved twice in this run (1030 → 1032 with the envelope tests, → 1039 with this round's seven), so it was taken from the final run rather than carried forward |
| I3-F4 | major | 95 | The plan asserts in five files that *every* role sets `disallowedTools: Agent`, which the `S-F1` fix made untrue — the property still holds but the prose contradicts the implementation (impl-standard 1, plan fidelity) | fixed | **Self-reported, not a Codex finding** — found while checking whether `S-F1` broke AC3. It did not: `ac3-role-agents.sh` already accepts either mechanism and still exits 0. But `spec.md`, `acceptance-criteria.md`, `decisions.md` (×2), `tasks.md` and `implementation-notes.md` all stated the denial form as universal. Each restated as the property it exists to guarantee — no role can spawn another — naming both mechanisms, rather than deleting the guarantee or silently narrowing it |

### Implementation round 4 — delta on `febd6e4..00771ca`

`gpt-5.6-sol` at `medium` (one effort step down from round 3, per the gate), reviewed head
`00771ca`. 3 findings: **2 blocking, 1 advisory**. Two are regressions or omissions in the
round-3 fixes themselves; none reopened an earlier disposition without new evidence.

**This run's 2-round allowance is now spent (rounds 3 and 4), so these fixes were not
re-verified by a further Codex round.** That is what the human gate is being asked to accept.

| ID | Sev | Conf | Finding | Disposition | Evidence |
| --- | --- | --- | --- | --- | --- |
| I4-F1 | major | 98 | The `I3-F1` fix discards the first level-1 heading unconditionally, so a titleless plan whose three sections *are* `#` headings keeps only two and falsely fails the three-novel-sections bar | fixed | **A regression my own fix introduced, and a fair catch.** The rule is now conditional: a level-1 heading is a document title only when something else supplies the inventory — a deeper heading, or a list. A plan whose sections are level-1 headings has no title to discard and keeps all of them. Verified across seven fixtures, three checks: the pre-`I3-F1` check scores 5/7 (false-passing both metadata cases), the round-3 check 6/7 (this regression), the corrected check 7/7. `test_b4_keeps_level_one_headings_when_they_are_the_sections` added as the H1-only regression Codex asked for |
| I4-F2 | major | 100 | `I3-F3` is not fully fixed: `dev-report.html` still shows `1030` tests, `15 / 16` criteria, "AC16 evidence outstanding", "Closed (15)" and "Outstanding (1)", contradicting the 1039/all-closed evidence in the same page | fixed | Correct — the round-3 pass updated the AC table rows and the narrative but missed the headline `<dl class="facts">` block and the criteria filter buttons, so the page contradicted itself. All four regenerated. Verified by grep: zero occurrences of any stale counter and zero `data-k="open"` rows remain. The count landed at **1040** after this round's H1 test — it moved four times across the run (1030 → 1032 → 1039 → 1040), so every quoting document was re-derived from the final run rather than incremented |
| I4-F3 | minor | 100 | `I3-F4`'s false universal survives in `dev-report.html`: the AC3 row still claims all nine roles use `disallowedTools: Agent` | fixed | Advisory by severity, fixed anyway since it is the same one-line correction applied to the other six files. The row now states the enforced property — nine role agents, none able to spawn a subagent — which is what `ac3-role-agents.sh` actually asserts |

### Terminal — approved at the human gate by override

The implementation flavor's 2-round allowance for this run was spent on rounds 3 and 4, so
round 4's fixes were never re-reviewed. The gate presented that, together with the run's own
base rate — **every fix round in this run introduced new blocking defects**: round 3's fixes
carried two of round 4's three findings, and `I4-F1` was a regression in the `I3-F1` fix — and
recommended a fifth round. The user chose **ship as-is**.

| Item | Disposition | Reason |
| --- | --- | --- |
| `I4-F1`, `I4-F2`, `I4-F3` fixes unverified by a fifth Codex round | overridden | User chose "ship as-is" at the human gate, having been shown the fix-round defect rate and the recommendation to run round 5 |

Nothing else is outstanding. Every blocking finding across implementation rounds 1–4 is
`fixed`, none is `disputed`, AC16 carries a measured rate, and the suite is green at 1040
passed / 2 skipped with all seven plan-local checks at exit 0.

**The merge itself was not run by the review session** — that is `/harness-layer:harness-ship`,
which merges with `gh pr merge --squash --match-head-commit <approved-sha>`. The approved SHA
is **`7e5fe38`**.
