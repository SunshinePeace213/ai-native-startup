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

- **What diverged:** The dry run's Design-Lead gate needed a second, targeted fix pass: the SOP routes blocking findings back once, but the route-back fix itself introduced a new blocker (the copy-deck's `Email *` label contradicting the package's at-least-one contact rule and PRD US-1).
  - **What forced it:** A fix pass can introduce defects the original review never saw; leaving a package that literally violates the PRD was not an option.
  - **The call made:** One surgical follow-up fix (drop the asterisk) plus a confirmation re-review, then approval. Recorded as a department lesson in `cpo-lessons.md` (re-verify contract lines a fix touches; budget re-reviews per finding generation).
  - **Spec impact:** none — the once-routed rule governs the original finding set; the follow-up addressed a regression, not a surviving finding.
- **What diverged:** Fixture stage commits carry no `Refs #35` footer while build checkpoint commits do.
  - **What forced it:** The fixture trail contract (`commit=current branch + recorded SHA`, no engagement issue exists) is itself under test in the dry run; stamping the build issue onto SOP-governed commits would falsify the trail being validated.
  - **The call made:** SOP commits follow the fixture contract; lead checkpoint commits (specs/, pushes) keep `Refs #35`.
  - **Spec impact:** none.

- **What diverged (R1 fix pass):** validate.sh's new section-scoped assertions match `## <heading>` by prefix, not exact equality (so `## Return to the caller (short)` resolves under the canonical name `## Return to the caller`).
  - **What forced it:** The shipped prd-review heading carries a `(short)` qualifier the canonical scoping name omits; exact matching would fail on green files.
  - **The call made:** Prefix matching per the fixer's judgment; assertion strength unchanged (fragments still asserted inside the resolved section).
  - **Spec impact:** none.
- **What diverged (R1 fix pass):** the wireframe desktop-reflow notes were added to EVERY per-section annotation including the shared nav/footer comments, not only page-specific content sections.
  - **What forced it:** The wireframe header claim ("noted per section") is unqualified; a partial reading would leave the claim half-true.
  - **The call made:** One concise `(desktop: …)` clause per section tag, one-to-one, in all four flagged pages.
  - **Spec impact:** none.

- **What diverged (R2 over-cap, round 3):** the round-3 fix delta is Codex-authored (`gpt-5.6-sol`), not Claude-authored — validate.sh's AC12/AC4/AC9 redesign plus the cpo-prd.md canonical-line dedupe.
  - **What forced it:** Round 2 dispositioned F8/F9 as not fixed — repeat root-cause failures after the opus round-1 fix; the root-cause rule reassigns those across providers, and the redesign (fail-closed snapshot engine, exact/unique/ordered assertion parsing) is exactly the algorithmic class stamped for sol.
  - **The call made:** Over-cap gate exit (a) — the single permitted redesigned round 3 — taken under the user's standing instruction to fix the Codex findings and finish the workflow; the redesign boundaries were consulted and recorded in `## Locked Boundaries` before authoring, and an internal Claude `opus` review of the Codex delta returned clean (2 non-blocking advisories) before the round-3 delta review.
  - **Spec impact:** none beyond the recorded Locked Boundaries refinements; if round 3 is still changes-requested the build stops for an explicit user decision.

## Fold-Forward

- `quick_validate.py` vs Claude Code-only frontmatter keys (`autoInvoke`, `disable-model-invocation`): consider a follow-up chore aligning the packaging validator or the meta-skills docs on which validator gates project-internal skills.
