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
- **2026-08-07 · hand-off `validate-all`** — read-only validator (sonnet/high),
  worktree HEAD 64b3d46
  - AC1 → "PASS: gitignore semantics correct for wiki layer" exit 0 · AC2 →
    "PASS: wiki seed structure correct" exit 0 · AC3 → "2 passed" · AC4 →
    "1 passed" · AC5 → "PASS: AGENTS.md amendments exact and within budget"
    exit 0 · AC6 → "3 passed" · AC7 → 3/3 corroborated against on-disk state
    (2 ingest log entries after 3 runs = structural idempotency proof; MD024
    defect-and-fix trail supports evidence authenticity). Overall: PASS.
  - Advisory for review (not a failure, not fixed here — the check script is a
    plan-time artifact outside the build's tasks): ac5-memory-amendments.py
    computes its ≤14-line budget from a hardcoded list length rather than the
    real git diff; the real diff (+9/−3) satisfies the budget independently.
- **2026-08-07 · tidy** — harness-simplifier: 7 behavior-preserving edits across
  query.md / status.md / lint.md / wiki-standards.md (deduplicated read-only
  guards into single strongest statements, cut one rationale clause from
  lint.md's routine section, merged one restated rule in the standards file);
  ingest.md clean. code-simplifier: 4 edits to test_wiki_layer.py (command set
  derived once from `COMMAND_KEY_SETS`, one section-matching mechanism, merged
  roster-column helpers, dropped an unused unpacking) with an old-vs-new
  equivalence script over every heading keyword; 3 redundant-assertion removals
  flagged but not applied (assertions are kept per the tidy constraint).
  Build-lead re-verification after both: `uv run pytest tests/harness-layer/ -q`
  → "936 passed, 2 skipped in 11.16s"; AC1 "PASS", AC2 "PASS", AC5 "PASS"
  (exit 0).
- **2026-08-07 · drift check** — `BASE=b62cf9a` (merge-base with origin/main);
  every changed file outside `specs/wiki-layer/` maps to its owner, and every
  task maps to a present diff:

  | File | Owner |
  | --- | --- |
  | `.gitignore`, `ai-docs/.obsidian/app.json`, `ai-docs/.obsidian/appearance.json` | `wiki-foundation` |
  | `ai-docs/wiki/index.md`, `ai-docs/wiki/log.md` | `wiki-foundation` (seed) + `pilot-eval` (entries) + MD024 fix (log) |
  | `.claude/rules/wiki-layer/wiki-standards.md` | `wiki-standards-rule` (+ tidy) |
  | `.claude/commands/wiki/ingest.md`, `.claude/commands/wiki/lint.md` | `wiki-commands-ingest-lint` (lint also MD024 fix + tidy) |
  | `.claude/commands/wiki/query.md`, `.claude/commands/wiki/status.md` | `wiki-commands-query-status` (+ tidy) |
  | `AGENTS.md` | `agents-md-amendments` |
  | `tests/harness-layer/test_wiki_layer.py` | `wiki-drift-test` (+ tidy) |
  | `ai-docs/wiki/engineering/llm-wiki-pattern.md`, `obsidian-vault.md` | `pilot-eval` |
  | `ai-docs/sources.yaml` | plan stage — gate R1 KB gap-fill (routines.md registration), pre-build, approved at the human gate |

  Reverse direction: all seven file-owning tasks show their diff;
  `validate-all` is read-only by design (Files: none). No unmapped files, no
  diff-less tasks — no deviation.
- **2026-08-07 · AC7 manual validation command, executed** — per the
  acceptance-criteria.md AC7 command, the
  build lead runs the fixture flow three times in fresh sessions — done, as
  recorded in the three pilot-eval run entries above; observed outcome: 3/3
  runs met every pilot-rubric.md condition (pages, cross-link, index, log,
  idempotency, query, lint, privacy).
- **2026-08-07 · impl lint** — first run: 2 FAILs. (1) the AC7 manual check's
  probe text was missing from the notes — recorded above (process gap, not a
  work gap: the runs themselves were already logged). (2) checkpoint commit
  4aee857's subject was 76 chars (>72) — the build lead's own commit, fixed by
  `git filter-branch --msg-filter` shortening that one subject
  ("gitignore negations, seed, vault config" → "gitignore, seed, vault
  config"); history from that commit rewritten (old→new head SHA mapping:
  3deffc6 → 6a04ede; earlier SHAs cited in prior entries refer to pre-rewrite
  history), force-pushed with lease. Both fixes were build-lead-owned (notes
  file and git are the lead's surfaces — no builder owns them), so neither was
  routed to a builder.
- **2026-08-07 · memory step** — one lesson routed beyond the plan
  (pipeline-process → the command it corrects): harness-build.md's read-the-plan
  step now says to copy referenced mirrors missing from the worktree's
  device-local `ai-docs/` in from the main checkout before builders launch —
  the gap this build hit at start. The lint-log lessons were already absorbed
  by the MD024 fix; the pyyaml prompt error, the AC2 footer parsing note, and
  the plan-session trailing commit stay plan-local here. Follow-up (not an
  edit): `personal/log.md` is created lazily by a future personal ingest and
  should mirror the shared log's seed shape including the MD024 disable —
  carried to the PR's `## Follow-ups`.
- **2026-08-07 · plan-artifact catch-up** — `specs/wiki-layer/artifacts/implementation-plan.html`
  found untracked in the worktree (authored at plan stage, never committed);
  committed now so the artifact inventory matches artifacts.md.
- **2026-08-07 · review fix: evidence restatement (impl gate I1-F10, I1-F15)** —
  appended, never a rewrite: every entry above stands as its session wrote it.

  What those entries actually are. The pilot-eval run 1–3 entries and the
  `wiki-foundation` / `wiki-standards-rule` / `wiki-commands-*` / `wiki-drift-test` /
  `agents-md-amendments` / `validate-all` hand-off entries record build-lead
  *observations* — summaries of results and on-disk spot-checks — not captured
  transcripts. Specifically not captured at the time, and therefore gone: the AC7
  `/wiki:query` answers and the citation targets they named, the AC7 `/wiki:lint`
  console output for each of the three runs, the full text of the frontmatter-parse
  one-liners the hand-off entries abbreviate as `python -c "…split('---')[1]…"`, and
  the per-assertion output behind `validate-all`'s label-level results. None of that
  is reconstructed or backfilled here.

  "page count 4 → 4" (run 2 entry) counted tracked files under `ai-docs/wiki/`, not
  wiki pages — the two-page pilot plus the index and the log. Verifiable now:
  `git ls-files ai-docs/wiki/` → `ai-docs/wiki/engineering/llm-wiki-pattern.md`,
  `ai-docs/wiki/engineering/obsidian-vault.md`, `ai-docs/wiki/index.md`,
  `ai-docs/wiki/log.md` (exit 0) — 4 tracked files = 2 pages + index + log. Run 3's
  "page count 2 → 2" counted pages, which is why the two numbers differ.

  Re-runnable commands, re-run verbatim this session from the repo root after the
  I1-F* fixes, with their literal output:

  - `bash specs/wiki-layer/checks/ac1-privacy-gitignore.sh` → `PASS: gitignore
    semantics correct for wiki layer`; exit 0
  - `uv run specs/wiki-layer/checks/ac2-seed.py` → `PASS: wiki seed structure
    correct`; exit 0
  - `uv run specs/wiki-layer/checks/ac5-memory-amendments.py` → `PASS: AGENTS.md
    amendments exact and within budget`; exit 0
  - `uv run pytest tests/harness-layer/test_wiki_layer.py::test_command_registry tests/harness-layer/test_wiki_layer.py::test_command_frontmatter -q`
    → `2 passed in 1.06s`; exit 0
  - `uv run pytest tests/harness-layer/test_wiki_layer.py::test_standards_rule -q` →
    `1 passed in 1.04s`; exit 0
  - `uv run pytest tests/harness-layer/test_wiki_layer.py -q` → `3 passed in 1.08s`;
    exit 0
  - `uv run pytest tests/harness-layer/ -q` → `1 failed, 935 passed, 2 skipped in
    11.95s`; exit 1. The failure is
    `tests/harness-layer/test_pipeline_formats.py::test_lens_clusters_cover_every_stamped_standard[I]`
    — `AssertionError: unassigned standards: ['I9']; phantom cluster IDs: []`. It is
    pre-existing and unrelated to this diff: the gate's own self-improve commit
    `eaed8cd` added `I9` to `impl-standards.md` without adding it to the codex-gate
    skill's Lens clusters table (`grep -n "I9" .claude/skills/codex-gate/SKILL.md` →
    no output), and `git status --porcelain .claude/skills/codex-gate/SKILL.md
    .claude/rules/harness-layer/impl-standards.md` → empty, so neither of the test's
    two inputs is touched here. Flagged to the gate lead; it is not one of the 13
    blocking findings.
  - `uv run ruff check tests/harness-layer/test_wiki_layer.py specs/wiki-layer/checks/ac5-memory-amendments.py specs/wiki-layer/checks/ac2-seed.py`
    → `All checks passed!`; exit 0
  - `bunx markdownlint-cli2 ".claude/commands/wiki/*.md" ".claude/rules/wiki-layer/wiki-standards.md"`
    → `Linting: 5 file(s)` / `Summary: 0 error(s)`; exit 0
  - The frontmatter-parse one-liner the hand-off entries abbreviated, written out in
    full and re-run:

    ```bash
    uv run --with pyyaml python -c "
    import pathlib, yaml
    for name in ('ingest','query','lint','status'):
        p = pathlib.Path('.claude/commands/wiki')/(name+'.md')
        fm = yaml.safe_load(p.read_text(encoding='utf-8').split('---')[1])
        print(name, sorted(fm), fm['model'], fm['effort'])
    "
    ```

    Output, exit 0:

    ```text
    ingest ['argument-hint', 'description', 'effort', 'model'] opus high
    query ['argument-hint', 'description', 'effort', 'model'] sonnet high
    lint ['description', 'effort', 'model'] opus high
    status ['description', 'effort', 'model'] haiku medium
    ```

  AC7's on-disk residue, corroborated with literal commands and output (this is what
  survives of the three pilot runs; it is not a re-run of the pilot):

  - Page frontmatter —
    `uv run python -c "import pathlib
    for p in sorted(pathlib.Path('ai-docs/wiki/engineering').glob('*.md')): print('---', p); print(p.read_text(encoding='utf-8').split('---')[1].strip())"`:

    ```text
    --- ai-docs/wiki/engineering/llm-wiki-pattern.md
    type: pattern
    domain: engineering
    status: current
    created: 2026-08-07
    updated: 2026-08-07
    sources: ["specs/wiki-layer/checks/fixtures/article-a-llm-wiki-pattern.md", "specs/wiki-layer/checks/fixtures/article-b-obsidian-vaults.md", ".claude/rules/wiki-layer/wiki-standards.md"]
    related: ["[[obsidian-vault]]"]
    --- ai-docs/wiki/engineering/obsidian-vault.md
    type: tool
    domain: engineering
    status: current
    created: 2026-08-07
    updated: 2026-08-07
    sources: ["specs/wiki-layer/checks/fixtures/article-b-obsidian-vaults.md", ".claude/rules/wiki-layer/wiki-standards.md"]
    related: ["[[llm-wiki-pattern]]"]
    ```

  - Cross-references — `grep -n "\[\[" ai-docs/wiki/engineering/llm-wiki-pattern.md ai-docs/wiki/engineering/obsidian-vault.md`:

    ```text
    ai-docs/wiki/engineering/llm-wiki-pattern.md:8:related: ["[[obsidian-vault]]"]
    ai-docs/wiki/engineering/llm-wiki-pattern.md:79:The [[obsidian-vault]] is the reading surface this repository uses, and it fits the
    ai-docs/wiki/engineering/obsidian-vault.md:8:related: ["[[llm-wiki-pattern]]"]
    ai-docs/wiki/engineering/obsidian-vault.md:34:[[llm-wiki-pattern]] describes
    ai-docs/wiki/engineering/obsidian-vault.md:49:which is the same drift that the [[llm-wiki-pattern]]'s lint operation sweeps for
    ```

  - Index rows — `grep -n "^| \[\[" ai-docs/wiki/index.md`:

    ```text
    9:| [[llm-wiki-pattern]] | pattern | current | 2026-08-07 |
    10:| [[obsidian-vault]] | tool | current | 2026-08-07 |
    ```

  - Log entries — `grep -n "^## \[2026" ai-docs/wiki/log.md`:

    ```text
    21:## [2026-08-07] ingest | LLM Wiki Pattern | specs/wiki-layer/checks/fixtures/article-a-llm-wiki-pattern.md
    23:## [2026-08-07] ingest | Obsidian Vault | specs/wiki-layer/checks/fixtures/article-b-obsidian-vaults.md
    25:## [2026-08-07] lint | engineering | clean — 2 pages checked, no findings
    29:## [2026-08-07] lint | engineering | clean — 2 pages, index and log consistent
    33:## [2026-08-07] lint | engineering | clean — 2 pages, index and log consistent
    ```

    Two ingest entries carrying the fixture paths after three runs, against three
    lint entries — the structural idempotency residue, consistent with the run 2–3
    entries above.

  ac5 negative demonstration (I1-F14 / I1-F16), on temp copies of `AGENTS.md` under
  `/home/ringo/.claude/jobs/8440784b/tmp/`, never in the repo tree — each copy edited,
  then `uv run <repo>/specs/wiki-layer/checks/ac5-memory-amendments.py` run with that
  copy's directory as cwd:

  - 10 blank lines inserted inside `## Wiki Layer` (section = 15 lines, no extra
    non-empty line, so only the budget check can fire) → `FAIL: the '## Wiki Layer'
    section spans 15 lines in AGENTS.md > budget 14`; exit 1
  - 10 extra bullet lines inserted (section = 15 lines) → `FAIL: Wiki Layer section
    carries 10 unprescribed non-empty line(s)` and `FAIL: the '## Wiki Layer' section
    spans 15 lines in AGENTS.md > budget 14`; exit 1
  - trailing sentence appended to the KB bullet 1 line → `FAIL: KB bullet 1
    (wiki-over-mirrors) is not exactly one line in AGENTS.md`; exit 1
  - KB bullet 1 wrapped across two lines → `FAIL: Knowledge Base section lacks the
    exact prescribed KB bullet 1 (wiki-over-mirrors)`; exit 1
- **2026-08-07 · review fix: impl gate cycle 2 (I2-F1, I2-F3)** — two fixes, nothing
  else touched.

  I2-F1 (`.claude/commands/wiki/ingest.md`): the changed-source re-ingest branch said
  "refresh the existing INDEX rows only; the LOG keeps its one entry", contradicting
  wiki-standards.md's locked metric "100% of ingests update the index and the log".
  Resolved in the command, not the metric: a changed-source re-ingest now appends its
  own dated LOG entry (the log is append-only history; the file-local MD024 disable
  already permits repeated sibling headings), while "never a second page and never a
  second index row" stands. Instructions branch list, Workflow step 6, and the KEY
  variable ("its LOG entries") updated together; the Report line already said "the
  index rows and log entry written", so the behavior change makes it true as written.
  The identical-repeat branch still writes nothing at all, log entry included, and
  idempotency identity is unchanged — presence of the canonical path in page
  `sources:`/the LOG, which a second entry for the same path does not affect.

  I2-F3 (`specs/wiki-layer/checks/ac2-seed.py`): the MD024 regression check was a bare
  substring test, so it passed on a directive that markdownlint ignores. It now scans
  the log line by line with a ``` fence toggle and requires the comment on its own line
  outside any fence and before the first `##` entry heading.

  Verification, run from the repo root this session:

  - `uv run specs/wiki-layer/checks/ac2-seed.py` → `PASS: wiki seed structure
    correct`; exit 0
  - `bunx markdownlint-cli2 ".claude/commands/wiki/ingest.md"` → `Linting: 1 file(s)` /
    `Summary: 0 error(s)`; exit 0
  - `uv run pytest tests/harness-layer/ -q` → `936 passed, 2 skipped in 13.01s`; exit 0
    (the 2 skips are `test_model_drift.py:169`/`:179`, "got empty parameter set" —
    pre-existing; the I9 lens-cluster failure recorded in the cycle-1 entry above no
    longer fires)
  - `uv run ruff check specs/wiki-layer/checks/ac2-seed.py` → `All checks passed!`;
    exit 0

  I2-F3 negative demonstrations, on temp copies of the seed under
  `/home/ringo/.claude/jobs/8440784b/tmp/case-{a,b,c}/ai-docs/`, never in the repo tree
  — each copy's `wiki/log.md` edited, then
  `uv run --no-project <repo>/specs/wiki-layer/checks/ac2-seed.py` run with that copy's
  directory as cwd:

  - (a) directive moved inside the ```` ```text ```` fence → `FAIL: log.md lacks an
    effective file-local '<!-- markdownlint-disable MD024 -->' comment on its own line
    outside any code fence`; exit 1
  - (b) directive deleted → same FAIL line; exit 1
  - (c) directive placed after the first real entry heading → `FAIL: log.md's
    '<!-- markdownlint-disable MD024 -->' comment follows the first '## ' entry
    heading, so it does not cover the whole file`; exit 1

  Regression confirmed against the pre-fix script (`git show
  HEAD:specs/wiki-layer/checks/ac2-seed.py`, run on the same copies): cases (a) and (c)
  both printed `PASS: wiki seed structure correct`, exit 0.
