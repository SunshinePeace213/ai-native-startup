# SKILL.md Frontmatter Reference

Live docs (authoritative for fields/constraints):
- https://code.claude.com/docs/en/skills#frontmatter-reference
- https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices
- https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview

Every field is optional. Only `description` is recommended — without it Claude can't decide when to load the skill. Frontmatter is YAML between `---` markers at the top of `SKILL.md`.

## The two listing limits (read first)

Every skill's metadata is injected into **every session** so Claude can decide what to load. Two ceilings govern it:

- **Combined `description` + `when_to_use` ≤ 1,536 chars per entry.** The listing concatenates both fields and truncates at 1,536 — trigger phrases past the cap silently vanish. Front-load the primary use case. (Live Claude Code docs; tunable via `maxSkillDescriptionChars`.)
- **`description` ≤ 1,024 chars, plain text, NO XML / angle brackets `< >`.** This is the public Agent Skills spec / validator rule: "Maximum 1024 characters, non-empty, no XML tags." A `<` anywhere in the description fails validation. (best-practices doc.)

A long description does **not** "trigger better." Past a tight trigger set it only burns shared budget; when the global budget (1% of context, `skillListingBudgetFraction`) overflows, the least-used skills' descriptions are dropped first — one bloated skill silently evicts *others* from discovery. Run `/doctor` to see what's being shortened. Editorial target: keep `description` well under the 1,024 wall (a few hundred chars is plenty).

## Field-by-field

| Field | Req | Type / constraints | Controls | Set it when |
|---|---|---|---|---|
| `name` | No | String. **Conflict — see below.** | Display label in listings. Does *not* set the `/command` (that comes from the directory name). | Almost never. Leave it off and let it default to the directory. Only meaningful for a plugin-root `SKILL.md`, where it does set the command name. |
| `description` | **Recommended** | Plain text, ≤ 1,024 chars, no `< >`. Third person. | Whether Claude auto-loads the skill. If omitted, the first paragraph of the body is used. | Always. This is the trigger document — write it for the model (see below). |
| `when_to_use` | No | Plain text. Counts toward the 1,536 combined cap. | Extra routing context appended to `description` in the listing. | Only for a non-redundant gate/precondition or sibling-routing ("not for X → /other"). Omit if it would only echo `description`. |
| `allowed-tools` | No | Space- or comma-separated string, or YAML list. Supports scoping, e.g. `Bash(git add *)`. | Tools Claude may use **without a permission prompt** while the skill is active. Does NOT restrict the pool — every tool stays callable. | The skill repeatedly needs specific tools and you want to skip per-use approval (e.g. `/commit` pre-approving `Bash(git *)`). Project skills apply it only after the workspace-trust dialog. |
| `disallowed-tools` | No | Space- or comma-separated string, or YAML list. | **Removes** tools from the pool while the skill is active. Clears on your next message. | An autonomous/background skill must never call a tool — e.g. denying `AskUserQuestion` in a loop that shouldn't stop for input. |
| `disable-model-invocation` | No (default `false`) | Boolean. | `true` → only the user can `/name`; Claude can't auto-trigger, and the description leaves the listing entirely. Also blocks preloading into subagents. | Task skills with side effects (`/deploy`, `/commit`, `/send-slack-message`) — so Claude doesn't run them because the code "looks ready." |
| `user-invocable` | No (default `true`) | Boolean. | `false` → hidden from the `/` menu; only Claude invokes it. | Background knowledge that isn't a meaningful user action (`legacy-system-context`). Note: this only hides the menu entry; use `disable-model-invocation` to block programmatic access. |
| `model` | No | Same values as `/model`, or `inherit`. | Model used while the skill is active; reverts to the session model on the next prompt (override lasts the current turn). | The skill's work wants a different model than the session (cheap exploration on Haiku, hard reasoning on Opus). |
| `effort` | No (inherits session) | `low` \| `medium` \| `high` \| `xhigh` \| `max` (availability depends on model). | Effort level while the skill is active; overrides session effort. | Quality depends on deep reasoning or more tool use. **The dominant capability lever on Opus 4.8** — raise this instead of adding "think harder" prose. `xhigh` for hard coding/agentic, `high` as a reasoning-sensitive default. |
| `context` | No | `fork`. | `fork` runs the skill in an isolated subagent context (no conversation history). | Heavy work that would flood the main context (research, large sweeps). Only meaningful for skills with an actual task — guideline-only skills forked return nothing useful. |
| `agent` | No (default `general-purpose`) | Subagent type: built-in (`Explore`, `Plan`, `general-purpose`) or any custom agent in `.claude/agents/`. | Which subagent executes when `context: fork` is set. | Pair with `context: fork`. `agent: Explore` for read-only codebase research (skips CLAUDE.md/git status, keeps context small). |
| `hooks` | No | YAML hook config (event → matcher → hooks). | Lifecycle hooks scoped to **this skill only** — they fire just while it's active. | Correctness needs determinism, not model goodwill: lint after edits (`PostToolUse`), block unsafe Bash (`PreToolUse`), verify done (`Stop`). On-demand hooks make opinionated rules viable without polluting the global workflow. |
| `paths` | No | Comma-separated string or YAML list of globs (path-specific-rules format). | Auto-loads the skill **only** when in-play files match the globs. | Skill is domain-scoped to certain files (`migrations/**`, `**/*.tsx`) and shouldn't trigger elsewhere. |
| `arguments` | No | Space-separated string or YAML list of names. | Declares named positional args; `$name` expands to them in order. | The skill takes structured positional input you want to name (`arguments: [issue, branch]` → `$issue`, `$branch`). |
| `argument-hint` | No | String, e.g. `[issue-number]` or `[filename] [format]`. | Autocomplete hint for expected args. Purely cosmetic. | The skill takes arguments and you want the `/` menu to show their shape. |
| `shell` | No (default `bash`) | `bash` \| `powershell`. | Shell used for `` !`cmd` `` dynamic-context injection and ` ```! ` blocks. | Windows skills needing PowerShell (also requires `CLAUDE_CODE_USE_POWERSHELL_TOOL=1`). |

## The `name` conflict — surface, don't average

Two sources disagree. They are not reconcilable, so pick one and know why:

- **Public Agent Skills spec / best-practices doc:** `name` is a real identifier — max 64 chars, lowercase letters/numbers/hyphens only, no XML tags, no reserved words (`anthropic`, `claude`), gerund form preferred (`processing-pdfs`).
- **Current Claude Code behavior (live skills doc):** `name` is a **display label that defaults to the directory name** and does *not* set the `/command`. The directory name is what you type after `/`. The single exception is a plugin-root `SKILL.md`, where `name` *does* set the command because there's no directory to take it from.

**Follow today (Claude Code):** name your **directory** in lowercase-hyphen form — that becomes both the command and the effective name. Omit the `name` field, or set it to match the directory. Don't rely on `name` to control invocation; it won't. If you author for the cross-tool Agent Skills standard (claude.ai / API uploads), keep `name` ≤ 64 chars, lowercase-hyphen, no reserved words, since validators there enforce it. The two collapse to one rule in practice: **use a lowercase-hyphen directory name and you satisfy both.**

## Writing the `description` (the one field that decides triggering)

Claude scans the listing of every skill's name + description to answer "is there a skill for this request?" The description is a **trigger document for the model, not a human summary.**

- **Third person.** It's injected into the system prompt; first/second person ("I can help…", "You can use…") degrades discovery. Use "Drafts…", "Generates…", "Extracts…".
- **Front-loaded.** Primary use case + trigger phrases first — that's the part that survives truncation at 1,536.
- **Name the user's actual vocabulary**, not just technical terms. Include phrasings a user would type even when they don't name the skill or file type.
- **Be slightly pushy.** Claude under-triggers skills on Opus 4.8. A mildly emphatic, trigger-rich description counters it — e.g. add "Use this whenever the user mentions migrations, schema changes, or 'alter table', even if they don't ask for a migration by name." This is steering, not the deprecated all-caps "MUST" pattern.
- **What counts toward the caps:** `description` against 1,024 (and no `< >`); `description` + `when_to_use` against 1,536 combined.

Example:
```yaml
description: >-
  Drafts safe, reversible PostgreSQL migration files following the project's
  conventions. Use when the user asks to add or drop a column, change a
  constraint, backfill data, add an index, or mentions "migration", "schema
  change", or "alter table" — even without naming a migration explicitly.
```

## Referencing bundled files at runtime: `${CLAUDE_SKILL_DIR}`

`${CLAUDE_SKILL_DIR}` expands to the directory containing this `SKILL.md` (for plugin skills, the skill's subdirectory, not the plugin root). Use it so bundled scripts/assets resolve regardless of where the skill is installed (personal / project / plugin) or the current working directory.

```markdown
Run the analyzer: `python3 ${CLAUDE_SKILL_DIR}/scripts/analyze.py --mode latency`
```

Other confirmed substitutions (live docs): `$ARGUMENTS`, `$ARGUMENTS[N]` / `$N`, `$name` (from `arguments`), `${CLAUDE_SESSION_ID}`, `${CLAUDE_EFFORT}` (reports `xhigh` for ultracode). Escape a literal `$` before a digit/`ARGUMENTS`/arg-name with a backslash (`\$1.00`).

## Unverified / needs confirmation

- **`${CLAUDE_PLUGIN_DATA}`** — used in the distilled Thariq material as the stable per-plugin folder for state that survives upgrades. It is **not** listed in any official string-substitution table I could reach (live skills doc lists only `${CLAUDE_SESSION_ID}`, `${CLAUDE_EFFORT}`, `${CLAUDE_SKILL_DIR}`; best-practices and overview docs don't mention it). Treat as plausible but unconfirmed; verify against current docs before relying on it in a shipped skill. Do not present it as official.
- **1,024-char `description` limit in Claude Code specifically** — confirmed in the public Agent Skills best-practices spec, not restated verbatim in the live Claude Code skills page (which states the 1,536 *combined* cap). The 1,024 single-field limit and the no-XML rule are the cross-product validator rules; they hold for skills uploaded to claude.ai / the API. In Claude Code the binding practical limit is the 1,536 combined truncation. Both are documented; they govern different layers.
