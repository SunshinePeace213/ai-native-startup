# Implementation Notes: Wiki Layer

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

- **2026-08-07 · build start** — plan resolved to `specs/wiki-layer/` on worktree
  `.claude/worktrees/wiki-layer` (issue #88, complex, kb-grounded). KB mirrors are
  device-local and were split across checkouts: karpathy, lucianfialho, rohitg00,
  and cerebras mirrors copied from the main checkout into the worktree's
  `ai-docs/` (byte-identical copies, no content edits) so builders can ground
  against all nine `## KB References` docs. Frontmatter claims (command
  `description`/`argument-hint`/`model`/`effort`; rule `paths:` globs) verified
  against `ai-docs/anthropic/skills.md` and `ai-docs/anthropic/memory.md`.
- **2026-08-07 · spec staleness absorbed (R2-F7/R2-F8)** — spec.md Objective says
  "five plan-local checks"; `checks/` ships three scripts (ac1, ac2, ac5) — the
  drift test owns AC3/AC4/AC6. spec.md Notes still lists the routines-mirror KB
  gap; `ai-docs/anthropic/routines.md` was already mirrored at gate round 1.
  Neither affects the build; recorded here per the spec's Codex Verification note.
- **2026-08-07 · phase 1 start** — `wiki-foundation` (sonnet/medium) and
  `wiki-standards-rule` (opus/high) launched concurrently, disjoint files.
- **2026-08-07 · hand-off `wiki-foundation`** — `.gitignore`,
  `ai-docs/wiki/index.md`, `ai-docs/wiki/log.md`, `ai-docs/.obsidian/app.json`,
  `ai-docs/.obsidian/appearance.json`
  - `bash specs/wiki-layer/checks/ac1-privacy-gitignore.sh` → "PASS: gitignore
    semantics correct for wiki layer", exit 0 (re-run by build lead)
  - `uv run specs/wiki-layer/checks/ac2-seed.py` → "PASS: wiki seed structure
    correct", exit 0 (re-run by build lead)
  - Deviation (minor, no locked decision touched): the index footer lives under
    its own `## Notes` heading instead of trailing bare after `## Personal` —
    the AC2 parser scopes all content after the last `##` heading to that
    section, so a bare footer would have broken the "Personal holds only the
    pointer line" condition. Spec's footer requirement still met.
- **2026-08-07 · hand-off `wiki-standards-rule`** — `.claude/rules/wiki-layer/wiki-standards.md` (new)
  - Drift test doesn't exist yet (lands at task 6); build lead verified by full
    read against the AC4 content contract: `paths: ["ai-docs/wiki/**"]`
    frontmatter parses; sections `## Page Schema` (7 fields + 3 status values as
    code spans, propagation duty), `## Linking and Citations` (per-claim ≥1
    source), `## Writing Standards` (theme-over-chronology, anti-cramming,
    anti-thinning, flat tone, quote discipline, length bounds), `## Domains`
    (all six), `## Privacy` (personal index/log, `wiki/personal/assets/`,
    secret/PII stripping, re-read-before-edit), `## Obsidian` (Web Clipper /
    Dataview / Marp, recommended-never-required), `## Operations` (the
    model/effort source-of-truth table), `## Layer Requirements` (lane fit, 4
    metrics targets, archetypes) — all present. `bunx markdownlint-cli2` on the
    file: 0 errors (builder-run).
  - Deviation (minor, no locked decision touched): the farzaa em-dash ban was
    dropped when distilling the tone standard — it contradicts this repo's own
    prose style; decisions.md locks "customize, do not port", so this is within
    bounds. All other farzaa tone constraints carried over.
  - Note for task 6: the operations table lives under its own `## Operations`
    heading; command/model/effort cells are code spans.
- **2026-08-07 · phase 2 start** — `wiki-commands-ingest-lint` (opus/high) and
  `wiki-commands-query-status` (sonnet/high) launched concurrently after the
  standards rule landed; disjoint files under `.claude/commands/wiki/`.
- **2026-08-07 · hand-off `wiki-commands-query-status`** — `.claude/commands/wiki/query.md`,
  `.claude/commands/wiki/status.md` (both new)
  - `uv run --with pyyaml python -c "…split('---')[1]…"` → both frontmatters
    parse; descriptions byte-match spec.md's blocks; query `sonnet`/`high` +
    `argument-hint: <question>`, status `haiku`/`medium`, matching the
    wiki-standards `## Operations` table (re-run by build lead, exit 0)
  - Build lead full-read: query body declares itself strictly read-only (drift
    test hook), no-coverage and seed-only degrade paths present; status derives
    absorb/breakdown/cleanup from `sources.yaml` + the lint log payload fields,
    with insufficient-history/no-lint-yet cases and personal-domain
    counts-only handling. Deviations: none.
- **2026-08-07 · hand-off `wiki-commands-ingest-lint`** — `.claude/commands/wiki/ingest.md`,
  `.claude/commands/wiki/lint.md` (both new)
  - `uv run --with pyyaml python -c "…split('---')[1]…"` → both parse; key sets
    exactly `[argument-hint, description, effort, model]` (ingest) and
    `[description, effort, model]` (lint), both opus/high per the Operations
    table (re-run by build lead, exit 0)
  - Build lead full-read: ingest carries the URL refusal → `/harness-layer:kb add`,
    integrate-never-append, the canonical-source-path idempotency key matched
    across pages/index/log, the shared-vs-personal index+log split, secret/PII
    stripping, 5-source batch checkpoints, and the crystallization gate; lint
    carries all check classes incl. missing-mirrors-as-"run /harness-layer:kb",
    the fix-vs-report split, the exact two-line log payload, the /schedule
    weekly-routine prompt grounded in ai-docs/anthropic/routines.md, and
    clean-on-seed. Builder-run markdownlint: 0 errors.
  - Deviation (minor, no locked decision touched): a secret/PII leak found by
    lint is redacted in place (then reported) rather than left in a tracked
    file as a report-only judgment finding — the task didn't assign leaks to
    either side; redact-first is the safe reading of the privacy obligations.
- **2026-08-07 · hand-off `agents-md-amendments`** — `AGENTS.md`
  - `uv run specs/wiki-layer/checks/ac5-memory-amendments.py` → "PASS: AGENTS.md
    amendments exact and within budget", exit 0 (re-run by build lead)
  - `git diff --numstat AGENTS.md` → 9 added / 3 removed, net +6 lines — within
    the ≤14 budget. All three spec amendment blocks applied verbatim; the
    wiki-standards.md link target exists. Deviations: none.
- **2026-08-07 · phase 3** — `agents-md-amendments` ran alone (Parallel: false),
  then `wiki-drift-test` (sonnet/high) launched; pilot-eval run 1 started
  concurrently with the drift test (disjoint files: tests/ vs ai-docs/wiki/).
- **2026-08-07 · hand-off `wiki-drift-test`** — `tests/harness-layer/test_wiki_layer.py` (new)
  - `uv run pytest tests/harness-layer/test_wiki_layer.py -q` → "3 passed in
    1.01s" (re-run by build lead)
  - `uv run pytest tests/harness-layer/ -q` → "936 passed, 2 skipped in 11.33s"
    (re-run by build lead)
  - `uv run ruff check tests/harness-layer/test_wiki_layer.py` → "All checks
    passed!" (re-run by build lead)
  - Deviation (spawn-prompt error, builder corrected it): the build lead's
    prompt claimed pyyaml was available under `uv run pytest`; it is not a
    project dependency. The builder used a small house-style frontmatter
    parser (same pattern as test_model_drift.py) instead of adding a
    dependency — matching the repo convention. Expectations re-derive from
    AGENTS.md, wiki-standards.md's Operations table, and model-selection.md;
    the argument-hint key split is the one stated design fact, named with a
    comment.
- **2026-08-07 · plan-artifact catch-up** — `specs/wiki-layer/artifacts/implementation-plan.html`
  found untracked in the worktree (authored at plan stage, never committed);
  committed now so the artifact inventory matches artifacts.md.
