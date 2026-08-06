# Acceptance Criteria: Wiki Layer

> The definition of "done" for [spec.md](./spec.md). Every criterion is observable and
> testable, and every task in tasks.md maps to at least one criterion here.

## Acceptance Criteria

### Storage & privacy

- **AC1** — Wiki pages are tracked while the personal domain stays local-only:
  `git check-ignore` reports `ai-docs/wiki/personal/**` as ignored, and reports
  `ai-docs/wiki/index.md`, shared-domain pages, and `ai-docs/.obsidian/app.json` as
  NOT ignored, with `ai-docs/.obsidian/workspace*` ignored.
- **AC2** — The wiki seed exists: `ai-docs/wiki/index.md` (domain-grouped catalog
  with the documented column set), `ai-docs/wiki/log.md` (append-only, documents the
  `## [YYYY-MM-DD] <op> | <title>` entry format), and `ai-docs/.obsidian/app.json`
  (valid JSON, `attachmentFolderPath` = `wiki/assets`).

### Layer surface

- **AC3** — The command family exists: `.claude/commands/wiki/{ingest,query,lint,status}.md`,
  each with frontmatter carrying a non-empty `description`, a `model` alias and
  `effort` from `.claude/rules/model-selection.md`, and an `argument-hint` where the
  command takes arguments (ingest, query); query declares itself read-only in its
  body; each body implements its operation per spec.md `## Interfaces & Contracts`.
- **AC4** — The layer standards rule exists at
  `.claude/rules/wiki-layer/wiki-standards.md`, path-scoped to `ai-docs/wiki/**`,
  and states: the page frontmatter contract (all seven core fields with the status
  vocabulary), linking rules, writing standards, the domain taxonomy, the privacy +
  secret-stripping rule, the supported Obsidian plugin set, and the layer
  requirements (lane fit, metrics targets, archetypes).

### Memory integration

- **AC5** — AGENTS.md is amended: the Knowledge Base task-start protocol checks
  `ai-docs/wiki/index.md` before `ai-docs/index.md`; the durability rule routes
  gate-passing synthesis into the wiki (crystallization); a Wiki Layer section
  registers the layer with pointers to the commands and the standards rule. Total
  addition ≤ 14 lines.

### Verification

- **AC6** — The drift test `tests/harness-layer/test_wiki_layer.py` passes: it
  re-derives the wiki command set from `.claude/commands/wiki/*.md`, parses each
  frontmatter (never substring-scans prose), asserts model/effort values against
  the model-selection roster, and asserts the standards rule's `paths` scoping.
- **AC7** — Pilot (manual, user-run, post-ship): a fresh web article clipped via
  Obsidian Web Clipper is ingested with `/wiki:ingest`; the resulting page has valid
  frontmatter, ≥1 `[[wikilink]]` and ≥1 source citation, appears in
  `ai-docs/wiki/index.md` and the Obsidian graph; `/wiki:query` answers a question
  about it with a citation; `/wiki:lint` reports clean. Output recorded in
  implementation-notes.md.

## Validation Commands

### AC1 — privacy boundary holds in git semantics

- `bash specs/wiki-layer/checks/ac1-privacy-gitignore.sh` — pass: exit 0 (personal
  ignored; wiki core, shared domains, and Obsidian config tracked; workspace files
  ignored). Fails on the untouched tree because `ai-docs/*` ignores everything.

### AC2 — wiki seed structure

- `uv run specs/wiki-layer/checks/ac2-seed.py` — pass: exit 0 (index.md with domain
  grouping, log.md with entry-format contract, app.json valid JSON with
  `attachmentFolderPath` = `wiki/assets`).

### AC3 — command family contract

- `uv run specs/wiki-layer/checks/ac3-commands.py` — pass: exit 0 (all four files
  present; frontmatter parses; required keys and value constraints hold).

### AC4 — standards rule contract

- `uv run specs/wiki-layer/checks/ac4-standards-rule.py` — pass: exit 0 (paths
  scoping correct; all required schema fields, status values, and layer-requirement
  sections present).

### AC5 — AGENTS.md amendments

- `uv run specs/wiki-layer/checks/ac5-memory-amendments.py` — pass: exit 0
  (wiki-first order, crystallization amendment, layer registration all present;
  addition size within budget).

### AC6 — drift test

- `uv run pytest tests/harness-layer/test_wiki_layer.py -q` — pass: pytest green.
  Fails when the change is reverted (the test file and its targets are absent).

### AC7 — pilot migration

- `manual: user clips one fresh web article, runs /wiki:ingest on the clipped file,
  then /wiki:query with a question about the article, then /wiki:lint` — pass: all
  AC7 conditions observed; transcript + resulting page path recorded in
  implementation-notes.md.
