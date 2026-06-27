# Decisions: Task Tools Orchestration Rule

## Summary

We are extracting the team-lead orchestration protocol out of `.claude/commands/plan-w-team.md` and into a new always-loaded project rule, `.claude/rules/task-tools.md`. Per the Claude Code memory docs, rule files in `.claude/rules/` **without `paths:` frontmatter load into context at the start of every session** with the same priority as `.claude/CLAUDE.md` — so no `@import`, hook, or command reference is required. The new rule documents the **full schemas of all six Task\* series tools** (TaskCreate / TaskGet / TaskList / TaskUpdate / TaskOutput / TaskStop) using every available field, plus task dependencies, owner assignment, agent deployment, resume/continue, parallel execution, and the orchestration workflow — corrected to match the real harness. The entire instructional `### Team Orchestration` block is removed from `plan-w-team.md`, with **no pointer back** to the rule (it always loads anyway).

## Resolved Decisions

### Load mechanism

- **Question**: How does `.claude/rules/task-tools.md` get loaded into every session, given Claude Code has no obvious "rules loader"?
- **Answer**: Native `.claude/rules/` auto-loading. A rule file with **no `paths:` frontmatter** loads unconditionally at launch, with the same priority as `.claude/CLAUDE.md`, and is re-injected after `/compact`. No `@import`, no SessionStart hook, no command reference needed.
- **Rationale**: Confirmed verbatim by the Claude Code memory docs: _"Rules without `paths` frontmatter are loaded at launch with the same priority as `.claude/CLAUDE.md`."_ This corrected an earlier (wrong) assumption that a `.claude/rules/` file needs an `@import` to load. Simplest mechanism and correctly project-scoped.

### Extraction scope

- **Question**: What goes into the rule, and what (if anything) stays in `plan-w-team.md`?
- **Answer**: The **entire** Team Orchestration playbook moves into the rule — Task\* tools, dependencies, owner assignment, agent deployment, resume, parallel execution, **and** the orchestration workflow. The whole instructional `### Team Orchestration` block is removed from `plan-w-team.md`.
- **Rationale**: User: _"the Orchestration Workflow should be included in the rules files. Not required to include in command."_

### Command linkage

- **Question**: Should the command keep a one-line pointer / `@import` to the rule?
- **Answer**: No. No pointer, no `@import`, no link of any kind. The rule auto-loads every session, so the command can simply rely on its presence.
- **Rationale**: User: _"Not required to point the rules, as it always loaded in every session ... No required to linking with this file."_

### Schema fidelity / accuracy

- **Question**: Relocate the existing prose verbatim, or correct + enrich it against the real tool schemas?
- **Answer**: Correct and enrich. Use **every** field from the real schemas; flag `TaskOutput` as deprecated with the recommended alternative; replace the fictional `Task({... resume})` pattern with the real harness (the **Agent** tool for deployment, **SendMessage** to continue an agent).
- **Rationale**: User: _"make good use of all variables from each tool with its schemas."_ The docs also warn that duplicated/conflicting instructions cause Claude to "pick one arbitrarily," so the single surviving source must be accurate.

## Assumptions

- **Filename**: `.claude/rules/task-tools.md` (singular "task"). The user wrote both `task-tools.md` and `tasks-tools.md`; chose the singular form to mirror the "Task\* tools" naming. `.claude/rules/` is created (does not yet exist).
- **No `paths:` frontmatter** → unconditional every-session load (the explicit goal), as opposed to a path-scoped rule.
- **Dangling-reference cleanup**: `plan-w-team.md` line ~45 (`Understand your role as the team lead. Refer to the `Team Orchestration` section for more details.`) is softened so it no longer points at the removed section, **without** adding a link to the rule file.
- **Template preservation**: The `## Team Orchestration` block inside the `## Plan Format` template (the section emitted _into generated plans_, currently ~lines 298–317) is **NOT** removed. Only the instructional `### Team Orchestration` block under `## Instructions` (currently ~lines 47–210) is removed.
- **Project-level rule** (`.claude/rules/`), not user-level (`~/.claude/rules/`). User: _"loaded within this repos."_
- **Final grilling confirmation skipped** because the user explicitly said: _"You can now continue with these answers in mind."_

## Open Questions / Out of Scope

- The command frontmatter `disallowed-tools: Task` names a tool that differs from this harness's actual agent-deployment tool (`Agent`). **Noted but not changed** (surgical scope; the frontmatter does not become orphaned by this refactor).
- `build.md` and other commands do **not** reference the protocol, so only `plan-w-team.md` is edited.
- No automated test launches a fresh interactive session / inspects `/memory` to prove the rule is listed as loaded (interactive-only). Loading is validated structurally instead (file present, no `paths:` frontmatter).
- This refactor does not change orchestration _behavior_ — it relocates and corrects the reference material.
