# Decisions: Refactor plan-w-team to SDD four-file templates + enhance spec-review

## Summary — one paragraph: agreed scope + key choices

Externalize `/plan-w-team`'s hard-coded Plan/Decision formats into four spec-driven templates
under `specs/_templates/` (`spec.md`, `decisions.md`, `tasks.md`, `acceptance-criteria.md`),
rename the canonical plan file `plan.md` → `spec.md` across **every** consumer in one pass,
add a **blocking** Stop hook (bash, exit 2) that gates file + required-section completeness, and
enhance the `spec-review` skill to read all four files and apply a five-category review lens while
**keeping** its load-bearing `### Round N — Verdict:` / `## Codex Findings` output contract.
`plan-w-team` stays a slash command. `spec.md` becomes the single lifecycle record (Tracking +
Codex Findings + Codex Verification + Status); `decisions.md` stays the lean, immutable grilling
record. The plan-w-team Codex loop also flips `spec.md`'s `Status:` to `Approved` after a Codex
`approved` verdict.

## Tracking — issue (#N, or `none — gh unavailable`), intended convention branch name (`<type>/<N>-<slug>`, or `<type>/<slug>` with no #N), and worktree path. Mirrors `plan.md`'s `## Tracking`; the issue field is the single source of truth /build reads.

- Issue: #4
- Branch: chore/4-plan-w-team-sdd-refactor
- Worktree: /Users/ringo/Desktop/ai-native-startup/.claude/worktrees/chore+4-plan-w-team-sdd-refactor

## Resolved Decisions — per decision: Question / Answer / Rationale

- **Q:** How wide should the rename's blast radius be, given `/build` must keep working?
  - **A:** Full rename everywhere — `spec.md` canonical across `plan-w-team`, `spec-review`,
    `build`, `ship`, `implementation-review`, and `task-tools` in this same plan.
  - **Why:** The workflow ends "ready for build commands"; a partial rename leaves `/build`
    broken. A consistent name across the lifecycle beats a smaller-but-broken diff.

- **Q:** Should `plan-w-team` become a Skill or stay a Command?
  - **A:** Stay a Command (`/plan-w-team`); the Stop hook lives in its frontmatter.
  - **Why:** It's a deliberate, args-driven, heavyweight orchestration; auto-triggering as a skill
    risks firing on planning-shaped prompts. Lowest churn, keeps the clean `/command` UX.

- **Q:** The reviewer reference outputs `Status: Approved | Issues Found`, but the existing skill
  outputs `### Round N — Verdict: …` that the Codex loop greps. How to reconcile?
  - **A:** Keep the Round-N verdict + `## Codex Findings` contract; fold the five-category lens
    (Completeness/Consistency/Clarity/Scope/YAGNI) + calibration + an advisory, non-blocking
    Recommendations subsection _into_ the finding bar.
  - **Why:** The verdict line is load-bearing — the plan-w-team loop reads it with `grep`. Swapping
    formats would force rewriting the verdict-reading and round-numbering logic for no gain.

- **Q:** What should the 4th file be named (current file has a typo and holds criteria + commands)?
  - **A:** `acceptance-criteria.md` (rename via `git mv` from `accepance-criteria.md`).
  - **Why:** Fixes the typo, most explicit about contents, reads naturally in build/review refs.

- **Q:** What should the Stop hook do on a failed check?
  - **A:** Block the stop — `exit 2` with the missing files/sections on stderr — so Claude must
    complete them before the run ends. Implemented in bash to match `block-coauthor-trailer.sh`.
  - **Why:** A gate that only warns isn't a gate; gaps slip through silently. Exit-2 mirrors the
    repo's existing deny pattern.

- **Q:** Should `decisions.md` carry `## Tracking` and `## Codex Verification`?
  - **A:** No. Consolidate both into `spec.md`, so `spec.md` is the single record of the plan's
    whole lifecycle (Tracking + every Codex round + final outcome + Status). `decisions.md` stays
    the lean, immutable grilling record (Summary / Resolved Decisions / Assumptions / Open
    Questions). To preserve ownership, `spec.md` splits the review record into Codex-owned
    `## Codex Findings` (raw per-round verdicts) and Claude-owned `## Codex Verification` (outcome +
    rejected findings + rationale).
  - **Why:** User's explicit intent ("spec.md will contain all issue records of the entire plan").
    One home prevents drift; `/build` reads Tracking from `spec.md`.

- **Q:** Should the four templates be locked as drafted, or revised?
  - **A:** Locked with enhancements: spec.md gets the Status enum, `## Non-Goals`, Claude-owned
    `## Codex Verification`, fleshed Edge Cases + References (file tree), and renderable `[ ]`
    Self Validation checkboxes; tasks.md gets a back-link + a `Satisfies:` traceability field;
    acceptance-criteria.md gets stable `AC#` ids + a per-command→AC mapping. Conditional sections
    (Problem Statement, Solution Approach, Implementation Phases) stay conditional.
  - **Why:** SDD wants explicit non-goals, traceability (spec → task → done), and a clean
    machine-readable status. The drafts were close; these close the gaps.

## Assumptions — every deferred "you decide" / accept-all item, explicitly

- **Stop hook target detection**: the hook gates the **newest-modified** `specs/*/` folder
  excluding `_templates`. Assumed safe because the hook is command-scoped (only fires on a
  `/plan-w-team` Stop), where exactly one fresh folder is expected. _Invalidated if_ the hook is
  ever reused outside `/plan-w-team`.
- **Required-section list is unconditional-only**: the hook requires only always-present headings,
  excluding conditional sections, so simple chores don't false-fail. _Invalidated if_ a section's
  conditionality changes in the templates without updating the hook's allowlist.
- **macOS `stat -f`**: the hook uses BSD `stat` to match the `darwin` runtime. _Invalidated if_ the
  repo must run the hook on Linux (switch to `stat -c '%Y %n'`).
- **build.md keeps a legacy `plan.md` fallback** so historical plans (including this one) still
  build after the rename. _Invalidated if_ old plans are migrated to `spec.md`.
- **No new dependencies**: bash + existing `gh`/`codex`/prettier toolchain only.

## Open Questions / Out of Scope — deferred or excluded items (non-goals)

- **Out of scope:** Migrating existing `specs/*/plan.md` from past plans to the new four-file
  layout — only the templates, command, skill, hook, and downstream docs change.
- **Out of scope:** Any change to the `implementation-review` _logic_ beyond the `plan.md`→`spec.md`
  rename (its build-phase review contract is untouched).
- **Out of scope:** Converting `plan-w-team` to a skill, or adding a skill wrapper.
- **Out of scope:** Changing the Codex loop's 2-round cap or the `gh` tracking/publish flow.
- **Open question:** Whether the Stop hook should also lint that `Satisfies:` ids in `tasks.md`
  actually resolve to `AC#` ids in `acceptance-criteria.md` (deeper traceability). Deferred — the
  agreed hook does exactly two checks (files exist, required sections present); owner: future
  enhancement.

## Codex Verification — outcome (one of: approved at round N / proceeded without approval after 2 rounds / skipped — Codex unavailable), plus any Codex findings Claude rejected with rationale

**Outcome: approved at round 2.**

- **Round 1 — changes-requested.** Two findings, both applied (none rejected):
  1. `refactor-command` depended on the later `add-stop-hook`, violating top-to-bottom execution
     → physically reordered so the Stop hook is Task 2 and the command refactor is Task 3.
  2. No acceptance criterion verified the Stop-hook frontmatter wiring or the Status-flip logic
     → added **AC10** (hook wired in `plan-w-team.md` frontmatter) and **AC11** (Status flips to
     Approved / Needs Human Review), each with a validation command.
- **Round 2 — approved.** No blocking findings; the spec meets the bar.
- **Rejected findings:** none.
