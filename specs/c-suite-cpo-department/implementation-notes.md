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

## Fold-Forward

- `quick_validate.py` vs Claude Code-only frontmatter keys (`autoInvoke`, `disable-model-invocation`): consider a follow-up chore aligning the packaging validator or the meta-skills docs on which validator gates project-internal skills.
