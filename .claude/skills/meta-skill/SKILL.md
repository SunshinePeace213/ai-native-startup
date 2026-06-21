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
| `references/schemas.md` + `agents/grader.md` | The eval/grade/benchmark JSON shapes and grading rubric |

Bundled scripts (invoke from the skill directory so `scripts.` resolves as a
package):
- Validate: `uv run --with pyyaml python -m scripts.quick_validate <skill_dir>`
- Aggregate benchmark runs: `uv run python -m scripts.aggregate_benchmark <benchmark_dir>`
- Package: `uv run python -m scripts.package_skill <skill_dir> [out_dir]`
- Inspect eval results: `uv run python eval-viewer/generate_review.py <workspace_dir>`

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

### 4. Test — candidate vs baseline

There is no automated runner here; the test step is semi-manual.
- Author a handful of **realistic eval prompts** — a mix that *should* trigger
  the skill and a few that should *not* (to catch over-triggering). Shape them
  like `references/schemas.md` `evals.json` (prompt + expectations).
- Run each prompt **with the candidate skill and against a no-skill baseline.**
  Spawn the two as subagents in parallel when the work is independent, or judge
  by reading the skill cold — the comparison is what reveals whether the skill
  actually moves output, not the absolute score.
- Save each run's transcript and any output files so the grader can read them.

### 5. Grade / benchmark

- Grade each transcript with the rubric in `agents/grader.md` against the
  expectations, producing `grading.json` per the shape in
  `references/schemas.md`. Verdicts need cited evidence; a pass on a weak
  assertion is worse than useless.
- Aggregate with-skill vs without-skill runs:
  `uv run python -m scripts.aggregate_benchmark <benchmark_dir>` → mean/stddev
  and the delta. A skill that doesn't beat baseline isn't pulling its weight.
- Inspect visually: `uv run python eval-viewer/generate_review.py <workspace_dir>`.

### 6. Iterate

Fix the highest-leverage gap and re-run the relevant evals:
- **Not triggering / over-triggering** → tighten the `description` (phase 7).
- **Right trigger, weak output** → fix the body against
  `references/anti-patterns.md`: cut obvious-stating, de-railroad, split bloat
  into references, raise `effort` instead of prompting around shallow reasoning.

### 7. Description-optimize (optional)

When triggering accuracy is the bottleneck, do this by hand:
- Generate two prompt sets — ones that *should* fire and ones that *shouldn't*.
- Test the current `description` against both; tighten until should-fire hits
  and should-not stays quiet. Use the BAD→GOOD examples in
  `references/anti-patterns.md` as the pattern. Front-load the primary use case;
  trigger phrases past the 1,536 cap silently vanish.

### 8. Package

- Run the pre-ship checklist at the bottom of `references/anti-patterns.md`.
- Validate: `uv run --with pyyaml python -m scripts.quick_validate <skill_dir>`
  (must print "Skill is valid!").
- Package: `uv run python -m scripts.package_skill <skill_dir> [out_dir]`.

## Gotchas

- `quick_validate` needs PyYAML — always invoke with `--with pyyaml`. It takes a
  skill **directory**, not the `SKILL.md` file, and accepts no flags.
- `package_skill` and `aggregate_benchmark` import from the `scripts` package,
  so run them as `python -m scripts.<name>` **from the skill directory** (the
  one containing `scripts/`), not by absolute path to the `.py` file.
- The validator **rejects angle brackets** anywhere in `description`. Use plain
  text and ellipses, never bracketed placeholders.
- A skill's body **stays in context for the whole session** once loaded —
  Claude does not re-read it on later turns. Write standing instructions, not
  one-time steps, and keep the body lean because every line recurs.
- A longer `description` does not trigger better; past a tight trigger set it
  only burns the shared listing budget and can evict *other* skills from
  discovery. Run `/doctor` to see what's being truncated.
