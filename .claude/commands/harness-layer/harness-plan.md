---
description: Drafts a concise engineering implementation plan for any coding OR harness-layer task — grounded in the ai-docs/ knowledge base when the work touches the harness — and saves it to the specs directory. Never interviews; /harness-layer:harness-interview locks decisions first
argument-hint: [finalized prompt] [orchestration prompt]
model: fable
effort: max
disallowed-tools: Task, EnterPlanMode, AskUserQuestion
hooks:
  Stop:
    - hooks:
        - type: command
          command: uv run --script "$CLAUDE_PROJECT_DIR"/.claude/hooks/check_spec_completeness.py
---

# Harness Plan

Draft the spec directly — no interviewing. Turn `USER_PROMPT` (ideally the finalized prompt from `/harness-layer:harness-interview`) into a four-file spec folder the team can build from — for any coding OR harness-layer task. When the work touches the harness layer, ground every claim in the KB first (see `Domain Knowledge`); otherwise plan straight from the codebase. Draft at `PLAN_OUTPUT_DIRECTORY/<name-of-plan>/` on the chain's worktree (or a fresh one), push to GitHub, gate with a Codex peer review (`CROSS_REVIEW_SKILL`), then publish the implementation-plan page for the user's async review.

## Variables

USER_PROMPT: $1
ORCHESTRATION_PROMPT: $2 - (Optional) Guidance for team assembly, task structure, and execution strategy
PLAN_OUTPUT_DIRECTORY: `specs/`
SPEC_TEMPLATES: `specs/_templates/` - the four canonical templates to copy and fill
ISSUE_SKELETONS: `specs/_templates/issues/` - agent-facing issue-body skeletons (feature|bug|chore|epic), one per kind
SPEC_FILES: `spec.md`, `tasks.md`, `decisions.md`, `acceptance-criteria.md`
KNOWLEDGE_BASE: `ai-docs/` — cached official docs; catalog in `ai-docs/index.md`, manifest in `ai-docs/sources.yaml`
STALE_AFTER: `30` days — a KB doc older than this is stale
MAX_REVIEW_ROUNDS: `2` - hard cap on NEW Codex rounds per review cycle; over the cap auto-resolves to needs-human
CODEX_TIMEOUT: `900` seconds — every `codex exec` runs under `timeout --kill-after=30s`
CROSS_REVIEW_SKILL: `spec-review` — the Codex-side review skill in `.agents/skills/`
GENERAL_PURPOSE_AGENT: `general-purpose`

## Instructions

- **PLANNING ONLY**: Do NOT build, write code, or deploy agents. Your only output is the four-file spec folder plus its artifacts — drafted in the worktree, then committed and pushed to `origin` (plan docs plus any gap-filled KB docs, never implementation code).
- **NEVER ASK THE USER.** AskUserQuestion is disallowed. Every open point is either answered by the input (see `Input Gate`) or resolved with your recommended choice and recorded in decisions.md `## Assumptions`. Draft anyway; never stall. The only stops: missing `USER_PROMPT`, failed Preflight, or input so ambiguous no defensible approach exists — then stop and recommend `/harness-layer:harness-interview "<USER_PROMPT>"`.
- If no `USER_PROMPT` is provided, stop and ask the user to provide it.
- If `ORCHESTRATION_PROMPT` is provided, use it to guide team composition, task granularity, dependency structure, and parallel/sequential decisions.
- Carefully analyze the user's requirements provided in the USER_PROMPT variable
- Determine the task type (feat|fix|docs|style|refactor|perf|test|chore) and complexity (simple|medium|complex)
- Think deeply (ultrathink) about the best approach to implement the requested functionality or solve the problem
- Understand the codebase directly without subagents — application code and any existing harness patterns under `.claude/` and `.agents/` — the one exception is the `claude-code-guide` subagent the expert layer uses to cross-check harness claims
- **Ground harness-layer claims.** When the expert layer is active, statements about hooks, frontmatter, subagents, skills, commands, MCP, or model aliases must trace to a KB doc (see `Domain Knowledge`); record what you consulted in decisions.md's `## KB References`.
- Follow the `Output: Spec Folder` section below to create a comprehensive implementation plan
- Name the plan: reuse the chain's `<slug>` when the worktree pre-exists (rename with `git mv` only if actively wrong); otherwise generate a descriptive kebab-case name from the plan's main topic
- Ensure the spec is detailed enough that another developer could follow it to implement the solution
- Consider edge cases, error handling, and scalability concerns

## Domain Knowledge

Conditional expert layer. Run it only when the task touches the harness surface — any of `.claude/`, `.agents/`, `.codex/`, `ai-docs/`, the memory files (CLAUDE.md, AGENTS.md), or a domain that has an `ai-docs/index.md` entry. When no signal fires, state that the expert layer is skipped, read no KB docs, and set the review profile to `standard`. When a signal fires, set the profile to `kb-grounded` and run collect → cross-check → reconcile:

1. **Collect.** Read `ai-docs/index.md` and open every cached doc relevant to the request's surface (hooks work → hooks.md; a new command → skills-and-commands.md; and so on). If a doc you load is older than `STALE_AFTER`, continue with the stale copy, note it in decisions.md `## KB References`, and flag it in the Report with a `/harness-layer:kb` suggestion.
2. **Cross-check.** Spawn the built-in `claude-code-guide` subagent with the specific harness claims/topics the plan depends on, asking it to verify them against current official behavior.
3. **Reconcile.** Where both sources agree, continue. Where they conflict on a claim, WebFetch the official page — the fresh fetch wins; refresh that KB mirror inside the worktree (same mechanics as gap-fill: frontmatter `source` + `fetched`, `> **In here:**` bullets, faithful body, `ai-docs/sources.yaml` entry) and log the conflict + resolution in decisions.md `## KB References`. If the page is unreachable, prefer the source with the newer verifiable date and mark the claim unverified in the spec.
4. **Gap-fill:** if the KB has no doc for a topic the plan depends on, fetch and READ it now — WebFetch the official page (or ask the claude-code-guide subagent for the right URL) — then write the mirror under `ai-docs/` inside the worktree (frontmatter `source` + `fetched`, `> **In here:**` bullets, faithful body) AND add its entry to `ai-docs/sources.yaml`, committed with the spec.
5. Log every doc you relied on — path + its `fetched` date — in decisions.md under `## KB References` (a section you append; the templates don't carry it).

## Input Gate

No interviewing — every decision was locked upstream or becomes an assumption.

- **Ledger.** When `specs/<slug>/discovery/decisions-draft.md` exists in the worktree, transcribe it into decisions.md — resolved decisions stay resolved, never re-litigated. Reference any discovery pages from the spec; never copy them.
- **Gaps.** Any decision still open after the ledger: pick your recommended answer and record it in decisions.md `## Assumptions` with what would invalidate it.
- **Revision.** When the worktree already holds `specs/<slug>/spec.md`, this run is a revision (a tweak prompt from the implementation-plan page, or blockers resolved after needs-human) — see `Revision Mode`.

## Workflow

IMPORTANT: **PLANNING ONLY** - Do not execute, build, or deploy. Output is a plan document.

1. Preflight - Before anything else, verify required tools. If `gh` is missing or `gh auth status` fails, STOP and ask the user to configure GitHub auth (`gh auth login`). If `command -v codex` fails, STOP and point them to `/codex:setup`. Resolve the issue assignee with `gh api user -q .login`. Continue only when all pass.
2. Analyze Requirements - Parse the USER_PROMPT to understand the core problem and desired outcome
3. Enter Worktree - `Worktree:` line in the prompt → `EnterWorktree(path: ...)`; otherwise `EnterWorktree(name: "<slug>")` (see `Worktree & Handoff`). An existing `specs/<slug>/spec.md` switches the run to `Revision Mode`.
4. Run the Input Gate - Ingest the discovery ledger; convert remaining gaps to Assumptions
5. Understand Codebase - Without subagents (except the `claude-code-guide` subagent the expert layer uses to cross-check harness claims), directly understand the relevant code and any existing harness patterns under `.claude/` and `.agents/`
6. Set Review Profile - Apply the `Domain Knowledge` trigger: if an expert-layer signal fires, load the KB docs and set the profile to `kb-grounded`; otherwise skip the layer and set `standard`.
7. Design Solution - Develop technical approach including architecture decisions and implementation strategy, grounded in the KB docs when the expert layer is active
8. Define Team Members - Use `ORCHESTRATION_PROMPT` (if provided) to guide team composition. Draw team members from the available agent types, defaulting to `GENERAL_PURPOSE_AGENT`. Document in plan.
9. Define Step by Step Tasks - Use `ORCHESTRATION_PROMPT` (if provided) to guide task granularity and parallel/sequential structure. Write out tasks with IDs, dependencies, assignments, and each task's model and effort stamped per the model-selection rule (it loads every session). Document in plan.
10. Name the Plan - Reuse the chain slug (or name it now), and pick its change `<type>` (feat/fix/chore/refactor/docs/style/perf/test)
11. Create & Link Issue - First cycle only: file the GitHub issue from the ledger + Assumptions and link its convention branch (see `Worktree & Handoff`)
12. Write the Spec Folder - Create `PLAN_OUTPUT_DIRECTORY/<name-of-plan>/` and fill all four `SPEC_FILES` from `SPEC_TEMPLATES`; append `## KB References` to decisions.md when the expert layer is active; write any gap-filled KB docs and their `ai-docs/sources.yaml` entries; record the issue, branch, worktree path, and review profile in spec.md's `## Tracking`
13. Commit & Push - Commit the spec folder (plus gap-filled KB docs) with a `Refs #N` footer, push its branch to `origin`, then post the plan-links comment on the issue (see `Worktree & Handoff`)
14. Cross-Review - Have Codex review the spec with `CROSS_REVIEW_SKILL`, at most `MAX_REVIEW_ROUNDS` new rounds this cycle, fixing blocking findings each round (see `Codex Cross-Review`)
15. Implementation-Plan Page - After the gate settles, author and publish the page per `Plan Artifacts`, commit and push it
16. Report - Follow the `Report` section to summarize the spec folder and its key components

## Output: Spec Folder

Write the plan as four files under `PLAN_OUTPUT_DIRECTORY/<name-of-plan>/`. Copy each file from `SPEC_TEMPLATES`, then replace every `<placeholder>` with real content. Keep each template's `##` headings exactly as written — a Stop hook checks that every required section is present before the run can end.

```text
specs/<name-of-plan>/
├── discovery/             # committed by the pre-plan passes (pages + decisions-draft.md); reference, never copy
├── spec.md                # what & why: task, objective, non-goals, locked decisions, tracking, review record
├── tasks.md               # how & who: phases, team members, step-by-step tasks
├── decisions.md           # the interview record (+ ## KB References when the expert layer is active)
├── acceptance-criteria.md # done: testable criteria + validation commands
├── artifacts/             # implementation-plan page (+ reference map when porting semantics)
└── reviews/               # Codex verdicts
```

When filling them:

- Include the conditional sections (`## Problem Statement` and `## Solution Approach` in spec.md, `## Implementation Phases` in tasks.md) only when task_type is feature or complexity is medium/complex.
- Trace requirements end to end: each requirement in spec.md maps to a task in tasks.md, and each task names the `AC#` from acceptance-criteria.md that it satisfies.
- Volatile-decisions-first: within spec.md's existing `##` headings (do not rename or reorder them), lead with the decisions most likely to change — data model, type/interface signatures, anything user-facing — so the highest-churn choices sit up front.
- Codex writes its verdicts under `reviews/`, never into the spec.

## Plan Artifacts

After the Codex gate settles, author the **Implementation plan** page from the final spec state into `specs/<name-of-plan>/artifacts/`, publish best-effort, and commit + push it (`Refs #N`). When the plan ports semantics from a reference implementation named in the prompt, also author the **Reference map** page. Crafting and publish rules live in `.claude/rules/harness-layer/artifacts.md` (it also auto-loads on `specs/**`); publishing never blocks. Simple plans skip artifacts.

## Worktree & Handoff

Every plan gets a GitHub issue and its convention branch before anything is pushed, so `/harness-layer:harness-build` can pick it up and GitHub can track it. Run the steps in order; if any `gh` call fails, STOP and tell the user how to fix it — never proceed degraded or with a placeholder issue.

- **Enter the worktree.** The discovery chain usually created it — `EnterWorktree(path: ".claude/worktrees/<slug>")`; without one, `EnterWorktree(name: "<slug>")` branches from `origin/main` into `.claude/worktrees/<slug>`. Write the spec folder there, never on `main`. Discovery commits already on the branch ride along with the first push.
- **Create the issue** (first cycle only). Pick the skeleton kind from `<type>` — feat→`feature`, fix→`bug`, docs/style/refactor/perf/test/chore→`chore`, `epic` only for a genuine multi-issue initiative. Fill `ISSUE_SKELETONS/<kind>.md` from the interview ledger and Assumptions, write it to a temp file, and create the issue: `gh issue create --title "<emoji> <type>: <plan title>" --body-file <tmp> --label <type> --label priority:P<0-3> --assignee <login>` (gitmoji from the commit table, matching the issue forms) — exactly one type label from {feat,fix,docs,style,refactor,perf,test,chore}, one `priority:P0`–`priority:P3` label, and the login from Preflight. Note the returned issue number `#N`.
- **Link the branch.** `gh issue develop <N> --base main --name <type>/<N>-<slug>` creates the convention branch on the issue.
- **Tracking.** In spec.md's `## Tracking`, record Issue `#N`, Branch `<type>/<N>-<slug>`, the absolute worktree path (`git rev-parse --show-toplevel`), and `Review profile: kb-grounded|standard`.
- **Commit.** Stage the spec folder (`git add specs/<name-of-plan>/`) plus any gap-filled KB docs (`git add ai-docs/`) and make one commit `<emoji> <type>(spec): draft plan for <name-of-plan>` with a `Refs #N` footer.
- **Push.** `git push -u origin HEAD:refs/heads/<type>/<N>-<slug>` lands the convention branch on GitHub (bare `git push` refuses from the local `worktree-<slug>` branch).
- **Plan-links comment.** After the first push, upsert one issue comment whose first line is `<!-- plan-links -->`, its body markdown links to all four spec files as blob URLs on the convention branch. Upsert: list comments with `gh api --paginate repos/{owner}/{repo}/issues/<N>/comments`; if the marker is found, update with `gh api --method PATCH repos/{owner}/{repo}/issues/comments/<comment-id> -F body=@<file>`; else create with `gh issue comment <N> --body-file <file>`. Always write the body to a file first (`gh api` has no `--body-file`).

## Revision Mode

When the worktree already holds `specs/<slug>/spec.md`:

- Apply the input (tweak prompt or resolved blockers) to the spec files; log what changed and why in decisions.md. Keep issue `#N` from `## Tracking` — no new issue, no new branch, no re-litigating resolved decisions.
- Commit with `Refs #N` and push with the same refspec.
- Run a fresh Codex cycle: round numbers continue from the last report (a cycle allows at most `MAX_REVIEW_ROUNDS` new rounds).
- Re-author and republish the implementation-plan page from the revised spec.
- When the cycle reaches `approved` after a prior needs-human, remove the label: `gh issue edit <N> --remove-label status:needs-human`.

## Codex Cross-Review

Once the plan is pushed, Codex reviews it as a peer inside the worktree — at most `MAX_REVIEW_ROUNDS` new rounds this cycle, round numbers continuing across cycles. Before each round, pick the Codex model and reasoning effort per the model-selection rule based on the spec's complexity. Beyond ordinary spec defects, when the expert layer is active it verifies the spec's harness claims against the KB docs, and it always challenges the approach for a simpler, cleaner design. Snapshot the reviewed head SHA before each round; check every push's exit status directly. Loop per round N:

1. **Ask Codex — under a hard timeout, in the background.** Run via Bash with `run_in_background: true` and continue when the exit notification arrives: `timeout --kill-after=30s <CODEX_TIMEOUT> codex exec -C "<worktree root>" -s workspace-write --model <codex-model> -c model_reasoning_effort="<effort>" "Use the spec-review skill to review round <N> of the plan at specs/<name-of-plan>/spec.md; read all four files and (when present) the KB docs listed in decisions.md ## KB References, write your verdict to specs/<name-of-plan>/reviews/codex-spec-review-round-<N>.md, and return only the terse summary."`
2. **Read the verdict from the report file, not stdout:** `grep -E '^### Round [0-9]+ — Verdict: (approved|changes-requested)$' specs/<name-of-plan>/reviews/codex-spec-review-round-<N>.md | tail -1`. Timed out, or exited with no verdict written → re-run the same round exactly once; a second consecutive failure → take the `Needs-human exit` with reason `codex-unavailable`.
3. **Relay the digest.** Read the `**Issue-comment digest:**` paragraph from the round's report file and post it verbatim as an issue comment whose first line is `<!-- codex-spec-round-N -->` (N = the round). Upsert by marker exactly as the plan-links comment does (paginated `gh api` search → PATCH `-F body=@<file>`, else `gh issue comment --body-file`). Codex never calls `gh` — you relay.
4. **`changes-requested`** → commit the report on its own (`git add specs/<name-of-plan>/reviews/`, one commit with `Refs #N`), fix the blocking findings, commit the fixes on their own (`git add specs/<name-of-plan>/ ai-docs/`, one commit with `Refs #N`), then push both commits together. Rounds left in the cycle → round N+1; otherwise take the `Needs-human exit`.
5. **`approved`** → gate passed; commit the report (`git add specs/<name-of-plan>/reviews/`, one commit with `Refs #N`) and push. Set spec.md `Status: Approved`, record any advisories, and record the outcome in spec.md's `## Codex Verification`.

**Advisories never spawn extra rounds.** Better-approach and other non-blocking suggestions are recorded as a follow-ups checklist in decisions.md to feed a future plan — they are not fixed in this run and never trigger another review round.

**Needs-human exit** (cycle cap reached still `changes-requested`, or Codex unavailable) — no user gate; resolve automatically:

- `gh issue edit <N> --add-label status:needs-human`, and post an issue comment naming the blockers (or the Codex failure).
- Record `needs-human` and the reason (`blockers` | `codex-unavailable`) in spec.md's `## Codex Verification`; leave `Status: Drafted for Review`.
- Still author the implementation-plan page and run the `Report`, ending it with the ready-made recovery prompt: `/harness-layer:harness-interview "Resolve these review blockers: <one line per blocker>. Worktree: .claude/worktrees/<slug>"` — the interview locks the blockers, a plan re-run enters `Revision Mode`, and an `approved` cycle removes the label.

## Report

After creating and saving the spec folder, provide a concise report with the following format:

```text
✅ Spec Folder Created

Folder: PLAN_OUTPUT_DIRECTORY/<name-of-plan>/ (spec.md, tasks.md, decisions.md, acceptance-criteria.md)
Issue: #N <url>
Branch: <type>/<N>-<slug> — pushed to origin
Worktree: <absolute worktree path>
Review profile: <kb-grounded | standard>
Codex Review: <approved at round N | needs-human (blockers | codex-unavailable)>
KB Grounding: <N docs consulted, M gap-filled — or "none (standard profile)">
Discovery: <passes present under discovery/, or "none">
Assumptions: <count recorded in decisions.md, or "none">
Page: <implementation-plan page URL + committed path, or "none — simple plan">
Topic: <brief description of what the plan covers>
Key Components:
- <main component 1>
- <main component 2>
- <main component 3>

Team Task List:
- <list of tasks, and owner (concise)>

Team members:
- <list of team members and their roles (concise)>

Review the plan on the implementation-plan page — paste one of its tweak prompts back to revise.
When you're ready, execute the plan in a new agent by running:
/harness-layer:harness-build <name-of-plan>
```

On a needs-human outcome, end with the recovery prompt from the `Needs-human exit` instead of the build hand-off.
