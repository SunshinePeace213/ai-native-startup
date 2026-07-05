---
name: meta-skills
description: The team standard and guided workflow for authoring Claude Code Skills and slash commands. Use when the user wants to create a new skill or slash command, turn a workflow or prompt into a reusable skill or /command, fix a skill or command that isn't triggering or fires too often, run evals or benchmark a skill against baseline, optimize a description for triggering accuracy, or package a skill for distribution. Also use when the user describes a repeatable workflow worth capturing, even if they never say "skill" or "command". Covers choosing between a skill, a slash command, or a subagent. Not for authoring subagents — use meta-agent.
---

# Meta-Skills

A skill for creating and iteratively improving Claude Code Skills and slash
commands. Based on Anthropic's skill-creator; the `scripts/`, `agents/`,
`eval-viewer/`, `assets/`, and `references/schemas.md` files are kept in sync
with it. Tooling and model rules come from `AGENTS.md` (uv, bun, model aliases).

At a high level, creating a skill goes like this:

- Decide what the skill should do and roughly how
- Write a draft
- Create a few test prompts and run claude-with-access-to-the-skill on them
- Help the user evaluate the results qualitatively (the eval viewer) and
  quantitatively (assertions, benchmark)
- Rewrite based on their feedback, repeat until satisfied
- Optionally optimize the description for triggering, then package

Figure out where the user is in this process and jump in there. If they already
have a draft, go straight to the eval/iterate loop. If they say "skip the
evaluations, just vibe with me", do that instead.

## Skill, command, or subagent?

Confirm the artifact before building anything.

- A **slash command** is a reusable prompt the user invokes by name (`/build`,
  `/commit`). Default form: a flat file at `.claude/commands/<name>.md`.
- A **skill** is knowledge or capability Claude reaches for on its own, or any
  command that needs bundled material: a directory at
  `.claude/skills/<name>/SKILL.md` with optional `references/`, `scripts/`,
  `assets/`, `evals/`.
- A **subagent** does delegated, context-isolated work (research that would
  flood the thread, a scoped executor, a fan-out worker). That's a different
  artifact — route to the **meta-agent** skill.

Commands *are* skills in current Claude Code: both forms produce `/name`, run
identically, and accept the same frontmatter. So this is a layout-and-invocation
choice, not two artifacts:

- **Recommend the flat command** when the user drives it by typing `/name`, it
  is a single prompt (possibly with args), and it needs no supporting files.
- **Recommend the skill directory** when Claude should auto-trigger it from a
  discoverable description, or it needs `references/` it points at, `scripts/`
  it runs, or an eval suite.
- **Never ship both names** — a same-name skill silently beats the flat
  command. When one replaces the other, delete the loser.
- Either form with side effects (`/commit`, `/deploy`, `/send-*`) gets
  `disable-model-invocation: true` so only the user can run it.

## Creating a skill

### Capture intent

The conversation may already contain the workflow the user wants to capture
("turn this into a skill") — extract the tools used, the step sequence, the
corrections they made, and confirm before proceeding. Pin down:

1. What should this skill enable Claude to do?
2. When should it trigger? (what user phrases/contexts)
3. What's the expected output format?
4. Should we set up test cases? Objectively verifiable outputs (file
   transforms, data extraction, code generation, fixed workflows) benefit from
   them; subjective outputs (writing style, design) often don't. Suggest a
   default, let the user decide.

### Interview and research

Ask about edge cases, input/output formats, example files, success criteria,
and dependencies before writing test prompts. Read 1–2 existing skills near
the domain (`.claude/skills/`, installed plugins) for conventions to match.

### Write the SKILL.md

Frontmatter first — `name` and `description` are what every session sees:

- **name**: match the directory, lowercase-hyphen.
- **description**: the trigger document. It decides whether Claude loads the
  skill, so include what the skill does AND the specific contexts to use it.
  Claude tends to *undertrigger* skills, so make it a little pushy: "Use this
  whenever the user mentions dashboards, data visualization, or internal
  metrics, even if they don't say 'dashboard'." Full field surface, char caps,
  and description guidance: `references/frontmatter.md`.

Then the body. Anatomy:

```
skill-name/
├── SKILL.md          # required — YAML frontmatter + Markdown instructions
└── Bundled resources (optional)
    ├── scripts/      # executable code for deterministic/repetitive work
    ├── references/   # docs loaded into context on demand
    ├── assets/       # files used in output (templates, icons, fonts)
    └── evals/        # evals.json + trigger-eval.json test definitions
```

**Progressive disclosure** — skills load in three levels:

1. **Metadata** (name + description) — always in context, every session
2. **SKILL.md body** — in context whenever the skill triggers, and it stays
   there for the rest of the session, so every line is a recurring cost; write
   standing instructions, not one-time steps
3. **Bundled resources** — on demand; scripts execute without ever entering
   context, unused references cost nothing

Key patterns:

- Keep SKILL.md under 500 lines. Approaching the limit, split material into
  `references/<topic>.md` with clear pointers on when to read each ("For form
  filling, see `references/forms.md`"). One level deep — nested references get
  partially read. Files over ~300 lines get a table of contents.
- When a skill spans variants (aws/gcp/azure), give each its own reference
  file and let the body route — Claude reads only the relevant one.
- Reference bundled files as `${CLAUDE_SKILL_DIR}/...` so paths resolve
  regardless of install location or cwd. Forward slashes only. MCP tools by
  their qualified `Server:tool` name.

**Writing style**: imperative form. Explain the *why* behind constraints in
lieu of heavy-handed MUSTs — if you find yourself writing ALWAYS or NEVER in
all caps, reframe with the reasoning instead. Keep it general, not overfit to
the examples at hand. Draft, then reread with fresh eyes and improve. Scan the
draft against `references/anti-patterns.md` before showing it.

### Test cases

Write 2–3 realistic test prompts — what a real user would actually type — and
confirm them with the user before running. Save them to the skill's
`evals/evals.json` (prompts only; assertions come later, see
`references/schemas.md` for the full shape).

## Creating a slash command

Draft the body in the house template — `# Purpose`, `## Variables`,
`## Instructions`, `## Workflow`, `## Report` — per
`references/command-format.md`, which also covers the flat-file-vs-directory
decision tree and dynamic context injection. Frontmatter (argument-hint,
allowed-tools, and friends): `references/frontmatter.md`.

Commands skip the eval pipeline unless their output is gradeable. The test is
simpler: would Claude fire it on the phrasings users type, and does invoking
it beat typing the request by hand?

## Validate

After drafting (skill or command):

```
uv run --with pyyaml python ${CLAUDE_SKILL_DIR}/scripts/validate.py <path-to-file>
```

Fix every FAIL; treat WARNs as prompts to double-check intent. This validator
knows the full Claude Code surface. Packaging (`quick_validate` /
`package_skill`) enforces the stricter public Agent-Skills surface — a skill
meant for distribution must keep to `name`, `description`, `license`,
`allowed-tools`, `metadata`, `compatibility`.

## Running and evaluating test cases

This section is one continuous sequence — don't stop partway through.

Put results in `<skill-name>-workspace/` as a sibling to the skill directory
(gitignored — results are never committed). Organize by iteration
(`iteration-1/`, `iteration-2/`), one directory per test case inside, created
as you go, named descriptively (not just `eval-0`).

**Step 1 — spawn all runs in the same turn.** For each test case, spawn two
subagents at once: one with the skill, one baseline. Don't run the with-skill
set first and circle back — launch everything together so the comparison
finishes together.

- With-skill: give the subagent the skill path, the prompt, any input files,
  and the save path `<workspace>/iteration-<N>/<eval-name>/with_skill/outputs/`.
- Baseline for a **new** skill: no skill at all → `without_skill/outputs/`.
  Baseline for an **edit**: snapshot first (`cp -r <skill-path>
  <workspace>/skill-snapshot/`), point the baseline at the snapshot →
  `old_skill/outputs/`.

Write an `eval_metadata.json` per test case (assertions may start empty).

**Step 2 — draft assertions while runs are in flight.** Good assertions are
objectively verifiable and read clearly in the viewer. Don't force assertions
onto subjective outputs — those are evaluated qualitatively. Update the
`eval_metadata.json` files and the skill's `evals/evals.json` once drafted.

**Step 3 — capture timing as each run completes.** The task notification
carries `total_tokens` and `duration_ms`; save them to `timing.json` in the
run directory immediately — they can't be recovered later.

**Step 4 — grade, aggregate, review.**

1. Grade each run against its assertions per `agents/grader.md`, writing
   `grading.json` with the exact fields `text` / `passed` / `evidence` — the
   viewer depends on those names. Prefer a script for programmatically
   checkable assertions over eyeballing.
2. Aggregate: `uv run python -m scripts.aggregate_benchmark
   <workspace>/iteration-N --skill-name <name>` (run from this skill's
   directory so `scripts.` resolves) → `benchmark.json` + `benchmark.md` with
   pass rate / time / tokens, mean ± stddev, and the with-skill delta. A skill
   that doesn't beat baseline isn't pulling its weight.
3. Analyst pass per `agents/analyzer.md`: surface what the aggregate hides —
   non-discriminating assertions, high-variance evals, time/token tradeoffs.
4. Launch the viewer — **before** evaluating the outputs yourself; get them in
   front of the user first:

   ```
   uv run python ${CLAUDE_SKILL_DIR}/eval-viewer/generate_review.py \
     <workspace>/iteration-N --skill-name <name> \
     --benchmark <workspace>/iteration-N/benchmark.json
   ```

   Iteration 2+: add `--previous-workspace <workspace>/iteration-<N-1>`.
   Headless / no display: add `--static <workspace>/iteration-N/review.html`
   to write a standalone file; "Submit All Reviews" then downloads
   `feedback.json`, which you copy into the iteration directory. Use
   `generate_review.py`, not hand-written HTML.

**Step 5 — read `feedback.json`** when the user says they're done. Empty
feedback on a case means it was fine; focus on the complaints.

## Improving the skill

1. **Generalize from the feedback.** The skill will run across prompts nobody
   imagined; overfitting to the handful of test examples makes it useless.
   For stubborn issues, try different framings rather than piling on
   constraints.
2. **Keep the prompt lean.** Read the transcripts, not just the outputs — if
   the skill makes the model do unproductive work, cut the lines causing it.
   Remove anything not pulling its weight.
3. **Explain the why** behind each instruction so the model can handle the
   cases the letter of the rule doesn't cover.
4. **Bundle repeated work.** If several transcripts independently wrote the
   same helper script, write it once into `scripts/` and point the skill at
   it.

Then rerun every test case (with-skill and baseline) into a fresh
`iteration-<N+1>/`, relaunch the viewer with `--previous-workspace`, and wait
for the next round of feedback. Stop when the user is happy, the feedback is
all empty, or progress flatlines.

## Advanced: blind comparison

For a rigorous "is the new version actually better?", give two outputs to an
independent agent without saying which is which and let it judge — read
`agents/comparator.md`, then `agents/analyzer.md` for why the winner won.
Optional; the human review loop is usually enough.

## Description optimization

After the skill works, offer to optimize its description for triggering.

**Generate ~20 trigger queries** — 8–10 should-trigger, 8–10 should-not —
saved as `[{"query": "...", "should_trigger": true}, ...]`. Make them
realistic: file paths, column names, backstory, casual phrasing, typos.
Should-trigger queries cover different phrasings including ones that never
name the skill; should-not queries are near-misses that share keywords but
need something else — obviously-irrelevant negatives test nothing. Note that
Claude only consults skills for tasks it can't trivially handle, so one-step
queries are poor test cases regardless of description quality.

**Sign off with the user** via `assets/eval_review.html`: substitute
`__EVAL_DATA_PLACEHOLDER__` (the JSON array, unquoted),
`__SKILL_NAME_PLACEHOLDER__`, `__SKILL_DESCRIPTION_PLACEHOLDER__`; write to a
temp file; the user edits, toggles, and exports the signed-off set. Bad
queries make bad descriptions. Save the set to the skill's
`evals/trigger-eval.json`.

**Run the loop** in the background from this skill's directory:

```
uv run python -m scripts.run_loop \
  --eval-set <path-to-trigger-eval.json> \
  --skill-path <skill-dir> \
  --model sonnet --max-iterations 5 \
  --results-dir <workspace>/triggering --verbose
```

It shells out to `claude -p`, splits 60% train / 40% held-out test, runs each
query 3 times per evaluation, proposes improved descriptions from the
failures, and returns a `best_description` chosen by held-out score. Pass the
model as an alias; `sonnet` is enough for this high-volume loop — confirm the
final description on the session's model, since triggering is
model-sensitive. Tail `log.txt` to keep the user updated. Apply
`best_description` to the frontmatter and show before/after with the scores.

## Package

Only when the skill is for distribution:

```
uv run --with pyyaml python -m scripts.quick_validate <skill-dir>   # "Skill is valid!"
uv run --with pyyaml python -m scripts.package_skill <skill-dir> dist/
```

Run the pre-ship checklist at the bottom of `references/anti-patterns.md`
first. The `.skill` goes to `dist/` or straight to the user — never into the
workspace.

## Reference files

Read these when the step needs them — don't preload:

- `references/frontmatter.md` — field surface, caps, description writing
- `references/command-format.md` — house command template, layout tree,
  injection
- `references/anti-patterns.md` — what to cut, BAD→GOOD descriptions,
  pre-ship checklist
- `references/schemas.md` — JSON shapes for evals, grading, benchmark
- `agents/grader.md`, `agents/analyzer.md`, `agents/comparator.md` — prompts
  for the grading, analysis, and blind-comparison subagents
