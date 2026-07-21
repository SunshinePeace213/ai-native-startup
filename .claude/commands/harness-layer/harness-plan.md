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

Turn `USER_PROMPT` (ideally the finalized prompt from `/harness-layer:harness-interview`) into a four-file spec folder the team can build from — for any coding OR harness-layer task. Resolve what the codebase and KB answer, fill only genuinely-open gaps through the `Readiness Gate`, and never re-litigate a locked ledger. When the work touches the harness layer, ground every claim in the KB first (see `Domain Knowledge`); otherwise plan straight from the codebase. Draft at `specs/<name-of-plan>/` on the chain's worktree (or a fresh one), push to GitHub, gate with a Codex peer review (`spec-review`, driven by a `sonnet` runner), then publish the implementation-plan page for the user's async review.

## Variables

USER_PROMPT: $1
ORCHESTRATION_PROMPT: $2 - (Optional) Guidance for team assembly, task structure, and execution strategy
MAX_REVIEW_ROUNDS: `2` - hard cap on NEW Codex rounds per review cycle; over the cap auto-resolves to needs-human
CROSS_REVIEW_SKILL: `spec-review` — the Codex-side review skill in `.agents/skills/`
KNOWLEDGE_BASE: `ai-docs/` — cached official docs; catalog in `ai-docs/index.md`, manifest in `ai-docs/sources.yaml`
STALE_AFTER: `30` days — a KB doc older than this is stale

## Instructions

- **PLANNING ONLY** — draft the spec; do not build, write code, or deploy builder agents. Helper subagents are allowed: the `claude-code-guide` KB cross-check, `kb-fetcher` for KB mirrors, and the `sonnet` Codex review runner — never builders; you never write mirror content yourself. Output is the four-file spec folder plus its artifacts — drafted in the worktree, then committed and pushed to `origin` (plan docs plus any gap-filled KB docs, never implementation code).
- If no `USER_PROMPT` is provided, stop and ask the user for it.
- Think deeply (ultrathink) about the best approach; determine the task type (feat|fix|docs|style|refactor|perf|test|chore) and complexity (simple|medium|complex).
- Understand the codebase directly — application code and any existing harness patterns under `.claude/` and `.agents/` — without subagents, save the helpers above.
- If `ORCHESTRATION_PROMPT` is provided, let it guide team composition, task granularity, dependency structure, and parallel/sequential decisions.
- **Ground harness-layer claims.** When the expert layer is active, statements about hooks, frontmatter, subagents, skills, commands, MCP, or model aliases must trace to a KB doc (see `Domain Knowledge`); record what you consulted in decisions.md's `## KB References`.
- Ensure the spec is detailed enough that another developer could follow it, covering edge cases, error handling, and scalability.

## Domain Knowledge

Conditional expert layer. Run it only when the task touches the harness surface — any of `.claude/`, `.agents/`, `.codex/`, `ai-docs/`, the memory files (CLAUDE.md, AGENTS.md), or a domain that has an `ai-docs/index.md` entry. When no signal fires, state that the expert layer is skipped, read no KB docs, and set the review profile to `standard`. When a signal fires, set the profile to `kb-grounded` and run collect → cross-check → reconcile:

1. **Collect.** Read `ai-docs/index.md` and open every cached doc relevant to the request's surface (hooks work → hooks.md; a new command → skills-and-commands.md; and so on). If a doc you load is older than `STALE_AFTER`, continue with the stale copy, note it in decisions.md `## KB References`, and flag it in the Report with a `/harness-layer:kb` suggestion.
2. **Cross-check.** Deploy the `Agent` tool with `subagent_type: "claude-code-guide"`, passing the specific harness claims/topics the plan depends on and asking it to verify them against current official behavior.
3. **Reconcile.** Where both sources agree, continue. Where they conflict on a claim, refresh that mirror via a `kb-fetcher` subagent (the entry's url + the absolute target path in the worktree), then Read the fresh mirror — it wins; log the conflict + resolution in decisions.md `## KB References`. If the fetch fails, prefer the source with the newer verifiable date and mark the claim unverified in the spec.
4. **Gap-fill:** if the KB has no doc for a topic the plan depends on, mirror it now — spawn a `kb-fetcher` subagent with the official page's URL (ask the claude-code-guide subagent for the right URL if unsure) and the absolute target path under `ai-docs/` in the worktree, add its entry to `ai-docs/sources.yaml`, then Read the fresh mirror — all committed with the spec.
5. Log every doc you relied on — path + its `fetched` date — in decisions.md under `## KB References` (a section you append; the templates don't carry it).

## Readiness Gate

No re-interviewing a locked ledger; a bounded ask only for what's genuinely open.

- **Ledger.** When `specs/<slug>/discovery/decisions-draft.md` exists in the worktree, transcribe it into decisions.md — resolved decisions stay resolved, never re-litigated. Reference discovery pages from the spec; never copy them.
- **Assess coverage the way the interview does:** first resolve every point the codebase and KB can answer, so only genuinely-open decisions remain. Then respond by how much is open:
  - **Fully covered** (all fields present, or ledger-complete) → ask nothing; go straight to design.
  - **A few open points** → ONE `AskUserQuestion` round (≤4 questions, biggest blast radius first); fold answers into decisions.md and any related spec file.
  - **Many unknowns / no defensible approach** → STOP and recommend `/harness-layer:harness-interview "<USER_PROMPT>"`.
- **Residual gaps** after asking → pick your recommended answer and record it in decisions.md `## Assumptions` with what would invalidate it. Never stall.
- **Revision.** When the worktree already holds `specs/<slug>/spec.md`, this run is a revision (a tweak prompt from the implementation-plan page, or blockers resolved after needs-human) — see `Revision Mode`.

## Workflow

IMPORTANT: **PLANNING ONLY** — do not execute, build, or deploy builder agents. Output is a plan document.

1. Enter Worktree — `Worktree:` line in the prompt → `EnterWorktree(path: ...)`; otherwise `EnterWorktree(name: "<slug>")` (see `Worktree & Handoff`). An existing `specs/<slug>/spec.md` switches the run to `Revision Mode`.
2. Readiness Gate — transcribe any discovery ledger, assess coverage, and fill only genuinely-open gaps (see `Readiness Gate`).
3. Understand Codebase — directly read the relevant code and any existing harness patterns under `.claude/` and `.agents/` (only the helper subagents from Instructions are allowed).
4. Set Review Profile — apply the `Domain Knowledge` trigger: an expert-layer signal fires → load the KB docs and set the profile to `kb-grounded`; otherwise skip the layer and set `standard`.
5. Design Solution — technical approach, architecture decisions, edge cases, error handling, and scalability, grounded in the KB docs when the expert layer is active.
6. Define Team & Tasks — draw team members from the available agent types (default `general-purpose`); write tasks with IDs, dependencies, assignments, and each task's model + effort stamped per the model-selection rule (it loads every session). `ORCHESTRATION_PROMPT`, when provided, guides composition, granularity, and parallel/sequential structure. Document both in the plan. Mark any task whose outcome must be recorded to memory — the build/review memory steps record exactly those.
7. Name the Plan — reuse the chain `<slug>` (rename with `git mv` only if actively wrong) or generate a descriptive kebab-case name from the plan's main topic; pick its change `<type>` (feat/fix/chore/refactor/docs/style/perf/test).
8. Create & Link Issue — first cycle only: file the GitHub issue from the ledger + Assumptions and link its convention branch (see `Worktree & Handoff`).
9. Write the Spec Folder — create `specs/<name-of-plan>/` and fill all four files from `specs/_templates/`; append `## KB References` to decisions.md when the expert layer is active; write any gap-filled KB docs and their `ai-docs/sources.yaml` entries; record the issue, branch, worktree path, and review profile in spec.md's `## Tracking`.
10. Commit & Push — commit the spec folder (plus gap-filled KB docs) with a `Refs #N` footer, push its branch to `origin`, then post the plan-links comment on the issue (see `Worktree & Handoff`).
11. Cross-Review — a `sonnet` runner has Codex review the spec with `CROSS_REVIEW_SKILL`, at most `MAX_REVIEW_ROUNDS` new rounds this cycle, fixing blocking findings each round (see `Codex Cross-Review`).
12. Implementation-Plan Page — after the gate settles, author and publish the page per `Plan Artifacts`, commit and push it.
13. Report — summarize the spec folder and its key components (see `Report`).

## Output: Spec Folder

Write the plan as four files under `specs/<name-of-plan>/`. Copy each file from `specs/_templates/`, then replace every `<placeholder>` with real content. Keep each template's `##` headings exactly as written — a Stop hook checks that every required section is present before the run can end.

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
- **Create the issue** (first cycle only). Pick the skeleton kind from `<type>` — feat→`feature`, fix→`bug`, docs/style/refactor/perf/test/chore→`chore`, `epic` only for a genuine multi-issue initiative. Fill `specs/_templates/issues/<kind>.md` from the interview ledger and Assumptions, write it to a temp file, and create the issue: `gh issue create --title "<emoji> <type>: <plan title>" --body-file <tmp> --label <type> --label priority:P<0-3> --assignee <login>` (gitmoji from the commit table, matching the issue forms) — exactly one type label from {feat,fix,docs,style,refactor,perf,test,chore}, one `priority:P0`–`priority:P3` label, and your GitHub login (`gh api user -q .login`) as `<login>`. Note the returned issue number `#N`.
- **Link the branch.** `gh issue develop <N> --base main --name <type>/<N>-<slug>` creates the convention branch on the issue.
- **Tracking.** In spec.md's `## Tracking`, record Issue `#N`, Branch `<type>/<N>-<slug>`, the absolute worktree path (`git rev-parse --show-toplevel`), and `Review profile: kb-grounded|standard`.
- **Commit.** Stage the spec folder (`git add specs/<name-of-plan>/`) plus any gap-filled KB docs (`git add ai-docs/`) and make one commit `<emoji> <type>(spec): draft plan for <name-of-plan>` with a `Refs #N` footer.
- **Push.** `git push -u origin HEAD:refs/heads/<type>/<N>-<slug>` lands the convention branch on GitHub (bare `git push` refuses from the local `worktree-<slug>` branch).
- **Plan-links comment.** After the first push, upsert one issue comment keyed `<!-- plan-links -->` whose body links all four spec files as blob URLs on the convention branch — upsert per `git-workflow.md` § Idempotent Marker Comments.

## Revision Mode

When the worktree already holds `specs/<slug>/spec.md`:

- Apply the input (tweak prompt or resolved blockers) to the spec files; log what changed and why in decisions.md. Keep issue `#N` from `## Tracking` — no new issue, no new branch, no re-litigating resolved decisions.
- Commit with `Refs #N` and push with the same refspec.
- Run a fresh Codex cycle: round numbers continue from the last report (a cycle allows at most `MAX_REVIEW_ROUNDS` new rounds).
- Re-author and republish the implementation-plan page from the revised spec.
- When the cycle reaches `approved` after a prior needs-human, remove the label: `gh issue edit <N> --remove-label status:needs-human`.

## Codex Cross-Review

Once the plan is pushed, a `sonnet` review runner drives Codex as a peer reviewer inside the worktree — at most `MAX_REVIEW_ROUNDS` new rounds this cycle, round numbers continuing across cycles. Before each round, pick the Codex model and reasoning effort per the model-selection rule based on the spec's complexity. Beyond ordinary spec defects, when the expert layer is active Codex verifies the spec's harness claims against the KB docs, and it always challenges the approach for a simpler, cleaner design. Snapshot the reviewed head SHA before each round; check every push's exit status directly. Loop per round N:

1. **Spawn the review runner.** Deploy it with the `Agent` tool — `subagent_type: "general-purpose"`, `model: "sonnet"`, `run_in_background: false` — never run `codex exec` yourself. Its prompt carries the round number, the worktree root, the Codex model + effort, and the exact command below. The runner runs the command via Bash, checks the exit status and whether the verdict line was written, re-runs the same command once if Codex crashed / exited non-zero / wrote no verdict, and returns ONLY the round verdict (`approved` | `changes-requested`) and the report's `**Issue-comment digest:**` paragraph. It touches no git and no gh. The command:

   ```bash
   codex exec -C "<worktree root>" -s workspace-write --model <codex-model> \
     -c model_reasoning_effort="<effort>" \
     "Use the spec-review skill to review round <N> of the plan at specs/<name-of-plan>/spec.md; \
      read all four files and (when present) the KB docs listed in decisions.md ## KB References, \
      write your verdict to specs/<name-of-plan>/reviews/codex-spec-review-round-<N>.md, \
      and return only the terse summary."
   ```

2. **Verdict** from the runner's return (it matched `^### Round <N> — Verdict: (approved|changes-requested)$` in the report file). The runner reports no verdict after its one retry → take the `Needs-human exit` with reason `codex-unavailable`.
3. **Relay the digest.** Post the runner's digest paragraph verbatim as an issue comment keyed `<!-- codex-spec-round-N -->` (N = the round), upserted per `git-workflow.md` § Idempotent Marker Comments. Codex never calls `gh` — you relay.
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

Folder: specs/<name-of-plan>/ (spec.md, tasks.md, decisions.md, acceptance-criteria.md)
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
