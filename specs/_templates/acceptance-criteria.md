# Acceptance Criteria: <task name>

> The definition of "done" for [spec.md](./spec.md). Every criterion is observable and
> testable, and every task in tasks.md maps to at least one criterion here.

## Acceptance Criteria

<!-- Numbered criteria, each with a stable id (AC1, AC2 …) that tasks.md references.
     Each states what is true and how you would observe it — no "works well", no "feels
     fast". Group related criteria under "### <group>" headings once there are more than
     a handful. -->

- **AC1** — <specific, measurable outcome; what is true and how you'd observe it>
- **AC2** — <…>
- **AC3** — <…>

## Validation Commands

<!-- One or more commands per criterion, run from the repo root. Prefer the project's own
     test suite or a checked-in validator over a bespoke script; a script written only for
     this plan lives in `specs/<name>/checks/` and exits 0 on pass. Prefix a check that
     cannot run unattended with `manual:` and say where its output is recorded.

     Falsifiability: each command must FAIL if the change is reverted. A command that
     passes on today's tree and on the untouched tree proves nothing — replace it. -->

### AC1 — <what it proves>

- `<command>` — pass: <the observable pass condition>

### AC2 — <what it proves>

- `<command>` — pass: <…>
- `manual: <command or procedure>` — pass: <…>; output recorded in implementation-notes.md
