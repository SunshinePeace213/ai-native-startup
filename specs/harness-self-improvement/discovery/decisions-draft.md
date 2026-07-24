# Decisions: harness-self-improvement

> Interview ledger (2 rounds, all recommendations accepted). The plan transcribes this
> verbatim into decisions.md. Evidence base: soriza-cpo-department's 9 spec rounds,
> restore commits #40/#42, the never-fired #52 convergence machinery (841e772), and
> development-log.md's single line.

## Summary

Make the plan → build → review → ship pipeline self-improving: every failure becomes a
machine-checked constraint at the earliest stage that could have caught it, and the
layer's health becomes measurable. Delivered as an epic with one child plan per phase,
substrate first: Plan 1 ships the machine-check foundation (#4 gate re-target, #1
prompt-contract tests, #6 CI, #2 stop-gate lint), Plan 2 the learning loop (#3 findings
ledger, #7 PR self-learning gate, #5 health metrics), Plan 3 the review economics (#8
fix verification, #9 retirement, #11 constraint registry, #10 #52 fire-drill), with
the #12 retro stage deferred until metrics exist. Standing requirement: learning
ships inside the PR's reviewed diff, machine-checked before merge — never post-merge.

## Resolved Decisions

- **Q:** Which interventions form the first plan, and in what sequence?
  - **A:** Substrate first. Plan 1 = #4 (gate re-target) + #1 (prompt-contract tests) + #6 (CI) + #2 (stop-gate lint). Plan 2 = #3 (findings ledger) + #7 (PR learning gate) + #5 (health metrics). Plan 3 = #8 (fix verification) + #9 (retirement) + #11 (constraint registry) + #10 (#52 fire-drill). #12 (retro) deferred until Plan 2's metrics exist.
  - **Why:** Tests without CI gate nothing; #4 is the cheapest proof the encode loop works (shipped through the pipeline itself); #7's payload wants #3 and #6 in place first.
- **Q:** How is the program tracked on GitHub?
  - **A:** One epic issue (epic.yml) with a child-issue checklist; each plan gets its own child issue (`Part of #E`) and ships independently.
  - **Why:** git-workflow.md reserves epics for genuine multi-issue initiatives, which this is.
- **Q:** Do the new machine checks block or warn?
  - **A:** Structure blocks, wording warns. Machine-verifiable structure (a Validation Commands bullet must invoke a committed `checks/` script; required sections; verdict-line format) exits 2. Prose heuristics (absolute-promise wording near hook mechanisms) print warnings only.
  - **Why:** Preserves spec-review's "never demand regex-parsing of prose" calibration — hooks pin structure, Codex stays the judge of prose.
- **Q:** Where does the self-learning gate sit, and when does the payload land?
  - **A:** Both gates, payload inside the reviewed diff. Dispositions and rule/memory edits ride each round's fix commit so the next round reviews them; harness-review step 7 refuses the ready-flip when blocking rounds occurred but the diff carries no payload (or explicit accepted-one-off); harness-ship re-checks the same predicate cheaply. Zero-blocking-finding PRs owe nothing.
  - **Why:** Today the memory step lands in the post-approval terminal commit Codex never reviews — the standing requirement forbids that.
- **Q:** Does the findings ledger backfill the 55 existing review reports?
  - **A:** Fresh start. The ledger begins with the next reviewed plan; metrics read old `reviews/` files directly for the coarse baseline (round counts).
  - **Why:** Pre-#52 reports carry no CX IDs, SHA, or scope lines — backfill means heuristic prose parsing; the rounds-to-approval baseline (5,6,2,6,5,10,9,7,5) needs only file counts.
- **Q:** What proves the layer is actually self-improving (the epic's acceptance bar)?
  - **A:** Regression-proof + observable: every shipped constraint carries a would-have-caught test replaying its motivating failure (#40/#42 replay for prompt-contract tests; the soriza wrong-target repro for the gate fix), and the health metrics exist and refresh per ship. Trend numbers are observational, not gates.
  - **Why:** Outcome-trend gates punish honest plans for hard problems; would-have-caught tests are directly checkable.
- **Q:** References / prior art?
  - **A:** Repo anchors only: `tests/harness-layer/hooks/test_wiring.py` (structural Counter pinning — the model for prompt-contract tests), `specs/soriza-cpo-department/checks/` (committed check-script convention), `.claude/rules/development-log.md` (distill-then-delete cap — the model for retirement). No external references.
  - **Why:** The user confirmed no outside prior art; the Reference map builds from these.
- **Q:** Findings-ledger schema, home, and maintainer? (#3)
  - **A:** Parser-regenerated JSONL: a committed script regenerates `specs/findings-ledger.jsonl` from `reviews/*.md` — one row per blocking finding: plan, round, finding_id, class, repeat_of, summary, disposition (from the next round's Prior-blockers or the approval), constraint_ref. Run in the review terminal step; CI asserts it is current.
  - **Why:** Post-#52 reports are the parseable source of truth; regeneration kills drift; append-only JSONL merges cleanly.
- **Q:** Health-metrics delivery surface and refresh trigger? (#5)
  - **A:** Committed script + committed dashboard page, refreshed at ship; the ship report quotes the headline line. Metrics: rounds-to-approval, repeat-rate, finding-class frequencies, post-approval escapes. On-demand runs work anytime.
  - **Why:** A page nobody regenerates goes stale; ship is the natural refresh point and already runs terminal mechanics.
- **Q:** What counts as a legal learning payload? (#7)
  - **A:** Three forms, path-verified. Per blocking finding, one of: (a) rule/memory edit (`.claude/rules/**`, AGENTS.md, development-log.md), (b) new/updated machine check (test, hook, check script) citing the finding class, (c) accepted-one-off with a stated reason. Every PR template gains a `## Self-Learning` section mapping finding ID → disposition → payload path; the gate script verifies all blocking CX IDs are covered and payload paths appear in the diff.
  - **Why:** An enumerable predicate the gate can check; free-form sections regress to prose nobody validates.
- **Q:** Who verifies fixes between rounds, and what does failure do? (#8)
  - **A:** A sonnet/low verifier checks each CX finding's fix evidence (diff hunk + rationale, or failing-then-passing check). Any incomplete fix → the next codex round is NOT spawned; the fixer redoes it at the escalated tier per the existing repeat rules.
  - **Why:** Never burn a paid round on a known-incomplete fix — targets the "partially resolved" chains that stretched soriza to 9 rounds; guarded-mechanical verification fits sonnet/low per model-selection.
- **Q:** Retirement threshold, cadence, and approval? (#9)
  - **A:** A constraint whose finding class hasn't fired in the last 5 shipped plans is flagged during the ship-time metrics refresh; harness-simplifier drafts the removal as a chore issue labeled `status:needs-human`. Removals never auto-ship.
  - **Why:** Extends the dev-log distill-then-delete cap layer-wide; human approval keeps context-cost cuts deliberate.
- **Q:** Fire-drill the #52 machinery with real Codex or contract-only? (#10)
  - **A:** Hybrid: a repeatable pytest contract suite pins the parseable surfaces (verdict-line grammar, CX/repeat tags, delta ranges, ledger parser round-trip) and runs in CI; one real `codex exec` drill on a seeded fixture plan (with the sandbox network flag per the dev-log lesson) validates end-to-end once, re-run manually only after skill changes. Real calls never in CI.
  - **Why:** Real calls are paid and nondeterministic; the parseable surfaces are testable for free.
- **Q:** Constraint-registry home, format, and promotion path? (#11)
  - **A:** `tests/harness-layer/constraint-registry.yaml` — one entry per finding class: stage (template > checklist > lint > hook > review), mechanism path, evidence. A test asserts every entry's mechanism exists and every ledger class is registered. spec-review references it in one line and carries only classes marked `stage: review`. Promotion = a PR moving an entry down-stage with its new mechanism, gated by the same test.
  - **Why:** Machine-checkable without loading session context; a rules-file registry would bloat every session.
- **Q:** Retro-stage autonomy, cadence, and proof? (#12 — pre-locked, stays deferred)
  - **A:** Propose-only: after each ship, the retro mines the ledger + metrics and files at most one proposed-constraint chore issue (`status:needs-human`). Adoption runs the normal pipeline; a proposal needs ≥2 ledger rows of the same class, and the shipped constraint must include its would-have-caught test.
  - **Why:** Autonomy earns trust after the loop proves itself; the 2-row bar blocks one-off overfitting.

### Resolved from the codebase (plan-1 mechanics)

- **Q:** Contract-test style for command/skill prompt files? (#1)
  - **A:** Structural asserts mirroring `test_wiring.py`'s semantic Counter pinning — required sections, frontmatter keys, load-bearing clauses. No golden files.
  - **Why:** Golden files churn under auto-format and prose edits; the wiring test proves the structural pattern survives reformatting.
- **Q:** Which clauses count as load-bearing? (#1)
  - **A:** Frontmatter keys (model, effort, disable-model-invocation, hooks, allowed/disallowed-tools), required `##` sections, and clauses other components parse (the verdict-line grammar, CX ID scheme, marker-comment keys, the push refspec, report paths).
  - **Why:** "Parsed by something else" is an objective criterion; pure prose stays Codex's job.
- **Q:** Stop-gate targeting channel? (#4)
  - **A:** The hook reads its stdin JSON (cwd / session identity) and gates only the invoking session's plan folder — replacing `newest_plan_folder`'s cross-worktree mtime scan. Ships with concurrency regression tests (two worktrees, unrelated sessions).
  - **Why:** Same defect class Codex blocked four rounds running in soriza's intake hook; session-scoped stdin is the channel that resolved it there.
- **Q:** Extend `check_spec_completeness.py` or add a sibling hook? (#2)
  - **A:** Extend the existing hook (same command-scoped Stop registration in harness-plan.md frontmatter): add the validation-command structure check (blocking) and the absolute-promise wording heuristic (warn-only).
  - **Why:** One gate, one registration; hooks.md's ship-together rule covers the test updates.
- **Q:** CI workflow details? (#6)
  - **A:** GitHub Actions on PRs touching `.claude/**`, `.agents/**`, `tests/**`, `pyproject.toml`/`uv.lock`; astral-sh/setup-uv; `uv run pytest tests/harness-layer`; honors the `[skip-ci]` title token per git-workflow.md.
  - **Why:** Matches the repo's uv/pytest conventions; [skip-ci] stays the documented emergency bypass.

## Assumptions

- CI needs no secrets (pytest only, no network) — invalidated if a future check calls Codex or GitHub APIs.
- The findings-ledger parser targets only the post-#52 report contract — invalidated if the spec-review output contract changes shape (the contract tests then pin it).
- `specs/findings-ledger.jsonl` as the aggregate home — plan may relocate it if a check proves a better spot, keeping the append-only JSONL shape.
- The sonnet/low fix verifier reads evidence assembled by the fixer (diff hunk + rationale) rather than re-deriving fixes — invalidated if verification quality proves insufficient (then escalate the tier, per standing permission).
- Plan-1 items are independently shippable within one PR; the epic's child plans land sequentially (1 → 2 → 3).

## Open Questions / Out of Scope

- **Out of scope:** the discovery commands (unknowns, brainstorm, prototypes, interview) — no self-improvement machinery for them.
- **Out of scope:** backfilling per-finding rows from the 55 pre-#52 review reports.
- **Out of scope:** activating the #12 retro stage before Plan 2's metrics exist (its shape is pre-locked above).
- **Open question:** exact load-bearing clause inventory per command/skill file — enumerated at plan time under the locked criterion (owner: Plan 1's spec).
- **Open question:** finding-class taxonomy for the ledger `class` field — Plan 2's spec derives it from spec-review's "What to judge" list (owner: Plan 2's spec).
