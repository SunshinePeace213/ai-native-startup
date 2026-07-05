---
source: https://code.claude.com/docs/en/large-codebases
fetched: 2026-07-05
---
> **In here:** Nested CLAUDE.md files for scoped configuration · Sparse worktrees and deny rules · Code intelligence plugins and per-directory skills

# Set up Claude Code in a monorepo or large codebase

> Configure Claude Code for monorepos and large single-tree codebases with nested CLAUDE.md files, sparse worktrees, code intelligence, and per-package skills so Claude stays focused on the code you're working in.

A large codebase can be one repository with millions of lines or a monorepo with many packages. Claude Code works at any size, but as the codebase grows, the defaults tuned for smaller projects can fill the context window with instructions and file reads unrelated to the task, costing tokens and degrading Claude's performance.

This guide shows individual developers and engineering teams how to scope Claude to the part of the codebase a task touches. Each section notes whether a setting is personal to your machine or committed to the repository.

## What this guide covers

The [table below](#settings-on-this-page) lists each setting and what it accomplishes. The [file tree after it](#the-example-monorepo) is the example monorepo every code sample on this page refers to.

### Settings on this page

Each setting below is independent. They layer rather than replace each other, so apply whichever fit your repository. [Choose where to start Claude](#choose-where-to-start-claude) determines where your settings files live, so read it first. [Put it together](#put-it-together) shows all of them combined.

| I want to                                                                                           | Use                                                                                        |
| :-------------------------------------------------------------------------------------------------- | :----------------------------------------------------------------------------------------- |
| Load only the conventions for the code you touch, instead of one root file covering every subsystem | Per-directory [CLAUDE.md files](#layer-claude-md-files-by-directory)                       |
| Exclude CLAUDE.md files for packages you never work in                                              | [`claudeMdExcludes`](#exclude-irrelevant-claude-md-files)                                  |
| Block Claude from opening build output, generated code, and vendored dependencies                   | [`Read` deny rules](#block-reads-of-generated-and-vendored-code) in `permissions.deny`     |
| Find a symbol's definition or callers through the language server instead of scanning files         | A [code intelligence plugin](#reduce-file-reads-with-code-intelligence)                    |
| Check out only the directories a task needs when Claude creates a worktree                          | [`worktree.sparsePaths`](#check-out-only-the-directories-you-need)                         |
| Read and edit a sibling package or another repository from the same session                         | [`--add-dir`](#grant-access-across-packages-or-repositories) or `additionalDirectories`    |
| Give Claude procedures specific to one area that load only when relevant                            | Per-directory [skills](#add-per-directory-skills)                                          |
| Replace many per-directory CLAUDE.md files with one set of conventions everyone installs            | A [plugin](#centralize-conventions-when-layering-stops-scaling) in an internal marketplace |

<Tip>
  For workflow techniques that keep context small in any repository, such as [running exploration in a subagent](/en/best-practices#use-subagents-for-investigation) so file reads stay out of the main conversation, see [Best practices for Claude Code](/en/best-practices). To roll out a baseline configuration to every developer in your organization, see [Set up Claude Code for your organization](/en/admin-setup).
</Tip>

### The example monorepo

These code samples below refer to a monorepo with this structure:

```
project/
├── .claude/
│   ├── CLAUDE.md              # Root configuration
│   └── rules/
│       └── shared-rules.md    # Shared formatting and naming conventions
├── packages/
│   ├── api/
│   │   ├── .claude/
│   │   │   └── CLAUDE.md      # API-specific settings override root config
│   │   ├── src/
│   │   │   └── routes/
│   │   │       ├── users.ts
│   │   │       └── posts.ts
│   │   ├── node_modules/
│   │   └── dist/              # Ignored by deny rules
│   ├── web/
│   │   ├── src/
│   │   │   └── components/
│   │   │       ├── Button.tsx
│   │   │       └── Card.tsx
│   │   └── node_modules/
│   ├── ui/
│   │   ├── .claude/
│   │   │   └── CLAUDE.md      # UI library settings
│   │   └── src/
│   │       └── components/
│   │           ├── Input.tsx
│   │           └── Modal.tsx
│   └── shared/
│       ├── .claude/
│       │   └── CLAUDE.md      # Shared package rules
│       └── src/
│           └── types.ts
└── README.md
```

## Choose where to start Claude

All settings in this guide come in two flavors: **personal** (in `~/.claude/config/` or `~/.claude/rules/`) and **repository** (in `.claude/` inside the project). The convention below determines which you set and how they interact.

**For personal settings that apply across all your projects:**

1. Create `~/.claude/config/config.json`
2. Add any settings below marked "personal"
3. They apply to every project you work in

**For settings checked into the repository:**

1. Create or edit `.claude/CLAUDE.md` and `.claude/permissions.deny` in the root
2. Add nested `.claude/` directories inside packages as needed
3. These settings override your personal ones in that directory and below (unless the nested directory has its own setting)

## Layer CLAUDE.md files by directory

Each CLAUDE.md file in the repository acts as a "settings layer." When you open a directory, Claude loads:

1. Your personal CLAUDE.md from `~/.claude/CLAUDE.md` (if it exists)
2. The repository root `.claude/CLAUDE.md`
3. Every .claude/CLAUDE.md in ancestor directories up to the root
4. The .claude/CLAUDE.md in the current directory (if it exists)

Each layer overrides settings from the one before. Layers are additive for most fields — skills, rules, and custom instructions add to the pool rather than replacing it.

### Root CLAUDE.md

The root `.claude/CLAUDE.md` at project root should contain conventions that apply across the entire repository. This example assumes you follow [Common patterns for CLAUDE.md files](/en/claude-md-reference):

```markdown
# Project conventions

## Coding style
- Use TypeScript strict mode in all packages
- Keep functions under 50 lines
- Name private fields with leading underscore

## Testing
- Test coverage must be > 80%
- Use Jest for unit tests, Playwright for E2E

## Commit messages
Follow [Conventional Commits](https://www.conventionalcommits.org/).
```

This file is optional if all your packages have their own .claude/CLAUDE.md files, but a root file is a good place to put organization-wide conventions that apply everywhere.

### Per-package CLAUDE.md

A .claude/CLAUDE.md inside `packages/api/` overrides the root settings for that package and its subdirectories:

```markdown
# API package configuration

Extends the root project conventions with API-specific rules.

## Project structure
- `src/routes/` — HTTP endpoint handlers
- `src/middleware/` — Express middleware
- `src/models/` — Data models and database types

## Testing
Tests live in `src/__tests__/` and run against a local SQLite database.
Use the test database setup in `./__test-setup.ts`.

## Dependencies
Do not import from `../web` or `../ui`. Use `packages/shared` for shared types.
```

Layering works: the API package's CLAUDE.md inherits the root coding style and commit conventions, then adds API-specific rules.

### Tip: Which settings go where?

- **Root .claude/CLAUDE.md**: Conventions that apply everywhere (coding style, naming, git workflow)
- **Per-package .claude/CLAUDE.md**: How to run tests, the package structure, constraints between packages
- **Rules files under .claude/rules/**: Long procedures shared across packages (`shared-rules.md`)

## Exclude irrelevant CLAUDE.md files

By default, Claude loads every .claude/CLAUDE.md it finds walking up the directory tree from your current location. If you have many packages and only work in a few, you can prevent Claude from loading settings files in packages you don't touch.

Add this to your root `.claude/CLAUDE.md` (this is a **repository** setting):

```markdown
# Exclude CLAUDE.md from packages we don't usually work in
claudeMdExcludes:
  - packages/analytics/**
  - packages/mobile/**
```

This uses glob syntax. The paths are relative to the root of the repository. Now when you work in `packages/api`, Claude won't load conventions from `packages/analytics`.

(If you later do work in an excluded package, just comment out its entry temporarily.)

## Block reads of generated and vendored code

Large codebases contain generated files (build output, compiled types), vendored dependencies, and build artifacts. Reading these fills the context window without adding useful information.

Create or edit `.claude/permissions.deny` in your repository root (this is a **repository** setting):

```
# Deny read access for generated code and dependencies
Read: packages/*/dist/**
Read: packages/*/build/**
Read: **/node_modules/**
Read: **/.next/**

# Deny build logs and caches
Read: .next/**
Read: .turbo/**
Read: **/__pycache__/**

# Deny version control and CI artifacts
Read: .git/**
Read: .github/workflows/
```

The format is `<action>: <glob>`. Each rule blocks Claude from opening that file or directory. Globbing follows the [standard glob syntax](https://github.com/brace-expansion/minimatch#features).

You can also create a `permissions.allow` file to explicitly grant access to files that would otherwise be denied. Nested `.claude/permissions.deny` files in subdirectories work too — a permissions file in `packages/special/` overrides deny rules from the root for that package and below.

### Tip: Use per-directory deny rules to lock down generated code

In a monorepo where one package's build output is another's input, create a `packages/api/.claude/permissions.deny`:

```
# API only: don't open the web build
Read: ../web/dist/**
```

This prevents Claude from trying to understand web's generated JavaScript when working on the API.

## Reduce file reads with code intelligence

Code intelligence uses your language server to find the definition of a symbol or its callers without Claude reading all the source files. It's much cheaper than asking Claude to scan a large folder.

To enable it for a repository, add this to your root `.claude/CLAUDE.md` (this is a **repository** setting):

```yaml
codeIntelligence:
  typescript:
    command: npx
    args: ["typescript-language-server", "--stdio"]
```

For now, TypeScript/JavaScript is the only supported language. The command and arguments should start your language server on stdin/stdout.

Once enabled, code intelligence features:

- **Symbol search**: "Find the definition of X" queries the language server instead of scanning files, returning just the relevant file and line
- **Find usages**: "Show me all call sites of Y" without reading all files that might import it
- **Faster refactors**: "Rename X across the codebase" runs against the language server's symbol index

If you have multiple packages with different TypeScript configurations, each package can have its own `.claude/CLAUDE.md` with a different language server setup.

### Language server setup examples

**TypeScript via typescript-language-server:**

```yaml
codeIntelligence:
  typescript:
    command: npx
    args: ["typescript-language-server", "--stdio"]
```

**Ruff LSP for Python:**

```yaml
codeIntelligence:
  python:
    command: ruff
    args: ["server"]
```

**Pylance (requires setup):**

```yaml
codeIntelligence:
  python:
    command: node
    args: ["/path/to/pylance-server.js", "--stdio"]
```

If your language server isn't listed, check whether it supports the LSP (Language Server Protocol) and pass the command that starts it on stdio.

## Check out only the directories you need

When Claude creates a git worktree to edit files, it can check out the entire repository or a sparse set of paths. For a large monorepo, checking out only the directories you need saves time and disk space.

Add this to your root `.claude/CLAUDE.md` (this is a **repository** setting):

```yaml
worktree:
  sparsePaths:
    - .claude/
    - packages/api/
    - packages/shared/
```

When Claude creates a worktree to edit files in those locations, it will check out only those paths. The sparse checkout doesn't affect what Claude can read in the main repository — it only limits what gets cloned into the worktree.

### Paths in sparsePaths

Each path in `sparsePaths`:

- Is relative to the repository root
- Can be a directory or file glob (e.g., `packages/*/src/` checks out the `src/` subdirectory of every package)
- Should include `.claude/` itself if you reference `.claude/rules/` files or have nested `.claude/` configs

Sparse checkout doesn't remove directories; it just prevents them from being cloned. A sparse worktree still has full git history.

## Grant access across packages or repositories

When a task touches multiple packages, or when you need to read code from a related but separate repository, use `--add-dir`:

```bash
code --add-dir packages/web --add-dir /home/you/other-repo
```

The `--add-dir` flag appends directories to the context window, and Claude gains read and edit access to those locations (subject to `permissions.deny` rules). You can add multiple directories in one command.

To make this permanent for a project, add this to your root `.claude/CLAUDE.md` (this is a **repository** setting):

```yaml
additionalDirectories:
  - packages/web/
  - packages/shared/
```

When you open Claude Code in any package, it will automatically grant access to `packages/web/` and `packages/shared/`.

## Add per-directory skills

Skills are reusable procedures (tests, linters, deployment scripts) that load only in the directory where you place them. Each package can have its own skills specific to its needs.

Create `.claude/skills/` in any package:

```
packages/api/
├── .claude/
│   ├── CLAUDE.md
│   └── skills/
│       ├── test.md        # "Run tests for the API"
│       ├── lint.md        # "Lint the API code"
│       └── build.md       # "Build the API for production"
└── src/
    └── ...
```

A skill file is a markdown file that describes a repeatable task. Create `packages/api/.claude/skills/test.md`:

```markdown
# Run API tests

Run all tests for the API package.

## Steps
1. Change to the `packages/api/` directory
2. Run `npm test`
3. Report any failures or coverage drops
```

When you open Claude Code in `packages/api/`, the skill "Run API tests" will appear in the command menu. If you open Claude Code in a different package, it won't.

The skill file is just markdown — no special syntax. Keep skills concise; each one should describe what the command does and how to run it.

## Centralize conventions when layering stops scaling

If you have dozens of packages, creating a .claude/CLAUDE.md for each one becomes tedious. Instead, publish a plugin to your organization's Claude marketplace that every developer installs.

1. Create a plugin repository with a `.claude/CLAUDE.md` and skill files
2. Publish it to your internal marketplace (contact Anthropic to enable it)
3. Every developer installs it once
4. Every project loads that plugin's settings and skills automatically

This is an advanced workflow. For most monorepos, per-directory CLAUDE.md files work fine.

## Put it together

Here's what a complete configuration looks like using most features above. This is the `.claude/CLAUDE.md` at the root of a monorepo:

```markdown
# Project configuration for the Example Monorepo

All developers should follow these conventions.

## Coding standards

- Use TypeScript strict mode everywhere
- Format code with Prettier (configured at the root)
- Tests must have > 80% coverage, measured with Jest
- Follow [Conventional Commits](https://www.conventionalcommits.org/) for commit messages

## Project structure

This is a monorepo with packages under `packages/`:

- `packages/api/` — Node.js backend service
- `packages/web/` — Next.js frontend
- `packages/ui/` — Shared React components
- `packages/shared/` — Shared types and utilities

## Import rules
- Never import from `web` in the `api` package
- Shared types always come from `packages/shared/`

claudeMdExcludes:
  - packages/mobile/**
  - packages/desktop/**

additionalDirectories:
  - packages/shared/

codeIntelligence:
  typescript:
    command: npx
    args: ["typescript-language-server", "--stdio"]

worktree:
  sparsePaths:
    - .claude/
    - packages/api/
    - packages/shared/
    - packages/web/
```

Then, in `packages/api/.claude/CLAUDE.md`, override with API-specific rules:

```markdown
# API package configuration

Extends the root project conventions.

## API-specific structure
- Endpoints live in `src/routes/`
- Use Express.js for the server
- Database models in `src/models/`, using Prisma ORM

## Testing
- Tests live alongside source: `src/__tests__/`
- Run `npm test` to run the full suite
- Run `npm test -- --watch` for watch mode

## Building and deployment
- Run `npm run build` to compile TypeScript to `dist/`
- Docker image: see `Dockerfile` in this directory
- Deployed via GitHub Actions CI/CD

## Do not import from
- `packages/web/`
- `packages/desktop/`
```

And `packages/api/.claude/permissions.deny`:

```
# Deny API access to unrelated packages
Read: ../web/dist/**
Read: ../ui/dist/**
Read: ../mobile/**
```

The final result:
- Developers see only API-specific instructions when working in `packages/api/`
- Claude skips conventions for mobile and desktop packages
- Sparse checkouts only pull API, shared, and root configuration
- deny rules prevent Claude from accidentally reading build output or unrelated packages
- Code intelligence queries the TypeScript language server for symbol definitions

## Scope and plan changes that span packages

The configuration above controls what Claude sees. When a single change touches several packages, such as updating a shared type along with every call site that uses it, how you scope and sequence the task also affects the result.

Two techniques help keep a cross-package change consistent:

* **Give Claude the whole change in one session**: handing over the shared edit and its call sites together keeps the decisions behind each edit consistent, rather than re-deriving them per package
* **Save the plan to a file before editing**: [plan first](/en/best-practices#explore-first-then-plan-then-code) and ask Claude to write the plan to a markdown file in the repository. A long cross-package session [compacts its context](/en/context-window#what-survives-compaction) along the way, and the saved plan survives where conversation history may not

## Next steps

Once this configuration is in place, you can refine it:

* Use [hooks](/en/hooks-guide) to run per-directory linters or type-checkers after Claude edits files
* Review [Manage costs effectively](/en/costs) to understand how codebase size affects token usage and how to set spend limits before a wider rollout
* Read [How Claude Code works in large codebases](https://claude.com/blog/how-claude-code-works-in-large-codebases-best-practices-and-where-to-start) on the Claude blog for organizational rollout patterns and ownership models that sit above the per-repository configuration on this page
