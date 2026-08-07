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
- **2026-08-07 · pilot-eval run 1/3 (AC7)** — fresh opus/high session executed
  `/wiki:ingest` fixture A → `/wiki:ingest` fixture B → `/wiki:query "why does
  the LLM wiki pattern pair well with Obsidian?"` → `/wiki:lint`, from the seed.
  Rubric conditions (build-lead spot-checked on disk): pages ✓
  (`ai-docs/wiki/engineering/llm-wiki-pattern.md` type `pattern`,
  `obsidian-vault.md` type `tool`; all seven fields, `status: current`, fixture
  paths in `sources:`); cross-link ✓ (`[[obsidian-vault]]` ↔
  `[[llm-wiki-pattern]]`, `related:` in sync both directions); index ✓ (two
  Engineering rows, Personal still pointer-only); log ✓ (one ingest entry per
  fixture carrying its path); query ✓ (synthesis across both pages with inline
  citations, nothing disputed, zero writes — verified via git status between
  steps); lint ✓ (clean report, log entry
  `## [2026-08-07] lint | engineering | clean — 2 pages checked, no findings` +
  payload `missing-pages: none · mechanical-fixes: 0`); privacy ✓ (no
  `ai-docs/wiki/personal/`, no personal content in shared index/log).
  Idempotency (condition 5) is runs 2–3's job. Run 1: PASS on all applicable
  conditions.
- **2026-08-07 · lesson (memory-marked, pipeline-process)** — the markdown
  auto-format hook inserts a blank line between a lint log heading and its
  payload line, so the on-disk shape is heading / blank / payload. lint.md says
  the payload directly follows the heading — the hook wins on every write.
  Route at the memory step: relax lint.md's wording to "on the next non-blank
  line" so command text matches reality; /wiki:status parsing is unaffected.
- **2026-08-07 · pilot-eval run 2/3 (AC7, idempotency)** — fresh opus/high
  session re-ran the same four-command flow against run 1's pages. Both ingests
  recognized their canonical source path in page `sources:`, index row, and log
  entry, and wrote NOTHING: `git diff --stat ai-docs/wiki/` after both ingests
  was empty, page count 4 → 4, no duplicate rows or entries (build lead
  verified the final diff: only lint's own 4-line log append). Query synthesized
  across both pages with citations, zero writes; lint clean; privacy boundary
  intact. Run 2: PASS on all 8 conditions.
- **2026-08-07 · defect found by run 2 (deviation, no locked decision)** —
  `.markdownlint.jsonc` MD024 `siblings_only: true` blocks appending a lint log
  heading identical to a prior pass (same date | scope | summary — the
  deterministic case for a clean wiki linted twice in one day); the auto-format
  hook rejects the write. Run 2 landed its entry with a truthful distinct
  summary. Fix routed to a builder: file-local
  `<!-- markdownlint-disable MD024 -->` in the seed `ai-docs/wiki/log.md`
  (append-only logs legitimately repeat sibling headings), plus lint.md wording
  relaxed to "payload on the next non-blank line" (absorbs the run-1 lesson —
  the formatter separates heading and payload with a blank line).
- **2026-08-07 · fix: MD024 log defect** — builder (sonnet/medium) added the
  file-local `<!-- markdownlint-disable MD024 -->` to `ai-docs/wiki/log.md` and
  the one-sentence payload-placement clarification to lint.md. Verified (all
  re-reported from the builder's run, spot-confirmed by the commit diff): ac2
  "PASS", ac1 "PASS", drift suite "3 passed", markdownlint 0 errors, and a
  scratch-copy proof that a duplicated lint heading no longer fires MD024.
  This absorbs both pilot lint-log lessons — nothing further routes at the
  memory step for them.
- **2026-08-07 · pilot-eval run 3/3 (AC7, idempotency post-fix)** — fresh
  opus/high session, same four-command flow. Both ingests were exact no-ops
  (canonical path matched in page `sources:`, log entry, and index row; page
  SHA-256 hashes byte-identical to baseline; page count 2 → 2); query answered
  across both pages with citations and zero writes; lint clean and appended a
  heading byte-identical to run 2's entry with markdownlint at 0 errors —
  proving the MD024 fix in the real flow. Build lead verified the final diff:
  only lint's 4-line log append; no `personal/`, no personal content in the
  shared index/log. Run 3: PASS on all 8 conditions.
- **2026-08-07 · AC7 verdict** — pass rate 3/3 on every applicable
  pilot-rubric.md condition (run 1 from seed: conditions 1–4 and 6–8; runs 2–3:
  all 8 incl. idempotency). `pilot-eval` complete.
- **2026-08-07 · plan-artifact catch-up** — `specs/wiki-layer/artifacts/implementation-plan.html`
  found untracked in the worktree (authored at plan stage, never committed);
  committed now so the artifact inventory matches artifacts.md.
