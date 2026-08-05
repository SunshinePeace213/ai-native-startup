---
description: Drafts a concise engineering implementation plan for any coding OR harness-layer task — grounded in the ai-docs/ knowledge base when the work touches the harness — and saves it to the specs directory. Fills only blocking gaps via a bounded readiness gate; heavy unknowns bounce to /harness-layer:harness-interview
argument-hint: [finalized prompt] [orchestration prompt]
model: fable
effort: xhigh
disable-model-invocation: true
disallowed-tools: Task, EnterPlanMode
hooks:
  Stop:
    - hooks:
        - type: command
          command: uv run --script "$CLAUDE_PROJECT_DIR"/.claude/hooks/check_spec_completeness.py
---

# Harness Plan

Turn `USER_PROMPT` (ideally the finalized prompt from `/harness-layer:harness-interview`) into a spec folder the team can build from — for any coding OR harness-layer task. Resolve what the codebase and KB answer, fill only genuinely-open gaps through the `Readiness Gate`, and never re-litigate a locked ledger. When the work touches the harness layer, ground every claim in the KB first (see `Domain Knowledge`); otherwise plan straight from the codebase. Draft at `specs/<name-of-plan>/` on the chain's worktree (or a fresh one) to the bar in `spec-standards.md`, push to GitHub, publish the implementation-plan page for the user's review, gate with the `codex-gate` skill, and end at its human gate — the user always decides what happens next.

## Variables

USER_PROMPT: $1
ORCHESTRATION_PROMPT: $2 - (Optional) Guidance for team assembly, task structure, and execution strategy
KNOWLEDGE_BASE: `ai-docs/` — cached official docs; catalog in `ai-docs/index.md`, manifest in `ai-docs/sources.yaml`
STALE_AFTER: `30` days — a KB doc older than this is stale

## Instructions

- **PLANNING ONLY** — draft the spec; do not build, write code, or deploy builder agents. Allowed subagents: the `claude-code-guide` KB cross-check, `kb-fetcher` for KB mirrors (never write mirror content yourself), and the `opus` page author. You write the spec files and any plan-local check scripts yourself — they are one coupled artifact and splitting authorship breaks traceability.
- If no `USER_PROMPT` is provided, stop and ask the user for it.
- **Route first.** When the request passes every direct-lane check — ≤2 files and roughly ≤80 changed lines; docs/chore/style/fix with an obvious local cause; no executable surface (`.claude/hooks/`, `settings.json`, `checks/`, `scripts/`, `.github/workflows/`) and no security boundary; no new command, skill, agent, or rule — stop and recommend `/harness-layer:harness-direct "<request>"`. When in doubt, keep the full lane.
- Determine the task type (feat|fix|docs|style|refactor|perf|test|chore) and complexity (simple|medium|complex).
- If `ORCHESTRATION_PROMPT` is provided, let it guide team composition, task granularity, dependency structure, and parallel/sequential decisions.
- **Draft to the bar.** `spec-standards.md` (auto-loaded on `specs/**`) is the same checklist the Codex gate judges against — self-check the draft against every standard before pushing.
- **Ground harness-layer claims.** When the expert layer is active, statements about hooks, frontmatter, subagents, skills, commands, MCP, or model aliases must trace to a KB doc; record what you consulted in decisions.md's `## KB References`.

## Domain Knowledge

Conditional expert layer. Run it only when the task touches the harness surface — any of `.claude/`, `.codex/`, `ai-docs/`, the memory files (CLAUDE.md, AGENTS.md), or a domain that has an `ai-docs/index.md` entry. When no signal fires, state that the expert layer is skipped, read no KB docs, and set the review profile to `standard`. When a signal fires, set the profile to `kb-grounded` and run collect → cross-check → reconcile:

1. **Collect.** Read `ai-docs/index.md` and open every cached doc relevant to the request's surface. A doc older than `STALE_AFTER` → continue with the stale copy, note it in decisions.md `## KB References`, and flag it in the Report with a `/harness-layer:kb` suggestion.
2. **Cross-check.** Deploy a `claude-code-guide` subagent with the specific harness claims the plan depends on, asking it to verify them against current official behavior.
3. **Reconcile.** Sources agree → continue. They conflict on a claim → refresh that mirror via a `kb-fetcher` subagent (the entry's url + the absolute target path in the worktree), then Read the fresh mirror — it wins; log the conflict + resolution in decisions.md `## KB References`. Fetch fails → prefer the source with the newer verifiable date and mark the claim unverified in the spec.
4. **Gap-fill.** The KB lacks a doc the plan depends on → spawn a `kb-fetcher` subagent with the official URL (ask the claude-code-guide subagent if unsure) and the absolute target path under `ai-docs/` in the worktree, add its `ai-docs/sources.yaml` entry, then Read the fresh mirror — all committed with the spec.
5. Log every doc you relied on — path, `fetched` date, and the claim it grounds — in decisions.md's `## KB References` table.

## Readiness Gate

No re-interviewing a locked ledger; a bounded ask only for what's genuinely open.

- **Ledger.** When `specs/<slug>/discovery/decisions-draft.md` exists in the worktree, transcribe it into decisions.md — resolved decisions stay resolved. Reference discovery pages from the spec; never copy them.
- **Assess coverage:** first resolve every point the codebase and KB can answer, so only genuinely-open decisions remain. Then:
  - **Fully covered** → ask nothing; go straight to design.
  - **A few open points** → ONE `AskUserQuestion` round (≤4 questions, biggest blast radius first); fold answers into decisions.md and any related spec file.
  - **Many unknowns / no defensible approach** → STOP and recommend `/harness-layer:harness-interview "<USER_PROMPT>"`.
- **Residual gaps** after asking → pick your recommended answer and record it in decisions.md `## Assumptions` with what would invalidate it. Never stall.
- **Revision.** When the worktree already holds `specs/<slug>/spec.md`, this run is a revision — see `Revision Mode`.

## Workflow

IMPORTANT: **PLANNING ONLY** — do not execute, build, or deploy builder agents. Output is a plan document.

1. Enter Worktree — `Worktree:` line in the prompt → `EnterWorktree(path: ...)`; otherwise `EnterWorktree(name: "<slug>")` (see `Worktree & Handoff`). An existing `specs/<slug>/spec.md` switches the run to `Revision Mode`.
2. Readiness Gate — transcribe any discovery ledger, assess coverage, and fill only genuinely-open gaps.
3. Understand Codebase & Set Review Profile — read the relevant code and the `specs/lessons/digest.md` rows matching the touched surface (fold their pitfalls into the draft); apply the `Domain Knowledge` trigger and set `kb-grounded` or `standard`.
4. Design & Draft — the technical approach, grounded in the KB when the expert layer is active. Define the team and tasks from the available agent types (default `general-purpose`) — IDs, dependencies, assignments, each task's model + effort stamped per the model-selection rule; mark any task whose outcome must be recorded to memory. Write the spec folder (see `Output`), including one executable check script per acceptance criterion, then self-check every file against `spec-standards.md`.
5. Name, Issue & Push — reuse the chain `<slug>` (rename with `git mv` only if actively wrong) or generate a descriptive kebab-case name; pick the change `<type>`; first cycle only, create and link the issue; commit and push per `Worktree & Handoff`.
6. Spec Lint — `uv run scripts/spec_lint.py specs/<name-of-plan>/` from the worktree root; fix every FAIL yourself, re-run to green, and commit+push the fixes (`Refs #N`). The gate re-runs this lint first.
7. Implementation-Plan Page — spawn the page author now, in the background (see `Plan Artifacts`), so the user reviews while the gate runs.
8. Codex Gate — invoke the `codex-gate` skill and follow it to its human gate: the lint, lens panel, ledger, classification, dispute handling, the user's decision, and the self-improve step all live there.
9. Report — commit and push anything still uncommitted (the page, ledger, standards amendments), then summarize (see `Report`).

## Output: Spec Folder

Write the plan under `specs/<name-of-plan>/`. Copy each file from `specs/_templates/`, then replace every `<placeholder>` with real content; the templates' HTML comments are guidance, not content, so a section holding only a comment counts as unwritten. Keep each template's `##` headings exactly as written — a Stop hook blocks the run while any required section is missing, empty, or still holds a placeholder.

```text
specs/<name-of-plan>/
├── discovery/             # committed by the pre-plan passes; reference, never copy
├── spec.md                # what & why: task, objective, non-goals, locked decisions, tracking, review record
├── tasks.md               # how & who: phases, team members, step-by-step tasks
├── decisions.md           # the interview record (+ ## KB References when the expert layer is active)
├── acceptance-criteria.md # done: testable criteria, each mapped to validation commands
├── checks/                # plan-local scripts, only where no suite or validator covers an AC — `uv run` for Python, `bun` for JS/TS, bash otherwise; pass = exit 0
├── artifacts/             # implementation-plan page (+ reference map when porting semantics)
└── reviews/               # Codex round reports + findings-ledger.md (the gate writes these)
```

When filling them:

- Include the conditional sections (`## Problem Statement` and `## Solution Approach` in spec.md, `## Implementation Phases` in tasks.md) only when task_type is feature or complexity is medium/complex; `## Interfaces & Contracts` only when the change adds or alters an interface, and `## KB References` in decisions.md only under `kb-grounded`. Delete a section you omit rather than leaving it empty.
- Volatile-decisions-first: within spec.md's existing `##` headings (do not rename or reorder them), lead with the decisions most likely to change — data model, type/interface signatures, anything user-facing.
- Prefer the project's own suite or a checked-in validator over a bespoke script; when a plan-local script is the only option, name it `ac<N>-<slug>.<ext>`, self-contained and runnable from the repo root. Every validation command must fail if the change is reverted.

## Plan Artifacts

Right after the first push, spawn one background `Agent` (`subagent_type: "general-purpose"`, `model: "opus"`) to author the **Implementation plan** page from the committed spec folder into `specs/<name-of-plan>/artifacts/` and publish it, following `.claude/rules/harness-layer/artifacts.md`. When the plan ports semantics from a reference implementation named in the prompt, the same agent also authors the **Reference map** page. Commit and push the page files when the agent returns (`Refs #N`); publishing never blocks. Simple plans skip artifacts. If the Codex gate later changes the spec materially, have the agent re-author and republish from the final state.

## Worktree & Handoff

Every plan gets a GitHub issue and its convention branch before anything is pushed. Run the steps in order; if any `gh` call fails, STOP and tell the user how to fix it — never proceed degraded or with a placeholder issue.

- **Enter the worktree.** The discovery chain usually created it — `EnterWorktree(path: ".claude/worktrees/<slug>")`; without one, `EnterWorktree(name: "<slug>")` branches from `origin/main` into `.claude/worktrees/<slug>`. Write the spec folder there, never on `main`. Discovery commits already on the branch ride along with the first push.
- **Create the issue** (first cycle only). Pick the skeleton kind from `<type>` — feat→`feature`, fix→`bug`, docs/style/refactor/perf/test/chore→`chore`, `epic` only for a genuine multi-issue initiative. Fill `specs/_templates/issues/<kind>.md` from the interview ledger and Assumptions, write it to a temp file, and create the issue: `gh issue create --title "<emoji> <type>: <plan title>" --body-file <tmp> --label <type> --label priority:P<0-3> --assignee <login>` (gitmoji from the commit table) — exactly one type label, one priority label, and your GitHub login (`gh api user -q .login`). Note the returned issue number `#N`.
- **Link the branch.** `gh issue develop <N> --base main --name <type>/<N>-<slug>`.
- **Tracking.** In spec.md's `## Tracking`, record Type and Complexity, Issue `#N`, Branch `<type>/<N>-<slug>`, the absolute worktree path (`git rev-parse --show-toplevel`), and `Review profile: kb-grounded|standard`.
- **Commit.** Stage the spec folder plus any gap-filled KB docs and make one commit `<emoji> <type>(spec): draft plan for <name-of-plan>` with a `Refs #N` footer.
- **Push.** `git push -u origin HEAD:refs/heads/<type>/<N>-<slug>` (bare `git push` refuses from the local `worktree-<slug>` branch).
- **Plan-links comment.** After the first push, upsert one issue comment keyed `<!-- plan-links -->` linking the four spec files as blob URLs on the convention branch — upsert per `pr-process.md` § Idempotent Marker Comments.

## Revision Mode

When the worktree already holds `specs/<slug>/spec.md`:

- Apply the input (tweak prompt from the page, or resolved blockers) to the spec files and checks; log what changed and why in decisions.md. Keep issue `#N` from `## Tracking` — no new issue, no new branch, no re-litigating resolved decisions.
- Commit with `Refs #N` and push with the same refspec; have the page author republish.
- Run a fresh `codex-gate` cycle — round numbers and the findings ledger continue from where they left off; the cap never resets to grant free rounds.
- When the gate reaches `approved` (or the user proceeds) after a prior park, remove the label: `gh issue edit <N> --remove-label status:needs-human`.

## Report

After the gate's human decision, provide a concise report:

```text
✅ Spec Folder Created

Folder: specs/<name-of-plan>/ (spec.md, tasks.md, decisions.md, acceptance-criteria.md<, checks/ when used>)
Issue: #N <url>
Branch: <type>/<N>-<slug> — pushed to origin
Worktree: <absolute worktree path>
Review profile: <kb-grounded | standard>
Spec Lint: <clean | N catches fixed pre-gate>
Codex Gate: <approved at round N | user chose <proceed|revise|park> — <open blockers | dispute | codex-unavailable>>
Ledger: <X blocking fixed, Y advisory recorded, Z disputed — lens substitutions: <none | list>>
Checks: <N validation commands — M plan-local scripts under checks/>
KB Grounding: <N docs consulted, M gap-filled — or "none (standard profile)">
Assumptions: <count recorded in decisions.md, or "none">
Page: <implementation-plan page URL + committed path, or "none — simple plan">
Standards: <amended: <one line> | unchanged>
Topic: <brief description of what the plan covers>
Key Components:
- <main component 1>
- <main component 2>

Team Task List:
- <list of tasks, and owner (concise)>

Review the plan on the implementation-plan page — paste one of its tweak prompts back to revise.
When you're ready, execute the plan in a new agent by running:
/harness-layer:harness-build <name-of-plan>
```

On a revise or park outcome, end with the gate's recovery prompt instead of the build hand-off.
