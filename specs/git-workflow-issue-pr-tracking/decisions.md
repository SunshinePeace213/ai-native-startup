# Decisions: Git Workflow & Issue/PR/Commit + Agent-Task Lifecycle Tracking

## Summary

Establish a single, documented Git-workflow standard for this repo and wire it into
the two existing workflows (`/plan-w-team` and `/build`) plus their Codex review
gates. The standard covers gitmoji + Conventional-Commits messages, issue-numbered
branches, per-type PR and curated issue templates, and a "Model C" linking scheme
whose durable join key is the **GitHub issue number** (no Jira). Both workflows share
**one worktree, one branch, one issue, and one PR** end-to-end: `/plan-w-team` opens a
single Epic/Plan issue at draft and posts each Codex **spec-review** round as a
comment; `/build` resumes the same worktree, opens a single PR (`Closes #N`) on
completion, and posts each Codex **implementation-review** round as a Build-Status
update — never merging to `main` (the user merges). Codex stays verdict-only; Claude
relays verdicts to GitHub via `gh`. `AGENTS.md` is treated as user-owned: agents
produce a paste-ready `GIT-COMMIT-PR-MESSAGE.md` plus precise merge instructions, and the user
merges it **before** running `/build`. Enforcement is documentation-only — no
scripts, hooks, or CI.

## Resolved Decisions

### Commit messages

- **Q: Format?** A: `<emoji> <type>(<scope>): <description>`, with the issue link as
  `Refs #N` in the **footer** (not the subject). Rationale: keeps the subject ≤72 and
  groups the link with the existing Claude trailers; tooling still parses `type:`.
- **Q: Emoji ↔ type map (all 8 allowed types)?** A: ✨ `feat`, 🐛 `fix`, 📝 `docs`,
  🎨 `style`, ♻️ `refactor`, ⚡️ `perf`, ✅ `test`, 🔧 `chore`. Rationale: keep the
  Conventional-Commits `type:` word AND a decorative gitmoji (belt-and-suspenders) so
  changelog/commitlint tooling keeps working.
- **Q: 💄 or 🎨 for `style`?** A: 🎨 (`:art:`). Rationale: in gitmoji 💄 means UI/CSS
  work; 🎨 = "improve code structure/format", which matches Conventional-Commits
  `style` (whitespace/formatting, no logic change). Swapped from the 💄 shown during
  grilling, flagged to the user.
- **Q: Subject-line rules?** A: imperative mood, lowercase type/scope, no trailing
  period, first line ≤72 chars, never append `Signed-off-by`, **literal unicode**
  emoji (not `:shortcode:`). The global Claude trailers (`Co-Authored-By` /
  `Claude-Session`) remain in the footer, unaffected.
- **Q: Jira ticket?** A: No Jira. The **GitHub issue number is the ticket**; the
  original "extract ticket from branch" idea is realized with `#N`.

### Branching & worktrees

- **Q: Branch naming?** A: `<type>/<issue#>-<slug>` (e.g. `feat/42-auth-endpoint`).
  Changes the current `AGENTS.md` branching line.
- **Q: How does Claude's git-worktree isolation interact with the branch
  convention?** A (as approved): name the worktree to match the branch and treat the
  worktree as an isolated working dir; the branch/commits/PR behave as a normal
  checkout. **Amended after discovery (see Assumptions):** `EnterWorktree` mangles the
  local branch name (`feat/x` → `worktree-feat+x`), so the convention is enforced on
  the **remote** branch via an explicit push refspec, and the issue number is the
  recorded source of truth rather than parsed from the local branch. Base ref `fresh`
  (origin/main) already satisfies "branch from main".

### PR templates

- **Q: One template or many?** A: **One file per commit type — all 8** under
  `.github/PULL_REQUEST_TEMPLATE/` (`feat.md`, `fix.md`, `docs.md`, `style.md`,
  `refactor.md`, `perf.md`, `test.md`, `chore.md`), each with sections tailored to
  that type (e.g. `feat` has Breaking-changes + Screenshots; `fix` has Root-cause +
  Regression-test; `docs` is minimal). `/build` selects the matching file with
  `gh pr create --template <type>.md` (confirmed supported).
- **Q: Section pool?** A: Summary, Test Plan, linked issue, UI structural text-maps,
  Changes (bullet list), Reviewer checklist, Screenshots/recordings, Breaking changes
  & migration, **Agent Task Manifest**, **Build Status checklist** — each template
  includes the subset that fits its type.
- **Q: PR title format?** A: carries the emoji to match commits, e.g.
  `[PR] ✨ feat(api): user login`.
- **Q: Closing keyword?** A: `Closes #N` in the PR body — the PR is the **only**
  artifact that closes an issue. Carry over `[skip-ci]` / `[skip-drift-check]` bypass
  tokens.

### Issue templates

- **Q: Granularity?** A: **Curated tailored set of 4** under `.github/ISSUE_TEMPLATE/`
  — `feature.md`, `bug.md`, `chore.md` (umbrella for refactor/perf/style/test/build/
  ci), `epic-plan.md` — plus `config.yml`. Rationale: issues describe intent/problems,
  which collapse to feature/bug/chore + epic; standalone `style`/`perf` issues are
  awkward. Each template is uniquely tailored (not a shared skeleton). The Epic/Plan
  template links `specs/<feature>/plan.md` and carries a child checklist; issue
  acceptance criteria become Agent-Task success criteria.

### Linking model

- **Q: How do ephemeral Agent Tasks bind to durable issues?** A: **Model C — PR task
  manifest.** One GitHub issue per unit of intent; Agent Tasks stay ephemeral/
  session-local; the PR body carries an "Agent Task Manifest" checklist copied from
  `TaskList` as the single durable audit point. Durable join key throughout = the
  issue number. Reference vocab: `Closes #N` (PR only), `Refs #N` (commits/cross-
  refs), `Part of #N` (sub-task of an epic). Rejected: Model B (sub-issue per task —
  too much churn/glue) and "Issue is the spine" (no durable task trace).

### Enforcement / glue

- **Q: Automation level?** A: **Documented conventions only** — no scripts, git
  hooks, or CI. Rationale: the repo has no JS/husky toolchain; behavior is enforced by
  the standard + Claude following it. (`+ shell hooks` and `+ GitHub Actions` options
  were declined.)

### Workflow integration — `/plan-w-team`

- Create **one** Epic/Plan GitHub issue at the initial plan draft, **after** sign-off
  (title + objective known), **before** entering the worktree (issue-first ordering so
  the intended branch carries `#N`).
- Post each Codex **spec-review** round to that same issue as a comment (verdict +
  findings + what Claude fixed) — a single-issue chronological audit.
- Record the issue number, intended convention branch name, and worktree path in a
  `## Tracking` block in `plan.md` and in `decisions.md`, so `/build` can resume.
- `EnterWorktree` by default; planning files are written inside the worktree.

### Workflow integration — `/build`

- **Resume the same worktree** via `EnterWorktree(path=<recorded path>)`; run the
  whole build there.
- On completion, push the branch to the convention-named **remote** branch
  (`git push -u origin HEAD:refs/heads/<type>/<N>-<slug>`) and open **one** PR with the
  matching `--template`, `Closes #N`, and the Agent Task Manifest filled from
  `TaskList`.
- Surface per-phase status as a **live "Build Status" checklist in the PR body** plus
  **one `gh pr comment` per phase** (implementation done → Codex R1 → fixes → Codex R2
  → result). PR opens **ready** (no draft dependency; repo is public but we don't rely
  on it).
- **Never push to / merge `main`.** The PR stays open; the user decides to merge.

### Codex relay

- The Codex skills (`spec-review`, `implementation-review`) stay **verdict-only** and
  functionally unchanged (they emit `approved`/`changes-requested`); Codex runs
  sandboxed and does not touch GitHub. **Claude relays** each verdict to the issue/PR
  via `gh`. The two skill files get only a short note documenting that the orchestrator
  relays their verdict.
- **gh graceful degrade:** if `gh`/remote/auth is unavailable, **skip** the issue/PR
  integration, warn the user, and continue local-only — mirroring the existing Codex
  graceful-skip pattern. Never block planning/build on a missing `gh`.

### Output / AGENTS.md handoff

- Do **not** edit `AGENTS.md` (treated as user-owned; no settings-deny exists today,
  but the plan honors the constraint and notes an optional deny rule as out-of-scope).
- Produce a standalone **`specs/git-workflow-issue-pr-tracking/GIT-COMMIT-PR-MESSAGE.md`** that
  contains the paste-ready "Git Workflow & Pull Requests" sections **and** precise
  merge instructions (which `AGENTS.md` lines to replace/insert). The **user** merges
  it into `AGENTS.md` **before** `/build` runs, so the conventions are in builders'
  context.
- Plan name: `git-workflow-issue-pr-tracking`.

## Assumptions

- **Worktree branch mangling (discovered during planning).** `EnterWorktree(name="feat/
git-workflow-issue-pr-tracking")` produced local branch
  `worktree-feat+git-workflow-issue-pr-tracking`, not `feat/...`. Therefore: (a) the
  intended convention branch name and issue # are recorded explicitly and treated as
  the source of truth; (b) the convention is enforced on the **remote** branch via an
  explicit push refspec; (c) the local worktree branch name is cosmetic. Recorded as
  an assumption because it overrides the originally-approved "name worktree = branch =
  extract from branch" phrasing.
- Literal unicode emoji (not `:shortcode:`).
- The Epic/Plan issue is created with title + objective right after sign-off and its
  body updated to link `plan.md` once written.
- `gh` is authenticated (verified during planning: account `SunshinePeace213`).
- Validation of `config.yml` uses `uv run --with pyyaml python` (no project Python env
  assumed).
- Standalone doc lives at `specs/<plan-name>/GIT-COMMIT-PR-MESSAGE.md` (chosen over repo-root
  `docs/`).

## Open Questions / Out of Scope

- **No commitlint / husky / CI enforcement** — documentation-only this iteration.
- **No Jira integration** — the GitHub issue number is the ticket.
- **No auto-merge to `main`** — the PR is left open for the user.
- **No sub-issue-per-task (Model B)** — explicitly rejected.
- **No settings-level permission-deny on `AGENTS.md`** — optional follow-up, not built
  here.
- **No retroactive rewrite of existing commit history** — the standard applies going
  forward.
- Migrating existing open PRs/issues to the new templates is out of scope.

## Codex Verification

**Outcome: approved at round 2.**

- **Round 1 — changes-requested (1 finding, accepted).** Codex flagged that the
  graceful-`gh`-skip path produced no issue number, yet Step 4 still recorded one and
  Step 5 required `#N` for the push refspec and `Closes #N` — contradicting the locked
  "missing `gh` never blocks" decision. Resolution: amended Step 4 (record `Issue: none
— gh unavailable`, branch falls back to `<type>/<slug>`), Step 5 (skip PR creation/
  comments/Build-Status/`Closes #N` and print the manual `gh pr create` command when no
  issue number is present), and added a "No-issue fallback" Note making the
  `## Tracking` issue field the single source of truth.
- **Round 2 — approved.** No remaining blocking findings.
- No Codex findings were rejected.

## Amendment (post-plan, user-directed)

A user-approved design change made during build supersedes the **Output / AGENTS.md
handoff** decision above:

- **Single canonical doc at the repo root.** The standard now lives in one
  `GIT-COMMIT-PR-MESSAGE.md` at the **repo root**, promoted from the originally-planned
  `specs/git-workflow-issue-pr-tracking/GIT-COMMIT-PR-MESSAGE.md`. There is no longer a separate
  standalone copy inside the specs folder.
- **One-line AGENTS.md pointer, not a full paste.** The user chose to add a single
  one-line pointer in `AGENTS.md` referencing the root `GIT-COMMIT-PR-MESSAGE.md`, instead of
  pasting the full standard into the `AGENTS.md` "Git Workflow & Pull Requests" section.
- **Stray `.claude/rules/git-commit-pr.md` removed.** A `git-commit-pr.md` rule had been
  created outside the plan's scope; because `.claude/rules/*` auto-load into every
  session, it injected the standard automatically and thereby **bypassed the user-merge
  gate**. It was removed so the standard reaches builders only via the user-applied
  pointer.
- **AGENTS.md remains user-owned.** `AGENTS.md` is updated by the **user**, not by
  agents; agents still never edit it. The user applies the one-line pointer **before**
  running `/build`.
