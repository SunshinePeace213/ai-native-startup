# Plan: Git Workflow & Issue/PR/Commit + Agent-Task Lifecycle Tracking

## Task Description

Establish a single documented Git-workflow standard for this repo and wire it into the
two existing workflows (`/plan-w-team` and `/build`) and their Codex review gates. The
standard defines: gitmoji + Conventional-Commits messages, issue-numbered branches,
eight per-type PR templates, four curated issue templates, and a "Model C" linking
scheme whose durable join key is the **GitHub issue number** (no Jira). The two
workflows are upgraded to share **one worktree, one branch, one issue, and one PR**
end-to-end. `/plan-w-team` opens a single Epic/Plan issue at draft and posts each
Codex **spec-review** round as a comment on it; `/build` resumes the same worktree,
opens a single PR (`Closes #N`) on completion, and posts each Codex
**implementation-review** round as a Build-Status update — **never merging to
`main`**. Codex stays verdict-only; **Claude relays** verdicts to GitHub via `gh`,
degrading gracefully if `gh` is unavailable. `AGENTS.md` is user-owned: agents produce
a paste-ready `GIT-COMMIT-PR-MESSAGE.md` plus precise merge instructions, and the **user**
merges it **before** `/build`. Enforcement is documentation-only — no scripts, hooks,
or CI.

## Objective

When this plan is complete:

1. A canonical `GIT-COMMIT-PR-MESSAGE.md` at the repo root exists with the "Git Workflow & Pull
   Requests" content **and** a one-line `AGENTS.md` pointer to it (user-applied).
2. `.github/ISSUE_TEMPLATE/` holds 4 tailored templates + `config.yml`, and
   `.github/PULL_REQUEST_TEMPLATE/` holds 8 per-type templates.
3. `.claude/commands/plan-w-team.md` creates one Epic/Plan issue at draft, enters a
   worktree, posts each spec-review round to that issue, and records `#N` + branch +
   worktree path.
4. `.claude/commands/build.md` resumes that worktree, opens one PR (`Closes #N`) with
   the matching template + Agent Task Manifest, maintains a Build-Status checklist +
   per-phase comments, and never merges to `main`.
5. Both Codex skill files note that Claude relays their verdict to the tracking
   issue/PR; their verdict contract is unchanged.
6. `AGENTS.md` is **not** modified by any agent; merging it is a documented,
   user-performed step gated before `/build`.

## Requirements & Decisions

- **Linking model = Model C.** One GitHub issue per intent; ephemeral Agent Tasks;
  the PR body carries an Agent Task Manifest as the single durable audit point; durable
  join key = issue number. Vocab: `Closes #N` (PR only) / `Refs #N` (commits) /
  `Part of #N` (epic).
- **One shared worktree, plan→build→PR.** `/plan-w-team` enters it (issue-first so the
  intended branch carries `#N`); `/build` resumes it via `EnterWorktree(path=…)`.
  **Discovery:** `EnterWorktree` mangles the local branch name (`feat/x` →
  `worktree-feat+x`), so the convention is enforced on the **remote** branch via an
  explicit push refspec and `#N` is the recorded source of truth, not parsed from the
  local branch.
- **Documentation-only enforcement**; **never auto-merge to `main`**; **`AGENTS.md` is
  user-merged** before `/build`.
- Full record in `decisions.md`.

## Problem Statement

The repo has aspirational Git rules in `AGENTS.md` that don't match practice (history
is sentence-style, not Conventional Commits), references a PR template that does not
exist, and has no issue templates and no traceability between its AI-orchestration
layer (the `Task*` tools) and durable GitHub artifacts. The Codex review gates in
`/plan-w-team` and `/build` produce verdicts that live only in local files, so a human
cannot watch the spec/build progress on GitHub. There is no convention tying an
intent (issue) → branch → commits → PR → back to the issue, and no rule for how
Claude's worktree isolation interacts with branch naming.

## Solution Approach

Build the standard as the foundation, then layer the workflow automation on top:

1. **Foundation — standards & templates.** Author the mergeable `GIT-COMMIT-PR-MESSAGE.md`
   (branching, gitmoji+CC commits, the 8 PR templates' usage, the 4 issue templates,
   the Model-C linking vocab, and the worktree rule incl. the remote-refspec
   correction). Create the `.github/` issue and PR template files.
2. **Core — workflow lifecycle tracking.** Edit `plan-w-team.md` to create/track the
   single Epic/Plan issue and enter the worktree; edit `build.md` to resume the
   worktree, open/track the single PR, and never merge `main`. Add relay notes to the
   two Codex skills.
3. **Integration & polish.** Validate file presence, template tailoring, YAML config,
   and the no-merge / no-AGENTS-edit / no-tooling guarantees; confirm the AGENTS.md
   merge-handoff instructions are precise.

The issue number threads everything: `/plan-w-team` creates `#N` and records it;
`/build` reads it and opens a PR that `Closes #N`. Codex remains a sandboxed
verdict-emitter; Claude is the only actor that calls `gh`.

## Relevant Files

Use these files to complete the task:

- `AGENTS.md` — **read-only for agents.** Current home of the (aspirational) Git
  rules; the standalone doc's merge instructions target its "Git Workflow & Pull
  Requests" section. Agents must NOT edit it.
- `.claude/commands/plan-w-team.md` — the planning workflow; gains the GitHub
  Issue-tracking + worktree-by-default behavior and the `## Tracking` record step.
- `.claude/commands/build.md` — the build workflow; gains worktree-resume + single-PR
  lifecycle tracking + never-merge-main behavior.
- `.agents/skills/spec-review/SKILL.md` — Codex spec-review (appends to
  `## Codex Findings`); gains a one-paragraph relay note only.
- `.agents/skills/implementation-review/SKILL.md` — Codex implementation-review (final
  CLI message verdict); gains a one-paragraph relay note only.
- `.claude/rules/task-tools.md` — the orchestration protocol the Agent Task Manifest
  is copied from (`TaskList`); read for the manifest format.

### New Files

- `GIT-COMMIT-PR-MESSAGE.md` (repo root) — the canonical standard + a "How to merge into
  AGENTS.md" section describing the one-line pointer the user applies.
- `.github/ISSUE_TEMPLATE/feature.md` — feature request (problem, solution, acceptance
  criteria → task success criteria).
- `.github/ISSUE_TEMPLATE/bug.md` — bug report (repro, expected/actual, environment).
- `.github/ISSUE_TEMPLATE/chore.md` — chore/maintenance umbrella (refactor/perf/style/
  test/build/ci; scope + rationale).
- `.github/ISSUE_TEMPLATE/epic-plan.md` — epic/plan (links `specs/<feature>/plan.md`,
  child checklist, tracks the plan-w-team lifecycle).
- `.github/ISSUE_TEMPLATE/config.yml` — chooser config (e.g. `blank_issues_enabled`,
  contact links).
- `.github/PULL_REQUEST_TEMPLATE/{feat,fix,docs,style,refactor,perf,test,chore}.md` —
  8 per-type templates, each tailored; all include the linked-issue (`Closes #N`),
  Agent Task Manifest, and Build Status checklist anchors.

## Implementation Phases

### Phase 1: Foundation

Author `GIT-COMMIT-PR-MESSAGE.md` (the full standard + AGENTS.md merge instructions) and create
all `.github/` issue and PR templates. No workflow edits yet; this phase establishes
the vocabulary and files the workflows will reference (template filenames, manifest
format, `Closes #N`).

### Phase 2: Core Implementation

Edit `plan-w-team.md` and `build.md` to add the issue/PR lifecycle tracking and the
shared-worktree behavior, and add the relay notes to the two Codex skills. These edits
reference the Phase-1 template filenames and the linking vocab, so they depend on
Phase 1.

### Phase 3: Integration & Polish

Validate everything: file presence, per-type template tailoring, `config.yml` YAML
validity, the never-merge-main / never-edit-AGENTS / no-tooling guarantees, and that
the AGENTS.md merge instructions are precise and unambiguous.

## Team Orchestration

- You operate as the team lead and orchestrate the team to execute the plan.
- You're responsible for deploying the right team members with the right context to
  execute the plan.
- IMPORTANT: You NEVER operate directly on the codebase. You use `Task` and `Task*`
  tools to deploy team members to the building, validating, and testing tasks.
  - This is critical. Your job is to act as a high-level director of the team, not a
    builder.
  - Your role is to validate all work is going well and make sure the team is on track
    to complete the plan.
  - You'll orchestrate this by using the Task* Tools to manage coordination between the
    team members.
  - Communication is paramount. You'll use the Task* Tools to communicate with the team
    members and ensure they're on track to complete the plan.
- Take note of the session id of each team member. This is how you'll reference them.

### Team Members

No `.claude/agents/team/*.md` agents exist, so every builder uses the
`general-purpose` agent type.

- Builder
  - Name: builder-standards
  - Role: author `GIT-COMMIT-PR-MESSAGE.md` — the full standard plus exact `AGENTS.md` merge
    instructions.
  - Agent Type: general-purpose
  - Resume: true
- Builder
  - Name: builder-issue-templates
  - Role: create the 4 curated, tailored issue templates + `config.yml`.
  - Agent Type: general-purpose
  - Resume: true
- Builder
  - Name: builder-pr-templates
  - Role: create the 8 per-type, tailored PR templates.
  - Agent Type: general-purpose
  - Resume: true
- Builder
  - Name: builder-plan-workflow
  - Role: edit `plan-w-team.md` — single Epic/Plan issue creation, worktree-by-default,
    spec-review round comments, `## Tracking` record, graceful `gh` skip.
  - Agent Type: general-purpose
  - Resume: true
- Builder
  - Name: builder-build-workflow
  - Role: edit `build.md` — worktree resume, single PR (`Closes #N`, `--template`,
    manifest), Build-Status checklist + per-phase comments, never-merge-main, graceful
    `gh` skip.
  - Agent Type: general-purpose
  - Resume: true
- Builder
  - Name: builder-codex-relay
  - Role: add the one-paragraph relay note to both Codex skill files without altering
    their verdict contract.
  - Agent Type: general-purpose
  - Resume: true
- Builder
  - Name: validator
  - Role: run all Validation Commands and verify every Acceptance Criterion.
  - Agent Type: general-purpose
  - Resume: true

## Step by Step Tasks

- IMPORTANT: Execute every step in order, top to bottom. Each task maps directly to a
  `TaskCreate` call.
- Before you start, run `TaskCreate` to create the initial task list that all team
  members can see and execute.

### 1. Author the git-workflow standard doc

- **Task ID**: create-git-workflow-doc
- **Depends On**: none
- **Assigned To**: builder-standards
- **Agent Type**: general-purpose
- **Parallel**: true
- Write `specs/git-workflow-issue-pr-tracking/GIT-COMMIT-PR-MESSAGE.md` containing the
  paste-ready "Git Workflow & Pull Requests" sections: Branching Strategy
  (`<type>/<issue#>-<slug>`), Commit Message Rules (the gitmoji+CC format, the 8-type
  emoji table, `Refs #N` footer, subject rules), Pull Request Requirements (per-type
  templates, emoji title, `Closes #N`, bypass tokens), Issue Requirements (the 4
  templates, acceptance-criteria→task-success-criteria), the Model-C Linking &
  Reference vocab (`Closes`/`Refs`/`Part of`), and the Worktree Rule (incl. the
  branch-mangling correction + remote push refspec).
- Add a clearly delimited "How to merge into AGENTS.md" section: which `AGENTS.md`
  lines to replace (the current "Git Workflow & Pull Requests" block) and which to
  insert, so the user can apply it by hand. State that the merge is a prerequisite for
  `/build`.

### 2. Create the issue templates

- **Task ID**: create-issue-templates
- **Depends On**: none
- **Assigned To**: builder-issue-templates
- **Agent Type**: general-purpose
- **Parallel**: true
- Create `.github/ISSUE_TEMPLATE/feature.md`, `bug.md`, `chore.md`, `epic-plan.md` —
  each uniquely tailored (distinct sections), with proper YAML front-matter (`name`,
  `about`, `labels`).
- `epic-plan.md` links `specs/<feature>/plan.md` and includes a child checklist;
  `feature.md` includes an Acceptance Criteria section noted as the source of Agent
  Task success criteria.
- Create `.github/ISSUE_TEMPLATE/config.yml` (`blank_issues_enabled` + any contact
  links). Must be valid YAML.

### 3. Create the per-type PR templates

- **Task ID**: create-pr-templates
- **Depends On**: none
- **Assigned To**: builder-pr-templates
- **Agent Type**: general-purpose
- **Parallel**: true
- Create the 8 files `.github/PULL_REQUEST_TEMPLATE/{feat,fix,docs,style,refactor,perf,
test,chore}.md`, each tailored to its type (e.g. `feat`: Summary, Changes, Test
  Plan, Breaking changes & migration, Screenshots, Agent Task Manifest, Build Status,
  `Closes #N`; `fix`: Summary, Root cause, Repro, Fix, Regression test, manifest,
  Build Status, `Closes #N`; `docs`: minimal Summary + Changes + `Closes #N`).
- Every template includes the `Closes #N` linked-issue line, the Agent Task Manifest
  block, and the Build Status checklist anchor.

### 4. Enhance /plan-w-team with issue tracking + worktree default

- **Task ID**: enhance-plan-w-team
- **Depends On**: create-git-workflow-doc, create-issue-templates
- **Assigned To**: builder-plan-workflow
- **Agent Type**: general-purpose
- **Parallel**: false
- Edit `.claude/commands/plan-w-team.md`: after grilling sign-off, create one
  Epic/Plan GitHub issue (`gh issue create`) with title + objective; then
  `EnterWorktree` by default; write the plan inside the worktree.
- Add a `## Tracking` step that records, into `plan.md` and `decisions.md`: the issue
  number (or the literal `none — gh unavailable` when no issue was created), the
  intended convention branch name (`<type>/<N>-<slug>`, or `<type>/<slug>` with no
  `#N` when there is no issue), and the worktree path. This recorded issue field is the
  single source of truth `/build` reads — it never re-derives `#N`.
- In the Codex Verification Loop, after reading each round's verdict, post a comment to
  the issue (`gh issue comment #N`) with the verdict + findings + Claude's fixes —
  **only when an issue number exists**.
- Add a graceful-skip clause: if `gh`/remote/auth is unavailable, skip issue creation
  and all issue comments, record `Issue: none — gh unavailable` in `## Tracking` (so
  the branch falls back to `<type>/<slug>`), warn the user, and continue local-only.
  Never block planning on a missing `gh`.

### 5. Enhance /build with single-PR lifecycle tracking

- **Task ID**: enhance-build
- **Depends On**: create-git-workflow-doc, create-pr-templates
- **Assigned To**: builder-build-workflow
- **Agent Type**: general-purpose
- **Parallel**: false
- Edit `.claude/commands/build.md`: read `## Tracking` from the plan; resume the shared
  worktree with `EnterWorktree(path=…)`; implement there.
- On completion **when an issue number is present** in `## Tracking`: push to the
  convention-named remote branch (`git push -u origin HEAD:refs/heads/<type>/<N>-<slug>`)
  and open **one** PR with `gh pr create --template <type>.md`, the emoji title,
  `Closes #N`, and the Agent Task Manifest filled from `TaskList`.
- Maintain a "Build Status" checklist in the PR body and post one `gh pr comment` per
  phase (implementation done → Codex R1 → fixes → Codex R2 → result), each relayed from
  the implementation-review verdict.
- **No-issue / graceful-skip fallback:** if `## Tracking` has no issue number (a
  local-only plan) or `gh`/remote/auth is unavailable, **skip** PR creation, all PR
  comments, the Build-Status updates, and the `Closes #N` line; still implement and run
  the Codex implementation-review locally, leave the branch in the worktree, and print
  the exact `gh pr create` command the user can run to open the PR manually later.
  Never block the build on a missing issue or `gh`.
- Add explicit guards: **never** `git push` to `main` and **never** `gh pr merge`; the
  PR is left open for the user.

### 6. Add Codex relay notes

- **Task ID**: add-codex-relay-notes
- **Depends On**: enhance-plan-w-team, enhance-build
- **Assigned To**: builder-codex-relay
- **Agent Type**: general-purpose
- **Parallel**: false
- Add a short note to `.agents/skills/spec-review/SKILL.md` and
  `.agents/skills/implementation-review/SKILL.md` stating that the orchestrator
  (Claude) relays the per-round verdict to the tracking issue/PR via `gh`, and that the
  skill itself must NOT call `gh` or touch GitHub. Do not change the verdict contract,
  round numbering, or output format.

### 7. Validate everything

- **Task ID**: validate-all
- **Depends On**: create-git-workflow-doc, create-issue-templates, create-pr-templates,
  enhance-plan-w-team, enhance-build, add-codex-relay-notes
- **Assigned To**: validator
- **Agent Type**: general-purpose
- **Parallel**: false
- Run all commands under Validation Commands and verify every Acceptance Criterion.
- Confirm `AGENTS.md` is unchanged in the diff and that no scripts/hooks/CI were added.

## Acceptance Criteria

- `GIT-COMMIT-PR-MESSAGE.md` (repo root) exists and contains: the
  gitmoji 8-type table, `<type>/<issue#>-<slug>` branching, `Refs #N` footer rule, the
  8 PR templates' usage, the 4 issue templates, the `Closes`/`Refs`/`Part of` vocab,
  the worktree rule **including** the remote-refspec correction, and a "How to merge
  into AGENTS.md" section that describes the one-line pointer — replacing the AGENTS.md
  "Git Workflow & Pull Requests" section body with a single reference line — rather than
  a full paste.
- `.github/ISSUE_TEMPLATE/` contains `feature.md`, `bug.md`, `chore.md`,
  `epic-plan.md`, and a valid `config.yml`; the four templates have **distinct**
  tailored sections (not identical skeletons).
- `.github/PULL_REQUEST_TEMPLATE/` contains all 8 per-type files; each is tailored to
  its type and each contains `Closes #`, an Agent Task Manifest block, and a Build
  Status checklist.
- `.claude/commands/plan-w-team.md` references `gh issue create`, `EnterWorktree`, a
  `## Tracking` record, `gh issue comment`, and a graceful-`gh`-skip clause.
- `.claude/commands/build.md` references `EnterWorktree(path`, `gh pr create
--template`, `Closes #`, a Build Status checklist, `gh pr comment`, and explicit
  "never merge/push main" guards; it contains **no** `gh pr merge` and **no**
  `git push origin main`.
- Both Codex skill files contain a relay note and retain their original verdict
  contract (`### Round N — Verdict:` line unchanged).
- `AGENTS.md` is unchanged (not in the diff). No files added under `.githooks/`,
  `.github/workflows/`, or any `package.json`/husky config.

## Validation Commands

Execute these commands to validate the task is complete (run from the repo/worktree
root):

- `ls GIT-COMMIT-PR-MESSAGE.md` — canonical root doc exists.
- `ls .github/ISSUE_TEMPLATE/feature.md .github/ISSUE_TEMPLATE/bug.md .github/ISSUE_TEMPLATE/chore.md .github/ISSUE_TEMPLATE/epic-plan.md .github/ISSUE_TEMPLATE/config.yml`
  — issue templates + config exist.
- `ls .github/PULL_REQUEST_TEMPLATE/{feat,fix,docs,style,refactor,perf,test,chore}.md`
  — all 8 PR templates exist.
- `uv run --with pyyaml python -c "import yaml; yaml.safe_load(open('.github/ISSUE_TEMPLATE/config.yml'))"`
  — `config.yml` is valid YAML.
- `grep -lE 'Closes #' .github/PULL_REQUEST_TEMPLATE/*.md | wc -l` — expect `8`.
- `grep -lE 'Agent Task Manifest' .github/PULL_REQUEST_TEMPLATE/*.md | wc -l` — expect
  `8`.
- `grep -qE 'gh issue create' .claude/commands/plan-w-team.md && grep -qE 'EnterWorktree' .claude/commands/plan-w-team.md && echo OK`
  — plan-w-team wired.
- `grep -qE 'gh pr create --template' .claude/commands/build.md && grep -qE 'EnterWorktree\(path' .claude/commands/build.md && echo OK`
  — build wired.
- `! grep -qE 'gh pr merge|git push +origin +main' .claude/commands/build.md && echo "no-merge-main OK"`
  — build never merges/pushes main.
- `grep -qE '### Round N — Verdict:' .agents/skills/spec-review/SKILL.md .agents/skills/implementation-review/SKILL.md && echo "verdict contract intact"`
  — Codex contract unchanged.
- `git status --porcelain AGENTS.md` — expect **empty** output (AGENTS.md untouched).
- `test ! -d .githooks && test ! -d .github/workflows && test ! -f package.json && echo "no tooling added"`
  — documentation-only enforcement held.

## Notes

- **AGENTS.md is user-applied & unchanged by agents.** Agents must not edit
  `AGENTS.md`; the canonical standard lives in repo-root `GIT-COMMIT-PR-MESSAGE.md`, and the user
  adds a one-line `AGENTS.md` pointer to it **before** running `/build` so builders load
  the conventions. (No settings-level deny exists today; adding one is an optional
  out-of-scope follow-up.)
- **Worktree branch mangling.** `EnterWorktree` names the local branch
  `worktree-<type>+<...>`, not `<type>/<...>`. The convention lives on the **remote**
  branch via `git push -u origin HEAD:refs/heads/<type>/<N>-<slug>`; `#N` is read from
  the recorded `## Tracking` block, never parsed from the local branch.
- **Codex is verdict-only.** Only Claude calls `gh`. If `gh`/remote/auth is missing,
  both workflows skip the GitHub integration, warn, and continue local-only.
- **No-issue fallback (single source of truth).** The `## Tracking` issue field is the
  one place `#N` lives. When it is absent (no `gh`), `/plan-w-team` records `none — gh
unavailable` and the branch falls back to `<type>/<slug>`; `/build` then skips PR
  creation, comments, Build-Status, and `Closes #N`, implements + reviews locally, and
  prints the manual `gh pr create` command. A missing `gh` never blocks planning or
  building.
- **No new libraries** are required for the deliverable. Validation uses
  `uv run --with pyyaml python` (per the repo's `uv` rule) for the YAML check only.
- `gh` is already authenticated (account `SunshinePeace213`, repo public).

## Codex Findings

_Pending Codex review. Codex-owned (the spec-review skill); Claude must not edit this section._

### Round 1 — Verdict: changes-requested

- **The graceful-`gh` skip path leaves `/build` without the required issue number.** Step 4 says to skip issue creation and comments when `gh`/remote/auth is unavailable and continue local-only, but the same step still records an issue number in `## Tracking`, and Step 5 later requires `/build` to push `refs/heads/<type>/<N>-<slug>` and open a PR with `Closes #N`. That contradicts the locked decision that missing `gh` must never block planning/build. Recommend: update Step 4 and Step 5 to specify the fallback tracking state when no issue number exists, and make `/build` skip PR creation/comments or otherwise continue local-only when `## Tracking` has no issue number.

### Round 2 — Verdict: approved

The spec meets the blocking-review bar with no remaining findings this round.
