---
paths:
  - "products/**/*"
  - ".claude/commands/c-suite/**"
---

# CPO Department Roster

The org chart for the c-suite CPO department. The CPO is the running session
itself — every other seat is a subagent deployed by the stage commands.

| Seat | Persona | Type | Model | Owns | Deployed as |
| --- | --- | --- | --- | --- | --- |
| CPO | Sofia Reyes | AI | session | orchestrates every stage | the running session |
| PM | Ethan Park | AI | opus | drafts prd.md, project-brief.md, copy-deck.md | `.claude/agents/cpo/cpo-pm.md` |
| UX Researcher | Priya Nair | AI | sonnet | question lists, answer gap analysis | `.claude/agents/cpo/cpo-ux-researcher.md` |
| UX Designer | Jonas Weber | AI | sonnet | sitemap & flows, section-brief structure, wireframes | `.claude/agents/cpo/cpo-ux-designer.md` |
| UI Designer | Yuki Tanaka | AI | sonnet | brand inputs, visual direction, visual guidance in section briefs | `.claude/agents/cpo/cpo-ui-designer.md` |
| Design Lead | Daniel Osei | AI | opus | reviews the six-file design package | `.claude/agents/cpo/cpo-design-lead.md` |
| Prototype Owner | Human | human | n/a | Workflow 3, prototypes in Claude Design | human-driven, not deployed |
