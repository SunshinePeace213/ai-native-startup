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

### Phase 4: Validation

Tasks: `validate-all`.

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
- Seed `ai-docs/wiki/index.md`: title, one-line purpose, the six domain sections
  (engineering, business, development, books, articles, personal — personal marked
  local-only), each with an empty catalog table (`Page | Type | Status | Updated`),
  and a footer note that ingest maintains this file.
- Seed `ai-docs/wiki/log.md`: title, the entry-format contract line documenting
  `## [YYYY-MM-DD] <op> | <title>` with `<op>` ∈ ingest|query|lint|status, and no
  entries yet.
- Write minimal `ai-docs/.obsidian/app.json` (`attachmentFolderPath: "wiki/assets"`,
  `alwaysUpdateLinks: true`) and `appearance.json` (defaults) per the contract block.

### 2. Wiki Standards Rule

- **Task ID:** `wiki-standards-rule`
- **Depends On:** none
- **Agent Type:** `general-purpose`
- **Model / Effort:** opus / high
- **Files:** `.claude/rules/wiki-layer/wiki-standards.md`
- **Parallel:** true
- **Satisfies:** AC4
- **Verify:** `uv run specs/wiki-layer/checks/ac4-standards-rule.py` — exit 0.
- Author the layer's normative rule, path-scoped with `paths: ["ai-docs/wiki/**"]`,
  in fluent KISS prose per the repo's harness style. Content contract (see spec.md
  `## Interfaces & Contracts` for the frontmatter block): page frontmatter (seven
  core fields, status vocabulary and its propagation duty — disputed/superseded is
  flagged inline wherever cited); linking (`[[wikilinks]]` between wiki pages,
  markdown links to mirrors/repo files; cite ≥1 source per claim-bearing page);
  writing standards distilled fresh from the farzaa study (theme-over-chronology,
  anti-cramming, anti-thinning, flat factual tone, quote discipline, length
  bounds); domain taxonomy (the six domains, per-domain page types, folders created
  on first need, `personal/` local-only) ; privacy (secret/PII stripping on every
  ingest; personal attachments under `wiki/personal/assets/`); Obsidian (vault root
  `ai-docs/`, supported plugins Web Clipper / Dataview / Marp — recommended, never
  required); layer requirements (lane fit, the four metrics targets, archetype
  staffing) as agreed in decisions.md.

### 3. Commands: ingest + lint

- **Task ID:** `wiki-commands-ingest-lint`
- **Depends On:** `wiki-standards-rule`
- **Agent Type:** `general-purpose`
- **Model / Effort:** opus / high
- **Files:** `.claude/commands/wiki/ingest.md`, `.claude/commands/wiki/lint.md`
- **Parallel:** true
- **Satisfies:** AC3 (ingest, lint)
- **Verify:** `uv run specs/wiki-layer/checks/ac3-commands.py` — no failures naming
  ingest.md or lint.md.
- Write `/wiki:ingest` per the Interfaces contract: argument = mirror path, local
  file/folder, or plan artifact (external URLs are refused with a pointer to
  `/harness-layer:kb add`); workflow reads the standards rule's schema, the wiki
  index, then the source; integrates across pages (create/update, never
  append-only), updates index + log, strips secrets/PII; batch input checkpoints
  every 5 sources; crystallization gate for plan artifacts (cited +
  non-duplicative, else decline with the reason).
- Write `/wiki:lint` per the contract: checks orphans, broken `[[links]]`, index ↔
  page drift, schema violations, stale pages, contradictions
  (both sides flagged `disputed`), missing-mirror citations (report "run /kb",
  not broken), cramming/thinning signals; fixes mechanical findings itself,
  reports judgment findings; appends a log entry; documents the weekly-routine
  prompt (`/schedule`, weekly, runs `/wiki:lint`, lands fixes as a PR) and notes
  personal/ is local-lint only.

### 4. Commands: query + status

- **Task ID:** `wiki-commands-query-status`
- **Depends On:** `wiki-standards-rule`
- **Agent Type:** `general-purpose`
- **Model / Effort:** sonnet / high
- **Files:** `.claude/commands/wiki/query.md`, `.claude/commands/wiki/status.md`
- **Parallel:** true
- **Satisfies:** AC3 (query, status)
- **Verify:** `uv run specs/wiki-layer/checks/ac3-commands.py` — no failures naming
  query.md or status.md.
- Write `/wiki:query` per the contract: strictly read-only on the wiki; index →
  3–8 pages → links up to 2 hops; synthesize with page citations; flag any
  non-`current` status inline; when the wiki doesn't cover it, say so — never
  guess; close by naming crystallization when the answer qualifies (user runs
  `/wiki:ingest` on it).
- Write `/wiki:status` per the contract: page counts by domain and type, orphan
  and disputed counts, last lint date from log.md, and the expansion-trigger
  readout (unprocessed-source backlog vs the absorb threshold).

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
- **Depends On:** `wiki-commands-ingest-lint`, `wiki-commands-query-status`, `wiki-standards-rule`
- **Agent Type:** `general-purpose`
- **Model / Effort:** sonnet / medium
- **Files:** `tests/harness-layer/test_wiki_layer.py`
- **Parallel:** false
- **Satisfies:** AC6
- **Verify:** `uv run pytest tests/harness-layer/test_wiki_layer.py -q` — green.
- Drift tier per test-tiers.md: re-derive the expected command set from
  `.claude/commands/wiki/*.md`; parse each file's frontmatter (structure, not
  substrings) asserting description present, `model` ∈ the model-selection roster
  aliases, `effort` ∈ its effort levels, `argument-hint` on ingest/query; parse
  the standards rule's frontmatter asserting `paths` covers `ai-docs/wiki/**`.
  Match the style of the existing drift tests in `tests/harness-layer/`.

### 7. Validate Everything

- **Task ID:** `validate-all`
- **Depends On:** `wiki-foundation`, `wiki-standards-rule`, `wiki-commands-ingest-lint`,
  `wiki-commands-query-status`, `agents-md-amendments`, `wiki-drift-test`
- **Agent Type:** `general-purpose`
- **Model / Effort:** sonnet / high
- **Files:** none — read-only
- **Parallel:** false
- **Satisfies:** every AC (AC7 verified as "pilot procedure documented and
  runnable"; its execution is the user's post-ship step)
- **Verify:** every command in acceptance-criteria.md `## Validation Commands`
  passes from the repo root, and each criterion is met.
