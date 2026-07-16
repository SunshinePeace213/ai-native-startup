---
source: https://claude.com/blog/using-claude-code-the-unreasonable-effectiveness-of-html
fetched: 2026-07-16
---

> **In here:** · Why HTML outperforms Markdown for Claude Code outputs · Practical use cases from specs to custom interfaces · Getting started with HTML generation

# Using Claude Code: The Unreasonable Effectiveness of HTML

**Publication Date:** May 20, 2026  
**Reading Time:** 5 minutes  
**Author:** Thariq Shihipar, Member of Technical Staff at Anthropic

---

## Overview

The article argues that HTML has become the preferred output format for Claude Code agents over Markdown. According to the author, "Markdown has become the dominant file format used by agents to communicate with humans," yet it increasingly feels restrictive for complex work.

## Why Use HTML?

The author identifies four primary advantages:

### Information Density

HTML can represent diverse data types—tables, SVG illustrations, interactive elements, and code snippets—that Markdown cannot efficiently convey. This prevents agents from resorting to "ASCII diagrams or estimating colors with unicode characters" when Markdown proves insufficient.

### Visual Clarity and Ease of Reading

As Claude tackles increasingly complex tasks, output files grow substantially. The author notes difficulty engaging with Markdown files exceeding 100 lines, whereas HTML documents leverage tabs, illustrations, and responsive design to improve readability and encourage stakeholder review.

### Ease of Sharing

HTML files can be uploaded and shared via links, whereas Markdown typically requires email attachments. This accessibility significantly increases the likelihood others will actually read specifications and reports.

### Two-Way Interactions

HTML enables interactive features—sliders, toggles, and live previews—allowing users to adjust designs dynamically and export results back into Claude Code, creating tighter feedback loops.

### Data Ingestion

Claude Code can access file systems, MCPs like Slack and Linear, browser history, and git logs—context unavailable to standard Claude.ai. This additional information enhances HTML generation capabilities.

## Getting Started

The author emphasizes that prompting Claude to create HTML is straightforward: simply request "_make an HTML file_" or "_make an HTML artifact_." Understanding your desired outcome and use case matters more than complex instructions.

## Use Cases

### Specs, Planning, and Exploration

HTML serves as an effective canvas for problem exploration. Users can request Claude to generate multiple design approaches in grid layouts for side-by-side comparison, complete with labeled tradeoffs. Implementation plans benefit from mockups, data flow diagrams, and code snippets—all visually organized in HTML format.

### Code Review and Understanding

HTML enables rendering diffs, annotations, flowcharts, and module diagrams more effectively than Markdown. Teams can use this for PR reviews and code explanations, with color-coded findings and inline annotations.

### Design and Prototypes

HTML allows prototyping interactions, animations, and component behaviors. The author suggests requesting sliders and parameter controls to experiment with animations, allowing users to export optimized settings.

### Reports, Research, and Learning

Claude Code can synthesize information across Slack, codebases, git history, and internet sources into readable HTML reports. SVG diagrams enhance visualization of complex concepts.

### Custom Editing Interfaces

Purpose-built HTML editors allow users to manipulate structured data—reordering tickets, editing feature flags, tuning prompts—with export functionality to generate Markdown, JSON, or diffs for downstream use.

## Frequently Asked Questions

**Isn't it less efficient?**

While Markdown uses fewer tokens, HTML's expressiveness and higher readability rates result in better overall output. With Claude's 1MM context window, increased token usage remains negligible.

**When do you use Markdown?**

The author reports abandoning Markdown for nearly all use cases, though acknowledges occupying an "HTML maximalist" position.

**Has this replaced planning?**

Rather than single plans, users typically maintain multiple HTML files for different implementation stages—exploration documents, UI mockups, and component libraries—retained as future references.

## Conclusion

The author emphasizes that HTML's primary benefit is keeping users "much more in the loop with Claude." As AI capabilities expand, richer output formats help maintain meaningful human engagement rather than passive handoffs.

---

**Getting started:** Users can access Claude Code documentation and explore HTML use case examples.
