# Model Selection

The cross-model roster for every deployment decision — orchestrator, subagent, workflow
stage, or Codex task. Plans stamp a model + effort per task from this file; never
hard-code model guidance in templates, tasks, or commands.

Rankings 1–10, higher = better. Intelligence is how hard a problem the model handles
unsupervised. Taste covers UI/UX, code quality, API design, and copy. Cost reflects
what we actually pay (Codex limits are generous), not list price.

## Roster

| Model | Invoke via | Intelligence | Taste | Speed | Cost | Choose for |
| --- | --- | --- | --- | --- | --- | --- |
| `fable` (Fable 5) | Agent/Workflow `model` | 10 | 9 | 3 | 4 | Highest-judgment work — deep specs, and long-horizon autonomous runs `opus` cannot finish at any effort. Orchestrator only — never deploy as a subagent |
| `opus` (Opus 5) | Agent/Workflow `model` | 9 | 8 | 5 | 5 | Complex implementation; behavior-preserving refinement; reviews every Codex-authored change |
| `sonnet` (Sonnet 5) | Agent/Workflow `model` | 7 | 7 | 7 | 7 | Default workhorse — standard implementation, review fixes, guarded mechanical flows |
| `haiku` (Haiku 4.5) | Agent/Workflow `model` | 4 | 3 | 9 | 10 | Utility micro-tasks only — eligibility, summaries, scoring |
| `gpt-5.6-sol` | `codex exec -m` | 9 | 8 | 4 | 9 | Complex, open-ended, high-value Codex work needing depth and polish — default Codex pick when unsure |
| `gpt-5.6-terra` | `codex exec -m` | 7 | 7 | 6 | 9 | Everyday Codex workhorse — strong reasoning and tool use without Sol's depth |
| `gpt-5.6-luna` | `codex exec -m` | 5 | 5 | 8 | 10 | Clear, repeatable tasks — extraction, classification, transformation, structured summaries |

## Effort

`high` is every model's default. Start there: step down for routine, precisely-specified
work, and up for demanding agentic or capability-sensitive work. Never stamp below the
default just to save tokens.

Effort is not just thinking time — it also sets how many files the model reads, how much
it verifies, and how far it pushes a multi-step task before checking back in. A step that
must run unattended end to end, or whose job is verification, never goes below `medium`.

| Effort | Claude | Codex | Choose for |
| --- | --- | --- | --- |
| `low` | ✓ | ✓ | Mechanical, hard-guarded steps that may pause for the user |
| `medium` | ✓ | ✓ | Standard scoped edits; precisely-specified unattended flows |
| `high` | ✓ | ✓ | **Default.** Complex logic; verification-shaped work; consolidating judgment |
| `xhigh` | ✓ | ✓ (verify per model) | Cross-cutting or harness-core design; deep specs; long agentic runs |
| `max` | ✓ | ✓ | Hardest single problems — depth over speed; rare |
| `ultra` | — | ✓ | Work divisible into meaningful parallel parts (Codex runs subagents); rare |

## How to apply

- These are defaults, not limits. Standing permission to escalate: if a cheaper model's
  output misses the bar, redo the work on a smarter model without asking. Judge the
  output, not the price tag.
- Cost is a tie-breaker only; when axes conflict for anything that ships,
  intelligence > taste > cost. When torn between two tiers, take the higher. This
  overrides the global per-task/per-session token budgets in this repo.
- Pick the axis by the failure. Check the prompt, context, and scoping first — a task
  that shouldn't need escalation is usually starved upstream. Then: it didn't *know*
  enough (subtle bug, unfamiliar domain, confidently wrong however much context it got)
  → raise the model; it didn't *try* hard enough (skipped a file, skipped the tests,
  bailed mid-task, checked back in early) → raise the effort.
- One agent, one purpose. A fix that failed a review round escalates a tier (model or
  effort) — never retry the same tier twice. A repeat root-cause failure reassigns the
  task across providers.
- Anything user-facing (UI, copy, API design) needs taste ≥ 7.
- Codex implements only adversarial or algorithmic tasks a plan explicitly stamps to
  `gpt-5.6-sol` (security boundaries, parsers/matchers, architectural redesigns), or
  escalations after a repeat root-cause failure. `opus` reviews every Codex-authored
  change; Codex never solely gates its own code.

## Mechanics

- Claude models: pass the alias (`fable`, `opus`, `sonnet`, `haiku`) via the
  Agent/Workflow `model` parameter. Never hardcode a dated id like `claude-opus-4-8`.
- Codex models: run `codex exec` directly through this repo's skills and agents
  (`.agents/skills/`, `.codex/agents/*.toml`), passing model and effort explicitly per
  task — never rely on the `config.toml` default.
- Codex inside a Workflow (the `model` parameter only takes Claude aliases): spawn a
  thin `sonnet`/`low` wrapper agent whose prompt writes a self-contained codex prompt,
  runs `codex exec` via Bash, and returns the output.
