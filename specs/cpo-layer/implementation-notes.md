# Implementation Notes: studio-layer — design-delivery studio through signed handoff

> Chronological dev log for [spec.md](./spec.md), created from this template at
> `/harness-layer:harness-build` implement start and appended by both
> `/harness-layer:harness-build` and `/harness-layer:harness-review` as the work
> proceeds. Entries land at each checkpoint commit, the moment the event happens;
> the PR body and build brief are derived from these notes — never reconstructed.
>
> Boundary: per-plan phases, hand-offs, deviations, fixes, and lessons live here.
> A lesson worth keeping beyond this plan is routed to its rule-file home by the
> memory step per memory-series.md.

## Log

<!-- Append-only; one entry per phase, hand-off, deviation, fix, or lesson — never edit or
     delete a prior entry. "No entries yet" is a valid starting body. -->

- **2026-08-01 · build start** — worktree `.claude/worktrees/cpo-layer` on branch
  `worktree-cpo-layer` (remote `feat/80-cpo-layer`), plan approved at the human gate,
  review profile `kb-grounded`.
  - `uv run pytest -q` → `875 passed, 2 skipped in 22.62s` — baseline before any build change.
- **2026-08-01 · phase 1 (ground the namespace)** — launched `studio-namespace`, `studio-roster`,
  `studio-client-artifacts`, `studio-question-bank` and `gate-signoff-hook` as concurrent
  builders; their **Files** fields are the disjointness contract.
- **2026-08-01 · hand-off `studio-namespace`** — `.gitignore`, `clients/.gitkeep`,
  `.claude/rules/studio-layer/studio-identity.md`, `AGENTS.md`
  - `git check-ignore -v clients/acme/site/brief.md` → `.gitignore:378:clients/* clients/acme/site/brief.md`
  - `git check-ignore -q clients/.gitkeep; echo $?` → `1` — the negation re-includes the contract file.
  - `bash specs/cpo-layer/checks/ac1-client-data-home.sh` → `AC1 pass: clients/ is contracted,
    ignored, and invisible to the spec gate`, exit 0. The builder's own run of this check
    returned exit 1 on two counts, both because `clients/.gitkeep` was still untracked — the
    builder is barred from `git add`, so the lead staged and committed it and the check went
    green with no file change.
  - `bash specs/cpo-layer/checks/ac5-rules-path-scoped.sh` → exit 1, reporting only
    `roster.md is missing` / `client-artifacts.md is missing` / `expected at least 3 studio
    rules, found 1`. No failure against `studio-identity.md`: it cleared the scope, name,
    voice, letterhead, sign-off and ≥400-char body assertions. Pending the two concurrent rules.
  - Deviations: none.
- **2026-08-01 · hand-off `studio-roster`** — `.claude/rules/studio-layer/roster.md`
  - Ten data rows; the principal row (Maya Lindqvist, `fable`/`xhigh`) states "No agent file"
    in its escalation cell, so the drift test can identify the row it must skip from the table
    itself rather than from a hard-coded name.
  - Every `Model` cell checked against `model-selection.md`'s Roster table and every `Effort`
    cell against its Effort table; all ten match.
  - `bash specs/cpo-layer/checks/ac5-rules-path-scoped.sh` → exit 0.
  - Deviations: none.
- **2026-08-01 · hand-off `studio-client-artifacts`** — `.claude/rules/studio-layer/client-artifacts.md`
  - `bash specs/cpo-layer/checks/ac4-client-artifacts.sh` → `AC4 pass: forks craft/publish,
    unlocks the palette, four patterns each with a return`, exit 0. That check also proves
    `.claude/rules/harness-layer/artifacts.md` is byte-identical to `origin/main` — the fork,
    not an edit, guardrail.
  - Deviations: none.
- **2026-08-01 · deviation (glob form) · `studio-namespace`, `studio-roster`, `studio-client-artifacts`**
  — plan said `paths: clients/**`; did `paths: clients/**/*` on all three studio rules.
  `studio-roster` surfaced the split (it had written `clients/**/*`, the other two the literal
  plan text). Settled on `clients/**/*` because `ai-docs/anthropic/memory.md` documents
  `src/**/*` as "All files under `src/`" and carries no bare `dir/**` row — under the
  kb-grounded profile "`clients/**` matches nested files" is a memory claim with no citable
  source — and because every path-scoped rule already in this repo uses that form
  (`specs/**/*`, `tests/**/*`, `.claude/hooks/**/*`, `**/*.py`). Had `clients/**` been wrong,
  the failure would have been silent: no studio rule would ever load on a client project.
  AC5 is satisfied either way (its assertion is the substring `clients/**`, which
  `clients/**/*` contains), so no acceptance criterion or locked decision changed — only the
  glob form the plan spelled out in prose. The two one-line edits were made by the builders
  owning each file, not by the lead.
  - `bash specs/cpo-layer/checks/ac4-client-artifacts.sh` → exit 0 after the change.
  - `bash specs/cpo-layer/checks/ac5-rules-path-scoped.sh` → exit 0 after the change.
- **2026-08-01 · hand-off `studio-question-bank`** —
  `.claude/skills/studio-layer/studio-client-questions/SKILL.md`, `…/evals/evals.json`
  - The machine-readable contract the coverage checker parses: **every `###` heading under
    `## Dimensions` is one dimension, and the heading text is its name.** The skill states this
    in its own `## Machine-readable dimension list` section, so the parser has a documented
    anchor rather than an inferred one. Eight dimensions today: the job the site does; the
    audience and their situation; brand voice; references loved and hated; the content that
    actually exists; hard constraints; budget; success at six months.
  - Frontmatter carries `name` and `description` and does **not** carry
    `disable-model-invocation`; directory name equals `name:`, which is what becomes the command.
  - `(cd .claude/skills/meta-skills && uv run --with pyyaml python -m scripts.eval ../studio-layer/studio-client-questions --lint)`
    → `PASS (0 warning(s))`, exit 0.
  - Eval suite: 2 cases, 11 assertions, 6 of them executable `check`s.
  - `bash specs/cpo-layer/checks/ac6-question-bank-skill.sh` → exit 1 on exactly two counts,
    both pending later tasks: `check_question_coverage.py is missing` and
    `p1-discovery.md is missing`. No assertion against the skill itself failed.
  - Deviations: none.
- **2026-08-01 · phase 2/3** — launched `studio-role-agents` (roster landed) and
  `studio-check-scripts` (question bank landed) as concurrent builders.
