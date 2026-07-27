# Git Workflow

Branching, commits, and pushing. PR templates, issue forms, labels, linking, and
marker comments live in [pr-process.md](harness-layer/pr-process.md) — read it
before opening a PR or creating an issue.

## Branching Strategy

- Always branch from `main`.
- Branch name convention: `<type>/<issue#>-<slug>` (e.g. `feat/42-auth-endpoint`).
- Allowed types: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `chore`.
- Keep branches tightly scoped to a single task or issue.
- **Create the issue first** — issue creation is mandatory at plan time (no deferred issues). Then link the branch to it: `gh issue develop <N> --base main --name <type>/<N>-<slug>` creates the branch already tied to issue #N.
- The `<issue#>` is the GitHub issue number — the durable join key for the whole workflow. There is no Jira; the GitHub issue **is** the ticket.

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
