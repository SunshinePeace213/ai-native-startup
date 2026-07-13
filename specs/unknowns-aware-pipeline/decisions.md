# Decisions: Unknowns-Aware Pipeline

> The grilling record for [spec.md](./spec.md) — why the plan is the way it is. Lifecycle tracking and
> the Codex review record live in spec.md, NOT here; this file is the immutable decision history.

## Summary

Adopt all four "finding your unknowns" techniques as conditional checkpoints inside the existing
plan/build commands: blindspot pass + design-directions channel (plan), implementation notes +
plan-fidelity lens (build), ship brief + advisory quiz (build finish). Artifacts are dual-homed —
committed HTML under `specs/<name>/artifacts/` plus a best-effort published page. harness-ship is
untouched; no new hooks; templates, the spec-completeness gate, both Codex skills, and AGENTS.md
move in the same change.

## Resolved Decisions

- **Q:** Which unknowns techniques does the pipeline adopt?
  - **A:** All four — blindspot pass, design directions + tweakable-plan ordering, implementation notes, ship brief + merge quiz (user multi-selected all in the proposal interview).
  - **Why:** Each cures a different quadrant/phase gap; adopting a subset leaves a quadrant blind.
- **Q:** Where do interactive artifacts live?
  - **A:** Committed HTML under `specs/<name>/artifacts/` AND published via the Artifact tool.
  - **Why:** Committed files are versioned and PR-linkable; published pages carry the interaction. Rules out hosted-only (invisible in PR) and files-only (no interaction).
- **Q:** How binding is the merge quiz?
  - **A:** Advisory at end of build; harness-ship performs no quiz check and is not modified.
  - **Why:** Keeps ship a fast mechanical sonnet/low merge; the guard stays the approved-head SHA.
- **Q:** When do artifact checkpoints fire?
  - **A:** Conditional on signals — blindspot pass always (depth scaled by complexity); design directions only for taste-shaped decisions; ship brief + quiz only for medium/complex builds.
  - **Why:** Matches the adaptive-depth grilling rule and the repo's KISS harness conventions; rules out always-on (token waste on chores) and opt-in-only (forgotten when most needed).
- **Q:** How does the ship brief coexist with the approved-head merge guard?
  - **A:** The brief (+quiz) is committed together with the approval-round report commit; that single commit is the approved head recorded in the stage table.
  - **Why:** A separate post-approval commit would move the PR head past the approved SHA and abort harness-ship. Same precedent as review reports (lead-authored, non-implementation content).
- **Q:** What do reviews do with the new artifacts and deviations?
  - **A:** Delta reviews exclude `specs/<name>/artifacts/` exactly as they exclude `reviews/`; the review packet points at implementation-notes.md; harness-review gains a `plan-fidelity` lens (an undocumented divergence from the plan is a finding); implementation-review dispositions each recorded deviation; spec-review verifies each blindspot was dispositioned.
  - **Why:** Divergence becomes dispositionable evidence instead of being rediscovered or silently shipped.
- **Q:** Where do blindspot findings and deviations live?
  - **A:** Blindspots in `decisions.md ## Blindspots` (new required section, enforced by the spec-completeness Stop gate); deviations in `specs/<name>/implementation-notes.md` (build-time file, NOT gated at plan time).
  - **Why:** Two existing homes extended; rules out a third spec file (`unknowns.md`).
- **Q:** How are grilling questions ordered?
  - **A:** By architectural blast radius — questions whose answers would change the architecture come first; blindspot-pass items needing user input lead the ledger.
  - **Why:** Spends the user's attention where a wrong guess is most expensive (field-guide interview technique).

## Assumptions

- Quiz shape: 3–6 questions keyed to the riskiest parts of the diff, each wrong answer pointing at the file/section to re-read. Invalidated if quizzes prove too long or too shallow in practice.
- Taste-route trigger is planner judgment (recognition-over-specification decisions: UX, output format, report layout), plus explicit user request. Invalidated if the route over- or under-fires; the fallback is AskUserQuestion `preview` fields.
- Artifact publishing is best-effort: on any availability failure (login, plan, provider, org policy per `ai-docs/anthropic/artifacts.md`) the phase proceeds with the committed file only. Invalidated only if the team later requires shareable URLs as a hard deliverable.
- Blindspot depth scaling: simple → ~3 cards inline (no artifact file); medium/complex → up to ~7 cards + artifact. Numbers are guidance, not enforced.
- Pre-worktree artifacts (blindspot/design directions are produced before the worktree exists) are drafted in the session scratchpad and copied into `specs/<name>/artifacts/` at worktree entry — preserving the writes-only-in-worktree rule.
- Final sign-off was given via the user's /goal directive ("follow the plan and implement the changes") after the four-question proposal interview and the published proposal artifact; remaining sub-decisions above are closed with recommended answers under the accept-all escape hatch.

## Blindspots

Found during this plan's own blindspot pass; each dispositioned:

- **Ship-brief commit vs approved-head guard** — a post-approval artifact commit would break `--match-head-commit`. Resolved: combined commit with the approval-round report (locked decision above).
- **Artifact availability is conditional** — publishing can legitimately fail (auth, plan, provider, org policy). Resolved: best-effort publishing; committed HTML is the durable record.
- **Template/hook drift** — adding `## Blindspots` to the template without updating `check_spec_completeness.py` (or vice versa) would break every future plan run. Resolved: one task owns template + hook + test together.
- **Pre-worktree write restriction** — plan-phase artifacts are needed before the worktree exists, but the plan command forbids writes outside it. Resolved: scratchpad drafts, copied in at worktree entry.
- **Stale ship brief after late fixes** — an over-cap round-3 fix would invalidate an already-authored brief. Resolved: re-author before the new approval commit (spec.md edge case).

## Open Questions / Out of Scope

- **Out of scope:** any change to `/harness-layer:harness-ship`; new hooks; quiz-state recording/enforcement; 2×2 quadrant bookkeeping in spec files; mandatory artifacts on simple plans; artifact design-system work.
- **Open question:** whether AskUserQuestion `preview` fields can replace small design-directions artifacts over time — owner: ringo, revisit after a few real uses.

## KB References

- `ai-docs/anthropic/artifacts.md` — fetched 2026-07-05 (Artifact publishing, page constraints, availability, copy-back pattern)
- `ai-docs/anthropic/skills.md` — fetched 2026-07-05 (commands-as-skills, frontmatter, invocation control)
- `ai-docs/anthropic/hooks.md` — fetched 2026-07-05 (Stop hook event semantics, exit-code contract)
