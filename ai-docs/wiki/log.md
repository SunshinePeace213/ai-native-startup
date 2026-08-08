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

## [2026-08-08] ingest | LLM Wiki (Karpathy) | ai-docs/llm-wiki/karpathy/llm-wiki.md

## [2026-08-08] ingest | Personal Knowledge Wiki skill (farzaa) | ai-docs/llm-wiki/farzaa/wiki-gen-skill.md

## [2026-08-08] ingest | graphwiki: an LLM Wiki pattern for graph databases (lucianfialho) | ai-docs/llm-wiki/lucianfialho/graphwiki-pattern.md

## [2026-08-08] ingest | LLM Wiki v2 (rohitg00) | ai-docs/llm-wiki/rohitg00/llm-wiki.md

## [2026-08-08] lint | engineering | 13 pages — no orphans or broken links; 2 fixes, 3 findings for review

missing-pages: none · mechanical-fixes: 2

## [2026-08-09] ingest | Graph Engineering for Multi-Agentic Systems: The Andrew Ng Playbook | ai-docs/graph-engineering/index.md

new-domain: agentic-systems (11 pages) · enriched: engineering/graph-wiki-variant
