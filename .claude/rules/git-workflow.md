# Git Workflow & Pull Requests

## Branching Strategy

- Always branch from `main`.
- Branch name convention: `<type>/<issue#>-<slug>` (e.g. `feat/42-auth-endpoint`).
- Allowed types: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `chore`.
- Keep branches tightly scoped to a single task or issue.
- **Create the issue first** — issue creation is mandatory at plan time (no deferred issues). Then link the branch to it: `gh issue develop <N> --base main --name <type>/<N>-<slug>` creates the branch already tied to issue #N.
- The `<issue#>` is the GitHub issue number — the durable join key for the whole workflow (see Model-C Linking). There is no Jira; the GitHub issue **is** the ticket.

## Commit Message Rules

- Format: `<emoji> <type>(<scope>): <description>` — keep BOTH the gitmoji AND the Conventional-Commits `type:` word so commitlint/changelog tooling keeps parsing the type.
- The issue link goes in the **footer** as `Refs #N` — **never** in the subject line (keeps the subject ≤72 chars and groups the link in the footer).
- Subject rules:
  - Imperative mood (`add`, not `added`/`adds`).
  - Lowercase `type` and `scope`.
  - No trailing period.
  - First line ≤72 characters.
  - Use a **literal unicode emoji**, not a `:shortcode:` (write `✨`, not `:sparkles:`).
  - **Never** append a `Signed-off-by:` line on automated commits.
- Do **not** add a `Co-Authored-By: Claude …` trailer to commits or PRs — a message without it is correct as-is.

Emoji ↔ type table (all 8 allowed types — use exactly these):

| Emoji | Type | Use for |
| --- | --- | --- |
| ✨ | `feat` | a new feature |
| 🐛 | `fix` | a bug fix |
| 📝 | `docs` | documentation only |
| 🎨 | `style` | code structure/formatting, no logic change |
| ♻️ | `refactor` | code change that neither fixes a bug nor adds a feature |
| ⚡️ | `perf` | a performance improvement |
| ✅ | `test` | adding or correcting tests |
| 🔧 | `chore` | tooling, build, config, maintenance |

- `🎨` (`:art:`) is **deliberately** chosen for `style` — not `💄` (`:lipstick:`). In gitmoji `💄` means UI/CSS work, while `🎨` = "improve structure/format", which matches the Conventional-Commits `style` type (whitespace/formatting, no logic change).

Example commit:

```text
✨ feat(api): add user login endpoint

Implements JWT-based login with refresh-token rotation.

Refs #42
```

## Pull Request Requirements

- Use **one PR template per commit type**. The 8 templates live under `.github/PULL_REQUEST_TEMPLATE/`: `feat.md`, `fix.md`, `docs.md`, `style.md`, `refactor.md`, `perf.md`, `test.md`, `chore.md`. Each is tailored to its type (e.g. `feat` carries Breaking-changes + Screenshots; `fix` carries Root-cause + Regression-test) and all 8 share the stage table, Test Evidence, Risk & Rollback, Review Reports, and Reviewer Checklist.
- `/harness-layer:harness-build` opens a **draft** PR right after the first implementation checkpoint, filling the body from the matching template with `gh pr create --draft --body-file <type>.md` (not `--template`).
- PR title carries the emoji to mirror the commit, e.g. `✨ feat(api): user login`.
- The PR body carries `Closes #N` — the PR is the **only** artifact that closes an issue.
- Fill out the Summary and Test Evidence, and keep the linked-issue line accurate.
- The PR body carries the **stage table** (Implementation → Ready) and the **Agent Task Manifest** table (copied from `TaskList`) — the single durable audit point for the ephemeral Agent Tasks.
- Each review posts a **marker comment** — `<!-- report:tidy -->`, `<!-- report:codex-round-N -->` — upserted in place (never stacked), each stating the reviewed head SHA; the `Review Reports` section links them.
- The PR flips from draft to **ready only when its head commit equals the Codex-approved SHA**; `/harness-layer:harness-ship` then merges with `gh pr merge --squash --match-head-commit <approved-sha>` (no local squash-merge).
- If a task requires a bypass (e.g. emergency hotfix), carry over `[skip-ci]` or `[skip-drift-check]` tokens as required.
- If modifying user-facing UI, include structural text maps or mock descriptions.

## Issue Requirements

- Use the curated set of **4 issue forms** (GitHub issue-forms YAML) under `.github/ISSUE_TEMPLATE/`, plus `config.yml`:
  - `feature.yml` — feature request (problem, solution, acceptance criteria).
  - `bug.yml` — bug report (repro, expected/actual, severity, environment).
  - `chore.yml` — maintenance umbrella covering `refactor` / `perf` / `style` / `test` / `build` / `ci`.
  - `epic.yml` — epic/plan that links the `specs/<name>/` plan files and carries a child-issue checklist.
- Forms can't be submitted from the CLI, so `/harness-layer:harness-plan` fills the paired markdown skeletons under `specs/_templates/issues/` and creates the issue with `gh issue create --body-file`.
- A feature issue's **Acceptance Criteria become the Agent-Task success criteria** for the build — write them as verifiable checks.
- File **one issue per unit of intent**; the issue number threads the entire workflow.

## Labels

- Exactly **one type label** per issue, matching the change type: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `chore` (the old `enhancement` / `bug` / `documentation` labels are renamed to `feat` / `fix` / `docs`).
- Exactly **one `priority:P0`–`priority:P3`** label, chosen at creation (default `priority:P2`).
- `status:needs-human` is the **only** status label — apply it when a plan or build is flagged for human review; remove it when the flagged work later passes review.
- `epic` is orthogonal — it rides alongside the type + priority labels on an epic/plan issue.
- **Who applies them:** the agent path (`gh issue create` in the plan commands) attaches the full type + priority set at creation. Manual web-form submissions attach only the form's built-in labels (the type; `epic` for epics) — the maintainer completes the priority (and, for epics, the type) label at triage; GitHub issue forms cannot map a dropdown to a label.

## Model-C Linking & Reference Vocabulary

- **One GitHub issue per unit of intent.** Agent Tasks (the `Task*` orchestration list) stay **ephemeral / session-local** — they are not mirrored into GitHub as sub-issues.
- The **PR body carries an "Agent Task Manifest"** table copied from `TaskList` — the single durable audit point that ties the ephemeral tasks back to a permanent artifact.
- The **durable join key throughout is the GitHub issue number.**
- Reference vocabulary:
  - `Closes #N` — **PR body only**; closes the issue on merge.
  - `Refs #N` — commits and cross-references; links without closing.
  - `Part of #N` — a sub-task of an epic/plan issue.

## Worktree Rule

- Claude's `EnterWorktree(name: "<slug>")` names the local branch **`worktree-<slug>`**, which does not match the remote convention branch `<type>/<N>-<slug>`. The local branch name is therefore cosmetic.
- Name the worktree with the plan's kebab-case `<slug>`.
- The `<type>/<issue#>-<slug>` convention is enforced on the **remote** branch via an explicit push refspec:

  ```bash
  git push -u origin HEAD:refs/heads/<type>/<N>-<slug>
  ```

- **Every push from the worktree needs that explicit refspec**, not just the first: from the local `worktree-<slug>` branch a bare `git push` refuses (`push.default=simple` name mismatch). Check each push's exit status directly — piping push output into another command hides the failure.
- The **issue number recorded in the plan's `## Tracking` block is the source of truth** — never parse `#N` from the local `worktree-<slug>` branch name.
- Base ref `fresh` (branches from `origin/main`) already satisfies "always branch from `main`".
