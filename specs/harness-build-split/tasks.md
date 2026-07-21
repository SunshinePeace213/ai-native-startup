# Tasks: Split harness-build into build + review commands

> Execution plan for [spec.md](./spec.md). Owner and scope are defined there; this file is how & who.

## Implementation Phases

### Phase 1: Core Implementation

Three file-disjoint tasks run in parallel: the command pair, the skill rewrite, and the
notes/rules edits. The command pair and the skill both implement the **runner-prompt
contract pinned in spec.md § Requirements & Decisions** — neither derives it from the other.

### Phase 2: Integration & Polish

Validation sweeps every acceptance criterion (line budget, greps, template sections) after
all Phase 1 tasks land.

## Team Orchestration

- You operate as the team lead and orchestrate the team to execute the plan.
- IMPORTANT: You NEVER operate directly on the codebase. Your job is to direct, not to build.
- The `Task*` tools coordinate the board; they deploy nobody. Create every task with
  `TaskCreate`, then **spawn each builder with the Agent tool** per task-tools.md — model via
  the `model` param, effort in the task brief — and assign it as the task's owner.
- Keep the shared task list (TaskCreate/TaskUpdate) as the single source of truth for who is doing
  what; verify each task on the board before marking it complete.
- Note the session id / name of each team member — that is how you reference them.

## Team Members

- **Builder**
  - **Name:** builder-commands
  - **Role:** Author the two command files against the shared line budget and hand-off contract
  - **Agent Type:** general-purpose
  - **Resume:** true
- **Builder**
  - **Name:** builder-skill
  - **Role:** Rewrite implementation-review/SKILL.md to the runner-prompt contract
  - **Agent Type:** general-purpose
  - **Resume:** true
- **Builder**
  - **Name:** builder-notes
  - **Role:** Dev-log template, development-log rule, and the four one-line memory-truth edits
  - **Agent Type:** general-purpose
  - **Resume:** true
- **Validator**
  - **Name:** validator
  - **Role:** Run every validation command and check each AC
  - **Agent Type:** general-purpose
  - **Resume:** false

## Step by Step Tasks

- Execute every step in order, top to bottom. Each task maps directly to one `TaskCreate` call.
- Before starting, run `TaskCreate` for every task below so all team members can see the board.
- Each task names the acceptance criteria (from acceptance-criteria.md) it satisfies, so work traces to "done".

### 1. Author the command pair

- **Task ID:** write-command-pair
- **Depends On:** none
- **Assigned To:** builder-commands
- **Agent Type:** general-purpose
- **Model / Effort:** `opus` / `high`
- **Parallel:** true
- **Satisfies:** AC1, AC2, AC3, AC4, AC5, AC9, AC10
- Rewrite `.claude/commands/harness-layer/harness-build.md`: frontmatter (`description`, `argument-hint: [name-or-path-of-plan]`, `model: fable`, `disable-model-invocation: true`); Variables = `PATH_TO_PLAN`, `ISSUE_NUMBER`, `PR_NUMBER`, `REVIEW_PROFILE` only; workflow = resolve plan → STOP without Issue `#N` in `## Tracking` → enter/restore worktree → read plan (+ KB docs under `kb-grounded`) → create `implementation-notes.md` from the template → deploy builders per tasks.md stamps → checkpoint commits+pushes → tidy (`harness-simplifier` for harness files / `code-simplifier` for app code, both `opus`, auto-fix, behavior-preserving) → open draft PR from `.github/PULL_REQUEST_TEMPLATE/<type>.md` via `--body-file` (never `--template`), mirror issue labels, seed body (`## Plan` links + `Closes #N`, stage table Implementation → Tidy → Codex R1 → Fixes → Codex R2 → Ready, Agent Task Manifest, `## Review Reports`, `## Dev Notes`, `## Follow-ups`) → post tidy findings directly as `<!-- report:tidy -->` (upsert; no holding) → tick Implementation + Tidy → append the dev-log entries and run the memory step per memory-series.md, commit+push (every repository write is now done) → snapshot `HANDOFF_SHA=$(git rev-parse HEAD)` → record `PR: #M` + `Hand-off SHA: <sha>` (+ anything the human must know) in `## Tracking` as ONE final metadata commit, push → report ending "Next: /harness-layer:harness-review <name>".
- Create `.claude/commands/harness-layer/harness-review.md`: same frontmatter fields; same four Variables; workflow = resolve plan → read `## Tracking` → STOP without `PR #M` → enter/restore worktree → read plan + implementation-notes.md → attempts (invocation-local A = 1–2 drives control flow; global report number N = highest existing report + 1 names the report and picks the review range): spawn the `sonnet` runner with the spec.md runner-prompt contract (it runs `codex exec -C "<worktree root>" -s workspace-write --model <codex-model> -c model_reasoning_effort="<effort>"` — model/effort per model-selection — checks exit status + verdict line, retries the identical command once, returns ONLY verdict + digest) → post digest as `<!-- report:codex-round-N -->` (upsert) → attempt-1 `changes-requested`: commit report, spawn fixers per model-selection (failed fix escalates a tier), ONE fix commit, push both, attempt 2 → terminal outcome (any `approved`, or attempt-2 `changes-requested`): render `artifacts/dev-notes.html` from implementation-notes.md (medium/complex; per artifacts.md) and run the memory step FIRST, then ONE terminal commit (report + dev-notes + dev-log/memory/notes edits), push, link the page under `## Dev Notes` — on `approved`: verify the PR head equals the terminal commit, tick stages with it as Ready evidence, `gh pr ready`; nothing mutates the repo after it — on attempt-2 `changes-requested`: post the final report comment, PR stays draft, human owns → report ("Next: /harness-layer:harness-ship <slug>" on approved; "human owns the PR blockers" otherwise).
- Both files: instructions-not-rationale; no Preflight, no held report, no `round-N-input/`, no needs-human/over-cap/root-cause/Locked-Boundaries/consult; a mid-round push discards and re-runs the round; empty diff and missing verdict are never approvals; lean on always-loaded rules (git-workflow, model-selection, task-tools) instead of restating them. Combined `wc -l` < 132.
- **Record to memory:** if the line budget forces cutting a contract item, that trade-off is a cross-plan lesson for development-log.md.

### 2. Rewrite the implementation-review skill

- **Task ID:** rewrite-review-skill
- **Depends On:** none
- **Assigned To:** builder-skill
- **Agent Type:** general-purpose
- **Model / Effort:** `opus` / `medium`
- **Parallel:** true
- **Satisfies:** AC6
- Rewrite `.agents/skills/implementation-review/SKILL.md` to the spec.md runner-prompt contract. Codex: derives its own diff (`git diff --name-status/--numstat` + full diff over the injected `BASE_SHA..REVIEWED_HEAD_SHA`, excluding `specs/<name>/reviews/` and `specs/<name>/artifacts/`); reads the four plan files + `implementation-notes.md` on round 1 (delta rounds: prior report + delta only); **runs the plan's Validation Commands itself**, recording real results — unexecutable commands recorded with reason and blocking, never fabricated; keeps deterministic lens selection from `.codex/agents/*.toml` (+ sequential-vs-spawn mode line), the KB-grounding pass with its signal triggers, the confidence filter (floor 80), and the blocking/advisory split.
- Delete: Review packet / attestation / `round-N-input/` inputs, zero-git and zero-shell rules, `validation.md` judging, Locked Boundaries, fix-author (`Author: codex`) handling, contract-defect checks that referenced the packet.
- Report format: first line `### Round N — Verdict: approved|changes-requested` (em-dash, verbatim N); keep Scope/SHAs/Mode/Profile/Lenses/Findings/Validation lines and prior-blocker dispositions on delta rounds; **end with an `**Issue-comment digest:**` paragraph** (mirror spec-review's — round, verdict, blocking count + headlines, next action). Terse two-line CLI return; git read-only (diff/log only — no commits); never call `gh`; write only the round report; a round that cannot run or writes no verdict is re-run by the caller, never an approval; update the frontmatter `description` to the new contract.

### 3. Dev-log template, rule file, and memory-truth edits

- **Task ID:** notes-rules-pointers
- **Depends On:** none
- **Assigned To:** builder-notes
- **Agent Type:** general-purpose
- **Model / Effort:** `sonnet` / `medium`
- **Parallel:** true
- **Satisfies:** AC7, AC8, AC9 (harness-plan line)
- Expand `specs/_templates/implementation-notes.md`: chronological per-plan dev log — intro naming both appending commands, a stated boundary (per-plan phases/hand-offs/deviations/fixes/lessons here; cross-plan one-liners → `.claude/rules/development-log.md`), and a `## Log` section of append-only dated entries (`- **<date> · <phase|event>** — <what happened; deviations state plan-said-X / did-Y / why>`). Keep it a template: placeholders, no rationale.
- Create `.claude/rules/development-log.md`: no frontmatter; states it loads every session; one line per lesson `YYYY-MM-DD · <plan> · <lesson>`; appended by harness-build/harness-review memory steps; cap ≈40 lines — at the cap, distill generalizable lessons into their proper rule file and delete their entries; the same per-plan vs cross-plan boundary sentence; an empty `## Lessons` list to start.
- `.claude/rules/harness-layer/artifacts.md`: replace the Deviations board inventory row with `| Build + review / dev log | **Dev notes** | The implementation-notes.md log as a chronological timeline — phases, hand-offs, deviations, fixes, lessons — rendered by /harness-layer:harness-review on any verdict; linked from the PR |`.
- `.claude/commands/harness-layer/harness-plan.md`: in Workflow step 6 (Define Team & Tasks), append one line/clause: mark any task whose outcome must be recorded to memory — the build/review memory steps record exactly those.
- `.claude/rules/git-workflow.md`: change "opens a **draft** PR right after the first implementation checkpoint" to "right after the tidy checkpoint"; touch nothing else.
- `AGENTS.md`: Core pipeline line becomes plan → build → review → ship (add `/harness-layer:harness-review`); add one Harness Development bullet pointing to `.claude/rules/development-log.md` (cross-plan lessons) vs per-plan `implementation-notes.md`.

### 4. Validate Everything

- **Task ID:** validate-all
- **Depends On:** write-command-pair, rewrite-review-skill, notes-rules-pointers
- **Assigned To:** validator
- **Agent Type:** general-purpose
- **Model / Effort:** `sonnet` / `low`
- **Parallel:** false
- Run every command in acceptance-criteria.md → `## Validation Commands`.
- Verify each acceptance criterion is met; report any FAIL with the exact output.
