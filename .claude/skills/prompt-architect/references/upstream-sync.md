# Upstream sync record

`/prompt-architect` forks the executable apparatus (`agents/`, `scripts/`, `eval-viewer/`, `assets/eval_review.html`, `references/schemas.md`) from Anthropic's official `/skill-creator`.

## Forked from

- **Repo:** https://github.com/anthropics/skills
- **Path:** `skills/skill-creator/`
- **Commit:** `690f15cac7f7b4c055c5ab109c79ed9259934081`
- **Date:** 2026-05-27

## What was modified after the fork

The ported scripts were modified to handle three artifact types (skill, command, subagent) instead of just skills:

- `scripts/run_eval.py` — added `--artifact-type {skill,command,subagent}` flag *(later retired — see divergence below)*
- `scripts/run_loop.py` — gates description optimization to skills/commands *(later retired — see divergence below)*
- `scripts/aggregate_benchmark.py` — generalized `with_skill`/`without_skill` labels to `with_<type>`/`without_<type>`
- `scripts/quick_validate.py` — extended to validate all three artifact-type structures
- `scripts/package_skill.py` — restricted to skill-only, errors clearly otherwise
- `scripts/utils.py` — `parse_skill_md` accepts command and subagent files too (they have similar frontmatter)

`eval-viewer/` is artifact-type-agnostic and unchanged.

## Post-fork divergence — 2026-06-03 (workflows migration)

Phases 5–6 were re-architected onto native Claude Code **dynamic workflows**, diverging structurally from upstream skill-creator:

- **Retired** `scripts/run_eval.py`, `scripts/run_loop.py`, `scripts/improve_description.py`, `scripts/generate_report.py` — the `claude -p` subprocess apparatus. Reason: `claude -p` bills as separate invocations, and prose "spawn subagents" instructions under-fire on Opus 4.8 (it spawns fewer subagents by default).
- **Added** `.claude/workflows/artifact-eval.js` (Phase 5 eval loop) and `.claude/workflows/description-optimize.js` (Phase 6 trigger optimization). These spawn agents deterministically and use the in-session token budget rather than a separate CLI process.
- **Renamed + upgraded** the eval agents to the `meta-skill-*` series with full subagent frontmatter (least-privilege tools, deliberate `effort`, the local body skeleton): `agents/grader.md → meta-skill-grader.md`, `comparator.md → meta-skill-comparator.md`, `analyzer.md → meta-skill-analyzer.md`. They are no longer artifact-type-agnostic copies of upstream.
- **Kept** (still close to upstream): `aggregate_benchmark.py`, `quick_validate.py`, `package_skill.py`, `utils.py`, `eval-viewer/`, `assets/eval_review.html`, `references/schemas.md`.

Implication for future syncs: do **not** pull upstream's `agents/*.md` or the four retired scripts back in — Phases 5–6 are now workflow-native and intentionally diverged.

## Drift audit cadence

Re-run `gh api repos/anthropics/skills/commits/main --jq '.sha'` and diff against the SHA above every quarter. Pull in upstream improvements selectively — be conservative about anything that breaks our `--artifact-type` parameterization.

## What is NOT forked from skill-creator (prompt-architect's unique IP)

Everything in:

- `references/4-8-principles.md`
- `references/anti-patterns.md`
- `references/command-template.md`
- `references/composition-rules.md`
- `references/decision-tree.md`
- `references/hooks.md`
- `references/skill-categories.md`
- `references/skill-template.md`
- `references/subagent-template.md`
- `references/thariq-principles.md`
- `assets/examples/`
- `SKILL.md` (the 7-checkpoint workflow + artifact-type decision)

These are local IP. Do not overwrite them with upstream content.
