---
description: Grills the user to lock requirements, then creates a concise engineering implementation plan and a decision log, saved to a per-plan specs folder
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

First grill the user to lock requirements via the `Grilling Protocol`, then create a detailed implementation plan based on those locked requirements provided through the `USER_PROMPT` variable. Analyze the request, think through the implementation approach, and save the four spec-driven files to the per-plan folder `specs/<plan-name>/` by copying and filling the templates in `TEMPLATES_DIR`: the spec (`spec.md`, the entry point), the tasks (`tasks.md`), the acceptance criteria (`acceptance-criteria.md`), and a decision log (`decisions.md`) recording the grilling outcome. Follow the `Instructions` and work through the `Workflow` to create the plan.

## Variables

USER_PROMPT: $1
ORCHESTRATION_PROMPT: $2 - (Optional) Guidance for team assembly, task structure, and execution strategy
PLAN_OUTPUT_DIRECTORY: `specs/<plan-name>/` - per-plan folder; `<plan-name>` is the descriptive kebab-case topic
SPEC_FILE: `specs/<plan-name>/spec.md` - what/why, the `## Tracking` block, and the Codex review record (the entry point)
DECISION_LOG: `specs/<plan-name>/decisions.md` - grilling decision log + assumptions
TASKS_FILE: `specs/<plan-name>/tasks.md` - phases, team, and step-by-step tasks
ACCEPTANCE_FILE: `specs/<plan-name>/acceptance-criteria.md` - acceptance criteria + validation commands
TEMPLATES_DIR: `specs/_templates/` - the four source templates; the single source of truth for section layout
TEAM_MEMBERS: `.claude/agents/team/*.md`
GENERAL_PURPOSE_AGENT: `general-purpose`

## Instructions

- **PLANNING ONLY**: Do NOT build, write code, or deploy agents. Your only output is the four spec files saved to `PLAN_OUTPUT_DIRECTORY`.
- The PLANNING ONLY rule still permits the tracking/setup this plan explicitly calls for: creating the single Epic/Plan tracking issue (`gh issue create`), entering the shared worktree (`EnterWorktree`), committing the plan artifacts (`specs/<plan-name>/spec.md`, `tasks.md`, `acceptance-criteria.md`, `decisions.md`) and pushing the convention branch, and relaying Codex spec-review verdicts to that issue (`gh issue comment`). These record, publish, and stage the plan — they are NOT building, writing product code, or deploying agents. See `GitHub Issue Tracking` and `Publish & Per-Phase Tracking`.
- If no `USER_PROMPT` is provided, stop and ask the user to provide it.
- If `ORCHESTRATION_PROMPT` is provided, use it to guide team composition, task granularity, dependency structure, and parallel/sequential decisions.
- Carefully analyze the user's requirements provided in the USER_PROMPT variable
- Before designing or writing any files, run the `Grilling Protocol` to lock requirements. Explore the codebase to self-answer questions; ask the user only what the code cannot answer.
- Determine the task type (chore|feature|refactor|fix|enhancement) and complexity (simple|medium|complex)
- Think deeply (ultrathink) about the best approach to implement the requested functionality or solve the problem
- Understand the codebase directly without subagents to understand existing patterns and architecture
- Follow the `Output Files` section below to create the four spec files from the templates in `TEMPLATES_DIR`
- Include all required sections and conditional sections based on task type and complexity, as the templates direct
- Generate a descriptive kebab-case `<plan-name>` and create the per-plan folder `specs/<plan-name>/`.
- Save the spec to `SPEC_FILE`, the tasks to `TASKS_FILE`, the acceptance criteria to `ACCEPTANCE_FILE`, and the grilling decision log to `DECISION_LOG`.
- Ensure the plan is detailed enough that another developer could follow it to implement the solution
- Include code examples or pseudo-code where appropriate to clarify complex concepts
- Consider edge cases, error handling, and scalability concerns
- Understand your role as the team lead and orchestrate the team accordingly.
- The `## Codex Findings` section of `spec.md` is Codex-owned (written only by the `spec-review` skill). NEVER write to or edit that section. Claude refines only the rest of the plan body between Codex rounds.

## Grilling Protocol

Before designing the plan, interview the user relentlessly until every decision
needed to build is resolved. The goal is a shared, written understanding, not a guess.

- **Explore first.** If a question can be answered by reading the codebase, answer
  it yourself. Ask the user only what the code cannot tell you.
- **One question at a time.** Ask exactly one question per turn using the
  AskUserQuestion tool. Provide 2-4 concrete options, put your recommended answer
  first and append " (Recommended)" to its label; the tool's automatic "Other"
  choice lets the user type a free-form answer. Wait for the answer before the
  next question.
- **Coverage ledger.** Track a checklist of decision dimensions as resolved or
  open; keep grilling until none are open. Cover, as applicable: scope & non-goals,
  target users, success criteria & acceptance tests, data model, interfaces/APIs,
  edge cases & error handling, performance & scale, security & authz,
  observability, rollout/migration, dependencies, testing strategy. Mark
  genuinely-irrelevant dimensions N/A.
- **Adaptive depth.** Grill in proportion to complexity: a light pass for simple
  chores, a deep pass for complex features. Do not interrogate trivial tasks.
- **Accept-all escape hatch.** Offer a standing way to stop early. If the user
  chooses "Accept all recommendations", close every open item with your
  recommended answers, record them as assumptions, and move on.
- **Record every decision.** Capture each answer, and every deferred "you decide"
  as an explicit assumption, for the decision log (`decisions.md` — see `Output Files`).
- **Final confirmation.** When the ledger is clear, replay all decisions in a
  single AskUserQuestion for sign-off (Approve / revise a specific decision / add
  more). Proceed to design only after approval.

## Workflow

IMPORTANT: **PLANNING ONLY** - Do not execute, build, or deploy. Output is a plan document.

1. Analyze Requirements - Parse the USER_PROMPT to understand the core problem and desired outcome
2. Understand Codebase - Without subagents, directly understand existing patterns, architecture, and relevant files
3. Grill Requirements - Run the `Grilling Protocol`: interview the user one question at a time via AskUserQuestion until the coverage ledger is clear, then get final sign-off. Do NOT design or write files before this completes.
4. Design Solution - Develop technical approach including architecture decisions and implementation strategy
5. Create Tracking Issue - After sign-off, with the plan title and objective known and BEFORE entering the worktree (so the intended branch carries `#N`), create ONE Epic/Plan GitHub issue via `gh issue create` (see `GitHub Issue Tracking`). Skips gracefully if `gh`/remote/auth is unavailable.
6. Enter Worktree - `EnterWorktree` by default so the plan→build lifecycle shares one worktree; the plan folder and all four spec files (`spec.md`, `tasks.md`, `acceptance-criteria.md`, `decisions.md`) are all written INSIDE the worktree.
7. Define Team Members - Use `ORCHESTRATION_PROMPT` (if provided) to guide team composition. Identify from `.claude/agents/team/*.md` or use `general-purpose`. Document in plan.
8. Define Step by Step Tasks - Use `ORCHESTRATION_PROMPT` (if provided) to guide task granularity and parallel/sequential structure. Write out tasks with IDs, dependencies, assignments. Document in plan.
9. Generate Plan Folder - Create a descriptive kebab-case `<plan-name>` and the per-plan folder `specs/<plan-name>/`
10. Save Plan - Copy each template from `TEMPLATES_DIR` and write all four files: the spec to `SPEC_FILE`, the tasks to `TASKS_FILE`, the acceptance criteria to `ACCEPTANCE_FILE`, and the grilling decision log to `DECISION_LOG` (see `Output Files`)
11. Record Tracking - Record the `## Tracking` block in `spec.md` (issue number, intended convention branch name, worktree path) per `GitHub Issue Tracking`. `spec.md` is the single home for this block; `decisions.md` does NOT duplicate it.
12. Publish Plan Branch - Create the issue-linked convention branch (`createLinkedBranch`), commit `specs/<plan-name>/`, push the plan commits, then update the issue's "Link to plan" to accessible blob URLs — see `Publish & Per-Phase Tracking`. Skips the push gracefully when `gh`/remote/GraphQL is unavailable.
13. Codex Verification - Run the `Codex Verification Loop` to hand the saved spec to Codex for review, committing + pushing the plan after each round/fix (per-phase tracking); skips gracefully if the Codex CLI is unavailable.
14. Save & Report - Follow the `Report` section to summarize key components and emit the new file paths

## GitHub Issue Tracking

The plan→build lifecycle is threaded by a single GitHub issue. `/plan-w-team` opens that issue, enters a shared worktree, and records both in a `## Tracking` block that `/build` later reads to resume. Codex stays verdict-only — Claude is the only actor that calls `gh`.

### Create the Epic/Plan issue (Workflow step 5)

After the Grilling Protocol sign-off, once the plan title and objective are known and BEFORE entering the worktree (so the intended branch can carry `#N`), create ONE Epic/Plan issue with `gh issue create`, then assign + label it idempotently so a missing label can never abort creation:

```
# 1. ensure every label exists FIRST (idempotent; self-heals a fresh clone / deleted label)
gh label create epic         --color … --description … --force
gh label create <type-label> --color … --description … --force
# 2. create the issue
gh issue create --template "Epic / Plan" --title "📋 epic: <descriptive core title>" --body "<objective + a placeholder link to specs/<plan-name>/spec.md>"
# 3. apply assignee + labels AFTER create, so a missing label can't abort the create
gh issue edit <N> --add-assignee @me --add-label epic --add-label <type-label>
```

- Title = `📋 epic: <descriptive core title>` — the `📋 epic:` prefix is standardized here in the create step (the frontmatter `title:` prefix only auto-applies in the web UI, not via `gh issue create --title`). Body = the objective plus a placeholder link to `specs/<plan-name>/spec.md`; the link is updated to accessible blob URLs once `spec.md` is pushed (see `Publish & Per-Phase Tracking`).
- The template lives at `.github/ISSUE_TEMPLATE/epic-spec.md`; `--template "Epic / Plan"` is matched by the frontmatter `name:` field, so the file rename does not change the flag.
- Create exactly one issue per plan — its number `#N` is the durable join key for the whole workflow.
- **Assignee + labels**: every epic issue is assigned to the human owner (`--assignee @me`) and labelled `epic` + the branch-`<type>` label.
- **`<type>`→label mapping**: `feat→enhancement`, `fix→bug`, `docs→documentation`; `chore`/`refactor`/`perf`/`style`/`test` are same-named; plus `epic` for plan issues.
- **Labels are created on demand**: run the idempotent `gh label create <name> --color … --description … --force` for each label BEFORE applying it, so a fresh clone or a deleted label self-heals and never aborts the run.
- Graceful-skip the entire label/assignee/issue step if `gh` is unavailable (see `Graceful gh skip`).

### Enter the worktree (Workflow step 6)

After issue creation, `EnterWorktree` by default. Write the per-plan folder and all four spec files (`spec.md`, `tasks.md`, `acceptance-criteria.md`, `decisions.md`) INSIDE the worktree so `/build` can resume the same working directory.

### Record the `## Tracking` block (Workflow step 11)

Record into `spec.md`'s `## Tracking` section (the single home for this block — `decisions.md` does NOT duplicate it):

- **Issue**: the issue number `#N`, or the literal `none — gh unavailable` when no issue was created.
- **Branch**: the intended convention branch name `<type>/<N>-<slug>`, or `<type>/<slug>` (no `#N`) when there is no issue.
- **Worktree**: the worktree path.

IMPORTANT: the recorded **Issue** field is the SINGLE SOURCE OF TRUTH that `/build` reads — `/build` NEVER re-derives `#N` (e.g. by parsing the mangled local branch name).

### Graceful `gh` skip

If `gh`/remote/auth is unavailable (gh not installed, not authenticated, or no remote), SKIP issue creation, label creation, assignee/label application, the `createLinkedBranch` linkage, all branch pushes, the issue-body link update, and ALL issue comments: record `Issue: none — gh unavailable` in the `## Tracking` block (so the branch falls back to `<type>/<slug>`), warn the user, commit the plan locally, and continue local-only. A missing `gh` must NEVER block planning. (Mirrors the Codex graceful-skip pattern in the Codex Verification Loop below.)

## Publish & Per-Phase Tracking

`/plan-w-team` is publish-and-track: once the `## Tracking` block is recorded it creates the issue-linked convention branch, pushes the plan artifacts so the plan is reviewable on GitHub immediately, and then commits + pushes again after every spec-review round (per-phase tracking) so the branch shows the plan's evolution. Claude is the only actor that calls `gh`/`git` here; product code is still NEVER written and agents are NEVER deployed (this is the relaxed PLANNING-ONLY carve-out).

### Commit conventions for every plan commit

- **No `Co-Authored-By` trailer** on ANY plan commit (dogfoods the repo's no-trailer policy).
- Plan-doc commits use the `📝 docs` type even though the branch type is `chore` — e.g. `📝 docs(plan): …`, with a `Refs #<N>` footer.
- **Scope each commit to `specs/<plan-name>/` only** (`git add specs/<plan-name>/`), NEVER `git add -A`, so unrelated working-tree changes (e.g. pending build work) are never swept in.

### Create the issue-linked branch, then initial publish (Workflow step 12)

`createLinkedBranch` can only CREATE a branch — it cannot attach to a branch that was already pushed — so it MUST run BEFORE the first push. Create the branch FROM the issue (so it shows under the issue's **Development** panel), then push the plan commits onto it:

```
ISSUE_ID=$(gh api repos/<owner>/<repo>/issues/<N> --jq .node_id)
BASE=$(git rev-parse origin/main)
gh api graphql -f query='mutation($i:ID!,$o:GitObjectID!,$n:String!){createLinkedBranch(input:{issueId:$i,oid:$o,name:$n}){linkedBranch{ref{name}}}}' \
  -f i="$ISSUE_ID" -f o="$BASE" -f n="<type>/<N>-<slug>"   # creates + links the branch on origin
git add specs/<plan-name>/
git commit -m "📝 docs(plan): add plan for <plan-name>" -m "Refs #<N>"
git push -u origin HEAD:refs/heads/<type>/<N>-<slug>        # pushes plan commits onto the linked branch
```

- **Branch linkage stays Option B**: the mangled local worktree branch is kept; the clean convention name is enforced only on the remote ref via `git push -u origin HEAD:refs/heads/<type>/<N>-<slug>`. The Worktree Rule docs are unchanged.
- If the branch was already pushed UNLINKED, the only retrofit is a destructive delete+recreate of the remote branch at the same SHA — gate that on EXPLICIT user approval.

### Update the issue's "Link to plan" with accessible URLs (right after the first push) — body-sync touchpoint (1)

Once the branch + files exist on origin, this `gh issue edit --body-file <updated-body>` writes the COMPLETE `epic-spec.md` body skeleton — ALL sections (Objective, Non-Goals, `## Lifecycle` with ▲ at **Plan**, `## Link to plan` filled with the four path-as-text links, `## Spec-review status` seeded at `_pending_` / `Drafted for Review`, `## Acceptance criteria` pointer, Open Questions, How to act) — not just the two link sections. (The `gh issue create --body "<objective + placeholder>"` at create time seeds only a minimal body and `--body` overrides `--template`, so the created issue has none of these sections yet.) This PUBLISH-time edit seeds the full structured skeleton, which the per-round body-sync touchpoints (2)/(3) then overwrite in place — so it establishes the precondition those touchpoints depend on. For the `## Link to plan` and `## Acceptance criteria` sections specifically, use **path-as-text markdown links** — the **display text is the repo path** (`specs/<plan-name>/spec.md`) and the **href is the blob URL on the convention branch** so it resolves pre-merge (never against `main`, where the plan files don't exist until merge, so a bare repo-relative path 404s). Never show a bare repo-relative path and never show the raw URL as the display text. Link all four plan files; point Acceptance criteria at `acceptance-criteria.md`. This is **body-sync touchpoint (1)**; graceful-skip the `gh issue edit` if `gh`/remote is unavailable (see `Graceful skip`).

```
gh issue edit <N> --body-file <updated-body>
# ## Link to plan — one path-as-text link per plan file:
#   - Spec: [specs/<plan-name>/spec.md](https://github.com/<owner>/<repo>/blob/<type>/<N>-<slug>/specs/<plan-name>/spec.md)
#   - Tasks: [specs/<plan-name>/tasks.md](https://github.com/<owner>/<repo>/blob/<type>/<N>-<slug>/specs/<plan-name>/tasks.md)
#   - Acceptance: [specs/<plan-name>/acceptance-criteria.md](https://github.com/<owner>/<repo>/blob/<type>/<N>-<slug>/specs/<plan-name>/acceptance-criteria.md)
#   - Decisions: [specs/<plan-name>/decisions.md](https://github.com/<owner>/<repo>/blob/<type>/<N>-<slug>/specs/<plan-name>/decisions.md)
# ## Acceptance criteria — a pointer to acceptance-criteria.md (NOT a mirrored checklist)
```

A commit-pinned permalink (`/blob/<commit-sha>/…`) is acceptable for post-merge durability; a branch URL is preferred while the work is in review because it always shows the latest.

### Per-phase commit + push through the Codex loop

After the initial publish, commit + push again after EACH spec-review round and EACH fix, so the published branch reflects the gated plan. The push always happens AFTER the round that produced the appended `## Codex Findings`:

- after Codex Round 1 appends its verdict → `git commit -m "📝 docs(plan): record Codex spec-review round 1" -m "Refs #<N>"` → push
- after Claude applies round-1 fixes → `git commit -m "📝 docs(plan): apply Codex round 1 fixes" -m "Refs #<N>"` → push
- after Codex Round 2 → commit → push
- after any final fix → commit → push

Each push is `git push -u origin HEAD:refs/heads/<type>/<N>-<slug>` (Option B refspec). See `Codex Verification Loop` for where each round happens.

### Graceful skip

If `command -v gh` fails, there is no remote, a push errors, or GraphQL is unavailable: commit LOCALLY and SKIP the push (warn, continue). The `createLinkedBranch` and `gh issue edit` steps skip the same way. A missing `gh`/remote MUST NEVER block planning — mirrors the graceful `gh` skip in `GitHub Issue Tracking`.

## Codex Verification Loop

After the four spec files are saved (Workflow step 13) and before the report, hand the drafted spec to Codex for an independent review. Codex writes its verdict + findings into the Codex-owned `## Codex Findings` section of `spec.md`; Claude reads the verdict, refines the rest of the plan body where warranted, and re-submits — capped at 2 Codex rounds.

### Precondition / graceful skip

- Check Codex availability with `command -v codex`. If Codex is unavailable, SKIP the loop: warn the user (point them to `/codex:setup`), record the outcome `skipped — Codex unavailable` in `spec.md`'s Claude-owned `## Codex Verification` section, leave `spec.md`'s `Status:` at `Drafted for Review`, and continue to the report normally. Never block planning on a missing Codex.

### Scaffold

- `spec.md` already contains the `## Codex Findings` section seeded with the `_Pending Codex review._` note (from the `spec.md` template). Do NOT write into that section — it is Codex-owned. Claude refines only the rest of the plan body between rounds.

### Invocation (verbatim)

Run the following, substituting `<REPO_ROOT>` (the repo cwd that contains `.agents/skills/spec-review/`) and `<SPEC_PATH>` = `specs/<plan-name>/spec.md`:

```
codex exec -C "<REPO_ROOT>" -s workspace-write "Use the spec-review skill to review the four-file plan-w-team spec under specs/<plan-name>/ (spec.md is the entry point) at <SPEC_PATH>. Follow the skill's output contract exactly: append your per-round verdict and findings ONLY under the '## Codex Findings' section of that file, and edit nothing else in the file."
```

- `codex exec` has NO `--skill` / `--full-auto` / `-a` flag — use `-s workspace-write` (the skill is auto-discovered and invoked by naming it in the prompt).
- Give each review round a generous timeout (~5 minutes): a findings-heavy round can run past the default 2-minute window, and a round that times out writes no verdict block — re-run it rather than treating the empty result as approval.

### Read the verdict from the FILE (not stdout)

The `spec-review` skill writes its full verdict + findings into `spec.md`'s Codex-owned `## Codex Findings` section and returns only a TERSE summary (the verdict line + a finding count) to the caller. Therefore Claude reads BOTH the verdict AND the detailed findings from `spec.md`'s `## Codex Findings` via the file — never from the `codex exec` stdout — when applying fixes and relaying to the issue. Do NOT pipe or expand the codex stdout; the terse return is intentional.

```
grep -E '^### Round [0-9]+ — Verdict: (approved|changes-requested)$' specs/<plan-name>/spec.md | tail -1
```

(The dash is a literal em-dash, U+2014.)

### Relay the verdict to the issue — body-sync touchpoint (2)

After reading each round's verdict, do TWO things — ONLY when an issue number exists in the `## Tracking` block (skip both entirely when it reads `Issue: none — gh unavailable`):

1. **Append the HISTORY** — relay the round to the tracking issue with `gh issue comment`, using the canonical Verdict relay-comment from `Canonical issue snippets` below:

```
gh issue comment <N> --body "<the canonical Verdict relay-comment for this round>"
```

2. **Overwrite the STATE** — then `gh issue edit <N> --body-file <updated-body>` to overwrite the issue body's `## Spec-review status` block with the canonical `## Spec-review status` state-mirror snippet from `Canonical issue snippets` below:

```
gh issue edit <N> --body-file <updated-body>   # overwrite ONLY the `## Spec-review status` block in place
```

- This is **body-sync touchpoint (2)**.
- The split is explicit: **comment = history (appended)**, **body `## Spec-review status` = state (overwritten)**. The comment thread grows one entry per round; the body block is replaced **in place / idempotently** so re-running a round never appends a duplicate `## Spec-review status` block.
- The `gh issue comment` builds a single chronological spec-review audit trail on the issue; the `gh issue edit` keeps the body's state mirror current.
- Never block the loop on a failed or unavailable `gh` call — warn and continue, graceful-skipping the `gh issue edit` the same way (mirrors the graceful `gh` skip in `GitHub Issue Tracking`).

### Canonical issue snippets (reproduce exactly)

Reproduce BOTH blocks exactly — the first is the per-round `gh issue comment` body (HISTORY, appended once per round), the second is the issue-body `## Spec-review status` block (STATE, overwritten in place each round).

**(a) Verdict relay-comment** — the per-round `gh issue comment` body (HISTORY):

```
### 🔍 Codex spec-review — Round <N> · <approved | changes-requested>

**Blocking findings:** <count, or "none">

- <one bullet per blocking finding — title + one-line summary, or "—">

**Claude this round:** <the fixes Claude applied this round, or "no changes — approved">

Full detail: [spec.md › ## Codex Findings](https://github.com/<owner>/<repo>/blob/<type>/<N>-<slug>/specs/<plan-name>/spec.md#codex-findings)
```

**(b) `## Spec-review status` state-mirror** — the issue-body block overwritten each round (STATE):

```
## Spec-review status

- Latest verdict: <approved | changes-requested> (round <N>)
- Status: <Drafted for Review | Approved ✅ | Needs Human Review ⚠️>
- History: see thread ↓
```

- The relay-comment's `Full detail` pointer is a **clickable markdown link** to `spec.md`'s Codex Findings section via the `#codex-findings` heading anchor on the convention branch — NOT plain text.

### Commit + push after each round (per-phase tracking)

After each round's verdict is appended to `## Codex Findings`, and after each fix Claude applies, commit + push the plan per `Publish & Per-Phase Tracking` so the published branch reflects the gated plan: Round 1 verdict → commit/push; round-1 fixes → commit/push; Round 2 verdict → commit/push; final fix → commit/push. The push always happens AFTER the round that produced the appended findings. Graceful-skip the push if `gh`/remote is unavailable.

### Loop control — max 2 Codex rounds

- **Round 1** → if the verdict is `approved`, the loop is done. If `changes-requested`, Claude applies the warranted fixes to the spec body ONLY — any of the four files, but NEVER the Codex-owned `## Codex Findings` section; for any finding Claude rejects, it records the finding + its rationale in `spec.md`'s Claude-owned `## Codex Verification` section. Then run **Round 2**.
- **Round 2** → if still `changes-requested`, Claude applies a best-effort final pass and PROCEEDS anyway, recording "proceeded without full Codex approval after 2 rounds" + the outstanding findings in `spec.md`'s `## Codex Verification` section.
- Never exceed 2 Codex rounds.

### Record the outcome + flip the Status (Workflow step 13)

Once the loop settles, Claude writes the result into `spec.md`'s Claude-owned `## Codex Verification` section (the outcome summary — `approved at round N` | `proceeded without full approval after 2 rounds` | `skipped — Codex unavailable` — plus any rejected findings with their rationale; this is NOT `decisions.md` and NOT the Codex-owned `## Codex Findings`), then edits `spec.md`'s `Status:` line:

- Codex returned `approved` → set the `Status:` line to `Approved`.
- still `changes-requested` after 2 rounds → set the `Status:` line to `Needs Human Review`.
- Codex was skipped (unavailable) → leave the `Status:` line at `Drafted for Review`.

Then — **body-sync touchpoint (3)** — once the loop settles, in addition to flipping `spec.md`'s `Status:` line, also `gh issue edit <N> --body-file <updated-body>` the issue body to (a) set the `## Spec-review status` `Status` line and (b) advance the `## Lifecycle` ▲ marker to the settled phase:

- Codex returned `approved` → `## Spec-review status` Status `Approved ✅` and `## Lifecycle` ▲ advanced to **Approved**.
- still `changes-requested` after 2 rounds → Status `Needs Human Review ⚠️`, but the `## Lifecycle` ▲ marker STAYS at **Spec-review** (the phase the plan is stuck in).
- Codex was skipped (unavailable) → leave the ▲ marker at **Plan**/Drafted for Review (no advance).

The `## Lifecycle` ▲ marker only ever points at one of the six real Lifecycle nodes (`Plan ▸ Spec-review ▸ Approved ▸ Build ▸ Ship ▸ Done`) — "Needs Human Review" is a Status, not a Lifecycle phase, so it never appears under the ▲.

Graceful-skip this `gh issue edit` if `gh`/remote is unavailable (mirrors the graceful `gh` skip in `GitHub Issue Tracking`).

## Skill Contracts (spec-review / implementation-review)

The reworked flow respects two Codex skills; this is documentation only — **do NOT edit the skill files**.

- **`spec-review` (plan phase)** — invoked via `codex exec -s workspace-write` (network-off; `workspace-write` disables network by default), auto-discovered from `.agents/skills/` and invoked by NAMING it in the prompt (no `--skill` flag). It appends a per-round `### Round N — Verdict: approved|changes-requested` block ONLY under the `## Codex Findings` heading and edits nothing else; that section is Codex-owned (Claude never writes there). It writes its full findings into `## Codex Findings` and returns only a terse verdict summary (verdict line + finding count) to the caller, so Claude reads the detail from the file rather than from stdout. It **MUST NOT call `gh`** — Claude relays each verdict to the issue. Max 2 rounds. Each per-phase push happens AFTER the round that produced the appended findings.
- **`implementation-review` (build phase)** — invoked via `codex exec -s workspace-write` (same network-off, auto-discovery, name-to-invoke rules). It reads `spec.md` + `decisions.md` + the working-tree diff, RUNS the plan's Validation Commands and reports real PASS/FAIL, emitting its per-round verdict as its FINAL CLI message only (writes no files, edits no source). Claude's builders apply fixes; Claude relays each verdict to the PR. Max 2 rounds.
- **Shared**: both run network-off, are auto-discovered from `.agents/skills/`, and are invoked by naming them (no `--skill` flag); Claude is the only actor that calls `gh`.

## Output Files

Copy each template from `TEMPLATES_DIR` (`specs/_templates/`), fill every `<…>` micro-prompt and the required `##` sections, and save it to the matching per-plan path. Do not invent structure — the templates are the single source of truth for section layout.

- The micro-prompt rule still applies: `<requested content>` is a prompt to replace with the requested content; everything OUTSIDE the `<…>` placeholders is copied verbatim from the template.
- Include the conditional sections each template marks (e.g. `## Problem Statement` / `## Solution Approach` in `spec.md`, `## Implementation Phases` in `tasks.md`) for feature or medium/complex tasks; omit them for simple chores, exactly as the in-template comments direct.

Which content goes in which file:

| Template (in `TEMPLATES_DIR`) | Save to           | Content it owns                                                                                                                                                                                                                   |
| ----------------------------- | ----------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `spec.md`                     | `SPEC_FILE`       | The _what_ & _why_: Task Description, Objective, Non-Goals, Requirements & Decisions, the `## Tracking` block, plus the Codex review records — `## Codex Findings` (Codex-owned) and `## Codex Verification` (Claude-owned). The entry point. |
| `tasks.md`                    | `TASKS_FILE`      | The _how_ & _who_: Implementation Phases, Team Orchestration / Team Members, and the Step by Step Tasks.                                                                                                                          |
| `acceptance-criteria.md`      | `ACCEPTANCE_FILE` | The _done_ definition: the Acceptance Criteria and the Validation Commands that prove them.                                                                                                                                       |
| `decisions.md`                | `DECISION_LOG`    | The grilling record ONLY: Summary, Resolved Decisions, Assumptions, Open Questions / Out of Scope. No `## Tracking` block — that lives only in `spec.md`.                                                                          |

`spec.md` is the entry point and the single home of the `## Tracking` block; `decisions.md` does NOT duplicate Tracking.

## Report

After creating and saving the four spec files, provide a concise report with the following format:

```
✅ Implementation Spec Created

Spec: specs/<plan-name>/spec.md
Tasks: specs/<plan-name>/tasks.md
Acceptance Criteria: specs/<plan-name>/acceptance-criteria.md
Decisions: specs/<plan-name>/decisions.md
Topic: <brief description of what the plan covers>
Status: <Drafted for Review | Approved | Needs Human Review>
Codex Verification: <approved at round N | proceeded without approval after 2 rounds | skipped (Codex unavailable)>
Key Components:
- <main component 1>
- <main component 2>
- <main component 3>

Key Decisions (from grilling):
- <most important locked decision or assumption 1>
- <decision 2>
- <decision 3>

Team Task List:
- <list of tasks, and owner (concise)>

Team members:
- <list of team members and their roles (concise)>

When you're ready, you can execute the plan in a new agent by running:
/build <plan-name>
```
