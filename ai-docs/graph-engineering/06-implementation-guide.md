---
source: raw/Graph-Engineering-Andrew-Ng-Playbook.pdf
fetched: 2026-08-05
pages: 7
---
> **In here:** Day 1 reflection → Month 1 graph · Token cost of planning agents (~10× a direct call) · Implementation timeline (Table IV)

# VI. Practical Implementation Guide

The recommended build path starts with the smallest reliable loop and adds one capability at a time. Each stage should have a baseline, a task-level metric, a cost budget, and a rollback path.

## A. Start with Reflection — Day 1

Choose one existing LLM call whose output can be evaluated. Add a second call that critiques the first against an explicit rubric. Feed the critique into a revision call. Compare the revised output with the baseline. Expected improvement: 10–30% quality boost, but the team should measure its own lift. The implementation is deliberately minimal: two additional LLM calls and a for-loop. The rubric should be written before the first run, not discovered after — "improve this" is not a rubric. A good starting rubric names the specific qualities the output must have (correct information, appropriate length, required sections) and the specific defects the critic should look for (unsupported claims, missing citations, logical contradictions). The rubric itself is a kind of unit test for the output.

## B. Add Tool Use — Day 2

Give the agent access to at least one tool: code execution or web search. Let the agent decide when to use it. Validate tool results before incorporating them. Watch for the "rerouting around failures" moment Ng describes — the agent discovering and using a fallback tool is one of the clearest signs that the agentic architecture is adding value beyond what a fixed script could provide. Start with read-only tools before adding write access; a tool that reads a database is safe to experiment with, while a tool that modifies production data requires the same permission controls you would apply to a junior engineer.

## C. Build a Planning Agent — Week 1

For complex tasks, have the LLM write a plan as structured JSON before executing. Execute each step, collect results. If a step fails, replan with context of what already worked. Preserve successful work across replans. The practical constraint: planning agents consume significantly more tokens than direct calls because the plan itself is generated text, each step's execution generates text, and the synthesis of results generates text. Budget accordingly — a planning agent that runs 8 steps at 2,000 tokens each plus a 3,000-token synthesis is consuming ~19,000 tokens, roughly 10× a direct call. The lift in task completion rate must justify this cost, and for simple tasks it usually does not.

## D. Go Multi-Agent — Week 2

Split your task into roles: generator + critic minimum. Use same model, different system prompts. Iterate until critic is satisfied or iteration limit reached. Define artifact contracts for every handoff.

## E. Wire Into a Graph — Month 1

Add persistent state between agent runs. Start simple: shared JSON file or database. Graduate to knowledge graph when agents need to chain facts across sessions. Add provenance tracking and version history. This is the stage Ng's July 2026 course covers in detail: building the graph from scratch using Google ADK, with extraction agents feeding entities into a Neo4j-backed knowledge graph that multiple agents query and extend.

### Table IV — Implementation Timeline

| Step | Time | Complexity | Expected Lift |
| --- | --- | --- | --- |
| Add reflection | 1 day | Low | 10–30% quality |
| Add tool use | 1 day | Low | New capabilities |
| Planning agent | 1 week | Medium | Complex tasks |
| Multi-agent | 2 weeks | Medium | Better quality |
| Graph architecture | 1 month | High | Persistent, scalable |
