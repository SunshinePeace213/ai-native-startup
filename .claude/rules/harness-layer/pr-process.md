---
paths:
  - ".github/**/*"
  - "specs/**/*"
---

# PR & Issue Process

Ship-time conventions: PR templates, issue forms, labels, linking, and status
comments. Commit format, branching, and the worktree push refspec live in
[git-workflow.md](../git-workflow.md).

## Pull Request Requirements

- Use **one PR template per commit type**. The 8 templates live under `.github/PULL_REQUEST_TEMPLATE/`: `feat.md`, `fix.md`, `docs.md`, `style.md`, `refactor.md`, `perf.md`, `test.md`, `chore.md`.
- Every template runs `## Summary` → `## Plan` → its type-specific sections (`feat` carries Breaking-changes + Screenshots; `fix` carries Root-cause + Regression-test) → a **shared tail that is byte-identical across all 8**: `## Test Evidence`, `## Risk & Rollback`, `## Agent Task Manifest`, `## Build Status`, `## Review Reports`, `## Dev Notes`, `## Follow-ups`. Edit the tail in one → edit all 8 in the same commit, and keep the section set matching what the pipeline commands write. `tests/harness-layer/test_pr_templates.py` fails on either drift.
- `/harness-layer:harness-build` opens a **draft** PR right after the tidy checkpoint, filling the body from the matching template with `gh pr create --draft --body-file <type>.md` (not `--template`).
- PR title carries the emoji to mirror the commit, e.g. `✨ feat(api): user login`.
- The PR body carries `Closes #N` — the PR is the **only** artifact that closes an issue.
- Fill out the Summary and Test Evidence, and keep the linked-issue line accurate.
- The PR body carries the **stage table** (`## Build Status`, Implementation → Ready) and the **Agent Task Manifest** table (copied from `TaskList`) — the single durable audit point for the ephemeral Agent Tasks. Manifest task IDs stay bare kebab-case; a `#N` there autolinks to an unrelated issue.
- Each review posts a **marker comment** — `<!-- report:tidy -->`, `<!-- report:codex-round-N -->` — upserted in place (never stacked), each stating the reviewed head SHA; the `Review Reports` section links them.
- The PR flips from draft to **ready only when its head commit equals the Codex-approved SHA**, recorded in the `## Build Status` **Ready** row's Evidence cell; `/harness-layer:harness-ship` reads that cell and merges with `gh pr merge --squash --match-head-commit <approved-sha>` (no local squash-merge), so a wrong value aborts the merge.
- Bypass tokens (`[skip-ci]`, `[skip-drift-check]`) belong in the PR title only when a workflow or hook actually consumes them — none exists in this repo today, so leave them off. They also ride into the squash-commit subject, which is capped at 72 characters.
- If modifying user-facing UI, include structural text maps or mock descriptions.

## Issue Requirements

- Use the curated set of **4 issue forms** (GitHub issue-forms YAML) under `.github/ISSUE_TEMPLATE/`, plus `config.yml`:
  - `feature.yml` — feature request (problem, solution, acceptance criteria).
  - `bug.yml` — bug report (repro, expected/actual, severity, environment).
  - `chore.yml` — maintenance umbrella covering `refactor` / `perf` / `style` / `test` / `build` / `ci` / `docs`.
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

## Idempotent Marker Comments

Status comments the harness posts on an issue or PR — plan-links, Codex round digests, review reports — must **upsert in place, never stack**. Each is keyed by a stable first-line HTML marker (e.g. `<!-- plan-links -->`, `<!-- codex-spec-round-N -->`, `<!-- report:codex-round-N -->`). To upsert one:

1. Write the body to a file first — `gh api` has no `--body-file`.
2. Find it: `gh api --paginate repos/{owner}/{repo}/issues/<N>/comments` and search for the marker (the same endpoint serves issues and PRs).
3. Found → update in place: `gh api --method PATCH repos/{owner}/{repo}/issues/comments/<comment-id> -F body=@<file>`.
4. Not found → create: `gh issue comment <N> --body-file <file>` (or `gh pr comment <N> --body-file <file>`).
