## Tooling & Runtime

- **Python**: Always use `uv` (Astral UV), never raw `python` or `pip`. Full general + testing conventions live in [general-practice.md](.claude/rules/python/general-practice.md)
- **JavaScript/TypeScript**: Always use `bun`, never raw `npm` or `npx`
- **Safe delete**: NEVER use `rm -rf` directly. Use `mv <target> ~/.Trash/` instead of permanent deletion to prevent accidental data loss

## Knowledge Base

- `ai-docs/` is the shared KB — the wiki (`ai-docs/wiki/`, compiled synthesis; catalog: `ai-docs/wiki/index.md`) over the raw-source layer (immutable archives of web pages, PDFs, and files in the other `ai-docs/` folders).
- Start every task wiki-first: `qmd search "<terms>" -c wiki` (or `qmd query` for a concept) to find pages matching the work, `Read` the hits, and follow their `sources:` into the raw layer — `-c sources` — when the source's own words matter. Nothing relevant → move on.
- Consulted an official page the KB lacks → archive and ingest it with `/wiki:ingest <url>`.
- Durability rule: pages worth keeping get archived into the raw layer via `source-archiver`; synthesis that passes the crystallization gate — cited, non-duplicative — files into the wiki via `/wiki:ingest`; synthesis that doesn't stays in that plan's `discovery/research.md`; raw search results go nowhere.
- Archives are read-only: fix wrong or stale content by re-archiving through `source-archiver`, never by hand-editing. If the source itself is wrong, record a project note in `ai-docs/` instead.

## Wiki Layer

- `ai-docs/wiki/` — LLM-maintained synthesis over the raw-source layer; open-ended domain folders, each with its own `schema.md` over one shared spine; `personal/` is gitignored and local-only.
- Operations: `/wiki:ingest`, `/wiki:query`, `/wiki:lint` (weekly routine + on-demand), `/wiki:status`.
- Search is `qmd` over two collections — `wiki` (synthesis) and `sources` (raw archives) — always scoped with `-c`. Anything that writes under `ai-docs/` ends with `qmd update && qmd embed`.
- Standards, schema, search contract, lane fit, metrics, archetypes: [wiki-standards.md](.claude/rules/wiki-layer/wiki-standards.md). Sources stay immutable; ingest reads, never edits them.

## Harness Development

- **Instructions, not rationale**: State what to do, not why. No "chose A over B", no decision logs, no design history — that's context bloat the agent never acts on.
- **No stray cross-refs**: Don't reference other commands or skills unless the file actually needs them to run. Mentions "for context" just add noise.
- **Keep it short**: Write harness/prompt files (skills, agents, commands, and rules under `.claude/`) in fluent, KISS prose. Every line loads into context — say it once, briefly, then stop. When in doubt, cut.
- **Hooks**: [hooks.md](.claude/rules/harness-layer/hooks.md) is the authoritative catalog of every hook — event/matcher, contract, files, and the hook-test rules. Read it before any hook work; never re-summarize hook behavior elsewhere or re-derive it from memory.
- **Standards**: plans must clear [spec-standards.md](.claude/rules/harness-layer/spec-standards.md); implementation diffs must clear [impl-standards.md](.claude/rules/harness-layer/impl-standards.md). The drafting agent self-checks; the Codex gate judges against the same list.
- **Tests**: which tier a change needs — contract, drift, or eval — follows [test-tiers.md](.claude/rules/harness-layer/test-tiers.md). CI (`.github/workflows/ci.yml`) runs the suite and lints `.claude/hooks/` + `tests/` on every PR.
- **Memory**: `AGENTS.md` is the hub — topic rules live in `.claude/rules/` (domain families in folders like `harness-layer/`, path-scoped via `paths:` frontmatter; rules every session needs stay flat at the root with no `paths:`). Never persist memory in `CLAUDE.md` (it only `@`-imports this file) or a new root markdown file. Fetch/record/edit/create contract: [memory-series.md](.claude/rules/memory-series.md).
- **Model selection**: every model/effort assignment — Claude and Codex; orchestrators, subagents, workflows, Codex tasks — follows [model-selection.md](.claude/rules/model-selection.md). It loads every session; never duplicate its guidance in templates, tasks, or commands.
- **Orchestration**: choosing between doing the work yourself, subagents, and an agent team — plus the shared `Task*` board — follows [orchestration.md](.claude/rules/orchestration.md). It loads every session.
- **Lessons**: the build/review memory steps route each lesson to its home per [memory-series.md](.claude/rules/memory-series.md) — file-scoped → the matching rule, pipeline-process → the file it corrects; per-plan process (phases, hand-offs, deviations, fixes) lives in that plan's `specs/<name>/implementation-notes.md`.

## Git Workflow & Pull Requests

- **Standard**: Branching, commits, and pushing follow [git-workflow.md](.claude/rules/git-workflow.md); PR templates, issue forms, labels, linking, and marker comments follow [pr-process.md](.claude/rules/harness-layer/pr-process.md).

## Project Structure

- `.claude/rules/` — path-scoped project rules
- `ai-docs/` — the wiki + raw-source KB managed by the `/wiki:*` commands (catalog: `ai-docs/wiki/index.md`), plus hand-written project notes
- `specs/` — planning files (per-plan folders; pre-plan discovery pages live in each plan's `discovery/`)
- `specs/index.md` — catalog of what has shipped. Check it before concluding a feature does not exist, and read a plan's `summary.md` (outcome) before its `spec.md` (intent).

## Harness-Layer Pipeline

- **Router** — at intake, a request passing every direct-lane check (≤2 files, ~≤80 lines, docs/chore/style/fix, no executable surface, nothing new) ships via `/harness-layer:harness-direct`; anything else — and any doubt — takes the full lane.
- **Core (full lane)** — every other task, app code or harness work: `/harness-layer:harness-plan` → `/harness-layer:harness-build` → `/harness-layer:harness-review` → `/harness-layer:harness-ship`.
- **Discovery (optional, pre-plan)** — run when the problem is still fuzzy; each pass hands its successor an improved prompt and commits its pages to `specs/<slug>/discovery/` for the plan to draft from:
  - `/harness-layer:harness-unknowns` — surface unknown unknowns in unfamiliar code or domains.
  - `/harness-layer:harness-brainstorm` — rough problem → intervention options, cheapest to most ambitious.
  - `/harness-layer:harness-prototypes` — throwaway mocks and design directions to react to.
  - `/harness-layer:harness-research` — vague mission → focused questions → a provenance-tiered claims ledger (quick/standard/deep tiers).
  - `/harness-layer:harness-interview` — lock every open decision, round by round.
- **Questioning the user** — when unknowns need the user's answers outside the passes above (an ad-hoc design discussion, a mid-task ambiguity), invoke the `grilling` skill instead of improvising questions.
- **KB** — the domain-expert layer auto-engages when work touches the harness, grounding plan claims in the KB per `## Knowledge Base`; grow it with `/wiki:ingest`.
- **Lessons** — ship folds each plan's ledger + metrics into `specs/lessons/digest.md`; `/harness-layer:harness-lessons` runs the deep pass monthly, landing amendments through the direct lane; plan reads the digest for the touched surface before drafting.
- **Artifacts** — pipeline stages publish interactive pages committed under `specs/<name>/artifacts/`; crafting rules: [artifacts.md](.claude/rules/harness-layer/artifacts.md).

## Designing a New Layer

A new layer (cpo, studio, …) is a full-lane plan whose product is another
pipeline. It ships four things: its raw-source group under `ai-docs/`, its own
standards file, its lane fit (which of its work takes direct vs full), and its
metrics targets — and names which archetypes (Prototyper / Builder / Sweeper /
Grower / Maintainer) staff it at its stage.
