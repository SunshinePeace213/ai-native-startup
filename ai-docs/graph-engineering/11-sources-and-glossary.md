---
source: raw/Graph-Engineering-Andrew-Ng-Playbook.pdf
fetched: 2026-08-05
pages: 11-12
---
> **In here:** Ng talks, The Batch essays, DeepLearning.AI courses · Referenced papers and industry data · Glossary of terms (Table VI)

# Acknowledgment & Sources

This document is an independent synthesis for study. It is not affiliated with or endorsed by Andrew Ng, DeepLearning.AI, Anthropic, Neo4j, or Google.

Andrew Ng, "What's Next for AI Agentic Workflows," Sequoia Capital AI Ascent, Mar. 2024; "Four AI Agent Strategies," The Batch, DeepLearning.AI, Mar. 2024; "Agentic Design Patterns Parts 2–4," The Batch, Apr. 2024; "Agentic AI," DeepLearning.AI course, Oct. 2025; Agentic Knowledge Graphs course (DeepLearning.AI + Neo4j + Google ADK), Jul. 2026.

E. Schluntz & B. Zhang, "Building Effective Agents," Anthropic Engineering, Dec. 2024. Anthropic, "Building Effective AI Agents: Architecture Patterns and Implementation Frameworks," 2026.

Referenced papers: Self-Refine (Madaan et al., 2023), Reflexion (Shinn et al., 2023), CRITIC (Gou et al., 2024), Toolformer (Schick et al., 2023), HuggingGPT (Shen et al., 2023), ChemCrow (Bran et al., 2023), AutoGen (Wu et al., 2023), ChatDev (Qian et al., 2024).

Industry data: 93% of IT leaders plan AI agents within 2 years (2025 Connectivity Benchmark Report); Deloitte predicts 25% of companies will have agentic pilots by 2025. All diagrams are original to this document.

# Appendix: Glossary

### Table VI — Terms Used in This Note

| Term | Meaning |
| --- | --- |
| Zero-shot | Single LLM call, no iteration. |
| Agentic workflow | LLM prompted multiple times with iteration. |
| Reflection | LLM critiques and revises its output. |
| Tool use | LLM calls external capabilities. |
| Planning | LLM decomposes task into steps. |
| Multi-agent | Multiple LLM instances collaborate. |
| Prompt chaining | Fixed sequence of LLM calls. |
| Routing | Classify input, send to specialist. |
| Parallelization | Multiple LLM calls simultaneously. |
| Orchestrator-workers | Central LLM delegates to workers. |
| Evaluator-optimizer | One LLM generates, another evaluates. |
| Graph architecture | Shared persistent memory with typed edges. |
| Knowledge graph | Entities as nodes, relationships as edges, with provenance. |
| Artifact contract | Typed schema for agent handoffs. |
| Provenance | Source from which a fact was derived. |

---

This document is an independent synthesis assembled for study. It is not a publication of, and is not affiliated with or endorsed by, Andrew Ng, DeepLearning.AI, Anthropic, Neo4j, or Google. All benchmark numbers are from Andrew Ng's published analysis. All quotes are from his public talks and writings. Diagrams are original.
