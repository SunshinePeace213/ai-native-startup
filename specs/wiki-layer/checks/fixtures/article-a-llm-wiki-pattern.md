# The LLM Wiki Pattern: Knowledge That Compounds

> Pilot fixture A — a clipped-article stand-in. Source: fixture (committed with the
> plan); treat as a local file ingest.

Most document-chat systems retrieve and forget: every question rebuilds its answer
from raw chunks, and the synthesis evaporates when the session ends. The LLM wiki
pattern inverts this. An LLM incrementally builds and maintains a persistent wiki —
a structured, interlinked set of markdown pages sitting between the reader and the
raw sources.

The architecture has three layers. Raw sources are immutable; the LLM reads them
but never edits them. The wiki is the maintained layer: entity pages, topic
syntheses, comparisons, an index, a log — the LLM writes all of it. The schema is a
configuration document telling the LLM how the wiki is structured and what
workflows to follow; it is what turns a generic assistant into a disciplined
maintainer.

Three operations drive the loop. Ingest reads a new source and integrates it
across existing pages — a single source can touch a dozen pages. Query reads the
index, drills into relevant pages, and synthesizes an answer with citations; good
answers are filed back in, so exploration compounds like sources do. Lint is the
periodic health check: orphan pages, stale claims, contradictions, missing
cross-references.

The pattern's admirers point out that the bottleneck of human wikis was never the
reading or the thinking — it was the bookkeeping. Machines don't get bored, which
is why a maintained wiki finally became cheap. Practitioners typically browse the
result in a dedicated markdown editor while the LLM edits the same folder — two
programs, one set of files.
