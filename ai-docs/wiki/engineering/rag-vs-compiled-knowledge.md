---
type: comparison
domain: engineering
status: disputed
created: 2026-08-08
updated: 2026-08-08
sources: ["ai-docs/llm-wiki/karpathy/llm-wiki.md", "ai-docs/llm-wiki/lucianfialho/graphwiki-pattern.md", "ai-docs/llm-wiki/rohitg00/llm-wiki.md", ".claude/rules/wiki-layer/wiki-standards.md"]
related: ["[[llm-wiki-pattern]]", "[[wiki-index-and-log]]", "[[graph-wiki-variant]]", "[[ingest-pipeline]]"]
---

# RAG vs Compiled Knowledge

Two arrangements put an LLM between a reader and a document collection. The common one
retrieves at query time: files are uploaded, relevant chunks are pulled per question, and
an answer is generated — NotebookLM, ChatGPT file uploads, and most RAG systems work this
way ([Karpathy](../../llm-wiki/karpathy/llm-wiki.md)). The other compiles: when a source arrives
the LLM reads it, extracts the key information, and integrates it into a persistent
interlinked set of markdown pages that sits between the reader and the raw sources
([Karpathy](../../llm-wiki/karpathy/llm-wiki.md)). The two differ less in retrieval quality than
in when the synthesis work is done and whether it is kept.

## Where the synthesis happens

Under retrieval, a question that requires reconciling five documents has that
reconciliation performed at answer time, and performed again from scratch for the next
question ([Karpathy](../../llm-wiki/karpathy/llm-wiki.md)). Under compilation the reconciliation
happens once, at ingest, and is written down: the cross-references are already there, the
contradictions have already been flagged, and the synthesis already reflects everything
read ([Karpathy](../../llm-wiki/karpathy/llm-wiki.md)). Karpathy's phrasing for the result is that
the knowledge is "compiled once and then *kept current*, not re-derived on every query"
([Karpathy](../../llm-wiki/karpathy/llm-wiki.md)). Query then reads finished pages rather than
rebuilding an answer out of chunks.

## What accumulates

Adding a document to a retrieval system changes nothing about the collection except what
is searchable; the LLM rediscovers knowledge from scratch on every question and nothing is
built up ([Karpathy](../../llm-wiki/karpathy/llm-wiki.md)). Compilation makes the wiki a persistent,
compounding artifact that gets richer with every source added and every question asked
([Karpathy](../../llm-wiki/karpathy/llm-wiki.md)). Questions compound on the same terms as sources:
a comparison, an analysis, or a discovered connection is filed back as a new page instead
of disappearing into chat history ([Karpathy](../../llm-wiki/karpathy/llm-wiki.md)). This
repository encodes that as a write rule — crystallizing a query answer is itself an
ingest, and query stays read-only
([wiki-standards.md](../../../.claude/rules/wiki-layer/wiki-standards.md)).

One extension pushes filing-back from an option to a defined operation. Crystallization
there means taking a completed chain of work — a research thread, a debugging session, an
analysis — and distilling it automatically into a structured digest recording what the
question was, what was found, which entities were involved, and what lessons emerged, with
the digest becoming a first-class page and the lessons extracted as standalone facts
([LLM Wiki v2](../../llm-wiki/rohitg00/llm-wiki.md)). The framing is that explorations are a source
like any article or paper and the wiki should ingest them as one
([LLM Wiki v2](../../llm-wiki/rohitg00/llm-wiki.md)). Whether an answer earns that treatment is
proposed as an automatic check against a quality threshold rather than a human decision
([LLM Wiki v2](../../llm-wiki/rohitg00/llm-wiki.md)).

## Retrieval does not disappear, it moves

Compiling does not remove the problem of finding things; it moves the problem from chunks
to pages. At moderate scale — Karpathy's figure is roughly 100 sources and hundreds of
pages — a maintained catalog file is enough to navigate, which avoids embedding-based RAG
infrastructure altogether ([Karpathy](../../llm-wiki/karpathy/llm-wiki.md)) *[disputed — see
[[wiki-index-and-log]]]*. That mechanism is the subject of [[wiki-index-and-log]]. Past
that scale, search over the wiki is named as the
most obvious CLI tool to build, with `qmd` — a local markdown search engine combining
BM25 and vector search with LLM re-ranking, exposed as both a CLI and an MCP server — as
one option ([Karpathy](../../llm-wiki/karpathy/llm-wiki.md)). Search in that setup runs over
compiled pages, so it is retrieval layered on top of synthesis rather than in place of it.

A production account puts the ceiling lower and treats crossing it as inevitable rather
than optional. A single catalog file is reported to work up to maybe 100 to 200 pages,
beyond which the index itself becomes too long for the LLM to read in one pass and real
search is required ([LLM Wiki v2](../../llm-wiki/rohitg00/llm-wiki.md)) *[disputed — see
[[wiki-index-and-log]], which carries the higher figure]*. Its recommendation is to keep
the catalog as a human-readable artifact but stop relying on it as the primary retrieval
mechanism past roughly 100 pages ([LLM Wiki v2](../../llm-wiki/rohitg00/llm-wiki.md)). The two
claims are estimates from different practitioners running different corpora and neither is
resolved by a measurement, so both are recorded.

The replacement proposed is three streams fused rather than one: BM25 for keyword matching
with stemming and synonym expansion, vector search for semantic similarity, and graph
traversal for entity-aware relationship walking, combined with reciprocal rank fusion
([LLM Wiki v2](../../llm-wiki/rohitg00/llm-wiki.md)). The argument for fusing is that each stream
catches what the others miss — exact terms, semantic similarity, and structural connections
respectively ([LLM Wiki v2](../../llm-wiki/rohitg00/llm-wiki.md)).

## Graph traversal against flat retrieval, measured

The claim that structural retrieval beats flat similarity has one published measurement.
Over an eight-document corpus and six questions each requiring two to three connected
documents, none answerable from a single document, flat top-k retrieval by cosine
similarity to the raw question retrieved all necessary documents for 4 of 6, while graph
traversal from an embedding-selected entry node retrieved all necessary documents for 6 of
6 at both two and three hops
([graphwiki](../../llm-wiki/lucianfialho/graphwiki-pattern.md)). The stated reason flat retrieval
loses is specific: it reliably misses the bridge document when that document is not itself
semantically close to the question text
([graphwiki](../../llm-wiki/lucianfialho/graphwiki-pattern.md)).

The result comes with its own counterweight. On 3 of the 6 questions the traversal pulled
in 5 or 6 of the 8 documents, giving precision as low as 0.33, so recall was solved and
precision was not ([graphwiki](../../llm-wiki/lucianfialho/graphwiki-pattern.md)). The author
attributes that to a small densely connected corpus and leaves precision at scale — bigger,
sparser graphs, and how many hops is too many — untested
([graphwiki](../../llm-wiki/lucianfialho/graphwiki-pattern.md)). The comparison is therefore
narrower than compiled-versus-retrieved: both arms here read a compiled corpus, and what is
being measured is how the compiled layer is traversed. [[graph-wiki-variant]] covers the
storage form that makes the traversal arm possible.

## Which one a body of work fits

Retrieval fits a collection consulted once and not revisited, where nothing would be
gained by keeping the reconciliation. Compilation fits accumulation over weeks or months —
Karpathy lists tracking one's own goals and health, going deep on a research topic,
reading a book chapter by chapter, an internal team wiki fed by threads and transcripts,
and cases like competitive analysis, due diligence, trip planning, and course notes
([Karpathy](../../llm-wiki/karpathy/llm-wiki.md)). The dividing question is whether the same
material will be asked about again; see [[llm-wiki-pattern]] for what the compiled side
costs to run.
