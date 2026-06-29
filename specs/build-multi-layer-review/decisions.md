# Decisions: Multi-Layer Review Pipeline for /build

> The grilling record for [spec.md](./spec.md) — why the plan is the way it is. Lifecycle tracking and
> the Codex review record live in spec.md, NOT here; this file is the immutable decision history.

## Summary

We are reworking `/build` from a single-pass command into a worktree-first, multi-layer
review pipeline, structured as a **hybrid**: `/build` stays the thin orchestrating
command (sequencing, commits, `gh`) and delegates to focused, reusable files — a new
`claude-code-review` skill, a tailored multi-language `code-simplifier` agent, an
upgraded `implementation-review` Codex skill, and six new `.codex/agents/*.toml`
review subagents. The build now: enters the worktree (arg-or-autodiscover) before
resolving specs, opens a draft PR early, runs a Claude internal-check then a Claude
code-review (against AGENTS.md), then a cross-model Codex review where the orchestrator
spawns 6 subagents (ports of `pr-review-toolkit` lenses), writes one committed
consolidated report, and Claude fixes — for a max of 2 Codex rounds. Each phase commits
a trailer-free `Refs #N` checkpoint and ticks a Build-Status item; the PR is marked
ready at the end for `/ship`.

## Resolved Decisions

- **Q:** As the workflow expands, do we keep `/build` a command, inline everything, or
  convert it to a skill?
  - **A:** Hybrid — `/build` stays the orchestrating command; the three new review
    capabilities are extracted into a skill (`claude-code-review`), an agent
    (`code-simplifier`), the upgraded `implementation-review` skill, and 6
    `.codex/agents/*.toml` subagents.
  - **Why:** `build.md` is already ~13k; inlining bloats it and makes the review logic
    non-reusable. Extraction makes each phase independently testable and reusable, while
    a command (not a skill) remains the right fit for a user-invoked, arg-taking entry
    point.

- **Q:** How does `/build` find and enter the worktree *before* it can read `spec.md`
  (the worktree path is recorded inside `spec.md`, and `specs/<plan>/` exists only on
  the feature branch, not `main`)?
  - **A:** Arg-or-autodiscover. `/build <plan> [worktree]`: if a worktree path/branch
    arg is given, enter it; else glob `.claude/worktrees/*/specs/<plan>/spec.md` and
    enter the unique match; then read `## Tracking`. One match → enter; many → ask;
    none → fall back to the current dir (legacy/local plan).
  - **Why:** Breaks the chicken-and-egg bootstrap deterministically, honors the user's
    "get worktree from Args" intent as an override, and self-heals without forcing the
    user to paste a mangled worktree path.

- **Q:** Should the Claude code-review reuse the `code-review` plugin as-is, and does
  our approach cover its ideas?
  - **A:** Port the plugin's full pipeline (eligibility gate → 5 parallel Sonnet lenses
    → per-finding Haiku 0–100 confidence → keep ≥80, with the false-positive
    guardrails) but retarget the standard from **CLAUDE.md to AGENTS.md** (+
    `~/.codex/AGENTS.md`, `.claude/rules/*`, `GIT-COMMIT-PR-MESSAGE.md`), run it on
    `git diff origin/main...HEAD`, and add a second output sink (findings feed Claude's
    fix step, not just a PR comment).
  - **Why:** It is a strict superset — every plugin stage is retained; the only changes
    are additive (AGENTS.md retargeting, local-diff target, findings→fixes). CLAUDE.md
    in this repo is literally `@AGENTS.md`, so AGENTS.md is the real standard.

- **Q:** Vendor the plugin `code-simplifier`, or tailor our own?
  - **A:** Tailor our own `.claude/agents/code-simplifier.md`, multi-language: Python
    (`uv`, type hints, full-width rich panels), TypeScript/Next.js/React (ES modules,
    `function` declarations, explicit `Props`, server/client boundaries, no nested
    ternaries), and the **Markdown harness layer** (skills/agents/commands/rules) with
    a hard semantics-preservation guardrail (never weaken or drop an instruction when
    "simplifying" a prompt). AGENTS.md-aware; recently-modified scope.
  - **Why:** The plugin agent is JS/React-only and assumes CLAUDE.md; our repo spans
    React/TS, Python, and a Markdown prompt-engineering harness, so it must understand
    all of those — especially that "simplifying" a prompt must not change its behavior.

- **Q:** For the Codex cross-check, follow `pr-review-toolkit` as-is or customize?
  - **A:** Necessarily customize. `pr-review-toolkit`'s 6 agents are Claude `.md`
    agents — Codex cannot run them — so we **port** their 6 specialties into 6 Codex
    TOML subagents (read-only), and the `implementation-review` orchestrator keeps the
    build-gate-unique work `pr-review-toolkit` lacks: plan-adherence (acceptance
    criteria, step tasks, locked decisions) + running the Validation Commands. The
    orchestrator spawns the 6, collects, and writes one consolidated committed report.
  - **Why:** Defense-in-depth ("not trusted yet"): Claude self-reviews intra-model,
    then Codex independently cross-reviews so a single model's blind spots cannot pass
    the gate. The port is forced by runtime (TOML, not Claude agents); plan-adherence +
    validation are what make it a *build gate*, not a generic review.

- **Q:** When is the PR created?
  - **A:** Draft early — open a draft PR immediately after entering the worktree (the
    convention branch already carries the plan commits), seed the 7-item Build-Status
    checklist, tick items per phase, and mark the PR ready only after the final Codex
    verdict.
  - **Why:** Matches the user's step-2 ordering, gives a live audit trail from the
    first phase, and satisfies `/ship`'s "Build Status complete" guard.

- **Q:** Where does the Codex consolidated report live, and how granular are commits?
  - **A:** The report is **committed** (not scratch) to
    `specs/<plan>/reviews/codex-impl-review-round-N.md` so it appears in the PR diff as
    an audit trail; Claude reads the verdict/findings from that file. One trailer-free
    conventional `Refs #N` commit per checkpoint (impl, internal-check, Claude-review
    fixes, each Codex round's report, each fix round).
  - **Why:** The user's flow is explicitly "Output Report + Commit"; committing the
    report makes the cross-review durable and reviewable, and per-checkpoint commits
    give a legible build history.

## Assumptions

- **`codex exec` can spawn the 6 subagents headlessly.** Uncertain — to be VERIFIED at
  build time. If it cannot, the `implementation-review` skill degrades to running the 6
  lenses as sequential passes in one Codex context, still writing the same consolidated
  report. Invalidated if a verification smoke-test shows neither path works under
  `codex exec`.
- **The convention branch already exists on `origin` with plan commits** when `/build`
  runs (created + pushed by `/plan-w-team`), so a draft PR can open without a new push.
  Invalidated for legacy/local-only plans → graceful-skip path applies.
- **`.claude/worktrees/` is the worktree home** and `/build` is invoked from the main
  checkout, so the autodiscover glob resolves. Invalidated if worktrees are relocated.
- **AGENTS.md (+ the global and rules files) is the complete standard set** the review
  layers must check; no separate per-directory CLAUDE.md files carry rules in this repo.
- **Default Codex `[agents]` limits (max_threads 6, max_depth 1) suffice** — exactly 6
  review subagents, no nested spawning needed.

## Open Questions / Out of Scope

- **Out of scope:** modifying `/plan-w-team`, `/ship`, the `spec-review` skill, or the
  four `specs/_templates/` files.
- **Out of scope:** publishing the Codex subagents or the new skill as a distributable
  plugin; migrating in-flight legacy `plan.md` plans.
- **Out of scope:** adding any new runtime dependency beyond the already-required
  `codex` and `gh`.
- **Open question (owner: @SunshinePeace213):** if the headless subagent-spawn
  verification fails *and* sequential passes prove too slow/expensive, do we cap the
  Codex lenses below 6? Revisit only if the build-time smoke-test forces it.
- **Open question (owner: @SunshinePeace213):** should the Claude code-review's
  "prior-PRs" lens be dropped while the repo has few PRs, or kept (it degrades to no
  findings)? Kept for now; revisit if it adds noise.
