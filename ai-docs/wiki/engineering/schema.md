# Engineering Schema

Types beyond the core five: `tool` (a piece of software and the property that
makes it fit), `architecture` (how a system's layers fit together),
`failure-mode` (a recurring way engineering work goes wrong).

Layout: flat pages in `engineering/`, no hub page. Kebab-case file names
matching the page title.

Current pages use `pattern`, `comparison`, and `topic` (core) plus all three domain
types — `tool`, `architecture`, and `failure-mode`. Co-evolve this file as the domain
grows — ingest edits it freely.

Raw sources are grouped by topic rather than by site: the LLM-wiki material lives under
`ai-docs/llm-wiki/<author>/<slug>.md`, one folder per author. Pages cite those paths
directly, so a source that moves needs every citing page and log entry rewritten with it.
