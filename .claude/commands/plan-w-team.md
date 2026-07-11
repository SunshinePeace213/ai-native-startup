---
description: Creates a concise engineering implementation plan based on user requirements and saves it to specs directory
argument-hint: [user prompt] [orchestration prompt]
model: opus
disallowed-tools: Task, EnterPlanMode
hooks:
  PostToolUse:
    - matcher: "Edit|Write"
      hooks:
        - type: command
          command: "jq -r '.tool_input.file_path' | xargs bunx prettier --write"
  Stop:
    - hooks:
        - type: command
          command: '"$CLAUDE_PROJECT_DIR"/.claude/hooks/check-spec-completeness.sh'
---

# Plan With Team

Grill with the user to lock requirements via the `Grilling Protocol`, then turn those locked requirements (passed in `USER_PROMPT`) into a spec the team can build from. Analyze the request, think through the approach, and write the plan as a four-file spec folder at `PLAN_OUTPUT_DIRECTORY/<name-of-plan>/`, drafted on its own git worktree and pushed to GitHub so the work stays trackable, then gated by a Codex peer review before hand-off. Follow the `Instructions` and work through the `Workflow` to create the plan.

## Variables

USER_PROMPT: $1
ORCHESTRATION_PROMPT: $2 - (Optional) Guidance for team assembly, task structure, and execution strategy
PLAN_OUTPUT_DIRECTORY: `specs/`
SPEC_TEMPLATES: `specs/_templates/` - the four canonical templates to copy and fill
ISSUE_SKELETONS: `specs/_templates/issues/` - agent-facing issue-body skeletons (feature|bug|chore|epic), one per kind
SPEC_FILES: `spec.md`, `tasks.md`, `decisions.md`, `acceptance-criteria.md`
MAX_REVIEW_ROUNDS: `2` - max Codex cross-review rounds before flagging the spec for a human
TEAM_MEMBERS: `.claude/agents/team/*.md`
GENERAL_PURPOSE_AGENT: `general-purpose`

## Instructions

- **PLANNING ONLY**: Do NOT build, write code, or deploy agents. Your only output is the four-file spec folder — drafted in a git worktree, then committed and pushed to `origin` (plan docs only, never implementation code).
- If no `USER_PROMPT` is provided, stop and ask the user to provide it.
- If `ORCHESTRATION_PROMPT` is provided, use it to guide team composition, task granularity, dependency structure, and parallel/sequential decisions.
- Carefully analyze the user's requirements provided in the USER_PROMPT variable
- Determine the task type (feat|fix|docs|style|refactor|perf|test|chore) and complexity (simple|medium|complex)
- Think deeply (ultrathink) about the best approach to implement the requested functionality or solve the problem
- Understand the codebase directly without subagents — existing patterns and architecture
- Follow the `Output: Spec Folder` section below to create a comprehensive implementation plan
- Include all required sections and conditional sections based on task type and complexity
- Generate a descriptive, kebab-case name for the plan based on its main topic
- Create the folder `PLAN_OUTPUT_DIRECTORY/<name-of-plan>/` and write all four `SPEC_FILES` into it, copying each template from `SPEC_TEMPLATES` and replacing every placeholder
- Ensure the spec is detailed enough that another developer could follow it to implement the solution
- Include code examples or pseudo-code where appropriate to clarify complex concepts
- Consider edge cases, error handling, and scalability concerns
- Understand your role as the team lead and orchestrate the team accordingly.

## Grilling Protocol

Before designing anything, interview the user until every decision needed to build is settled — a shared written understanding, not a guess.

- **Explore first.** Answer from the codebase whatever the code can answer; ask the user only what it can't.
- **One question at a time.** Use AskUserQuestion with 2-4 concrete options, your pick first and labeled "(Recommended)". Wait for the answer before the next question.
- **Coverage ledger.** Track each decision dimension as resolved or open, and keep going until none are open. Cover as applicable: scope & non-goals, users, success criteria & acceptance tests, data model, interfaces/APIs, edge cases & errors, performance & scale, security & authz, observability, rollout/migration, dependencies, testing. Mark irrelevant ones N/A.
- **Adaptive depth.** Match complexity — a light pass for chores, a deep pass for complex features. Don't interrogate trivial tasks.
- **Accept-all escape hatch.** Always offer an early exit: if the user picks "Accept all recommendations", close every open item with your recommended answers, record them as assumptions, and move on.
- **Record every decision.** Log each answer — and every deferred "you decide" as an explicit assumption — in `decisions.md`.
- **Final confirmation.** When the ledger is clear, replay all decisions in one AskUserQuestion for sign-off (Approve / revise one / add more). Design only after approval.

## Workflow

IMPORTANT: **PLANNING ONLY** - Do not execute, build, or deploy. Output is a plan document.

1. Preflight - Before anything else, verify required tools. If `gh` is missing or `gh auth status` fails, STOP and ask the user to configure GitHub auth (`gh auth login`). If `command -v codex` fails, STOP and point them to `/codex:setup`. Resolve the issue assignee with `gh api user -q .login`. Continue only when all pass.
2. Analyze Requirements - Parse the USER_PROMPT to understand the core problem and desired outcome
3. Understand Codebase - Without subagents, directly understand existing patterns, architecture, and relevant files
4. Grill Requirements - Run the `Grilling Protocol`: interview the user one question at a time via AskUserQuestion until the coverage ledger is clear, then get final sign-off. Do NOT design or write files before this completes.
5. Design Solution - Develop technical approach including architecture decisions and implementation strategy
6. Define Team Members - Use `ORCHESTRATION_PROMPT` (if provided) to guide team composition. Identify from `TEAM_MEMBERS` or use `GENERAL_PURPOSE_AGENT`. Document in plan.
7. Define Step by Step Tasks - Use `ORCHESTRATION_PROMPT` (if provided) to guide task granularity and parallel/sequential structure. Write out tasks with IDs, dependencies, assignments. Document in plan.
8. Name the Plan - Create a descriptive kebab-case name from the plan's main topic, and pick its change `<type>` (feat/fix/chore/refactor/docs/style/perf/test)
9. Create & Link Issue - File the GitHub issue from the grilling ledger and link its convention branch (see `Worktree & Handoff`). Do this before entering the worktree.
10. Enter Worktree - BEFORE writing any file, call `EnterWorktree(name: "<type>/<N>-<slug>")` to branch from `origin/main` into `.claude/worktrees/` and draft inside it (see `Worktree & Handoff`)
11. Write the Spec Folder - Create `PLAN_OUTPUT_DIRECTORY/<name-of-plan>/` and fill all four `SPEC_FILES` from `SPEC_TEMPLATES`; record the issue, branch, and worktree path in spec.md's `## Tracking`
12. Commit & Push - Commit the spec folder with a `Refs #N` footer, push its branch to `origin`, then post the plan-links comment on the issue (see `Worktree & Handoff`)
13. Cross-Review - Have Codex review the spec, up to `MAX_REVIEW_ROUNDS`, fixing blocking findings each round (see `Codex Cross-Review`). Gate the hand-off on the outcome.
14. Report - Follow the `Report` section to summarize the spec folder and its key components

## Output: Spec Folder

Write the plan as four files under `PLAN_OUTPUT_DIRECTORY/<name-of-plan>/`. Copy each file from `SPEC_TEMPLATES`, then replace every `<placeholder>` with real content. Keep each template's `##` headings exactly as written — a Stop hook checks that every required section is present before the run can end.

```
specs/<name-of-plan>/
├── spec.md                # what & why: task, objective, non-goals, locked decisions, tracking, review record
├── tasks.md               # how & who: phases, team members, step-by-step tasks
├── decisions.md           # the grilling record: resolved decisions, assumptions, out-of-scope
└── acceptance-criteria.md # done: testable criteria + validation commands
```

When filling them:

- Include the conditional sections (`## Problem Statement` and `## Solution Approach` in spec.md, `## Implementation Phases` in tasks.md) only when task_type is feature or complexity is medium/complex.
- Trace requirements end to end: each requirement in spec.md maps to a task in tasks.md, and each task names the `AC#` from acceptance-criteria.md that it satisfies.
- Leave spec.md's `## Codex Findings` untouched — it is Codex-owned.

## Worktree & Handoff

Every plan gets a GitHub issue and its own convention branch so `/build` can pick it up and GitHub can track it. Run the steps in order; if any `gh` call fails, STOP and tell the user how to fix it — never proceed degraded or with a placeholder issue.

- **Create the issue.** Pick the skeleton kind from `<type>` — feat→`feature`, fix→`bug`, docs/style/refactor/perf/test/chore→`chore`, `epic` only for a genuine multi-issue initiative. Fill `ISSUE_SKELETONS/<kind>.md` from the grilling ledger (no second interview), write it to a temp file, and create the issue: `gh issue create --title "<emoji> <type>: <plan title>" --body-file <tmp> --label <type> --label priority:P<0-3> --assignee <login>` (gitmoji from the commit table, matching the issue forms) — exactly one type label from {feat,fix,docs,style,refactor,perf,test,chore}, one `priority:P0`–`priority:P3` label, and the login from Preflight. Note the returned issue number `#N`.
- **Link the branch.** `gh issue develop <N> --base main --name <type>/<N>-<slug>` creates the convention branch on the issue.
- **Enter the worktree.** Call `EnterWorktree(name: "<type>/<N>-<slug>")` — it branches from `origin/main` into `.claude/worktrees/` and switches in. Write the spec folder there, never on `main`. (`EnterWorktree` mangles the local branch name; the convention name is what you push below.)
- **Tracking.** In spec.md's `## Tracking`, record Issue `#N`, Branch `<type>/<N>-<slug>`, and the absolute worktree path (`git rev-parse --show-toplevel`).
- **Commit.** Stage only the spec folder (`git add specs/<name-of-plan>/`) and make one commit `<emoji> <type>(spec): draft plan for <name-of-plan>` with a `Refs #N` footer — no `Co-Authored-By`.
- **Push.** `git push -u origin HEAD:refs/heads/<type>/<N>-<slug>` lands the convention branch on GitHub.
- **Plan-links comment.** After the first push, upsert one issue comment whose first line is `<!-- plan-links -->`, its body markdown links to all four spec files as blob URLs on the convention branch. Upsert: list comments with `gh api --paginate repos/{owner}/{repo}/issues/<N>/comments`; if the marker is found, update with `gh api --method PATCH repos/{owner}/{repo}/issues/comments/<comment-id> -F body=@<file>`; else create with `gh issue comment <N> --body-file <file>`. Always write the body to a file first (`gh api` has no `--body-file`).

## Codex Cross-Review

Once the plan is pushed, Codex reviews it as a peer — up to `MAX_REVIEW_ROUNDS` — inside the worktree. It catches spec defects AND challenges the approach for a simpler, cleaner design. Every round ends with exactly one commit+push checkpoint on the convention branch (with a `Refs #N` footer) — never amend a pushed checkpoint. Loop per round N:

1. **Ask Codex.** `codex exec -C "<worktree root>" -s workspace-write "Use the spec-review skill to review round <N> of the plan at specs/<name-of-plan>/spec.md; read all four files, append your verdict inside spec.md's ## Codex Findings, and return only the terse summary."`
2. **Read the verdict from the file, not stdout:** `grep -E '^### Round [0-9]+ — Verdict: (approved|changes-requested)$' specs/<name-of-plan>/spec.md | tail -1`. A round that writes no verdict is re-run — never treated as approval.
3. **Relay the digest.** Read the `**Issue-comment digest:**` paragraph at the end of the round's verdict block and post it verbatim as an issue comment whose first line is `<!-- codex-spec-round-N -->` (N = the round). Upsert by marker exactly as the plan-links comment does (paginated `gh api` search → PATCH `-F body=@<file>`, else `gh issue comment --body-file`). Codex never calls `gh` — you relay.
4. **`changes-requested`** → fix the blocking findings, then checkpoint: `git add specs/<name-of-plan>/`, one commit with `Refs #N`, push. Go to round N+1.
5. **`approved`** → gate passed. Set spec.md `Status: Approved`, then checkpoint the approval round (one commit with `Refs #N`, push). Handle the recommendations below.

**Better-approach recommendations are advisory** — they never block approval. Once approved, for each one Codex left, analyze it, explain to the user whether it is genuinely better, and ask via AskUserQuestion whether to apply. Applying a recommendation is a NEW commit and triggers one more review round — approval never covers unreviewed changes. Advice rounds never count against `MAX_REVIEW_ROUNDS` (that cap governs `changes-requested` loops), so an approval at the cap still has a valid re-review path.

**Over `MAX_REVIEW_ROUNDS` and still `changes-requested`** → STOP. Set spec.md `Status: Needs Human Review`, add the `status:needs-human` label to the issue (`gh issue edit <N> --add-label status:needs-human`), record the outstanding findings in `## Codex Verification`, commit and push, and tell the user to resolve them before the plan continues. Do NOT run the hand-off Report. When a later round reaches `approved` after this escalation, remove the label (`gh issue edit <N> --remove-label status:needs-human`).

Record the final outcome (approved at round N | needs human review after N rounds) in spec.md's `## Codex Verification`.

## Report

After creating and saving the spec folder, provide a concise report with the following format:

```
✅ Spec Folder Created

Folder: PLAN_OUTPUT_DIRECTORY/<name-of-plan>/ (spec.md, tasks.md, decisions.md, acceptance-criteria.md)
Issue: #N <url>
Branch: <type>/<N>-<slug> — pushed to origin
Worktree: <absolute worktree path>
Codex Review: <approved at round N>
Topic: <brief description of what the plan covers>
Key Components:
- <main component 1>
- <main component 2>
- <main component 3>

Team Task List:
- <list of tasks, and owner (concise)>

Team members:
- <list of team members and their roles (concise)>

When you're ready, execute the plan in a new agent by running:
/build <name-of-plan>
```
