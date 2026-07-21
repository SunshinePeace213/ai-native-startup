---
source: https://code.claude.com/docs/en/skills
fetched: 2026-07-21
---
> **In here:** Skill creation and structure · Bundled skills and invocation · Configuration and troubleshooting

# Extend Claude with skills

> Create, manage, and share skills to extend Claude's capabilities in Claude Code. Includes custom commands and bundled skills.

Skills extend what Claude can do. Create a `SKILL.md` file with instructions, and Claude adds it to its toolkit. Claude uses skills when relevant, or you can invoke one directly with `/skill-name`.

Create a skill when you keep pasting the same instructions, checklist, or multi-step procedure into chat, or when a section of CLAUDE.md has grown into a procedure rather than a fact. Unlike CLAUDE.md content, a skill's body loads only when it's used, so long reference material costs almost nothing until you need it.

<Note>
  For built-in commands like `/help` and `/compact`, and bundled skills like `/debug` and `/code-review`, see the [commands reference](/docs/en/commands).

  **Custom commands have been merged into skills.** A file at `.claude/commands/deploy.md` and a skill at `.claude/skills/deploy/SKILL.md` both create `/deploy` and work the same way. Your existing `.claude/commands/` files keep working. Skills add optional features: a directory for supporting files, frontmatter to [control whether you or Claude invokes them](#control-who-invokes-a-skill), and the ability for Claude to load them automatically when relevant.
</Note>

Claude Code skills follow the [Agent Skills](https://agentskills.io) open standard, which works across multiple AI tools. Claude Code extends the standard with additional features like [invocation control](#control-who-invokes-a-skill), [subagent execution](#run-skills-in-a-subagent), and [dynamic context injection](#inject-dynamic-context).

## Bundled skills

Claude Code includes a set of bundled skills that are available in every session unless disabled with the [`disableBundledSkills`](/docs/en/settings#available-settings) setting, including `/doctor`, `/code-review`, `/batch`, `/debug`, `/loop`, and `/claude-api`. Unlike most built-in commands, which execute fixed logic directly, bundled skills are prompt-based: they give Claude detailed instructions and let it orchestrate the work using its tools. You invoke them the same way as any other skill, by typing `/` followed by the skill name.

The [`/doctor`](/docs/en/commands#all-commands) setup checkup is the one exception to `disableBundledSkills` in Claude Code v2.1.205 and later: it stays typable when the setting is on. To hide it, set the `DISABLE_DOCTOR_COMMAND` environment variable or a [`skillOverrides`](#override-skill-visibility-from-settings) entry of `"doctor": "off"`. Before v2.1.205, `/doctor` was a built-in command rather than a bundled skill.

Bundled skills are listed alongside built-in commands in the [commands reference](/docs/en/commands), marked **Skill** in the Purpose column.

### Run and verify your app

Three bundled skills work together to launch your app and confirm changes against the running app instead of just tests:

| Skill                  | Purpose                                                                                                           |
| :--------------------- | :---------------------------------------------------------------------------------------------------------------- |
| `/run`                 | Launch and drive your app to see a change working                                                                 |
| `/verify`              | Build and run your app to confirm a code change does what it should, without falling back to tests or type checks |
| `/run-skill-generator` | Teach `/run` and `/verify` how to build and launch your project                                                   |

{/* min-version: 2.1.145 */}All three skills require Claude Code v2.1.145 or later. Check your version with `claude --version` or the `/status` command.

`/run` and `/verify` work without setup. They infer the launch from your project type (CLI, server, TUI, browser-driven) and from what's in your README, `package.json`, or `Makefile`. That inference gets unreliable for projects that need anything beyond a standard launch: a database, an env file, a graphical session, a multi-step build.

`/run-skill-generator` records the recipe instead. It gets your app running from a clean environment, captures what worked (the install commands, the env vars, the launch script), and commits it as a per-project skill at `.claude/skills/run-<name>/`. After that, `/run`, `/verify`, and any other agent in the repo follow the recorded recipe instead of rediscovering it. Run `/run-skill-generator` once per project, and again if the build or launch process changes.

## Getting started

### Create your first skill

This example creates a skill that summarizes the uncommitted changes in your git repository and flags anything risky. It pulls the live diff into the prompt before Claude reads it, so the response is grounded in your actual working tree rather than what Claude can guess from open files. Claude loads the skill automatically when you ask about your changes, or you can invoke it directly with `/summarize-changes`.

<Steps>
  <Step title="Create the skill directory">
    Create a directory for the skill in your personal skills folder. Personal skills are available across all your projects.

    ```bash theme={null}
    mkdir -p ~/.claude/skills/summarize-changes
    ```
  </Step>

  <Step title="Write SKILL.md">
    Every skill needs a `SKILL.md` file with two parts: YAML frontmatter between `---` markers that tells Claude when to use the skill, and markdown content with the instructions Claude follows when the skill runs. The directory name becomes the command you type, and the `description` helps Claude decide when to load the skill automatically.

    Save this to `~/.claude/skills/summarize-changes/SKILL.md`:

    ```yaml theme={null}
    ---
    description: Summarizes uncommitted changes and flags anything risky. Use when the user asks what changed, wants a commit message, or asks to review their diff.
    ---

    ## Current changes

    !`git diff HEAD`

    ## Instructions

    Summarize the changes above in two or three bullet points, then list any risks you notice such as missing error handling, hardcoded values, or tests that need updating. If the diff is empty, say there are no uncommitted changes.
    ```

    The `` !`git diff HEAD` `` line uses [dynamic context injection](#inject-dynamic-context): Claude Code runs the command and replaces the line with its output before Claude sees the skill content, so the instructions arrive with the current diff already inlined.
  </Step>

  <Step title="Test the skill">
    Open a git project, make a small edit to any file, and start Claude Code by running `claude`. You can test the skill two ways.

    **Let Claude invoke it automatically** by asking something that matches the description:

    ```text theme={null}
    What did I change?
    ```

    **Or invoke it directly** with the skill name:

    ```text theme={null}
    /summarize-changes
    ```

    Either way, Claude should respond with a short summary of your edit and a list of risks.
  </Step>
</Steps>

### Where to save skills

- **Personal skills** in `~/.claude/skills/` are available to every project on your machine.
- **Project skills** in `.claude/skills/` are shared with anyone who clones your repository.
- **Team skills** in a `.claude/skills/` folder in a private repository that you grant the team permission to share across projects: see [permissions](/docs/en/permissions#share-your-skills).

All three locations load skills the same way: a directory with a `SKILL.md` file. Subdirectories of `.claude/skills/` in the repo also load; this allows you to organize related skills: `.claude/skills/deploy/SKILL.md` and `.claude/skills/deploy/backup/SKILL.md` both register as skills.

Skills in a `.claude/commands/` directory (the old location before skills were introduced) still work. When both files exist at `.claude/commands/skill.md` and `.claude/skills/skill/SKILL.md`, the skill wins. New skills should go in `.claude/skills/`.

### Skill structure

A skill is a directory containing:

- **`SKILL.md`** — required, contains frontmatter and instructions
- **Supporting files** — optional, referenced in the skill and loaded together with it

The directory name (stripped of suffixes like `-skill` or `-helper` if you add them) becomes the command name. `/my-skill` invokes `~/.claude/skills/my-skill/SKILL.md` or `.claude/skills/my-skill/SKILL.md`.

### Write SKILL.md

The `SKILL.md` file has two parts: YAML frontmatter between `---` markers, and markdown instructions.

```yaml
---
description: A one-line description Claude reads when deciding whether to invoke this skill automatically. Use keywords matching the kinds of requests you want to trigger the skill.
when_to_use: |
  Optional. A detailed explanation of when to use this skill and when not to use it.
  Use to disambiguate between similar skills, or to rule out edge cases.
---

# Skill title

Your instructions here. Can span multiple sections.
```

**`description`** — Claude reads this when deciding whether to run your skill automatically. Write it for Claude, not for humans: include keywords that match the requests you want to trigger the skill. Examples:

- ✅ `Helps debug environment setup, imports, build failures, and test failures by running diagnostics.`
- ❌ `Debugging tool` (too vague)
- ✅ `Writes and updates Dockerfiles and containerization workflows for Node, Python, Ruby, and Go projects.`
- ❌ `Docker helper` (doesn't say what problems it solves)

**`when_to_use`** — optional, a detailed explanation that helps Claude pick between similar skills or rule out edge cases.

The frontmatter keys are case-sensitive. Additional keys specific to skill invocation and behavior are documented below.

### Skill syntax

Inside a skill's instructions, you can use:

- **Markdown** — normal markdown syntax for headings, lists, links, code blocks
- **Dynamic context** — special syntax to inject live command output or file content:
  - `` !`command` `` — runs a shell command and inlines the output
  - `` !`file.md` `` — reads a file's contents and inlines it
- **HTML and JSX** — custom elements like `<Note>`, `<Steps>`, and collapsible sections for structure and navigation

Use these to keep your skill instructions grounded in the live state of the project, and to make long reference material navigable without bloating the skill's loaded size.

### Control who invokes a skill

By default, Claude can invoke your skill automatically when it's relevant, and you can always invoke it manually with the skill name. Two settings let you change this:

- **`disable-model-invocation: true`** — only you can invoke this skill with `/skill-name`; Claude won't run it automatically.
- **`disable-user-invocation: true`** — only Claude can invoke this skill automatically; you can't invoke it with `/skill-name`.

Example:

```yaml
---
description: Runs the project's tests whenever you ask about test results or whether the code works.
disable-user-invocation: true
---
```

Use `disable-model-invocation` for skills that are too specialized or destructive for automatic invocation (e.g., a `/deploy` skill, or a `/quick-test-only` that's meant to skip comprehensive tests). Use `disable-user-invocation` for skills designed for automatic invocation only and not useful when manually triggered.

### Run skills in a subagent

Large or complex skills can run in a subagent: a separate Claude instance that loads the skill, runs it unsupervised, and returns the result. Subagents let you:

- **Dedicate Claude to one task** without interruption
- **Use a specialized model** (`opus` for complex work, `haiku` for lightweight utilities)
- **Isolate long-running work** so it doesn't block the main session
- **Keep skill code separate** from the main chat context

Add these keys to a skill's frontmatter:

```yaml
---
subagent: true
subagent-model: "opus"  # optional: "opus", "sonnet", "haiku"; default "sonnet"
---
```

When you invoke a skill with `subagent: true`, Claude Code spins up a new agent instance, loads the skill, streams the output back, and returns to the main chat. The subagent runs in the same project directory and has access to your project's files and tools.

If the skill uses dynamic context (`` !`command` `` or `` !`file` ``), the injection happens in the subagent's environment, so the skill sees the current state of the project. This makes subagents ideal for skills that explore the codebase or run commands.

### Inject dynamic context

Dynamic context syntax lets you inject live data into a skill without storing that data in the skill file. Before Claude sees the skill, Claude Code runs the commands or reads the files you specify, and inlines the output.

**Read a file:**

```markdown
## Project layout

!`find . -type f -name "*.json" | head -20`
```

**Run a command:**

```markdown
## Recent commits

!`git log --oneline -10`
```

Claude Code runs the command in the same directory as the project and inlines the output. If the command fails or produces no output, Claude Code leaves the line as-is (the `` !`...` `` syntax remains visible to Claude) so you can decide how to handle the error case.

**Full example:**

```yaml
---
description: Summarizes uncommitted changes and suggests a commit message.
---

## Current changes

!`git diff HEAD`

## Instructions

Summarize the diff in 1–2 sentences, then suggest a commit message. If the diff is empty, say there are no uncommitted changes.
```

**Scoping:** Claude Code runs injections in the project's root directory. If you need output from a subdirectory, include the path in the command: `` !`ls subdir/` ``.

**Performance:** Each injection adds a small delay while Claude Code runs the command or reads the file. Keep commands fast and targeted. For expensive operations (full test suites, large file searches), consider running them manually and pasting the output, or loading the skill and asking Claude to run the command itself.

**Error handling:** Commands can fail (non-zero exit status) or produce no output. If a failure matters, include a fallback in the skill instructions:

```markdown
## Current test status

!`npm test 2>&1`

If the tests above didn't run, describe what happened and I'll diagnose the issue.
```

### Load skills from version control

Skills checked into `.claude/skills/` load automatically when you open the project. You can also load skills from a different repository:

```yaml
---
description: Deploys the project using the deployment skill from the platform repo.
load-skills-from: 
  - repo: "https://github.com/myteam/platform"
    path: ".claude/skills"
---
```

This merges the `path` directory from the `repo` into your skill context temporarily. Merging happens at load time, so you see the latest version of the loaded skills. If a skill name conflicts between your project and the loaded repo, your project's version takes priority.

**Permissions:** Loading skills from a remote repository requires permission. The first time you load a skill from a new repo, Claude Code asks for your approval before downloading and running it.

### File requirements

Files are local to each machine; a skill can't reference files outside the project directory. Paths are relative to the project root.

If you need to reference files that won't exist until the skill runs (e.g., files generated by a previous step), use a `if-exists` wrapper or check in the skill instructions. Example:

```yaml
---
description: Updates the changelog after a release.
---

## Recent changes

!`if [ -f "CHANGELOG_SINCE_LAST_RELEASE.md" ]; then cat CHANGELOG_SINCE_LAST_RELEASE.md; fi`

## Instructions

If the file from the recent changes exists, update `CHANGELOG.md` with its contents. Otherwise, generate the changelog from the recent git log.
```

## Advanced

### Share skills with the team

Skills in a `.claude/skills/` directory in a repository also load in Claude Tag channels created from that repository. If you want to make certain skills available to your team without sharing the entire repository:

1. Create a private repository with your shared skills in `.claude/skills/`
2. Grant team members access to the repository
3. Link to it in another skill's `load-skills-from:` field, or have them clone it locally and work from there

When a team member opens a project and a skill loads a skill from your repository, Claude Code prompts them for permission the first time, then remembers their choice.

### Share skills publicly

To publish a skill for public use, host it on GitHub and share the URL. Anyone can load it with:

```yaml
---
description: Your description here.
load-skills-from:
  - repo: "https://github.com/your-org/your-skill-repo"
    path: ".claude/skills"
---
```

### Load skills from a monorepo

In a monorepo, a skill in one subdirectory can load skills from another:

```yaml
---
description: Runs the frontend build using the build skill from the shared tools directory.
load-skills-from:
  - path: "../../tools/.claude/skills"
---
```

Use relative paths to refer to other directories in the same repository. Claude Code resolves the path relative to the skill's directory.

If the monorepo itself has a `.claude/skills/` directory, skills there load automatically for any subdirectory project.

### Load skills conditionally

A skill can declare dependencies that determine whether it's available:

```yaml
---
description: Runs tests using pytest when pytest is installed.
requires: "pytest"
---
```

The `requires` field accepts a space-separated list of command names or environment variable names that must be present:

```yaml
requires: "docker node npm"
requires: "DATABRICKS_HOST DATABRICKS_TOKEN"
```

If a requirement is missing, the skill won't appear in `/list-skills` or load automatically, but you can still invoke it manually with `/skill-name`.

### Register a tool

Skills can register tools that Claude can use to perform actions:

```yaml
---
description: Scans a URL with Lighthouse and returns a performance report.
---

## Tools

- **url** (required): The URL to scan
- **format** (optional): json or html (default json)

## Instructions

I will scan the URL you provide using Lighthouse and return a JSON report of performance metrics. This includes the Lighthouse score, Core Web Vitals, and a breakdown of performance by metric.
```

A tool declared in a skill behaves like a Bash tool — Claude can invoke it with parameters, and the skill content (instructions) receives the parameters and provides the output.

The tool name is the skill name. If your skill is at `.claude/skills/lighthouse/SKILL.md`, the tool is named `/lighthouse`. Claude calls the skill with each parameter, and the skill instructions receive them as variables: `${url}` and `${format}` in the example above.

The tool is available to you and Claude whenever the skill is available. If a skill's frontmatter sets `disable-user-invocation: true`, its tool is also unavailable to you, though Claude can still use it.

### Troubleshooting

#### Skill not loading or appearing in `/list-skills`

Run `/doctor` to diagnose the issue. Common problems:

- **File not found:** Ensure the skill is in `~/.claude/skills/skill-name/SKILL.md` or `.claude/skills/skill-name/SKILL.md`
- **Frontmatter syntax error:** Frontmatter must be valid YAML between `---` markers. Use a YAML validator to check.
- **Directory permissions:** Claude Code must be able to read the skill directory.
- **Pattern mismatch:** The `requires` condition failed (a command or environment variable is missing)

#### Skill always triggers

Make your description more specific to the use cases you want. Examples:

- ❌ `Helps with anything` (too broad)
- ✅ `Diagnoses build failures in Node and Python projects by running dependency checks and build commands`
- ❌ `Lint checker` (doesn't say what it does or lints what)
- ✅ `Checks TypeScript files for type errors and style violations using eslint and TypeScript compiler`

#### Skill triggers too often

If Claude uses your skill when you don't want it:

1. Make the description more specific
2. Add `disable-model-invocation: true` if you only want manual invocation

#### Skill descriptions are cut short

Claude Code loads a listing of skill names and descriptions into context so Claude knows what's available. The listing always contains every skill name, but if you have many skills, Claude Code shortens descriptions to fit the listing's character budget, which can strip the keywords Claude needs to match your request. The budget scales at 1% of the model's context window. When the listing overflows, Claude Code drops descriptions starting with the skills you invoke least, so the skills you use most keep their full text.

Run `/doctor` for an estimate of the listing's context cost and its biggest contributors. When the listing exceeds its budget, Claude Code also writes a warning to the debug log, visible with [`--debug`](/docs/en/cli-reference#cli-flags).

The Skills row in `/context` reports the size of the listing after the budget is applied, so it matches what the model receives. Before v2.1.196, the row counted the full text of every description and could show a value several times larger than the configured budget.

To raise the budget, set the [`skillListingBudgetFraction`](/docs/en/settings#available-settings) setting (e.g. `0.02` = 2%) or the `SLASH_COMMAND_TOOL_CHAR_BUDGET` environment variable to a fixed character count. To free budget for other skills, set low-priority entries to `"name-only"` in [`skillOverrides`](#override-skill-visibility-from-settings) so they list without a description. You can also trim the `description` and `when_to_use` text at the source: put the key use case first, since each entry's combined text is capped at 1,536 characters regardless of budget. The cap is configurable with [`skillListingMaxDescChars`](/docs/en/settings#available-settings).

## Related resources

* **[Debug your configuration](/docs/en/debug-your-config)**: diagnose why a skill isn't appearing or triggering
* **[Evaluating skill output quality](https://agentskills.io/skill-creation/evaluating-skills)**: the eval file format and iteration workflow on agentskills.io
* **[Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)**: writing guidance that applies across Claude products
* **[Subagents](/docs/en/sub-agents)**: delegate tasks to specialized agents
* **[Plugins](/docs/en/plugins)**: package and distribute skills with other extensions
* **[Hooks](/docs/en/hooks)**: automate workflows around tool events
* **[Memory](/docs/en/memory)**: manage CLAUDE.md files for persistent context
* **[Commands](/docs/en/commands)**: reference for built-in commands and bundled skills
* **[Permissions](/docs/en/permissions)**: control tool and skill access
* **[Claude Tag skills](https://claude.com/docs/claude-tag/admins/skills-repo)**: project skills committed to a repo also load when that repo is used in a Claude Tag channel
