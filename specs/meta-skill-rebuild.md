# Plan: Rebuild `meta-skill` as the team standard for creating Agent Skills

## Task Description

Retire the current, bloated meta-skill and recreate a clean, maintainable skill named **`meta-skill`** that becomes the team's single canonical standard for authoring Claude Code Agent Skills. The current skill (`.claude/skills/meta-skill/SKILL.md`, frontmatter `name: creating-new-skills`) is a 435-line generic restatement of skill-101 material plus 1,078 lines of scraped docs — verbose, partly stale, and not a tight "standard."

The new `meta-skill` must encode, with progressive disclosure:
1. A **complete frontmatter reference** — every SKILL.md frontmatter field, its constraints, what it controls, and when an authoring agent should set it (the user's explicit must-have).
2. **Structure & progressive-disclosure rules** distilled from the official Claude Code skills docs.
3. **Authoring principles** merged from Thariq's tips and the Opus 4.8 prompting guidance.
4. A **test-and-iterate workflow modeled on `skill-creator`**, enhanced to drop deprecated machinery and stay lean.

Knowledge references are authored **fresh** from the live docs (per decision Q3), not salvaged from `prompt-architect`. `prompt-architect` is being **retired in the future**; `meta-skill` therefore becomes the **primary, standalone** skill-creation skill and must not depend on `prompt-architect` at runtime.

**Task type:** refactor (cleanup + recreate). **Complexity:** complex.

## Objective

A working `.claude/skills/meta-skill/` skill that:
- Triggers reliably on skill-creation requests ("create a new skill…", "use your meta skill to…", "turn this into a skill").
- Has a `SKILL.md` body under 500 lines (target ~200–300) that reads as a standard + workflow, not a tutorial.
- Documents **all** frontmatter fields in a dedicated reference.
- Carries a `skill-creator`-style test/iterate loop using only the pure-compute apparatus (validate, benchmark, viewer, grader), with deprecated `claude -p` subprocess scripts removed.
- Replaces the old `creating-new-skills` skill, whose directory is moved to `~/.Trash/` (per AGENTS.md safe-delete rule).

## Problem Statement

`prompt-architect` (6,152 lines across SKILL.md + 13 references + scripts + workflows) grew "extremely large and hard to maintain." It also brands itself "a meta-skill" and auto-triggers on "create a skill for X," so any new skill-creation skill collides with it. The team wants to **stop maintaining that sprawl** and converge on one clean standard. Meanwhile the existing `meta-skill` is generic and not authoritative — it doesn't document the current 16-field frontmatter surface, predates Opus 4.8 guidance, and ships stale scraped docs. There is no single, lean, trustworthy "this is how we build skills" artifact.

## Solution Approach

Build a new `meta-skill` whose value is **standards + a guided workflow**, kept small through progressive disclosure:

- **Lean `SKILL.md` body** = the workflow (intent → interview → draft → test → iterate → optional description-optimize → package) plus pointers into references. No long prose that restates the obvious (Thariq tip 1).
- **`references/` authored fresh** from the four live sources studied during planning:
  - `code.claude.com/docs/en/skills` (official: 16 frontmatter fields, structure, 1,536-char listing cap, `${CLAUDE_SKILL_DIR}`, invocation control).
  - `shanraisshan/.../best-practice/claude-skills.md` (field-by-field frontmatter usage).
  - `shanraisshan/.../tips/claude-thariq-tips-17-mar-26.md` (9 authoring tips).
  - `platform.claude.com/.../prompting-claude-opus-4-8` (4.8 deltas: `effort` as the dominant lever, literalness, conservative tool/subagent use, no `$100 tip`/"think harder" prose, drop forced progress-update scaffolding, pushy descriptions to counter under-triggering).
- **Testing apparatus ported from `skill-creator`** (which is skills-only already, so no parameterization needed), keeping the pure-compute pieces and the grader rubric; **dropping** the retired `claude -p` subprocess scripts. SKILL.md references the apparatus so it loads only during the test phase.
- **Clean cutover:** old `meta-skill/` → `~/.Trash/`; new `meta-skill/` written at the same path with `name: meta-skill`.

**Known transient overlap (flagged, not fixed here):** while `prompt-architect` still exists, both it and `meta-skill` can match "create a skill." The user asked not to refactor `prompt-architect`. Mitigation: give `meta-skill` a strong, specific, front-loaded description; since `prompt-architect` is slated for retirement, the collision is temporary. Optional later step: narrow `prompt-architect`'s description (out of scope for this plan).

## Relevant Files

Use these files to complete the task:

- `.claude/skills/meta-skill/SKILL.md` — **current skill to retire** (frontmatter `name: creating-new-skills`); read for any reusable framing, then move the whole directory to `~/.Trash/`.
- `.claude/skills/meta-skill/docs/*.md` — 1,078 lines of scraped docs; **do not carry over** (drop with the Trash move). Live docs + fresh references replace them.
- `.claude/skills/prompt-architect/SKILL.md` — the skill being retired; read for structure ideas only. **Do not** copy its references (Q3 = author fresh).
- `~/.claude/plugins/cache/claude-plugins-official/skill-creator/unknown/skills/skill-creator/` — **source of the test/iterate apparatus** to port:
  - `SKILL.md` — the loop this skill's workflow should follow.
  - `scripts/aggregate_benchmark.py`, `scripts/quick_validate.py`, `scripts/package_skill.py`, `scripts/utils.py`, `scripts/__init__.py` — **keep** (pure-compute, stdlib).
  - `scripts/run_eval.py`, `scripts/run_loop.py`, `scripts/improve_description.py`, `scripts/generate_report.py` — **drop** (deprecated `claude -p` subprocess apparatus — the "enhancement" fix).
  - `eval-viewer/generate_review.py`, `eval-viewer/viewer.html` — **keep**.
  - `agents/grader.md` — **keep** (grading rubric); `agents/analyzer.md`, `agents/comparator.md` — keep only if the workflow uses them.
  - `references/schemas.md` — **keep** (eval/grading/benchmark JSON shapes).
  - `assets/eval_review.html` — keep only if a description-optimization review step is included.
- `AGENTS.md` — tooling rules: `uv` for Python, `bun` for JS, full-width rich panels, **safe-delete via `mv … ~/.Trash/`** (governs the cutover).

### New Files
- `.claude/skills/meta-skill/SKILL.md` — new lean workflow body + frontmatter.
- `.claude/skills/meta-skill/references/frontmatter.md` — **centerpiece**: every frontmatter field documented.
- `.claude/skills/meta-skill/references/structure.md` — directory layout, progressive disclosure, size rules, MCP tool naming, `${CLAUDE_SKILL_DIR}`.
- `.claude/skills/meta-skill/references/authoring-principles.md` — Thariq's 9 tips + Opus 4.8 deltas, merged and de-duplicated.
- `.claude/skills/meta-skill/references/anti-patterns.md` — older-model holdovers + bad-vs-good descriptions + a pre-ship review checklist.
- `.claude/skills/meta-skill/references/schemas.md` — ported from skill-creator (eval/grading/benchmark JSON).
- `.claude/skills/meta-skill/scripts/` — ported pure-compute scripts (`quick_validate.py`, `aggregate_benchmark.py`, `package_skill.py`, `utils.py`, `__init__.py`).
- `.claude/skills/meta-skill/eval-viewer/` — ported `generate_review.py` + `viewer.html`.
- `.claude/skills/meta-skill/agents/grader.md` — ported grading rubric.
- `.claude/skills/meta-skill/assets/eval_review.html` — optional, only if description-optimization step is kept.

## Implementation Phases

### Phase 1: Foundation
Cutover and scaffold. Move the old `meta-skill/` (incl. `creating-new-skills` SKILL.md and scraped `docs/`) to `~/.Trash/`. Create the new directory skeleton (`references/`, `scripts/`, `eval-viewer/`, `agents/`, optional `assets/`). Author the four **fresh knowledge references** from the live docs, and port + prune the **apparatus** from skill-creator. These two streams are independent and run in parallel.

### Phase 2: Core Implementation
Write the lean `SKILL.md`: frontmatter (`name: meta-skill`, pushy front-loaded description within the 1,536-char combined cap), then the workflow body (intent → interview/research → draft → test-and-iterate → optional description-optimize → package), with clear "read this when…" pointers into the references and apparatus. Keep body < 500 lines.

### Phase 3: Integration & Polish
Validate the artifact: run the ported `quick_validate` on the new SKILL.md, confirm body < 500 lines and references are one level deep, confirm description+when_to_use ≤ 1,536 chars, and smoke-test triggering with 2–3 realistic prompts. Verify the old skill is gone from `.claude/skills/` and present in `~/.Trash/`. Produce a short report of what passed.

## Team Orchestration

- You operate as the team lead and orchestrate the team to execute the plan.
- You're responsible for deploying the right team members with the right context to execute the plan.
- IMPORTANT: You NEVER operate directly on the codebase. You use `Task` and `Task*` tools to deploy team members to do the building, validating, and testing.
  - Your job is high-level direction, not building.
  - Validate all work is on track and the team is converging on the plan.
  - Coordinate via the Task* tools.
- Take note of the session id of each team member so you can resume them.

> Note: `.claude/agents/team/` does not exist in this repo, so all team members use the `general-purpose` agent type.

### Team Members

- Builder
  - Name: `builder-knowledge`
  - Role: Authors the four fresh knowledge references (`frontmatter.md`, `structure.md`, `authoring-principles.md`, `anti-patterns.md`) from the live docs. Owns accuracy of every frontmatter field and the 4.8/Thariq distillation.
  - Agent Type: `general-purpose`
  - Resume: true
- Builder
  - Name: `builder-core`
  - Role: Performs the cutover (Trash old, scaffold new), ports + prunes the skill-creator apparatus, and writes the lean `SKILL.md` once references and apparatus exist.
  - Agent Type: `general-purpose`
  - Resume: true
- Validator
  - Name: `validator-qa`
  - Role: Validates frontmatter/structure/size, runs `quick_validate`, smoke-tests triggering, and confirms the old skill was safely trashed. Reports pass/fail against acceptance criteria.
  - Agent Type: `general-purpose`
  - Resume: false

## Step by Step Tasks

- IMPORTANT: Execute every step in order, top to bottom. Each task maps directly to a `TaskCreate` call.
- Before you start, run `TaskCreate` to create the initial task list that all team members can see and execute.

### 1. Cutover and scaffold
- **Task ID**: cutover-scaffold
- **Depends On**: none
- **Assigned To**: builder-core
- **Agent Type**: general-purpose
- **Parallel**: false
- Read the current `.claude/skills/meta-skill/SKILL.md` for any framing worth preserving (then discard the rest).
- Move the entire old directory to Trash: `mv .claude/skills/meta-skill ~/.Trash/meta-skill-old-$(date +%s)` (per AGENTS.md — never `rm -rf`).
- Create the new skeleton: `mkdir -p .claude/skills/meta-skill/{references,scripts,eval-viewer,agents}`.
- Confirm the old `docs/` (1,078 scraped lines) did NOT carry over.

### 2. Author fresh knowledge references
- **Task ID**: author-references
- **Depends On**: cutover-scaffold
- **Assigned To**: builder-knowledge
- **Agent Type**: general-purpose
- **Parallel**: true
- Author `references/frontmatter.md` documenting **every** SKILL.md frontmatter field — at minimum: `name`, `description`, `when_to_use`, `allowed-tools`, `disallowed-tools`, `disable-model-invocation`, `user-invocable`, `model`, `effort`, `context`, `agent`, `hooks`, `paths`, `arguments`, `argument-hint`, `shell`. For each: required/optional, exact constraints, what it controls, and "when an agent should set it." Include: combined `description`+`when_to_use` cap = **1,536 chars**; the **`name` conflict** (legacy gerund/lowercase/≤64 guidance vs. the current official behavior where `name` is a display label defaulting to the directory name); third-person + pushy description guidance; `${CLAUDE_SKILL_DIR}` usage.
- Author `references/structure.md`: directory layout, the 3 progressive-disclosure levels, the **< 500-line** SKILL.md rule, when/how to split into references (one level deep, ToC for files > ~300 lines), MCP tool naming (`Server:tool`), domain-organized references pattern.
- Author `references/authoring-principles.md`: Thariq's 9 tips (don't state the obvious; Gotchas section; file-system progressive disclosure; don't railroad — goals+constraints; setup/config.json; description-for-the-model; memory/`${CLAUDE_PLUGIN_DATA}`; bundle scripts; on-demand hooks) merged with Opus 4.8 deltas (effort as dominant lever; literalness/state scope explicitly; conservative tool & subagent use → be explicit when fan-out is wanted; remove forced progress-update scaffolding; no `$100 tip`/"think harder" prose; pushy descriptions to counter under-triggering). De-duplicate overlaps.
- Author `references/anti-patterns.md`: older-model holdovers to avoid, bad-vs-good description examples, and a concrete pre-ship review checklist.
- Keep each reference tight and example-driven; cite the live doc URLs at the top of each file.

### 3. Port and prune the test/iterate apparatus
- **Task ID**: port-apparatus
- **Depends On**: cutover-scaffold
- **Assigned To**: builder-core
- **Agent Type**: general-purpose
- **Parallel**: true
- Copy from skill-creator into `meta-skill/`: `scripts/{aggregate_benchmark.py,quick_validate.py,package_skill.py,utils.py,__init__.py}`, `eval-viewer/{generate_review.py,viewer.html}`, `agents/grader.md`, `references/schemas.md`.
- **Do NOT** copy `run_eval.py`, `run_loop.py`, `improve_description.py`, `generate_report.py` (deprecated `claude -p` subprocess apparatus).
- Verify the kept scripts are stdlib-only and run via `uv` (`uv run python -m scripts.quick_validate …` from the skill dir). Fix any skill-creator-specific path assumptions revealed by a dry run.
- If `quick_validate.py` hard-codes artifact types beyond `skill`, leave skill handling intact (scope is skills-only).

### 4. Write the lean SKILL.md
- **Task ID**: write-skill-md
- **Depends On**: author-references, port-apparatus
- **Assigned To**: builder-core
- **Agent Type**: general-purpose
- **Parallel**: false
- Write frontmatter: `name: meta-skill`; a front-loaded, third-person, slightly pushy `description` naming concrete trigger phrasings ("create a new skill…", "use your meta skill to…", "turn this workflow into a skill", "make a SKILL.md that…"); keep `description` (+ `when_to_use` if used) ≤ 1,536 chars combined.
- Write the workflow body following skill-creator's loop, enhanced: **Capture Intent → Interview/Research → Draft SKILL.md → Test (with-skill vs baseline) → Grade/Benchmark → Iterate → (optional) Description-Optimize → Package**. Give goals + constraints, not a rigid script (Thariq tip 4).
- Add clear "read this when…" pointers to `references/frontmatter.md`, `references/structure.md`, `references/authoring-principles.md`, `references/anti-patterns.md`, and to the apparatus (`scripts/`, `eval-viewer/`, `agents/grader.md`, `references/schemas.md`).
- Apply the principles to the skill's own prose (no obvious-stating, no `$100 tip`, no forced progress updates). Keep body < 500 lines (target ~200–300).

### 5. Validate, smoke-test, and report
- **Task ID**: validate-all
- **Depends On**: cutover-scaffold, author-references, port-apparatus, write-skill-md
- **Assigned To**: validator-qa
- **Agent Type**: general-purpose
- **Parallel**: false
- Run the Validation Commands below; capture output.
- Confirm `SKILL.md` body < 500 lines, references one level deep, and `description`+`when_to_use` ≤ 1,536 chars.
- Confirm `references/frontmatter.md` covers every field listed in Task 2.
- Smoke-test triggering: draft 2–3 realistic creation prompts and confirm `meta-skill` is the natural match; note any residual overlap with `prompt-architect`.
- Confirm old skill is absent from `.claude/skills/` and present in `~/.Trash/`.
- Report pass/fail per acceptance criterion; surface anything skipped (fail loud).

## Acceptance Criteria

- `.claude/skills/meta-skill/SKILL.md` exists with frontmatter `name: meta-skill` and a valid, parseable YAML header.
- `SKILL.md` body is < 500 lines and reads as a standard + workflow (not a tutorial that restates the obvious).
- `description` + `when_to_use` combined ≤ 1,536 characters; description is third-person, front-loaded, and names concrete trigger phrases.
- `references/frontmatter.md` documents **every** frontmatter field (the 16 listed), each with required/optional, constraints, what it controls, and when to set it — including the 1,536-char cap and the `name` legacy-vs-current conflict.
- `references/structure.md`, `references/authoring-principles.md`, and `references/anti-patterns.md` exist, are tight, and cite the live docs.
- Test apparatus present and runnable: `scripts/quick_validate.py`, `scripts/aggregate_benchmark.py`, `scripts/package_skill.py`, `eval-viewer/generate_review.py`, `agents/grader.md`, `references/schemas.md`. Deprecated `claude -p` scripts are **absent**.
- All references are exactly one level deep from `SKILL.md`.
- Old skill (`creating-new-skills` + scraped `docs/`) is moved to `~/.Trash/` and no longer in `.claude/skills/`.
- `meta-skill` triggers on the smoke-test creation prompts.

## Validation Commands

Execute these commands to validate the task is complete:

- `test -f .claude/skills/meta-skill/SKILL.md && echo OK` — new SKILL.md exists.
- `wc -l .claude/skills/meta-skill/SKILL.md` — confirm body < 500 lines.
- `head -20 .claude/skills/meta-skill/SKILL.md` — confirm frontmatter (`name: meta-skill`, description present).
- `uv run python -c "import yaml,sys; d=open('.claude/skills/meta-skill/SKILL.md').read().split('---')[1]; print(yaml.safe_load(d))"` — frontmatter parses as valid YAML.
- `cd .claude/skills/meta-skill && uv run python -m scripts.quick_validate SKILL.md --artifact-type skill` — frontmatter/structure validation passes (adjust flag to the ported script's interface).
- `find .claude/skills/meta-skill/references -maxdepth 1 -name '*.md'` — references exist and are one level deep.
- `ls .claude/skills/meta-skill/references/frontmatter.md .claude/skills/meta-skill/references/structure.md .claude/skills/meta-skill/references/authoring-principles.md .claude/skills/meta-skill/references/anti-patterns.md` — all four knowledge refs present.
- `ls .claude/skills/meta-skill/scripts/run_eval.py 2>&1` — must report "No such file" (deprecated apparatus dropped).
- `ls .claude/skills/meta-skill/ | grep -v docs` and `ls ~/.Trash/ | grep meta-skill-old` — confirm cutover (no scraped `docs/` in new skill; old skill in Trash).
- `awk 'NR>1 && /^---/{exit} NR>1{print}' .claude/skills/meta-skill/SKILL.md | wc -c` — sanity-check frontmatter size toward the 1,536-char listing budget.

## Notes

- **Tooling (AGENTS.md):** Python via `uv` only; never `python`/`pip`. JS via `bun`. Rich panels full width. Safe-delete via `mv … ~/.Trash/` — never `rm -rf`. No new dependencies expected; the ported scripts are Python-stdlib (optional `PyYAML` hardens frontmatter parsing — `uv run --with pyyaml …`).
- **Maintainability watch (the whole point):** the bundled test apparatus is the heaviest part and the main future maintenance cost. It's included because the user chose "follow skill-creator" for testing; progressive disclosure keeps it out of the always-loaded path. If maintainability later outweighs in-skill evals, the apparatus can be slimmed to a "test with realistic prompts + `quick_validate`" inline step or delegated — flagged for a future decision, not done here.
- **`prompt-architect` retirement is out of scope.** This plan does not modify or delete it. Expect transient trigger overlap until it's retired; `meta-skill`'s stronger, more specific description is the interim mitigation.
- **Decisions locked during planning:** Scope = skills only (commands diverge, handled separately). Testing = follow skill-creator, enhanced (drop deprecated `claude -p` scripts). Knowledge refs = authored fresh from live docs, not salvaged from prompt-architect.
- **Live source docs** (cite at the top of each reference): `code.claude.com/docs/en/skills`; `shanraisshan/claude-code-best-practice/best-practice/claude-skills.md`; `shanraisshan/claude-code-best-practice/tips/claude-thariq-tips-17-mar-26.md`; `platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-4-8`.
