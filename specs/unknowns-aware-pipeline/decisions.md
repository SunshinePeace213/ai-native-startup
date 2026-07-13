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
  - **A:** In whichever round approves (round-1 both-clean, round-2 approved, or an approved round 3), the lead authors the brief after reading the `approved` verdict and BEFORE making that round's report commit; report + brief land as ONE commit — the approved head recorded in the stage table. The Finish step only publishes best-effort, adds `## Ship Brief` to the PR body, and verifies that exact head.
  - **Why:** A separate post-approval commit would move the PR head past the approved SHA and abort harness-ship; authoring inside the approving round also guarantees the brief describes the final tree. Same precedent as review reports (lead-committed, non-implementation content).
- **Q:** Who maintains implementation-notes.md, given the build lead's never-edit-directly rule?
  - **A:** The lead — harness-build.md scopes an explicit lead-owned ledger exception covering implementation-notes.md folding, alongside the existing `## Tracking` and `## Locked Boundaries` ledger edits.
  - **Why:** The never-edit rule targets implementation code; ledger bookkeeping already has lead-edit precedent, and a dedicated recorder subagent adds a hop for no quality gain.
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
- Pre-worktree interaction is inline: blindspot cards and design alternatives are presented as text or AskUserQuestion previews during grilling. The durable HTML artifacts are authored only after worktree entry, directly under `specs/<name>/artifacts/`, and published best-effort from those project-local files (`ai-docs/anthropic/artifacts.md`: the page is written to a project file, then published). Invalidated if pre-worktree interactive pages prove necessary in practice.
- Final sign-off was given via the user's /goal directive ("follow the plan and implement the changes") after the four-question proposal interview and the published proposal artifact; remaining sub-decisions above are closed with recommended answers under the accept-all escape hatch.

## Blindspots

Found during this plan's own blindspot pass; each dispositioned:

- **Ship-brief commit vs approved-head guard** — a post-approval artifact commit would break `--match-head-commit`. Resolved: combined commit with the approval-round report (locked decision above).
- **Artifact availability is conditional** — publishing can legitimately fail (auth, plan, provider, org policy). Resolved: best-effort publishing; committed HTML is the durable record.
- **Template/hook drift** — adding `## Blindspots` to the template without updating `check_spec_completeness.py` (or vice versa) would break every future plan run. Resolved: one task owns template + hook + test together.
- **Pre-worktree write restriction** — plan-phase interaction is needed before the worktree exists, but the plan command forbids project writes outside it and the Artifact contract publishes a project-local file. Resolved: inline presentation (text / AskUserQuestion previews) during grilling; durable artifacts authored post-worktree under `specs/<name>/artifacts/` and published from there.
- **Stale ship brief after late fixes** — a brief authored once could describe a pre-fix tree. Resolved: the brief is authored fresh inside whichever round approves, immediately before that round's report commit — never reused from a failed round.

## Open Questions / Out of Scope

- **Out of scope:** any change to `/harness-layer:harness-ship`; new hooks; quiz-state recording/enforcement; 2×2 quadrant bookkeeping in spec files; mandatory artifacts on simple plans; artifact design-system work.
- **Open question:** whether AskUserQuestion `preview` fields can replace small design-directions artifacts over time — owner: ringo, revisit after a few real uses.

## KB References

- `ai-docs/anthropic/artifacts.md` — fetched 2026-07-05 (Artifact publishing, page constraints, availability, copy-back pattern)
- `ai-docs/anthropic/skills.md` — fetched 2026-07-05 (commands-as-skills, frontmatter, invocation control)
- `ai-docs/anthropic/hooks.md` — fetched 2026-07-05 (Stop hook event semantics, exit-code contract)
