# Wiki Log

<!-- markdownlint-disable MD024 -->

Append-only history of writes to the shared wiki. Only `ingest` and `lint` write
here — `query` and `status` are read-only and never add an entry.

Ingest entries:

```text
## [YYYY-MM-DD] ingest | <title> | <source-path>
```

Lint entries, followed by the payload line:

```text
## [YYYY-MM-DD] lint | <scope> | <summary>
missing-pages: <comma-list or none> · mechanical-fixes: <N>
```

## [2026-08-07] ingest | LLM Wiki Pattern | specs/wiki-layer/checks/fixtures/article-a-llm-wiki-pattern.md

## [2026-08-07] ingest | Obsidian Vault | specs/wiki-layer/checks/fixtures/article-b-obsidian-vaults.md

## [2026-08-07] lint | engineering | clean — 2 pages checked, no findings

missing-pages: none · mechanical-fixes: 0

## [2026-08-07] lint | engineering | clean — 2 pages, index and log consistent

missing-pages: none · mechanical-fixes: 0

## [2026-08-07] lint | engineering | clean — 2 pages, index and log consistent

missing-pages: none · mechanical-fixes: 0

## [2026-08-08] lint | engineering | domain retired — the two pilot pages were built from dev fixtures, not real sources; pages, `schema.md`, and the index section removed, 0 pages remain

missing-pages: none · mechanical-fixes: 0
