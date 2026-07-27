# Development Log

Loads every session. Cross-plan lessons only, one line each:
`YYYY-MM-DD · <plan> · <lesson>`. Per-plan process (phases, hand-offs,
deviations, fixes, lessons) belongs in that plan's `implementation-notes.md`,
not here.

Appended by the `/harness-layer:harness-build` and `/harness-layer:harness-review`
memory steps. Cap ≈40 lines — at the cap, distill generalizable lessons into
their proper rule file and delete their entries.

## Lessons

- 2026-07-27 · codex-hooks-sync · Codex loads `.codex/` from the main repo root, so a worktree's own
  layer never runs — probe Codex from a scratch repo, and treat an untrusted project path as having
  no hook layer.
- 2026-07-27 · codex-hooks-sync · A fail-open hook can only be proven by a positively observed block;
  a green suite pins registration, never execution.
