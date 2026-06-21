# Subagent Anti-Patterns & Pre-Ship Review

Live docs:
- https://code.claude.com/docs/en/sub-agents
- https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-4-8
- https://github.com/shanraisshan/claude-code-best-practice/blob/main/best-practice/claude-subagents.md

Scan every draft for these before shipping. If the user explicitly wants one, explain the cost once and comply only if they confirm.

## Anti-patterns → why wrong on 4.8 → fix

| Anti-pattern | Why it's wrong on 4.8 | Fix |
|---|---|---|
| **Too many tools / inheriting all when read-only suffices** | Inheriting (omitting `tools`) pulls in every tool incl. all MCP servers and their context cost; more tools = more ways to go off-script. | Least privilege: `tools: Read, Grep, Glob` for a researcher. Use `disallowedTools` only when "almost everything" is the real need. |
| **Vague description** ("helps with code") | Claude routes off the description; vague = never delegates, or delegates wrongly. | Third person, name real trigger contexts + phrasings, "use proactively", a NOT-boundary. See the BAD→GOOD table below. |
| **Bloated persona** ("senior dev, 10k PRs at a FAANG") | Read literally; the numbers and résumé add tokens, not behavior. | One sentence on the relevant lens: "You review diffs for correctness and security." |
| **All-caps MUST/NEVER without a why** | Aggressive language over-triggers, or on review tasks over-filters; 4.8 reads it literally. | Sentence case + the reason. Keep caps only where the model would do the wrong thing without them. |
| **`memory` for one-shot work** | Auto-enables Read/Write/Edit and injects MEMORY.md every run — context cost + write tools you may not want, for nothing. | Omit `memory`. Set it only when knowledge compounds across runs. |
| **Forced progress-update cadence** ("summarize every 3 tool calls") | 4.8 emits good updates natively; cadence fights its pacing. | Remove. If updates are miscalibrated, describe a good one + give one example. |
| **"Think harder" / reasoning-permission prose** | Thinking is off unless adaptive; depth comes from `effort`. No-op at best, overthinking at worst. | Set `effort` (`high`/`xhigh`); reserve prose for *steering* when to think. |
| **Setting `hooks`/`mcpServers`/`permissionMode` on a plugin agent** | Silently ignored for plugin-loaded subagents — no error, no effect. | Move the agent to `.claude/agents/` or `~/.claude/agents/`, or use session-wide `permissions.allow` for the permission case. |
| **Listing the unavailable tools** (`AskUserQuestion`, `EnterPlanMode`, `ScheduleWakeup`, `WaitForMcpServers`, `ExitPlanMode` outside `plan` mode) | These never work in a subagent regardless of `tools`. An agent designed to "ask the user" mid-run can't. | Don't depend on them. For plan-mode exit, set `permissionMode: plan`. |
| **Listing `Skill` in `tools` to preload skills** | `tools: Skill` only grants the Skill tool; it does NOT preload content. | Use the `skills:` field to inject full skill content at startup. |
| **Body assumes shared conversation history** | A non-fork subagent sees only its prompt + delegation message — not what the main thread read or discussed. | Restate every needed rule/context/path in the body. |
| **Duplicate `name` across the agents tree** | Same `name` in one scope = one silently discarded; across scopes = priority collision. | Keep `name` unique tree-wide; confirm before shipping. |
| **Unqualified MCP names in tool lists** | Bare `tool` may not resolve when multiple servers are connected. | Use `mcp__<server>__<tool>` or `mcp__<server>` patterns. |

## BAD → GOOD descriptions (subagents)

| BAD | GOOD |
|---|---|
| `description: Reviews code.` | `description: Read-only reviewer of the current git diff. Use proactively after code changes to check correctness and security. Reports findings only; does not edit. Not for running tests (use test-runner).` |
| `description: A debugging helper.` | `description: Debugging specialist for errors, test failures, and unexpected behavior. Use proactively when a command fails or a test breaks. Isolates root cause and applies a minimal fix.` |
| `description: Does database stuff.` | `description: Runs read-only SQL queries and summarizes results. Use when analyzing data or generating reports. Not for migrations or writes — those go to the migration agent.` |
| `description: Research agent.` | `description: Read-only codebase research. Use proactively to locate code, trace data flow, or map a module before changes are made. Returns a summary; does not modify files.` |

The shift each time: vague summary → third person, names real trigger contexts + user phrasings, "use proactively" where auto-delegation is wanted, and a NOT-boundary routing adjacent work to a sibling.

## Pre-ship checklist

Run before shipping. Any failure → fix, then re-read the whole draft fresh.

**Identity & triggering**
- [ ] `name` is lowercase letters + hyphens, and unique across the whole agents tree (project + user + plugins)
- [ ] `description` is the trigger: third person, names real contexts/phrasings, "use proactively" where auto-delegation is wanted, with a NOT-boundary

**Tools & capability**
- [ ] Least-privilege `tools` (or a deliberate inherit-all / `disallowedTools` choice, knowing it pulls in MCP tools)
- [ ] No dependency on the unavailable tools (`AskUserQuestion`, `EnterPlanMode`, `ScheduleWakeup`, `WaitForMcpServers`, `ExitPlanMode` unless `permissionMode: plan`)
- [ ] Skills preloaded via `skills:`, not `tools: Skill`; no preloaded skill has `disable-model-invocation: true`
- [ ] `model` and `effort` set intentionally (`xhigh` hard coding/agentic, `high` reasoning-sensitive default, `low`/`medium` cheap scoped)

**Memory & plugin safety**
- [ ] `memory` set only if knowledge compounds across runs
- [ ] No plugin-ignored fields (`hooks`, `mcpServers`, `permissionMode`) set on a plugin-distributed agent

**Body**
- [ ] Body restates every rule/context/path the agent needs (no reliance on shared history)
- [ ] Lean and focused — nothing that states what 4.8 already does; one job
- [ ] Explicit `Output` / return contract; no forced progress-update cadence; no "think harder" prose
- [ ] No bloated persona; no all-caps MUST/NEVER without a why

**YAML hygiene**
- [ ] Frontmatter is real YAML between `---` markers at the top of the file (NOT a fenced ```yaml block)
- [ ] Only `name` and `description` are required; every other field is valid per `frontmatter.md`
