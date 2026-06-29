# Tasks: Multi-Layer Review Pipeline for /build

> Execution plan for [spec.md](./spec.md). Owner and scope are defined there; this file is how & who.

## Implementation Phases

### Phase 1: Foundation

Create the three delegated capabilities `/build` will call — they have no
dependencies on each other and can be built in parallel: the 6 Codex review
subagents, the tailored `code-simplifier` agent, and the `claude-code-review` skill.

### Phase 2: Core Implementation

Wire the capabilities into the gate: upgrade the `implementation-review` skill into the
6-subagent orchestrator (depends on the subagents), then rewrite `/build` into the
worktree-first, draft-PR-early, multi-phase pipeline that sequences every layer and
owns commits + `gh` (depends on the agent, the skill, and the upgraded orchestrator).

### Phase 3: Integration & Polish

Validate the whole reworked workflow structurally and confirm nothing out-of-scope
changed.

## Team Orchestration

- You operate as the team lead and orchestrate the team to execute the plan.
- IMPORTANT: You NEVER operate directly on the codebase. You use the `Task*` tools to deploy team
  members to build, validate, test, and deploy. Your job is to direct, not to build.
- Keep the shared task list (TaskCreate/TaskUpdate) as the single source of truth for who is doing
  what; verify each task on the board before marking it complete.
- Note the session id / name of each team member — that is how you reference them.

## Team Members

- **Builder**
  - **Name:** builder-codex-agents
  - **Role:** Author the 6 `.codex/agents/*.toml` review subagents (read-only ports of
    `pr-review-toolkit` lenses) and run the headless subagent-spawn smoke-test.
  - **Agent Type:** `general-purpose`
  - **Resume:** true

- **Builder**
  - **Name:** builder-simplifier
  - **Role:** Author the tailored multi-language `code-simplifier` agent.
  - **Agent Type:** `general-purpose`
  - **Resume:** true

- **Builder**
  - **Name:** builder-claude-review
  - **Role:** Author the `claude-code-review` skill (ported pipeline, AGENTS.md-targeted).
  - **Agent Type:** `general-purpose`
  - **Resume:** true

- **Builder**
  - **Name:** builder-impl-review
  - **Role:** Upgrade the `implementation-review` skill into the 6-subagent
    orchestrator that writes one committed consolidated report.
  - **Agent Type:** `general-purpose`
  - **Resume:** true

- **Builder**
  - **Name:** builder-command
  - **Role:** Rewrite `.claude/commands/build.md` (worktree-first, draft-PR-early, the
    three new phases, Build-Status checklist, commit/push cadence).
  - **Agent Type:** `general-purpose`
  - **Resume:** true

- **Validator**
  - **Name:** validator-structural
  - **Role:** Run every Validation Command, the structural checks, and the
    scope-preserved diff check; confirm each acceptance criterion.
  - **Agent Type:** `general-purpose`
  - **Resume:** true

## Step by Step Tasks

- Execute every step in order, top to bottom. Each task maps directly to one `TaskCreate` call.
- Before starting, run `TaskCreate` for every task below so all team members can see the board.
- Each task names the acceptance criteria (from acceptance-criteria.md) it satisfies, so work traces to "done".

### 1. Create the 6 Codex review subagents

- **Task ID:** create-codex-subagents
- **Depends On:** none
- **Assigned To:** builder-codex-agents
- **Agent Type:** `general-purpose`
- **Parallel:** true
- **Satisfies:** AC5, AC9
- Create `.codex/agents/{review-code-standards,review-comment-accuracy,review-test-coverage,review-silent-failure,review-type-design,review-simplification}.toml`, each with `name`, `description`, `developer_instructions`, and `sandbox_mode = "read-only"`, per `https://developers.openai.com/codex/subagents`.
- `review-code-standards` checks against AGENTS.md (+ `~/.codex/AGENTS.md`, `.claude/rules/*`, `GIT-COMMIT-PR-MESSAGE.md`) and obvious bugs; the others mirror `pr-review-toolkit`'s comment/test/silent-failure/type/simplification lenses.
- Each subagent's instructions: review the working-tree diff, report only grounded findings (file + reason), edit nothing, and return findings to the orchestrator.
- Add an optional `.codex/config.toml` `[agents]` note (max_threads 6 / max_depth 1 are the defaults that already fit).
- **Verify (fail loud):** smoke-test that `codex exec -s read-only` can spawn at least one named subagent headlessly; record the result so `builder-impl-review` knows whether to use spawn or sequential-pass mode.

### 2. Create the tailored code-simplifier agent

- **Task ID:** create-simplifier-agent
- **Depends On:** none
- **Assigned To:** builder-simplifier
- **Agent Type:** `general-purpose`
- **Parallel:** true
- **Satisfies:** AC3, AC9
- Create `.claude/agents/code-simplifier.md` with valid frontmatter (`name`, `description`, `model: opus`) and a multi-language body: Python (`uv`, type hints, full-width rich panels), TS/Next.js/React (ES modules, `function` decls, explicit `Props`, server/client boundaries, no nested ternaries), and the Markdown harness layer.
- Encode the hard guardrail: when simplifying prompt/Markdown files (skills/agents/commands/rules), preserve every instruction's semantics — never weaken, reorder away, or drop a rule.
- Reference AGENTS.md as the standard; scope to recently-modified files; preserve functionality.

### 3. Create the claude-code-review skill

- **Task ID:** create-claude-review-skill
- **Depends On:** none
- **Assigned To:** builder-claude-review
- **Agent Type:** `general-purpose`
- **Parallel:** true
- **Satisfies:** AC4, AC9
- Create `.claude/skills/claude-code-review/SKILL.md` with valid frontmatter and the ported `code-review` pipeline: eligibility gate (skip trivial/docs-only) → list the standards files (AGENTS.md + `~/.codex/AGENTS.md` + `.claude/rules/*` + `GIT-COMMIT-PR-MESSAGE.md`) → summary → 5 parallel Sonnet lenses (AGENTS.md adherence / shallow bugs / git history / prior PRs / code comments) → per-finding Haiku 0–100 confidence with the verbatim rubric + false-positive examples → keep ≥80.
- Target the diff `git diff origin/main...HEAD`; use model aliases (`haiku`/`sonnet`), never dated ids.
- Two output sinks: (a) a concise, permalink-cited PR comment, and (b) the filtered ≥80 findings returned to `/build` for fixing. The skill itself edits no source.

### 4. Upgrade the implementation-review skill to a 6-subagent orchestrator

- **Task ID:** upgrade-impl-review
- **Depends On:** create-codex-subagents
- **Assigned To:** builder-impl-review
- **Agent Type:** `general-purpose`
- **Parallel:** false
- **Satisfies:** AC5, AC6, AC9
- Rewrite `.agents/skills/implementation-review/SKILL.md` so the skill, run via `codex exec -s workspace-write`, (a) reads `spec.md` + `decisions.md`, (b) runs the plan's Validation Commands and records real PASS/FAIL, (c) spawns the 6 `.codex/agents` subagents on the diff (or, if headless spawn is unavailable per Task 1, runs the 6 lenses as sequential passes — state which mode in the report), (d) collects + dedups their findings + its own plan-adherence findings.
- Write ONE consolidated report to `specs/<plan>/reviews/codex-impl-review-round-N.md`: first line `### Round N — Verdict: approved|changes-requested`, a `Validation:` block, findings grouped by lens/severity, digest-first. Round number N is injected by the prompt.
- Return only a terse summary (verdict line + finding count) to the caller; Codex edits no source — Claude's builders fix. Mirror `spec-review`'s file-write + terse-return + never-touch-source contract.

### 5. Rewrite the /build command

- **Task ID:** rewrite-build-command
- **Depends On:** create-simplifier-agent, create-claude-review-skill, upgrade-impl-review
- **Assigned To:** builder-command
- **Agent Type:** `general-purpose`
- **Parallel:** false
- **Satisfies:** AC1, AC2, AC3, AC4, AC6, AC7, AC8
- Rewrite `.claude/commands/build.md` with the worktree-first bootstrap (arg-or-autodiscover via `.claude/worktrees/*/specs/<plan>/spec.md`; resolve `spec.md` only AFTER `EnterWorktree`; `#N` from `## Tracking` is the source of truth).
- Add the draft-PR-early step (`gh pr create --draft` on the convention branch, `Closes #N`, seed the 7-item Build-Status checklist) and the final `gh pr ready` + Result tick.
- Sequence the phases with their commit/push cadence (trailer-free `Refs #N`, scoped `git add`): implement → internal-check (code-simplifier) → Claude code-review (skill, fix, PR comment) → Codex cross-review loop (per round: invoke `implementation-review` via `codex exec`, commit the `specs/<plan>/reviews/codex-impl-review-round-N.md` report, read the verdict from that file, relay to PR, tick; fix on `changes-requested`) — max 2 rounds.
- Preserve every existing guard (never merge, never push to `main`, graceful-skip on no-gh / no-issue / no-codex) and the legacy `plan.md` fallback.

### 6. Validate Everything

- **Task ID:** validate-all
- **Depends On:** create-codex-subagents, create-simplifier-agent, create-claude-review-skill, upgrade-impl-review, rewrite-build-command
- **Assigned To:** validator-structural
- **Agent Type:** `general-purpose`
- **Parallel:** false
- **Satisfies:** AC9, AC10
- Run every command in acceptance-criteria.md → `## Validation Commands`.
- Verify each acceptance criterion (AC1–AC10) is met, including the scope-preserved check (no diff to `/plan-w-team`, `/ship`, `spec-review`, or `specs/_templates/`).
- Do a human read-through of `build.md`, the new skill, the agent, and the 6 TOMLs for prompt-quality issues a structural check can't catch (fail loud on anything unclear).
