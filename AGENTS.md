

## Tooling & Runtime

- **Python**: Always use `uv` (Astral UV), never raw `python` or `pip`
- **JavaScript/TypeScript**: Always use `bun`, never raw `npm` or `npx`
- **Python rich panels**: Always full width panels
- **Safe delete**: NEVER use `rm -rf` directly. Use `mv <target> ~/.Trash/` instead of permanent deletion to prevent accidental data loss
