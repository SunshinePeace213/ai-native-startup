

## Tooling & Runtime

- **Python**: Always use `uv` (Astral UV), never raw `python` or `pip`
- **JavaScript/TypeScript**: Always use `bun`, never raw `npm` or `npx`
- **Python rich panels**: Always full width panels
- **Safe delete**: NEVER use `rm -rf` directly. Use `mv <target> ~/.Trash/` instead of permanent deletion to prevent accidental data loss
- **Model selection**: For simple work that doesn't require a pinned version, pass a model **alias** (`opus`, `sonnet`, `haiku`) so it always resolves to the latest — never hardcode a dated id like `claude-sonnet-4-6` or `claude-opus-4-8`. Pin a specific version only when reproducibility genuinely requires it. Applies everywhere a model is chosen: `claude -p`, `--model` flags, subagent config, and SDK calls.
