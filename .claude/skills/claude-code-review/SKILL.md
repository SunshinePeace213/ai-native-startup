---
name: claude-code-review
description: >-
  Multi-lens Claude self-review of the working-tree diff (git diff
  origin/main...HEAD) against this repo's AGENTS.md standards, run during the
  /build "Claude code review" phase before the cross-model Codex gate. Ports the
  code-review plugin pipeline: an eligibility gate that skips trivial/docs-only
  diffs, 5 parallel Sonnet review lenses, then per-finding Haiku confidence
  scoring 0-100 keeping only findings >= 80. Use during /build, or whenever asked
  to self-review / code-review the current branch's changes against AGENTS.md
  before hand-off. Outputs two sinks — a concise, permalink-cited PR comment AND
  the filtered >= 80 findings returned to /build for the fix step. Edits no source.
---

# Claude Code Review

You are the intra-model code reviewer in the `/build` pipeline. You run **after**
the internal-check (code-simplifier) phase and **before** the cross-model Codex
review. Your job: review the branch's changes against this repo's written standards,
surface only high-confidence findings, and hand them back so `/build` can fix them —
you **edit no source yourself**.

This is a faithful port of the `code-review` plugin pipeline, retargeted from
`CLAUDE.md` to **AGENTS.md** (this repo's `CLAUDE.md` is literally `@AGENTS.md`, so
AGENTS.md is the real standard) and pointed at a **local diff** instead of a fetched
PR. Two additions over the plugin: the standards set is AGENTS.md + the global +
rules + commit standard, and findings feed a fix step (sink b) in addition to the PR
comment (sink a).

## Hard rules

- **Target diff:** review only `git diff origin/main...HEAD` (the branch's changes
  vs. `main`). Do not review unrelated files. Run `git fetch -q origin main` first so
  the three-dot range is accurate.
- **Edit no source.** You produce findings and a comment body; `/build` applies fixes
  and posts the comment (it owns every `git` and `gh` call).
- **Model aliases only.** Launch subagents with the aliases `haiku` and `sonnet` —
  NEVER a dated id like `claude-sonnet-4-6` or `claude-opus-4-8`.
- **No build/typecheck.** Do not build, typecheck, or run the app — CI runs those
  separately and they are not your concern.
- Make a todo list first.

## The standards files (what the review checks against)

Collect the **paths** (not the contents up front) of the written standards this repo
reviews against. These REPLACE the plugin's CLAUDE.md set:

- `AGENTS.md` — the project standard (Tooling & Runtime, Claude SDK best practice, Git
  workflow, project structure).
- `~/.codex/AGENTS.md` — the global engineering rules (Think-before-coding, Simplicity
  First, Surgical Changes, Goal-Driven Execution, model-judgment-only, token budgets,
  surface-conflicts, read-before-write, tests-verify-intent, checkpoint, fail-loud).
- `.claude/rules/*` — repo rules (e.g. `.claude/rules/task-tools.md`, the team
  orchestration protocol). Glob the directory; include every match.
- `GIT-COMMIT-PR-MESSAGE.md` — the commit / PR / issue / worktree standard.

Do **not** use `CLAUDE.md` as a standard — it is `@AGENTS.md` and adds nothing.

## Pipeline

Follow these steps precisely.

### 1. Eligibility gate

Use a **Haiku** agent to inspect the diff (`git diff --stat origin/main...HEAD` plus
the changed file list) and decide whether the change merits a review. Skip (do not
proceed) when the diff is:

- empty (no changes vs. `main`), or
- **docs-only / trivial** — only Markdown prose, comments, formatting, or otherwise
  obviously fine and too small to warrant a review.

If skipped, **STOP** and record `skipped — trivial diff` as the result; return zero
findings and a one-line note so `/build` ticks the phase and moves on. Otherwise
continue.

### 2. List the standards files

Use a **Haiku** agent to return the **paths** (not the contents) of the standards
files above that exist and are relevant to the directories the diff touches: always
`AGENTS.md`, `~/.codex/AGENTS.md`, `GIT-COMMIT-PR-MESSAGE.md`, and every `.claude/rules/*`
file. This path list is passed to every later agent.

### 3. Diff summary

Use a **Haiku** agent to read `git diff origin/main...HEAD` and return a short summary
of the change (what it does, which files, intent). This grounds the review lenses.

### 4. Five parallel Sonnet review lenses

Launch **5 parallel Sonnet agents** to independently review the change. Each returns a
list of issues, and for each issue **the reason it was flagged** (e.g. AGENTS.md
adherence, bug, historical git context, prior-PR comment, code-comment guidance):

- **Agent #1 — AGENTS.md adherence.** Audit the changes for compliance with the
  standards files from step 2 (AGENTS.md + `~/.codex/AGENTS.md` + `.claude/rules/*` +
  `GIT-COMMIT-PR-MESSAGE.md`). Note that these are guidance written for Claude as it
  writes code, so not every instruction is applicable during review — flag only real,
  specific violations the standards actually call out (e.g. raw `python`/`pip` instead
  of `uv`, raw `npm`/`npx` instead of `bun`, a dated model id instead of an alias, a
  `Co-Authored-By` trailer, an `rm -rf` instead of `mv … ~/.Trash/`, speculative
  abstractions or unrequested features per Simplicity-First / Surgical-Changes).
- **Agent #2 — shallow bug scan.** Read the file changes and do a shallow scan for
  obvious bugs. Avoid reading extra context beyond the changes; focus on the changes
  themselves. Focus on large bugs; avoid small issues and nitpicks. Ignore likely
  false positives.
- **Agent #3 — git history.** Read the `git blame` and history of the modified code to
  identify bugs in light of that historical context.
- **Agent #4 — prior PRs.** Read previous pull requests that touched these files and
  check for comments on those PRs that may also apply to the current change. If the
  repo has few or no prior PRs, this lens degrades gracefully to **no findings** — that
  is expected, not an error.
- **Agent #5 — code comments.** Read code comments in the modified files and make sure
  the changes comply with any guidance in those comments.

### 5. Per-finding Haiku confidence score (0-100)

For each issue found in step 4, launch a parallel **Haiku** agent that takes the diff,
the issue description, and the standards-file paths (from step 2), and returns a
**confidence score 0-100** for whether the issue is real or a false positive. For
issues flagged due to a standards-file instruction, the agent must double-check that
the standards file actually calls out that issue specifically.

Give the agent this rubric **verbatim** (only "CLAUDE.md" is retargeted to the
standards files / AGENTS.md, per this skill's purpose):

> a. **0: Not confident at all.** This is a false positive that doesn't stand up to
>    light scrutiny, or is a pre-existing issue.
> b. **25: Somewhat confident.** This might be a real issue, but may also be a false
>    positive. The agent wasn't able to verify that it's a real issue. If the issue is
>    stylistic, it is one that was not explicitly called out in the relevant standards
>    file (AGENTS.md / `~/.codex/AGENTS.md` / `.claude/rules/*` / GIT-COMMIT-PR-MESSAGE.md).
> c. **50: Moderately confident.** The agent was able to verify this is a real issue,
>    but it might be a nitpick or not happen very often in practice. Relative to the
>    rest of the change, it's not very important.
> d. **75: Highly confident.** The agent double checked the issue, and verified that it
>    is very likely a real issue that will be hit in practice. The existing approach in
>    the change is insufficient. The issue is very important and will directly impact
>    the code's functionality, or it is an issue directly mentioned in the relevant
>    standards file (AGENTS.md / `~/.codex/AGENTS.md` / `.claude/rules/*` /
>    GIT-COMMIT-PR-MESSAGE.md).
> e. **100: Absolutely certain.** The agent double checked the issue, and confirmed it
>    is definitely a real issue that will happen frequently in practice. The evidence
>    directly confirms this.

**Examples of false positives** (for steps 4 and 5 — apply these guardrails verbatim):

- Pre-existing issues.
- Something that looks like a bug but is not actually a bug.
- Pedantic nitpicks that a senior engineer wouldn't call out.
- Issues that a linter, typechecker, or compiler would catch (e.g. missing or incorrect
  imports, type errors, broken tests, formatting issues, pedantic style issues like
  newlines). No need to run these build steps yourself — assume CI runs them separately.
- General code quality issues (e.g. lack of test coverage, general security issues, poor
  documentation), unless explicitly required in the standards files (AGENTS.md etc.).
- Issues that are called out in a standards file but explicitly silenced in the code
  (e.g. via a lint-ignore comment).
- Changes in functionality that are likely intentional or directly related to the
  broader change.
- Real issues, but on lines the change did not modify.

### 6. Keep only findings >= 80

Filter out any issue with a confidence score **less than 80**. If no issues meet the
>= 80 bar, do not proceed to flag anything — record "no blocking findings" and emit the
clean PR comment.

### 7. Re-check eligibility

Use a **Haiku** agent to repeat the eligibility check from step 1, confirming the
change is still review-eligible (not trivial/docs-only). If it is no longer eligible,
record `skipped — trivial diff`.

## Outputs (two sinks)

You produce two artifacts and return them as your final message; you post nothing and
edit nothing — `/build` owns the `gh` call and the fix step.

### Sink (a) — the PR comment body

A concise, permalink-cited comment for `/build` to post with `gh pr comment`. Keep it
brief, avoid emojis in finding text, and link/cite each finding with a full-SHA GitHub
permalink. Format precisely (example for 3 findings):

```
### Code review

Found 3 issues:

1. <brief description> (AGENTS.md says "<...>")

<permalink to file + line range with full sha, e.g.
https://github.com/<owner>/<repo>/blob/<full-sha>/path/to/file#L13-L17>

2. <brief description> (.claude/rules/task-tools.md says "<...>")

<permalink with full sha>

3. <brief description> (bug due to <file and code snippet>)

<permalink with full sha>
```

If no findings survive the >= 80 filter:

```
### Code review

No issues found. Checked for bugs and AGENTS.md compliance.
```

Permalink format (otherwise the Markdown preview won't render):
`https://github.com/<owner>/<repo>/blob/<full-sha>/path/to/file#L10-L15`
- Requires the **full** git sha (the pushed HEAD of the PR branch) — never `$(git rev-parse HEAD)` substitution in the comment text; resolve the sha and write it literally.
- `#` after the file name; line range as `L<start>-L<end>`.
- Provide at least 1 line of context before and after the line in question.
- Cite and link every finding (if it cites a standards file, link that file too).

### Sink (b) — the >= 80 findings for /build

Return the filtered findings as a structured list `/build` can act on in its fix step.
For each: file path, line range, the reason flagged (which standard / why), the
confidence score, and a one-line fix suggestion. If none survived the filter, return an
empty list with the note "no blocking findings" (or "skipped — trivial diff" if the
eligibility gate fired). `/build` applies the fixes; you do not.

## Notes

- Cite and link each finding; if a finding refers to a standards file, link it.
- Keep output brief; avoid emojis in finding text.
- Use `gh` (not web fetch) for any GitHub lookups the lenses need (e.g. prior PRs).
- This skill never edits source, never builds/typechecks, and never posts to GitHub
  itself — it returns the comment body and the findings to `/build`.
