# Acceptance Criteria: Standardize /plan-w-team issue tracking

> The definition of "done" for [spec.md](./spec.md). Every criterion is observable and testable, and
> every task in tasks.md should map to at least one criterion here.

## Acceptance Criteria

- **AC1** — The Epic template is renamed `epic-plan.md` → `epic-spec.md` with history preserved: `.github/ISSUE_TEMPLATE/epic-spec.md` exists, `.github/ISSUE_TEMPLATE/epic-plan.md` does not, `git status` shows a rename (`R`), and the frontmatter still carries `name: Epic / Plan` and `title: "📋 epic: "`.
- **AC2** — `epic-spec.md`'s body contains, in order, the sections `## Objective`, `## Non-Goals`, `## Lifecycle`, `## Link to plan`, `## Spec-review status`, `## Acceptance criteria`, `## Open Questions`, `## How to act`; the `## Spec-review status` section has `Latest verdict`, `Status`, and `History` lines; the `## Lifecycle` line contains `Plan ▸ Spec-review ▸ Approved ▸ Build ▸ Ship ▸ Done`; and there is NO `Child task checklist` section.
- **AC3** — `.claude/commands/plan-w-team.md` references `epic-spec.md` (and no longer `epic-plan.md`), standardizes the issue title as `📋 epic: <…>`, instructs path-as-text markdown plan links (not bare URLs / not `plan.md`), and documents all three body-sync touchpoints (publish-fill, per-round Spec-review-status update, loop-settle Status + Lifecycle), each with a graceful-`gh` skip.
- **AC4** — `.claude/commands/plan-w-team.md` contains both canonical snippets: the verdict relay-comment block (header `### 🔍 Codex spec-review — Round N`) and the `## Spec-review status` state-mirror block (the `Latest verdict` / `Status` / `History` lines).
- **AC5** — All eight `.github/PULL_REQUEST_TEMPLATE/*.md` seed the identical 7-item Build Status — `Implementation`, `Internal check`, `Claude code review`, `Codex review R1`, `Fixes`, `Codex review R2`, `Result` — with no 5-item list remaining.
- **AC6** — No **runtime/implementation** file references the old filename `epic-plan.md`: the stale-reference check covers `.github/`, `.claude/`, and `.agents/` only (the plan folder `specs/plan-w-team-issue-tracking/` legitimately mentions `epic-plan.md` as historical context describing the rename, so it is excluded by design). `config.yml` is unchanged and still references only `feature.md`/`bug.md`.

## Validation Commands

Run these from the worktree root. Map each command to the criteria it verifies.

- `test -f .github/ISSUE_TEMPLATE/epic-spec.md && ! test -f .github/ISSUE_TEMPLATE/epic-plan.md && echo "AC1 rename OK"` — verifies **AC1** file move. Pass = prints `AC1 rename OK`.
- `git -c core.quotepath=false status --porcelain .github/ISSUE_TEMPLATE | grep -E '^R' && echo "AC1 git-rename OK"` — verifies **AC1** rename is tracked as a rename, not add+delete.
- `grep -qE '^name: Epic / Plan$' .github/ISSUE_TEMPLATE/epic-spec.md && grep -qE '^title: "📋 epic: "$' .github/ISSUE_TEMPLATE/epic-spec.md && echo "AC1 frontmatter OK"` — verifies **AC1** preserved frontmatter.
- `grep -E '^## (Objective|Non-Goals|Lifecycle|Link to plan|Spec-review status|Acceptance criteria|Open Questions|How to act)$' .github/ISSUE_TEMPLATE/epic-spec.md` — verifies **AC2** the eight sections exist (expect 8 lines).
- `grep -q 'Plan ▸ Spec-review ▸ Approved ▸ Build ▸ Ship ▸ Done' .github/ISSUE_TEMPLATE/epic-spec.md && grep -qi 'Latest verdict' .github/ISSUE_TEMPLATE/epic-spec.md && grep -qi 'History' .github/ISSUE_TEMPLATE/epic-spec.md && echo "AC2 fields OK"` — verifies **AC2** Lifecycle line + Spec-review-status fields.
- `! grep -qi 'Child task checklist' .github/ISSUE_TEMPLATE/epic-spec.md && echo "AC2 no-child-checklist OK"` — verifies **AC2** the dropped section is gone.
- `grep -q 'epic-spec.md' .claude/commands/plan-w-team.md && ! grep -q 'epic-plan.md' .claude/commands/plan-w-team.md && echo "AC3 reference OK"` — verifies **AC3** the template reference was updated.
- `grep -qiE 'Spec-review status' .claude/commands/plan-w-team.md && grep -qiE 'path-as-text|display text' .claude/commands/plan-w-team.md && echo "AC3 touchpoints OK"` — verifies **AC3** the body-sync + link instructions are present.
- `grep -q '### 🔍 Codex spec-review — Round' .claude/commands/plan-w-team.md && echo "AC4 relay-comment OK"` — verifies **AC4** the relay-comment snippet.
- `for f in .github/PULL_REQUEST_TEMPLATE/chore.md docs.md feat.md fix.md perf.md refactor.md style.md test.md; do c=$(grep -cE '^- \[ \] (Implementation|Internal check|Claude code review|Codex review R1|Fixes|Codex review R2|Result)$' ".github/PULL_REQUEST_TEMPLATE/$(basename $f)"); echo "$f=$c"; done` — verifies **AC5**: every file must print `=7`.
- `! grep -rn 'epic-plan.md' .github .claude .agents 2>/dev/null && echo "AC6 no-dangling-ref OK"` — verifies **AC6** no stale filename reference in the runtime surfaces (the plan folder is intentionally excluded — it documents the rename).
- `grep -q 'feature.md' .github/ISSUE_TEMPLATE/config.yml && ! grep -q 'epic-plan' .github/ISSUE_TEMPLATE/config.yml && echo "AC6 config OK"` — verifies **AC6** `config.yml` untouched/clean.
