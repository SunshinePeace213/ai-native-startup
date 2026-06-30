# Decisions: Standardize /plan-w-team issue tracking

> The grilling record for [spec.md](./spec.md) — why the plan is the way it is. Lifecycle tracking and
> the Codex review record live in spec.md, NOT here; this file is the immutable decision history.

## Summary

We discussed how to maximize GitHub Issue tracking across the `/plan-w-team` lifecycle. The agreed scope: make the Epic issue **body** a live state-mirror for the **plan phase** (Issue = plan-primary, PR = build-primary, nothing mirrored across the line), keeping comments as append-only history. Concretely: rename + rework the Epic issue template, wire three body-sync touchpoints into `/plan-w-team`, standardize two artifacts (verdict relay-comment + body state-mirror), standardize the issue title, and clean up the eight PR Build-Status templates that drifted after the multi-layer-review rework. Codex stays file-write-only; Claude remains the sole `git`/`gh` writer; build-phase issue ticking is deferred.

## Resolved Decisions

- **Q:** Should the workflow update the Issue's _body_ or post _comments_ after creation?
  - **A:** Both, for different payloads — body = current state (overwritten), comments = history (appended). Wire body-sync in addition to the existing relay comments.
  - **Why:** The standard GitHub split; a reader gets state-at-a-glance from the body and the trail from comments. Today only comments exist → the body is "write-once, then dead."

- **Q:** Should Codex commit and state-track its own findings (the proposed "Codex Commit + State Tracking" step)?
  - **A:** No. Codex keeps self-writing findings into `## Codex Findings` (already implemented); Claude does all commits/pushes/`gh`.
  - **Why:** `spec-review` runs `-s workspace-write` (network-off) so Codex literally cannot push; and the single-`git`-writer invariant is what enforces the no-trailer policy, the scoped `git add`, and a race-free branch ref. The "self-write findings" half the user wanted is already the design.

- **Q:** Which issue-body checkboxes survive, and who maintains them?
  - **A:** Keep + wire **Spec-review status** (live, plan-phase). Drop **Child task checklist** (duplicates the PR's Agent Task Manifest). Keep **Acceptance criteria** as a pointer to `acceptance-criteria.md`, not a mirrored checklist.
  - **Why:** Issue = plan altitude, PR = build altitude; mirroring build progress onto the issue is the double-maintenance anti-pattern.

- **Q:** Keep the `📋 epic:` title prefix or drop it (label already carries type)?
  - **A:** Keep `title: "📋 epic: "` (user's call).
  - **Why:** User preference; noted that the `epic` label also carries type, but the prefix stays.

- **Q:** How should the "Link to plan" render?
  - **A:** Path-as-text markdown links — display text is the repo path (`specs/<name>/spec.md`), href is the blob URL on the convention branch. Link **all four** plan files (spec.md, tasks.md, acceptance-criteria.md, decisions.md), each its own entry.
  - **Why:** Readable (no raw URL shown) but clickable; convention-branch href avoids a pre-merge 404 against `main`. (Revised from an earlier "two links + rely on spec.md's References tree" — the user asked that the issue surface all four files directly, so a reader needn't open spec.md to reach tasks/acceptance.)

- **Q:** Should the relay-comment's `Full detail` pointer be plain text or a link?
  - **A:** A clickable markdown link to `spec.md`'s Codex Findings section via the heading anchor on the convention branch (`[spec.md › ## Codex Findings](<blob-url>/spec.md#codex-findings)`).
  - **Why:** A reader jumps straight from the issue comment to the verdict detail; a bare `spec.md › ## Codex Findings` string forces a manual hunt.

- **Q:** What is the Epic template file renamed to?
  - **A:** `.github/ISSUE_TEMPLATE/epic-plan.md` → `epic-spec.md` (via `git mv`; `name: Epic / Plan` and the title prefix preserved).
  - **Why:** Echoes the SDD entry file `spec.md` without the collision that a literal `spec.md` template filename would cause; `epic-` keeps it unambiguous.

- **Q:** Which new body sections add value for both agents and developers?
  - **A:** Add `## Non-Goals` (scope fence) and `## Lifecycle` (macro phase line) as must-haves; add `## Open Questions` and `## How to act` as optional sections. Stop there to keep the body scannable.
  - **Why:** Lifecycle is the only cross-phase view; Non-Goals stops `/build` gold-plating; Open Questions uses the issue as the discussion surface; How-to-act self-documents the next command.

- **Q:** Which artifacts actually need new standardization?
  - **A:** Only two — the verdict relay-comment and the `## Spec-review status` state-mirror. The invocation string, the `### Round N — Verdict:` findings block, the terse stdout return, the `## Codex Verification` block, and the final Report are already templated; leave them.
  - **Why:** Don't template what's already templated (simplicity).

- **Q:** Is the PR Build-Status cleanup in scope, given build enhancements are out?
  - **A:** Yes — it is _cleanup_, not a build enhancement. All eight PR templates go from the stale 5-item to the 7-item Build Status `build.md` already seeds.
  - **Why:** The templates currently disagree with `build.md`; a hand-opened PR gets the wrong checklist and `/ship`'s gate is confused.

## Assumptions

- `gh issue create --template` is resolved by the `name:` field (`Epic / Plan`, unchanged) and is moot when `--body-file` is supplied — so the file rename does not break creation. _Invalidated if_ a `gh` version matches `--template` strictly by filename; validation greps for any lingering `epic-plan.md` reference to catch this.
- No repository code path references the Epic template by its old filename `epic-plan.md` (only `config.yml`, which points at `feature.md`/`bug.md`). _Invalidated if_ the validation grep finds a reference.
- Leaving the Lifecycle `Build ▸ Ship ▸ Done` segments un-advanced is acceptable for this iteration (the issue still closes via `Closes #N`). _Invalidated if_ stakeholders need the issue to reflect build/ship progress live — that becomes a separate `/build` enhancement.

## Open Questions / Out of Scope

- **Out of scope:** Build-phase issue updates / `/build` ticking the issue (the PR owns build progress).
- **Out of scope:** Making Codex a `git`/`gh` writer.
- **Out of scope:** Any `/build` behavioral change beyond the PR-template text cleanup; the `spec-review` / `implementation-review` skill files.
- **Out of scope:** Dropping the `type:` prefix from the bug / feature / chore issue templates (only the Epic template is touched).
- **Open question (deferred, owner @ringo):** whether a future iteration should advance the issue Lifecycle marker during `/build` and `/ship`.
- **Open question (deferred, owner @ringo):** whether to post a short "plan published" comment at publish in addition to the silent body-fill.
