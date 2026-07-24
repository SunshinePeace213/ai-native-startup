# Decisions: harness-self-improvement

> The interview record for [spec.md](./spec.md) — why the plan is the way it is. Lifecycle tracking and
> the Codex review record live in spec.md, NOT here; this file is the immutable decision history.
> Transcribed from [discovery/decisions-draft.md](./discovery/decisions-draft.md) (2 interview rounds,
> all recommendations accepted) — the program-wide ledger; this folder is Plan 1's spec. Evidence base:
> soriza-cpo-department's 9 spec rounds, restore commits #40/#42, the never-fired #52 convergence
> machinery (841e772), and development-log.md's single line.

## Summary

Make the plan → build → review → ship pipeline self-improving: every failure becomes a
machine-checked constraint at the earliest stage that could have caught it, and the
layer's health becomes measurable. Delivered as an epic (#53) with one child plan per phase,
substrate first: Plan 1 (#54, this spec) ships the machine-check foundation (#4 gate re-target, #1
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

### Resolved at plan time (this run)

- **Q:** Where does Plan 1's spec folder live, given the chain slug names the whole program?
  - **A:** Reuse the chain folder `specs/harness-self-improvement/` for Plan 1's spec; the program-wide discovery stays in its `discovery/`. Plans 2 and 3 draft their own folders from their own chains, referencing this discovery.
  - **Why:** The plan command's default (reuse the chain slug; rename only if actively wrong) — moving discovery would break committed page paths for no behavioral gain.
- **Q:** How does the re-targeted hook resolve the session root from stdin?
  - **A:** Root = first success of: `git -C <stdin cwd> rev-parse --show-toplevel` → the stdin `cwd` itself (if it is a directory) → `$CLAUDE_PROJECT_DIR` → `git rev-parse --show-toplevel` from the process cwd → `Path.cwd()`. Scan only `<root>/specs/*` — the `.claude/worktrees/*/specs` glob is deleted. Malformed or empty stdin degrades down the same chain and never crashes (documented fail-open contract).
  - **Why:** stdin `cwd` is the only channel that tracks the session into its worktree (KB: hooks reference, common input fields); every fallback is a single root, so no fallback re-opens the cross-session defect.
- **Q:** What exactly does the validation-command lint block versus warn?
  - **A:** Block (exit 2): a bullet under `## Validation Commands` with no recognized stage tag (`[plan-time]`, `[child-build-time]`, `[post-merge]`); a bullet invoking neither `uv run --script specs/<plan>/checks/…` nor `uv run pytest …`; a `[plan-time]` bullet whose check script does not exist. Warn only: a `[child-build-time]`/`[post-merge]` path that does not exist yet (build creates those), and absolute-promise wording in spec.md.
  - **Why:** `[plan-time]` commands must be runnable by spec-review now; later-stage artifacts legitimately arrive with the build.
- **Q:** How do warn-only findings surface, given Stop-hook exit-0 output is not fed to Claude?
  - **A:** Warnings print to stderr with a `WARN:` prefix and never change the exit code; they reach the agent only when a blocking finding forces exit 2 (they ride along), otherwise they land in verbose logs only. Accepted as the cost of "warns only" — spec-review remains the prose judge.
  - **Why:** KB hooks reference: on Stop, only exit 2 feeds stderr back to Claude; JSON block-decisions would make the warning blocking, which the ledger forbids.
- **Q:** CI trigger details beyond the ledger?
  - **A:** `pull_request` with `types: [opened, synchronize, reopened, edited]` (so a title edit adding `[skip-ci]` takes effect) and the five path filters (superseded at review round 1 → seven); job-level `if: !contains(github.event.pull_request.title, '[skip-ci]')`; `actions/checkout` + `astral-sh/setup-uv` (versions pinned by the builder against the official docs); then `uv run pytest tests/harness-layer`. No secrets. The workflow is observational — making it a required check is a GitHub-settings step for the human (follow-up).
  - **Why:** Title-based skip evaluates at run creation; without `edited`, a late `[skip-ci]` would be ignored until the next push.
- **Q:** Where does the prompt-contract suite live and how does it prove #40/#42 would have been caught?
  - **A:** `tests/harness-layer/prompts/` (sibling of `hooks/`). Expectations live in module-level per-file dicts (frontmatter pins, exact `##` section tuples, clause lists) checked by small helper functions; the #40/#42 replay tests feed the helpers a mutated copy of harness-build.md/harness-review.md text with `## Report` / `## Instructions` removed and assert the loss is flagged.
  - **Why:** Factoring the assertion into helpers makes "would-have-caught" a directly runnable unit test instead of a claim.
- **Q:** Issue priority?
  - **A:** `priority:P2` for the epic (#53) and Plan 1 (#54) — the documented default; nothing in the ledger locks a higher one.
  - **Why:** git-workflow.md sets P2 as the creation default.

### Resolved at review round 1 (Codex CX1-1 … CX1-4)

- **CX1-1 — prompts suite couldn't reach `load_hook_module`:** the fixture lives in
  `tests/harness-layer/hooks/conftest.py`, out of pytest scope for the sibling `prompts/` dir.
  The build promotes it verbatim to a new `tests/harness-layer/conftest.py` (path constants
  re-derived); `run_hook` and the git-isolation helpers stay put, and hooks tests resolve the
  fixture from the parent conftest unchanged.
- **CX1-2 — discovery-command scope contradiction:** the Non-Goal is narrowed to learning-loop
  machinery (Plan 2/3 ledger rows, gate coverage, metrics). The AC3 contract pins apply to all
  9 command files — under the locked "parsed by something else" criterion, frontmatter and
  required sections are load-bearing regardless of which command carries them.
- **CX1-3 — CI filters omitted tested surfaces:** the filter set widens from five to seven,
  adding `specs/_templates/**` (AC3's hook↔template coupling makes templates a tested surface)
  and `.github/workflows/harness-tests.yml` (the workflow gates itself). Supersedes the
  five-path lists in the two CI entries above; `checks/ac4_ci_workflow.py` updated to match.
- **CX1-4 — per-task effort stamps weren't deployable:** the Agent tool passes only `model` per
  invocation, and subagent `effort` is definition-level frontmatter defaulting to session
  inheritance (KB: subagents.md); `general-purpose` has no definition file. Task stamps change
  to `<model> / session-inherited`, with the mechanics stated once in tasks.md's Team
  Orchestration. A real per-task effort vehicle is recorded as a follow-up, not designed here.
  The KB References below are refreshed accordingly (the prior "ungrounded effort key" note is
  superseded — the refreshed skills mirror documents `effort`).
  **Superseded:** Codex round 2 rejected this fix as CX2-1 (session inheritance violates
  model-selection.md's per-task stamping mandate); the CX2-1 interview pass below re-derived
  the mechanism from root cause at the escalated tier.

### Resolved in the CX2-1 interview pass (effort deployment)

- **Q:** How does the build deploy each task at its stamped effort? (CX2-1 blocker)
  - **A:** Effort-bearing subagent definitions in project `.claude/agents/`: thin pinned-effort
    executors deployed via `Agent({subagent_type: "effort-<tier>", model: <task's stamped
    alias>})`. tasks.md restores concrete per-task effort stamps and sets each task's Agent
    Type to the matching executor.
  - **Why:** `effort` exists only as subagent-definition frontmatter
    (`ai-docs/anthropic/subagents.md`); the Agent tool overrides only `model` per invocation.
    This honors both stamps while keeping the task-tools board protocol intact — Workflow
    deployment would restructure orchestration, and revising the mandate would give up
    per-task effort differentiation.
- **Q:** Naming and reuse scope of the executor definitions?
  - **A:** Generic pinned-effort executors named `effort-low` … `effort-max`, reusable by any
    explicit deployment (builders, review-fix escalations) — not build-scoped `builder-*` names.
  - **Why:** model-selection.md's stamps apply beyond the build stage; one generic set serves
    every deployer.
- **Q:** Which effort tiers get a definition?
  - **A:** All five: `effort-low`, `effort-medium`, `effort-high`, `effort-xhigh`, `effort-max`.
  - **Why:** The mechanism is total — a future plan stamping `xhigh`/`max` never re-hits this
    blocker; each file is ~6 lines.
- **Q:** Definition shape?
  - **A:** Minimal executor: `name`, an explicit-deployment-only `description` (so it never
    auto-delegates), `effort` frontmatter; no `model` (the plan's stamp passes per-invocation),
    no tools restriction; a 2–3-line body — the deploying prompt carries all task context.
    Authored per the meta-agent standard.
  - **Why:** KISS harness rules; baking the board protocol into bodies would duplicate
    task-tools.md.
- **Q:** Automated verification for the mechanism?
  - **A:** Inventory only — the five definition files enter the spec's file inventory, covered
    by the existing AC5 inventory check. No bespoke stamp→definition mapping script.
  - **Why:** File presence is what regresses; a mapping script is speculative machinery.
- **Q:** References and documentation home?
  - **A:** Mirror the existing `.claude/agents/*.md` house style; the deployment mechanic
    (stamped effort → `effort-<tier>` subagent type) is documented in model-selection.md
    §Mechanics only.
  - **Why:** AGENTS.md forbids duplicating model-selection guidance elsewhere; harness-build.md
    needs no edit — its "each on the model/effort its task stamps" promise becomes true again.

### Resolved at revision (cycle 3)

- **Q:** When do the five executor definitions land — with this plan revision or as a build task?
  - **A:** With the plan revision, committed alongside the spec (like the `checks/` scripts).
  - **Why:** Bootstrap: the build's very first `Agent({subagent_type: "effort-<tier>"})` call
    needs the definitions to exist before any build task could author them, and AC5's inventory
    check is `[plan-time]` — its five new rows must hold when spec-review runs it. Authored per
    the meta-agent standard and validated with its `validate_agent.py` (all five PASS).
- **Q:** Do the five inventory rows also feed the AC3 build-time contract suite?
  - **A:** No — AC5-only, stated in the inventory preamble; the AC3 suite pins command and
    skill rows exactly as before.
  - **Why:** The locked verification decision is inventory-only; widening AC3's scope to agent
    definitions would silently grow the suite beyond its locked file set.
- **Q:** Which concrete stamps do the tasks restore?
  - **A:** The pre-CX1-4 originals: retarget-stop-gate `opus`/`medium`, stop-gate-lint
    `opus`/`medium`, contract-tests `sonnet`/`high`, ci-workflow `sonnet`/`low`, validate-all
    `sonnet`/`low` — so builder-hook's two resumed tasks share one `effort-medium` pin (a
    resumed agent keeps its spawn-time effort).
  - **Why:** The original tiers were never the finding — only their deployability was; restoring
    them re-satisfies model-selection.md without re-litigating tier choices.

## Assumptions

- CI needs no secrets (pytest only, no network) — invalidated if a future check calls Codex or GitHub APIs.
- The findings-ledger parser targets only the post-#52 report contract — invalidated if the spec-review output contract changes shape (the contract tests then pin it).
- `specs/findings-ledger.jsonl` as the aggregate home — plan may relocate it if a check proves a better spot, keeping the append-only JSONL shape.
- The sonnet/low fix verifier reads evidence assembled by the fixer (diff hunk + rationale) rather than re-deriving fixes — invalidated if verification quality proves insufficient (then escalate the tier, per standing permission).
- Plan-1 items are independently shippable within one PR; the epic's child plans land sequentially (1 → 2 → 3).
- (Plan time) A Stop hook registered in harness-plan.md's frontmatter receives the same stdin JSON schema as a settings-registered Stop hook, including `cwd` — grounded on the hooks reference's common-fields table; invalidated if command-scoped delivery diverges, which the new contract tests would surface as a hook that never blocks.
- (Plan time) `$CLAUDE_PROJECT_DIR` in a worktree session is a usable single-root fallback — unverified (the cross-check subagent was unavailable this run); the design does not depend on it, since stdin `cwd` is the primary channel and every fallback is still a single root.

## Open Questions / Out of Scope

- **Out of scope (clarified at review round 1):** learning-loop machinery for the discovery commands (unknowns, brainstorm, prototypes, interview); their prompt files remain AC3 contract-pin subjects.
- **Out of scope:** backfilling per-finding rows from the 55 pre-#52 review reports.
- **Out of scope:** activating the #12 retro stage before Plan 2's metrics exist (its shape is pre-locked above).
- **Out of scope (Plan 1):** every Plan 2 / Plan 3 item — findings ledger, self-learning gate, health metrics, fix verification, retirement, constraint registry, fire-drill.
- **Out of scope (Plan 1):** making the CI workflow a required status check (GitHub settings; human follow-up).
- **Resolved (was open):** the load-bearing clause inventory per command/skill file — enumerated in spec.md's `## Load-Bearing Contract Inventory` under the locked "parsed by something else" criterion.
- **Open question:** finding-class taxonomy for the ledger `class` field — Plan 2's spec derives it from spec-review's "What to judge" list (owner: Plan 2's spec).

## KB References

Review profile: `kb-grounded`. Docs consulted (path — fetched — what it grounds):

- `ai-docs/anthropic/hooks.md` — 2026-07-21 — Stop-hook stdin common fields (`session_id`, `cwd`, `hook_event_name`; `stop_hook_active` on Stop); exit-2 blocks the stop with stderr fed to Claude; exit-0 output is not fed to Claude; frontmatter-declared hooks are scoped to the component's lifecycle ("while the component is active").
- `ai-docs/anthropic/skills.md` — 2026-07-23 (refreshed since draft) — command/skill frontmatter fields (`description`, `argument-hint`, `disable-model-invocation`, `allowed-tools`, `disallowed-tools`, `model`, `effort` — effort overrides the session level, default inherits); commands merged into skills share the same frontmatter reference. Supersedes the draft's "ungrounded effort key" note.
- `ai-docs/anthropic/subagents.md` — 2026-07-23 — subagent `effort` is definition-level frontmatter (values `low`…`max`, overrides the session level, default inherits); the Agent tool takes `model` per invocation, no per-invocation effort; per-invocation `model` overrides the definition's — grounds the CX2-1 pinned-effort executor mechanism (and, historically, the superseded CX1-4 fix).
- `.claude/skills/meta-agent/` (repo standard, not a KB mirror) — the authoring standard for the five executor definitions: frontmatter reference (`effort` values, tools-omitted = inherit-all, description-as-trigger with a Not-for boundary), body skeleton, and `validate_agent.py` (all five files PASS).
- **Cross-check unavailable (cycle 3):** the `claude-code-guide` verification subagent could not be deployed (Agent tool denied in this background session, as in cycle 2). The executor mechanism's claims rest on the fresh subagents.md mirror and were independently confirmed by Codex's own round-2 finding ("`effort` is available on subagent definitions while only `model` has a per-invocation override").
- **Gap (fetch unavailable):** GitHub Actions workflow syntax and astral-sh/setup-uv usage have no `ai-docs/` mirror, and the `kb-fetcher`/cross-check subagents were unavailable this session (Agent tool denied). The CI item's `paths`/`if`/`contains()` and setup-uv claims are marked unverified; the builder verifies them against the official docs at build time. Follow-up: `/harness-layer:kb add https://docs.astral.sh/uv/guides/integration/github/` and `/harness-layer:kb add https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax`.

## Follow-ups (advisory, Codex round 1 — feed a future plan, never this run)

- [ ] Tighten `checks/ac5_inventory.py` (enforce section order and true frontmatter placement, not presence-anywhere) and `checks/ac4_ci_workflow.py` (assert the exact filter set and job-level skip placement, not token presence).
- [ ] Add an AC1 regression whose stdin `cwd` is a nested directory inside a temporary git worktree — proves the primary `git -C <cwd> rev-parse --show-toplevel` branch directly.
- [ ] Fold the hooks reference's `${CLAUDE_PROJECT_DIR}` = project-root definition into the fallback-chain assumption when next revised.
- [x] Give per-task effort stamps a real delivery vehicle for Claude subagents — resolved by the CX2-1 revision: pinned-effort executors in `.claude/agents/effort-*.md`, documented in model-selection.md §Mechanics.
