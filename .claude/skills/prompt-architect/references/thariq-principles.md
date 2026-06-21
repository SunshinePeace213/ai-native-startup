# Thariq's 9 Tips for Effective Skills

Distilled from Thariq Shihipar's (@trq212) March 2026 post *"Lessons from Building Claude Code: How We Use Skills"* — drawn from running hundreds of skills internally at Anthropic. This is the canonical source for these principles; `anti-patterns.md` and `skill-template.md` reference back here rather than duplicating.

The summary up front: a skill is a **folder**, not a markdown file. The flexibility comes from scripts, references, assets, hooks, and dynamic context — not from the prose. Most tips push toward leveraging that.

## Tip 1: Don't State the Obvious

Claude already knows a lot. If a section of `SKILL.md` could be deleted with no change in Claude's outputs, delete it. Every kept line is a recurring token cost on every session that loads the skill.

**The high-signal content is what pushes Claude out of its defaults.** The canonical example is `frontend-design` — it exists to steer Claude *away* from Inter font, white backgrounds, and purple gradients, defaults Claude reaches for unprompted. It earns its place because Claude wouldn't get there otherwise.

**Anti-pattern signals:** "Use clear variable names", "Write good tests", "Handle edge cases", "Be careful with destructive operations." All things Claude already does. Cut them.

**The test:** read each paragraph and ask "if I deleted this, would the output meaningfully change?" If no, delete.

## Tip 2: Build a Gotchas Section

The single highest-signal section in any mature skill is the Gotchas list — specific things that bit someone in the past and that aren't in any official documentation. Thariq's framing: *"a senior engineer whispering, 'hey, just so you know — this will bite you.'"*

**Format:** flat bullets, each one or two sentences, no preamble. Example:

```markdown
## Gotchas

- Always check `.env.local` before running `npm run build` — the build silently picks up old values from `.env` if `.env.local` was deleted.
- This API rate-limits at 60 req/min — add a `sleep 1` between calls in batch jobs or the second-to-last request silently 429s.
- Run migrations in a transaction even if the docs say it's optional; the rollback path assumes one.
```

**What belongs:** silent failures, order-of-operations requirements not enforced by tooling, environment variables that must be set/unset, rate limits, naming conventions downstream tools depend on, "if you skip step X, step Y looks like it works but doesn't."

**Where to put it:** near the top of `SKILL.md`, after the overview but before the deep references. Skills with a Gotchas section measurably outperform those without, and the section compounds — every time something breaks, add a gotcha and the skill gets permanently better.

**When to skip:** brand-new skills with no production history. Add it the first time something bites — that's the first real gotcha.

## Tip 3: Use the File System & Progressive Disclosure

A skill is a folder. Treat the whole filesystem as context engineering. The loading model:

1. **Frontmatter description** — always in context. ~100 words. Determines whether the skill triggers at all.
2. **SKILL.md body** — loaded when the skill triggers. Aim for under 500 lines.
3. **`references/*.md`** — read on demand when the workflow points at them.
4. **`scripts/`** — executed but not loaded into context.
5. **`assets/`** — used as inputs/outputs, not context.

**Patterns:**
- Split detailed reference material out: API signatures, edge-case catalogs, framework-specific guidance → `references/<topic>.md`
- Use subfolders by domain: `references/aws/`, `references/gcp/`, `references/azure/` if the skill covers variants
- Tell Claude explicitly where to look — explicit pointers beat implicit discovery

**When NOT to split:** content short enough to live inline, content needed every time the skill runs, splitting creates more confusion than clarity.

## Tip 4: Avoid Railroading Claude

Skills are reusable across many user requests and contexts. A rigid step-by-step procedure handles the cases the author imagined and breaks for everything else. **Give Claude the goal and constraints, not the script.**

Railroaded (avoid):
```markdown
1. Run `git status`
2. Run `git diff --staged`
3. Open the editor
4. Type the message with format `type(scope): description`
5. Run `git push origin HEAD`
```

Goal + constraints (prefer):
```markdown
Compose a commit message and create the commit. Push only if the user asked for it.

Constraints:
- Subject under 72 chars, Conventional Commits format
- Body explains *why*; the diff already shows *what*
- Don't push to a branch the user hasn't explicitly named
```

**Exception:** workflows where order is genuinely load-bearing — regulatory compliance, irreversible production operations, legally mandated procedures. Recognize the difference. Default to goal + constraints.

## Tip 5: Think Through the Setup

Skills that need per-installation context (a Grafana URL, a billing account ID, a Slack channel) should not hardcode those values. The `config.json` pattern:

```json
{ "grafana_url": "...", "alert_channel": "#oncall" }
```

In `SKILL.md`:
```markdown
## Setup
Read `${CLAUDE_SKILL_DIR}/config.json`.
If it doesn't exist, ask the user for the values (use AskUserQuestion for
multiple-choice fields), write the file, then proceed.
If it exists, use the values directly.
```

This pattern is especially useful for Data Fetching, Business Process, and Runbook skills. Skip it when the skill is purely transformation or the info lives in the codebase already.

## Tip 6: The Description Field Is For the Model

When Claude Code starts a session, it builds a listing of every available skill with its description. Claude scans that listing to decide *"is there a skill for this request?"* The description is **not a summary for humans** — it's a trigger document for Claude.

Bad (summary):
```yaml
description: A helpful skill for working with PostgreSQL migrations.
```

Good (trigger document):
```yaml
description: |
  Draft safe, reversible PostgreSQL migration files following the project's conventions.
  Use when the user asks to add/drop a column, change a constraint, backfill data, add
  an index, or anything involving "migration", "schema change", or "alter table".
```

Be slightly emphatic — Claude tends to under-trigger skills. Name the user's vocabulary alongside technical terms. Stay under the 1,536-char combined `description` + `when_to_use` limit.

For systematic refinement, see `description-optimization.md`.

## Tip 7: Memory & Storing Data

Skills can carry state across sessions — append-only logs, JSON caches, SQLite databases. This is what lets a Business Process or Runbook skill get better over time.

**Use `${CLAUDE_PLUGIN_DATA}` for persistence across upgrades.** Data written inside the skill directory itself may be wiped on upgrade; `${CLAUDE_PLUGIN_DATA}` is the stable per-plugin folder.

Example:
```markdown
After each run, append a log entry to `${CLAUDE_PLUGIN_DATA}/runs.jsonl` with
the date, request, and one-line summary. At the start of each run, read the
last 5 entries for consistency with prior runs.
```

Skip memory for skills that are stateless by nature.

## Tip 8: Store Scripts and Generate Code

The most powerful thing a skill can give Claude is **code that already works**, so Claude spends turns on composition rather than reconstructing boilerplate.

**Bundle a script when:** the same helper would be written from scratch in 80% of invocations, the operation is deterministic, the operation benefits from being atomic (transactions, multi-step API calls with cleanup).

**Pattern:**
```
my-skill/scripts/
  ├── _lib.py       ← shared helpers Claude imports
  ├── validate.py   ← runs via PostToolUse hook
  └── analyze.py    ← composable; Claude can run with different args
```

Reference scripts with `${CLAUDE_SKILL_DIR}` so paths resolve correctly regardless of install location:
```markdown
Run: `python3 ${CLAUDE_SKILL_DIR}/scripts/analyze.py --mode latency`
```

## Tip 9: On-Demand Hooks

Hooks in skill frontmatter only fire **while the skill is active** — which makes opinionated hooks viable. They don't pollute the user's overall workflow but enforce rules during this skill's invocation.

**Canonical examples:**
- `/careful` — blocks `rm -rf`, `DROP TABLE`, `git push --force`, `kubectl delete` via `PreToolUse` matcher on Bash. Outside `/careful`, these work (because sometimes you need them).
- `/freeze` — blocks any Edit/Write outside a specific directory.

**Use when:** the enforcement is too opinionated to run globally, the skill represents a "mode" the user opts into, or the hook protects against a failure mode specific to this skill's domain.

See `hooks.md` for the full frontmatter spec.

## Distribution (bonus)

Two patterns:
- **Check into the repo at `.claude/skills/`** — best for small teams, single repo
- **Build as a plugin** with a Claude Code Plugin marketplace — best at scale; users install only what they need

Every checked-in skill adds to the description listing every session sees. At scale this crowds Claude's selection. Plugins solve this.

## Measurement (bonus)

To find skills that are popular or under-triggering, add a `PreToolUse` hook (defined globally or in a plugin) that logs skill invocations to a central location. Gives you a data-driven view of which skills earn their place.

## Cross-references

- `skill-categories.md` — the 9-category framework for classifying what kind of skill this is
- `schemas.md` — JSON shapes used by the bundled scripts
- `../../../workflows/artifact-eval.js` — Phase 5 eval loop (artifact vs baseline, grades each run)
- `../../../workflows/description-optimize.js` — Phase 6 trigger optimization (skill/command only)
- `../scripts/aggregate_benchmark.py` — turns iteration outputs into benchmark stats
- `../agents/meta-skill-grader.md` — bundled eval agent that grades assertions against artifact outputs
