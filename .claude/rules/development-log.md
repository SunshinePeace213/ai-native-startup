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
- 2026-07-25 · harness-self-improvement-p1 · A hook that picks its target by newest mtime across roots breaks under concurrent sessions — resolve the root from the hook's stdin `cwd` (git toplevel, then single-root fallbacks only) and scan just that root; regression-test both directions (foreign root never blocks, foreign root never masks).
- 2026-07-25 · harness-self-improvement-p1 · Substring membership is not a contract pin — a commented (`# model: fable`) or prefixed (`x-model:`) key keeps it green; pin whole frontmatter entries line-anchored and ship the mutation replay as a test.
- 2026-07-25 · harness-self-improvement-p1 · Codex's comment-accuracy lens blocks false rationale even when every assertion is right — ground each docstring's mechanism claim in the KB before shipping (skill resolution is directory-keyed; frontmatter `name:` is declared metadata).
