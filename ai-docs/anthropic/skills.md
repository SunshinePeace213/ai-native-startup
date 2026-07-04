---
source: https://code.claude.com/docs/en/skills
fetched: 2026-07-05
---
> **In here:** Create and manage skills · Configure invocation and context · Share skills across projects

# Extend Claude with skills

> Create, manage, and share skills to extend Claude's capabilities in Claude Code. Includes custom commands and bundled skills.

Skills extend what Claude can do. Create a `SKILL.md` file with instructions, and Claude adds it to its toolkit. Claude uses skills when relevant, or you can invoke one directly with `/skill-name`.

Create a skill when you keep pasting the same instructions, checklist, or multi-step procedure into chat, or when a section of CLAUDE.md has grown into a procedure rather than a fact. Unlike CLAUDE.md content, a skill's body loads only when it's used, so long reference material costs almost nothing until you need it.

<Note>
  For built-in commands like `/help` and `/compact`, and bundled skills like `/debug` and `/code-review`, see the [commands reference](/en/commands).

  **Custom commands have been merged into skills.** A file at `.claude/commands/deploy.md` and a skill at `.claude/skills/deploy/SKILL.md` both create `/deploy` and work the same way. Your existing `.claude/commands/` files keep working. Skills add optional features: a directory for supporting files, frontmatter to [control whether you or Claude invokes them](#control-who-invokes-a-skill), and the ability for Claude to load them automatically when relevant.
</Note>

Claude Code skills follow the [Agent Skills](https://agentskills.io) open standard, which works across multiple AI tools. Claude Code extends the standard with additional features like [invocation control](#control-who-invokes-a-skill), [subagent execution](#run-skills-in-a-subagent), and [dynamic context injection](#inject-dynamic-context).

## Bundled skills

Claude Code includes a set of bundled skills that are available in every session unless disabled with the [`disableBundledSkills`](/en/settings#available-settings) setting, including `/code-review`, `/batch`, `/debug`, `/loop`, and `/claude-api`. Unlike most built-in commands, which execute fixed logic directly, bundled skills are prompt-based: they give Claude detailed instructions and let it orchestrate the work using its tools. You invoke them the same way as any other skill, by typing `/` followed by the skill name.

Bundled skills are listed alongside built-in commands in the [commands reference](/en/commands), marked **Skill** in the Purpose column.

### Run and verify your app

Three bundled skills work together to launch your app and confirm changes against the running app instead of just tests:

| Skill                  | Purpose                                                                                                           |
| :--------------------- | :---------------------------------------------------------------------------------------------------------------- |
| `/run`                 | Launch and drive your app to see a change working                                                                 |
| `/verify`              | Build and run your app to confirm a code change does what it should, without falling back to tests or type checks |
| `/run-skill-generator` | Teach `/run` and `/verify` how to build and launch your project                                                   |

{/* min-version: 2.1.145 */}All three skills require Claude Code v2.1.145 or later.

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

### Where skills live

Skills can live in three places:

- **Personal skills** (available in every project): `~/.claude/skills/`
- **Project skills** (this project only): `.claude/skills/`
- **Shared skills** (in a published package): a Git repo or npm package

Project skills take precedence over personal skills with the same name. When you type `/skill-name`, Claude Code searches in order and uses the first match. To list all available skills, type `/help` and scroll to the **Skills** section.

## Configure skills

### Write the SKILL.md file

Every skill needs a `SKILL.md` file. The simplest version has just a body:

```markdown
# My Skill

This is a skill that does something useful.
```

Most skills add frontmatter (YAML between `---` markers) to configure when Claude uses it:

```yaml
---
description: Short description. Use when the user asks X.
autoInvoke: true
---

# My Skill

Instructions for Claude...
```

Here's what each frontmatter field does:

| Field            | Type                                      | Default                    | Purpose                                                                                                                                                                                                          |
| :--------------- | :---------------------------------------- | :------------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `description`    | string                                    | ""                         | A short (one-sentence) description of what the skill does. Claude uses this to decide when to auto-invoke the skill. Ignored if `autoInvoke: false`.                                                            |
| `autoInvoke`     | boolean                                   | true                       | If true, Claude will load this skill when your message matches the description. If false, the skill only runs when explicitly invoked with `/skill-name`.                                                         |
| `invoke`         | `user` \| `claude` \| `both` (default)    | `both`                     | Controls who can invoke the skill. See [Control who invokes a skill](#control-who-invokes-a-skill).                                                                                                             |
| `runAs`          | `direct` \| `subagent`                    | `direct`                   | If `subagent`, Claude Code will run the skill in a subagent instead of using it as a prompt. See [Run skills in a subagent](#run-skills-in-a-subagent).                                                         |
| `model`          | `opus` \| `sonnet` \| `haiku` \| `fable` | [Current default model](/) | Model to use if this skill runs in a subagent. Ignored if `runAs: direct`.                                                                                                                                       |
| `environment`    | object                                    | `{}`                       | Environment variables to pass to the skill (for injected dynamic context). Does not affect security or permissions.                                                                                             |
| `dependencies`   | array of strings                          | `[]`                       | Names of other skills or commands to load before this one. Useful if your skill refers to behavior that another skill implements. See [Skill dependencies](#skill-dependencies).                                  |
| `tags`           | array of strings                          | `[]`                       | Arbitrary tags to categorize and organize your skills. Example: `["refactoring", "testing", "codegen"]`.                                                                                                      |

### Control who invokes a skill

By default, both you and Claude can invoke a skill: you type `/skill-name` to use it directly, and Claude auto-invokes it when relevant. You can restrict invocation with the `invoke` field:

```yaml
---
invoke: user  # Only you can invoke with /skill-name. Claude never auto-invokes.
---
```

This is useful when the skill sets up a workflow that only makes sense when explicitly requested. For example, a skill that runs a data migration:

```yaml
---
description: Runs the nightly data migration. Not for routine use.
invoke: user
---

# Data Migration

This skill runs the nightly data migration. **Do not invoke lightly.**

!`./scripts/migrate-data.sh`
```

The `invoke: claude` setting is rare but useful for workflow skills that should run when you ask for something that matches the description, but that you should not invoke directly yourself:

```yaml
---
description: Runs tests when you ask to verify your changes.
invoke: claude
---

# Verify Tests

!`npm test`
```

### Run skills in a subagent

By default, Claude uses a skill as a prompt: the skill text is loaded into Claude's context and Claude orchestrates the work. Some skills are more powerful as **subagent tasks**: Claude Code spawns a separate instance of Claude that runs the skill, and reports the result back.

Use `runAs: subagent` to run a skill in a subagent:

```yaml
---
description: Refactor a module to improve maintainability.
runAs: subagent
---

# Refactor for Readability

... detailed refactoring instructions ...
```

When Claude invokes this skill, Claude Code spawns a subagent, passes it the skill instructions, and the subagent works independently. The subagent's result comes back to Claude as a concise summary.

Subagent skills are useful when:

- **You want isolation**: The skill makes edits, runs tests, and iterates. You don't want that loop in your main chat context.
- **You want focus**: The subagent runs only the skill's logic, not every skill and tool you have loaded.
- **You want to pick the model**: Use `model: haiku` for a lightweight skill, or `model: opus` for complex reasoning.
- **You want clear success criteria**: The subagent's work is wrapped in a task, so you can ask "did this skill work?" and get a yes/no answer.

The subagent still has access to your project's files and tools. It just runs independently.

### Inject dynamic context

Skills can pull in dynamic context — the results of a command, the current git branch, the uncommitted diff — before Claude reads the skill. Use the syntax `` !`command` `` in your skill body:

```markdown
# Current Changes

## Uncommitted changes

!`git diff HEAD`

## Current branch

!`git branch --show-current`

## Instructions

Summarize the changes above...
```

When the skill runs, Claude Code runs each command, captures the output, and replaces the `` !`command` `` line with the output. Claude then reads the skill with the context already inlined. The output is evaluated as markdown: if it's a code block, it renders as code; if it's plain text, it's prose.

You can also use dynamic context in the skill's frontmatter `environment` field to pass values to later environment references. Example:

```yaml
---
environment:
  PR_NUMBER: !`gh pr view --json number -q .number`
  PR_TITLE: !`gh pr view --json title -q .title`
---

# Your PR Context

The PR number is {PR_NUMBER} and the title is "{PR_TITLE}".
```

Dynamic context runs in the shell, so you can pipe and chain commands:

```markdown
!`git diff HEAD | wc -l`

!`find . -name "*.test.ts" | head -5`
```

## Additional resources

- [Agent Skills spec](https://agentskills.io) — the open standard Claude Code follows.
- [commands reference](/en/commands) — all built-in commands and bundled skills.
- [models reference](/en/models) — model alias and details.

## Advanced patterns

### Skill dependencies

You can reference another skill or command by name from inside a skill. When you do, Claude Code loads the dependency before your skill runs. This is useful when your skill builds on behavior that another skill implements.

Example: a `/review-change` skill might depend on a `/summarize-changes` skill (from the example above). The review instructions can assume that summarizing changes is available:

```yaml
---
description: Reviews your uncommitted changes and suggests improvements.
dependencies: ["summarize-changes"]
---

# Review Changes

First, use the /summarize-changes skill to see what changed. Then, review the changes and suggest improvements.
```

Dependencies load in order. If skill A depends on skill B, which depends on skill C, they load as: C, B, A.

### Make a skill that respects .gitignore

Some skills operate on your repository. If you want them to respect `.gitignore`, use `git ls-files`:

```markdown
# Audit Your Codebase

Review the files below and suggest improvements:

!`git ls-files | head -20`

## Instructions

Audit the files above...
```

### Share skills across projects

Skills in `~/.claude/skills/` are available everywhere. For skills that are specific to a team or project, put them in `.claude/skills/` and commit them to your repo. That way, every team member gets the same skills.

You can also share skills as a package:

1. **Create a repo** with skills in `.claude/skills/`.
2. **Publish to npm**: `npm init -y && npm publish` (skills work as local packages too).
3. **In a project that wants to use your skills**: add a dependency in your `.claude/dependencies.yaml`:

   ```yaml
   imports:
     - https://github.com/myteam/my-skills-repo
     - npm://my-skills-package
   ```

This way, team members can have consistent, versioned skills across all their projects.

## Pull request context

This section walks through another example: a skill that uses context from your current pull request. The skill shows how to combine dynamic context with instructions that guide Claude.

The result is a skill that runs when you ask Claude to review your changes, and that pulls in the PR title, description, and your recent commits — context that helps Claude make better suggestions.

### Your task

Create a skill that:

1. Pulls in metadata from your current PR (title, description, commits)
2. Reviews the PR's changes
3. Suggests improvements based on the PR's goals

### Environment

Set up a GitHub CLI (`gh`) and a git repo with a PR open. The skill uses `gh pr view` to fetch PR metadata.

### Build the skill

Create `~/.claude/skills/review-pr/SKILL.md`:

```yaml
---
description: Reviews the current PR. Use when you're ready to submit a pull request.
environment:
  PR_TITLE: !`gh pr view --json title --jq .title`
  PR_DESCRIPTION: !`gh pr view --json body --jq .body`
  PR_COMMITS: !`gh pr view --json commits --jq '.commits[] | .message' | head -10`
---

# Review This PR

**PR Title:** {PR_TITLE}

**PR Description:**

{PR_DESCRIPTION}

**Recent Commits:**

```
{PR_COMMITS}
```

## Your task

Review the PR above for clarity, correctness, and alignment with the PR's stated goals. Suggest improvements to the code, commit messages, and PR description.
```

The skill uses three environment variables (`PR_TITLE`, `PR_DESCRIPTION`, `PR_COMMITS`), each populated by a `gh` command. When the skill runs, Claude sees the actual PR context inlined.

### Test the skill

Open a project with a GitHub PR, then ask Claude:

```text
/review-pr
```

or

```text
Review my PR for issues.
```

Claude should respond with a review based on the actual PR data.

### Evaluate and iterate on a skill

The skill above is a starting point. Here's how to make it better:

1. **Pull in the diff**: Add a line like `` !`git diff origin/main` `` to show the actual code changes.
2. **Add a checklist**: Use a markdown checklist to guide Claude's review (e.g., "Check for error handling", "Verify tests are sufficient").
3. **Name who should review**: Add a line that tags reviewers (using environment variables or a static list).
4. **Make it specific to your project**: If you're reviewing a backend API, add specific checks for authentication, validation, and error handling. If you're reviewing a UI, add checks for accessibility and performance.

The more context and the clearer your instructions, the better Claude's suggestions will be.

## Share skills

### Publish to npm

Skills live in a `.claude/skills/<name>/` directory inside a repo. To share them:

1. Create a public repo with your skills.
2. Add a `package.json` at the root:

```json
{
  "name": "my-skills",
  "version": "1.0.0",
  "description": "Custom skills for development",
  "files": [".claude/skills"]
}
```

3. Publish to npm:

```bash
npm publish
```

4. In any project, add the skills to `.claude/dependencies.yaml`:

```yaml
imports:
  - npm://my-skills
```

### Use skills from a git repo

You can also import skills from a git repo without publishing to npm:

```yaml
imports:
  - https://github.com/myteam/my-skills-repo
```

The repo should have `.claude/skills/` at the root.

### Usage

Once you've imported skills, they work the same way as local skills. Type `/skill-name` to invoke, or Claude auto-invokes when the description matches your message.

## Organize and visualize your skills

### Tags and visualization

Skills can have tags to help organize them:

```yaml
---
tags: ["refactoring", "testing", "performance"]
---
```

When you type `/help`, Claude Code displays your skills in a grid, organized by tag. Skills without tags appear in an **Untagged** section.

### What the visualization shows

The help output shows:

| Column                     | Meaning                                                              |
| :------------------------- | :------------------------------------------------------------------- |
| **Skill Name** / Shorthand | The skill name and abbreviation (usually the first letter).          |
| **Purpose**                | The `description` field from the skill's frontmatter.                |
| **Type**                   | **Skill** for custom skills, **Command** for built-in commands.      |
| **Invocation**             | Who can invoke it: **You**, **Claude**, or **Both** (the default).   |
| **Run As**                 | **Direct** (prompt-based) or **Subagent** (spawned task).            |
| **Tags**                   | Tags to help organize and discover skills.                          |

## Troubleshooting

### The skill is not being invoked automatically

Check the frontmatter:

- Is `autoInvoke` set to `true` (or omitted, which defaults to true)?
- Does the `description` match what you're asking? Make the description short and specific. If Claude doesn't understand when to use the skill, it won't auto-invoke.
- Is there a more specific skill with a similar description? Claude picks the best match, so if two skills have overlapping descriptions, the more specific one wins.

### The skill is running, but not behaving as expected

- Check that your **instructions are clear**. Skills are prompts: unclear instructions lead to unpredictable behavior.
- If the skill uses dynamic context (`` !`command` ``), check that the command runs correctly in your shell. Run it manually to debug.
- If the skill runs in a subagent (`runAs: subagent`), check the subagent's output to see what went wrong.

### I need to update an imported skill

Skills imported from npm or Git are read-only. If you need to modify one, create a local skill with the same name (in `.claude/skills/`). Local skills take precedence.

### A skill is missing or appears under a different name

Skills are discovered by directory name. If your skill is in `.claude/skills/my-skill/SKILL.md`, the command is `/my-skill`. Check:

- Is the directory name correct?
- Is there a `SKILL.md` file inside?
- Is the `.claude/skills/` directory at the root of your project (for project skills) or in `~/.claude/skills/` (for personal skills)?

## Related resources

- [**Agent Skills spec**](https://agentskills.io/) — the open standard that Claude Code implements.
- [**Bundled skills**](#bundled-skills) — pre-built skills for code review, batch processing, debugging, and more.
- [**Commands reference**](/en/commands) — built-in commands and bundled skills.
- [**How to use Claude Code**](/en/guide) — get started with Claude Code.
