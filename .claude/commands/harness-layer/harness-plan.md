---
description: Creates a concise engineering implementation plan for any coding OR harness-layer task — grounded in the ai-docs/ knowledge base when the work touches the harness — and saves it to the specs directory
argument-hint: [user prompt] [orchestration prompt]
model: fable
effort: max
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
          command: uv run --script "$CLAUDE_PROJECT_DIR"/.claude/hooks/check_spec_completeness.py
---

# Harness Plan

Grill with the user to lock requirements via the `Grilling Protocol`, then turn those locked requirements (passed in `USER_PROMPT`) into a spec the team can build from — for any coding OR harness-layer task. When the work touches the harness layer, ground every claim in the KB first (see `Domain Knowledge`); otherwise plan straight from the codebase. Write the plan as a four-file spec folder at `PLAN_OUTPUT_DIRECTORY/<name-of-plan>/`, drafted on its own git worktree and pushed to GitHub, then gated by a Codex peer review (`CROSS_REVIEW_SKILL`) before hand-off.

## Variables

USER_PROMPT: $1
ORCHESTRATION_PROMPT: $2 - (Optional) Guidance for team assembly, task structure, and execution strategy
PLAN_OUTPUT_DIRECTORY: `specs/`
SPEC_TEMPLATES: `specs/_templates/` - the four canonical templates to copy and fill
ISSUE_SKELETONS: `specs/_templates/issues/` - agent-facing issue-body skeletons (feature|bug|chore|epic), one per kind
SPEC_FILES: `spec.md`, `tasks.md`, `decisions.md`, `acceptance-criteria.md`
KNOWLEDGE_BASE: `ai-docs/` — cached official docs; catalog in `ai-docs/index.md`, manifest in `ai-docs/sources.yaml`
STALE_AFTER: `30` days — a KB doc older than this is stale
MAX_REVIEW_ROUNDS: `2` - hard cap on Codex cross-review rounds; every round counts, and going over triggers the user gate
CROSS_REVIEW_SKILL: `spec-review` — the Codex-side review skill in `.agents/skills/`
TEAM_MEMBERS: `.claude/agents/team/*.md`
GENERAL_PURPOSE_AGENT: `general-purpose`

## Instructions

- **PLANNING ONLY**: Do NOT build, write code, or deploy agents. Your only output is the four-file spec folder — drafted in a git worktree, then committed and pushed to `origin` (plan docs plus any gap-filled KB docs, never implementation code).
- If no `USER_PROMPT` is provided, stop and ask the user to provide it.
- If `ORCHESTRATION_PROMPT` is provided, use it to guide team composition, task granularity, dependency structure, and parallel/sequential decisions.
- Carefully analyze the user's requirements provided in the USER_PROMPT variable
- Determine the task type (feat|fix|docs|style|refactor|perf|test|chore) and complexity (simple|medium|complex)
- Think deeply (ultrathink) about the best approach to implement the requested functionality or solve the problem
- Understand the codebase directly without subagents — application code and any existing harness patterns under `.claude/` and `.agents/`
- **Ground harness-layer claims.** When the expert layer is active, statements about hooks, frontmatter, subagents, skills, commands, MCP, or model aliases must trace to a KB doc (see `Domain Knowledge`); record what you consulted in decisions.md's `## KB References`.
- Follow the `Output: Spec Folder` section below to create a comprehensive implementation plan
- Generate a descriptive, kebab-case name for the plan based on its main topic
- Create the folder `PLAN_OUTPUT_DIRECTORY/<name-of-plan>/` and write all four `SPEC_FILES` into it, copying each template from `SPEC_TEMPLATES` and replacing every placeholder
- Ensure the spec is detailed enough that another developer could follow it to implement the solution
- Consider edge cases, error handling, and scalability concerns
- Understand your role as the team lead and orchestrate the team accordingly.

## Domain Knowledge

Conditional expert layer. Run it only when the task touches the harness surface — any of `.claude/`, `.agents/`, `.codex/`, `ai-docs/`, the root memory files (CLAUDE.md, AGENTS.md, HARNESS-LAYER.md, GIT-COMMIT-PR-MESSAGE.md), or a domain that has an `ai-docs/index.md` entry. When no signal fires, state that the expert layer is skipped, read no KB docs, and set the review profile to `standard`. When a signal fires, set the profile to `kb-grounded` and:

1. Read `ai-docs/index.md` and open every cached doc relevant to the request's surface (hooks work → hooks.md; a new command → skills-and-commands.md; and so on).
2. If a doc you load is older than `STALE_AFTER`, warn the user and suggest running `/harness-layer:kb` first; continue with the stale copy only if they accept.
3. **Gap-fill:** if the KB has no doc for a topic the plan depends on, fetch and READ it now — WebFetch the official page (or ask the claude-code-guide subagent for the right URL) — but write nothing yet: all writes happen inside the worktree. After entering the worktree, write the mirror under `ai-docs/` (frontmatter `source` + `fetched`, `> **In here:**` bullets, faithful body) AND add its entry to `ai-docs/sources.yaml`, then commit them with the spec.
4. Log every doc you relied on — path + its `fetched` date — in decisions.md under `## KB References` (a section you append; the templates don't carry it).

## Grilling Protocol

Before designing anything, interview the user until every decision needed to build is settled — a shared written understanding, not a guess.

- **Explore first.** Answer from the codebase and (when active) the KB whatever they can answer; ask the user only what they can't.
- **One question at a time, biggest blast radius first.** Order questions by architectural blast radius — answers that would change the architecture come before ones that tune it. Use AskUserQuestion with 2-4 concrete options, your pick first and labeled "(Recommended)". Wait for the answer before the next question.
- **Taste route.** When a decision is one the user would recognize but can't specify (UX, output format, report layout) — or the user asks — present 2-4 concrete alternatives via AskUserQuestion labels and rich descriptions; use option previews only where the running harness supports them (best-effort, never a required contract). A decision that truly needs a rendered comparison is recorded as PROVISIONAL and re-confirmed against the design-directions page (see `Plan Artifacts`) before the spec commit.
- **Coverage ledger.** Track each decision dimension as resolved or open, and keep going until none are open. Cover as applicable: scope & non-goals, users, success criteria & acceptance tests, data model, interfaces/APIs, edge cases & errors, performance & scale, security & authz, observability, rollout/migration, dependencies, testing. When the expert layer is active, also cover the harness dimensions: invocation & trigger control (user-invoked vs auto-triggered vs disable-model-invocation), context budget (what loads always vs on demand), frontmatter (tools, model alias, effort), hook lifecycle & exit-code semantics, artifact choice (skill vs command vs subagent), and distribution (project vs user vs plugin). Mark irrelevant ones N/A.
- **Adaptive depth.** Match complexity — a light pass for chores, a deep pass for complex features. Don't interrogate trivial tasks.
- **Accept-all escape hatch.** Always offer an early exit: if the user picks "Accept all recommendations", close every open item with your recommended answers, record them as assumptions, and move on.
- **Record every decision.** Log each answer — and every deferred "you decide" as an explicit assumption — in `decisions.md`.
- **Final confirmation.** When the ledger is clear, replay all decisions in one AskUserQuestion for sign-off (Approve / revise one / add more). Design only after approval.

## Workflow

IMPORTANT: **PLANNING ONLY** - Do not execute, build, or deploy. Output is a plan document.

1. Preflight - Before anything else, verify required tools. If `gh` is missing or `gh auth status` fails, STOP and ask the user to configure GitHub auth (`gh auth login`). If `command -v codex` fails, STOP and point them to `/codex:setup`. Resolve the issue assignee with `gh api user -q .login`. Continue only when all pass.
2. Analyze Requirements - Parse the USER_PROMPT to understand the core problem and desired outcome
3. Understand Codebase - Without subagents, directly understand the relevant code and any existing harness patterns under `.claude/` and `.agents/`
4. Set Review Profile - Apply the `Domain Knowledge` trigger: if an expert-layer signal fires, load the KB docs and set the profile to `kb-grounded`; otherwise skip the layer and set `standard`.
5. Blindspot Pass - Report the task's top unknown unknowns as inline cards — what / why it matters / proposed resolution — scanned from the codebase and (when active) the KB: ~3 cards for simple tasks, up to ~7 for medium/complex. Unresolved cards seed the grilling ledger first; record every card and its disposition in decisions.md `## Blindspots`.
6. Grill Requirements - Run the `Grilling Protocol`: interview the user one question at a time via AskUserQuestion until the coverage ledger is clear, then get final sign-off. Do NOT design or write files before this completes.
7. Design Solution - Develop technical approach including architecture decisions and implementation strategy, grounded in the KB docs when the expert layer is active
8. Define Team Members - Use `ORCHESTRATION_PROMPT` (if provided) to guide team composition. Identify from `TEAM_MEMBERS` or use `GENERAL_PURPOSE_AGENT`. Document in plan.
9. Define Step by Step Tasks - Use `ORCHESTRATION_PROMPT` (if provided) to guide task granularity and parallel/sequential structure. Write out tasks with IDs, dependencies, assignments, and each task's model and effort per the AGENTS.md tables and selection principle (Quality > time > cost — when torn between tiers, take the higher; one agent, one purpose): `opus` for complex tasks, `sonnet` otherwise; effort `low` mechanical, `medium` default, `high` complex, `xhigh` cross-cutting or harness-core, `max` hardest single tasks. Stamp adversarial or algorithmic tasks (security boundaries, parsers/matchers, architectural redesigns) to Codex `gpt-5.6-sol` as implementer — Claude `opus` reviews all Codex-authored code. Document in plan.
10. Name the Plan - Create a descriptive kebab-case name from the plan's main topic, and pick its change `<type>` (feat/fix/chore/refactor/docs/style/perf/test)
11. Create & Link Issue - File the GitHub issue from the grilling ledger and link its convention branch (see `Worktree & Handoff`). Do this before entering the worktree.
12. Enter Worktree - BEFORE writing any file, call `EnterWorktree(name: "<slug>")` to branch from `origin/main` into `.claude/worktrees/` and draft inside it (see `Worktree & Handoff`)
13. Write the Spec Folder - Create `PLAN_OUTPUT_DIRECTORY/<name-of-plan>/` and fill all four `SPEC_FILES` from `SPEC_TEMPLATES`; author the plan artifacts per `Plan Artifacts`; append `## KB References` to decisions.md when the expert layer is active; write any gap-filled KB docs and their `ai-docs/sources.yaml` entries inside the worktree; record the issue, branch, worktree path, and review profile in spec.md's `## Tracking`
14. Commit & Push - Commit the spec folder (plus gap-filled KB docs) with a `Refs #N` footer, push its branch to `origin`, then post the plan-links comment on the issue (see `Worktree & Handoff`)
15. Cross-Review - Have Codex review the spec with `CROSS_REVIEW_SKILL`, up to `MAX_REVIEW_ROUNDS`, fixing blocking findings each round (see `Codex Cross-Review`). Gate the hand-off on the outcome.
16. Report - Follow the `Report` section to summarize the spec folder and its key components

## Output: Spec Folder

Write the plan as four files under `PLAN_OUTPUT_DIRECTORY/<name-of-plan>/`. Copy each file from `SPEC_TEMPLATES`, then replace every `<placeholder>` with real content. Keep each template's `##` headings exactly as written — a Stop hook checks that every required section is present before the run can end.

```text
specs/<name-of-plan>/
├── spec.md                # what & why: task, objective, non-goals, locked decisions, tracking, review record
├── tasks.md               # how & who: phases, team members, step-by-step tasks
├── decisions.md           # the grilling record (+ ## KB References when the expert layer is active)
├── acceptance-criteria.md # done: testable criteria + validation commands
└── artifacts/             # medium/complex only: blindspot cards, design directions (see Plan Artifacts)
```

When filling them:

- Include the conditional sections (`## Problem Statement` and `## Solution Approach` in spec.md, `## Implementation Phases` in tasks.md) only when task_type is feature or complexity is medium/complex.
- Trace requirements end to end: each requirement in spec.md maps to a task in tasks.md, and each task names the `AC#` from acceptance-criteria.md that it satisfies.
- Codex writes its verdicts under `reviews/`, never into the spec.

## Plan Artifacts

For medium/complex plans, author durable pages inside the worktree under `specs/<name-of-plan>/artifacts/` while writing the spec folder — a blindspot-cards page, plus a design-directions page rendering the alternatives and the chosen one when the taste route fired. Publish each best-effort via the Artifact tool FROM those project-local files; on any availability failure keep the file, note "publish skipped", and continue — publishing never blocks. Re-confirm any PROVISIONAL taste decision with one AskUserQuestion against the design-directions page before the spec commit. The artifacts live inside the spec folder, so the spec commit ships them. Simple plans skip artifacts.

## Worktree & Handoff

Every plan gets a GitHub issue and its own convention branch so `/harness-layer:harness-build` can pick it up and GitHub can track it. Run the steps in order; if any `gh` call fails, STOP and tell the user how to fix it — never proceed degraded or with a placeholder issue.

- **Create the issue.** Pick the skeleton kind from `<type>` — feat→`feature`, fix→`bug`, docs/style/refactor/perf/test/chore→`chore`, `epic` only for a genuine multi-issue initiative. Fill `ISSUE_SKELETONS/<kind>.md` from the grilling ledger (no second interview), write it to a temp file, and create the issue: `gh issue create --title "<emoji> <type>: <plan title>" --body-file <tmp> --label <type> --label priority:P<0-3> --assignee <login>` (gitmoji from the commit table, matching the issue forms) — exactly one type label from {feat,fix,docs,style,refactor,perf,test,chore}, one `priority:P0`–`priority:P3` label, and the login from Preflight. Note the returned issue number `#N`.
- **Link the branch.** `gh issue develop <N> --base main --name <type>/<N>-<slug>` creates the convention branch on the issue.
- **Enter the worktree.** Call `EnterWorktree(name: "<slug>")` — it branches from `origin/main` into `.claude/worktrees/<slug>` and switches in. Write the spec folder there, never on `main`. (`EnterWorktree` creates the local branch `worktree-<slug>`; the convention branch `<type>/<N>-<slug>` is reached only through the explicit push refspec below.)
- **Tracking.** In spec.md's `## Tracking`, record Issue `#N`, Branch `<type>/<N>-<slug>`, the absolute worktree path (`git rev-parse --show-toplevel`), and `Review profile: kb-grounded|standard`.
- **Commit.** Stage the spec folder (`git add specs/<name-of-plan>/`) plus any gap-filled KB docs (`git add ai-docs/`) and make one commit `<emoji> <type>(spec): draft plan for <name-of-plan>` with a `Refs #N` footer — no `Co-Authored-By`.
- **Push.** `git push -u origin HEAD:refs/heads/<type>/<N>-<slug>` lands the convention branch on GitHub (bare `git push` refuses from the local `worktree-<slug>` branch).
- **Plan-links comment.** After the first push, upsert one issue comment whose first line is `<!-- plan-links -->`, its body markdown links to all four spec files as blob URLs on the convention branch. Upsert: list comments with `gh api --paginate repos/{owner}/{repo}/issues/<N>/comments`; if the marker is found, update with `gh api --method PATCH repos/{owner}/{repo}/issues/comments/<comment-id> -F body=@<file>`; else create with `gh issue comment <N> --body-file <file>`. Always write the body to a file first (`gh api` has no `--body-file`).

## Codex Cross-Review

Once the plan is pushed, Codex reviews it as a peer inside the worktree — a hard cap of `MAX_REVIEW_ROUNDS` rounds, every round counted. Before each round, pick the Codex model and reasoning effort from the AGENTS.md Codex table based on the spec's complexity — never hardcoded. Beyond ordinary spec defects, when the expert layer is active it verifies the spec's harness claims against the KB docs, and it always challenges the approach for a simpler, cleaner design. Snapshot the reviewed head SHA before each round. Every push uses the explicit ref spec `git push origin HEAD:refs/heads/<type>/<N>-<slug>` (bare `git push` refuses from the local `worktree-<slug>` branch); check its exit status directly. Loop per round N:

1. **Ask Codex.** `codex exec -C "<worktree root>" -s workspace-write --model <codex-model> -c model_reasoning_effort="<effort>" "Use the spec-review skill to review round <N> of the plan at specs/<name-of-plan>/spec.md; read all four files and (when present) the KB docs listed in decisions.md ## KB References, write your verdict to specs/<name-of-plan>/reviews/codex-spec-review-round-<N>.md, and return only the terse summary."`
2. **Read the verdict from the report file, not stdout:** `grep -E '^### Round [0-9]+ — Verdict: (approved|changes-requested)$' specs/<name-of-plan>/reviews/codex-spec-review-round-<N>.md | tail -1`. A round that writes no verdict is re-run — never treated as approval.
3. **Relay the digest.** Read the `**Issue-comment digest:**` paragraph from the round's report file and post it verbatim as an issue comment whose first line is `<!-- codex-spec-round-N -->` (N = the round). Upsert by marker exactly as the plan-links comment does (paginated `gh api` search → PATCH `-F body=@<file>`, else `gh issue comment --body-file`). Codex never calls `gh` — you relay.
4. **`changes-requested`** → commit the report on its own (`git add specs/<name-of-plan>/reviews/`, one commit with `Refs #N`), fix the blocking findings, commit the fixes on their own (`git add specs/<name-of-plan>/ ai-docs/`, one commit with `Refs #N`), then push both commits together. Go to round N+1.
5. **`approved`** → gate passed; the approval round's report commit is the approved head. Commit the report (`git add specs/<name-of-plan>/reviews/`, one commit with `Refs #N`) and push. Set spec.md `Status: Approved`, record any advisories, and record the outcome (below).

**Advisories never spawn extra rounds.** Better-approach and other non-blocking suggestions are recorded as a follow-ups checklist in decisions.md to feed a future plan — they are not fixed in this run and never trigger another review round.

**Over `MAX_REVIEW_ROUNDS` and still `changes-requested`** (round 2's verdict is `changes-requested`) → STOP and present ONE AskUserQuestion that explains why a further round would be needed and what it would do, with these options and their exit statuses:

- **Run one more delta round** — Codex re-reviews the fix delta as a new round.
- **`accepted-with-unverified-fixes`** — allowed ONLY when the remaining blockers are non-severe and mechanically verifiable AND the plan's validation commands pass after the fixes; the user must pick it explicitly. Record it on the issue.
- **`needs-human`** — add the `status:needs-human` label (`gh issue edit <N> --add-label status:needs-human`) and post an issue comment naming the blockers.

The user's selection is final. Record the final outcome (`approved` at round N | `accepted-with-unverified-fixes` | `needs-human`) in spec.md's `## Codex Verification`. On `needs-human`, do NOT run the hand-off Report; when a later round reaches `approved`, remove the label (`gh issue edit <N> --remove-label status:needs-human`).

## Report

After creating and saving the spec folder, provide a concise report with the following format:

```text
✅ Spec Folder Created

Folder: PLAN_OUTPUT_DIRECTORY/<name-of-plan>/ (spec.md, tasks.md, decisions.md, acceptance-criteria.md)
Issue: #N <url>
Branch: <type>/<N>-<slug> — pushed to origin
Worktree: <absolute worktree path>
Review profile: <kb-grounded | standard>
Codex Review: <approved at round N | accepted-with-unverified-fixes | needs-human>
KB Grounding: <N docs consulted, M gap-filled — or "none (standard profile)">
Artifacts: <committed paths + published URLs, or "none — simple plan">
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
/harness-layer:harness-build <name-of-plan>
```
