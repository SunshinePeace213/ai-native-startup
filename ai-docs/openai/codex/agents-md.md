---
source: https://developers.openai.com/codex/guides/agents-md
fetched: 2026-07-05
---

> **In here:** AGENTS.md hierarchy and discovery · Global and project-level guidance · Custom instruction layering

# Custom Instructions with AGENTS.md

Codex reads `AGENTS.md` files to apply project-specific and global guidance before executing tasks. This layered approach ensures consistent expectations across different repositories.

## Discovery Hierarchy

Codex follows a three-tier precedence order:

1. **Global scope**: Checks `~/.codex/AGENTS.override.md` first, then `~/.codex/AGENTS.md`
2. **Project scope**: Walks from repository root to current directory, checking each level for override files, then regular files
3. **Merge order**: Combines files from root downward, with closer files overriding earlier guidance

Empty files are skipped, and discovery stops once combined content reaches `project_doc_max_bytes` (32 KiB default).

## Setting Up Global Guidance

Store persistent defaults in your Codex home directory:

```bash
mkdir -p ~/.codex
```

Create `~/.codex/AGENTS.md`:

```markdown
## Working agreements

- Always run `npm test` after modifying JavaScript files.
- Prefer `pnpm` when installing dependencies.
- Ask for confirmation before adding new production dependencies.
```

Verify loading:

```bash
codex --ask-for-approval never "Summarize the current instructions."
```

## Layering Project Instructions

Add repository-level guidance in the root `AGENTS.md`, then create nested overrides for specialized directories.

**Repository root example**:
```markdown
## Repository expectations

- Run `npm run lint` before opening a pull request.
- Document public utilities in `docs/` when you change behavior.
```

**Team-specific override** (`services/payments/AGENTS.override.md`):
```markdown
## Payments service rules

- Use `make test-payments` instead of `npm test`.
- Never rotate API keys without notifying the security channel.
```

## Custom Fallback Filenames

Modify `~/.codex/config.toml` to recognize alternate instruction files:

```toml
project_doc_fallback_filenames = ["TEAM_GUIDE.md", ".agents.md"]
project_doc_max_bytes = 65536
```

Codex now checks in order: `AGENTS.override.md` → `AGENTS.md` → `TEAM_GUIDE.md` → `.agents.md`.

## Verification Steps

- Run `codex --ask-for-approval never "Summarize current instructions."` from a repo root
- Test nested overrides with `codex --cd subdir --ask-for-approval never "Show active instruction files."`
- Check `session-*.jsonl` files if session logging is enabled
- Restart Codex to rebuild the instruction chain fresh

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Nothing loads | Verify repository root via `codex status`; ensure files contain content |
| Wrong guidance | Look for unexpected `AGENTS.override.md` files up the directory tree |
| Fallback names ignored | Confirm spelling in config; restart Codex |
| Instructions truncated | Increase `project_doc_max_bytes` or split across directories |

For additional context, consult the [AGENTS.md](https://agents.md) website and review [Prompting Codex](/codex/prompting) for complementary patterns.
