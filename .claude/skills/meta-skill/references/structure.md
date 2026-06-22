# Skill Structure & Progressive Disclosure

A skill is a **folder**, not a file. The flexibility comes from bundled scripts, references, and assets — not from longer prose in `SKILL.md`.

## Directory layout

```
my-skill/
├── SKILL.md          # required — overview + navigation + the trigger description
├── config.json       # optional — per-installation settings (read at runtime)
├── references/
│   ├── topic-a.md    # loaded on demand when the body points at it
│   └── topic-b.md
├── scripts/
│   └── helper.py     # executed via bash; contents never enter context
└── assets/
    └── template.html # used as output material, not read into context
```

`SKILL.md` is the entrypoint. Everything else is optional and exists to keep the entrypoint lean.

## Three progressive-disclosure levels

| Level | What | When it loads | Cost |
|---|---|---|---|
| 1 — Metadata | `name` + `description` (+ `when_to_use`) | Always, at startup, in the system prompt | ~100 tokens/skill; this is why many installed skills are cheap |
| 2 — Body | The `SKILL.md` markdown | When the skill triggers (Claude reads it via bash) | Whole body enters context |
| 3+ — Bundled files | `references/*.md`, `scripts/`, `assets/` | On demand — references when the body points at them; scripts execute without loading | Effectively unbounded: unused files cost zero tokens |

The whole point: Level 1 advertises, Level 2 instructs, Level 3 holds the heavy material that only sometimes matters. Bundle comprehensive API docs, large datasets, dozens of examples — they cost nothing until read.

**Lifecycle gotcha:** once a skill loads, its rendered body **stays in context for the rest of the session** — Claude does not re-read the file on later turns. Write standing instructions, not one-time steps. Every body line is therefore a *recurring* cost. (After auto-compaction, Claude re-attaches the most recent invocation of each skill, keeping the first 5,000 tokens, within a combined 25,000-token budget — large or late-invoked skills can be dropped; re-invoke to restore.)

## The 500-line rule

**Keep the `SKILL.md` body under 500 lines** (target 200–300). State what to do, not how or why Claude already knows it. When you approach the limit, split into `references/` rather than letting the body grow — the body is the recurring cost; references are not.

## When and how to split

Split a chunk into `references/<topic>.md` when **any** holds:
- It's substantial (more than a paragraph or two) and only needed sometimes.
- It's stable reference material (API signatures, edge-case catalogs, framework specifics) better as a doc than inline.
- Two paths are mutually exclusive — separate files keep the unused one out of context.

Keep it inline when it's short, needed every run, or splitting adds more confusion than clarity.

**Rules for splitting:**
- **One level deep.** Every reference links directly from `SKILL.md`. Avoid `SKILL.md → a.md → b.md`: Claude may preview nested files with `head -100` and read them incompletely. Flat references get read in full.
- **Tell Claude where to look.** Explicit pointers ("For form filling, see `references/forms.md`") beat implicit discovery.
- **ToC for long files.** Reference files over ~300 lines get a short table of contents at the top, so a partial read still reveals the full scope. (Best-practices says >100 lines; ~300 is the editorial bar for this skill.)

## Domain-organized references

When a skill spans variants/frameworks, organize references by domain so Claude reads only the relevant one:

```
cloud-deploy/
├── SKILL.md              # workflow + which-variant selection
└── references/
    ├── aws.md
    ├── gcp.md
    └── azure.md
```

The body routes ("Deploying to AWS? See `references/aws.md`"). Claude loads one file, not three. Same pattern for multi-dataset skills (`references/finance.md`, `references/sales.md`) — a `grep` over the right file beats loading everything.

## Bundled scripts & assets: `${CLAUDE_SKILL_DIR}`

Reference bundled files with `${CLAUDE_SKILL_DIR}` (the directory holding this `SKILL.md`) so paths resolve regardless of install location or cwd:

```markdown
Run: `python3 ${CLAUDE_SKILL_DIR}/scripts/visualize.py .`
```

Make execution intent explicit:
- **Execute** (most common): "Run `analyze.py` to extract fields." Script code never enters context — only its output costs tokens.
- **Read as reference**: "See `analyze.py` for the extraction algorithm." Only when Claude needs the logic, not the result.

## MCP tool naming: `Server:tool`

When the skill references MCP tools, use the **fully qualified** name `ServerName:tool_name` (e.g. `BigQuery:bigquery_schema`, `GitHub:create_issue`). Without the server prefix Claude may fail to locate the tool when multiple MCP servers are connected.

## File-path hygiene

Always forward slashes, even on Windows: `scripts/helper.py`, not `scripts\helper.py`. Backslashes break on Unix. Name files for their content (`form_validation_rules.md`, not `doc2.md`) so Claude can navigate by name.

## Reference Docs
- https://code.claude.com/docs/en/skills#add-supporting-files
- https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices#progressive-disclosure-patterns
- https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview#how-skills-work
