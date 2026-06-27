# Plan: Migrate /grilling into /plan-w-team

## Task Description

`/plan-w-team` (`.claude/commands/plan-w-team.md`) builds an engineering spec but
has no requirement-gathering step — it goes straight from `USER_PROMPT` to a
written plan, so the plan rests on assumptions. The `/grilling` skill
(`.claude/skills/grilling/SKILL.md`) is a relentless one-question-at-a-time
interview. This task inlines grilling as a new phase in `/plan-w-team` that runs
before design, driven by the `AskUserQuestion` tool, and reorganizes output into
a per-plan folder with a separate decision log. The standalone `/grilling` skill
keeps its behavior; only its description is corrected.

Task type: enhancement. Complexity: medium. (Two-file prompt-engineering edit; no
runtime code.)

## Objective

When complete:
- `/plan-w-team` grills the user via `AskUserQuestion` (one question per call,
  recommended answer first, "Other" for free input) until a coverage ledger is
  clear and the user signs off — *before* any design or file writing.
- `/plan-w-team` writes to `specs/<plan-name>/plan.md` and a decision log to
  `specs/<plan-name>/decisions.md`.
- The four agreed features exist: coverage ledger, decision log file, accept-all
  escape hatch, final confirmation checkpoint.
- The standalone `/grilling` skill keeps `disable-model-invocation: true` and has
  a description with the dead auto-trigger clause removed.
- `/build <feature-name>` (e.g. `/build grilling-into-plan-w-team`) resolves to
  `specs/<feature-name>/`, reads both `plan.md` and `decisions.md`, and implements
  the plan honoring the decision log. Direct paths and legacy flat specs still work.

## Problem Statement

Plans drafted without resolving requirements bake in wrong assumptions, and there
is no durable record of why decisions were made. We need a structured interview
that terminates on real coverage and a traceable decision log, without making the
high-friction grilling auto-fire in unrelated work.

## Solution Approach

Inline the grilling protocol as a `/plan-w-team` phase (deterministic; no
cross-skill invocation, so the standalone skill's `disable-model-invocation: true`
is irrelevant to the integration). Use `AskUserQuestion` one-at-a-time with a
recommended-first option set. Track coverage in a ledger; loop until clear; offer
an accept-all escape hatch; end with a single confirmation question. Persist every
answer (and every deferred "you decide" as an explicit assumption) to a separate
`decisions.md`, and write the plan to `plan.md`, both under `specs/<plan-name>/`.

See `decisions.md` in this folder for the full rationale behind each choice.

## Relevant Files

- `.claude/commands/plan-w-team.md` — primary edit target. Add grilling phase,
  Grilling Protocol section, Decision Log Format section, per-plan output paths,
  and Workflow/Report updates.
- `.claude/skills/grilling/SKILL.md` — fix description only; keep
  `disable-model-invocation: true`. Source of the inlined protocol text.
- `.claude/commands/build.md` — edit target. Add feature-name resolution
  (`/build <feature-name>` → `specs/<feature-name>/`) and make it read both
  `plan.md` and `decisions.md`. Back-compat: direct paths and legacy flat specs.
- `.claude/skills/meta-commands/SKILL.md` — (a) read-only reference for the house
  command template (`# Purpose` → `## Variables` → `## Instructions` →
  `## Workflow` → `## Report`; model as alias; dynamic-first variables); (b) ALSO
  an edit target for the injection-bug fix in the Incident Report below — a
  separate, parallel change that does not block the grilling work.

## Implementation Phases

### Phase 1: Foundation
Reorganize output to per-plan folders. Update `## Variables` to add `PLAN_DIR`,
`PLAN_FILE`, `DECISION_LOG`; update the Purpose paragraph and the save-related
`## Instructions` bullets to reference the new paths and two-file output.

### Phase 2: Core Implementation
Add the `## Grilling Protocol` and `## Decision Log Format` sections to
`plan-w-team.md`; insert the "Grill Requirements" step into `## Workflow` between
"Understand Codebase" and "Design Solution"; add a brief
`## Requirements & Decisions` pointer to the Plan Format.

### Phase 3: Integration & Polish
Update the `## Report` block to emit the new paths and a "Key Decisions" summary
and the `/build <plan-name>` handoff. Fix the standalone `/grilling` description.
Update `/build` to accept a feature name and read both `plan.md` and `decisions.md`.
Validate all edited files.

## Exact Edits

### A. `.claude/commands/plan-w-team.md`

**A1 — Frontmatter `description`** (replace):
```
description: Grills the user to lock requirements, then creates a concise engineering implementation plan and a decision log, saved to a per-plan specs folder
```

**A2 — Purpose paragraph** (the line after `# Plan With Team`): rewrite to state
grilling runs first and that output is a per-plan folder with a plan plus a
decision log.

**A3 — `## Variables`**: keep existing vars; add below `PLAN_OUTPUT_DIRECTORY`:
```
PLAN_DIR: `specs/<plan-name>/` - per-plan folder; `<plan-name>` is the descriptive kebab-case topic
PLAN_FILE: `specs/<plan-name>/plan.md` - the implementation plan
DECISION_LOG: `specs/<plan-name>/decisions.md` - grilling decision log + assumptions
```

**A4 — `## Instructions`**: 
- Add a bullet near the top (after the "Carefully analyze the user's
  requirements" bullet): "Before designing or writing any files, run the
  `Grilling Protocol` to lock requirements. Explore the codebase to self-answer
  questions; ask the user only what the code cannot answer."
- Replace the filename bullet with: "Generate a descriptive kebab-case
  `<plan-name>` and create the per-plan folder `specs/<plan-name>/`."
- Replace the save bullet with: "Save the implementation plan to `PLAN_FILE` and
  the grilling decision log to `DECISION_LOG`."

**A5 — New `## Grilling Protocol` section** (insert before `## Workflow`):
```md
## Grilling Protocol

Before designing the plan, interview the user relentlessly until every decision
needed to build is resolved. The goal is a shared, written understanding, not a guess.

- **Explore first.** If a question can be answered by reading the codebase, answer
  it yourself. Ask the user only what the code cannot tell you.
- **One question at a time.** Ask exactly one question per turn using the
  AskUserQuestion tool. Provide 2-4 concrete options, put your recommended answer
  first and append " (Recommended)" to its label; the tool's automatic "Other"
  choice lets the user type a free-form answer. Wait for the answer before the
  next question.
- **Coverage ledger.** Track a checklist of decision dimensions as resolved or
  open; keep grilling until none are open. Cover, as applicable: scope & non-goals,
  target users, success criteria & acceptance tests, data model, interfaces/APIs,
  edge cases & error handling, performance & scale, security & authz,
  observability, rollout/migration, dependencies, testing strategy. Mark
  genuinely-irrelevant dimensions N/A.
- **Adaptive depth.** Grill in proportion to complexity: a light pass for simple
  chores, a deep pass for complex features. Do not interrogate trivial tasks.
- **Accept-all escape hatch.** Offer a standing way to stop early. If the user
  chooses "Accept all recommendations", close every open item with your
  recommended answers, record them as assumptions, and move on.
- **Record every decision.** Capture each answer, and every deferred "you decide"
  as an explicit assumption, for the decision log (see `Decision Log Format`).
- **Final confirmation.** When the ledger is clear, replay all decisions in a
  single AskUserQuestion for sign-off (Approve / revise a specific decision / add
  more). Proceed to design only after approval.
```

**A6 — New `## Decision Log Format` section** (insert after the Plan Format
fenced block):
```md
## Decision Log Format

Write the full grilling record to `DECISION_LOG`. Use this structure:

# Decisions: <task name>
## Summary — one paragraph: agreed scope + key choices
## Resolved Decisions — per decision: Question / Answer / Rationale
## Assumptions — every deferred "you decide" / accept-all item, explicitly
## Open Questions / Out of Scope — deferred or excluded items (non-goals)
```

**A7 — Plan Format**: add a short section inside the templated plan, after
`## Objective`:
```md
## Requirements & Decisions
<2-4 most important locked decisions and assumptions; full record in decisions.md>
```

**A8 — `## Workflow`**: insert as step 3 (renumber the rest):
```
3. Grill Requirements - Run the `Grilling Protocol`: interview the user one
   question at a time via AskUserQuestion until the coverage ledger is clear, then
   get final sign-off. Do NOT design or write files before this completes.
```
Also update the save steps to: create folder `specs/<plan-name>/`, write
`DECISION_LOG`, write `PLAN_FILE`.

**A9 — `## Report`**: replace the file/handoff lines with:
```
Plan: specs/<plan-name>/plan.md
Decisions: specs/<plan-name>/decisions.md
```
add a "Key Decisions (from grilling)" bullet list, and change the handoff to:
```
/build <plan-name>
```

### B. `.claude/skills/grilling/SKILL.md`

**B1 — keep** `disable-model-invocation: true` unchanged.

**B2 — `description`** (replace): remove the dead auto-trigger clause:
```
description: Interview the user relentlessly about a plan or design before building, one question at a time with a recommended answer for each. Invoke explicitly with /grilling.
```

### C. `.claude/commands/build.md`

Make `/build` accept a **feature name** and read both files in the per-plan folder.

**C1 — frontmatter** (replace):
```
description: Implement a saved plan. Pass a feature name (e.g. grilling-into-plan-w-team) to load its specs folder, or a direct path to a plan file.
argument-hint: [feature-name | path-to-plan]
```

**C2 — body** (replace the whole body with):
~~~md
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
~~~

## Acceptance Criteria

- `plan-w-team.md` contains a `## Grilling Protocol` section that mandates
  AskUserQuestion, one-question-at-a-time, recommended-first, a coverage ledger,
  an accept-all escape hatch, and a final confirmation.
- `plan-w-team.md` `## Variables` defines `PLAN_DIR`, `PLAN_FILE`, `DECISION_LOG`
  under `specs/<plan-name>/`; Workflow includes a "Grill Requirements" step before
  "Design Solution"; Report emits both file paths and `/build <plan-name>`.
- `plan-w-team.md` retains `disallowed-tools: Task, EnterPlanMode` and does NOT
  add an `allowed-tools` allowlist (so AskUserQuestion stays available).
- `grilling/SKILL.md` keeps `disable-model-invocation: true` and its description no
  longer mentions auto-trigger / "grill trigger phrases".
- All edited command/skill files (`plan-w-team.md`, `grilling/SKILL.md`,
  `build.md`) pass the meta-commands validator.
- `/build <feature-name>` resolves to `specs/<feature-name>/plan.md` and reads
  `decisions.md`; a direct path and a legacy flat `specs/<name>.md` still resolve;
  a missing target stops with a clear message; `build.md`'s description has no
  angle brackets.

## Validation Commands

- `cd .claude/skills/meta-commands && uv run --with pyyaml python scripts/validate_command.py ../../commands/plan-w-team.md` — frontmatter, caps, angle-bracket ban (note: angle brackets are only banned in `description`, not the body).
- `cd .claude/skills/meta-commands && uv run --with pyyaml python scripts/validate_command.py ../../skills/grilling/SKILL.md` — validate the skill frontmatter.
- `grep -n "disable-model-invocation: true" .claude/skills/grilling/SKILL.md` — confirm the flag is retained.
- `grep -n "AskUserQuestion" .claude/commands/plan-w-team.md` — confirm the tool is wired into the protocol.
- `cd .claude/skills/meta-commands && uv run --with pyyaml python scripts/validate_command.py ../../commands/build.md` — validate build.md (esp. no angle brackets in the description).

## Notes

- This is a surgical two-file edit. The standalone `/grilling` body is intentionally
  left as prose (description-only change); upgrading it for parity is an open
  decision recorded in `decisions.md`.
- The `meta-commands` SKILL.md injection bug is documented in the Incident Report
  below (per user request) and applied as a separate, parallel change.
- Out of scope: changing `plan-w-team`'s own `disable-model-invocation`.

## Incident Report: meta-skill-family Skill-tool load audit

Audited the three authoring skills by invoking each via the Skill tool and by
grepping every `SKILL.md` for dynamic-injection tokens. The harness pre-executes
those tokens as shell commands at skill-load time, *before* Claude sees the body —
two forms: inline (a bang immediately followed by a backtick-quoted command) and
a fenced block whose info string is a single bang.

| Skill | Skill-tool load | Injection tokens in SKILL.md | Status |
|---|---|---|---|
| `meta-skill` | loads OK | none | ✅ clean |
| `meta-agent` | loads OK | none | ✅ clean |
| `meta-commands` | FAILS to load | lines 51, 128, 129, 131 | ❌ broken |

### Root cause (meta-commands only)

`meta-commands/SKILL.md` documents the dynamic-injection feature by writing the
syntax as **live, unescaped tokens** in its prose. At load time the harness scans
the body, matches the inline token on line 131 as a real injection, and runs the
command inside it:

```text
git: '...' is not a git command
Shell command failed for pattern "!`git ...`"
```

`...` is not a git subcommand, so the command errors and the entire skill load
aborts — the skill that *teaches* the injection feature is unloadable because of
that feature. Four raw-source tokens trigger this (the offending substrings):

```text
L51   dynamic !`cmd`` + `@file` injection            (inline bang+backtick)
L128  Inline  !`cmd`  injects ...                     (inline bang+backtick)
L129  a ```! fenced block does the same ...           (fenced single-bang info string)
L131  ... for a  !`git ...`  injection). See          (inline bang+backtick — the one that errors)
```

### Fix

Neutralize the literal tokens so the loader can't evaluate them, without changing
what the syntax *means* to a reader. Rule: in raw source, never let a bang sit
immediately before a backtick, and never begin a fenced block with a single-bang
info string. Surgical rewrites (meaning preserved, "bang" spelled out):

```text
L51   → dynamic bang-backtick command injection and @file injection
L128  → Inline bang-backtick injection (a bang immediately before a backtick-quoted command) runs a shell command and injects its output ...
L129  → ... a fenced block whose info string is a single bang does the same for multi-line ...   (drop the literal token)
L131  → ... for a bang-backtick git injection). See ...
```

Alternative (also valid, and leaner per meta-commands' own "keep bodies lean"
rule): delete the inline examples from the body and point readers to
`references/command-format.md`, which already holds the full injection detail.

### Validation

- Re-invoke `meta-commands` via the Skill tool → must launch without a shell error.
- `grep -nF '!\`' .claude/skills/meta-commands/SKILL.md` → no matches.
- `grep -nF '\`\`\`!' .claude/skills/meta-commands/SKILL.md` → no matches.

### Scope note

This fix touches only `meta-commands/SKILL.md` and is independent of the grilling
migration. Apply it as its own commit; it does not block the grilling work.
