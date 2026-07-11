## Tooling & Runtime

- **Python**: Always use `uv` (Astral UV), never raw `python` or `pip`
- **JavaScript/TypeScript**: Always use `bun`, never raw `npm` or `npx`
- **Python rich panels**: Always full width panels
- **Safe delete**: NEVER use `rm -rf` directly. Use `mv <target> ~/.Trash/` instead of permanent deletion to prevent accidental data loss

## Python Testing

When writing test cases or running Python tests, use the installed pytest plugins — don't reinvent what they provide:

- **Run**: `uv run pytest` from the repo root — runs `tests/` in parallel (`-n auto`, pytest-xdist) with pytest-sugar output and a 60s per-test timeout (pytest-timeout); config in `pyproject.toml`
- **Debug one test**: `uv run pytest <file>::<test> -n 0` — disables workers so `-s`, breakpoints, and ordered output work
- **Timeouts**: a hung test is killed at 60s; mark a known-slow test `@pytest.mark.timeout(120)` — never raise the global value
- **Coverage**: `uv run pytest --cov=<path> --cov-report=term-missing` (pytest-cov) — measures in-process code only; code exercised via subprocess (e.g. the hooks) reports 0%
- **Mocking**: use the `mocker` fixture (pytest-mock; patches auto-undo at teardown) or built-in `monkeypatch`; never import `unittest.mock` directly
- **New tests must be parallel-safe**: isolate all state per test (`tmp_path`, `monkeypatch`); never rely on test order, shared globals, or fixed paths/ports
- **UI**: sugar theme lives in `pytest-sugar.conf` (repo root, loaded from cwd); `-p no:sugar` for plain output; the live bar only renders on a TTY — non-TTY runs (agents, CI) fall back to plain dots, which is correct for log parsing
- **No flake-retry plugins**: a failing test fails the run — fix it, don't auto-rerun it

## Harness Development

- **Hooks**: files Claude edits are auto-formatted in place (Prettier / ESLint / Ruff / markdownlint); unfixable lint errors come back as exit-2 diagnostics — fix them. New worktrees get `bun install` + `uv sync` automatically; on a fresh clone use the `meta-install` skill. Details: [HARNESS-LAYER.md](./HARNESS-LAYER.md)
- **Keep it short**: Write harness/prompt files (skills, agents, commands, and rules under `.claude/` and `.agents/`) in fluent, KISS prose. Every line loads into context — say it once, briefly, then stop. When in doubt, cut.
- **Memory goes here**: Persist project memory and preferences in this `AGENTS.md`, not `CLAUDE.md` (which only `@`-imports this file).
- **Memory series**: The root ALL-CAPS files are the project memory series; `AGENTS.md` is the hub. A genuinely new convention series → a new root `ALL-CAPS.md` referenced from here — brief and imperative, no rationale.
- **Settings sync**: Experiment in `.claude/settings.local.json` (untracked, personal, overrides in-session). Before merging to main, fold changes that should ship into the tracked `.claude/settings.json`.
- **Instructions, not rationale**: State what to do, not why. No "chose A over B", no decision logs, no design history — that's context bloat the agent never acts on.
- **No stray cross-refs**: Don't reference other commands or skills unless the file actually needs them to run. Mentions "for context" just add noise.
- **Model selection**: Always pass **alias** (`opus`, `sonnet`, `haiku`, `fable`). Never hardcode a dated id like `claude-sonnet-4-6` or `claude-opus-4-8`
- **Model & effort selection** — pick by the nature of the work

| Model    | Choose for                                                                          |
| -------- | ----------------------------------------------------------------------------------- |
| `fable`  | Highest-judgment work — specs, build orchestration, consolidating review findings   |
| `opus`   | Complex implementation; behavior-preserving refinement                              |
| `sonnet` | Default workhorse — standard implementation, review fixes, guarded mechanical flows |
| `haiku`  | Utility micro-tasks — eligibility, summaries, scoring                               |

| Effort   | Choose for                                                |
| -------- | --------------------------------------------------------- |
| `low`    | Mechanical or hard-guarded steps                          |
| `medium` | Standard scoped edits and behavior-preserving refinement  |
| `high`   | Complex logic; consolidating multiple sources of judgment |
| `xhigh`  | Cross-cutting or harness-core design; deep specs          |
| `max`    | Hardest problems — maximum depth on a single task; rare   |

- **Model & effort selection (Codex)** — never hardcode a Codex model or effort: before each peer review, pick both from the task at hand and pass them on `codex exec`:

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

- `.agents/` -- Codex Skills Confiugration
- `ai-docs/` — cached official docs KB managed by `/kb` (catalog: `ai-docs/index.md`), plus hand-written project notes
- `specs/` — planning files
- `HARNESS-LAYER.md` — how the project's auto-format/lint hooks work (format-on-save, linter install)

## Harness-Layer Pipeline

- **Pipeline** — every task, application code or harness work: `/harness-layer:harness-plan` → `/harness-layer:harness-build` → `/harness-layer:harness-ship`. The domain-expert KB layer engages automatically when the work touches the harness. Keep the `ai-docs/` KB fresh with `/harness-layer:kb`.
