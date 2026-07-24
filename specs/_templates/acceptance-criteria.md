# Acceptance Criteria: <task name>

> The definition of "done" for [spec.md](./spec.md). Every criterion is observable and testable, and
> every task in tasks.md should map to at least one criterion here.

## Acceptance Criteria

<numbered, testable criteria. Give each a stable id (AC1, AC2 …) so tasks.md can reference it. Each
must be checkable by a human or a command — no "feels fast", no "works well".>

- **AC1** — <specific, measurable outcome; what is true and how you'd observe it>
- **AC2** — <…>
- **AC3** — <…>

## Validation Commands

Validation logic lives in committed check scripts — one script per criterion under
`specs/<name>/checks/` (PEP 723 scripts, like hooks), or pytest files under `tests/`. Never inline
a multi-line program in this file. Each bullet below is exactly ONE line: a stage tag, the script
invocation, and the criterion it verifies.

The stage tag names the earliest point the command can pass. Reviewers run only the commands whose
stage has been reached and record later-stage commands as deferred — deferred is not a failure:

- `[plan-time]` — runnable against the spec folder alone, before any build.
- `[child-build-time]` — runnable once the implementing build (for an epic: the relevant child's
  build) has produced its changes.
- `[post-merge]` — runnable only after dependent work has merged to `main`.

<one bullet per criterion. Use `uv run --script …` for checks/ scripts, `uv run pytest …` for tests.>

- `[plan-time]` `uv run --script specs/<name>/checks/ac1_<slug>.py` — verifies AC1. <what a pass looks like>
- `[child-build-time]` `uv run pytest tests/<path> -k <ac2-marker>` — verifies AC2.
- `[post-merge]` `uv run --script specs/<name>/checks/ac3_<slug>.py` — verifies AC3.
