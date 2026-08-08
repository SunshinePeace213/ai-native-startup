---
source: raw/Graph-Engineering-Andrew-Ng-Playbook.pdf
fetched: 2026-08-05
---
> **In here:** Section catalog for the Graph Engineering playbook · Which section answers which question · Where the source PDF lives

# Graph Engineering for Multi-Agentic Systems: The Andrew Ng Playbook

A 2026 working note on agentic AI practice, mirrored from a locally supplied
12-page PDF held at
[`raw/Graph-Engineering-Andrew-Ng-Playbook.pdf`](./raw/Graph-Engineering-Andrew-Ng-Playbook.pdf).
Independently compiled — not affiliated with or endorsed by Andrew Ng,
DeepLearning.AI, Anthropic, Neo4j, or Google. Split by section so a session
loads only the part it needs.

Layout: original files in `raw/`, extracted figures in `assets/`, and the text
layer split across the numbered section files below.

| Section | Pages | In here |
| --- | --- | --- |
| [Abstract & I. Introduction](./01-abstract-and-introduction.md) | 1-2 | HumanEval 95.1% vs 67.0% · Loop/chain/network/graph as externalized cognition · Why graphs-vs-loops matters now |
| [II. The Four Design Patterns](./02-four-design-patterns.md) | 2-4 | Reflection, Tool Use, Planning, Multi-Agent · Failure modes and controls · Ng's maturity assessment |
| [III. Anthropic's Five Workflow Patterns](./03-anthropic-five-workflows.md) | 4-5 | Chaining, routing, parallelization, orchestrator-workers, evaluator-optimizer · Workflow before agent |
| [IV. From Loops to Graphs](./04-from-loops-to-graphs.md) | 5-6 | The four stages · Three roles a knowledge graph plays · Minimal five-node schema |
| [V. The Benchmark Evidence](./05-benchmark-evidence.md) | 6-7 | HumanEval table · Fast inference as capability multiplier · Model choice and workflow design are coupled |
| [VI. Practical Implementation Guide](./06-implementation-guide.md) | 7 | Day 1 reflection → Month 1 graph · Token cost of planning agents · Implementation timeline |
| [VII. Decision Framework](./07-decision-framework.md) | 7-8 | When to use each pattern · Five decision rules · Seven anti-patterns |
| [VIII. The Graphs vs. Loops Debate](./08-graphs-vs-loops-debate.md) | 8-9 | Three criteria that make a graph necessary · Add the graph at the failure point · Compound architecture |
| [Appendices B & C](./09-appendices-b-and-c.md) | 9-10 | Production readiness checklist by stage · Code-review assistant from zero-shot to graph |
| [IX–XI. Limitations, Adoption, Conclusion](./10-limitations-adoption-conclusion.md) | 10-11 | What still doesn't work reliably · Why teams shouldn't skip stages · The traceability sentence |
| [Sources & Glossary](./11-sources-and-glossary.md) | 11-12 | Ng talks and courses · Referenced papers and industry data · Glossary of terms |

## Reading order

Sections I–IV build the vocabulary and the loop→chain→network→graph
progression; VI–VII are the operational core (build path, decision rules,
anti-patterns). Read VII before adding any pattern to a live system.

## Provenance

The text layer is extracted verbatim from the supplied PDF, a two-column
letter-portrait layout (WeasyPrint) whose columns split at the x=306 gutter.
The PDF carries no hyperlink annotations, so no source links exist to preserve.

Fig. 1 is the document's only diagram, and it is a vector drawing rather than an
embedded raster — the PDF contains no embedded images on any page. It is
rasterised from page 1 at 300 dpi into
[`assets/`](./assets/fig-01-graph-grounded-multi-agent-architecture.png), with
the caption quoted verbatim and the figure's own labels carried in the alt text.
The shaded blocks on pages 2–7 are code-listing backgrounds, not figures. An
earlier revision of this archive reconstructed Fig. 1 as a mermaid graph instead;
that reconstruction mislabelled the diagram — it folded node subtitles such as
"planning + reflection" into edge labels and attached the "shares data" edge to
the wrong pair of nodes — and it has been replaced by the extracted image.

The document's own appendix lettering skips "Appendix A" — it runs B, C, then
an unlettered "Appendix: Glossary"; that numbering is mirrored as published.
