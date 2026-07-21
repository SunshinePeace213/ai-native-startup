# Decisions: Split harness-build into build + review commands

> The interview record for [spec.md](./spec.md) — why the plan is the way it is. Lifecycle tracking and
> the Codex review record live in spec.md, NOT here; this file is the immutable decision history.
> Transcribed from `discovery/decisions-draft.md` (locked over 1 interview round + sign-off).

## Summary

Split `.claude/commands/harness-layer/harness-build.md` (132 lines) into `harness-build`
(implement → tidy → draft PR) and `harness-review` (Codex gate → fixes → PR ready), both
files together under 132 lines, instructions-not-rationale. The review gate drops the
frozen-packet machinery for a sonnet-runner-driven Codex that diffs the branch itself;
failure hand-off is the PR itself, not gates or labels. A new every-session dev-log rule
file collects cross-plan lessons; implementation-notes.md grows into a chronological dev
log rendered as a dev-notes HTML page that replaces both the Deviations board and the ship
brief.

## Resolved Decisions

- **Q:** Command split and success bar?
  - **A:** Two commands — `harness-build` (implement → tidy → draft PR) and `harness-review` (Codex cross-check gate → fixes → PR ready). Combined length < 132 lines; instructions-not-rationale throughout.
  - **Why:** cheaper, faster, KISS; stated in the task.

- **Q:** Hand-off state between the two commands?
  - **A:** `spec.md`'s `## Tracking` is the sole shared state. Build ends by recording PR `#M` and its last pushed SHA there (plus anything the human must know at build end); review starts by reading it and refuses to run without a PR number.
  - **Why:** no other shared state; the Tracking block already carries issue/branch/worktree/profile.

- **Q:** State variables per command?
  - **A:** Declare only `PATH_TO_PLAN`, `ISSUE_NUMBER`, `PR_NUMBER`, `REVIEW_PROFILE` (sourced from `## Tracking`). Inline single-use constants — `STAGES`, simplifier names, `CROSS_CHECK`, `ROUND_INPUT`, `REQUIRED_PLUGINS` — into the sections that use them.
  - **Why:** only genuine state earns a variable.

- **Q:** How does Codex get the review input?
  - **A:** The orchestrator spawns a `sonnet` review runner (copying `harness-plan.md` § Codex Cross-Review's shape: retry-once, verdict-line grep, digest relay); Codex runs its own `git diff` over the review range, reviews, and reports back through the runner; the orchestrator spawns fixer subagents per model-selection. The `.agents/skills/implementation-review` skill is rewritten to match — the frozen-packet / zero-git contract and `round-N-input/` machinery are deleted.
  - **Why:** drops the packet-preparation cost; the skill must not drift from the real contract.

- **Q:** Round cap and human hand-off on failure?
  - **A:** Two rounds max. A round-2 `changes-requested` posts the final report comment, leaves the PR draft, and ends the run — no over-cap AskUserQuestion, no root-cause rule, no Locked Boundaries, no fix-design consult, no `status:needs-human` label. The draft PR + report comment tell the human they now own the remaining blockers.
  - **Why:** review focuses on reviewing; the PR is the notification surface.

- **Q:** Preflight?
  - **A:** Dropped entirely — no codex/plugin/gh probes; failures surface when the real command fails. Two STOPs survive, both read from `## Tracking`: build refuses without Issue `#N`; review refuses without PR `#M`.
  - **Why:** user note overrides the fold-into-compound-command work order.

- **Q:** implementation-notes.md and the dev-notes page?
  - **A:** `specs/_templates/implementation-notes.md` expands from deviations-only into a chronological per-plan dev log (phases, agent hand-offs, deviations, fixes, lessons), appended by both commands; `harness-review` renders `specs/<slug>/artifacts/dev-notes.html` from it at the end on any verdict, thariq-style, linked from the PR. It replaces the Deviations board row in `artifacts.md`'s inventory.
  - **Why:** the human can trace the entire agent process from one page.

- **Q:** Ship brief?
  - **A:** Dropped. The dev-notes page is the single completion page and leads with what shipped.
  - **Why:** two completion pages is one too many for a KISS split.

- **Q:** Cross-plan lesson store (name, loading, pruning)?
  - **A:** New `.claude/rules/development-log.md` — flat at the rules root, no `paths:`, loads every session. One line per lesson (`date · plan · lesson`), appended by build/review agents for hard-won cross-plan lessons. Capped ≈40 lines: on overflow, generalizable lessons are distilled into their proper rule file and their entries deleted. Both it and implementation-notes.md state the boundary: per-plan deviations/process → implementation-notes.md; cross-plan agent lessons → development-log.md.
  - **Why:** every-session loading only stays affordable with a hard cap and distillation path.

- **Q:** Memory-edit step?
  - **A:** Both commands end with a memory step: record session-worthy conventions per `memory-series.md` (cross-plan lessons → development-log; new/changed conventions → rule files / `AGENTS.md`). `harness-plan.md` gains one line requiring plans to mark tasks whose outcomes must be recorded to memory.
  - **Why:** lessons that should load in future sessions need a recording contract, and plans flag where to expect them.

- **Q:** Build order for tidy vs draft PR?
  - **A:** Tidy first, then open the draft PR at the first implementation checkpoint: spawn `harness-simplifier` / `code-simplifier` (auto-fix, behavior-preserving), then post their findings directly as the tidy PR comment. The held-report rule is deleted.
  - **Why:** stated in the task; no report can be held before a PR exists.

- **Q:** What carries over unchanged?
  - **A:** `git-workflow.md` mechanics (refspec pushes, marker-comment upserts, PR templates, labels), `REVIEW_PROFILE` gating, and the worktree rule.
  - **Why:** out of this task's blast radius.

## Assumptions

- The <132-line budget covers the two command files only; the rule file, skill rewrite, template, and `artifacts.md` edits sit outside it. Invalidated if the user meant the whole changeset.
- Both commands keep `model: fable` + `disable-model-invocation: true` frontmatter, matching every pipeline command. Invalidated if review should run cheaper.
- KB-grounding under `kb-grounded` survives minimally in both commands (build: check claims while implementing; review: Codex verifies claims against `ai-docs/`). Invalidated if it should be review-only.
- **Codex self-serves validation** (consequence of deleting `validation.md` with the packet): Codex runs the plan's Validation Commands itself in the `workspace-write` sandbox and records real results; a command it cannot execute is recorded as unexecuted-with-reason and blocks approval. Invalidated if validation should run lead-side and be handed to Codex.
- **Two one-line memory-truth edits ride along**: AGENTS.md's Core pipeline line gains `/harness-layer:harness-review` (+ the dev-log pointer memory-series.md requires for a new rule file), and git-workflow.md's draft-PR timing line says "after the tidy checkpoint". harness-ship.md's stale "after harness-build marks the PR ready" description is flagged as a follow-up, not edited. Invalidated if the user wants zero edits outside the ledger-named files or wants ship fixed now.
- **Round numbering across runs**: N = highest existing `codex-impl-review-round-*.md` + 1; each harness-review invocation performs at most 2 new rounds (a re-run after a human hand-off starts a fresh cycle, numbering continuing). Invalidated if 2 rounds should be a per-PR lifetime cap.

## Open Questions / Out of Scope

- **Out of scope:** `harness-ship.md`, the `spec-review` skill, discovery commands, issue/PR templates, `.claude/hooks/`.
- **Open question:** none — all interview dimensions resolved or N/A (performance & scale, security & authz, observability, rollout/migration).

## KB References

- `ai-docs/anthropic/memory.md` (fetched 2026-07-21, **gap-filled this plan**) — grounds `.claude/rules/development-log.md`: "Rules without `paths` frontmatter are loaded at launch with the same priority as `.claude/CLAUDE.md`"; rules directories are discovered recursively.
- `ai-docs/anthropic/skills.md` (fetched 2026-07-05) — custom commands are merged into skills; existing `.claude/commands/` files keep working with their frontmatter, so both commands reuse exactly the fields the current pipeline commands already run with (`description`, `argument-hint`, `model`, `disable-model-invocation`).
- `ai-docs/anthropic/agent-sdk/slash-commands.md` (fetched 2026-07-05) — command file format, `argument-hint`, `allowed-tools`, `$ARGUMENTS` substitution.
- `ai-docs/openai/codex/config-basic.md` (fetched 2026-07-05) — `model_reasoning_effort` config override used by the runner's `codex exec -c` flag.
- `ai-docs/openai/codex/models.md` (fetched 2026-07-11) — Codex model catalog + effort guidance backing model-selection.md's Codex rows.
- **Cross-check note:** the `claude-code-guide` subagent cross-check was denied this session; the reconcile step used a direct WebFetch of the official memory page instead (fresh fetch is authoritative — it became the gap-filled mirror above). No conflicts between cached docs and fetched content were found.
