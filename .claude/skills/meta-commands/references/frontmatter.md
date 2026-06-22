# Slash Command Frontmatter Reference

A slash command is a Markdown file with optional YAML frontmatter between `---`
markers, then a body that becomes the prompt Claude runs when you invoke it. It
lives either as a flat file (`.claude/commands/<name>.md`) or as a skill
directory (`.claude/skills/<name>/SKILL.md`). All frontmatter fields are
optional; only `description` matters for discovery and model-invocation.

## Read first — commands are now skills

**Custom commands have been merged into skills.** A file at
`.claude/commands/deploy.md` and a skill at `.claude/skills/deploy/SKILL.md` both
produce `/deploy` and run identically. Three load-bearing consequences:

1. **A same-name skill beats a flat command.** If both exist, the skill wins
   silently. Never ship both — point the old one at the new path or delete it.
2. **Flat `.md` is fully supported and is the simpler default.** Reach for the
   skill directory only when you need supporting files, bundled scripts, or model
   auto-trigger (see `command-format.md`).
3. **The flat file and the skill `SKILL.md` accept the same frontmatter surface**
   (the table below). The skill directory adds the ability to bundle
   `references/`/`scripts/` and to be discovered/auto-loaded by Claude.

## Char caps and the angle-bracket ban

- `description` ≤ **1,024** characters.
- `description` + `when_to_use` ≤ **1,536** characters combined (this is the hard
  cap at which the skill listing is truncated; put the key use case first).
- **No angle brackets (`<` / `>`) anywhere in `description`.** The validator
  rejects them. Use plain text and ellipses, never `<placeholder>` syntax. (This
  applies to `description`; the body may use angle brackets, but the modernized
  house template prefers prose micro-prompts over `<bracket>` fill-ins — see
  `command-format.md`.)

## Field-by-field

| Field | Req? | Type / constraints | Controls | Set it when |
|---|---|---|---|---|
| `name` | No | Display label. Defaults to the directory name (skill dir) or filename (flat command). | The **display label** in skill listings. Does **not** change what you type after `/` — except for a plugin-root `SKILL.md`, where it is the only source of the command name. | Almost never for project commands; the dir/file name already sets the command. Set it only to override the listing label, or as the required name for a plugin-root skill. |
| `description` | Recommended | Plain text, third person. **≤ 1,024 chars, no `<`/`>`.** | When Claude **auto-loads** the command and how it's discovered. The trigger document. If omitted, the first paragraph of the body is used. | Always (unless the command is purely manual and you set `disable-model-invocation`). Name the real phrasings. See "Writing the description" below. |
| `when_to_use` | No | Plain text. Counts toward the **1,536** combined cap. | Extra trigger context appended to `description` in the listing — example requests, edge phrasings. | You need more trigger surface than fits cleanly in `description`, or a `Not for: …` boundary that routes adjacent work to a sibling. |
| `argument-hint` | No | String shown in autocomplete, e.g. `[path-to-plan]` or `[user prompt] [orchestration prompt]`. | The hint the `/` menu shows for expected args. Cosmetic; does not parse args. | The command takes arguments. Mirror the positional order of your `$1`/`$2` usage. |
| `arguments` | No | Space-separated string or YAML list of names. Names map to positions **in order**. | Enables named `$name` substitution in the body. | You want readable named placeholders (`$issue`, `$branch`) instead of positional `$1`/`$2`. |
| `allowed-tools` | No | Space- or comma-separated string, or YAML list. MCP patterns + `Bash(...)` patterns allowed. | Tools Claude may use **without a permission prompt** while this command is active. Does NOT restrict the pool — every tool stays callable; this just pre-approves. | The command runs specific tools you don't want to be prompted for (e.g. `Bash(git add *)` for `/commit`, `WebFetch` for a research command, `Bash(gh *)` for a `!`gh ...`` injection). |
| `disallowed-tools` | No | Same syntax as `allowed-tools`. | **Removes** tools from Claude's pool while the command is active. Clears on your next message. | An autonomous command must never call a tool — e.g. `disallowed-tools: Task, EnterPlanMode` on `plan-w-team` to stop it spawning Task agents or entering plan mode. |
| `disable-model-invocation` | No (default `false`) | Boolean. | `true` = only you can invoke it (`/name`); Claude won't auto-run it, and its `description` leaves Claude's context. | The command has side effects or you control timing — `/commit`, `/deploy`, `/send-slack-message`. Don't let Claude deploy because code "looks ready." |
| `user-invocable` | No (default `true`) | Boolean. | `false` = hidden from the `/` menu; only Claude can invoke it. | Background knowledge that isn't a meaningful user action. Rare for commands (they're user-driven by definition); this is mostly a skill concern. |
| `model` | No (default `inherit`) | Same values as `/model`, **or `inherit`**. **Use an alias** (`opus`/`sonnet`/`haiku`), never a dated id. | The model for the rest of the current turn while the command runs; reverts on your next prompt. | The command's work needs a specific tier (`opus` for a heavy planner like `plan-w-team`; `haiku` for a cheap scoped command). Leave `inherit` to track the session. |
| `effort` | No (inherits session) | One of `low`, `medium`, `high`, `xhigh`, `max` (available levels depend on the model). | Reasoning depth + tool-use propensity while the command runs; overrides session effort. | Quality genuinely depends on depth — `high`/`xhigh` for hard agentic work. **This is the dominant capability lever on 4.8**; raise it before padding the body with prose. |
| `context` | No | `fork`. | Runs the command in a **forked subagent context** — no access to conversation history; the body becomes the subagent's prompt. | The command is a self-contained task you want isolated from the main thread (research, a scoped transform). Only makes sense when the body has explicit instructions, not just guidelines. |
| `agent` | No (default `general-purpose`) | A subagent type: `Explore`, `Plan`, `general-purpose`, or a custom agent from `.claude/agents/`. | Which subagent config (model, tools, permissions) runs the forked command. Only meaningful with `context: fork`. | You set `context: fork` and want a specific execution environment — e.g. `agent: Explore` for read-only research. |
| `shell` | No (default `bash`) | `bash` or `powershell`. | The shell for `` !`cmd` `` / ```` ```! ```` injection blocks. `powershell` requires `CLAUDE_CODE_USE_POWERSHELL_TOOL=1`. | The command's injection commands must run under PowerShell on Windows. |
| `hooks` | No | YAML hook config (event → matcher → hooks). | Lifecycle hooks scoped to this command/skill only. | You need determinism the model shouldn't be trusted to enforce — gate a Bash call, lint after edits, verify completion. |
| `paths` | No | Comma-separated string or YAML list of glob patterns. | Limits **auto-activation** to when Claude is working with files matching the globs. | A command should auto-load only in a relevant context — e.g. a migration command that only matters under `db/**`. Does not affect manual `/name` invocation. |

Fields NOT valid here (they belong to **subagents**, not commands): `tools`
(commands use `allowed-tools`/`disallowed-tools`), `permissionMode`, `memory`,
`maxTurns`, `isolation`, `background`, `color`, `skills`, `mcpServers`. If you
reach for those, you may actually want a subagent — re-check the decision gate
and route to **meta-agent**.

> **SKILL.md's own frontmatter is stricter.** The `meta-commands` SKILL.md is
> validated by a separate `quick_validate` that accepts ONLY `name`,
> `description`, `when_to_use`. The fuller field set above is for the **command
> files you author**, not for this skill's own SKILL.md.

## Command-name resolution

What you type after `/` comes from **location**, not the `name` field (with one
exception):

| Layout | Command name comes from | Example |
|---|---|---|
| Skill directory (`.claude/skills/<dir>/SKILL.md`) | The **directory** name | `.claude/skills/deploy-staging/SKILL.md` → `/deploy-staging` |
| Flat command file (`.claude/commands/<file>.md`) | The **filename** without extension | `.claude/commands/build.md` → `/build` |
| Nested skill that clashes with another | Subdir path + dir name | `apps/web/.claude/skills/deploy/SKILL.md` → `/apps/web:deploy` |
| Plugin `skills/<dir>/` subdirectory | Dir name, namespaced by plugin | `my-plugin/skills/review/SKILL.md` → `/my-plugin:review` |
| Plugin-root `SKILL.md` | Frontmatter **`name`** (dir name as fallback) | `my-plugin/SKILL.md` with `name: review` → `/my-plugin:review` |

- **Frontmatter `name` is a display label**, not the command name — except the
  plugin-root case, where there's no directory to take it from.
- **Same-name skill beats a flat command.** A `.claude/skills/deploy/` and a
  `.claude/commands/deploy.md` both define `/deploy`; the skill wins.
- Enterprise > personal > project for same-named skills across levels.

## Substitutions

Available inside the command body. The command body is rendered with these
expanded before Claude sees it.

| Token | Expands to | Notes |
|---|---|---|
| `$ARGUMENTS` | All args as typed, one string. | If the body has no `$ARGUMENTS` and no positional refs, args are appended as `ARGUMENTS: <value>`. |
| `$ARGUMENTS[N]` | One arg by **0-based** index. | `$ARGUMENTS[0]` = first arg. Shell-style quoting: `/x "a b" c` → `[0]`=`a b`, `[1]`=`c`. |
| `$N` | Shorthand for `$ARGUMENTS[N]` — **0-based** per the docs (`$0` = first, `$1` = second). | **Discrepancy:** the team house template and `plan-w-team.md` use `$1`/`$2` as **first/second** (older 1-based convention). When authoring, follow the team's `$1`=first usage to match existing commands, but know the documented shorthand is 0-based. When in doubt, use `$ARGUMENTS[N]` for unambiguous indexing or named `$name` args. |
| `$name` | A named arg declared in `arguments:`. | With `arguments: [issue, branch]`, `$issue` = first arg, `$branch` = second. Most readable for multi-arg commands. |
| `${CLAUDE_SESSION_ID}` | Current session ID. | For logging, session-scoped files, correlating output. |
| `${CLAUDE_EFFORT}` | Current effort level (`low`…`max`; ultracode reports `xhigh`). | Adapt body instructions to the active effort. |
| `${CLAUDE_SKILL_DIR}` | The directory holding this command's file. | Use in `` !`cmd` `` injections and script refs so bundled paths resolve regardless of cwd. Forward slashes only. |

Escape a literal `$` before a digit/`ARGUMENTS`/arg-name with a single backslash:
`\$1.00` stays literal.

## Writing the `description` (the field that decides discovery)

Claude reads each command's `name` + `description` to decide when to auto-load
it. It's a trigger document, not a human summary.

- **Third person, front-loaded.** "Creates…", "Implements…", "Commits…" — lead
  with the action and the trigger phrasings.
- **Name the real phrasings** a user would type, including when they don't say
  the command name.
- **Add a `Not for: …` boundary** in `when_to_use` when a sibling should handle
  adjacent work.
- **Keep it tight.** A longer description doesn't trigger better; past a tight
  trigger set it only burns the shared listing budget and can evict other
  commands from discovery. Run `/doctor` to see what's being truncated.
- **Set `disable-model-invocation: true`** for side-effecting commands instead of
  trying to phrase the description so Claude "won't" run it.

## Reference Docs
- https://code.claude.com/docs/en/slash-commands
- https://github.com/shanraisshan/claude-code-best-practice/blob/main/best-practice/claude-commands.md
- https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices
