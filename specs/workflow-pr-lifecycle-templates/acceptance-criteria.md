# Acceptance Criteria: Unify the lifecycle on one PR + standardize workflow templates

> The definition of "done" for [spec.md](./spec.md). Every criterion is observable and testable, and
> every task in tasks.md should map to at least one criterion here.

## Acceptance Criteria

- **AC1** — `WORKFLOW-TEMPLATES.md` exists at repo root and is cited from `AGENTS.md`. It
  contains a section for each standardized output: PR body skeleton, Lifecycle line,
  Spec-review status block, Build Status block, Agent Task Manifest, per-phase PR comments,
  Codex relay (spec→issue **and** impl→PR), Claude→Codex invocation prompts, Codex→Claude
  verdict format, and the `/build` + `/ship` report layouts.
- **AC2** — The issue Lifecycle marker advances end-to-end: `plan-w-team.md` advances it to
  **Approved** on a Codex `approved` settle (as today), `build.md` instructs advancing it to
  **Build**, and `ship.md` instructs advancing it to **Done**. No command leaves the spine
  frozen at "Approved" through build/ship.
- **AC3** — `plan-w-team.md` opens a **draft PR at plan time** (a `gh pr create --draft`
  step after the first plan push) seeded with the unified body skeleton, and writes the
  spec-review verdict into the PR body's `## Spec-review status` block while keeping the
  issue authoritative.
- **AC4** — The Agent Task Manifest is sourced from `tasks.md` (grouped by phase, kebab
  IDs, each `satisfies AC#`) and contains **no bare `#<number>`** in any PR template or in
  the manifest description; `Closes #N` remains the only GitHub reference.
- **AC5** — `build.md` Phase 1 **resumes** the existing draft PR (with a documented
  fallback-create when absent) and **never opens a second PR**; its per-phase comments
  reference the catalog rather than inlining ad-hoc bodies.
- **AC6** — The Codex `implementation-review` relay to the PR uses a canonical comment
  defined in the catalog, at parity with the spec-review issue snippet (verdict line +
  blocking-finding count + fixes-this-round + a clickable Full-detail pointer).
- **AC7** — Stale refs fixed and live fallback retained: `GIT-COMMIT-PR-MESSAGE.md`
  contains no `epic-plan.md` and no `specs/<feature>/plan.md`; `ship.md` contains no
  "Workstream C"; **and** `build.md` still contains its legacy `plan.md` fallback.
- **AC8** — `plan-w-team.md`, `build.md`, `ship.md`, `spec-review/SKILL.md`, and
  `implementation-review/SKILL.md` each reference `WORKFLOW-TEMPLATES.md`, and
  `plan-w-team.md` no longer embeds a duplicate "Canonical issue snippets" block.

## Validation Commands

Run these to prove the criteria above. Map each command to the criteria it verifies. Run
from the repo/worktree root.

- `test -f WORKFLOW-TEMPLATES.md && grep -q 'WORKFLOW-TEMPLATES.md' AGENTS.md && echo PASS` — verifies **AC1** (catalog exists + cited). Pass = prints `PASS`.
- `for s in "PR body" "Lifecycle" "Spec-review status" "Build Status" "Agent Task Manifest" "invocation" "Verdict"; do grep -qi "$s" WORKFLOW-TEMPLATES.md || echo "MISSING: $s"; done` — verifies **AC1** (catalog section coverage). Pass = no `MISSING:` lines.
- `grep -Eqi 'Build\b' .claude/commands/build.md && grep -Eqi 'Done\b' .claude/commands/ship.md && grep -qi 'Approved' .claude/commands/plan-w-team.md && echo PASS` — verifies **AC2** (each command advances its lifecycle node). Pass = `PASS`.
- `grep -q 'gh pr create --draft' .claude/commands/plan-w-team.md && grep -qi 'Spec-review status' .claude/commands/plan-w-team.md && echo PASS` — verifies **AC3** (PR opened at plan time + PR spec-review mirror). Pass = `PASS`.
- `! grep -rEn '#<taskId>|#[0-9]+ <subject>' .github/PULL_REQUEST_TEMPLATE/ && echo PASS` — verifies **AC4** (no false-link manifest format in PR templates). Pass = `PASS` with no matches.
- `grep -Eqi 'resume( the| the existing)? .*draft PR|resume the existing' .claude/commands/build.md && echo PASS` — verifies **AC5** (build resumes the PR). Pass = `PASS`.
- `grep -qi 'implementation-review' WORKFLOW-TEMPLATES.md && grep -qi 'parity\|impl-review relay\|Codex review R' WORKFLOW-TEMPLATES.md && echo PASS` — verifies **AC6** (impl-review relay canonicalized). Pass = `PASS`.
- `! grep -n 'epic-plan' GIT-COMMIT-PR-MESSAGE.md && ! grep -n 'specs/<feature>/plan.md' GIT-COMMIT-PR-MESSAGE.md && ! grep -n 'Workstream C' .claude/commands/ship.md && grep -q "plan.md" .claude/commands/build.md && echo PASS` — verifies **AC7** (stale refs gone, legacy fallback retained). Pass = `PASS`.
- `for f in .claude/commands/plan-w-team.md .claude/commands/build.md .claude/commands/ship.md .agents/skills/spec-review/SKILL.md .agents/skills/implementation-review/SKILL.md; do grep -q 'WORKFLOW-TEMPLATES.md' "$f" || echo "NO REF: $f"; done` — verifies **AC8** (all five reference the catalog). Pass = no `NO REF:` lines.
- `! grep -qi 'Canonical issue snippets' .claude/commands/plan-w-team.md && echo PASS` — verifies **AC8** (embedded snippets removed). Pass = `PASS`.
