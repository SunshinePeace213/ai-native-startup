# Shipped Plans

What has landed on `main`, newest first. Start here to find out whether a feature
exists, which plan built it, and what it decided — then read that plan's
`summary.md` before its `spec.md`, which is much longer and states intent rather
than outcome.

`/harness-layer:harness-review` appends a row and writes `summary.md` when it
approves a plan, so a plan that never shipped never appears here.

| Plan | PR | Merged | What shipped | Summary |
| --- | --- | --- | --- | --- |
| [wiki-layer](./wiki-layer/) | #89 | 2026-08-07 | LLM-maintained synthesis wiki over the ai-docs mirrors | [summary](./wiki-layer/summary.md) |
| [self-managing-memory-kb](./self-managing-memory-kb/) | #69 | 2026-07-27 | Trimmed and restructured the always-loaded rule set | — |
| [codex-hooks-sync](./codex-hooks-sync/) | #63 | 2026-07-27 | Mirrored the Claude hook surface into Codex | — |
| [harness-build-split](./harness-build-split/) | #38 | 2026-07-21 | Split `harness-build` into build + review commands | — |
| [unknowns-aware-pipeline](./unknowns-aware-pipeline/) | #31 | 2026-07-13 | Blindspot pass, deviations log, ship brief | — |
| [sensitive-file-guard](./sensitive-file-guard/) | #28 | 2026-07-12 | Denied agent access to secret-bearing files | — |
| [destructive-command-guard](./destructive-command-guard/) | #27 | 2026-07-12 | Pre-execution hook blocking destructive commands | — |
| [per-feature-harness-restructure](./per-feature-harness-restructure/) | #24 | 2026-07-12 | Restructured hooks, tests, and the build workflow per feature | — |
| [security-scan-hook](./security-scan-hook/) | #22 | 2026-07-12 | Security-scan hook family for agent-written files | — |
| [auto-format-hooks](./auto-format-hooks/) | #20 | 2026-07-11 | Auto-format hooks with worktree lifecycle install | — |

Rows above predate `summary.md`; their plan folders hold the full spec. Every plan
approved from now on carries one.
