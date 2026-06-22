# Plan: Make meta-skill a standalone replacement for skill-creator (create → eval → benchmark → HTML report → iterate)

## Task Description

The team's `meta-skill` (`.claude/skills/meta-skill/`) is the canonical standard and
workflow for authoring Claude Code Agent Skills. Today it teaches authoring craft well
(frontmatter, progressive disclosure, Opus 4.8 prompting) but its **test/measure loop is
deliberately semi-manual** — its SKILL.md literally says *"There is no automated runner
here; the test step is semi-manual"* and optimizes descriptions *"by hand."*

The third-party `skill-creator` plugin
(`~/.claude/plugins/cache/claude-plugins-official/skill-creator/...`) carries the full
pipeline meta-skill lacks: scripted trigger/description optimization (`run_eval.py`,
`improve_description.py`, `run_loop.py`), its HTML report (`generate_report.py`), a
benchmark analyst pass (`agents/analyzer.md`), blind A/B comparison
(`agents/comparator.md`), and a trigger-query review template (`assets/eval_review.html`).

**skill-creator will be deprecated/expired soon.** This task ports **every skill-creator
concept** into meta-skill so meta-skill becomes a complete, self-sufficient replacement,
and rewrites the meta-skill workflow so that when a user asks to "create a new skill" they
get the same end-to-end experience: a skill is drafted, run with-skill vs baseline, graded,
benchmarked, and **presented in an interactive HTML report the user reviews and leaves
feedback in**, then iterated until good — and finally packaged.

## Objective

When complete, meta-skill alone (skill-creator deletable) drives the full lifecycle:

1. **Create** — capture intent, draft `SKILL.md` + `references/`/`scripts/`/`assets/`; the
   reusable test suite (`evals.json` + trigger-eval set) lives **with the skill** in `{skill-dir}/evals/`.
2. **Eval** — spawn with-skill AND baseline runs in the same turn into a structured
   `evals/{skill-name}/iteration-N/` layout (repo-root `evals/`, never inside the packaged skill);
   capture `timing.json`; grade with `agents/grader.md`.
3. **Benchmark** — aggregate to `benchmark.json`/`benchmark.md` (pass-rate / time / tokens,
   mean ± stddev, with-skill vs baseline delta); run an analyst pass (`agents/analyzer.md`).
4. **Report for user review** — launch `eval-viewer/generate_review.py` → interactive HTML
   (Outputs tab with inline outputs + auto-saving feedback boxes + formal grades; Benchmark
   tab with stats and analyst notes). Headless/background → `--static` standalone HTML.
   User submits → `feedback.json` → meta-skill reads it and iterates into `iteration-N+1/`.
5. **Optimize triggering** — sign off trigger queries via `assets/eval_review.html`, then run
   the scripted `scripts/run_loop.py` loop (train/test split, `claude -p`) which emits its own
   HTML report via `scripts/generate_report.py` and returns the held-out `best_description`.
6. **(Advanced/optional) Blind compare** — `agents/comparator.md` + `agents/analyzer.md`.
7. **Package** — `quick_validate` → `package_skill`.

All of this lives behind a **lean SKILL.md body** (the skill's own core principle), with the
detailed mechanics in a new `references/eval-pipeline.md`.

## Problem Statement

Two concrete problems:

1. **Capability gap / impending dependency loss.** meta-skill cannot run the scripted
   triggering-optimization loop, has no analyst pass, no blind comparison, and no trigger-query
   review template. These currently only exist in skill-creator, which is going away. Without
   porting them, the team loses these capabilities when skill-creator expires.

2. **Workflow contradiction & undersold assets.** meta-skill's SKILL.md says there is no
   automated runner and does triggering "by hand," which contradicts the goal of an automated,
   self-sufficient pipeline. Separately, the interactive HTML feedback report the user wants
   **already exists** in meta-skill (`eval-viewer/generate_review.py`, byte-identical to
   skill-creator's, with `--benchmark` / `--static` / `--previous-workspace` support) but is
   only mentioned in the body as "inspect eval results" — its role as *the* user-review surface
   is never described. The workflow needs to be rewritten to use it as a first-class step.

## Solution Approach

**Vendor the missing files, then rewrite the docs — do not rewrite working code.**

The shared foundation is already in place and verified identical between the two skills:
`eval-viewer/generate_review.py`, `scripts/aggregate_benchmark.py`, `scripts/package_skill.py`,
`scripts/utils.py` (exports `parse_skill_md`), `agents/grader.md`, and `references/schemas.md`.
`scripts/quick_validate.py` is intentionally *ahead* of skill-creator (extended Claude Code
frontmatter allow-list) — **keep meta-skill's version**.

Because `utils.py` is identical and already exports `parse_skill_md`, and `find_project_root`
is defined inside `run_eval.py`, the four missing scripts are a **clean drop-in**: their imports
(`from scripts.utils import parse_skill_md`; `from scripts.run_eval import find_project_root, run_eval`;
`from scripts.generate_report import generate_html`; `from scripts.improve_description import improve_description`)
all resolve once the files sit together in `scripts/`. No dependency rewiring required.

Then rewrite the SKILL.md workflow (phases 4–8) to describe the full pipeline at a high level,
delegating the step-by-step mechanics to a **new `references/eval-pipeline.md`** (per the
decision to keep the always-loaded body lean). Resolve the contradiction by deleting the
"no automated runner / semi-manual / by hand" language and replacing it with the real loop.

**Resolved design decisions (from grilling):**
- **Full parity / standalone:** port every skill-creator concept; skill-creator becomes deletable.
- **Automation depth = hybrid (mirrors skill-creator):** output-quality evals stay
  subagent-orchestrated; trigger/description optimization is the scripted `run_loop` loop
  (`claude -p`). Accept the `claude` CLI dependency for the trigger loop.
- **Placement:** lean SKILL.md body + new `references/eval-pipeline.md` for mechanics.
- **HTML reports:** surface the existing `generate_review.py` viewer as the first-class user-review
  step AND port `generate_report.py` for the triggering loop. Both reports present.
- **Blind comparison:** port both `analyzer.md` and `comparator.md`; keep both. Blind comparison
  documented as the advanced/optional path it is in skill-creator; analyst pass is part of the
  normal benchmark flow.
- **Env boilerplate:** trim skill-creator's Claude.ai / Cowork / non-technical-user sections
  (delivery-channel boilerplate, not authoring concepts). **Keep `--static`** headless/no-display
  support (this repo runs background jobs). All script invocations documented with `uv run` per AGENTS.md.
- **Output layout:** eval **definitions** (the reusable test suite) live **with the skill** in
  `{skill-dir}/evals/`; eval **results** go to a repo-root **`evals/{skill-name}/`** (sibling to
  `specs/`), never inside the packaged skill. Definitions are the regression suite re-run on every
  edit; results are build artifacts. Git: ignore heavy run artifacts, commit `benchmark.md` + the
  HTML reports for a reviewable improvement history. (All scripts take path args, so this is a
  convention/docs change with zero code edits.)

## Results & Output Layout

The full workflow's files split into **definitions** (source, version-controlled with the skill)
and **results** (build artifacts, in a repo-root `evals/` tree). Scripts already accept explicit
path args, so this is a convention to document, not code to change.

**Definitions — live WITH the skill** (regression suite; re-found and re-run on every edit, travels
with the skill, behavior + test changes land in the same commit):

```
{skill-dir}/
├── SKILL.md
├── references/  scripts/  assets/  agents/
└── evals/
    ├── evals.json          # output-quality test prompts + assertions
    └── trigger-eval.json   # should / should-not-trigger queries
```

**Results — live at repo-root `evals/{skill-name}/`** (never inside the packaged skill, so
`package_skill` doesn't zip transcripts/outputs into the `.skill`):

```
evals/
└── {skill-name}/
    ├── iteration-1/
    │   ├── eval-<id>/with_skill/outputs/...      eval-<id>/without_skill/outputs/...
    │   ├── eval-<id>/{with_skill,without_skill}/{eval_metadata,timing,grading}.json
    │   ├── benchmark.json + benchmark.md         # pass-rate / time / tokens, mean±stddev, delta
    │   ├── review.html                           # generate_review.py --static (user-review report)
    │   └── feedback.json                         # user's viewer feedback
    ├── iteration-2/ …
    └── triggering/<timestamp>/                   # run_loop --results-dir
        ├── results.json  (incl. best_description)   report.html   log.txt
```

The final `.skill` package is a **deliverable, not a result** — write it to `dist/` (or hand
directly to the user), out of `evals/`.

**On edit / update of an existing skill:** re-use the skill's existing `{skill-dir}/evals/` suite
as the regression baseline (it's still valid — review/extend assertions only when the edit
intentionally changes scope), snapshot the prior skill version as the comparison baseline, and run
a fresh `iteration-N` into `evals/{skill-name}/`.

**Git:** ignore the heavy per-run artifacts (`outputs/`, transcripts, `results.json`, `log.txt`),
but commit `benchmark.md` and the HTML reports so the improvement history is reviewable. Concretely,
an `evals/.gitignore` like:

```
# ignore heavy run artifacts; keep summaries + reports
*/iteration-*/**
!*/iteration-*/benchmark.md
!*/iteration-*/*.html
*/triggering/**
!*/triggering/**/report.html
```

## Relevant Files

Use these files to complete the task:

- `.claude/skills/meta-skill/SKILL.md` — the workflow body to rewrite (phases 4–8, references
  table, bundled-scripts list, gotchas). Remove "no automated runner/semi-manual/by hand."
- `.claude/skills/meta-skill/scripts/utils.py` — already identical to skill-creator; exports
  `parse_skill_md` used by the ported scripts. **No change needed** (confirm only).
- `.claude/skills/meta-skill/scripts/quick_validate.py` — keep meta-skill's extended version;
  validator must pass against it.
- `.claude/skills/meta-skill/eval-viewer/generate_review.py` — already supports
  `--benchmark`/`--static`/`--previous-workspace`; becomes the documented user-review surface.
- `.claude/skills/meta-skill/scripts/aggregate_benchmark.py` — already present; used in benchmark step.
- `.claude/skills/meta-skill/agents/grader.md` — already present; used in grade step.
- `.claude/skills/meta-skill/references/schemas.md` — already present; the JSON shapes the
  pipeline and reports depend on.

Source files to port FROM (read-only reference; copy into meta-skill):
- `~/.claude/plugins/cache/claude-plugins-official/skill-creator/.../scripts/run_eval.py` (310 lines)
- `~/.claude/plugins/cache/claude-plugins-official/skill-creator/.../scripts/improve_description.py` (247 lines)
- `~/.claude/plugins/cache/claude-plugins-official/skill-creator/.../scripts/run_loop.py` (328 lines)
- `~/.claude/plugins/cache/claude-plugins-official/skill-creator/.../scripts/generate_report.py` (326 lines)
- `~/.claude/plugins/cache/claude-plugins-official/skill-creator/.../agents/analyzer.md` (274 lines)
- `~/.claude/plugins/cache/claude-plugins-official/skill-creator/.../agents/comparator.md` (202 lines)
- `~/.claude/plugins/cache/claude-plugins-official/skill-creator/.../assets/eval_review.html` (146 lines)
- `~/.claude/plugins/cache/claude-plugins-official/skill-creator/.../SKILL.md` — the prose source
  for the pipeline mechanics to adapt into `references/eval-pipeline.md`.

### New Files

- `.claude/skills/meta-skill/scripts/run_eval.py` — ported trigger-eval runner.
- `.claude/skills/meta-skill/scripts/improve_description.py` — ported description improver.
- `.claude/skills/meta-skill/scripts/run_loop.py` — ported eval+improve loop (train/test split).
- `.claude/skills/meta-skill/scripts/generate_report.py` — ported triggering-loop HTML report.
- `.claude/skills/meta-skill/agents/analyzer.md` — ported benchmark analyst.
- `.claude/skills/meta-skill/agents/comparator.md` — ported blind A/B comparator.
- `.claude/skills/meta-skill/assets/eval_review.html` — ported trigger-query review template
  (new `assets/` dir).
- `.claude/skills/meta-skill/references/eval-pipeline.md` — **new**: the detailed
  create→eval→benchmark→report→iterate + triggering-optimization mechanics, written in
  meta-skill's lean voice and pointed to from SKILL.md.

## Implementation Phases

### Phase 1: Foundation (vendor the missing files)
Copy the four scripts into `scripts/`, the two agents into `agents/`, and the template into a
new `assets/` dir. Confirm `utils.py` is unchanged and imports resolve. No code rewrites —
faithful port. Trim only what's strictly environment boilerplate inside the ported files if it
references Claude.ai/Cowork (the scripts themselves are environment-agnostic, so expect no edits).

### Phase 2: Core Implementation (rewrite the workflow + author the reference)
Rewrite SKILL.md phases 4–8 to describe the full automated pipeline at a high level and delete
the "no automated runner / semi-manual / by hand" language. Author `references/eval-pipeline.md`
with the step-by-step mechanics (the **Results & Output Layout** above: definitions in
`{skill-dir}/evals/`, results in repo-root `evals/{skill-name}/iteration-N/`; same-turn
with-skill+baseline spawn, `timing.json` capture, grade, aggregate, analyst pass, **launch viewer
before self-evaluating**, read `feedback.json`, iterate; the edit/regression path that re-uses the
skill's existing suite and snapshots the prior version as baseline; then triggering optimization via
`eval_review.html` sign-off → `run_loop --results-dir evals/{skill-name}/triggering` →
`generate_report` → apply `best_description`; blind comparison as advanced/optional; package to
`dist/`). Update the references table, bundled-scripts list, and gotchas. All commands use `uv run`.

### Phase 3: Integration & Polish (validate + smoke-test)
`quick_validate` must print "Skill is valid!". Smoke-test the four ported scripts import and run
(`--help` / module import). Confirm `generate_review.py --static` writes HTML and
`aggregate_benchmark` runs on a tiny fixture. Check char caps (`description` ≤ 1024, no `<`/`>`;
`description`+`when_to_use` ≤ 1536), SKILL.md body line count (< 500, target lean), and that all
cross-references (SKILL.md → `references/eval-pipeline.md`, `agents/*`, `scripts/*`, `assets/*`) resolve.

## Team Orchestration

- You operate as the team lead and orchestrate the team to execute the plan.
- You're responsible for deploying the right team members with the right context to execute the plan.
- IMPORTANT: You NEVER operate directly on the codebase. You use `Task` and `Task*` tools to deploy team members to the building, validating, testing, and other tasks.
  - This is critical. Your job is to act as a high level director of the team, not a builder.
  - Your role is to validate all work is going well and make sure the team is on track to complete the plan.
  - You'll orchestrate this by using the Task* Tools to manage coordination between the team members.
  - Communication is paramount. You'll use the Task* Tools to communicate with the team members and ensure they're on track to complete the plan.
- Take note of the session id of each team member. This is how you'll reference them.
- **Worktree note:** this repo enforces isolation — builders must call `EnterWorktree` before
  their first edit (or confirm they're already under `.claude/worktrees/`).

### Team Members

- Builder
  - Name: porter
  - Role: Vendor the four missing scripts, two agents, and the HTML template into meta-skill faithfully; verify imports resolve and `utils.py` is unchanged.
  - Agent Type: general-purpose
  - Resume: true
- Builder
  - Name: author
  - Role: Rewrite SKILL.md phases 4–8 (remove the semi-manual/by-hand language) and author the new `references/eval-pipeline.md`; update references table, scripts list, gotchas; trim env boilerplate, keep `--static`, use `uv run`.
  - Agent Type: general-purpose
  - Resume: true
- Builder
  - Name: validator
  - Role: Run `quick_validate`, smoke-test ported scripts and the viewer, check char caps / line count / cross-references; report pass/fail with evidence.
  - Agent Type: general-purpose
  - Resume: true

## Step by Step Tasks

- IMPORTANT: Execute every step in order, top to bottom. Each task maps directly to a `TaskCreate` call.
- Before you start, run `TaskCreate` to create the initial task list that all team members can see and execute.

### 1. Port pipeline scripts, agents, and template into meta-skill
- **Task ID**: port-pipeline-files
- **Depends On**: none
- **Assigned To**: porter
- **Agent Type**: general-purpose
- **Parallel**: true
- Copy `run_eval.py`, `improve_description.py`, `run_loop.py`, `generate_report.py` from the
  skill-creator cache path into `.claude/skills/meta-skill/scripts/` unchanged.
- Copy `analyzer.md` and `comparator.md` into `.claude/skills/meta-skill/agents/`.
- Create `.claude/skills/meta-skill/assets/` and copy `eval_review.html` into it.
- Confirm `scripts/utils.py` is unchanged and still exports `parse_skill_md`; do NOT downgrade
  `scripts/quick_validate.py` (keep meta-skill's extended frontmatter allow-list).
- Verify every cross-import resolves from the skill dir:
  `uv run python -c "import scripts.run_loop, scripts.run_eval, scripts.improve_description, scripts.generate_report"`.
- Report exact files added and any import errors.

### 2. Rewrite SKILL.md workflow and author references/eval-pipeline.md
- **Task ID**: rewrite-workflow-and-reference
- **Depends On**: none
- **Assigned To**: author
- **Agent Type**: general-purpose
- **Parallel**: true
- In `SKILL.md`: rewrite phases 4–8 to describe the full automated create→eval→benchmark→
  report→iterate→optimize→package pipeline at a high level; **delete** the
  "There is no automated runner here; the test step is semi-manual" line and the
  description-optimize "by hand" framing; replace with pointers to `references/eval-pipeline.md`.
- Update the references table (add `references/eval-pipeline.md`; note `agents/analyzer.md`,
  `agents/comparator.md`), the bundled-scripts list (add `run_eval`/`improve_description`/
  `run_loop`/`generate_report` with `uv run` invocations), and the gotchas (e.g., `run_loop`
  needs the `claude` CLI and a `--model` id; viewer review happens *before* self-evaluation;
  use `--static` in headless/background runs).
- Author `references/eval-pipeline.md` adapting skill-creator's SKILL.md mechanics into
  meta-skill's lean voice: results layout (`evals/{skill-name}/iteration-N/eval-<id>/{with_skill,without_skill}/outputs/`),
  spawn with-skill + baseline in the same turn, `eval_metadata.json`/`timing.json`/`grading.json`,
  grade (`agents/grader.md`), aggregate (`aggregate_benchmark`), analyst pass (`agents/analyzer.md`),
  **launch `generate_review.py` and wait for `feedback.json` before rewriting**, iterate;
  then triggering optimization (`assets/eval_review.html` sign-off → `run_loop` → `generate_report`
  → apply `best_description` chosen by held-out test score); blind comparison as advanced/optional
  (`agents/comparator.md`); package. Keep `--static`; drop Claude.ai/Cowork/non-technical sections.
- Honor the caps: keep SKILL.md body lean (< 500 lines, ideally ~200–300); `description` unchanged
  and within caps. Cross-reference files with `${CLAUDE_SKILL_DIR}/...` where the existing body does.
- Document the **Results & Output Layout** (definitions in `{skill-dir}/evals/`, results in
  repo-root `evals/{skill-name}/`, `.skill` to `dist/`) in both SKILL.md (briefly) and
  `references/eval-pipeline.md` (in full), and add a repo-root `evals/.gitignore` that ignores
  heavy run artifacts while keeping `benchmark.md` and `*.html` reports (see the Git block above).

### 3. Validate, smoke-test, and verify cross-references
- **Task ID**: validate-all
- **Depends On**: port-pipeline-files, rewrite-workflow-and-reference
- **Assigned To**: validator
- **Agent Type**: general-purpose
- **Parallel**: false
- Run `uv run --with pyyaml python -m scripts.quick_validate .` from the meta-skill dir; must
  print "Skill is valid!".
- Smoke-test ported scripts: `uv run python -m scripts.run_loop --help`,
  `uv run python -m scripts.run_eval --help`, `uv run python -m scripts.generate_report --help`,
  `uv run python -m scripts.improve_description --help` (or module import if no argparse `--help`).
- Smoke-test the report surfaces: `generate_review.py --static` writes a non-empty HTML file;
  `aggregate_benchmark` runs against a minimal fixture iteration dir.
- Verify char caps (`description` ≤ 1024, no `<`/`>`; `description`+`when_to_use` ≤ 1536),
  SKILL.md body line count, and that every path referenced in SKILL.md (`references/eval-pipeline.md`,
  `agents/grader.md`, `agents/analyzer.md`, `agents/comparator.md`, `scripts/*`, `assets/eval_review.html`,
  `eval-viewer/generate_review.py`) actually exists.
- Confirm the SKILL.md no longer contains "no automated runner", "semi-manual", or "by hand".
- Report pass/fail per check with evidence (the actual command output).

## Acceptance Criteria

- meta-skill contains every skill-creator concept: trigger-eval running, description improvement,
  the scripted optimization loop, the loop's HTML report, the benchmark analyst, blind comparison,
  and the trigger-query review template — i.e., skill-creator can be deleted with no capability loss.
- `quick_validate` prints "Skill is valid!" and all four ported scripts import/run without error.
- `SKILL.md` describes the full automated create→eval→benchmark→**HTML report for user
  review/feedback**→iterate→optimize→package pipeline, and no longer says "no automated runner",
  "semi-manual", or "by hand".
- The detailed mechanics live in `references/eval-pipeline.md`; the SKILL.md body stays lean
  (< 500 lines) and within all char caps.
- The user-review surface is documented as a first-class step: `generate_review.py` (Outputs +
  Benchmark tabs, auto-saving feedback → `feedback.json`), with `--static` for headless/background.
- Env boilerplate (Claude.ai/Cowork/non-technical) is absent; `--static` retained; all documented
  commands use `uv run`.
- All cross-references in SKILL.md resolve to files that exist.
- The output layout is documented and enforced: definitions in `{skill-dir}/evals/`, results in
  repo-root `evals/{skill-name}/`, `.skill` to `dist/`; an `evals/.gitignore` ignores heavy run
  artifacts while keeping `benchmark.md` + `*.html` reports. The reference explains that an edit
  re-uses the existing suite as the regression baseline.

## Validation Commands

Execute these commands to validate the task is complete (run from `.claude/skills/meta-skill/`):

- `uv run --with pyyaml python -m scripts.quick_validate .` — must print "Skill is valid!"
- `uv run python -c "import scripts.run_loop, scripts.run_eval, scripts.improve_description, scripts.generate_report, scripts.aggregate_benchmark, scripts.package_skill"` — all ported + existing scripts import cleanly
- `uv run python -m scripts.run_loop --help` — scripted optimization loop is wired up
- `uv run python eval-viewer/generate_review.py --help` — review/report surface present
- `ls assets/eval_review.html agents/analyzer.md agents/comparator.md references/eval-pipeline.md` — new files exist
- `grep -RInE "no automated runner|semi-manual|by hand" SKILL.md` — must return nothing
- `awk 'END{print NR}' SKILL.md` — body line count sanity (< 500)
- `grep -RIn "evals/{skill-name}/" references/eval-pipeline.md` and `test -f ../../../evals/.gitignore || test -f evals/.gitignore` — output layout documented and gitignore present (adjust path to repo root)

## Notes

- **CLI dependency:** the triggering-optimization loop (`run_loop.py` → `improve_description.py`)
  shells out to `claude -p`. This is an accepted new dependency for that one feature; the rest of
  the pipeline (subagent evals, grading, aggregation, viewer, packaging) has no such dependency.
- **`run_loop` model flag:** pass the session's model id (e.g. `--model claude-opus-4-8`) so the
  triggering test matches what users actually experience, per skill-creator's guidance.
- **Keep meta-skill's `quick_validate.py`** — it intentionally allows the Claude Code extended
  frontmatter set (`when_to_use`, `effort`, `disable-model-invocation`, etc.); do not overwrite it
  with skill-creator's narrower version.
- **No new libraries** required — the ported scripts use stdlib + the existing `scripts.utils`.
  Continue invoking Python via `uv run` and any JS/TS via `bun` per AGENTS.md.
- **Cleanup (mention, don't act):** once this lands and is verified, skill-creator is redundant;
  removing the plugin is the user's call (use `mv ... ~/.Trash/`, never `rm -rf`, per AGENTS.md).
- A stray `.claude/skills/meta-skill/scripts/__pycache__/` is untracked in git status — harmless,
  but the porter/validator may note it; do not commit it.
