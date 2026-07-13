# Implementation Notes: Unknowns-Aware Pipeline

> Running deviation log for [spec.md](./spec.md), kept by `/harness-layer:harness-build` — created
> from the new template this build ships (dogfooding it one build early).

## Deviations

- **What diverged:** tasks.md assigns six builder subagents; the lead implemented every task directly in-session.
  - **What forced it:** every Agent tool call was denied by the session's permission layer — no subagents available.
  - **The call made:** implement in ID order with the task board tracking status; keep the independent Codex cross-model gate as primary verification.
  - **Spec impact:** none — no locked decision or acceptance criterion touched; the tasks' content contract was followed exactly.
- **What diverged:** two files outside the strict task edits gained one-line changes — `specs/_templates/spec.md` (References fence) and `.agents/skills/spec-review/SKILL.md` (example fence) now carry a `text` language tag.
  - **What forced it:** the markdown auto-format hook blocks edits to files with pre-existing MD040 bare-fence errors; the harness contract says fix exit-2 diagnostics.
  - **The call made:** minimal `text` tag on the flagged fences only.
  - **Spec impact:** none.

## Fold-Forward

- Grant the build lead an Agent-tool allowlist entry (or record the expected permission prompt) so future builds can actually deploy the builders the plan stamps.
