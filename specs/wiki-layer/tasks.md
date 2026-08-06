# Tasks: Wiki Layer

> Execution plan for [spec.md](./spec.md). Owner and scope are defined there; this file is
> how & who. Orchestration mechanics live in `.claude/rules/orchestration.md`.

## Implementation Phases

### Phase 1: Foundation

Storage semantics and the layer's normative rule — everything else builds on these.
Tasks: `wiki-foundation`, `wiki-standards-rule` (parallel, disjoint files).

### Phase 2: Command surface

The four `/wiki:*` operations, written against the standards rule.
Tasks: `wiki-commands-ingest-lint`, `wiki-commands-query-status` (parallel, disjoint files).

### Phase 3: Memory & drift guard

AGENTS.md integration and the drift test over the new surface.
Tasks: `agents-md-amendments`, `wiki-drift-test`.

### Phase 4: Pilot & validation

The pre-ship fixture eval, then full validation.
Tasks: `pilot-eval`, `validate-all`.

## Step by Step Tasks

### 1. Wiki Foundation

- **Task ID:** `wiki-foundation`
- **Depends On:** none
- **Agent Type:** `general-purpose`
- **Model / Effort:** sonnet / medium
- **Files:** `.gitignore`, `ai-docs/wiki/index.md`, `ai-docs/wiki/log.md`,
  `ai-docs/.obsidian/app.json`, `ai-docs/.obsidian/appearance.json`
- **Parallel:** true
- **Satisfies:** AC1, AC2
- **Verify:** `bash specs/wiki-layer/checks/ac1-privacy-gitignore.sh` and
  `uv run specs/wiki-layer/checks/ac2-seed.py` — both exit 0.
- Append the wiki block to `.gitignore` exactly as given in spec.md
  `## Interfaces & Contracts` (negations after the existing `ai-docs/*` rules; do
  not touch the existing mirror rules).
- Seed `ai-docs/wiki/index.md` and `ai-docs/wiki/log.md` exactly per spec.md
  `### Wiki seed shapes`: five shared-domain sections with empty
  `Page | Type | Status | Updated` tables; a `## Personal` section holding only
  the local-only pointer line; the log's entry contract
  `## [YYYY-MM-DD] <op> | <title> | <source-path>` with `<op>` ∈ `ingest|lint`.
- Write minimal `ai-docs/.obsidian/app.json` (`attachmentFolderPath: "wiki/assets"`,
  `alwaysUpdateLinks: true`) and `appearance.json` per the contract block.

### 2. Wiki Standards Rule

- **Task ID:** `wiki-standards-rule`
- **Depends On:** none
- **Agent Type:** `general-purpose`
- **Model / Effort:** opus / high
- **Files:** `.claude/rules/wiki-layer/wiki-standards.md`
- **Parallel:** true
- **Satisfies:** AC4
- **Verify:** `uv run pytest tests/harness-layer/test_wiki_layer.py::test_standards_rule -q`
  once the drift test lands; until then self-check against the content contract below.
- Author the layer's normative rule, path-scoped with `paths: ["ai-docs/wiki/**"]`,
  in fluent KISS prose per the repo's harness style. Content contract (see spec.md
  `## Interfaces & Contracts` for the frontmatter block): page frontmatter (seven
  core fields, status vocabulary and its propagation duty — disputed/superseded is
  flagged inline wherever cited); linking (`[[wikilinks]]` between wiki pages,
  markdown links to mirrors/repo files; **every claim traces to ≥1 source** — not
  merely one source somewhere on the page); writing standards distilled fresh from
  the farzaa study (theme-over-chronology, anti-cramming, anti-thinning, flat
  factual tone, quote discipline, length bounds); domain taxonomy (the six
  domains, per-domain page types, folders created on first need); privacy —
  `personal/` is local-only with its own `personal/index.md` + `personal/log.md`
  (shared index/log never name personal content), personal attachments live under
  `wiki/personal/assets/`, and secret/PII stripping applies to every ingest;
  Obsidian (vault root `ai-docs/`, supported plugins Web Clipper / Dataview /
  Marp — recommended, never required); layer requirements (lane fit, the four
  metrics targets, archetype staffing) as agreed in decisions.md — including an
  **operations table** mapping each command to its model/effort stamp
  (ingest: opus/high · query: sonnet/high · lint: opus/high · status:
  haiku/medium), which the drift test treats as the source of truth for command
  frontmatter.

### 3. Commands: ingest + lint

- **Task ID:** `wiki-commands-ingest-lint`
- **Depends On:** `wiki-standards-rule`
- **Agent Type:** `general-purpose`
- **Model / Effort:** opus / high
- **Files:** `.claude/commands/wiki/ingest.md`, `.claude/commands/wiki/lint.md`
- **Parallel:** true
- **Satisfies:** AC3, AC7
- **Verify:** `uv run pytest tests/harness-layer/test_wiki_layer.py -q` (structural,
  once the drift test lands); behavioral proof is the `pilot-eval` task exercising
  both commands against `specs/wiki-layer/checks/fixtures/`.
- Write `/wiki:ingest` per the Interfaces contract: argument = mirror path, local
  file/folder, or plan artifact (external URLs are refused with a pointer to
  `/harness-layer:kb add`); workflow reads the standards rule's schema, the wiki
  index, then the source; integrates across pages (create/update, never
  append-only), updates the domain's index + log — **shared for shared domains,
  `personal/index.md` + `personal/log.md` for personal** — recording the canonical
  source path in both the page's `sources:` frontmatter and the log entry (the
  idempotency key: a re-run on the same path updates in place, never duplicates);
  strips secrets/PII; batch input checkpoints every 5 sources; crystallization
  gate for plan artifacts (cited + non-duplicative, else decline with the reason).
- Write `/wiki:lint` per the contract: checks orphans, broken `[[links]]`, index ↔
  page drift, schema violations, stale pages, contradictions (both sides flagged
  `disputed`), **secret/PII leakage in page content across every domain**,
  missing-mirror citations (report "run `/harness-layer:kb`", never a broken
  citation), personal pages referencing files outside `personal/`,
  cramming/thinning signals; fixes mechanical findings itself, reports judgment
  findings; appends its log entry in the lint form —
  `## [date] lint | scope | summary` plus the payload line
  `missing-pages: page-a, page-b (or none) · mechanical-fixes: N` — which is the
  state status later consumes; documents the weekly-routine prompt (created
  once via `/schedule`: weekly cron, fresh clone, runs `/wiki:lint`, lands fixes
  as a `claude/`-branch PR) and notes personal/ is local-lint only.

### 4. Commands: query + status

- **Task ID:** `wiki-commands-query-status`
- **Depends On:** `wiki-standards-rule`
- **Agent Type:** `general-purpose`
- **Model / Effort:** sonnet / high
- **Files:** `.claude/commands/wiki/query.md`, `.claude/commands/wiki/status.md`
- **Parallel:** true
- **Satisfies:** AC3, AC7
- **Verify:** `uv run pytest tests/harness-layer/test_wiki_layer.py -q` (structural,
  once the drift test lands); behavioral proof is the `pilot-eval` task exercising
  both commands against the fixture-built wiki.
- Write `/wiki:query` per the contract: strictly read-only on the wiki (no page,
  index, or log writes); index → the smallest relevant page set, following links
  only while they materially add evidence; synthesize with page citations; flag
  any non-`current` status inline; when the wiki doesn't cover it, say so — never
  guess; close by naming crystallization when the answer qualifies (the user runs
  `/wiki:ingest` on it, which is what gets logged).
- Write `/wiki:status` per the contract: read-only readout of page counts by
  domain and type, orphan and disputed counts, last lint date from log.md, and
  the three expansion triggers **derived from tracked state**: absorb — count of
  `sources.yaml` entries whose mirror is cited by no wiki page's `sources:`
  (backlog >10 fires); breakdown — the same page name appearing in the
  `missing-pages:` payload of ≥3 consecutive lint log entries; cleanup — the
  `mechanical-fixes:` payload trending up across the last 3 lint entries. Both
  payload fields are defined by the log contract and written by lint before
  status ever reads them.

### 5. AGENTS.md Amendments

- **Task ID:** `agents-md-amendments`
- **Depends On:** `wiki-standards-rule`
- **Agent Type:** `general-purpose`
- **Model / Effort:** opus / high
- **Files:** `AGENTS.md`
- **Parallel:** false
- **Satisfies:** AC5
- **Verify:** `uv run specs/wiki-layer/checks/ac5-memory-amendments.py` — exit 0.
- Apply the exact Knowledge Base section rewrite and the new Wiki Layer subsection
  from spec.md `## Interfaces & Contracts`. Keep the addition ≤ 14 lines total;
  no rationale, no duplicated schema content (the rule owns it).

### 6. Wiki Drift Test

- **Task ID:** `wiki-drift-test`
- **Depends On:** `wiki-commands-ingest-lint`, `wiki-commands-query-status`,
  `wiki-standards-rule`, `agents-md-amendments`
- **Agent Type:** `general-purpose`
- **Model / Effort:** sonnet / high
- **Files:** `tests/harness-layer/test_wiki_layer.py`
- **Parallel:** false
- **Satisfies:** AC3, AC4, AC6
- **Verify:** `uv run pytest tests/harness-layer/test_wiki_layer.py -q` — green.
- Drift tier per test-tiers.md — the single durable home for the layer's
  structural assertions (no duplicate plan-local scripts). Expectations re-derive
  from sources of truth, never from the directory under test:
  - `test_command_registry`: parse the `/wiki:<name>` pointers from AGENTS.md's
    Wiki Layer section (the registration), require the set non-empty, and compare
    exactly — no missing commands, no unplanned files under
    `.claude/commands/wiki/`.
  - `test_command_frontmatter`: YAML-parse each command's frontmatter; assert the
    exact key set per command (description/model/effort, plus `argument-hint` for
    ingest and query — no extra keys); assert each command's exact model/effort
    equals the operations table parsed from the wiki-standards rule (the declared
    source of truth), and that those values are legal per
    `.claude/rules/model-selection.md`; query's body declares itself read-only.
  - `test_standards_rule`: YAML-parse the rule's frontmatter (`paths` covers
    `ai-docs/wiki/**`); parse its `##` headings and assert, section-scoped, every
    AC4 obligation: all seven core fields and three status values as code spans in
    the schema section; the every-claim-cites-≥1-source rule; the writing
    standards (anti-cramming, anti-thinning, theme-over-chronology markers); all
    six domains; the privacy obligations (personal-only index/log, personal
    assets under `wiki/personal/assets/`, secret/PII stripping); the plugin set
    (Web Clipper, Dataview, Marp); the operations table; the lane-fit statement;
    all four metrics targets; the archetype staffing.
  - Match the style of the existing drift tests in `tests/harness-layer/`.

### 7. Pilot Eval (pre-ship)

- **Task ID:** `pilot-eval`
- **Depends On:** `wiki-foundation`, `wiki-commands-ingest-lint`,
  `wiki-commands-query-status`, `agents-md-amendments`
- **Agent Type:** run by the build lead in a real session (manual — eval tier)
- **Model / Effort:** opus / high
- **Files:** `ai-docs/wiki/` pages produced by the fixture ingest,
  `specs/wiki-layer/implementation-notes.md` (evidence)
- **Parallel:** false
- **Satisfies:** AC7
- **Verify:** every pass condition in
  `specs/wiki-layer/checks/fixtures/pilot-rubric.md` observed and recorded in
  implementation-notes.md.
- Eval tier per test-tiers.md: a pass rate over repeated runs — a single green
  run proves nothing. Run the fixture flow **three times, each in a fresh
  session**: `/wiki:ingest specs/wiki-layer/checks/fixtures/article-a-llm-wiki-pattern.md`,
  then the same for `article-b-obsidian-vaults.md` (two related articles, so a
  legitimate `[[wikilink]]` between their pages exists); then `/wiki:query` with
  a question spanning both; then `/wiki:lint`. Run 1 starts from the seed; runs
  2–3 re-run against the existing pages, exercising the idempotency condition.
- Score every run against `checks/fixtures/pilot-rubric.md`; required pass rate
  is 3/3 on every condition. Record in implementation-notes.md per run: the
  exact commands, resulting page paths, index/log entries, the query answer's
  citations, and lint's output.

### 8. Validate Everything

- **Task ID:** `validate-all`
- **Depends On:** `wiki-foundation`, `wiki-standards-rule`, `wiki-commands-ingest-lint`,
  `wiki-commands-query-status`, `agents-md-amendments`, `wiki-drift-test`, `pilot-eval`
- **Agent Type:** a validator agent, or `general-purpose`
- **Model / Effort:** sonnet / high
- **Files:** none — read-only
- **Parallel:** false
- **Satisfies:** every AC
- **Verify:** every command in acceptance-criteria.md `## Validation Commands`
  passes from the repo root; AC7's evidence exists in implementation-notes.md and
  meets the rubric; each criterion is met.
