# Frontmatter Reference — Skills & Slash Commands

Flat commands (`.claude/commands/<name>.md`) and skills
(`.claude/skills/<name>/SKILL.md`) accept the same frontmatter surface: YAML
between `---` markers at the top of the file. Every field is optional;
`description` is the one that decides triggering.

## Character caps

- `description` ≤ **1,024** chars, plain text, **no angle brackets** (`<` `>`)
  anywhere — the validator rejects them. Use prose and ellipses, never
  bracketed placeholders.
- `description` + `when_to_use` ≤ **1,536** chars combined — the listing
  truncates there, so front-load the primary use case.
- A longer description does not trigger better. Past a tight trigger set it
  only burns the shared listing budget and can evict other skills from
  discovery. Run `/doctor` to see what's being truncated.

## Field-by-field

| Field | Type / values | Controls | Set it when |
|---|---|---|---|
| `name` | lowercase-hyphen string, ≤ 64 chars | Display label. The `/command` name comes from the directory (skills) or filename (flat commands), not from this field. | Skills: set it to match the directory (packaging requires it). Flat commands: omit. |
| `description` | plain text, third person | Whether Claude auto-loads it, and discovery in the `/` menu. If omitted, only manual `/name` invocation works. | Always, unless the artifact is purely manual. See "Writing the description" below. |
| `when_to_use` | plain text | Extra routing context appended to `description` in the listing. | Only for a non-redundant gate or sibling-routing boundary ("Not for X — use /other"). Omit if it would echo `description`. |
| `argument-hint` | string, e.g. `[path-to-plan]` | Autocomplete hint for expected args. Cosmetic. | The command takes arguments; mirror the positional order. |
| `arguments` | space-separated string or YAML list of names | Declares named args; `$name` expands positionally. | Multi-arg commands where `$issue`, `$branch` read better than `$1`, `$2`. |
| `allowed-tools` | string or YAML list; supports scoping like `Bash(git add *)` | Tools usable **without a permission prompt** while active. Does not restrict the pool. | The body repeatedly needs specific tools (e.g. `Bash(git *)` for `/commit`), or an injection block needs its tool pre-approved. |
| `disallowed-tools` | same syntax | **Removes** tools from the pool while active; clears on the next user message. | The artifact must never call a tool (e.g. `Task, EnterPlanMode` on an autonomous planner). |
| `disable-model-invocation` | boolean, default `false` | `true` → only the user can invoke it; Claude can't auto-run it and its description leaves the listing. | Side-effecting artifacts (`/commit`, `/deploy`, `/send-*`) — the user controls the timing. |
| `user-invocable` | boolean, default `true` | `false` → hidden from the `/` menu; only Claude invokes it. | Background knowledge that isn't a meaningful user action. |
| `model` | alias (`opus`, `sonnet`, `haiku`, `fable`) or `inherit` | Model while the artifact runs; reverts on the next user prompt. Aliases only, per AGENTS.md. | The work needs a specific tier; otherwise inherit the session. |
| `effort` | `low` \| `medium` \| `high` \| `xhigh` \| `max` | Reasoning depth + tool-use propensity while active; overrides session effort. | Optional — leave it unset unless the user asks for it or quality demonstrably needs a specific level. |
| `context` | `fork` | Runs the body in an isolated subagent context with no conversation history. | Self-contained heavy work (research, large sweeps). Pointless for guideline-only bodies. |
| `agent` | `Explore`, `Plan`, `general-purpose`, or a custom agent name | Which subagent config executes a forked run. | Only with `context: fork` — e.g. `agent: Explore` for read-only research. |
| `shell` | `bash` (default) \| `powershell` | Shell for `` !`cmd` `` injection blocks. | Windows/PowerShell injection needs. |
| `hooks` | YAML hook config (event → matcher → hooks) | Lifecycle hooks scoped to this artifact only, active while it runs. | Correctness needs determinism the model shouldn't be trusted for: lint after edits, gate a Bash call, verify completion. |
| `paths` | string or YAML list of globs | Limits auto-activation to when in-play files match. | Domain-scoped artifacts (`migrations/**`) that shouldn't trigger elsewhere. Doesn't affect manual `/name`. |
| `license`, `metadata`, `compatibility` | strings / mapping | Packaging metadata for distributed skills. | Only when packaging with `package_skill`. |

Fields that belong to **subagents**, not commands/skills: `tools`,
`permissionMode`, `memory`, `maxTurns`, `isolation`, `background`, `color`,
`skills`, `mcpServers`. Reaching for those means the artifact is probably a
subagent — use meta-agent.

**Packaging surface**: `quick_validate` / `package_skill` accept only `name`,
`description`, `license`, `allowed-tools`, `metadata`, `compatibility`. The
other fields are Claude Code-only — fine in-repo, stripped before
distribution.

## Command-name resolution

What you type after `/` comes from location:

| Layout | `/name` comes from |
|---|---|
| `.claude/skills/<dir>/SKILL.md` | the directory name |
| `.claude/commands/<file>.md` | the filename without extension |
| plugin `skills/<dir>/SKILL.md` | dir name, namespaced `plugin:name` |
| plugin-root `SKILL.md` | frontmatter `name` (the one exception) |

A same-name skill silently beats a flat command — never keep both.

## Substitutions

Expanded in the body before Claude sees it:

| Token | Expands to |
|---|---|
| `$ARGUMENTS` | all args as typed, one string |
| `$ARGUMENTS[N]` | one arg by 0-based index |
| `$1`, `$2` … | positional args — house convention: `$1` is the first argument, matching the team's existing commands |
| `$name` | a named arg declared in `arguments:` |
| `${CLAUDE_SKILL_DIR}` | the directory holding this file — use for every bundled script/asset reference |
| `${CLAUDE_SESSION_ID}` | current session id |
| `${CLAUDE_EFFORT}` | active effort level |

Escape a literal `$` before a digit or arg name with a backslash: `\$1.00`.

## Writing the description

Claude scans every artifact's `name` + `description` to answer "is there a
skill for this request?" — it's a trigger document for the model, not a
human summary.

- **Third person, front-loaded**: lead with the action and the primary use
  case ("Drafts…", "Commits…", "Creates…").
- **Name the user's actual vocabulary**, including phrasings that never name
  the skill or file type.
- **Be slightly pushy** — Claude undertriggers skills. "Use whenever the user
  mentions migrations, schema changes, or 'alter table', even without asking
  for a migration by name."
- **Add a boundary** that routes adjacent work to a sibling ("Not for X — use
  /other"), in `when_to_use` if `description` is at budget.
- For side-effecting artifacts, don't try to phrase the description so Claude
  "won't" run it — set `disable-model-invocation: true`.

```yaml
description: Drafts safe, reversible PostgreSQL migration files following the
  project's conventions. Use when the user asks to add or drop a column,
  change a constraint, backfill data, add an index, or mentions "migration",
  "schema change", or "alter table" — even without naming a migration.
```
