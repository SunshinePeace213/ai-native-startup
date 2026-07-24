# Development Log

Loads every session. Cross-plan lessons only, one line each:
`YYYY-MM-DD · <plan> · <lesson>`. Per-plan process (phases, hand-offs,
deviations, fixes, lessons) belongs in that plan's `implementation-notes.md`,
not here.

Appended by the `/harness-layer:harness-build` and `/harness-layer:harness-review`
memory steps. Cap ≈40 lines — at the cap, distill generalizable lessons into
their proper rule file and delete their entries.

## Lessons

- 2026-07-24 · soriza-design-kb-seed · The Codex review sandbox has no network: validation commands that resolve deps at run time (`uv run --with pyyaml`) sit unexecuted and block approval — pass `-c sandbox_workspace_write.network_access=true` to `codex exec` for such rounds (documented in `ai-docs/openai/codex/config-advanced.md`).
