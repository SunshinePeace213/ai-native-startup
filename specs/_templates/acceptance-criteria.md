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

One executable script per criterion under [checks/](./checks/) proves it. Each script is
self-contained, runs from the repo root (`uv run` for Python, `bun` for JS/TS, bash otherwise),
and exits 0 on pass — no long inline scripts here, only invocations.

| Command | Verifies | Pass looks like |
| --- | --- | --- |
| `<bash specs/<name>/checks/ac1-<slug>.sh>` | AC1 | <observable pass condition> |
| `<uv run specs/<name>/checks/ac2-<slug>.py>` | AC2 | <…> |
