# Git Workflow & Pull Requests

## Branching Strategy

- Always branch from `main`.
- Branch name convention: `<type>/<issue#>-<slug>` (e.g. `feat/42-auth-endpoint`).
- Allowed types: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `chore`.
- Keep branches tightly scoped to a single task or issue.
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

- Use **one PR template per commit type**. The 8 templates live under `.github/PULL_REQUEST_TEMPLATE/`: `feat.md`, `fix.md`, `docs.md`, `style.md`, `refactor.md`, `perf.md`, `test.md`, `chore.md`. Each is tailored to its type (e.g. `feat` carries Breaking-changes + Screenshots; `fix` carries Root-cause + Regression-test; `docs` is minimal).
- `/build` selects the matching template with `gh pr create --template <type>.md`.
- PR title carries the emoji to mirror the commit, e.g. `✨ feat(api): user login`.
- The PR body carries `Closes #N` — the PR is the **only** artifact that closes an issue.
- Fill out the Summary and Test Plan, and keep the linked-issue line accurate.
- The PR body carries the **Agent Task Manifest** checklist (copied from `TaskList`) — the single durable audit point for the ephemeral Agent Tasks.
- If a task requires a bypass (e.g. emergency hotfix), carry over `[skip-ci]` or `[skip-drift-check]` tokens as required.
- If modifying user-facing UI, include structural text maps or mock descriptions.

## Issue Requirements

- Use the curated, tailored set of **4 issue templates** under `.github/ISSUE_TEMPLATE/`, plus `config.yml`:
  - `feature.md` — feature request (problem, solution, acceptance criteria).
  - `bug.md` — bug report (repro, expected/actual, environment).
  - `chore.md` — maintenance umbrella covering `refactor` / `perf` / `style` / `test` / `build` / `ci`.
  - `epic-plan.md` — epic/plan that links `specs/<feature>/plan.md` and carries a child checklist.
- A feature issue's **Acceptance Criteria become the Agent-Task success criteria** for the build — write them as verifiable checks.
- File **one issue per unit of intent**; the issue number threads the entire workflow.

## Model-C Linking & Reference Vocabulary

- **One GitHub issue per unit of intent.** Agent Tasks (the `Task*` orchestration list) stay **ephemeral / session-local** — they are not mirrored into GitHub as sub-issues.
- The **PR body carries an "Agent Task Manifest"** checklist copied from `TaskList` — the single durable audit point that ties the ephemeral tasks back to a permanent artifact.
- The **durable join key throughout is the GitHub issue number.**
- Reference vocabulary:
  - `Closes #N` — **PR body only**; closes the issue on merge.
  - `Refs #N` — commits and cross-references; links without closing.
  - `Part of #N` — a sub-task of an epic/plan issue.

## Worktree Rule

- Claude's `EnterWorktree` isolation **mangles the local branch name**: a worktree named `feat/x` produces local branch `worktree-feat+x`, not `feat/x`. The local branch name is therefore cosmetic.
- Name the worktree to match the intent (e.g. the feature slug).
- The `<type>/<issue#>-<slug>` convention is enforced on the **remote** branch via an explicit push refspec:

  ```bash
  git push -u origin HEAD:refs/heads/<type>/<N>-<slug>
  ```

- The **issue number recorded in the plan's `## Tracking` block is the source of truth** — never parse `#N` from the (mangled) local branch name.
- Base ref `fresh` (branches from `origin/main`) already satisfies "always branch from `main`".
