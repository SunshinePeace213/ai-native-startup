---
source: https://claude.com/blog/using-claude-code-the-unreasonable-effectiveness-of-html
fetched: 2026-07-21
---
> **In here:** HTML over Markdown for AI artifacts · Use cases: specs, reviews, design, reports · Interactive sharing and two-way editing

# Using Claude Code: The Unreasonable Effectiveness of HTML

## Article Overview

This blog post by Thariq Shihipar from Anthropic discusses why the Claude Code team prefers HTML over Markdown for generating AI outputs. The article was published on May 20, 2026, with an estimated 5-minute read time.

## Key Arguments for HTML Over Markdown

### Information Density

HTML enables richer information representation compared to Markdown, including:

- Tabular data through tables
- Design elements via CSS
- Illustrations using SVG
- Code snippets with script tags
- Interactive features with HTML elements, JavaScript, and CSS
- Workflow diagrams with SVG and HTML
- Spatial data using positioning and canvases
- Images via image tags

The author notes that "there is almost no set of information that Claude can read that you cannot efficiently represent with HTML."

### Visual Clarity and Reading Ease

Long Markdown files (beyond 100 lines) become difficult to read. HTML documents offer superior navigation through visual organization, tabs, illustrations, and links. Mobile responsiveness also allows content adaptation based on device type.

### Ease of Sharing

HTML files can be uploaded and shared via links, making them more accessible than Markdown attachments. This increases the likelihood of colleagues actually reading specifications and reports.

### Two-Way Interactions

HTML enables interactive elements like sliders and knobs, allowing users to adjust designs or test algorithms while maintaining a "copy as prompt" export function to feed results back into Claude Code.

### Data Ingestion Capabilities

Claude Code can leverage file system access, MCPs (Slack, Linear, etc.), Chrome browsing history, and git history—advantages unavailable through Claude.ai or Claude Design.

## Practical Use Cases

### Specs, Planning, and Exploration

Create side-by-side comparisons of different design approaches, implementation plans with mockups, data flow diagrams, and annotated code snippets.

**Example prompt:** "Generate 6 distinctly different approaches to an onboarding screen—vary layout, tone, and density—and lay them out as a single HTML file in a grid for comparison."

### Code Review and Understanding

HTML enables rendering of diffs with inline annotations, color-coded findings by severity, and visual flowcharts for PR descriptions and code explanations.

**Example prompt:** Create "an HTML artifact describing this PR, focusing on streaming/backpressure logic with colored diff annotations."

### Design and Prototypes

Use HTML to sketch designs with interactive elements like adjustable sliders and animated buttons, creating throwaway prototypes for testing animations and component variations.

### Reports, Research, and Learning

Synthesize information from multiple sources (Slack, codebase, git history, internet) into readable HTML reports, explainers, or slideshows with SVG diagrams.

**Example prompt:** "Produce a single HTML explainer page with a token-bucket flow diagram, annotated code snippets, and a 'gotchas' section."

### Custom Editing Interfaces

Build purpose-built HTML editors for specific tasks (ticket reordering, feature flag configuration, system prompt tuning) with export functions that return data as JSON or Markdown.

## FAQ Highlights

**Efficiency Concerns:** While Markdown uses fewer tokens, HTML's expressiveness and higher readability rates result in better overall output. With Opus 4.7's 1 million context window, token increases are negligible.

**Current Markdown Use:** The author has "stopped using Markdown altogether for almost everything" and acknowledges being "far on the HTML maximalist side of things."

**Replacing Planning:** Rather than single plans, the workflow involves multiple HTML files for different stages—exploration, UI options, implementation plans—kept as ongoing references.

## Core Philosophy

The fundamental reason for preferring HTML is maintaining engagement with Claude's work: "The real reason I use HTML instead of Markdown is that it helps me feel much more in the loop with Claude." As AI capabilities expand, staying actively involved in reviewing choices becomes increasingly important.

## Getting Started

Simply prompt Claude Code to "make an HTML file" or "make an HTML artifact" with descriptions of desired functionality. The platform includes example templates for common use cases, available on GitHub.
