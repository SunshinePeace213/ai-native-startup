# Acceptance Criteria: Wiki Layer

> The definition of "done" for [spec.md](./spec.md). Every criterion is observable and
> testable, and every task in tasks.md maps to at least one criterion here.

## Acceptance Criteria

### Storage & privacy

- **AC1** — Wiki pages are tracked while the personal domain stays local-only:
  `git check-ignore` semantics prove every shared-domain namespace and the
  Obsidian config are NOT ignored, `ai-docs/wiki/personal/**` (including its own
  index, log, and assets) IS ignored, `ai-docs/.obsidian/workspace*` variants are
  ignored, and `git ls-files` shows zero tracked files under
  `ai-docs/wiki/personal/`.
- **AC2** — The wiki seed matches spec.md `### Wiki seed shapes`:
  `ai-docs/wiki/index.md` has the five shared-domain sections each with a
  `Page | Type | Status | Updated` table and a Personal section holding only the
  local-only pointer; `ai-docs/wiki/log.md` documents the
  `## [YYYY-MM-DD] <op> | <title> | <source-path>` contract with `<op>` ∈
  `ingest|lint`; `ai-docs/.obsidian/app.json` is valid JSON with
  `attachmentFolderPath` = `wiki/assets` and `alwaysUpdateLinks` = true.

### Layer surface

- **AC3** — The command family matches its registration: the command set derived
  from AGENTS.md's Wiki Layer section equals the files under
  `.claude/commands/wiki/` (no missing, no unplanned); each frontmatter parses
  with non-empty `description`, `model`/`effort` from the model-selection roster,
  `argument-hint` on ingest and query; query's body declares itself read-only.
- **AC4** — The standards rule at `.claude/rules/wiki-layer/wiki-standards.md` is
  path-scoped to `ai-docs/wiki/**` and structurally contains: the seven-field
  frontmatter schema with the three status values, linking + every-claim-cites
  rules, writing standards, the six-domain taxonomy, the privacy section
  (personal-only index/log, personal assets, secret/PII stripping), the Obsidian
  section (Web Clipper / Dataview / Marp), and the layer requirements (lane fit,
  metrics, archetypes).

### Memory integration

- **AC5** — AGENTS.md is amended: within the Knowledge Base section the wiki
  index is named before the mirror index and the durability rule routes
  gate-passing synthesis into the wiki via `/wiki:ingest`; a Wiki Layer section
  registers all four commands and points at the standards rule. Total addition
  ≤ 14 lines.

### Verification

- **AC6** — The full drift suite `tests/harness-layer/test_wiki_layer.py` passes,
  with expectations re-derived from AGENTS.md, model-selection.md, and the rule
  file itself — never from the directory under test.
- **AC7** — Pre-ship fixture pilot, run by the build lead in a real session:
  ingesting the two committed fixture articles produces pages passing every
  condition in `specs/wiki-layer/checks/fixtures/pilot-rubric.md` (valid
  frontmatter with source paths, a legitimate `[[wikilink]]` between the two
  pages, shared index + log entries carrying source paths, a `/wiki:query` answer
  across both with citations, `/wiki:lint` clean), with the evidence recorded in
  implementation-notes.md. The user's fresh-article migration stays a post-ship
  follow-up on issue #88, outside this definition of done.

## Validation Commands

### AC1 — privacy boundary holds in git semantics

- `bash specs/wiki-layer/checks/ac1-privacy-gitignore.sh` — pass: exit 0. Fails on
  the untouched tree because `ai-docs/*` ignores everything.

### AC2 — wiki seed structure

- `uv run specs/wiki-layer/checks/ac2-seed.py` — pass: exit 0 (structured parse of
  domain sections + tables, personal pointer, log contract incl. source-path field
  and `ingest|lint` vocabulary, both app.json properties).

### AC3 — command family contract

- `uv run pytest tests/harness-layer/test_wiki_layer.py::test_command_registry tests/harness-layer/test_wiki_layer.py::test_command_frontmatter -q`
  — pass: green. Fails when reverted (test file absent).

### AC4 — standards rule contract

- `uv run pytest tests/harness-layer/test_wiki_layer.py::test_standards_rule -q`
  — pass: green.

### AC5 — AGENTS.md amendments

- `uv run specs/wiki-layer/checks/ac5-memory-amendments.py` — pass: exit 0
  (section-scoped assertions + size budget).

### AC6 — full drift suite

- `uv run pytest tests/harness-layer/test_wiki_layer.py -q` — pass: green.

### AC7 — fixture pilot (pre-ship)

- `manual: build lead runs /wiki:ingest on checks/fixtures/article-a-llm-wiki-pattern.md,
  then on article-b-obsidian-vaults.md, then /wiki:query with a question spanning
  both, then /wiki:lint` — pass: every pilot-rubric.md condition observed; commands,
  page paths, and outputs recorded in implementation-notes.md.
