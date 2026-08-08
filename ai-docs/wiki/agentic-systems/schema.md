# Agentic Systems Schema

How LLM agents are architected: the patterns a system is built from, the order
they are added in, and the state layer they share. Distinct from `engineering/`,
which covers the knowledge base this repo maintains rather than the agents that
read it.

Types beyond the core five: `architecture` (how a system's layers and state fit
together), `failure-mode` (a recurring way agentic work goes wrong). Core
`pattern`, `decision`, and `topic` carry the rest — a `pattern` page is one
named building block with its failure modes and controls, a `decision` page is a
rule for choosing between them.

Layout: flat pages in `agentic-systems/`, no hub page. Kebab-case file names
matching the page title.

Pattern pages are named for the mechanism, not its author — `reflection-loop`,
not "Ng's first pattern". Where two sources name the same mechanism differently,
the page carries both names and cites each.

Raw sources are grouped by topic under `ai-docs/<topic>/`, laid out as the
original documents in `<topic>/raw/`, extracted figures in `<topic>/assets/`,
and the text layer split into numbered section files at the topic root beside
`index.md`. The Ng playbook is archived that way as `ai-docs/graph-engineering/`;
pages cite the section files directly rather than the PDF, so a citation names
the passage it rests on.
