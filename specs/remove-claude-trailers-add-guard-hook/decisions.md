# Decisions: Trailer cleanup + guard hook + /plan-w-team publish-and-track workflow rework

## Summary

Two folded-together workstreams. **A — Trailer cleanup + guard hook**: strip the two
Claude attribution trailers from the repo's message standard, add a `PreToolUse` hook
(external script + `.claude/settings.local.json`) that blocks `git`/`gh` commands
carrying `Co-Authored-By: Claude`, research hooks → `ai-docs/`, and reduce
`GIT-COMMIT-PR-MESSAGE.md` to one policy line. **B — `/plan-w-team` rework**: make
`/plan-w-team` commit `plan.md`/`decisions.md` and push the convention branch so the
plan is reviewable on GitHub, with **per-phase commit+push** through the spec-review
loop (mirroring `/build`); document the `spec-review` and `implementation-review` skill
contracts (skill files NOT modified); `/build` resumes the same branch and opens one
PR. This plan is itself published to `chore/1-...` with per-phase commits as the dogfood.

## Tracking

- **Issue**: `#1` (https://github.com/SunshinePeace213/ai-native-startup/issues/1).
  Initially blocked by auto-mode's `External System Writes` soft-deny (publishing under
  the user's identity); the create was cleared via explicit user intent, and the user
  added an `autoMode.allow` rule to the main-repo `.claude/settings.local.json`.
- **Branch**: `chore/1-remove-claude-trailers-add-guard-hook` (Option B: mangled local
  worktree branch, pushed to this remote ref with `-u`).
- **Worktree**: `/home/ringo/ai-native-startup/.claude/worktrees/remove-claude-trailers-add-guard-hook`

## Resolved Decisions

### Workstream A — trailer cleanup + guard hook

- **Q: Hook enforcement behavior?** A: **Block & instruct.** `PreToolUse` denies the
  `git`/`gh` command (exit 2) + stderr guidance; Claude removes the trailer and retries.
  Avoids fragile bash rewriting.
- **Q: Hook lifecycle?** A: **`PreToolUse`** — the only event that prevents the commit
  before it runs (PostToolUse is too late; Stop/SessionEnd can't intercept a tool call).
- **Q: Which trailer(s) does the hook block?** A: **Only `Co-Authored-By: Claude …`**.
  `Claude-Session` is removed from docs but not enforced.
- **Q: Touch the historical decision log?** A: **No** — frozen audit record.
- **Q: Hook logic location?** A: **External script** `.claude/hooks/block-coauthor-trailer.sh`
  referenced from `.claude/settings.local.json`.
- **Q: GIT-COMMIT-PR-MESSAGE.md change?** A: remove the prose + example trailer lines;
  add ONE policy line; no hook internals documented there.

### Workstream B — /plan-w-team publish + per-phase tracking

- **Q: Fold into this plan or a new plan?** A: **Fold into this plan** and re-run the
  `/plan-w-team` flow on the expanded plan (user choice).
- **Q: What does /plan-w-team publish at plan time?** A: **Commit `plan.md`/`decisions.md`
  and push the convention branch — NO PR.** `/build` opens the single PR later. (User
  revised an earlier "branch + draft PR" answer to "branch + push plan files, no PR".)
- **Q: Per-phase commit+push?** A: **Yes** — `initial plan → commit/push → Codex R1 →
commit/push → fix → commit/push → Codex R2 → commit/push → fix → commit/push`. Push
  happens AFTER each spec-review round so the published branch reflects the gated plan.
  Mirrors `/build`'s per-phase tracking.
- **Q: How does /build resume?** A: reuse the same worktree/branch (already carrying the
  plan commits), add implementation commits, open ONE PR with `Closes #1`. No second
  branch/PR.
- **Q: Branch linkage (EnterWorktree mangles the local branch)?** A: **Option B** —
  keep the mangled local branch, push to `refs/heads/<type>/<N>-<slug>` with `-u` for
  tracking. The clean name shows on GitHub; local stays cosmetic. (User first leaned
  toward Option A "rename for better management", then confirmed Option B after the
  trade-off analysis: same GitHub result, matches the repo's existing Worktree Rule,
  lowest risk, no doc churn. Worktree Rule docs unchanged.)
- **Q: spec-review / implementation-review skills — modify or document?** A: **Document
  - sequence only** (Option 1). Capture both contracts in the plan; do NOT edit the
    skill files; sequence each push after the round that produced its findings.
- **Q: Apply per-phase publish to THIS run now?** A: **Yes** — commit+push each phase
  to `chore/1-...` so the plan is reviewable on GitHub immediately (dogfood).

## Assumptions

- **Commits** follow `GIT-COMMIT-PR-MESSAGE.md`, carry **no `Co-Authored-By`** trailer
  (dogfoods workstream A), and use a `Refs #1` footer. Plan-doc commits use the `docs`
  type (`📝 docs(plan): …`) even though the branch type is `chore`.
- **Commit scope**: per-phase commits are scoped to `specs/<plan-name>/` only (via
  `git add specs/<plan-name>/`), never `git add -A`, to avoid sweeping in unrelated
  working-tree changes (e.g. the pending `settings.local.json` hook work, which is a
  build task).
- **Graceful skip**: if `gh`/remote/push is unavailable, commit locally and skip the
  push — never block planning. Mirrors the existing `gh`/Codex graceful-skip patterns.
- **Pushing a feature branch** (`chore/1-...`, not the default branch) to the repo's own
  trusted remote is expected to pass auto-mode; explicit user intent ("publish now")
  also clears it.
- **Settings file**: the hook is wired into `.claude/settings.local.json` (tracked in
  this repo); the merge must preserve any `autoMode` block the user added.
- **Research output**: `ai-docs/claude-code-hooks.md` (new file).

## Open Questions / Out of Scope

- **Out of scope**: the harness PR-body note `🤖 Generated with Claude Code` (not one of
  the two named trailers).
- **Out of scope**: editor-based commits / `-F <file>` message bodies (the literal-string
  PreToolUse check covers the dominant `-m`/heredoc form).
- **Out of scope**: editing the `spec-review` / `implementation-review` skill files, the
  Worktree Rule docs (Option B retained), and the frozen historical decision log.
- **Note**: issue #1's title still reads as the trailer chore; its scope expanded to
  include the workflow rework. Updating the issue title/body is optional and left to the
  user (avoids extra `gh` writes).

## Codex Verification

<!-- Updated after the Codex spec-review loop re-runs on the expanded plan. -->

- **Prior (pre-expansion) outcome**: approved at round 2 (R1 flagged a raw-`python3`
  validation command → fixed to `uv run python`). No findings rejected.
- **Post-expansion**: re-running spec-review on the expanded plan; outcome recorded here
  after the loop completes.
