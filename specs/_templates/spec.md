# Spec: <task name>

<!-- Guidance lives in HTML comments so an unfilled section renders empty instead of
     shipping placeholder prose. A Stop hook blocks the planning run while a required
     section is empty or still holds a `<placeholder>`. Keep or delete the comments. -->

- **Owner:** @<github handle>
- **Status:** Drafted for Review
  <!-- Drafted for Review → Approved on a Codex `approved` verdict. A cycle ending
       changes-requested — or with Codex unavailable — keeps this status and records
       needs-human in ## Codex Verification. One value only. -->

## Tracking

<!-- Recorded by /harness-layer:harness-plan, read by the rest of the pipeline. Issue is
     the SINGLE SOURCE OF TRUTH for #N — never re-derive it from the local
     `worktree-<slug>` branch name. spec.md is the only home for this block. -->

- **Type:** <feat | fix | docs | style | refactor | perf | test | chore>
  <!-- Sets the branch prefix, commit type, PR template, and issue form. -->
- **Complexity:** <simple | medium | complex>
  <!-- Gates the conditional sections below and the artifact pages. -->
- **Issue:** <#N — mandatory, filed before the first push>
- **Branch:** <the convention branch, `type/N-slug`>
- **Worktree:** <absolute worktree path>
- **Review profile:** <kb-grounded | standard>
- **PR:** <#M — filled by /harness-layer:harness-build>

## Task Description

<!-- What is being asked and the context a builder needs, in plain language. -->

## Objective

<!-- One or two sentences stating what is true when this plan is complete —
     observable, not aspirational. -->

## Non-Goals

<!-- What this plan explicitly will NOT do — the scope fence. Pull the out-of-scope
     items from decisions.md so scope drift is visible here. Write "None" only if
     genuinely none. -->

<!-- ## Problem Statement and ## Solution Approach: include for a feature or for
     medium/complex work; omit for simple chores. -->

## Problem Statement

<!-- The specific problem or opportunity this addresses, and why it's worth doing now. -->

## Solution Approach

<!-- The chosen approach and how it satisfies the Objective. Name the main alternative
     considered and why it lost. -->

## Requirements & Decisions

<!-- The 2-4 LOCKED decisions a builder must honor, ordered by volatility:
     most-likely-to-change first, each stating the decision, a short why, AND its live
     alternative; mechanical constraints last. A summary — the full interview record
     lives in decisions.md. -->

<!-- ## Interfaces & Contracts: include when the change adds or alters an interface;
     omit when nothing's shape changes. -->

## Interfaces & Contracts

<!-- The exact shapes the build must produce, as code: function signatures, JSON/TOML
     fragments, CLI invocations, file layouts, before/after config. Prefer a code block
     to a sentence — an acceptance check can assert a signature, never an adjective. -->

## Relevant Files

<!-- Existing files the build will touch, each with a one-line why. Add a "### New Files"
     subsection for files to be created, each with its purpose. -->

## Edge Cases

<!-- The boundary and failure conditions the build must handle, one bullet each stating
     the expected behavior: empty or missing input, oversized input, concurrent or
     duplicate runs, partial failure, an unavailable dependency (gh/codex/network),
     idempotency on re-run. -->

## Risk & Rollback

<!-- What this change can break and how to undo it. Feeds the PR body's Risk & Rollback
     section. -->

- **Blast radius:** <what breaks if this is wrong, and what notices first>
- **Rollback:** <the exact undo — revert the commit, re-run a command, flip a setting; say
  so plainly if there is no clean undo>
- **In-flight work:** <what happens to sessions, worktrees, branches, or data created
  before this lands>

## Guardrails

<!-- The specific ways THIS build goes wrong — the tempting-but-wrong move a builder
     would otherwise make ("this is a move, not a rewrite"). Task-specific only; the
     standing process rules live in spec-standards.md. "None" is a valid answer. -->

## Notes

<!-- Optional: extra context, dependencies, follow-ups. New libs: specify with
     `uv add <pkg>` (Python) or `bun add <pkg>` (JS/TS). -->

## Codex Verification

<!-- CLAUDE-OWNED — the outcome summary Claude records after the Codex loop. -->

- **Outcome:** <approved at round N | needs-human (blockers | codex-unavailable)>
- **Rejected findings:** <each Codex finding Claude chose not to act on, with a one-line
  rationale; "none" if all warranted findings were applied>
