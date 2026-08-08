---
type: topic
domain: engineering
status: current
created: 2026-08-08
updated: 2026-08-08
sources: ["ai-docs/llm-wiki/lucianfialho/graphwiki-pattern.md", "ai-docs/llm-wiki/rohitg00/llm-wiki.md", "ai-docs/llm-wiki/farzaa/wiki-gen-skill.md"]
related: ["[[graph-wiki-variant]]", "[[ingest-pipeline]]", "[[wiki-drift]]", "[[llm-wiki-pattern]]"]
---

# Entity Resolution

Every ingest into a maintained knowledge base makes the same decision: is this mention the
thing already recorded, or a different thing? Getting it wrong in one direction splits one
entity across two nodes; getting it wrong in the other merges two entities into one. The
worked example is "garlic vs. minced garlic vs. garlic cloves" — surface forms that are
near-identical in text and not interchangeable as entities
([graphwiki](../../llm-wiki/lucianfialho/graphwiki-pattern.md)). In the [[graph-wiki-variant]] the
decision is MERGE-or-CREATE on a `:Concept` node
([graphwiki](../../llm-wiki/lucianfialho/graphwiki-pattern.md)); in a markdown wiki it is the same
decision wearing different clothes, described below.

## Cosine similarity measures the wrong thing

The obvious implementation is a single embedding-similarity threshold, and it was measured
and rejected. Across 45 labeled mention pairs spanning several domains, classed `same` /
`related-but-distinct` / `unrelated`, with real embedding models rather than hand-authored
vectors, `same` pairs scored a mean cosine of 0.76 while `related-but-distinct` pairs
scored a mean of 0.78 ([graphwiki](../../llm-wiki/lucianfialho/graphwiki-pattern.md)). Related
entities were on average *more* similar than true synonyms: `AWS`/`Azure` at 0.87
outscored `Cypher`/`CQL` at 0.85 ([graphwiki](../../llm-wiki/lucianfialho/graphwiki-pattern.md)).

No threshold separates the classes cleanly. The best achievable result was F1 0.667 at
precision 0.542 with the cutoff at 0.72, and the 0.97 cutoff guessed in the design's
earlier smoke test drives recall to approximately zero
([graphwiki](../../llm-wiki/lucianfialho/graphwiki-pattern.md)). The stated root cause is a task
mismatch: semantic-similarity embeddings measure "same topic", not "same real-world
entity" ([graphwiki](../../llm-wiki/lucianfialho/graphwiki-pattern.md)).

## A cheap filter in front of a judgment

The replacement splits the decision in two. Stage one embeds name plus context, vector-
searches existing concepts, and auto-rejects anything below a deliberately low threshold —
0.55, chosen to sit above the `unrelated` maximum of 0.50 and below the `same`/`related`
minimum of 0.64 — so obviously-unrelated mentions become a CREATE with no LLM call spent
([graphwiki](../../llm-wiki/lucianfialho/graphwiki-pattern.md)). Stage two gives everything that
clears the filter one explicit judgment call, "is this the same real-world entity as X, or
just related?", rather than a formula
([graphwiki](../../llm-wiki/lucianfialho/graphwiki-pattern.md)). `SAME` merges into the existing
node and refreshes its summary; `NOT_SAME` creates a new node and links it to the existing
one so the connection is not lost
([graphwiki](../../llm-wiki/lucianfialho/graphwiki-pattern.md)).

On the same 45 pairs the two-stage design scored F1 1.000: the filter removed the 15
obviously-unrelated pairs for free and all 30 remaining candidates were classified
correctly ([graphwiki](../../llm-wiki/lucianfialho/graphwiki-pattern.md)). The cost model is one
LLM call per candidate that clears stage one, not one per mention, which is the figure to
budget against ([graphwiki](../../llm-wiki/lucianfialho/graphwiki-pattern.md)).

## The filter does not have to be portable

The obvious objection to the result is that the judging model may be recalling facts about
AWS, Kubernetes, and NYC rather than resolving identity from context. That was tested
directly: the same 45-pair design was rerun against two fully invented technical domains —
a fictional distributed-compute system and a fictional metallurgy process — whose entities
exist nowhere outside the test, and the result held at F1 1.000
([graphwiki](../../llm-wiki/lucianfialho/graphwiki-pattern.md)).

A second finding fell out of that run and is the actual argument for the architecture. The
0.55 stage-one threshold did not transfer: one unrelated pair in the new domain scored 0.60
and leaked through as a candidate, and stage two rejected it correctly anyway
([graphwiki](../../llm-wiki/lucianfialho/graphwiki-pattern.md)). Stage one does not need to be
accurate or portable because stage two backstops it, which is a different claim from
"tune the threshold better" ([graphwiki](../../llm-wiki/lucianfialho/graphwiki-pattern.md)). The
caveat the author keeps is that the invented context sentences carried fairly explicit
distinguishing clues, and real extracted text is messier
([graphwiki](../../llm-wiki/lucianfialho/graphwiki-pattern.md)).

## The same decision in a markdown wiki

A page-based wiki resolves entities without embeddings, and the machinery is the index. The
absorption loop reads the index before each entry to match it against existing articles,
asking which existing articles the entry touches and what fails to match and therefore
suggests a new one ([wiki skill](../../llm-wiki/farzaa/wiki-gen-skill.md)). Index entries carry an
`also:` field of aliases specifically so entry text can be matched against article titles
that do not appear verbatim ([wiki skill](../../llm-wiki/farzaa/wiki-gen-skill.md)). Alias lists are
the flat-file stand-in for the embedding lookup in stage one, and the LLM reading the entry
supplies stage two.

Both forms treat the judgment as fallible and route a sample of it to review. Graph lint
checks the stage-two `NOT_SAME` decisions a human has not spot-checked, on the argument
that replacing a formula with an LLM call removes the threshold problem but not the error
rate ([graphwiki](../../llm-wiki/lucianfialho/graphwiki-pattern.md)). The page-based equivalent is
the expansion pass that mines articles for concrete entities mentioned without a page of
their own and ranks the candidates by reference count before creating any
([wiki skill](../../llm-wiki/farzaa/wiki-gen-skill.md)). Entity extraction is also named as
something ingest should do structurally rather than as prose, producing typed entities with
attributes and relationships instead of only paragraphs
([LLM Wiki v2](../../llm-wiki/rohitg00/llm-wiki.md)). Unresolved duplicates that neither pass catches
are one of the drift symptoms in [[wiki-drift]].
