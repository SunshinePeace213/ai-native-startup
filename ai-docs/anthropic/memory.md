---
source: https://code.claude.com/docs/en/memory
fetched: 2026-07-21
---
> **In here:** CLAUDE.md files — locations, load order, imports · `.claude/rules/` — path-scoped and always-loaded rules · Auto memory — storage, limits, /memory

# How Claude remembers your project

> Give Claude persistent instructions with CLAUDE.md files, and let Claude accumulate learnings automatically with auto memory.

Each Claude Code session begins with a fresh context window. Two mechanisms carry knowledge across sessions:

- **CLAUDE.md files**: instructions you write to give Claude persistent context
- **Auto memory**: notes Claude writes itself based on your corrections and preferences

## CLAUDE.md vs auto memory

Both are loaded at the start of every conversation. Claude treats them as context, not enforced configuration. To block an action regardless of what Claude decides, use a PreToolUse hook instead.

| | CLAUDE.md files | Auto memory |
| :-- | :-- | :-- |
| **Who writes it** | You | Claude |
| **What it contains** | Instructions and rules | Learnings and patterns |
| **Scope** | Project, user, or org | Per repository, shared across worktrees |
| **Loaded into** | Every session | Every session (first 200 lines or 25KB) |
| **Use for** | Coding standards, workflows, project architecture | Build commands, debugging insights, preferences Claude discovers |

## CLAUDE.md files

Markdown files that give Claude persistent instructions; read at the start of every session.

### Choose where to put CLAUDE.md files

Locations in load order, broadest scope first:

| Scope | Location | Purpose |
| --- | --- | --- |
| **Managed policy** | macOS: `/Library/Application Support/ClaudeCode/CLAUDE.md`; Linux/WSL: `/etc/claude-code/CLAUDE.md`; Windows: `C:\Program Files\ClaudeCode\CLAUDE.md` | Organization-wide instructions |
| **User instructions** | `~/.claude/CLAUDE.md` | Personal preferences for all projects |
| **Project instructions** | `./CLAUDE.md` or `./.claude/CLAUDE.md` | Team-shared instructions, via source control |
| **Local instructions** | `./CLAUDE.local.md` | Personal project-specific preferences; gitignored |

CLAUDE.md and CLAUDE.local.md in the directory hierarchy above the working directory load in full at launch. Files in subdirectories load on demand when Claude reads files in those directories.

### Write effective instructions

- **Size**: target under 200 lines per CLAUDE.md file; longer files reduce adherence. Growing files should move content to path-scoped rules.
- **Structure**: markdown headers and bullets; organized sections beat dense paragraphs.
- **Specificity**: concrete, verifiable instructions ("Use 2-space indentation", not "Format code properly").
- **Consistency**: contradicting rules make Claude pick one arbitrarily; review CLAUDE.md, nested files, and `.claude/rules/` periodically.

### Import additional files

CLAUDE.md files can import additional files with `@path/to/import` syntax; imported files expand and load into context at launch. Relative paths resolve relative to the importing file. Recursive imports allowed, max depth four hops. Import parsing skips code spans and fenced code blocks — wrap a path in backticks to keep it literal. An import resolving outside the working directory is "external" and triggers a one-time approval dialog in project-level memory files; user-scope files (`~/.claude/CLAUDE.md`, `~/.claude/rules/`) load without the dialog.

### AGENTS.md

Claude Code reads `CLAUDE.md`, not `AGENTS.md`. If a repo uses `AGENTS.md` for other agents, create a `CLAUDE.md` that imports it (`@AGENTS.md`), optionally appending Claude-specific instructions below the import. A symlink (`ln -s AGENTS.md CLAUDE.md`) also works.

### How CLAUDE.md files load

Claude Code walks up the directory tree from the working directory, loading `CLAUDE.md` and `CLAUDE.local.md` from each directory. All discovered files concatenate (never override), ordered from filesystem root down to the working directory; within a directory `CLAUDE.local.md` appends after `CLAUDE.md`. Subdirectory CLAUDE.md files load on demand when Claude reads files there. Block-level HTML comments (`<!-- ... -->`) are stripped before injection — free for maintainer notes; comments inside code blocks are preserved.

`--add-dir` directories don't load memory files by default; set `CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1` to load `CLAUDE.md`, `.claude/CLAUDE.md`, `.claude/rules/*.md`, and `CLAUDE.local.md` from them.

## Organize rules with `.claude/rules/`

For larger projects, organize instructions into multiple files under `.claude/rules/`. Rules can be scoped to specific file paths so they only load into context when Claude works with matching files.

> Rules load into context every session or when matching files are opened. For task-specific instructions that don't need to be in context all the time, use skills instead.

### Set up rules

Place markdown files in the project's `.claude/rules/` directory, one topic per file, descriptive filenames. **All `.md` files are discovered recursively**, so rules can be organized into subdirectories like `frontend/` or `backend/`.

**Rules without `paths` frontmatter are loaded at launch with the same priority as `.claude/CLAUDE.md`.**

Project rules are skipped if `project` is excluded from `--setting-sources`.

### Path-specific rules

Scope a rule with YAML frontmatter and a `paths` field of glob patterns:

```markdown
---
paths:
  - "src/api/**/*.ts"
---

# API Development Rules

- All API endpoints must include input validation
```

Rules without a `paths` field are loaded unconditionally and apply to all files. Path-scoped rules trigger when Claude reads files matching the pattern, not on every tool use.

| Pattern | Matches |
| --- | --- |
| `**/*.ts` | All TypeScript files in any directory |
| `src/**/*` | All files under `src/` |
| `*.md` | Markdown files in the project root |
| `src/components/*.tsx` | React components in a specific directory |

Multiple patterns and brace expansion (`src/**/*.{ts,tsx}`) are supported. A pattern with an unparseable `[` is invalid and matches nothing; other patterns in the rule keep working (escape a literal `[` as `\[`).

### Share rules across projects with symlinks

`.claude/rules/` supports symlinked files and directories; circular symlinks are detected and handled.

### User-level rules

Personal rules in `~/.claude/rules/` apply to every project on the machine; they load before project rules, giving project rules higher priority.

## Manage CLAUDE.md for large teams

- **Managed CLAUDE.md**: deploy at the managed policy location (MDM/Group Policy/Ansible); cannot be excluded by individual settings. The `claudeMd` key in `managed-settings.json` embeds content directly (managed/policy settings only).
- **Exclude files**: `claudeMdExcludes` (any settings layer; arrays merge) skips CLAUDE.md files or rules directories by absolute-path glob. Managed policy CLAUDE.md cannot be excluded.

## Auto memory

Claude saves notes for itself as it works. On by default; toggle via `/memory` (`autoMemoryEnabled` in settings) or `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1`.

- **Storage**: `~/.claude/projects/<project>/memory/` — derived from the git repo, so all worktrees share one directory. Override with `autoMemoryDirectory` (absolute or `~/` path).
- **Layout**: a `MEMORY.md` index plus optional topic files. The first 200 lines or 25KB of `MEMORY.md` (whichever first) load at session start; topic files load on demand. After a write near/over the limit, Claude Code reminds/errors so the index gets rewritten (frontmatter and HTML comments are stripped before measuring).
- Main-conversation auto memory isn't loaded into subagents (a fork is the exception); a subagent's own auto memory (subagent `memory` field) is a separate directory.

## View and edit with `/memory`

`/memory` lists CLAUDE.md, CLAUDE.local.md, and memory file locations across scopes, toggles auto memory, and opens files. `/context` shows which files actually loaded this session.

## Troubleshoot memory issues

- **Claude isn't following CLAUDE.md**: CLAUDE.md is delivered as a user message after the system prompt — no strict-compliance guarantee. Check `/context` Memory files; make instructions specific; remove conflicts. Must-run instructions belong in hooks; system-prompt-level content in `--append-system-prompt`. The `InstructionsLoaded` hook logs which instruction files load, when, and why — useful for debugging path-scoped rules.
- **CLAUDE.md too large**: use path-scoped rules or trim; `@path` imports organize but don't reduce context. `/doctor` proposes trims.
- **Instructions lost after `/compact`**: project-root CLAUDE.md is re-read and re-injected after compaction; nested CLAUDE.md files reload on next read in that subdirectory.
