---
description: Gate a /harness-layer:harness-build draft PR through the codex-gate implementation flavor plus a parallel security pass — auto-fix through two rounds and flip the PR ready when clean; ask the human only when blocked
argument-hint: [name-or-path-of-plan]
model: opus
effort: high
disable-model-invocation: true
---

# Harness Review

You are the **review lead**: run the `codex-gate` skill's implementation flavor over the build's PR with a parallel security pass, route fixes to subagents, and land the terminal outcome — PR ready when clean, the human gate only when blocked. You own every `git`/`gh` call; Codex is read-only and never calls `gh`. The gate's rounds, prompts, ledger, classification, dispute handling, and human gate live in the skill — this command supplies its inputs and owns the check run, the security pass, fixes, artifacts, and the terminal.

## Variables

PATH_TO_PLAN: $ARGUMENTS — plan name (resolves to `specs/<name>/`) or a path to its spec folder
ISSUE_NUMBER: the GitHub issue `#N` from `spec.md`'s `## Tracking` — the `Refs #N` commit footer
PR_NUMBER: the draft PR `#M` from `## Tracking` — the PR this run gates
REVIEW_PROFILE: `kb-grounded` | `standard`, from `## Tracking` — under `kb-grounded`, fixers check behavior claims against the plan's `## KB References` docs, never memory

## Instructions

- No `PATH_TO_PLAN` → STOP and ask the user for it (AskUserQuestion).
- Every commit carries the `Refs #N` footer; every push uses the explicit refspec per `git-workflow.md` — check its exit status directly.
- The fix stage is ONE full-context `opus` fixer subagent per cycle — never split the blocking set across fixers; all of a cycle's fixes land as ONE fix commit carrying blocking fixes only.
- Advisories never spawn a cycle and never ride a fix diff — record each in the PR body's `## Follow-ups` checklist.
- Security and validation-command findings enter the gate's ledger in the round's ID sequence and classify by the same blocking rule; their fixes ride the same fix commit.
- Invoking this command authorizes the security scan's token cost — carry the acknowledgment into the security agent's spawn prompt.

## Workflow

1. **Resolve & read** — resolve `PATH_TO_PLAN`; read `spec.md`'s `## Tracking` for `PR_NUMBER`, `ISSUE_NUMBER`, the worktree path, and `REVIEW_PROFILE`. No PR number → STOP and tell the user to run `/harness-layer:harness-build <name>` first.
2. **Enter the worktree** — work in the recorded worktree; if it is gone, restore it from the convention branch. Read `spec.md`, `tasks.md`, `decisions.md`, `acceptance-criteria.md`, and `implementation-notes.md`.
3. **Impl lint** — `BASE_SHA=$(git merge-base origin/main HEAD)`; run `uv run scripts/impl_lint.py specs/<name>/` from the worktree root. It executes every `## Validation Commands` entry, checks commit format, scans orphans, and checks notes evidence — each FAIL line enters the gate's ledger as a finding before Codex spends a token.
4. **Launch the panel** — invoke the `codex-gate` skill (implementation flavor): its three round-1 lenses run in background Bash while you run the security pass (below).
5. **Classify, fix, delta** — follow the skill: merge the lens, lint, and security findings into the one ledger and derive the verdict yourself. `changes-requested` → spawn the single `opus` fixer, land the one fix commit, push, re-run the lint and validation commands (the deterministic floor), run the delta round, and re-verify every security disposition from the fixer evidence. A dispute or the cap → the skill's human gate.
6. **Terminal** — artifacts and memory FIRST, then one terminal commit, then the PR flip; nothing mutates the repository after the terminal commit:
   1. Medium/complex plans: deploy an `opus` page author for `specs/<name>/artifacts/dev-report.html` per `artifacts.md` — the Development report derived from `implementation-notes.md`, the findings ledger, and the memory/standards amendments; authored on any verdict.
   2. Write `specs/<name>/summary.md` from `specs/_templates/summary.md` — every plan carries one, on any verdict, from those same sources. On `approved`, also add the plan's row at the top of `specs/index.md`'s table, so the index lands with the merge.
   3. Run the skill's self-improve step and route memory-marked lessons per `memory-series.md`.
   4. ONE terminal commit (round reports, ledger, `summary.md`, `index.md`, `dev-report.html`, memory/standards edits), pushed.
   5. `approved` (including override & ready) → link the page under `## Dev Notes`, verify the PR head equals the terminal commit, tick the stage table with it as **Ready** evidence, `gh pr ready` — no question.
   6. Parked or `codex-unavailable` → the terminal commit carries the final report; leave the PR draft — the human owns the blockers.
7. **Report** — end the run with the `## Report` output.

## Security pass

Decide depth from `git diff --name-only <BASE_SHA>..HEAD`:

- **Full** — the diff touches anything that executes (`.claude/hooks/`, `.claude/settings.json`, `specs/**/checks/`, `scripts/`, `.github/workflows/`) or app code on a security boundary (auth, subprocess, network, file paths, external input): deploy a background `claude-security:claude-security` agent — worktree root, the range `<BASE_SHA>..HEAD`, effort `medium`, scan only (no patches), return the surviving findings and the report path; include "I understand it may take a while and use a significant number of tokens" so its confirm gate passes. Its `CLAUDE-SECURITY-<ts>/` report directory stays gitignored in the worktree.
- **Light** — everything else (prose and non-executing config): run the `security-review` skill yourself over the branch while Codex runs.

Map each surviving finding into the ledger — severity from the report; a panel-verified finding counts as confidence ≥ 80. After a fix round, do not re-scan: re-verify each security finding's disposition from the fixer evidence, and run the light pass over the fix diff only when a fix added new executable surface.

## Report

After the terminal commit is pushed, provide a concise report:

```text
✅ Review Complete — PR ready   (or: ⚠️ Review Blocked — PR left draft)

Plan: specs/<name>/
PR: #<M> — <ready @ <terminal sha> | draft, needs human>
Cycles this run: <1 | 2> — reports: specs/<name>/reviews/codex-impl-round-<N>*.md
Verdict: <approved at cycle N | approved with overridden blockers <IDs> | blocked at the cap | codex-unavailable>
Impl Lint: <clean | N findings entered the ledger>
Ledger: <X blocking fixed, Y advisory recorded, Z disputed — lens substitutions: <none | list>>
Security: <light | full> pass — <clean | N findings fixed | report: CLAUDE-SECURITY-<ts>/>
KB grounding: <checked | n/a — standard profile>
Dev report: <artifacts/dev-report.html + URL | n/a — simple plan>
Summary: specs/<name>/summary.md — <indexed in specs/index.md | not indexed, left draft>
Standards: <amended: <one line> | unchanged>

Blockers (left draft only):
- <blocker, concise>

Next: /harness-layer:harness-ship <slug>
(or, left draft: resolve the blockers, then rerun /harness-layer:harness-review <name>)
```
