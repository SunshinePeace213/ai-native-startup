# Plan: Trailer cleanup + guard hook + /plan-w-team publish-and-track rework + /ship merge command

## Task Description

Two folded-together workstreams:

**A — Trailer cleanup + guard hook.** The repo's Git issue/commit/PR system carries two
Claude attribution schemas:

1. `Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>`
2. `Claude-Session: https://claude.ai/code/session_<id>`

The harness/global instruction injects the `Co-Authored-By` trailer by default. This
workstream removes both schemas from the repo's message standard, researches Claude
Code hooks (→ `ai-docs/`), adds a `PreToolUse` hook that blocks `git`/`gh` commands
carrying `Co-Authored-By: Claude` (wired into `.claude/settings.local.json`), and
reduces `GIT-COMMIT-PR-MESSAGE.md` to a single policy line.

**B — `/plan-w-team` publish-and-track workflow rework.** Today `/plan-w-team` is
planning-only and pushes nothing, so a plan is invisible on GitHub until `/build`
runs. This workstream makes `/plan-w-team` commit `plan.md`/`decisions.md` and push
the convention branch so the plan is reviewable on GitHub immediately, and adds
**per-phase commit+push** through the spec-review loop (mirroring `/build`'s per-phase
tracking). It also documents the `spec-review` and `implementation-review` skill
contracts in this plan so the reworked flow respects them. The skill files themselves
are NOT modified.

**C — `/ship` finish-merge command.** `/build` opens the PR and stops, so nothing
codifies the final merge. This workstream adds a new `/ship <PR#|branch>` command that
guards, **squash-merges** the PR into `main` with a single summary commit (not all the
per-phase logs), closes the linked issue (`Closes #N`), and cleans up the remote/local
branch and the worktree.

## Objective

When complete:

- (A) The only repo references to the two trailers are the **allowed** ones: the single
  `GIT-COMMIT-PR-MESSAGE.md` policy line (which names `Co-Authored-By` as forbidden),
  the guard hook script `.claude/hooks/block-coauthor-trailer.sh` (which must contain
  the literal `Co-Authored-By: Claude` string in order to match and block it) and its
  documentation `ai-docs/claude-code-hooks.md`, this plan's own spec files
  (`specs/remove-claude-trailers-add-guard-hook/`), and the frozen historical decision
  log (`specs/git-workflow-issue-pr-tracking/decisions.md`).
  `GIT-COMMIT-PR-MESSAGE.md` states the no-trailer policy in one line; a `PreToolUse`
  hook in `.claude/settings.local.json` blocks `git`/`gh` commands carrying
  `Co-Authored-By: Claude`; `ai-docs/claude-code-hooks.md` documents hooks.
- (B) `.claude/commands/plan-w-team.md` commits + pushes the plan artifacts on the
  convention branch and commits+pushes after each spec-review round/fix (graceful-skip
  when `gh`/push is unavailable); `.claude/commands/build.md` resumes that same branch
  (already carrying the plan commits) and opens exactly one PR with `Closes #N`; this
  plan documents both Codex skill contracts. This very plan is published to
  `chore/1-remove-claude-trailers-add-guard-hook` with per-phase commits as the
  reference dogfood.
- (C) A new `.claude/commands/ship.md` exists: `/ship <PR#|branch>` guards (open +
  mergeable + CI not failing + no unpushed commits + explicit confirm; never `--admin`),
  squash-merges with an explicit summary commit (`Closes #N`, no `Co-Authored-By`), and
  cleans up the remote branch (`--delete-branch`), the local branch, and the worktree.

## Requirements & Decisions

<!-- Full record in decisions.md. -->

- **Hook (A)**: lifecycle `PreToolUse` (only event that prevents the commit pre-run);
  block & instruct (exit 2 + stderr); blocks only `Co-Authored-By: Claude …`; external
  script `.claude/hooks/block-coauthor-trailer.sh` wired via `.claude/settings.local.json`.
- **Publish (B)**: `/plan-w-team` commits `plan.md`/`decisions.md` and pushes the
  convention branch — **no PR at plan time**; `/build` opens the single PR later.
- **Per-phase commit+push (B)**: `initial plan → commit/push → Codex R1 → commit/push
→ fix → commit/push → Codex R2 → commit/push → fix → commit/push`. Push happens
  AFTER each spec-review round so the published branch reflects the gated plan.
- **Branch linkage (B)**: Option B — keep the mangled local worktree branch, push to
  `refs/heads/<type>/<N>-<slug>` with `-u` for tracking (current Worktree Rule;
  unchanged). The clean name shows on GitHub; the local name stays cosmetic.
- **Link branch to the issue's Development section (B)**: `/plan-w-team` links the
  convention branch to the GitHub issue via the `createLinkedBranch` GraphQL mutation,
  so the branch shows under the issue's **Development** panel. IMPORTANT ordering:
  `createLinkedBranch` only _creates_ a new branch — it cannot attach to an
  already-pushed one. So the reworked flow must **create the branch from the issue
  first, then push** the plan commits to it:
  1. resolve the issue node id (`gh api repos/<owner>/<repo>/issues/<N> --jq .node_id`);
  2. `createLinkedBranch(issueId, oid=<base SHA, e.g. origin/main>, name="<type>/<N>-<slug>")`;
  3. `EnterWorktree`, write the plan, commit, and push to that now-linked branch.
     For a branch that was already pushed unlinked (the only retrofit path), the link
     requires deleting and recreating the remote branch at the same SHA — a destructive
     op that needs explicit user approval. Graceful-skip the whole linking step if
     `gh`/GraphQL is unavailable; never block planning.
- **Accessible file-path links in issue/PR bodies (B)**: whenever `/plan-w-team` (or
  `/build`) writes a file path into the GitHub issue or PR body, it MUST be an
  **accessible, clickable GitHub URL**, not a bare repo-relative path. Bare paths and
  relative Markdown links resolve against the **default branch (`main`)**, where the
  plan files don't exist until merge, so they 404. Use a full blob URL on the
  convention branch:
  `https://github.com/<owner>/<repo>/blob/<type>/<N>-<slug>/specs/<plan-name>/plan.md`
  (and the same for `decisions.md`). Update the issue's **Link to plan** to these URLs
  right after the initial push (the branch + files then exist). For post-merge
  durability a commit-pinned permalink (`/blob/<commit-sha>/…`) is acceptable; a branch
  URL is preferred while the work is in review because it always shows the latest. If
  `gh` is unavailable, skip the body update gracefully.
- **Label set + creation responsibility (B)**: the type→label mapping is `feat→enhancement`,
  `fix→bug`, `docs→documentation`, and `chore`/`refactor`/`perf`/`style`/`test` =
  same-named, plus `epic` for plan issues. Defaults `enhancement`/`bug`/`documentation`
  are reused; `epic`, `chore`, `refactor`, `perf`, `style`, `test` were created as repo
  setup. **Labels are created on demand by the workflow, not assumed**: both
  `/plan-w-team` AND `/build` run an idempotent `gh label create <name> --color … --description … --force`
  for each label they're about to apply, **before** applying it — so a fresh clone or a
  deleted label self-heals and never aborts a run. Graceful-skip if `gh` is unavailable.
- **Issue metadata (B)**: every epic issue `/plan-w-team` creates is **assigned to the
  human owner** (`--assignee @me`) and **labelled** `epic` + the branch-`<type>` label
  (ensure-exists first). Applied idempotently (`gh issue edit … --add-label … --add-assignee @me`
  after create) so nothing aborts creation; graceful-skip if `gh` is unavailable.
- **PR metadata (B) — mirror the issue config**: the single PR `/build` opens carries the
  **same config shape**: `--assignee @me`, the branch-`<type>` label (derived with the
  SAME `<type>`→label mapping variable as `/plan-w-team`; ensure-exists first), and
  `Closes #N` in the body. `Closes #N` makes the PR appear under the issue's **Development**
  panel and close it on merge, so no separate `createLinkedBranch` is needed for the PR.
  (`epic` stays on the tracking issue, not the PR.) Graceful-skip if `gh` is unavailable.
- **Skills (B)**: document `spec-review` + `implementation-review` contracts here and
  respect them; **no skill-file edits**.
- **Commits**: follow `GIT-COMMIT-PR-MESSAGE.md`, carry **no `Co-Authored-By`** trailer
  (dogfoods workstream A), `Refs #N` footer.
- **/ship finish-merge (C)**: new `/ship <PR#|branch>` command — guarded (open +
  mergeable + CI ok + no unpushed commits + confirm; never `--admin`), **squash-merges**
  to one summary commit on `main` (`Closes #N`, no `Co-Authored-By`), and cleans up the
  remote branch (`--delete-branch`), the local branch, and the worktree. Graceful-skip if
  `gh` is unavailable.

## Tracking

<!-- Recorded by /plan-w-team. The Issue field is the SINGLE SOURCE OF TRUTH /build reads — /build NEVER re-derives #N (e.g. by parsing the mangled local branch name). -->

- Issue: `#1` (https://github.com/SunshinePeace213/ai-native-startup/issues/1)
- Branch: `chore/1-remove-claude-trailers-add-guard-hook`
- Worktree: `/home/ringo/ai-native-startup/.claude/worktrees/remove-claude-trailers-add-guard-hook`

## Problem Statement

- (A) The harness default appends `Co-Authored-By: Claude …` to commits and the repo
  standard documents both Claude trailers as expected footer content. The user wants
  attribution-free commits/PRs; removing the doc lines isn't enough because the harness
  keeps injecting the trailer, so an automated guard is needed at commit time.
- (B) `/plan-w-team` produces only local plan docs in a worktree and pushes nothing, so
  there is no GitHub-visible artifact to review between planning and `/build`, and no
  incremental history of how the plan evolved through the Codex gate. The plan should be
  reviewable on GitHub the moment it is drafted and at every spec-review phase.

## Solution Approach

### Workstream A — docs cleanup + enforcement + research

1. **Docs cleanup** — remove the trailer references from `GIT-COMMIT-PR-MESSAGE.md`
   (prose + example block); add one policy line.
2. **Enforcement** — a `PreToolUse` hook (external script + `settings.local.json`
   entry) that blocks `git`/`gh` Bash commands containing `Co-Authored-By: Claude`
   (exit 2 + corrective stderr). `PreToolUse` is the only stage that can stop the
   command before it runs.
3. **Knowledge capture** — a `claude-code-guide` subagent writes a deep hooks
   reference to `ai-docs/claude-code-hooks.md`.

#### Hook script (target shape — `.claude/hooks/block-coauthor-trailer.sh`)

```bash
#!/usr/bin/env bash
# PreToolUse guard: block git/gh commands that carry the Claude Co-Authored-By trailer.
# Exit 2 => deny the tool call; stderr is fed back to Claude so it retries clean.
set -euo pipefail
payload="$(cat)"

# Act only on Bash tool calls that invoke git or gh.
printf '%s' "$payload" | grep -Eq '"tool_name"[[:space:]]*:[[:space:]]*"Bash"' || exit 0
printf '%s' "$payload" | grep -Eq '\b(git|gh)\b' || exit 0

# Block when the forbidden trailer is present.
if printf '%s' "$payload" | grep -q 'Co-Authored-By: Claude'; then
  {
    echo "Blocked: this git/gh command includes a 'Co-Authored-By: Claude ...' trailer."
    echo "Repo policy (GIT-COMMIT-PR-MESSAGE.md): commit/PR messages must NOT carry the Claude attribution trailer."
    echo "Remove the 'Co-Authored-By: Claude ...' line from the message and run the command again."
  } >&2
  exit 2
fi
exit 0
```

#### settings.local.json hooks block (merge into existing JSON)

```json
{
  "enabledPlugins": { "commit-commands@claude-plugins-official": true, "codex@openai-codex": true },
  "outputStyle": "default",
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/block-coauthor-trailer.sh"
          }
        ]
      }
    ]
  }
}
```

### Workstream B — publish + per-phase tracking in /plan-w-team

Edit `.claude/commands/plan-w-team.md`:

0. **Assignee + labels at issue creation** (extend the GitHub Issue Tracking step):
   create the epic issue assigned to the human owner and labelled, e.g.
   `gh issue create … --assignee @me --label epic --label <type-label>` (or create then
   `gh issue edit … --add-assignee @me --add-label epic --add-label <type-label>` so a
   missing label can't abort creation). `<type-label>` is mapped from the branch
   `<type>` (`feat→enhancement`, `fix→bug`, `docs→documentation`; others same-named).
   Graceful-skip if `gh` is unavailable.
1. **Relax the PLANNING-ONLY carve-out** to also permit committing the plan artifacts
   and pushing the convention branch (alongside the existing issue-creation,
   EnterWorktree, and Codex-relay carve-outs). Still NO product code, NO agent
   deployment.
2. **Create the issue-linked branch, then initial publish** (new Workflow step, after
   `## Tracking` is recorded). Create the branch FROM the issue so it shows in the
   issue's **Development** panel, then push the plan commits to it:

   ```
   ISSUE_ID=$(gh api repos/<owner>/<repo>/issues/<N> --jq .node_id)
   BASE=$(git rev-parse origin/main)
   gh api graphql -f query='mutation($i:ID!,$o:GitObjectID!,$n:String!){createLinkedBranch(input:{issueId:$i,oid:$o,name:$n}){linkedBranch{ref{name}}}}' \
     -f i="$ISSUE_ID" -f o="$BASE" -f n="<type>/<N>-<slug>"   # creates + links the branch on origin
   git add specs/<plan-name>/
   git commit -m "📝 docs(plan): add plan for <plan-name>" -m "Refs #<N>"
   git push -u origin HEAD:refs/heads/<type>/<N>-<slug>        # pushes plan commits onto the linked branch
   ```

   `createLinkedBranch` can only CREATE the branch (it cannot attach to a pre-existing
   one), so it MUST run before the first push. If the branch was already pushed
   unlinked, linking requires a destructive delete+recreate at the same SHA — gate that
   on explicit user approval.

3. **Update the issue's "Link to plan" with accessible URLs** (right after the first
   push, when the branch + files exist on origin): rewrite the issue body's plan and
   decisions references to full blob URLs on the convention branch so reviewers can
   click straight through — NEVER bare repo-relative paths (those resolve against `main`
   and 404 pre-merge):

   ```
   gh issue edit <N> --body-file <updated-body>
   # links like https://github.com/<owner>/<repo>/blob/<type>/<N>-<slug>/specs/<plan-name>/plan.md
   ```

4. **Per-phase commit+push inside the Codex Verification Loop** — after each round and
   each fix, commit + push so the branch shows the plan's evolution:
   - after Codex Round 1 appends its verdict → `git commit -m "📝 docs(plan): record Codex spec-review round 1" -m "Refs #<N>"` → push
   - after Claude applies round-1 fixes → `git commit -m "📝 docs(plan): apply Codex round 1 fixes" -m "Refs #<N>"` → push
   - after Codex Round 2 → commit → push
   - after any final fix → commit → push
5. **Graceful skip**: if `command -v gh` fails / no remote / push errors, commit
   locally and SKIP the push (warn, continue) — never block planning. Mirrors the
   existing `gh`/Codex graceful-skip patterns.
6. **Branch linkage** stays Option B (refspec push, mangled local kept) — the existing
   Worktree Rule in `GIT-COMMIT-PR-MESSAGE.md` is unchanged. The branch is linked to the
   issue's **Development** panel via `createLinkedBranch` (step 2), so the issue shows
   the branch even before a PR exists.
7. **No `Co-Authored-By`** on any of these commits (dogfoods workstream A).

Edit `.claude/commands/build.md` (minimal):

- Note that the convention branch already exists on `origin` carrying the plan commits;
  `/build`'s `git push -u origin HEAD:refs/heads/<type>/<N>-<slug>` adds implementation
  commits on top (fast-forward) — it MUST NOT create a second branch and MUST open
  exactly ONE PR (`Closes #N`) whose diff therefore includes both the plan and the
  implementation. The graceful-skip / no-issue fallbacks are unchanged.
- Any file path `/build` writes into the PR body (or issue comments) must likewise be an
  **accessible GitHub URL** (blob URL on the head branch, or a commit-pinned permalink),
  not a bare repo-relative path — same rule as the issue "Link to plan".
- **Mirror the issue's metadata config on the PR.** Using the SAME `<type>`→label
  mapping variable as `/plan-w-team`, the `gh pr create` must set `--assignee @me` and
  `--label <type-label>`, and the body must carry `Closes #N`. **Ensure the label exists
  first** (idempotent `gh label create <type-label> --force`) so build self-heals on a
  fresh repo — answering "are labels created during build?": yes, build creates the
  type label if missing before applying it. `Closes #N` links the PR in the issue's
  Development panel and closes it on merge (no `createLinkedBranch` needed for the PR).
  All of this rides the existing graceful-skip when `gh`/remote/auth is unavailable.

### Skill Contracts (requirements about both Codex skills)

This plan documents the contracts the reworked workflow must respect. Neither skill
file is edited.

- **`spec-review` (plan phase)**: invoked via `codex exec -s workspace-write`; reads
  `plan.md` + sibling `decisions.md`; judges against a blocking-only bar; appends a
  per-round `### Round N — Verdict: approved|changes-requested` block **ONLY** under
  the `## Codex Findings` heading and edits nothing else. It **MUST NOT call `gh`** —
  the orchestrator (Claude) relays each verdict to the issue. Max 2 rounds. The
  `## Codex Findings` section is **Codex-owned**: Claude never writes there.
  Requirement: each per-phase push happens **after** the round that produced the
  appended findings, so the published branch reflects the gated plan.
- **`implementation-review` (build phase)**: invoked via `codex exec -s workspace-write`;
  reads `plan.md` + `decisions.md` + the working-tree diff (`git status --porcelain
--untracked-files=all`, `git diff`); **runs the plan's Validation Commands** and
  reports real PASS/FAIL; emits its per-round verdict as its **final CLI message only**
  — it writes no files and edits no source. Claude's builders apply fixes; Claude
  relays each verdict to the PR. Max 2 rounds.
- **Shared**: both run network-off (`workspace-write` disables network by default),
  are auto-discovered from `.agents/skills/`, and are invoked by naming them in the
  prompt (no `--skill` flag). Claude is the only actor that calls `gh`.

### Workstream C — `/ship` finish-merge command

A new slash command `.claude/commands/ship.md` closes the lifecycle: `/build` opens the
PR and **deliberately stops** (its guard: "never merge — the user merges"); `/ship` is
that explicit, user-invoked merge+cleanup step.

- **Invocation**: `/ship <PR#|branch>`. Resolve the target with `gh pr view <arg>`
  (accepts a PR number, URL, or branch name); with **no arg**, infer the PR from the
  current worktree's branch (`gh pr view --json …` on the upstream branch). Read the
  PR's number `#N`, head branch, and the linked issue.
- **Pre-merge guards (abort cleanly on any failure; never `--admin`/force-bypass)**:
  1. PR exists and is **open**.
  2. PR is **mergeable** (no conflicts) — `gh pr view --json mergeable,mergeStateStatus`.
  3. **CI not failing** — `gh pr checks` shows no failing required checks (pending →
     warn/ask; failing → abort).
  4. **No unpushed commits** in the worktree (`git status -sb` / compare HEAD to
     `@{upstream}`) — squash merges the _remote_ PR head, so unpushed local commits
     would be lost and then destroyed by worktree removal. Abort and tell the user to
     push (or discard) first.
  5. Show a one-line summary (PR title, #N, commit count, target `main`) and require
     **explicit confirmation** before proceeding.
- **Squash merge** with an explicit summary message (NOT GitHub's commit-concatenating
  default):

  ```
  gh pr merge <N> --squash --delete-branch \
    --subject "<emoji> <type>(<scope>): <PR-title desc>" \
    --body "$(printf '%s\n\n%s' '<concise 1–3 sentence summary from the plan Objective / PR Summary>' 'Closes #<N>')"
  ```

  The subject mirrors the PR title; the body is a short human summary + `Closes #<N>`;
  **no `Co-Authored-By`** (the guard hook would block it anyway). `--delete-branch`
  removes the remote branch; `Closes #N` closes the linked issue on merge.

- **Cleanup (after a confirmed merge)**: switch out of the worktree first (you cannot
  remove a worktree you're inside) → `git worktree remove <path>` → delete the mangled
  local branch (`git branch -D worktree-…`) → `git fetch --prune`. The recorded
  worktree path comes from the plan's `## Tracking` block.
- **Graceful skips**: if `gh`/remote/auth is unavailable, or the PR isn't found, abort
  with a clear message and change nothing. If the worktree was already removed, skip
  that step. Never leave a half-merged state silently — report exactly what happened.

## Relevant Files

Use these files to complete the task:

- `GIT-COMMIT-PR-MESSAGE.md` — (A) remove prose trailer line + the two example-block
  trailer lines; add one policy line. Optionally reword line 14's "...existing
  trailers". (B) Worktree Rule is unchanged (Option B retained).
- `.claude/settings.local.json` — (A) add the `hooks.PreToolUse` block.
- `.claude/commands/plan-w-team.md` — (B) add initial publish + per-phase commit/push
  - graceful skip; relax PLANNING-ONLY carve-out; reference the skill contracts.
- `.claude/commands/build.md` — (B) note the pre-existing plan branch; keep single-PR;
  add PR assignee/label/`Closes #N` config + on-demand label creation.
- `.claude/commands/plan-w-team.md`, `.claude/commands/build.md` — (B) also referenced
  by Workstream C: `/ship` reads the `## Tracking` block these write.
- `.agents/skills/spec-review/SKILL.md`, `.agents/skills/implementation-review/SKILL.md`
  — read-only references for the contracts; **not edited**.
- `specs/git-workflow-issue-pr-tracking/decisions.md` — historical audit log; **do NOT
  edit** (Option-A trailer mentions left untouched by decision).

### New Files

- `.claude/hooks/block-coauthor-trailer.sh` — the PreToolUse guard script (chmod +x).
- `ai-docs/claude-code-hooks.md` — deep Claude Code hooks reference (research output).
- `.claude/commands/ship.md` — (C) the `/ship <PR#|branch>` finish-merge command.

## Implementation Phases

### Phase 1: Foundation

(A) Research Claude Code hooks via `claude-code-guide` → `ai-docs/claude-code-hooks.md`.
In parallel, scrub `GIT-COMMIT-PR-MESSAGE.md`. (B) Draft the `plan-w-team.md` edits
(publish + per-phase loop + graceful skip) against the documented skill contracts.

### Phase 2: Core Implementation

(A) Create the executable hook script; wire `hooks.PreToolUse` into
`.claude/settings.local.json` (merge, don't replace). (B) Apply the `plan-w-team.md`
rework and the minimal `build.md` handoff note.

### Phase 3: Integration & Polish

Validate: hook payload simulations; `settings.local.json` valid JSON; repo grep clean;
policy line present; `plan-w-team.md` contains the publish + per-phase + graceful-skip
steps and references the skill contracts; `build.md` keeps a single PR on the existing
branch; the published `chore/1-...` branch exists on origin with the plan commits.

## Team Orchestration

- You operate as the team lead and orchestrate the team to execute the plan.
- You're responsible for deploying the right team members with the right context.
- IMPORTANT: You NEVER operate directly on the codebase. You use `Task` and `Task*`
  tools to deploy team members to do the building, validating, and testing.
- Communication is paramount; use the Task* tools to coordinate and track progress.
- Take note of the session id of each team member to reference them.

> Note: `.claude/agents/team/` does not exist in this repo, so team members map to
> built-in agent types (`claude-code-guide`, `general-purpose`).

### Team Members

- Builder
  - Name: `researcher-hooks`
  - Role: deep-research Claude Code hooks and write `ai-docs/claude-code-hooks.md`.
  - Agent Type: `claude-code-guide`
  - Resume: false
- Builder
  - Name: `builder-hook`
  - Role: scrub trailers from `GIT-COMMIT-PR-MESSAGE.md`, create the hook script, wire
    `.claude/settings.local.json`.
  - Agent Type: `general-purpose`
  - Resume: true
- Builder
  - Name: `builder-workflow`
  - Role: rework `.claude/commands/plan-w-team.md` (publish + per-phase commit/push +
    graceful skip + skill-contract references) and the `build.md` handoff note.
  - Agent Type: `general-purpose`
  - Resume: true
- Builder
  - Name: `validator`
  - Role: test the hook and verify all acceptance criteria + validation commands for
    both workstreams.
  - Agent Type: `general-purpose`
  - Resume: false

## Step by Step Tasks

- IMPORTANT: Execute every step in order, top to bottom. Each task maps directly to a
  `TaskCreate` call.
- Before you start, run `TaskCreate` to create the initial task list that all team
  members can see and execute.

### 1. Research Claude Code hooks → ai-docs

- **Task ID**: research-hooks
- **Depends On**: none
- **Assigned To**: researcher-hooks
- **Agent Type**: claude-code-guide
- **Parallel**: true
- Fetch authoritative Claude Code hooks docs: lifecycle (PreToolUse, PostToolUse,
  UserPromptSubmit, Notification, Stop, SubagentStop, PreCompact, SessionStart,
  SessionEnd), matchers, the stdin JSON payload schema (incl. `tool_name` /
  `tool_input.command` for Bash), output semantics (exit 0 / exit 2 / other; JSON
  `decision` / `permissionDecision`), `$CLAUDE_PROJECT_DIR`, settings precedence.
- Write `ai-docs/claude-code-hooks.md` incl. a section justifying `PreToolUse`.

### 2. Scrub trailers from GIT-COMMIT-PR-MESSAGE.md

- **Task ID**: scrub-trailers
- **Depends On**: none
- **Assigned To**: builder-hook
- **Agent Type**: general-purpose
- **Parallel**: true
- Remove the prose trailer line + the two trailer lines in the example commit block.
- Add ONE policy line (no hook internals), e.g.:
  `- Do **not** add a \`Co-Authored-By: Claude …\` trailer to commits or PRs — a message without it is correct as-is.`
- Optionally reword line 14's "groups the link with the existing trailers" → "groups
  the link in the footer". Leave the historical decision log untouched.

### 3. Create the PreToolUse hook script

- **Task ID**: create-hook-script
- **Depends On**: research-hooks
- **Assigned To**: builder-hook
- **Agent Type**: general-purpose
- **Parallel**: false
- Create `.claude/hooks/block-coauthor-trailer.sh` matching the "Hook script" shape;
  `chmod +x`. Confirm exit 2 blocks a PreToolUse call (per the research).

### 4. Wire the hook into settings.local.json

- **Task ID**: wire-settings
- **Depends On**: create-hook-script
- **Assigned To**: builder-hook
- **Agent Type**: general-purpose
- **Parallel**: false
- Merge the `hooks.PreToolUse` block (matcher `Bash`, command via `$CLAUDE_PROJECT_DIR`)
  into `.claude/settings.local.json` WITHOUT dropping `enabledPlugins` / `outputStyle`
  (or any `autoMode` block the user added). Verify valid JSON.

### 5. Rework /plan-w-team for publish + per-phase tracking

- **Task ID**: rework-plan-w-team
- **Depends On**: none
- **Assigned To**: builder-workflow
- **Agent Type**: general-purpose
- **Parallel**: true
- Edit `.claude/commands/plan-w-team.md`: relax the PLANNING-ONLY carve-out to allow
  committing plan artifacts + pushing the convention branch; add issue assignee
  (`--assignee @me`) + labels (`epic` + branch-`<type>` label) at issue creation; add the
  create-linked-branch step (`createLinkedBranch` from the issue, then push — so the
  branch shows in the issue's Development panel); update the issue "Link to plan" to
  accessible blob URLs after the first push; add the per-phase commit+push through the
  Codex Verification Loop; add the `gh`/push/GraphQL graceful-skip; keep Option B branch
  linkage; require no `Co-Authored-By` on plan commits; reference the `spec-review` /
  `implementation-review` skill contracts (this plan's Skill Contracts section).

### 6. Update /build handoff note

- **Task ID**: update-build-handoff
- **Depends On**: rework-plan-w-team
- **Assigned To**: builder-workflow
- **Agent Type**: general-purpose
- **Parallel**: false
- Edit `.claude/commands/build.md`: note the convention branch already exists on origin
  with the plan commits; `/build` pushes implementation on top of it and opens exactly
  ONE PR (`Closes #N`) — no duplicate branch/PR. The PR mirrors the issue's metadata
  config: `--assignee @me` + the branch-`<type>` label (using the same `<type>`→label
  mapping as `/plan-w-team`), ensuring the label exists first via idempotent
  `gh label create … --force` (so build creates labels on demand). Use accessible GitHub
  URLs for any file path in the PR body. Leave graceful-skip/no-issue fallbacks intact.

### 7. Create the /ship finish-merge command

- **Task ID**: create-ship-command
- **Depends On**: update-build-handoff
- **Assigned To**: builder-workflow
- **Agent Type**: general-purpose
- **Parallel**: false
- Create `.claude/commands/ship.md` per Workstream C: `/ship <PR#|branch>` (resolve via
  `gh pr view`, infer from current worktree branch when no arg); pre-merge guards (open +
  mergeable + CI not failing + no unpushed commits + explicit confirm; never `--admin`);
  `gh pr merge --squash --delete-branch` with an explicit summary `--subject`/`--body`
  (`Closes #N`, no `Co-Authored-By`); cleanup (switch out of worktree → `git worktree
remove` → delete local branch → `git fetch --prune`); `gh` graceful-skip. Use proper
  command frontmatter (description, argument-hint) per the repo's command house style.

### 8. Validate all

- **Task ID**: validate-all
- **Depends On**: research-hooks, scrub-trailers, create-hook-script, wire-settings, rework-plan-w-team, update-build-handoff, create-ship-command
- **Assigned To**: validator
- **Agent Type**: general-purpose
- **Parallel**: false
- Run all Validation Commands below; confirm acceptance criteria for all workstreams.
- Simulate PreToolUse payloads (trailer present → exit 2; clean → exit 0; non-git → exit 0).

## Acceptance Criteria

- (A) `GIT-COMMIT-PR-MESSAGE.md` has no example/prose trailers beyond the single policy
  line; a repo-wide grep for the two trailers matches ONLY the allowed files: the
  `GIT-COMMIT-PR-MESSAGE.md` policy line, the guard hook script
  `.claude/hooks/block-coauthor-trailer.sh` and its documentation
  `ai-docs/claude-code-hooks.md` (both of which necessarily reference the trailer in
  order to block / explain it), `specs/git-workflow-issue-pr-tracking/decisions.md`, and
  this plan's specs.
- (A) `.claude/hooks/block-coauthor-trailer.sh` exists, is executable, exits 2 for a
  `git`/`gh` payload containing `Co-Authored-By: Claude`, exits 0 for a clean payload,
  exits 0 for a non-git command.
- (A) `.claude/settings.local.json` is valid JSON, retains existing keys, and contains
  the `hooks.PreToolUse` entry pointing at the script.
- (A) `ai-docs/claude-code-hooks.md` exists and covers hook concepts, lifecycle, and
  the PreToolUse rationale.
- (B) `.claude/commands/plan-w-team.md` documents: relaxed PLANNING-ONLY carve-out;
  create-linked-branch (`createLinkedBranch` from the issue) then initial commit + push
  of `specs/<plan-name>/`; per-phase commit+push through the Codex loop;
  `gh`/push/GraphQL graceful-skip; no `Co-Authored-By` on plan commits; and the two
  skill contracts.
- (B) The convention branch is linked to the issue's **Development** panel (visible via
  `gh api graphql … issue.linkedBranches`); for a future run this happens at branch
  creation; for this retrofit run it requires the user-approved delete+recreate.
- (B) `.claude/commands/build.md` resumes the pre-existing convention branch and opens
  exactly one PR with `Closes #N` (no duplicate branch/PR).
- (B) Skill files are unchanged; the plan documents both contracts.
- (B) The issue's **Link to plan** uses accessible blob URLs on the convention branch
  (clickable; resolve to the real files), not bare repo-relative paths; the workflow
  docs require accessible GitHub URLs for any file path written into an issue/PR body.
- (B) The repo label set is complete (defaults reused + `epic`, `chore`, `refactor`,
  `perf`, `style`, `test` created); issue #1 is assigned to the owner and carries
  `epic` + `chore`; `/plan-w-team` docs require `--assignee @me` + `epic` + branch-type
  label on every epic it creates.
- (B) Both `/plan-w-team` and `/build` docs create labels on demand (idempotent
  `gh label create … --force`) before applying them, so a missing label never aborts.
- (B) `/build` docs require the PR to mirror the issue config: `--assignee @me`, the
  branch-`<type>` label (same mapping), and `Closes #N` (which links it in the
  Development panel) — graceful-skip when `gh` is unavailable.
- (B) This plan is published to `chore/1-remove-claude-trailers-add-guard-hook` on
  origin with per-phase commits (dogfood).
- (C) `.claude/commands/ship.md` exists with valid command frontmatter and documents:
  `<PR#|branch>` resolution (+ no-arg inference); the pre-merge guards (open, mergeable,
  CI not failing, no unpushed commits, explicit confirm, no `--admin`); squash merge with
  an explicit summary subject/body + `Closes #N` + no `Co-Authored-By`; and full cleanup
  (remote branch via `--delete-branch`, local branch, worktree) with `gh` graceful-skip.

## Validation Commands

Execute these commands to validate the task is complete:

- `grep -nE 'Co-Authored-By|Claude-Session' GIT-COMMIT-PR-MESSAGE.md` — expect at most the single policy line.
- `test -x .claude/hooks/block-coauthor-trailer.sh && echo OK` — script exists and is executable.
- `printf '{"tool_name":"Bash","tool_input":{"command":"git commit -m \"x\\n\\nCo-Authored-By: Claude <noreply@anthropic.com>\""}}' | .claude/hooks/block-coauthor-trailer.sh; echo "exit=$?"` — expect `exit=2`.
- `printf '{"tool_name":"Bash","tool_input":{"command":"git commit -m \"clean message\""}}' | .claude/hooks/block-coauthor-trailer.sh; echo "exit=$?"` — expect `exit=0`.
- `printf '{"tool_name":"Bash","tool_input":{"command":"echo Co-Authored-By: Claude"}}' | .claude/hooks/block-coauthor-trailer.sh; echo "exit=$?"` — non-git → expect `exit=0`.
- `uv run --no-cache python -c "import json,sys; json.load(open('.claude/settings.local.json')); print('valid json')"` — settings parses (use `uv`, never raw `python`, per AGENTS.md; `--no-cache` keeps it runnable under the implementation-review sandbox, where `~/.cache` is read-only).
- `test -f ai-docs/claude-code-hooks.md && echo OK` — research doc exists.
- `grep -nE 'git push -u origin HEAD:refs/heads|per-phase|graceful' .claude/commands/plan-w-team.md` — publish + per-phase + graceful-skip steps present.
- `grep -nE 'spec-review|implementation-review' .claude/commands/plan-w-team.md` — skill contracts referenced.
- `git rev-parse --abbrev-ref '@{upstream}'` — expect `origin/chore/1-remove-claude-trailers-add-guard-hook`; network-free confirmation that the worktree branch is published + tracking the convention ref. (The remote-existence check is an orchestrator/plan-time step in `/plan-w-team`, NOT a build-time Validation Command, since `implementation-review` runs these network-off.)
- `test -f .claude/commands/ship.md && echo OK` — the /ship command file exists.
- `grep -nE 'gh pr merge --squash|--delete-branch|git worktree remove|--admin' .claude/commands/ship.md` — squash + delete-branch + worktree cleanup present (and confirm `--admin` appears only in a "never use" context).
- `grep -nE '<PR#\\|branch>|gh pr view|gh pr checks|unpushed|Closes #' .claude/commands/ship.md` — invocation, guards, and issue-close documented.

## Notes

- The hook counters the harness default that injects `Co-Authored-By`; it does NOT
  touch the harness PR-body note `🤖 Generated with Claude Code` (out of scope).
- The hook's literal-string check covers the dominant `-m`/heredoc commit form; it does
  not cover editor-based or `-F <file>` message bodies (out of scope).
- No new libraries are required; the hook is dependency-free bash.
- Workstream B intentionally keeps Option B branch linkage; the Worktree Rule docs are
  NOT changed. The skill files are NOT modified — only documented.

## Codex Findings

_Pending Codex review. Codex-owned (the spec-review skill); Claude must not edit this section._

### Round 1 — Verdict: changes-requested

- **The settings JSON validation command violates the repo's Python runtime rule.** The `Validation Commands` section tells `/build` to run raw `python3 -c ...`, while the project instructions require Python commands to use `uv`. Recommend: change that validation command to `uv run python -c "import json,sys; json.load(open('.claude/settings.local.json')); print('valid json')"` in `Validation Commands`.

### Round 2 — Verdict: approved

The spec meets the blocking-issue bar with no findings remaining this round.

### Round 3 — Verdict: changes-requested

- **The validation commands conflict with the documented implementation-review contract.** The `Skill Contracts` section says `implementation-review` runs network-off and runs the plan's Validation Commands, but `Validation Commands` includes `git ls-remote --heads origin 'chore/1-remove-claude-trailers-add-guard-hook'`, which requires network access to the remote. Recommend: move the remote branch publication check out of the implementation-review Validation Commands into an orchestrator/manual publish check, or replace it with a network-free local check in `Validation Commands`.
- **The trailer cleanup objective contradicts the acceptance criteria.** The `Objective` says no repo file except the frozen historical decision log references the two trailers, but the acceptance criteria allow this plan's specs and `GIT-COMMIT-PR-MESSAGE.md` is required to retain a single `Co-Authored-By: Claude` policy line. Recommend: update the `Objective` to match the intended allowed references (`GIT-COMMIT-PR-MESSAGE.md` policy line, this plan's spec files, and the frozen historical decision log), or tighten the acceptance criteria to match the objective.

### Round 4 — Verdict: approved

The spec meets the blocking-issue bar with no findings remaining this round.
