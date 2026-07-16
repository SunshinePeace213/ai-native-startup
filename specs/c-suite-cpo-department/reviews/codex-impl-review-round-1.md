### Round 1 — Verdict: changes-requested

Scope: full
Base SHA: c1e54d55083a5c24ffb5aa747ab8b10f485016dc
Reviewed head SHA: 33192f0df7d663d319613fbbacdda38a24df0d99
Mode: spawn (6 lenses)
Profile: kb-grounded
Lenses: plan-adherence, review-code-standards, review-silent-failure, review-type-design, review-test-coverage, review-comment-accuracy | skipped: review-simplification — history-brief.md records that a tidy pass ran
Findings: 11 surviving of 21 raw (floor 80)
Validation: all PASS

Digest: 11 blocking — 4 workflow/control-contract defects, 1 impossible ledger invariant, 1 code-standard violation, 1 silent cleanup failure, 2 critical validation-coverage gaps, and 2 inaccurate wireframe annotations. The caller's expected lens list was revised: structured frontmatter, command, review-request, and ledger contracts require `review-type-design`; `review-simplification` must be skipped because the recorded tidy pass ran. KB grounding found no contradiction across the seven injected claims; the 2026-07-05 sources are 12 days old and not stale.

Deviation disposition:

- AC7's validator invocation amendment — conforming under decisions.md `## Locked Boundaries`.
- Lead-owned TaskUpdate calls because Task tools were unavailable to builders — conforming; no product/spec behavior changed.
- `prd-review` omitting spec-review's harness-specific KB section — conforming to task 4's PRD-only criteria.
- AC8's per-file validator invocation amendment — conforming under decisions.md `## Locked Boundaries`.
- Subagent preload not positively observed on the `--agent` surface — conforming as a recorded probe limitation; the required brief-carried skill fallback is present.
- The fixture Design-Lead regression receiving a targeted second fix and confirmation review — conforming; it closed a newly introduced blocker.
- Fixture stage commits omitting `Refs #35` — conforming to the explicit fixture trail contract.

Findings:

**Plan adherence**

- **New real engagements scaffold in the hosting worktree before their engagement branch/worktree exists.** `.claude/commands/c-suite/cpo-intake.md:53-66` scaffolds `products/<client-slug>/` in step 3, then creates the real-mode branch and worktree in step 4, with no move or working-directory transition. That leaves the scaffold outside the engagement branch and contradicts tasks.md step 6 plus decisions.md's assumption that real engagement work happens in its own worktree. Fix: for a new real engagement, create and enter the engagement worktree before scaffolding; keep the current ordering only for fixture mode and make resume lookup explicit.
- **`accept-with-noted-gaps` cannot advance to the brief stage.** `.claude/commands/c-suite/cpo-prd.md:63-68` says this user-authorized exit passes, but `.claude/commands/c-suite/cpo-brief.md:31-33` accepts only an `approved` verdict report; the preceding reports remain `changes-requested`. This makes one of tasks.md step 6's required over-cap exits a dead end. Fix: persist a deterministic accepted-with-noted-gaps approval state in `status.md` and make brief preflight recognize it, or define another explicit approval artifact.

**review-code-standards / review-type-design**

- **The PRD reviewer is invoked without the engagement it must review.** `.claude/commands/c-suite/cpo-prd.md:53-55` injects only round N, while `.agents/skills/prd-review/SKILL.md:13-22` requires the prompt to provide `products/<client-slug>/`. A round number cannot select one client among multiple engagements or determine the report destination. Fix: pass the quoted engagement-folder path together with N and reconcile the skill's contradictory “prompt gives the engagement folder” / “caller injects only N” wording.
- **The advertised opening request is silently discarded.** `.claude/commands/c-suite/cpo-intake.md:3,18-19` advertises `[request…]` but binds only `$2`, and no workflow step consumes `REQUEST`. Multiword text is truncated before being ignored, contrary to tasks.md step 6's intake contract. Fix: capture the complete remainder after the slug and seed discovery with it, or remove the argument from the public contract.
- **The fixture run-log SHA invariant is self-referential and unenforceable.** `.claude/skills/cpo-question-bank/templates/status.md:11-13,31-35` says each run log records that stage's commit SHA, while the fixture exits in `.claude/commands/c-suite/cpo-intake.md:89-91`, `cpo-prd.md:77-80`, and `cpo-brief.md:70-73` update the ledger, commit, then record that commit's SHA. Recording a commit's SHA changes the commit, producing a different SHA. Fix: establish a new locked boundary defining either a two-commit protocol or the SHA as the preceding deliverable commit, then align commands and AC13 validation.
- **The validator violates the repository's safe-delete rule.** `specs/c-suite-cpo-department/validate.sh:14-15` installs an EXIT trap using `rm -rf "$TMP_DIR"`, while root AGENTS.md says never use `rm -rf` directly and requires moving targets to Trash. Fix: use the repository-approved cleanup pattern without `rm -rf`.

**review-silent-failure**

- **Failed quarantine of an AC12 side effect is hidden.** `specs/c-suite-cpo-department/validate.sh:369-372` redirects every `mv` error to `/dev/null` and ignores its status. A collision or permission failure leaves the forbidden product entry behind while reporting no cleanup failure. Fix: check `mkdir` and every `mv`, report the entry and destination on failure, and retain the failing AC result.

**review-test-coverage**

- **AC12 does not prove the claimed no-side-effect boundary.** `specs/c-suite-cpo-department/validate.sh:353-381` snapshots only top-level `products/` names and compares additions with `comm -13`; it misses modifications/deletions inside existing engagements, refs/worktrees, and forbidden `gh` actions. It also accepts a reply that merely echoes the regex without saying STOP. This does not establish acceptance-criteria.md AC12's before-any-side-effect contract. Fix: assert an explicit STOP and snapshot every in-scope mutable surface, or run the negative case in an isolated disposable repository and compare its full state.
- **The critical PRD review/gate checks are marker greps that allow broken control flow to pass.** `specs/c-suite-cpo-department/validate.sh:128-135,272-279` neither enforces prd-review's exact first-line/single-report/two-line-return/input/no-`gh` contract nor exercises missing-verdict, changes-requested routing, and round-cap behavior. The missing engagement input and dead-end accepted path above both passed. Fix: add exact structural assertions for AC9 and a disposable fixture test covering approval, changes requested, missing verdict, accepted gaps, and the round cap for AC4.

**review-comment-accuracy**

- **The Home wireframe falsely says its hero copy is unauthored.** `products/_example-bluebird-bakery/design/wireframes/home.html:172-175` says `Home / Hero` is “not yet authored this wave,” while `products/_example-bluebird-bakery/design/copy-deck.md:63-71` contains the complete entry. Fix: remove the stale parenthetical so the handoff annotation points designers to the existing copy.
- **Four wireframe headers promise per-section desktop reflow notes that do not exist.** `products/_example-bluebird-bakery/design/wireframes/custom-cakes.html:176-180`, `menu.html:144-148`, `our-story.html:130-134`, and `visit-us.html:119-123` claim desktop reflow is noted per section, but their section annotations contain no such notes. Fix: add the promised per-section behavior or narrow the header claim to what the files actually document.
