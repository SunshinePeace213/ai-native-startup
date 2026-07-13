# Spec: Unknowns-Aware Pipeline

- **Owner:** @SunshinePeace213
- **Status:** Drafted for Review

## Task Description

Fold the "finding your unknowns" techniques (Thariq Shihipar's Claude Fable field guide) into the
`/harness-layer:harness-plan` → `harness-build` → `harness-ship` pipeline as conditional
checkpoints: a blindspot pass and a design-directions channel at plan time, an implementation-notes
deviation log plus a plan-fidelity review lens at build time, and a ship brief with an advisory
merge quiz at build finish. Each checkpoint may produce an interactive artifact that is BOTH a
committed HTML file under `specs/<name>/artifacts/` and a best-effort published page (Artifact
tool). Templates, the spec-completeness Stop hook (+tests), both Codex review skills, and
AGENTS.md update in the same change. `/harness-layer:harness-ship` is untouched.

## Objective

Every phase of the pipeline surfaces its unknowns in a reviewable home — blindspots in
`decisions.md ## Blindspots`, mid-build deviations in `specs/<name>/implementation-notes.md`, and
merge comprehension in a ship brief + quiz — with all pipeline guards (approved-head SHA, review
round caps, ship mechanics) preserved and the full test suite passing.

## Non-Goals

- No changes to `/harness-layer:harness-ship` (quiz is advisory; ship stays a mechanical merge)
- No new hooks — only `check_spec_completeness.py` is updated
- No quiz-state recording or enforcement anywhere
- No written 2×2 quadrant classification of decisions in spec files
- No mandatory artifacts on simple-complexity plans
- No artifact styling/design-system work (the built-in design skill suffices)

## Problem Statement

The pipeline verifies what the spec says — grilling, acceptance criteria, dual review gates,
locked boundaries — but is blind to what the spec fails to say. Unknown unknowns surface late as
expensive Codex round-2 blockers; taste-shaped decisions funnel through text-only AskUserQuestion;
deviations builders make mid-flight never reach the review packet or the spec; and the merge is
SHA-guarded but not understanding-guarded.

## Solution Approach

Thread the four techniques through the existing command files rather than adding new commands:
harness-plan gains a blindspot-pass step and a taste-route inside the Grilling Protocol;
harness-build gains the implementation-notes contract, a review-packet pointer, and a ship brief
authored inside whichever review round approves — landing in that round's report commit, so the
approved-head guard holds and the brief always describes the final tree; harness-review gains a
`plan-fidelity` lens. The main alternative — a hard
quiz gate inside harness-ship — lost because it adds state and a check to a deliberately
mechanical, user-invoked-only command.

## Requirements & Decisions

Ordered by volatility — most-likely-to-change first, each with its live alternative:

- **Ship brief + quiz commit timing** (most likely to tweak): in whichever round approves, the
  lead authors the brief (+quiz for medium/complex) after reading the `approved` verdict and
  BEFORE making that round's report commit; report + brief land as ONE commit — the approved
  head, so the harness-ship `--match-head-commit` guard holds. The Finish step only publishes
  best-effort, adds `## Ship Brief` to the PR body, and verifies that head. Alternative if this
  proves awkward: publish-only (no commit), linking the URL from the PR body.
- **Taste-route mechanics** (likely to tweak): when the user would recognize the answer but can't
  specify it (UX, output format, report layout) or asks explicitly, present 2–4 concrete
  alternatives via AskUserQuestion labels and rich descriptions — option previews only where the
  running harness supports them (best-effort, never required); a decision that truly needs a
  rendered comparison is recorded as provisional and re-confirmed against the in-worktree
  design-directions page before the spec commit. AskUserQuestion always confirms; decisions.md
  always records.
- **Dual-homed artifacts** (settled): committed HTML under `specs/<name>/artifacts/` is the
  durable record; publishing via the Artifact tool is best-effort and never blocks a phase
  (availability is conditional — see `ai-docs/anthropic/artifacts.md` Availability).
- **Deviation gate** (settled): builders report deviations in hand-offs; the lead folds them into
  `implementation-notes.md` at each checkpoint; a deviation touching a locked decision or
  acceptance criterion STOPS for AskUserQuestion before work proceeds.

## Tracking

- **Issue:** #30
- **Branch:** feat/30-unknowns-aware-pipeline
- **Worktree:** /home/ringo/ai-native-startup/.claude/worktrees/unknowns-aware-pipeline
- **Review profile:** kb-grounded
- **PR:** <#M — filled by /harness-layer:harness-build>

## Relevant Files

Use these files to complete the task:

- `.claude/commands/harness-layer/harness-plan.md` — add the Blindspot Pass workflow step, blast-radius question ordering, the taste-route (design directions) in the Grilling Protocol, artifact handling (inline pre-worktree; durable artifacts authored in-worktree under `specs/<name>/artifacts/` and published from those project files), and Report additions
- `.claude/commands/harness-layer/harness-build.md` — implementation-notes creation + builder Deviations hand-off field + locked-decision gate + the lead-owned non-implementation-file exception (notes creation/folding, ship-brief authoring, `## Tracking` / `## Locked Boundaries`), review-packet pointer, `specs/<name>/artifacts/` delta-review exclusion, approval-path ship brief + quiz, PR-body `## Ship Brief` entry
- `.claude/commands/harness-layer/harness-review.md` — add the `plan-fidelity` reviewer lens
- `specs/_templates/spec.md` — volatility-ordered guidance inside `## Requirements & Decisions` (no heading change)
- `specs/_templates/decisions.md` — new `## Blindspots` section
- `.claude/hooks/check_spec_completeness.py` — add `Blindspots` to decisions.md's required sections
- `tests/harness-layer/hooks/spec-completeness/test_check_spec_completeness.py` — intent test pinning the new requirement
- `.agents/skills/spec-review/SKILL.md` — verify every blindspot is dispositioned in the spec
- `.agents/skills/implementation-review/SKILL.md` — read implementation-notes.md and disposition each deviation; honor the artifacts/ delta exclusion
- `AGENTS.md` — one–two imperative lines documenting the artifacts location and unknowns checkpoints

### New Files

- `specs/_templates/implementation-notes.md` — deviation-log template `/harness-layer:harness-build` copies at implement start (deviation | what forced it | call made | spec impact)

## Edge Cases

- **Artifact tool unavailable** (no `/login`, plan/provider/policy limits per `ai-docs/anthropic/artifacts.md`): keep the committed HTML as the record, note "publish skipped" in the report — never block or fail the phase.
- **Simple-complexity plan**: blindspot pass runs inline (cards as text, no artifact file); ship brief + quiz are skipped; `## Blindspots` is still present (may record "none material — simple chore").
- **Zero deviations during a build**: implementation-notes.md keeps its header plus "No deviations recorded"; reviews disposition nothing.
- **Worktree restored from branch**: committed `artifacts/` travel with the branch; republish from the project files if fresh URLs are needed.
- **Approval after late fixes** (over-cap round-3 path): the brief is authored fresh inside the approving round, immediately before that round's report commit — never reuse a brief from a failed round or ship one describing a pre-fix tree.
- **Re-run idempotency**: in-session republish keeps an artifact URL; a new session mints a new URL unless given the old one — the committed file is canonical, URLs are conveniences.

## Red Flags

- Starting to write code without any written requirements
- Asking "should I just start building?" before clarifying what "done" means
- Implementing features not mentioned in any spec or task list
- Making architectural decisions without documenting them
- Skipping the spec because "it's obvious what to build"
- Adding a required template section without updating `check_spec_completeness.py` AND its tests in the same task
- Committing the ship brief as its own post-approval commit, or sequencing it after the approval report commit already exists (breaks the approved-head guard)
- Any wording that makes the quiz a hard gate (locked: advisory) or artifact publishing mandatory (locked: best-effort)

## Notes

- No new dependencies; the change is prompt/template files plus one hook constant and one test.
- The interactive proposal that locked this design is committed at `specs/unknowns-aware-pipeline/artifacts/proposal.html` for builder reference — it demonstrates the card/chips/quiz patterns the commands will describe.

## Codex Verification

- **Outcome:** <pending — filled after the Codex spec-review loop>
- **Rejected findings:** <pending>

## References

```text
specs/unknowns-aware-pipeline/
├── spec.md                 # this file — what & why, tracking, review record
├── decisions.md            # grilling record: resolved decisions, assumptions, blindspots, out-of-scope
├── tasks.md                # how & who: phases, team, step-by-step tasks
├── acceptance-criteria.md  # done: acceptance criteria + validation commands
└── artifacts/proposal.html # the approved interactive proposal (reference for builders)
```

## Self Validation

- [x] Objective, Task Description, and Non-Goals are filled in (no placeholders left)
- [x] Requirements trace to tasks in tasks.md and to checks in acceptance-criteria.md
- [x] Acceptance criteria are specific and testable
- [x] All four files exist under specs/unknowns-aware-pipeline/ and are saved in the repository
- [ ] Codex has reviewed the spec and Status reflects the outcome
