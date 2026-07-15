## Tooling & Runtime

- **Python**: Always use `uv` (Astral UV), never raw `python` or `pip`. Full general + testing conventions live in [python-practice.md](.claude/rules/python-practice.md)
- **JavaScript/TypeScript**: Always use `bun`, never raw `npm` or `npx`
- **Safe delete**: NEVER use `rm -rf` directly. Use `mv <target> ~/.Trash/` instead of permanent deletion to prevent accidental data loss

## Harness Development

- **Instructions, not rationale**: State what to do, not why. No "chose A over B", no decision logs, no design history — that's context bloat the agent never acts on.
- **No stray cross-refs**: Don't reference other commands or skills unless the file actually needs them to run. Mentions "for context" just add noise.
- **Keep it short**: Write harness/prompt files (skills, agents, commands, and rules under `.claude/` and `.agents/`) in fluent, KISS prose. Every line loads into context — say it once, briefly, then stop. When in doubt, cut.
- **Hooks**: [harness-hooks.md](.claude/rules/harness-hooks.md) is the authoritative catalog of every hook — event/matcher, contract, files, and the hook-test rules. Read it before any hook work; never re-summarize hook behavior elsewhere or re-derive it from memory.
- **Memory goes here**: Persist project memory and preferences in this `AGENTS.md`, not `CLAUDE.md` (which only `@`-imports this file).
- **Memory series**: `AGENTS.md` is the hub. Topic rules live in `.claude/rules/<kebab-case>.md`, path-scoped via `paths:` frontmatter so they load only when relevant. A genuinely new convention series → a new rule file there, referenced from here — brief and imperative, no rationale.
- **Model selection**: Always pass **alias** (`opus`, `sonnet`, `haiku`, `fable`). Never hardcode a dated id like `claude-sonnet-4-6` or `claude-opus-4-8`
- **Selection principle — Quality > time > cost**: pick the model and effort the task's difficulty demands; when torn between two tiers, take the higher. One agent, one purpose. A fix that failed a review round escalates a tier (model or effort) — never retry the same tier twice. In this repo this overrides the global per-task/per-session token budgets.
- **Model & effort selection** — pick by the nature of the work

| Model    | Choose for                                                                                                                        |
| -------- | --------------------------------------------------------------------------------------------------------------------------------- |
| `fable`  | Highest-judgment work — specs, build orchestration, consolidating review findings. Orchestrator only — never deploy as a subagent |
| `opus`   | Complex implementation; behavior-preserving refinement                                                                            |
| `sonnet` | Default workhorse — standard implementation, review fixes, guarded mechanical flows                                               |
| `haiku`  | Utility micro-tasks — eligibility, summaries, scoring                                                                             |

| Effort   | Choose for                                                |
| -------- | --------------------------------------------------------- |
| `low`    | Mechanical or hard-guarded steps                          |
| `medium` | Standard scoped edits and behavior-preserving refinement  |
| `high`   | Complex logic; consolidating multiple sources of judgment |
| `xhigh`  | Cross-cutting or harness-core design; deep specs          |
| `max`    | Hardest problems — maximum depth on a single task; rare   |

- **Codex partnership**: Codex is a design consultant and escalation implementer, not a general co-builder — it implements only when a plan explicitly stamps an adversarial or algorithmic task (security boundaries, parsers/matchers, architectural redesigns) to `gpt-5.6-sol`, or on reassignment after a repeat root-cause failure. Claude `opus` reviews every Codex-authored change; Codex never solely gates its own code.
- **Model & effort selection (Codex)** — never hardcode a Codex model or effort: before each peer review or Codex-implemented task, pick both from the task at hand and pass them on `codex exec`:

| Codex model     | Choose for                                                                                 |
| --------------- | ------------------------------------------------------------------------------------------ |
| `gpt-5.6-sol`   | Complex, open-ended, high-value work needing depth and polish — default when unsure        |
| `gpt-5.6-terra` | Everyday workhorse — strong reasoning and tool use without Sol's depth                     |
| `gpt-5.6-luna`  | Clear, repeatable tasks — extraction, classification, transformation, structured summaries |

| Codex effort | Choose for                                                           |
| ------------ | -------------------------------------------------------------------- |
| `low`        | Quick, well-scoped tasks                                             |
| `medium`     | Tasks needing more planning — the balanced default                   |
| `high`       | Difficult multi-step work with several sources or tradeoffs          |
| `xhigh`      | The hardest rounds (model-dependent — verify support)                |
| `max`        | Hardest single problems — depth over speed and usage; rare           |
| `ultra`      | Work divisible into meaningful parallel parts (runs subagents); rare |

## Git Workflow & Pull Requests

- **Standard**: Follow the commit, PR, and issue standards in [GIT-COMMIT-PR-MESSAGE.md](./GIT-COMMIT-PR-MESSAGE.md)

## Project Structure

- `.agents/` -- Codex Skills Configuration
- `.claude/rules/` — path-scoped project rules
- `ai-docs/` — cached official docs KB managed by `/kb` (catalog: `ai-docs/index.md`), plus hand-written project notes
- `specs/` — planning files

## Harness-Layer Pipeline

- **Pipeline** — every task, application code or harness work: `/harness-layer:harness-plan` → `/harness-layer:harness-build` → `/harness-layer:harness-ship`. The domain-expert KB layer engages automatically when the work touches the harness. Keep the `ai-docs/` KB fresh with `/harness-layer:kb`.
- **Unknowns checkpoints** — the pipeline commands fire them conditionally: blindspot pass and taste route at plan time, deviation logging in `specs/<name>/implementation-notes.md` at build time, ship brief + quiz at approval. Pipeline artifacts live committed under `specs/<name>/artifacts/` and publish best-effort as interactive pages.
