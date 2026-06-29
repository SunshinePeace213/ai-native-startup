# Spec: Multi-Layer Review Pipeline for /build

- **Owner:** @SunshinePeace213
- **Status:** Approved
  <!-- Lifecycle, set by /plan-w-team: Drafted for Review → Approved (after a Codex `approved`
       verdict) → Needs Human Review (still changes-requested after 2 Codex rounds). One value only. -->

## Task Description

The `/build` command (`.claude/commands/build.md`) currently does: resolve the plan →
enter the worktree → implement → open a **ready** PR → run the Codex
`implementation-review` loop (the skill emits its verdict as a final CLI message that
`/build` captures to a scratch file) → report. Three problems motivate this rework:

1. **Specs-location bug (worktree-first).** `/build` resolves `specs/<plan>/spec.md`
   *before* it enters the worktree. But `specs/<plan>/` only exists on the feature
   branch (inside the worktree) — never on `main`, where the command is invoked. So
   the lookup searches the main checkout and fails. The worktree must be entered
   **first**, then specs resolved from inside it.
2. **No Claude self-review before the cross-model gate.** Subagent output goes
   straight to Codex with no intra-Claude QA. The user wants two Claude-side passes
   first — an internal-check (a tailored `code-simplifier`) and a Claude code-review
   modelled on the `code-review` plugin but checking **AGENTS.md** (our `CLAUDE.md` is
   literally `@AGENTS.md`).
3. **Codex review is single-pass and context-heavy.** The cross-model review should
   mirror `pr-review-toolkit`: the Codex orchestrator spawns **6 review subagents**,
   collects their feedback, and writes **one consolidated report** Claude reads from a
   file (not raw stdout) — solving long-context blow-up when findings are many.

This plan reworks `/build` into a worktree-first, draft-PR-early, multi-layer review
pipeline and adds the supporting skill, agent, and Codex subagent files. It is a
**chore** (harness/tooling) of **complex** scope: one command rewrite, one skill
upgrade, one new skill, one new agent, and six new Codex subagent definitions.

The target end-to-end flow:

```
enter worktree (arg-or-autodiscover)
  → open DRAFT PR (Closes #N) + seed Build Status
  → implement (builders)            → commit/push → tick Implementation
  → internal check (code-simplifier)→ commit/push → tick Internal check
  → Claude code review (vs AGENTS.md)→ fix → commit/push → PR comment → tick Claude code review
  → Codex cross-review R1 (6 subagents → 1 committed report) → commit/push → relay → tick Codex review R1
      ↳ if changes-requested: Claude fixes → commit/push → tick Fixes
  → Codex cross-review R2 (if needed) → committed report → relay → tick Codex review R2
      ↳ if changes-requested: best-effort fix → commit/push
  → mark PR ready → tick Result → Report
                                        (max 2 Codex rounds)
```

## Objective

`/build <plan> [worktree]` enters the correct worktree **before** resolving any spec,
opens a draft PR, and gates the implementation through internal-check →
Claude-code-review → a 6-subagent Codex cross-review (max 2 rounds) — each phase
producing a committed artifact and a ticked Build-Status item — leaving a
review-ready PR for `/ship`.

## Non-Goals

- **No changes to `/plan-w-team`, `/ship`, the `spec-review` skill, or the four
  `specs/_templates/` files.** This plan touches only `/build` and the build-phase
  review machinery. (`/ship` already tolerates extra Build-Status items — it only
  checks that every item is ticked.)
- **No new runtime dependencies** beyond `codex` and `gh`, which `/build` already
  requires.
- **No generic/distributable plugin.** The six Codex subagents are ports of
  `pr-review-toolkit`'s lenses tailored to *this* repo, not a republished plugin.
- **No auto-merge.** `/build` still stops at a ready PR; the user merges via `/ship`.
- **No migration of in-flight legacy plans.** The existing legacy `plan.md` fallback
  is retained as-is, not extended.

## Problem Statement

The build workflow has outgrown a single-file, single-review-pass command. Without a
worktree-first bootstrap it cannot reliably find its own spec; without Claude-side QA
it hands unreviewed code to the cross-model gate; and a single-pass Codex review both
misses the breadth of a `pr-review-toolkit`-style sweep and risks flooding Claude's
context with raw findings. Fixing these now — before more plans run through `/build` —
keeps every future build correct-by-construction and auditable on the PR.

## Solution Approach

**Hybrid: a thin orchestrating command that delegates to focused skills/agents.**
`/build` stays the user-invoked command and owns sequencing, commits, and every `gh`
call; the reusable review capabilities live in their own files:

- **Worktree-first bootstrap** — resolve the worktree from an optional `[worktree]`
  arg, else autodiscover by globbing `.claude/worktrees/*/specs/<plan>/spec.md` for
  the unique match; `EnterWorktree` it; *then* read `spec.md` + its `## Tracking`
  block (issue `#N` is the single source of truth).
- **Draft PR early** — immediately after entering the worktree, open a draft PR on the
  pre-existing convention branch (plan commits already pushed by `/plan-w-team`),
  seeded with the 7-item Build-Status checklist; mark it ready only at the end.
- **`code-simplifier` agent** (new, `.claude/agents/`) — tailored, multi-language
  (Python/`uv`, TS/Next.js/React, and the Markdown harness layer with a
  semantics-preservation guardrail), AGENTS.md-aware, recently-modified scope.
- **`claude-code-review` skill** (new, `.claude/skills/`) — a faithful port of the
  `code-review` plugin pipeline (eligibility → 5 parallel Sonnet lenses → per-finding
  Haiku confidence 0–100 → keep ≥80) retargeted from CLAUDE.md to **AGENTS.md** (+
  `~/.codex/AGENTS.md`, `.claude/rules/*`, `GIT-COMMIT-PR-MESSAGE.md`), run on
  `git diff origin/main...HEAD`, emitting a PR comment **and** feeding fixes back to
  `/build`.
- **`implementation-review` skill** (upgrade) — becomes a Codex **orchestrator**: it
  reads `spec.md`/`decisions.md`, runs the plan's Validation Commands itself, **spawns
  the 6 Codex review subagents**, collects + dedups their findings, and writes **one
  consolidated report** to `specs/<plan>/reviews/codex-impl-review-round-N.md`,
  returning only a terse verdict summary to Claude (who reads the report from the
  file). Max 2 rounds; Codex still edits no source — Claude's builders apply fixes.
- **6 Codex subagents** (new, `.codex/agents/*.toml`) — read-only ports of
  `pr-review-toolkit`'s lenses: code-standards (vs AGENTS.md), comment-accuracy,
  test-coverage, silent-failure, type-design, simplification.

**Main alternative considered & rejected:** inlining all three new phases directly in
`build.md`. Rejected because `build.md` is already ~13k, the review logic would not be
reusable outside `/build`, and each phase is independently testable as its own
skill/agent (see decisions.md).

## Requirements & Decisions

- **Worktree before specs.** `/build` MUST enter the worktree (arg-or-autodiscover via
  `.claude/worktrees/*/specs/<plan>/spec.md`) before resolving `spec.md`; the recorded
  issue `#N` stays the single source of truth, never re-derived from the mangled local
  branch. (Fixes the specs-location bug.)
- **AGENTS.md is the review standard.** Both the Claude code-review and the Codex
  code-standards subagent check against **AGENTS.md** (+ global `~/.codex/AGENTS.md`,
  `.claude/rules/*`, `GIT-COMMIT-PR-MESSAGE.md`), not CLAUDE.md, because CLAUDE.md is
  `@AGENTS.md`.
- **Codex writes the report; Claude reads the file.** The `implementation-review`
  orchestrator spawns 6 subagents and writes ONE consolidated, committed report per
  round to `specs/<plan>/reviews/`; Claude reads the verdict + findings from that file,
  never from stdout. Max **2** Codex rounds.
- **Commit at every checkpoint, trailer-free.** One conventional `Refs #N` commit
  (no `Co-Authored-By`) after impl, internal-check, Claude-review fixes, each Codex
  round's report, and each fix round; the Codex report is a committed PR artifact.

## Tracking

<!-- Recorded by /plan-w-team. The Issue field is the SINGLE SOURCE OF TRUTH /build reads — /build
     NEVER re-derives #N from the mangled local branch name. spec.md is the single home for this
     block; decisions.md does not duplicate it. -->

- **Issue:** #6
- **Branch:** chore/6-build-multi-layer-review
- **Worktree:** /Users/ringo/Desktop/ai-native-startup/.claude/worktrees/build-multi-layer-review

## Relevant Files

Use these files to complete the task:

- `.claude/commands/build.md` — **rewrite.** Worktree-first bootstrap, draft-PR-early,
  the three new review phases, the 7-item Build-Status checklist, and the per-phase
  commit/push cadence. The single biggest change.
- `.agents/skills/implementation-review/SKILL.md` — **upgrade.** From "emit verdict as
  final message, write no files" to a 6-subagent orchestrator that runs validation +
  plan-adherence, spawns the subagents, and writes one committed consolidated report;
  returns only a terse summary.
- `AGENTS.md`, `GIT-COMMIT-PR-MESSAGE.md`, `.claude/rules/task-tools.md` — read-only
  standards the review layers must encode and honor.
- `.agents/skills/spec-review/SKILL.md` — read-only reference for the file-write +
  terse-return + round-numbering contract the upgraded `implementation-review` mirrors.

### New Files

- `.claude/skills/claude-code-review/SKILL.md` — the Claude intra-model code-review
  skill (ported `code-review` pipeline, AGENTS.md-targeted, returns ≥80 findings).
- `.claude/agents/code-simplifier.md` — tailored multi-language simplifier agent
  (Python / TS-Next-React / Markdown-harness), AGENTS.md-aware, opus.
- `.codex/agents/review-code-standards.toml` — general code review vs AGENTS.md + bugs.
- `.codex/agents/review-comment-accuracy.toml` — comment-vs-code accuracy / rot.
- `.codex/agents/review-test-coverage.toml` — behavioral coverage + critical gaps.
- `.codex/agents/review-silent-failure.toml` — silent failures / error handling.
- `.codex/agents/review-type-design.toml` — type encapsulation + invariants.
- `.codex/agents/review-simplification.toml` — complexity / redundancy (advisory).
- `specs/build-multi-layer-review/reviews/` — created **at build time** by `/build` to
  hold the committed `codex-impl-review-round-N.md` reports (not authored by this plan).

## Edge Cases

- **Worktree discovery: zero matches** → fall back to the current working directory and
  treat as a legacy/local plan (resolve `specs/<plan>/spec.md` there); if still absent,
  STOP and report the paths searched.
- **Worktree discovery: multiple matches** → do not guess; ask the user which worktree
  (or require the `[worktree]` arg).
- **`gh` / remote / auth unavailable, or no issue (`none — gh unavailable`)** → skip
  the draft PR, every `gh pr comment`, Build-Status edits, and `gh pr ready`; STILL run
  every review phase and the Codex loop locally; print the manual `gh pr create`
  command. Mirrors the existing graceful-skip.
- **`codex` unavailable** → skip the Codex cross-review loop (warn → `/codex:setup`),
  record "skipped — Codex unavailable", finish with the Claude-side phases only.
- **`codex exec` cannot spawn subagents headlessly** (uncertain — VERIFY at build time)
  → the `implementation-review` skill degrades to running the 6 lenses as sequential
  passes inside a single Codex context, still writing the same consolidated report.
  Fail loud: the report must state which mode produced it.
- **Empty / docs-only / trivial diff** → the Claude code-review eligibility gate skips
  the review (records "skipped — trivial diff"); the build proceeds.
- **Codex finds many findings** → the orchestrator writes the consolidated report
  (grouped, deduped, digest-first) so Claude's context sees the digest, not 6 raw
  transcripts.
- **Validation Commands fail in a Codex round** → that round is `changes-requested`
  (never silently passed); a round that times out / writes no report is **re-run**,
  never treated as approval.
- **Re-run / idempotency** → re-running `/build` on a partially-built worktree resumes
  from the Build-Status ticks already present; round-N report files are suffixed by N,
  so a re-run never overwrites a prior round.

## Red Flags

- Starting to write code without any written requirements
- Asking "should I just start building?" before clarifying what "done" means
- Implementing features not mentioned in any spec or task list
- Making architectural decisions without documenting them
- Skipping the spec because "it's obvious what to build"
- **Resolving `specs/<plan>/spec.md` before `EnterWorktree`** (the exact bug this plan
  fixes) — the bootstrap order is load-bearing.
- **Letting the Codex skill or any subagent edit source** — Codex reviews and writes
  only its report; Claude's builders apply every fix.
- **Pointing the review at CLAUDE.md** instead of AGENTS.md.
- **Piping raw Codex stdout into Claude's context** instead of reading the committed
  report file.

## Notes

- Codex subagent design follows `https://developers.openai.com/codex/subagents`: TOML
  agents in `.codex/agents/` (`name` / `description` / `developer_instructions`,
  optional `model` / `sandbox_mode`); `[agents]` `max_threads` defaults to **6** (fits
  exactly the 6 review subagents) and `max_depth` to **1** (no nested spawning). Review
  subagents use `sandbox_mode = "read-only"`; the orchestrator runs under
  `-s workspace-write` solely to run Validation Commands and write its one report.
- `codex exec` has **no** `--skill` flag — the skill is auto-discovered from
  `.agents/skills/` and invoked by naming it in the prompt (unchanged).
- No application build/typecheck exists for these prompt/markdown artifacts; acceptance
  is **structural** (file existence, valid TOML/frontmatter, required sections/ordering)
  plus a human read-through — see acceptance-criteria.md.

## Codex Findings

<!-- CODEX-OWNED. Written only by the spec-review skill (one `### Round N — Verdict: …` block per
     round). Claude must NEVER edit this section. -->

### Round 1 — Verdict: approved

The spec meets the blocking-issue bar with no blocking findings this round.

## Codex Verification

<!-- CLAUDE-OWNED. The outcome summary Claude records after the Codex loop. -->

- **Outcome:** approved at round 1
- **Rejected findings:** none — Codex approved with no blocking findings

## References

<a tree of the sibling plan files and their purpose, so the four files trace to each other:>

```
specs/build-multi-layer-review/
├── spec.md                 # this file — what & why, tracking, review record
├── decisions.md            # grilling record: resolved decisions, assumptions, out-of-scope
├── tasks.md                # how & who: phases, team, step-by-step tasks
└── acceptance-criteria.md  # done: acceptance criteria + validation commands
```

## Self Validation

- [x] Objective, Task Description, and Non-Goals are filled in (no placeholders left)
- [x] Requirements trace to tasks in tasks.md and to checks in acceptance-criteria.md
- [x] Acceptance criteria are specific and testable
- [x] All four files exist under specs/build-multi-layer-review/ and are saved in the repository
- [x] Codex has reviewed the spec and Status reflects the outcome
