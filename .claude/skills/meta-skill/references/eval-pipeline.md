# Eval Pipeline — create → eval → benchmark → review → iterate → optimize → package

The mechanics behind SKILL.md phases 4–8. The body describes the loop at a high
level; this file is the step-by-step. Every command runs with `uv run` from the
**skill directory** (the one containing `scripts/`) so `scripts.` resolves as a
package. All `claude -p` invocations pass `--model sonnet` — use a model **alias** (`sonnet`/`opus`/`haiku`) so it tracks the latest, not a pinned dated id; `sonnet` is enough for the high-volume trigger loop.

## Output layout — definitions vs. results

Two trees. **Definitions** are source (version-controlled with the skill, the
regression suite). **Results** are build artifacts (a repo-root `evals/` tree,
never inside the packaged skill — so `package_skill` never zips transcripts into
the `.skill`).

**Definitions — live WITH the skill** (`{skill-dir}/evals/`):

```
{skill-dir}/
├── SKILL.md   references/   scripts/   assets/   agents/
└── evals/
    ├── evals.json         # output-quality prompts + assertions
    └── trigger-eval.json  # should / should-not-trigger queries
```

These are the regression suite: re-found and re-run on every edit, committed in
the same change as the behavior they test.

**Results — live at repo-root `evals/{skill-name}/`**:

```
evals/
└── {skill-name}/
    ├── iteration-1/
    │   ├── eval-<id>/with_skill/outputs/...    eval-<id>/without_skill/outputs/...
    │   ├── eval-<id>/{with_skill,without_skill}/{eval_metadata,timing,grading}.json
    │   ├── benchmark.json  +  benchmark.md     # pass-rate / time / tokens, mean±stddev, delta
    │   ├── review.html                          # generate_review.py --static
    │   └── feedback.json                        # the user's viewer feedback
    ├── iteration-2/ …
    └── triggering/<timestamp>/                  # run_loop --results-dir
        ├── results.json (incl. best_description)   report.html   log.txt
```

Don't pre-create the tree — make directories as runs land. The final `.skill` is
a **deliverable, not a result**: write it to `dist/`, never inside `evals/`.

The repo-root `evals/.gitignore` ignores the heavy per-run artifacts (`outputs/`,
transcripts, `results.json`, `log.txt`) but keeps `benchmark.md` and the HTML
reports, so the improvement history stays reviewable.

## 1. Eval — spawn with-skill AND baseline in the same turn

For each eval prompt, spawn two subagents **in the same turn** — one with the
skill, one without. Don't run the with-skill set first and circle back for
baselines; launch everything at once so the comparison is apples-to-apples and
finishes together.

- **With-skill:** give the subagent the skill path, the prompt, any input files,
  and an explicit save path: `evals/{skill-name}/iteration-N/eval-<id>/with_skill/outputs/`.
- **Baseline:** same prompt. For a **new** skill the baseline is no skill at all,
  saved to `without_skill/outputs/`. For an **edit**, the baseline is the prior
  version (see §5).

Write an `eval_metadata.json` per eval (`eval_id`, descriptive `eval_name`,
`prompt`, `assertions` — assertions may start empty and be filled while runs are
in flight). When each task notification returns, immediately save its
`total_tokens` / `duration_ms` to `timing.json` in the run dir — that data comes
only through the notification and can't be recovered later.

Then **grade** each run: a grader subagent reads `${CLAUDE_SKILL_DIR}/agents/grader.md`,
checks each assertion against the outputs, and writes `grading.json` per the shape
in `${CLAUDE_SKILL_DIR}/references/schemas.md`. The `expectations` array must use
the fields `text` / `passed` / `evidence` — the viewer depends on those exact
names. Prefer a script for programmatically-checkable assertions over eyeballing.

## 2. Benchmark — aggregate, then analyst pass

```
uv run python -m scripts.aggregate_benchmark evals/{skill-name}/iteration-N --skill-name {skill-name}
```

This emits `benchmark.json` + `benchmark.md`: pass-rate / time / tokens, mean ±
stddev, and the with-skill vs. baseline delta. Place each `with_skill` run before
its baseline counterpart. If you ever hand-write `benchmark.json`, match
`references/schemas.md` exactly (`configuration` must be `with_skill` /
`without_skill`; `result` fields stay nested) or the viewer shows zeros.

Then do an **analyst pass**: read `${CLAUDE_SKILL_DIR}/agents/analyzer.md` and
surface what the aggregate hides — non-discriminating assertions (pass regardless
of skill), high-variance evals (possibly flaky), and time/token-vs-quality
tradeoffs. These notes feed the benchmark report's analyst section.

## 3. Report for the user — and wait for feedback BEFORE you rewrite

Generate the interactive HTML report:

```
uv run python eval-viewer/generate_review.py evals/{skill-name}/iteration-N \
  --skill-name {skill-name} \
  --benchmark evals/{skill-name}/iteration-N/benchmark.json
```

For iteration 2+, add `--previous-workspace evals/{skill-name}/iteration-<N-1>`
so the report shows last iteration's outputs and feedback inline.

In headless / background runs (no display) write a standalone file with
`--static evals/{skill-name}/iteration-N/review.html` instead of serving — the
"Submit All Reviews" button then downloads `feedback.json`, which you copy into
the iteration dir.

The report has two tabs. **Outputs:** one eval at a time — prompt, the produced
files rendered inline, previous output (collapsed, iter 2+), formal grades
(collapsed), and an auto-saving feedback box. **Benchmark:** pass rates, timing,
token usage per configuration, with the analyst notes.

This is a first-class step, not an afterthought: **get the outputs in front of
the user and wait for `feedback.json` before you self-evaluate or rewrite the
skill.** Then read it:

```json
{"reviews": [{"run_id": "eval-0-with_skill", "feedback": "chart missing axis labels", "timestamp": "..."}], "status": "complete"}
```

Empty feedback means that eval was fine — focus on the ones with complaints.

## 4. Iterate

Generalize from the feedback rather than overfitting the handful of examples:
explain the *why* behind each instruction, cut lines that aren't pulling weight,
and if several transcripts independently wrote the same helper script, bundle it
into `scripts/` once. Apply the fix, then re-run every eval (with-skill and
baseline) into a fresh `iteration-N+1/`, re-report with `--previous-workspace`,
and wait for the next feedback. Stop when the user is happy, feedback is all
empty, or progress flatlines.

## 5. Edit / regression path

When updating an **existing** skill, don't start the suite from scratch — re-use
its `{skill-dir}/evals/` suite as the regression baseline (it's still valid;
review/extend assertions only when the edit intentionally changes scope).
Snapshot the prior skill version as the comparison baseline before editing
(`cp -r {skill-dir} evals/{skill-name}/skill-snapshot/`), point the baseline
subagent at the snapshot, and run a fresh `iteration-N`.

## 6. Triggering optimization

When triggering accuracy is the bottleneck (skill fires when it shouldn't or
won't fire when it should), run the scripted loop. It shells out to the `claude`
CLI (`claude -p`), so the `claude` CLI must be installed and `--model` must be set.
Pass a model **alias** (`sonnet`/`opus`/`haiku`) so it tracks the latest, not a
pinned dated id. The `sonnet` alias is enough for this high-volume loop;
triggering is model-sensitive, so confirm the final `best_description` on your
production model.

**Sign off the trigger queries first.** Build ~20 realistic should- /
should-not-trigger queries (concrete: file paths, column names, casual phrasing,
near-miss negatives — not toy examples), then review them with the user via the
template `${CLAUDE_SKILL_DIR}/assets/eval_review.html`: substitute
`__EVAL_DATA_PLACEHOLDER__` (the JSON array, unquoted), `__SKILL_NAME_PLACEHOLDER__`,
and `__SKILL_DESCRIPTION_PLACEHOLDER__`; write to a temp file; the user edits,
toggles, and clicks "Export Eval Set" to download the signed-off set. Bad queries
make bad descriptions, so this sign-off matters.

Then run the loop in the background:

```
uv run python -m scripts.run_loop \
  --eval-set evals/{skill-name}/trigger-eval.json \
  --skill-path {skill-dir} \
  --model sonnet \
  --max-iterations 5 \
  --results-dir evals/{skill-name}/triggering \
  --verbose
```

It splits the set 60% train / 40% held-out test, evaluates the current
description (each query run `--runs-per-query` times, default 3, for a stable
trigger rate), calls Claude to propose improvements on what failed, and
re-evaluates on both splits up to `--max-iterations`. It writes a timestamped
subdir under `--results-dir` (`results.json`, `report.html`, `log.txt`) and emits
its HTML via `scripts.generate_report`. Tail `log.txt` to update the user as it
runs. The returned `best_description` is chosen by **held-out test** score (not
train) to avoid overfitting — apply it to the SKILL.md frontmatter and show the
user before/after with the scores.

Underlying pieces, if you need finer control: `scripts.run_eval` runs one trigger
eval for a given description; `scripts.improve_description` proposes one improved
description from eval results; `scripts.generate_report <results.json> -o report.html`
renders the loop's HTML.

## 7. Blind comparison (advanced / optional)

For a rigorous "is the new version actually better?" check, give two outputs to an
independent agent without telling it which is which and let it judge. Read
`${CLAUDE_SKILL_DIR}/agents/comparator.md` for the blind A/B judging, then
`${CLAUDE_SKILL_DIR}/agents/analyzer.md` to analyze *why* the winner won. Optional
— the human review loop is usually enough.

## 8. Package

```
uv run --with pyyaml python -m scripts.quick_validate .        # must print "Skill is valid!"
uv run python -m scripts.package_skill {skill-dir} dist/
```

Write the `.skill` to `dist/` (or hand it directly to the user) — never into
`evals/`. Run the pre-ship checklist at the bottom of
`${CLAUDE_SKILL_DIR}/references/anti-patterns.md` before packaging.
