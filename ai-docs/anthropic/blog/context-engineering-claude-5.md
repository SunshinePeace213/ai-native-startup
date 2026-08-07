---
source: https://claude.com/blog/the-new-rules-of-context-engineering-for-claude-5-generation-models
fetched: 2026-07-26
---
> **In here:** Paradigm shifts from rules to judgment · System prompt and CLAUDE.md simplification · Progressive disclosure and context architecture

# The new rules of context engineering for Claude 5 generation models

**Date:** July 24, 2026  
**Author:** Thariq Shihipar, Member of Technical Staff, Anthropic  
**Categories:** Claude Code, Agents  
**Reading time:** 5 min

---

## Overview

Anthropic removed over 80% of Claude Code's system prompt for advanced models like Claude Opus 5 and Claude Fable 5 without measurable performance loss. This article explores how context engineering—assembling prompts, system instructions, skills, and memory—has evolved and how to apply these lessons to your own implementations.

## Unhobbling Claude

The research revealed that Claude Code was over-constrained through conflicting guidance in system prompts, CLAUDE.md files, and skills. For example, instructions simultaneously stated "leave documentation as appropriate" while also mandating "DO NOT add comments," forcing the model to work through these contradictions unnecessarily.

Modern Claude models demonstrate superior judgment and can handle nuanced decisions without explicit guardrails. Additionally, new tools—memory, artifacts, and skills—provide alternative methods for loading and sharing context across sessions, reducing reliance on CLAUDE.md as the primary information repository.

## Then and Now: Paradigm Shifts

### Then: Give Claude rules | Now: Let Claude use judgement

**Previous approach:** Strict rules like "Never write multi-paragraph docstrings or multi-line comment blocks — one short line max" protected against worst-case scenarios but created inflexibility.

**Current approach:** "Write code that reads like the surrounding code: match its comment density, naming, and idiom." Newer models handle contextual judgment better than explicit constraints.

### Then: Give Claude examples | Now: Design interfaces

**Previous approach:** Tool usage examples constrained Claude to demonstrated patterns.

**Current approach:** Thoughtfully designed tool interfaces with expressive parameters guide exploration more effectively than examples. Enumerated status fields and parameter design provide implicit instruction without limiting possibilities.

### Then: Put it all upfront | Now: Use progressive disclosure

**Previous approach:** Detailed information on code review and verification appeared in the system prompt regardless of need.

**Current approach:** Load context selectively through skills or deferred-loading tools that Claude searches for when needed. This applies to CLAUDE.md and Skill.md files—organize them hierarchically rather than as monolithic repositories.

### Then: Repeat yourself | Now: Simple tool descriptions

**Previous approach:** Instructions appeared in both system prompts and tool descriptions for emphasis.

**Current approach:** Place tool usage instructions in tool descriptions rather than duplicating them across context.

### Then: Memory in CLAUDE.md files | Now: Auto-memory

**Previous approach:** Users manually saved information to CLAUDE.md files using the # hotkey.

**Current approach:** Claude automatically preserves relevant memories without manual intervention.

### Then: Simple specs | Now: Rich references

**Previous approach:** Plain markdown files contained project plans and specifications.

**Current approach:** Claude can reference complex HTML artifacts, detailed test suites, code samples from other codebases, and rubrics that encode team preferences for verification by specialized agents.

## Applying This to Your Context

### System Prompt

Heavily tied to product context, system prompts define what product Claude operates within and its role. For custom agents, this deserves substantial effort.

### CLAUDE.md

Keep lightweight with brief repository descriptions. Focus tokens on gotchas specific to the codebase rather than obvious information Claude can infer from the file system. Use progressive disclosure extensively—create separate skills for complex verification procedures rather than embedding everything in one file.

### Skills

Function as lightweight guides for context discovery. Avoid over-constraining except in critical areas. For lengthy skills, split across multiple files and leverage progressive disclosure.

Skills work best encoding team-specific opinions, knowledge, and practices rather than universal best practices.

### References

@ mentions include files as in-depth references for current plans. Prefer code-based specifications over descriptions or screenshots, as Claude understands code with higher fidelity. Examples include specs files, mockups, entire codebases, and design mockups in HTML format.

## Try Simplifying

Anthropic introduced the `claude doctor` command (accessible via `/doctor` in Claude Code) to help automatically optimize system prompts, skills, and CLAUDE.md files. This tool assists in rightsizing context to match modern model capabilities.

---

## Related Resources

- [Claude models explained: choosing the best model for your use case](/blog/claude-models-explained-choosing-the-best-model-for-your-use-case) (July 24, 2026)
- [Building verification loops in Claude Code with skills](/blog/building-verification-loops-in-claude-code-with-skills) (July 22, 2026)
- [How Anthropic secures its AI-native software development lifecycle](/blog/how-anthropic-secures-its-ai-native-software-development-lifecycle) (July 21, 2026)
- [How Anthropic runs large-scale code migrations with Claude Code](/blog/ai-code-migration) (July 16, 2026)
