# Spec: <task name>

- **Owner:** <github handle of the human owner, e.g. @ringo>
- **Status:** Drafted for Review
  <!-- Lifecycle, set by /harness-layer:harness-plan: Drafted for Review → Approved (on a Codex
       `approved` verdict). A cycle that ends still changes-requested — or with Codex unavailable —
       records needs-human in ## Codex Verification and keeps this status. One value only. -->

## Task Description

<describe the task in detail, in plain language, based on the prompt — what is being asked and the context a builder needs>

## Objective

<one or two sentences stating what is true when this plan is complete — the definition of success, observable not aspirational>

## Non-Goals

<bullet list of what this plan explicitly will NOT do — the scope fence. Pull the out-of-scope items from decisions.md so scope drift is visible in the spec itself. Write "None" only if genuinely none.>

<!-- Include ## Problem Statement and ## Solution Approach only when task_type is feature OR complexity is medium/complex; omit for simple chores. -->

## Problem Statement

<define the specific problem or opportunity this addresses — why it's worth doing now>

## Solution Approach

<the chosen technical approach at a high level and how it satisfies the Objective; note the main alternative considered and why it lost>

## Requirements & Decisions

<the 2-4 most important LOCKED decisions/constraints a builder must honor, as bullets. A summary — the full interview record lives in decisions.md. Order by volatility: most-likely-to-change decisions first, each stating the decision, a short why, AND its live alternative; mechanical constraints last.>

## Tracking

<!-- Recorded by /harness-layer:harness-plan. The Issue field is the SINGLE SOURCE OF TRUTH
     /harness-layer:harness-build reads — it NEVER re-derives #N from the local `worktree-<slug>`
     branch name. spec.md is the single home for this block; decisions.md does not duplicate it. -->

- **Issue:** <#N — mandatory; every plan is filed as an issue before its first push>
- **Branch:** <convention branch `<type>/<N>-<slug>`>
- **Worktree:** <absolute worktree path>
- **Review profile:** <kb-grounded | standard>
- **PR:** <#M — filled by /harness-layer:harness-build>

## Relevant Files

Use these files to complete the task:

<bullet list of existing files the build will touch, each with a one-line why. Add an h3 "### New Files" subsection for files to be created, each with its purpose.>

## Edge Cases

<enumerate the boundary/failure conditions the build must handle: empty or missing input, oversized input, concurrent/duplicate runs, partial failure, an unavailable dependency (gh/codex/network), idempotency on re-run. One bullet each, stating the expected behavior.>

## Red Flags

<anti-patterns signalling the plan is being skipped or scope is drifting. Keep these standing examples; add task-specific ones:>

- Starting to write code without any written requirements
- Asking "should I just start building?" before clarifying what "done" means
- Implementing features not mentioned in any spec or task list
- Making architectural decisions without documenting them
- Skipping the spec because "it's obvious what to build"

## Notes

<optional: extra context, dependencies, follow-ups. New libs: specify with `uv add <pkg>` (Python) or `bun add <pkg>` (JS/TS).>

## Codex Verification

<!-- CLAUDE-OWNED. The outcome summary Claude records after the Codex loop. -->

- **Outcome:** <approved at round N | needs-human (blockers | codex-unavailable)>
- **Rejected findings:** <any Codex finding Claude chose not to act on, each with a one-line rationale; "none" if all warranted findings were applied>

## References

<a tree of the sibling plan files and their purpose, so the four files trace to each other:>

```text
specs/<plan-name>/
├── discovery/              # pre-plan pass pages + decisions-draft.md (when the chain ran)
├── spec.md                 # this file — what & why, tracking, review record
├── decisions.md            # interview record: resolved decisions, assumptions, out-of-scope
├── tasks.md                # how & who: phases, team, step-by-step tasks
├── acceptance-criteria.md  # done: acceptance criteria + validation commands
└── artifacts/              # implementation-plan page (+ reference map when porting semantics)
```

## Self Validation

- [ ] Objective, Task Description, and Non-Goals are filled in (no placeholders left)
- [ ] Requirements trace to tasks in tasks.md and to checks in acceptance-criteria.md
- [ ] Acceptance criteria are specific and testable
- [ ] All four files exist under specs/<plan-name>/ and are saved in the repository
- [ ] Codex has reviewed the spec and Status reflects the outcome
