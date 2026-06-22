---
name: meta-skill
description: >-
  The team's canonical standard and guided workflow for authoring Claude Code
  Agent Skills. Drafts, reviews, tests, and packages skills to current
  best practices (frontmatter, progressive disclosure, Opus 4.8 prompting).
  Use whenever the user wants to "create a new skill", says "use your meta
  skill to ...", asks to "turn this workflow into a skill" or "make a SKILL.md
  that ...", reports "my skill isn't triggering", or asks "is this a good
  skill" / how to fix a skill's description or triggering. Fires even when the
  build-a-skill intent is buried inside a longer request. This is THE authority
  for skill authoring — prefer it over ad-hoc advice.
when_to_use: >-
  Reach for this when reviewing or optimizing an existing skill's frontmatter,
  description, or triggering behavior; when a skill fires too often or not at
  all; when deciding directory-vs-single-file layout or how to split into
  references/; or when validating and packaging a skill for distribution. Also
  when the user describes a repeatable workflow and the right move is to capture
  it as a reusable skill, even if they didn't use the word "skill".
---

# Meta-Skill: Authoring Claude Code Agent Skills

This skill is both the **standard** for what a good Agent Skill looks like and a
**workflow** for producing one. The standard lives in `references/`; this body
is the loop that applies it. Read the relevant reference at the phase that needs
it — don't preload them all.

## Operating principle

A skill is a folder, not a prose dump. Its power comes from a tight trigger
(`description`), a lean body (goals + constraints, not a script), and heavy
material pushed into `references/` and `scripts/` that load only when needed.
You are authoring *for the model* — every body line is a recurring per-turn cost
once the skill loads, so cut anything Claude already does by default.

Apply these principles to the skill you build **and to your own conduct here.**
No fake incentives, no "think harder," no forced progress cadence. If quality
needs depth, advise raising `effort` (`high`/`xhigh`) rather than adding prose —
that is the dominant capability lever on Opus 4.8.

## References — load each when its phase arrives

| Read | When |
|---|---|
| `references/frontmatter.md` | Choosing/validating fields; writing the `description`; char caps; `${CLAUDE_SKILL_DIR}` substitutions |
| `references/structure.md` | Directory layout, the 500-line rule, when and how to split into `references/`, MCP tool naming |
| `references/authoring-principles.md` | The merged Thariq + Opus 4.8 craft principles (don't-state-the-obvious, gotchas, goals-not-railroad, effort lever) |
| `references/anti-patterns.md` | What to cut, BAD→GOOD descriptions, and the **pre-ship checklist** (run before packaging) |
| `references/eval-pipeline.md` | The full test/measure/optimize mechanics: output layout, same-turn eval, grade, benchmark, the HTML review report, iterate, triggering optimization, package |
| `references/schemas.md` | The eval/grade/benchmark JSON shapes |
| `agents/grader.md` | Grading rubric — assertions vs. outputs (eval step) |
| `agents/analyzer.md` | Benchmark analyst pass, and the post-hoc "why did it win" analysis |
| `agents/comparator.md` | Blind A/B comparison between two skill versions (advanced/optional) |

Bundled scripts (invoke from the skill directory so `scripts.` resolves as a
package; Python via `uv run`):
- Validate: `uv run --with pyyaml python -m scripts.quick_validate <skill_dir>`
- Run a trigger eval: `uv run python -m scripts.run_eval --eval-set <trigger-eval.json> --skill-path <skill_dir> --model sonnet`
- Improve a description: `uv run python -m scripts.improve_description --eval-results <results.json> --skill-path <skill_dir> --model sonnet`
- Triggering-optimization loop: `uv run python -m scripts.run_loop --eval-set <trigger-eval.json> --skill-path <skill_dir> --model sonnet --results-dir evals/<skill-name>/triggering`
- Render the loop's HTML report: `uv run python -m scripts.generate_report <results.json> -o report.html`
- Aggregate benchmark runs: `uv run python -m scripts.aggregate_benchmark <iteration_dir>`
- Package: `uv run python -m scripts.package_skill <skill_dir> [out_dir]`
- User-review report: `uv run python eval-viewer/generate_review.py <iteration_dir> --benchmark <benchmark.json>`

## The workflow

Phases, not a railroad. Skip what doesn't apply; loop back when a later phase
exposes a gap. The goal: a skill that triggers on the right requests and
produces materially better output than no skill.

### 1. Capture intent

Pin down three things before writing anything:
- **Artifact** — what does the skill produce or do? (transform, runbook,
  knowledge, code-gen.)
- **Triggers** — the actual phrases a user would type, including when they
  don't name the skill. These become the `description`.
- **Success criteria** — what "good output" looks like, concretely enough to
  test later. Vague criteria ("make it work") can't be graded.

If any of the three is unclear, ask — don't guess. State assumptions explicitly.

### 2. Interview / research

Clarify scope and survey prior art:
- Read 1–2 existing skills near this domain (in `.claude/skills/` or installed
  plugins) for conventions to match.
- Decide **single-file vs directory.** Single `SKILL.md` for a short, one-shot
  skill; a folder with `references/`/`scripts/` when there's stable reference
  material, deterministic work, or mutually exclusive paths. See
  `references/structure.md`.
- Decide whether per-installation config is needed (the `config.json` pattern in
  `references/authoring-principles.md`).

### 3. Draft SKILL.md

Frontmatter first, then a lean body.
- **Frontmatter:** read `references/frontmatter.md` when choosing fields. Keep
  it minimal — `description` is the only field that decides triggering. Write it
  third person, front-loaded, naming the user's vocabulary, slightly pushy
  (Claude under-triggers on 4.8). Honor the caps: `description` ≤ 1,024 chars
  with no `<`/`>`; `description` + `when_to_use` ≤ 1,536 combined. Set `effort`
  only if quality depends on it; set `disable-model-invocation: true` for
  side-effecting task skills so Claude doesn't run them because the code "looks
  ready."
- **Body:** goals + constraints, not a step-by-step script (unless the order is
  genuinely load-bearing — irreversible ops, regulated procedures). Under 500
  lines, target 200–300. Push substantial, sometimes-needed material into
  `references/<topic>.md`, one level deep, and point at it explicitly ("read
  `references/forms.md` when filling forms"). Reference bundled files with
  `${CLAUDE_SKILL_DIR}/...`; forward slashes only; MCP tools as `Server:tool`.
- Match repo tooling in any examples: Python via `uv`, JS/TS via `bun`.
- Save the reusable test suite **with the skill** in `{skill-dir}/evals/`:
  `evals.json` (output-quality prompts + assertions) and `trigger-eval.json`
  (should / should-not-trigger queries). These travel with the skill and become
  the regression suite re-run on every edit.

### 4–8. Test, measure, optimize, package — the pipeline

This is an automated loop, not a manual one. Drive it via the scripts above; the
step-by-step mechanics, exact commands, and JSON shapes live in
`references/eval-pipeline.md` — read it here. At a high level:

- **Eval** — for each prompt, spawn a with-skill run and a no-skill baseline **in
  the same turn**, save outputs, capture each task's `timing.json`, then grade
  every run with `agents/grader.md` → `grading.json`.
- **Benchmark** — `uv run python -m scripts.aggregate_benchmark <iteration_dir>`
  produces `benchmark.json`/`benchmark.md` (pass-rate / time / tokens, mean ±
  stddev, with-skill vs. baseline delta), then do an analyst pass with
  `agents/analyzer.md`. A skill that doesn't beat baseline isn't pulling weight.
- **Report for user review (first-class step)** — launch
  `uv run python eval-viewer/generate_review.py <iteration_dir> --benchmark <benchmark.json>`
  to produce the interactive HTML: an Outputs tab (inline outputs + auto-saving
  feedback boxes + formal grades) and a Benchmark tab (stats + analyst notes).
  Get the outputs in front of the user and **wait for their `feedback.json`
  before you self-evaluate or rewrite the skill.**
- **Iterate** — fix the highest-leverage gap (tighten `description` for
  triggering; fix the body against `references/anti-patterns.md` for weak
  output; raise `effort` instead of prompting around shallow reasoning), then
  re-run into a fresh `iteration-N+1/` and re-report. On an **edit**, re-use the
  skill's existing `{skill-dir}/evals/` suite as the regression baseline and
  snapshot the prior version as the comparison baseline.
- **Triggering optimization** — when triggering accuracy is the bottleneck, sign
  off the trigger queries via `assets/eval_review.html`, then run the scripted
  `scripts.run_loop` loop (`--results-dir evals/<skill-name>/triggering`). It
  splits train/test via `claude -p`, emits its own HTML via `scripts.generate_report`,
  and returns a held-out `best_description` to apply to the frontmatter.
- **Blind compare (advanced/optional)** — `agents/comparator.md` +
  `agents/analyzer.md` for a rigorous "is the new version actually better?".
- **Package** — run the pre-ship checklist (bottom of
  `references/anti-patterns.md`), then
  `uv run --with pyyaml python -m scripts.quick_validate .` (must print "Skill is
  valid!") and `uv run python -m scripts.package_skill <skill_dir> dist/`.

**Output layout** (full detail in `references/eval-pipeline.md`): eval
*definitions* live with the skill in `{skill-dir}/evals/`; eval *results* go to a
repo-root `evals/{skill-name}/iteration-N/` (sibling to `specs/`), never inside
the packaged skill; the final `.skill` is a deliverable → write it to `dist/`,
never inside `evals/`.

## Gotchas

- `quick_validate` needs PyYAML — always invoke with `--with pyyaml`. It takes a
  skill **directory**, not the `SKILL.md` file, and accepts no flags.
- `package_skill` and `aggregate_benchmark` import from the `scripts` package,
  so run them as `python -m scripts.<name>` **from the skill directory** (the
  one containing `scripts/`), not by absolute path to the `.py` file.
- `run_loop` / `improve_description` shell out to the `claude -p` CLI — the
  `claude` CLI must be installed and you must pass a `--model` id. Sonnet (`claude-sonnet-4-6`) is enough for this
  high-volume loop; triggering is model-sensitive, so confirm the final
  `best_description` on your production model.
- The `generate_review.py` viewer review happens **before** you self-evaluate or
  rewrite. Launch it, then wait for the user's `feedback.json`; don't iterate the
  skill ahead of their review.
- In headless / background runs (no display), pass `--static <path>` to
  `generate_review.py` so it writes a standalone HTML file instead of starting a
  server; the user's "Submit All Reviews" then downloads `feedback.json`.
- The validator **rejects angle brackets** anywhere in `description`. Use plain
  text and ellipses, never bracketed placeholders.
- A skill's body **stays in context for the whole session** once loaded —
  Claude does not re-read it on later turns. Write standing instructions, not
  one-time steps, and keep the body lean because every line recurs.
- A longer `description` does not trigger better; past a tight trigger set it
  only burns the shared listing budget and can evict *other* skills from
  discovery. Run `/doctor` to see what's being truncated.
