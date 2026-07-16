# Implementation Notes: c-suite CPO department

> Running deviation log for [spec.md](./spec.md), kept by `/harness-layer:harness-build` — created
> from this template at implement start, folded by the lead at each checkpoint commit.

## Deviations

- **What diverged:** AC7's literal validation command (`uv run .claude/skills/meta-skills/scripts/quick_validate.py <three paths>`) cannot pass: `quick_validate.py` is the packaging validator with allow-list `{name, description, license, allowed-tools, metadata, compatibility}` — it rejects `autoInvoke` (and would equally reject the legacy `disable-model-invocation`), and accepts only one path argument. The skills were built with `autoInvoke: false` per the locked "knowledge skills never auto-fire" decision and pass the meta-skills authoring validator `validate.py` (non-fatal WARN on the unknown key).
  - **What forced it:** No invocation-blocking frontmatter exists that passes quick_validate's allow-list — the AC7 command is internally contradictory with the locked decision and with AC7's own frontmatter clause.
  - **The call made:** Kept `autoInvoke: false` (locked decision + AC2/AC7 frontmatter clause); verified with `validate.py` instead. AC7's criterion text ("pass the meta-skills validator and their frontmatter blocks auto-invocation") is met under that reading.
  - **Spec impact:** acceptance-criterion validation command touched → user gate (AskUserQuestion) queued before `validate.sh` (task validate-all) encodes the AC7 check.
- **What diverged:** tasks.md instructs builders to flip their own board status via TaskUpdate; the Task* tools are unavailable to spawned subagents in this harness.
  - **What forced it:** ToolSearch inside subagent sessions resolves no Task* tools.
  - **The call made:** The lead flips board statuses from builder hand-offs; briefs after wave 1 drop the TaskUpdate instruction.
  - **Spec impact:** none.

- **What diverged:** `prd-review` omits spec-review's conditional `## KB grounding` section.
  - **What forced it:** That section verifies harness-behavior claims against `ai-docs/` — spec-review-specific; task 4's enumerated mechanics exclude it and the PRD review's inputs are product documents (prd.md, requirements.md, cpo-prd-standard).
  - **The call made:** Mirror every enumerated mechanic one-to-one; replace spec-only blocking types with the PRD-specific criteria.
  - **Spec impact:** none.
- **What diverged:** AC8's literal validation command (`uv run .claude/skills/meta-agent/scripts/validate_agent.py .claude/agents/cpo/*.md && ...`) fails on green files: the script needs `--with pyyaml` (its documented usage) and accepts exactly one path per call, rejecting the glob.
  - **What forced it:** `validate_agent.py`'s own arg guard (`len(argv) != 2`) and missing pyyaml in the project env.
  - **The call made:** Agents verified with the script's real contract — a per-file loop `uv run --with pyyaml python .claude/skills/meta-agent/scripts/validate_agent.py <path>`; all five pass. `validate.sh` must use the loop form.
  - **Spec impact:** acceptance-criterion validation command touched (mechanical invocation fix, checks unchanged) → bundled into the user gate queued before validate.sh.

- **What diverged:** The smoke check could not positively confirm `skills:` preloading end to end: on the `claude --agent cpo-ux-researcher -p` headless surface the persona activated (tools restricted correctly) but no skill content was in its context, and the true Agent-tool delegation path was unreachable from the probe's nested session (custom cpo-* agents not exposed there).
  - **What forced it:** `--agent` runs the persona as the main-session agent — the KB documents `skills:` preloading for subagent startup, a different mode; no probe surface for real delegation existed inside the smoke-check session.
  - **The call made:** `autoInvoke: false` is confirmed honored (no auto-fire; skills loadable by name), so no field fallback was triggered. The delegation-brief channel (personas Read the brief-carried SKILL.md first) is the plan's designed complete fallback and every stage-command brief carries it; the dry run observes persona knowledge in practice.
  - **Spec impact:** none — AC2/AC8's required coverage is met; preload-in-delegation remains unverified-by-probe, noted for the first real engagement.

## Fold-Forward

- `quick_validate.py` vs Claude Code-only frontmatter keys (`autoInvoke`, `disable-model-invocation`): consider a follow-up chore aligning the packaging validator or the meta-skills docs on which validator gates project-internal skills.
