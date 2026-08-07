---
source: https://gist.githubusercontent.com/lucianfialho/44034e0d02a2bfccca2ad6358bde1dff/raw/87cfb3057d450c0d8124994d4e9ff687dfff7cbf/graphwiki-pattern.md
fetched: 2026-08-07
---
> **In here:** graphwiki schema (Source/Concept/Claim nodes, typed edges) · ingest/query/lint pipeline · entity-resolution and graph-vs-flat-RAG benchmarks

# graphwiki: an LLM Wiki pattern for graph databases

Inspired by [Karpathy's LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f), which proposes a persistent, LLM-maintained knowledge base that compounds over time instead of re-deriving answers from raw sources on every query.

The original pattern stores the maintained layer as markdown pages with freeform links. This variant stores it as a property graph, so the "cross-references" a markdown wiki approximates with links become real, typed, queryable edges — and the retrieval step gets to use graph algorithms instead of just following links.

## The three layers

1. **Raw Sources** — immutable `:Source` nodes. Original text, never modified after ingest.
2. **Graph Wiki** — the maintained layer. `:Concept` nodes (a synthesized entity or topic, with a prose `summary` — this is the "page" equivalent) and `:Claim` nodes (atomic assertions extracted from a source), connected by typed relationships.
3. **Schema** — a small, fixed set of node labels and relationship types (below), enforced with Neo4j constraints. Fixed and generic on purpose: it keeps queries simple (`MATCH (:Concept)` always works) at the cost of some domain expressiveness. Domain nuance lives in node properties (`type: 'Gene'`), not in new labels.

## Vocabulary

**Nodes**
- `:Source {id, text, ingested_at}` — immutable
- `:Concept {id, name, type, summary, embedding, status, created_at, updated_at}`
- `:Claim {id, text, embedding, status, created_at}`

`status` is `current | superseded | disputed`. Two claims linked by `CONTRADICTS` with no resolution are both `disputed`. When a later source resolves the conflict, the losing claim flips to `superseded` — it is never deleted, so the graph keeps its own history instead of quietly rewriting the past.

**Relationships**
- `RELATES_TO` — generic association (concept↔concept, claim↔concept)
- `CONTRADICTS` — conflicting claims or concepts
- `DERIVED_FROM` — provenance; this *is* the citation
- `PART_OF` — hierarchy / composition

Four relationship types is deliberately narrow. `RELATES_TO` ends up doing double duty (structural links and claim-to-concept links) — a real implementation should watch whether that ambiguity ever causes wrong query results, and split it if so.

## INGEST

1. Create an immutable `:Source` node for the raw text.
2. An LLM extracts candidate `:Concept`s and `:Claim`s **against the fixed schema** — giving the extractor a schema to fill produces structured, typed output; asking it to "extract triples" does not.
3. Entity resolution is two stages, not a single cosine threshold — see [Benchmarks](#benchmarks) for why a single threshold measurably doesn't work:
   - **Stage 1 (cheap candidate filter)**: embed name + context, vector-search existing `:Concept` nodes (Neo4j native vector index). Anything below a low threshold (~0.55, calibrated so it only screens out the obviously-unrelated) is auto-rejected — **CREATE**, no LLM call spent.
   - **Stage 2 (LLM judgment)**: everything that clears stage 1 is a real candidate, and gets one explicit judgment call — "is this the same real-world entity as X, or just related?" — not a formula. `SAME` → **MERGE** into the existing node, refresh its `summary`. `NOT_SAME` → **CREATE** new node, `RELATES_TO` the existing one so the connection isn't lost.
   - This costs one LLM call per candidate that clears stage 1, not per source — budget for it, but it's not per-mention.
4. Link new claims `DERIVED_FROM` the source and `RELATES_TO` the concept they're about.
5. If a new claim conflicts with an existing one about the same concept, link them `CONTRADICTS`.

## QUERY

The question shape picks the algorithm, not just "traverse N hops":

| Question shape | Technique |
|---|---|
| "What is X" | N-hop traversal from the entry node, gather `DERIVED_FROM` sources for citation |
| "What else relates to X" | Personalized PageRank seeded at X |
| "How does X connect to Y" | Shortest path; the intermediate nodes *are* the explanation |
| "Find something shaped like X" | Subgraph pattern matching |

An LLM synthesizes the final natural-language answer from whatever subgraph was retrieved, always citing through `DERIVED_FROM`. Any `:Claim` or `:Concept` cited with `status != current` must be flagged inline ("X is declarative *[disputed — see claim-2]*") rather than presented as settled fact — status travels with the data all the way to the answer instead of getting silently dropped at read time.

## LINT

- Orphaned `:Concept` nodes (no `RELATES_TO`/`PART_OF`/`DERIVED_FROM`)
- Unresolved `CONTRADICTS` pairs (`status = disputed`) — not necessarily a problem to *fix*, but every one should be a deliberate state, not a forgotten one
- `NOT_SAME` judgments from stage 2 that a human hasn't spot-checked — the LLM call replaces the formula, but it can still be wrong, so a sample of its `RELATES_TO` calls (not just its `MERGE` calls) belongs in LINT
- Staleness — sources/concepts that haven't been touched by a re-ingest in N days

Drift — the agent under-updating cross-references or `status` on ingest — is the most common failure mode reported for this pattern in general (markdown or graph). LINT should run on a schedule (cron/CI), not only when someone remembers to ask; the graph stays healthy in proportion to how automatic that check is.

## Validated with a smoke test

Ran the full cycle against a real Neo4j 5 instance (Docker, with the GDS plugin for PageRank) instead of leaving this purely speculative:

- **Schema**: uniqueness constraints on `:Source/:Concept/:Claim.id` + native vector indexes on `:Concept.embedding` and `:Claim.embedding`.
- **Ingest**: fed 3 short texts about Neo4j/Cypher/GDS. Entity resolution correctly merged a same-name mention and a synonym ("CQL") into one `Cypher` node (cosine ≈ 1.0), while correctly keeping a related-but-distinct concept (`Neo4j GDS`, cosine ≈ 0.95 vs `Neo4j`) as its own node — exactly the "garlic vs. minced garlic vs. garlic cloves" problem the pattern is meant to solve.
- **Query**: traversal returned the right 1/2-hop neighborhoods with citations; `gds.pageRank.stream` with `sourceNodes` ran real Personalized PageRank and ranked directly-connected concepts above indirect ones; `shortestPath` correctly explained an indirect relationship as a chain through two intermediate concepts.
- **Lint**: correctly found zero orphans, surfaced the one unresolved contradiction (two claims about whether Cypher is declarative or imperative), and flagged the `Neo4j`/`Neo4j GDS` pair for review without auto-merging them.

This is the graph those three sources actually produced — `Cypher`/`CQL` merged into one node, `Neo4j GDS` stayed separate from `Neo4j`, and the two `Cypher: declarative` / `Cypher: imperative` claims are linked by the `CONTRADICTS` edge on the right:

![The resulting graph: 4 Concept nodes (Cypher, Neo4j, Neo4j GDS, Personalized PageRank), 3 Source nodes, 2 Claim nodes linked by CONTRADICTS](https://gist.githubusercontent.com/lucianfialho/44034e0d02a2bfccca2ad6358bde1dff/raw/graphwiki-graph.png)

Caveats from the test worth flagging honestly:
- Embeddings were hand-authored 8-dim vectors, not from a real embedding model, and the merge/reject decision was scripted (I picked the answer in advance) rather than judged. **This turned out to matter a lot — see [Benchmarks](#benchmarks) below, which replaced this assumption with measured results.**
- Staleness lint wasn't exercised — needs wall-clock time, not meaningfully testable with a scripted one-shot run.
- This was a single ingest session with no update/re-ingest cycle, so summary-merging behavior over time (a `:Concept` whose summary gets rewritten across multiple future sources) is untested.

## Benchmarks

![Entity resolution (precision/recall/F1: pure cosine threshold vs two-stage filter+LLM judge) and multi-hop question coverage (flat RAG vs graph traversal, 4/6 vs 6/6)](https://gist.githubusercontent.com/lucianfialho/44034e0d02a2bfccca2ad6358bde1dff/raw/benchmark-chart.png)

The smoke test above validated that the *mechanism* runs end-to-end. It didn't validate that the mechanism is *right* — the entity-resolution thresholds and the "graph beats flat retrieval" claim were both still assumptions. Tested both for real:

**1. Pure cosine-threshold entity resolution — measurably doesn't work.** 45 labeled mention pairs (`same` / `related-but-distinct` / `unrelated`) across several domains, real embeddings (`all-MiniLM-L6-v2` and `BAAI/bge-small-en-v1.5`, not hand-authored vectors). With bge-small: `same` pairs scored mean cosine 0.76, `related` pairs scored mean **0.78** — related-but-distinct entities were *more* similar on average than true synonyms (`AWS`/`Azure` at 0.87 outscored `Cypher`/`CQL` at 0.85). No threshold cleanly separates the classes; best achievable was F1=0.667 (precision 0.542) at threshold 0.72. The 0.97 guessed in the original smoke test was never viable — at 0.97, recall is ~0. Root cause: semantic-similarity embeddings measure "same topic," not "same real-world entity" — a different task than the one this pattern was asking them to do.

**2. Two-stage fix (cheap filter + LLM judgment) — F1 1.000 on the same data.** Same 45 pairs, but: a low threshold (0.55, chosen because it sits cleanly above the `unrelated` max of 0.50 and below the `same`/`related` min of 0.64) filters out the 15 obviously-unrelated pairs for free, then each of the 30 remaining candidates gets one real LLM judgment ("same entity or just related?") instead of a formula. All 30 were classified correctly. Caveat: these are common technical/general-knowledge terms (AWS, Kubernetes, NYC) — an LLM's world knowledge could be doing real work here for free. Tested that specifically next.

**3. Graph traversal beats flat semantic RAG on multi-hop questions — 6/6 vs 4/6.** 8-document real-facts corpus (Neo4j/Cypher/GDS/Docker/Kubernetes ecosystem) and 6 questions each requiring 2-3 connected documents to answer, none answerable from a single document. Flat RAG (top-k over cosine similarity to the raw question) retrieved all necessary documents for only 4/6 — it reliably misses the "bridge" document when that document isn't itself semantically close to the question text. Graph traversal (embedding-based entry node, then N hops over `RELATES_TO`/`PART_OF`) got 6/6 at both 2 and 3 hops. Caveat: this is the flip side of a small, densely-connected corpus — on 3 of 6 questions the traversal pulled in 5-6 of the 8 documents (precision as low as 0.33), not just the needed ones. Recall was solved; precision at scale (bigger, sparser graphs, how many hops is *too many*) is not tested here.

**4. Two-stage fix still holds with zero prior knowledge — F1 1.000 on an invented domain.** Result 2's biggest caveat was that the judging LLM might just be recalling AWS/Kubernetes/NYC facts instead of genuinely resolving identity from context. Re-ran the same 45-pair design (15 same / 15 related / 15 unrelated) against two fully invented technical domains — a fictional distributed-compute system and a fictional metallurgy process, entities that exist nowhere outside this test, so nothing could be recalled. Same result: F1 1.000. A second finding fell out of this run: the stage-1 threshold (0.55) that cleanly separated classes on the first domain did *not* transfer — one unrelated pair leaked through as a candidate in the new domain (cosine 0.60, above threshold). Stage 2 caught it and correctly rejected it anyway. That's the actual argument for the two-stage design over threshold-tuning: stage 1 doesn't need to be perfect or portable across domains, because stage 2 backstops it. Caveat this doesn't remove: the invented context sentences were written with fairly explicit distinguishing clues ("QDX is a density measurement, not a defect") — real extracted text from real sources is messier and less generous than that.

## Informed by the comment thread

The original gist's comments turned into a small survey of independently-built variants (Obsidian + graph view, NetworkX + ChromaDB hybrids, a Ruby gem with a live graph server, several local-first apps). A pattern in the discussion there shaped the `status` field above: multiple people converged on drift/staleness as the dominant failure mode, and one comment in particular ("grade the trust and make it travel — every page carries status ... so a stale or disputed page degrades honestly instead of silently") is why `status` propagates all the way to the QUERY answer instead of just living in LINT output.

## Open questions

- Does `RELATES_TO` need splitting once real usage shows the ambiguity above causes bad query results?
- Contradiction detection here was scripted (I decided claim-1 and claim-2 conflicted); in a real ingest an LLM has to make that call from claim text alone — worth a dedicated eval, same shape as the entity-resolution one that already got tested.
- Who/what flips a `disputed` claim to `superseded`? Scripted here as a manual decision; in practice this is either an LLM judgment call at ingest time or a human review gate — unresolved which fits better.
- Graph traversal fixed the recall problem on a small dense corpus but revealed a precision problem (5-6 of 8 docs pulled for some questions). At what corpus size/sparsity does "just add a hop" stop being the right answer, and what replaces it — tighter relationship typing, edge weights, a max-fanout cutoff?
- Stage-2 judgment held up on invented terms too, but only with generously explicit context sentences. Does it still hold on real extracted text, which is messier and more implicit than either test corpus here?
- Stage-1 threshold didn't transfer between the two entity-resolution domains tested (0.55 leaked one pair on the second). Is there a threshold-free stage-1 filter (kNN count instead of a fixed cutoff, for example) that doesn't need re-tuning per domain?
