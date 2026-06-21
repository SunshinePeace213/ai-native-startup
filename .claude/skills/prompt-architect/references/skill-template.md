# Skill Template (directory format)

A skill is a directory containing `SKILL.md` plus optional `references/`, `scripts/`, `assets/`. Auto-discovered by Claude based on the YAML description, also invocable as `/skill-name`.

**Note:** Commands and skills share frontmatter. `.claude/commands/deploy.md` (single file) and `.claude/skills/deploy/SKILL.md` (directory) both create `/deploy`. The directory format is recommended whenever bundled resources help; see `command-template.md` for the single-file format.

Reference: https://code.claude.com/docs/en/skills#frontmatter-reference

## Storage

| Location | Scope |
|---|---|
| `~/.claude/skills/<name>/SKILL.md` | Personal, all projects |
| `.claude/skills/<name>/SKILL.md` | Single project — commit to share with team |
| `<plugin>/skills/<name>/SKILL.md` | Bundled with plugins |
| Managed settings dir | Org-wide, admin-deployed |

Precedence when names collide: enterprise > personal > project. Plugin skills use `plugin-name:skill-name`.

## Directory layout

```
my-skill/
├── SKILL.md (required)
├── config.json (optional — per-installation settings, Thariq Tip 5)
├── references/topic-a.md (loaded on demand)
├── scripts/helper.py (executed, not loaded into context)
└── assets/template.html (used as output material)
```

Keep `SKILL.md` under 500 lines. Push longer reference material into `references/` (Thariq Tip 3 — progressive disclosure).

## Frontmatter reference

All fields optional. Only `description` is recommended.

```yaml
---
name: skill-name
description: What this skill does and when to use it
when_to_use: Additional trigger context
argument-hint: "[argument-name] [optional-arg]"
arguments: [first, second]
disable-model-invocation: false
user-invocable: true
allowed-tools: Read Grep Bash(git *)
model: inherit
effort: high
context: fork
agent: Explore
paths: "**/*.ts, **/*.tsx"
shell: bash
hooks:
  PostToolUse:
    - matcher: "Edit|Write"
      hooks:
        - type: command
          command: "npx prettier --write"
---
```

### Field-by-field

| Field | Required | Purpose |
|---|---|---|
| `name` | No (defaults to dir name) | Display name; kebab-case, max 64 chars |
| `description` | **Recommended** | What it does AND its trigger phrases. **Write for the model, not humans** (Thariq Tip 6). Combined with `when_to_use`, hard-capped at 1,536 chars — but aim *far* lower (see "Description budget" below). |
| `when_to_use` | No | Non-redundant routing only — the gate/precondition + which sibling to route to instead. **Never repeat trigger phrases already in `description`** (the listing concatenates both and counts every char). Omit it entirely if it would only echo the description. |
| `argument-hint` | No | Shown in autocomplete (e.g., `[issue-number]`) |
| `arguments` | No | Named positional arguments; map to `$name` in body |
| `disable-model-invocation` | No (default `false`) | `true` = only user can `/name`; Claude can't auto-trigger |
| `user-invocable` | No (default `true`) | `false` = hidden from `/` menu; only Claude can invoke |
| `allowed-tools` | No | Tools pre-approved while skill active |
| `model` | No | Override session model while skill active |
| `effort` | No | Override session effort (`low`..`max`) |
| `context` | No | `fork` runs skill in a forked subagent context |
| `agent` | No | Subagent type for `context: fork` (default `general-purpose`) |
| `hooks` | No | Lifecycle hooks scoped to this skill (see `hooks.md`). On-demand hooks (Thariq Tip 9). |
| `paths` | No | Globs; skill auto-loads only when matching files in play |
| `shell` | No | `bash` (default) or `powershell` |

### Description budget (and the de-dup rule)

The skill listing — every skill's `description` + `when_to_use` — is injected into **every session**, and it has two ceilings:

- **Per-entry: 1,536 chars** (`description` + `when_to_use` combined). Over this, the entry is **truncated** mid-text in the listing — trigger phrases at the end silently vanish.
- **Global: ~1% of the context window** for the whole listing. When it overflows, Claude **drops the least-used skills' descriptions first** — so one bloated skill silently evicts *other* skills from auto-discovery. Run `/doctor` to see whether the budget is overflowing and which skills are affected; the lever to raise it (`skillListingBudgetFraction`) costs tokens on every session, so trimming is the sustainable fix.

A long description is not free and does **not** "trigger better" — past a tight trigger set it only burns shared budget. Rules for every artifact this skill generates:

- **Front-load the primary use case + trigger phrases in `description`** — that is the part that survives truncation.
- **`when_to_use` = gate + NOT-boundaries only.** The precondition ("when a `hypothesis.md` exists") and sibling-routing ("not for X → /other-skill"). Never duplicate trigger phrases already in `description`; if `when_to_use` would only echo it, delete the field.
- **Keep the `description` field under 300 chars.** That's this layer's standard — the description's one job is telling Claude *when* to load the skill, so it needs trigger keywords, not how-it-works prose or feature lists. Put the long explanation in the body. (1,536 combined is the hard wall; 300 on `description` is the editorial target.)
- Validate: `python3 ${CLAUDE_SKILL_DIR}/scripts/quick_validate.py <artifact>` — it **fails** the combined 1,536 cap and **warns** when the `description` field exceeds 300 chars or when `when_to_use` largely repeats `description`.

### Reference vs Task content

**Reference content** — Claude auto-invokes based on description:

```yaml
---
name: api-conventions
description: REST API design patterns for this codebase. Use when writing or reviewing API endpoints.
---
```

**Task content** — user-triggered workflow with side effects:

```yaml
---
name: deploy
description: Deploy the application to production
disable-model-invocation: true
allowed-tools: Bash(npm test), Bash(npm run build), Bash(kubectl *)
---
```

Set `disable-model-invocation: true` so Claude doesn't auto-trigger a deploy because the code "looks ready."

### Invocation matrix

| Frontmatter | You invoke | Claude invokes | Loaded when |
|---|---|---|---|
| (default) | Yes (`/name`) | Yes (auto) | Description always in context; body when invoked |
| `disable-model-invocation: true` | Yes (`/name`) | No | Description not in context; body when you invoke |
| `user-invocable: false` | No | Yes (auto) | Description always in context; body when invoked |

## String substitutions

| Variable | Expands to |
|---|---|
| `$ARGUMENTS` | All arguments passed when invoking |
| `$ARGUMENTS[N]` / `$N` | Argument at position N (0-indexed) |
| `$name` | Named argument from `arguments` frontmatter |
| `${CLAUDE_SKILL_DIR}` | Directory containing this SKILL.md — use for bundled scripts |
| `${CLAUDE_PLUGIN_DATA}` | Stable per-plugin folder for persistent data (Thariq Tip 7) |
| `${CLAUDE_SESSION_ID}`, `${CLAUDE_EFFORT}` | Session metadata |

If `$ARGUMENTS` isn't present but arguments were passed, they're appended as `ARGUMENTS: <value>`.

## Dynamic context injection

Run a shell command and inline its output **before Claude sees the skill**:

```markdown
## Current changes
!`git diff HEAD`

## Instructions
Summarize the changes above...
```

The `` !`cmd` `` syntax is preprocessing — Claude sees the output, not the command. For multi-line: use a fenced block opened with ` ```! `.

## Body structure

```markdown
---
[frontmatter as above]
---

# [Skill Name]

[1-2 sentence overview. Lean per Thariq Tip 1 — don't restate what Claude already does.]

## When this skill applies
[Concrete situations and example phrasings.]

## Gotchas
[High-signal items not in public docs. See "Gotchas" below — often the most valuable section of a mature skill.]

## Workflow
[Goal + constraints, not a rigid script (Thariq Tip 4).]

## [Domain-specific sections]

## Reference files
- `references/x.md` — when to read this

## Bundled scripts
- `scripts/y.py` — purpose
```

## The Gotchas section (Thariq Tip 2)

Highest-signal section in mature skills. Flat bullets, each one or two sentences:

```markdown
## Gotchas
- Always check `.env.local` before `npm run build` — the build silently picks up old values from `.env` if `.env.local` was deleted.
- `CREATE INDEX CONCURRENTLY` cannot run inside a transaction — omit BEGIN/COMMIT for those.
- This API rate-limits at 60 req/min — add `sleep 1` between calls in batch jobs.
```

**Belongs:** silent failures, order-of-operations not enforced by tooling, env vars that must be set/unset, rate limits, naming conventions downstream tools depend on. **Doesn't belong:** generic best practices, background context.

Skip for brand-new skills; add the first time something bites — that's the first real gotcha.

## Per-installation setup (Thariq Tip 5)

If the skill needs per-user context (URLs, account IDs, channels):

```json
{ "grafana_url": "...", "alert_channel": "#oncall" }
```

```markdown
## Setup
Read `${CLAUDE_SKILL_DIR}/config.json`.
If it doesn't exist: ask the user for values, write the file, then proceed.
If it exists: use directly.
```

## When to add bundled resources

| Subdir | Add when |
|---|---|
| `references/` | Content is substantial (>1-2 paragraphs), loaded only sometimes, better as stable doc than inline |
| `scripts/` | Same multi-step operation comes up across invocations; deterministic; Claude keeps rewriting the same helper (Tip 8) |
| `assets/` | Skill outputs files that need templates, fonts, icons, brand elements |
| `config.json` | Per-installation context varies between users |

Reference scripts with `${CLAUDE_SKILL_DIR}`:

```markdown
Run: `python3 ${CLAUDE_SKILL_DIR}/scripts/analyze.py`
```

## Worked example (SQL migration writer)

```yaml
---
name: sql-migration-writer
description: |
  Draft safe, reversible PostgreSQL migration files following the project's conventions.
  Use when the user asks to add/drop a column, change a constraint, backfill data, add
  an index, or anything involving "migration", "schema change", or "alter table".
allowed-tools: Read, Grep, Glob, Bash(ls migrations/*), Bash(cat migrations/*)
paths: "migrations/**, db/schema.rb, db/structure.sql"
hooks:
  PostToolUse:
    - matcher: "Write"
      hooks:
        - type: command
          command: "${CLAUDE_SKILL_DIR}/scripts/validate_migration.sh"
---

# SQL Migration Writer

Drafts safe, reversible SQL migration files.

## Gotchas
- `CREATE INDEX CONCURRENTLY` cannot run inside a transaction — omit BEGIN/COMMIT.
- `ALTER TABLE ... DROP COLUMN` on large tables rewrites in Postgres < 11.
- The `down` migration must be tested — production rollbacks fail when down was never exercised.

## Workflow
Draft a migration file following the project's conventions, safe to apply and revert.

Constraints:
- Both `-- up` and `-- down` sections
- DDL in a transaction except where Postgres requires otherwise (see Gotchas)
- Use the project's existing naming — list `migrations/` first to detect
- Destructive changes (DROP COLUMN, DROP TABLE): confirm with user before drafting
```

## Anti-patterns

See `anti-patterns.md` for the full catalog. The skill-specific ones to double-check:

- Generic descriptions ("Helps with documents") — won't trigger; name user phrasings (Tip 6)
- Long unbroken `SKILL.md` — break at ~500 lines (Tip 3)
- Duplicating other skills — invoke by name; don't reinvent
- `disable-model-invocation: false` for task content with side effects — Claude may auto-run because the code "looks ready"
