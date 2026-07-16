---
description: Internal review of a build's branch diff — parallel read-only reviewer agents with confidence-filtered findings, plus a memory-sync check on the memory series (AGENTS.md, .claude/rules/, GIT-COMMIT-PR-MESSAGE.md). Invoked in-session (Skill tool) by the /harness-layer:harness-build lead; runs standalone on a PR or branch without posting anything.
argument-hint: [PR number | branch]
allowed-tools: Read, Grep, Glob, Agent, Bash(git *), Bash(gh pr view:*), Bash(gh pr diff:*), Bash(gh pr list:*), Bash(gh issue view:*), Bash(gh search:*)
---

# Harness Review

Review the diff at `TARGET` with parallel read-only reviewer agents, score every
finding for confidence, and return the consolidated findings to the caller. You are a
reviewer, not a fixer: you never edit files, post comments, or mutate GitHub state —
the caller (the `/harness-layer:harness-build` lead, or the user's session) applies
fixes and posts reports.

## Variables

TARGET: $ARGUMENTS — a PR number or branch. Empty → the current branch's diff against `origin/main`.
REVIEWED_HEAD_SHA: `git rev-parse HEAD` (or the PR head) — stated in the findings report.
MEMORY_FILES: the memory series — hub `AGENTS.md` (imported by `CLAUDE.md`), the rule files under `.claude/rules/`, and `GIT-COMMIT-PR-MESSAGE.md`.
CONFIDENCE_FLOOR: `80` — findings scoring below this are dropped.
REVIEWER_MODEL: `sonnet` — every reviewer agent; utility agents (eligibility, context, summary, scoring) run on `haiku`. Nothing above `sonnet` is spawned.

## Instructions

- **Read-only.** Use `gh` only to read (`pr view/diff/list`, `issue view`, `search`). Never post, comment, edit, or push.
- A draft PR is an expected input — this command runs inside builds. Never decline a review for draft state or absence of a prior review.
- Score findings honestly and drop what falls under `CONFIDENCE_FLOOR`; a short, real findings list beats a padded one. Pre-existing issues, linter-catchable nits, and likely-intentional changes are false positives.

## Workflow

1. **Eligibility** — Haiku agent: confirm `TARGET` resolves to a non-empty diff that warrants review (not closed/merged, not trivially empty). Ineligible → return the reason, stop.
2. **Context** — Haiku agent: list (paths only) the memory files and any `CLAUDE.md`/`AGENTS.md` relevant to the changed directories.
3. **Summary** — Haiku agent: summarize the change set.
4. **Review** — launch the reviewer agents in parallel on `REVIEWER_MODEL`, each returning findings with file:line, description, and reason:
   - **standards** — violations of `AGENTS.md`, `.claude/rules/*`, and `GIT-COMMIT-PR-MESSAGE.md`.
   - **bugs** — shallow scan of the changes themselves for real defects; no nitpicks.
   - **history** — bugs visible in light of `git blame`/log context for the touched lines.
   - **prior-art** — comments on earlier PRs touching these files that apply again.
   - **comment-accuracy** — changes contradicting code comments or making them stale.
   - **plan-fidelity** — when the branch carries a `specs/<name>/` plan folder: the diff vs spec.md, tasks.md, and (when present) implementation-notes.md — a divergence from the plan with NO implementation-notes entry is a finding; recorded deviations are conforming context, not findings. No plan folder → the lens reports nothing.
   - **memory-sync** — see `Memory Sync` below.
5. **Score** — one Haiku agent per finding: 0–100 confidence that it is real and introduced by this diff; verify cited memory/rule text actually says what the finding claims.
6. **Filter & consolidate** — drop findings under `CONFIDENCE_FLOOR`, merge duplicates sharing a root cause, order by severity.
7. **Return** — follow `Report`.

## Memory Sync

The memory series holds the repo's durable conventions; a
diff that changes what it documents must update it in the same branch. `AGENTS.md`
is the hub — `CLAUDE.md` only `@`-imports it. Ownership map:

- **AGENTS.md** — agent and pipeline conventions, plus a pointer to every rule.
- **`.claude/rules/`** — that topic's series (hooks → `harness-layer/hooks.md`, Python → `python/general-practice.md`, models → `model-selection.md`, orchestration → `task-tools.md`, memory authoring → `memory-series.md`).
- **GIT-COMMIT-PR-MESSAGE.md** — git, PR, and issue policy.
- A genuinely new convention series → a new rule file under `.claude/rules/` (domain folder if path-scoped, flat root if global), referenced from `AGENTS.md` — contract in `.claude/rules/memory-series.md`.

The memory-sync reviewer maps each gap to its owner file above and tags severity so
the caller can route it:

- **Blocking** — the diff falsifies a documented statement (name the file and the now-wrong passage); or it establishes an explicit new repo-wide convention with no memory home (propose the owning file per the map).
- **Advisory** — an inferred or one-off convention with no home; or memory in the wrong home — written into `CLAUDE.md` (which only `@`-imports `AGENTS.md`), or duplicated across files (point to the single correct home).

## Report

Return to the caller (no posting):

```text
Reviewed: <TARGET> @ <REVIEWED_HEAD_SHA>
Findings: <N> (of <M> raw, ≥<CONFIDENCE_FLOOR> confidence)

1. [<lens>, <score>] <file>:<line> — <finding>. Fix: <concrete fix>.
2. ...

Memory sync: <clean | N findings above, each tagged blocking or advisory>
```

No findings → `Findings: 0` with the eligibility and lens list confirmed — never
invent findings to pad the report.
