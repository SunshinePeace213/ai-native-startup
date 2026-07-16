---
paths:
  - ".claude/rules/**/*"
  - "AGENTS.md"
  - "CLAUDE.md"
---

# Memory Series

How this repo's memory is fetched, recorded, edited, and extended. All memory lives in
the hub or in `.claude/rules/` — never create a new root-level memory markdown file.

## Layout

- `AGENTS.md` (root) — the hub: tooling, pipeline, model selection, and a pointer to every rule. `CLAUDE.md` only `@`-imports it — never write memory into `CLAUDE.md`.
- `.claude/rules/<kebab-case>.md` — one file per convention series, scoped via `paths:` frontmatter.
- `GIT-COMMIT-PR-MESSAGE.md` (root) — git, PR, and issue policy.

## Record & edit

- A new preference or convention in an existing series → edit that series' rule file.
- Cross-cutting or repo-wide → the matching `AGENTS.md` section.
- A genuinely new convention series → create a new rule file (below) and reference it from `AGENTS.md`. One-off notes don't get a file.

## Create a new rule file

1. Name it `<kebab-case>.md` under `.claude/rules/`, one topic per file, brief and imperative.
2. Scope it with `paths:` frontmatter — the rule loads only when the session touches a matching file:

   | Pattern | Matches |
   | --- | --- |
   | `**/*.ts` | all TypeScript files in any directory |
   | `src/**/*` | all files under `src/` |
   | `*.md` | markdown files in the project root |
   | `src/components/*.tsx` | React components in that one directory |

3. No `paths:` frontmatter → the rule loads at session start, exactly like CLAUDE.md content. Reserve that for rules every session needs (`task-tools.md` is the only current one); everything else must be path-scoped.
4. Add a pointer to the new rule from the matching `AGENTS.md` section.
