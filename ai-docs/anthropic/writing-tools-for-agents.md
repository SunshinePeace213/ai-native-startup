---
source: https://www.anthropic.com/engineering/writing-tools-for-agents
fetched: 2026-07-05
---
> **In here:** Tool design and prototyping for agents · Evaluation-driven iteration and analysis · Tool architecture principles and implementation best practices

# Writing effective tools for AI agents — with agents

Published Sep 11, 2025

Agents are only as effective as the tools we give them. This post shares techniques for writing high-quality tools and evaluations, and how you can use Claude to optimize its tools for itself.

## What is a tool?

Tools represent a new contract between deterministic systems and non-deterministic agents. Unlike traditional software functions that produce identical outputs given the same inputs, agents can generate varied responses even with identical starting conditions. This fundamentally changes how developers should approach tool design—prioritizing agent ergonomics alongside human intuitiveness.

## How to write tools

### Building a prototype

Start by creating a quick prototype using local testing. Provide Claude with documentation for relevant software libraries, APIs, and SDKs (including the MCP SDK). Wrap tools in a local MCP server or Desktop extension to test them in Claude Code or the Claude Desktop app.

To connect your local MCP server to Claude Code:
```
claude mcp add <name> <command> [args...]
```

Test tools yourself to identify rough edges and collect user feedback about expected use cases.

### Running an evaluation

Measure how effectively Claude uses your tools through evaluation. Generate numerous real-world evaluation tasks and collaborate with agents to analyze results.

**Generating evaluation tasks**

Create prompt and response pairs based on realistic data sources and services. Tasks should require multiple tool calls and reflect actual workflows. Strong examples include:
- Scheduling meetings with document attachments and room reservations
- Investigating customer transaction issues across logs
- Analyzing cancellation requests with retention recommendations

Weaker tasks involve single, straightforward operations without complexity.

Pair each prompt with a verifiable response. Verifiers can range from exact string comparisons to Claude-based judgments. Avoid overly strict verification that rejects correct responses due to formatting differences.

**Running the evaluation**

Run evaluations programmatically using direct LLM API calls with simple agentic loops. Instruct evaluation agents to output reasoning and feedback blocks before tool calls to trigger chain-of-thought behaviors.

Collect metrics beyond accuracy: runtime, tool call counts, token consumption, and tool errors. These reveal common workflows and optimization opportunities.

**Analyzing results**

Observe where agents struggle. Read through reasoning transcripts and raw transcripts (including tool calls and responses) to identify issues. Analyze tool-calling patterns—redundant calls suggest parameter adjustments; invalid parameter errors indicate unclear descriptions.

### Collaborating with agents

Concatenate evaluation transcripts and paste them into Claude Code. Claude excels at analyzing transcripts and refactoring multiple tools simultaneously, ensuring consistency across changes. Held-out test sets prevent overfitting to training evaluations.

## Principles for writing effective tools

### Choosing the right tools for agents

More tools don't guarantee better outcomes. Agents have distinct affordances from traditional software: they operate within limited context windows. Rather than tools that merely wrap API endpoints, build thoughtful tools targeting high-impact workflows.

For address book searches, implement `search_contacts` rather than `list_contacts`. Tools can consolidate functionality, handling multiple discrete operations under the hood:
- Instead of separate `list_users`, `list_events`, and `create_event` tools, implement `schedule_event`
- Instead of `read_logs`, implement `search_logs` returning only relevant lines
- Instead of separate customer tools, implement `get_customer_context` compiling all relevant information

Each tool should have a clear, distinct purpose matching how humans would subdivide tasks.

### Namespacing your tools

Group related tools under common prefixes to help agents select appropriate tools. Examples include:
- Service-based: `asana_search`, `jira_search`
- Resource-based: `asana_projects_search`, `asana_users_search`

Naming schemes can significantly impact tool-use evaluations. Selective implementation reduces context load and offloads computation from the agent to tool implementations.

### Returning meaningful context from your tools

Tool implementations should return high-signal information prioritizing contextual relevance over flexibility. Use semantic identifiers rather than technical ones:
- Use `name`, `image_url`, `file_type` instead of `uuid`, `256px_image_url`, `mime_type`

Meaningful language significantly improves precision in retrieval tasks by reducing hallucinations.

When flexibility is needed, expose a `response_format` enum parameter:

```
enum ResponseFormat {
   DETAILED = "detailed",
   CONCISE = "concise"
}
```

Detailed responses include IDs for downstream tool calls (206 tokens). Concise responses exclude technical identifiers (72 tokens). Response structure—XML, JSON, or Markdown—also impacts performance based on training data distributions.

### Optimizing tool responses for token efficiency

Implement pagination, range selection, filtering, and/or truncation with sensible defaults for tool responses consuming substantial context. Claude Code restricts responses to 25,000 tokens by default.

When truncating, provide helpful instructions steering agents toward targeted searches. For errors, communicate specific, actionable improvements rather than opaque error codes.

Example guidance for truncated responses: "Only the first 50 results are shown. To find specific records, try filtering by date or using more specific search terms."

Example helpful error response: "Invalid format. Expected email address (e.g., jane@company.com). For bulk operations, use the batch_send tool instead."

### Prompt-engineering your tool descriptions

Tool descriptions and specs significantly influence agent behavior. Describe tools as you would to a new team member, making implicit context explicit. Avoid ambiguity in input parameters—use `user_id` instead of `user`.

Even small refinements yield dramatic improvements. Precise description refinements helped Claude Sonnet 3.5 achieve state-of-the-art performance on SWE-bench Verified, dramatically reducing errors and improving completion rates.

## Looking ahead

Building effective tools requires reorienting software development from predictable, deterministic patterns to non-deterministic ones. Through evaluation-driven iteration, successful tools are intentionally defined, use context judiciously, combine flexibly, and enable agents to solve real-world tasks intuitively.

As agents become more capable, tools must evolve alongside them through systematic, evaluation-driven approaches.
