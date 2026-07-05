## Tooling & Runtime

- **Python**: Always use `uv` (Astral UV), never raw `python` or `pip`
- **JavaScript/TypeScript**: Always use `bun`, never raw `npm` or `npx`
- **Python rich panels**: Always full width panels
- **Safe delete**: NEVER use `rm -rf` directly. Use `mv <target> ~/.Trash/` instead of permanent deletion to prevent accidental data loss

## Harness Development

- **Hooks**: files Claude edits are auto-formatted in place (Prettier / Ruff / markdownlint); a fresh checkout installs the linters on SessionStart or via `/meta-install`. Details: [HARNESS-LAYER.md](./HARNESS-LAYER.md)
- **Keep it short**: Write harness/prompt files (skills, agents, commands, and rules under `.claude/` and `.agents/`) in fluent, KISS prose. Every line loads into context — say it once, briefly, then stop. When in doubt, cut.
- **Memory goes here**: Persist project memory and preferences in this `AGENTS.md`, not `CLAUDE.md` (which only `@`-imports this file).
- **Instructions, not rationale**: State what to do, not why. No "chose A over B", no decision logs, no design history — that's context bloat the agent never acts on.
- **No stray cross-refs**: Don't reference other commands or skills unless the file actually needs them to run. Mentions "for context" just add noise.
- **Model selection**: Always pass **alias** (`opus`, `sonnet`, `haiku`, `fable`). Never hardcode a dated id like `claude-sonnet-4-6` or `claude-opus-4-8`

## Git Workflow & Pull Requests

- **Standard**: Follow the commit, PR, and issue standards in [GIT-COMMIT-PR-MESSAGE.md](./GIT-COMMIT-PR-MESSAGE.md)

## Project Structure

- `.agents/` -- Codex Skills Confiugration
- `ai-docs/` — cached official docs KB managed by `/kb` (catalog: `ai-docs/index.md`), plus hand-written project notes
- `specs/` — planning files
- `HARNESS-LAYER.md` — how the project's auto-format/lint hooks work (format-on-save, linter install)

## Harness-Layer Pipeline

- **Harness development** — files under `.claude/` and `.agents/`: `/harness-layer:harness-plan` → `/harness-layer:harness-build` → `/ship`. Keep the `ai-docs/` KB fresh with `/harness-layer:kb`.
- **Coding task** — application code: `/plan-w-team` → `/build` → `/ship`.
