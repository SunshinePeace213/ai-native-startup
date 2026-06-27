---
description: Implement a saved plan. Pass a feature name (e.g. grilling-into-plan-w-team) to load its specs folder, or a direct path to a plan file.
argument-hint: [feature-name | path-to-plan]
---

# Build

Resolve `TARGET` to a plan, read the plan and its decision log, then follow the
`Workflow` to implement it and `Report` the completed work.

## Variables

TARGET: $ARGUMENTS

## Instructions

- If no `TARGET` is provided, STOP immediately and ask the user to provide it (AskUserQuestion).
- Resolve `TARGET` to a plan file (PLAN) and an optional decision log (DECISIONS), in order:
  1. If `specs/<TARGET>/plan.md` exists → PLAN = `specs/<TARGET>/plan.md`, DECISIONS = `specs/<TARGET>/decisions.md` (feature-name form).
  2. Else if `<TARGET>` is an existing file → PLAN = `<TARGET>`, DECISIONS = a `decisions.md` sibling in the same folder if present (direct path / legacy flat spec).
  3. Else STOP and report which paths were searched.

## Workflow

- If DECISIONS exists, read it first: it holds the requirements, locked decisions, assumptions, and out-of-scope items that constrain the build. Treat it as binding context.
- Read PLAN, think hard about it, and implement it into the codebase, honoring the decision log. If PLAN and DECISIONS conflict, STOP and surface the conflict instead of guessing.

## Report

- Present the `## Report` section of the plan.
