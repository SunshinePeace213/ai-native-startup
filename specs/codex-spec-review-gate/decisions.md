# Decisions: Codex Spec-Review Gate for plan-w-team

## Summary

Add a Codex verification gate to the `plan-w-team` workflow. After Claude drafts
`plan.md` + `decisions.md` (and before the final report), an automated loop hands the
spec to Codex for review, Claude applies the resulting fixes, and the cycle repeats
until Codex approves or a 2-round cap is reached. The reviewer is delivered as a
**Codex Skill** (`spec-review`) — not a custom prompt, which OpenAI has deprecated in
favor of skills. The skill lives repo-level at `.agents/skills/spec-review/` (version
controlled, team-shared). Codex writes its review into a dedicated, **Codex-owned**
`## Codex Findings` section of `plan.md` that Claude scaffolds empty and never edits;
Claude applies any warranted changes only to the rest of the plan. The loop is
automated via `codex exec` invoking the skill explicitly. The gate runs on every
`plan-w-team` run but skips gracefully (with a recorded note) when the Codex CLI is
unavailable.

## Resolved Decisions

### 1. Reviewer artifact: Codex Skill, not a custom prompt

- **Question:** Build a Codex custom prompt (per the original ask) or a Codex Skill?
- **Answer:** A Codex **Skill** (`SKILL.md` with `name` + `description` frontmatter).
- **Rationale:** OpenAI's docs (developers.openai.com/codex/skills) deprecate custom
  prompts (`/prompts:name`, TUI-only) in favor of Skills, which support implicit
  invocation and repository sharing. The installed Codex (v0.142.3) ships a
  `skill-creator` system skill confirming the Skills model is live locally.

### 2. Invocation: automated via `codex exec`

- **Question:** How does the loop invoke Codex each round?
- **Answer:** `plan-w-team` runs `codex exec` non-interactively each round, explicitly
  invoking the `spec-review` skill on the spec path. Hands-free loop.
- **Rationale:** Custom-prompt slash commands are TUI-only; the repo is already
  `trust_level = "trusted"` in `~/.codex/config.toml`, so non-interactive, write-capable
  Codex runs are feasible. Skills are discoverable to `codex exec`.

### 3. Gate timing + fallback: always-on, graceful skip

- **Question:** Run every time? What if Codex CLI is missing/unauthenticated?
- **Answer:** Run the gate on every `plan-w-team` run, inserted after `plan.md`/
  `decisions.md` are drafted and before the final report. If the Codex CLI is
  unavailable, skip the loop, warn (point to `/codex:setup`), record the skip in
  `decisions.md`, and finish planning normally.
- **Rationale:** Verification should be the default, but a missing local tool must not
  block producing a plan. Fail loud via the recorded skip note.

### 4. Findings location + ownership: Codex-owned section in plan.md

- **Question:** Where does Codex write findings, and who may edit it?
- **Answer:** A `## Codex Findings` section inside `plan.md`. Claude scaffolds it empty
  (`_Pending Codex review._`) and is **never** permitted to edit it. Only Codex writes
  there; Claude applies plan changes to the rest of the document.
- **Rationale:** Partitioning the file by writer prevents Claude and Codex from
  colliding on the same region while keeping the review attached to the spec.

### 5. Findings format + verdict contract

- **Question:** How does the section track rounds and signal approval?
- **Answer:** Codex appends a per-round block headed exactly
  `### Round N — Verdict: approved` or `### Round N — Verdict: changes-requested`,
  listing what it found that round with a concrete recommendation per finding. Claude
  greps the latest `Verdict:` line to decide loop-vs-stop.
- **Rationale:** A machine-greppable verdict line gives Claude a deterministic loop
  signal; per-round blocks preserve the convergence trail.

### 6. Loop control: max 2 Codex rounds, then proceed

- **Question:** How many rounds, and what on non-approval?
- **Answer:** Cadence is Claude draft → Codex Round 1 → (if approved, done) → Claude fix
  → Codex Round 2 → Claude final pass. **Max 2 Codex rounds.** If Round 2 still requests
  changes, Claude applies the findings as a best-effort final pass and proceeds anyway,
  recording "proceeded without full Codex approval after 2 rounds" + the outstanding
  findings in `decisions.md`.
- **Rationale:** Two rounds converge most specs without risking an unbounded loop; the
  recorded non-approval keeps the outcome honest.

### 7. Skill location: repo-level `.agents/skills/`

- **Question:** Repo-level, user-level, or both?
- **Answer:** Repo-level `.agents/skills/spec-review/SKILL.md`, version controlled.
- **Rationale:** Travels with the repo, shared with the team, coupled to `plan-w-team`
  (also a repo artifact). Codex scans from cwd up to repo root.

### 8. Authoring quality: meta-skill-grade, Codex-native conventions

- **Question:** How is the skill authored?
- **Answer:** Authored to meta-skill-grade quality following Codex's native
  `skill-creator` conventions (`init_skill.py`/`quick_validate.py`, tight triggering
  `description`, concise imperative body, progressive disclosure).
- **Rationale:** Matches the team's skill-authoring bar while respecting Codex's own
  skill format and validation tooling.

### 9. Team: general-purpose builders

- **Question:** Who builds it?
- **Answer:** `general-purpose` agents — `.claude/agents/team/*.md` does not exist.
- **Rationale:** No specialized team agents are defined in this repo.

## Assumptions

- **A1 — Discovery path verified at build time.** Public docs say repo-level
  `.agents/skills`; the installed v0.142.3 `skill-creator` references
  `$CODEX_HOME/skills` (`~/.codex/skills`). The foundation task empirically determines
  the path Codex 0.142.3 actually scans for repo-level skills. If repo-level discovery
  is unsupported, fall back to a repo-canonical copy + a setup step that installs it to
  the user-level path — and flag this loudly rather than shipping an undiscoverable skill.
- **A2 — `codex exec` write flag.** The exact flag enabling file writes in this trusted
  repo (e.g. `--full-auto` or a `sandbox_mode=workspace-write` override) is confirmed in
  the foundation task; the loop uses the minimal flag that lets Codex edit only `plan.md`.
- **A3 — Explicit skill invocation in `codex exec`.** The loop references the skill
  explicitly (e.g. "use the `spec-review` skill on `<path>`" / `$spec-review`); the
  foundation task confirms the syntax that reliably triggers it non-interactively.
- **A4 — Skill name** is `spec-review`; the Codex Findings round-header and verdict
  strings are fixed exactly as in Decision 5 so Claude's grep is stable.
- **A5 — Finding bar.** Codex reports only blocking spec issues (missing/contradictory
  requirements, infeasible or mis-ordered steps, untestable acceptance criteria,
  security/data risks, scope drift) — not style nits — and approves when none remain.
- **A6 — Claude may reject findings.** When Claude declines a Codex finding, it records
  the finding + its rationale in `decisions.md` rather than silently ignoring it.
- **A7 — Removals use `mv … ~/.Trash/`**, never `rm -rf` (per AGENTS.md). Pre-existing
  state such as the `.skill-lock.json` in the repo root is inspected, not deleted.

## Open Questions / Out of Scope

- **Non-goal:** Changing `/build` or adding a Codex review of the _implemented code_
  during the build phase. This gate reviews the _planning spec_ only.
- **Non-goal:** User-level or machine-wide installation of the skill (repo-level chosen).
- **Non-goal:** A third Codex round or human-in-the-loop approval beyond the 2-round cap.
- **Deferred:** Tuning the finding bar / round cap after real usage; revisit if specs
  routinely fail to converge in 2 rounds.
