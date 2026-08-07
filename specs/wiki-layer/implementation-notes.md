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
- **2026-08-07 · plan-artifact catch-up** — `specs/wiki-layer/artifacts/implementation-plan.html`
  found untracked in the worktree (authored at plan stage, never committed);
  committed now so the artifact inventory matches artifacts.md.
