# Subagent Authoring Principles (Opus 4.8)

The subagent-relevant deltas only. Generic prompting craft lives in the model docs; this is what changes specifically when you author an agent on 4.8. The pre-ship checklist in `anti-patterns.md` re-checks these.

## 1. Effort is the dominant capability lever — set it in frontmatter

On Opus 4.8, reasoning depth and tool-use propensity are governed primarily by `effort`, more than on any prior Opus. A subagent is the one artifact where you bake effort directly into the file via the `effort` frontmatter field, so set it deliberately rather than inheriting by accident:

- **`xhigh`** — hard coding and agentic work. The recommended default for any agent that writes or modifies code, or runs a multi-step tool loop.
- **`high`** — the reasoning-sensitive default for most analysis/research agents. Balances tokens and intelligence.
- **`low` / `medium`** — cheap, scoped helpers where the task is mechanical and latency/cost matter (a fast lookup agent, a formatter). 4.8 scopes its work tightly at these levels — good for cost, but risks under-thinking on anything moderately complex.

If an agent shows shallow reasoning or under-uses a tool it needs, **raise effort** — don't add "think harder" prose. `high`/`xhigh` also produce substantially more tool use in agentic search and coding. At `xhigh`/`max`, give the session a large max-output budget (start 64k) so the agent has room to act across tool calls.

## 2. Thinking is off by default — drop reasoning-permission prose

Thinking is off unless `thinking: {type: "adaptive"}` is set. "Think harder," "take a deep breath," "let's think step by step," "reason carefully through every edge case" are no-ops at best and encourage overthinking at worst. They add tokens to a body that recurs every turn. Depth comes from `effort`, not from granting permission to think.

## 3. 4.8 follows instructions literally — state what's in AND out of scope

The model interprets the body literally, especially at lower effort. It won't silently generalize an instruction from one item to all, and won't infer requests you didn't make. So:

- Put a `Not for: …` boundary in `When to invoke`, so the agent declines adjacent work instead of stretching to cover it.
- When something should apply broadly, say so ("review every changed file, not just the first").
- Define the **return contract** explicitly — the caller only sees the agent's final output.

Literalism is an asset for agents: it makes a well-scoped agent predictable. Spend the words on precise scope, not on hedging.

## 4. Conservative subagent spawning — be explicit when you want fan-out

4.8 favors reasoning over tool calls and spawns fewer sub-subagents by default. Usually correct. If your agent is meant to fan out (a coordinator dispatching workers, a reviewer spawning a verifier per finding), it won't unless the body says so concretely:

```text
Spawn subagents in parallel when fanning out across independent items or
files. For work you can do directly in one pass, do it inline.
```

Requires `Agent` in the agent's `tools` (nested spawning is capped at depth 5). When parallel fan-out is genuinely load-bearing, prose still under-fires — enforce it with a hook-driven workflow rather than trusting a "spawn N" instruction.

## 5. Keep the body lean and focused — it recurs every turn

The body is the system prompt; it costs tokens on every turn the agent runs. One job, one focused prompt. Cut anything that wouldn't change the output if deleted ("write clean code," "use good names," "handle edge cases" — 4.8 already does). High-signal content is what pushes the agent *out of its defaults*: the codebase-specific facts, the constraints, the return format. Split genuinely long reference material into the skill's `references/`, not the agent body.

## 6. Least-privilege tools

Grant only the tools the job needs. A read-only researcher gets `Read, Grep, Glob` — not write, not Bash, not MCP. This is security, focus, and predictability at once: a smaller pool means fewer ways to go off-script. Omit `tools` (inherit everything) only when the agent genuinely needs the full set, and prefer `disallowedTools: Write, Edit` over a blanket inherit when "almost everything" is the real requirement. Remember inheriting all also pulls in every connected MCP server's tools and their context cost.

## 7. The description is the trigger — name real phrasings

Claude routes to an agent off its `name` + `description`. Third person, name the actual contexts and phrasings that should delegate here, add "use proactively" / `PROACTIVELY` when you want automatic delegation, and include a NOT-boundary that routes adjacent work to a sibling. A vague description ("helps with code") means the agent never fires. Full guidance and the BAD→GOOD table are in `frontmatter.md` and `anti-patterns.md`.

## 8. Memory only when knowledge compounds across runs

Set `memory` (`project` recommended) only when the agent genuinely benefits from remembering across conversations — recurring codebase patterns, debugging insights, conventions it keeps rediscovering. It auto-enables Read/Write/Edit and injects `MEMORY.md` into every run, so it costs context and grants write tools. For one-shot work (run tests, review this diff, fetch these docs) it's pure overhead — skip it.

## 9. Remove forced progress-update scaffolding

4.8 emits regular, well-calibrated progress updates on long agentic traces on its own. Delete "after every N tool calls, summarize progress" from agent bodies — it fights the model's native pacing. If the *content* of updates is wrong for your use case, describe what a good update looks like and give one example; don't mandate a cadence.

## Reference Docs
- https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-4-8
- https://code.claude.com/docs/en/sub-agents
- https://github.com/shanraisshan/claude-code-best-practice/blob/main/best-practice/claude-subagents.md