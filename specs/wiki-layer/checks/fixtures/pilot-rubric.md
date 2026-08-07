# Pilot Rubric — AC7 (pre-ship fixture eval)

Eval tier: the flow runs **three times, each in a fresh session** — run 1 from the
seed, runs 2–3 against the existing pages (idempotency). In order per run:
`/wiki:ingest` on fixture A, `/wiki:ingest` on fixture B, `/wiki:query` with one
question spanning both (e.g. "why does the wiki pattern pair well with
Obsidian?"), then `/wiki:lint`. Required pass rate: 3/3 runs meeting every
condition below; record per-run commands, page paths, and outputs in
implementation-notes.md.

## Pass conditions

1. **Pages** — each ingest produces or updates at least one page under
   `ai-docs/wiki/<shared-domain>/` with valid frontmatter: all seven core fields,
   `status: current`, and `sources:` containing the fixture's canonical path.
2. **Cross-link** — after ingest B, at least one legitimate `[[wikilink]]`
   connects the two pages' topics (the fixtures are related by design).
3. **Index** — `ai-docs/wiki/index.md` gains a row for each touched page in the
   correct domain section; the Personal section remains the pointer only.
4. **Log** — `ai-docs/wiki/log.md` gains one `## [date] ingest | <title> |
   <source-path>` entry per ingest, carrying the fixture paths.
5. **Idempotency** — re-running ingest on fixture A changes no page count and
   adds no duplicate index row (the log/frontmatter source path is the identity).
6. **Query** — the answer synthesizes across both pages, cites them by name, and
   flags nothing as disputed (nothing should be); no wiki file is modified.
7. **Lint** — reports clean (or only findings it fixed mechanically, with the
   fixes visible), and appends its own log entry.
8. **Privacy** — `git status` shows no changes under `ai-docs/wiki/personal/`
   and no personal content named in the shared index or log.
