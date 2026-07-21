## Tooling & Runtime

- **Python**: Always use `uv` (Astral UV), never raw `python` or `pip`. Full general + testing conventions live in [general-practice.md](.claude/rules/python/general-practice.md)
- **JavaScript/TypeScript**: Always use `bun`, never raw `npm` or `npx`
- **Safe delete**: NEVER use `rm -rf` directly. Use `mv <target> ~/.Trash/` instead of permanent deletion to prevent accidental data loss

## Harness Development

- **Instructions, not rationale**: State what to do, not why. No "chose A over B", no decision logs, no design history — that's context bloat the agent never acts on.
- **No stray cross-refs**: Don't reference other commands or skills unless the file actually needs them to run. Mentions "for context" just add noise.
- **Keep it short**: Write harness/prompt files (skills, agents, commands, and rules under `.claude/` and `.agents/`) in fluent, KISS prose. Every line loads into context — say it once, briefly, then stop. When in doubt, cut.
- **Hooks**: [hooks.md](.claude/rules/harness-layer/hooks.md) is the authoritative catalog of every hook — event/matcher, contract, files, and the hook-test rules. Read it before any hook work; never re-summarize hook behavior elsewhere or re-derive it from memory.
- **Memory**: `AGENTS.md` is the hub — topic rules live in `.claude/rules/` (domain families in folders like `harness-layer/`, path-scoped via `paths:` frontmatter; rules every session needs stay flat at the root with no `paths:`). Never persist memory in `CLAUDE.md` (it only `@`-imports this file) or a new root markdown file. Fetch/record/edit/create contract: [memory-series.md](.claude/rules/memory-series.md).
- **Model selection**: every model/effort assignment — Claude and Codex; orchestrators, subagents, workflows, Codex tasks — follows [model-selection.md](.claude/rules/model-selection.md). It loads every session; never duplicate its guidance in templates, tasks, or commands.
- **Dev log**: cross-plan lessons live in [development-log.md](.claude/rules/development-log.md); per-plan process (phases, hand-offs, deviations, fixes, lessons) lives in that plan's `specs/<name>/implementation-notes.md`.

## Git Workflow & Pull Requests

- **Standard**: Follow the commit, PR, and issue standards in [git-workflow.md](.claude/rules/git-workflow.md)

## Project Structure

- `.agents/` -- Codex Skills Configuration
- `.claude/rules/` — path-scoped project rules
- `ai-docs/` — cached official docs KB managed by `/kb` (catalog: `ai-docs/index.md`), plus hand-written project notes
- `specs/` — planning files (per-plan folders; pre-plan discovery pages live in each plan's `discovery/`)

## Harness-Layer Pipeline

- **Core** — every task, app code or harness work: `/harness-layer:harness-plan` → `/harness-layer:harness-build` → `/harness-layer:harness-review` → `/harness-layer:harness-ship`.
- **Discovery (optional, pre-plan)** — run when the problem is still fuzzy; each pass hands its successor an improved prompt and commits its pages to `specs/<slug>/discovery/` for the plan to draft from:
  - `/harness-layer:harness-unknowns` — surface unknown unknowns in unfamiliar code or domains.
  - `/harness-layer:harness-brainstorm` — rough problem → intervention options, cheapest to most ambitious.
  - `/harness-layer:harness-prototypes` — throwaway mocks and design directions to react to.
  - `/harness-layer:harness-interview` — lock every open decision, round by round.
- **KB** — the domain-expert layer auto-engages when work touches the harness; keep `ai-docs/` fresh with `/harness-layer:kb`.
- **Artifacts** — pipeline stages publish interactive pages committed under `specs/<name>/artifacts/`; crafting rules: [artifacts.md](.claude/rules/harness-layer/artifacts.md).
