# Evaluating a Skill

Three layers, cheapest first. Each gates the next, so a skill that fails the free
check never spends on the expensive one.

| Layer | Asks | Cost |
| --- | --- | --- |
| **lint** | Is the body free of the patterns that hurt a Claude 5 reader? | Free |
| **trigger** | Does the description fire on the queries users type, and stay quiet on near-misses? | ~20 queries × k |
| **behavior** | Does the body beat no-skill baseline on real tasks? | evals × 2 × k |

Run every command from this skill's directory so `scripts.` resolves.

```bash
uv run --with pyyaml python -m scripts.eval <skill-dir>          # lint, then plan the rest
uv run --with pyyaml python -m scripts.eval <skill-dir> --yes    # execute all three
uv run --with pyyaml python -m scripts.eval <skill-dir> --lint   # one layer alone
```

Without `--yes` this lints and prints what the paid layers would cost. Nothing
bills until you pass it.

## The suite is committed; the runs are not

`evals/evals.json` and `evals/trigger-eval.json` live in the skill directory and
go into git — they are the regression suite, and re-running them after an edit
is what makes them worth writing. Run artifacts land in a sibling
`<skill-name>-workspace/`, which is gitignored.

## Writing evals.json

```json
{
  "skill_name": "release-notes",
  "evals": [
    {
      "id": 0,
      "name": "groups-by-change-type",
      "prompt": "Turn CHANGELOG.md in this directory into release notes. Save them as NOTES.md.",
      "files": ["evals/files/CHANGELOG.md"],
      "assertions": [
        {"id": "a1", "text": "NOTES.md exists", "check": "test -f NOTES.md"},
        {"id": "a2", "text": "It mentions the CSV export", "check": "grep -qi csv NOTES.md"},
        {"id": "a3", "text": "Entries are grouped by change type"}
      ]
    }
  ]
}
```

Two or three evals is enough to start. Write the prompt a real user would type,
not a description of the task.

An assertion with a `check` runs as a shell command in the run's output
directory; exit 0 passes. One without goes to a judge that sees the task and the
produced files — never the transcript the executor wrote about itself. Prefer a
`check` wherever the outcome is mechanically decidable: it is free, exact, and
identical across runs. Reserve the judge for things like "grouped by change
type" that genuinely need reading.

A good assertion fails when the skill fails. "A file was created" passes for a
file with the wrong contents in it, so it discriminates nothing.

Skills with subjective outputs — writing voice, visual design — often shouldn't
have behavior evals at all. Lint and trigger still apply.

## Reading the result

```text
eval-<id>/<config>/run-<k>/{outputs/, grading.json, timing.json, result.md}
```

The runner creates this layout itself; nothing hand-builds it. `result.md` is
the assistant's closing text, kept for diagnosing a run that produced no files.

`benchmark.json` reports each configuration's pass rate as mean ± stddev across
the k repeats, plus the delta. **The spread is the point.** At k=1 there is no
spread and any delta is noise; k=3 is the default for that reason. When the two
configurations' intervals overlap, the honest reading is "no measured
difference", not "the skill won".

A skill that doesn't beat baseline isn't pulling its weight — that is a real
result, and it usually means the body is telling the model things it already
does.

## Iterating

Improve the skill, then rerun into a fresh iteration:

```bash
uv run --with pyyaml python -m scripts.eval <skill-dir> --behavior --iteration 2 --yes
```

When you improve rather than create, snapshot the old version first
(`cp -r <skill-dir> <workspace>/skill-snapshot/`) so the baseline is the version
you're trying to beat.

Read the run outputs, not only the scores. If the skill made the model do
unproductive work, cut the lines causing it. If several runs independently wrote
the same helper script, write it once into `scripts/` and point the skill at it.

Generalize from what you learn. The skill will run on prompts nobody imagined;
tuning it until these three pass makes it worse everywhere else. For a stubborn
issue, try a different framing rather than piling on constraints.

## Optional: the review viewer

For qualitative review of the outputs with a human in the loop:

```bash
uv run python ${CLAUDE_SKILL_DIR}/eval-viewer/generate_review.py \
  <workspace>/iteration-N --skill-name <name> \
  --benchmark <workspace>/iteration-N/benchmark.json
```

Add `--previous-workspace <workspace>/iteration-<N-1>` from iteration 2 on, and
`--static <path>` when there's no display — "Submit All Reviews" then downloads
`feedback.json` to copy back into the iteration directory. Use this script
rather than hand-written HTML. Empty feedback on a case means it was fine.

## Optional: blind comparison

To settle "is the new version actually better", hand both outputs to an
independent agent without saying which is which — `agents/comparator.md`, then
`agents/analyzer.md` for why the winner won.

## Description optimization

Once the skill works, tune the description for triggering.

Generate ~20 queries, 8–10 that should trigger and 8–10 that shouldn't, saved as
`evals/trigger-eval.json`:

```json
[{"query": "...", "should_trigger": true}]
```

Make them realistic — casual phrasing, typos, enough backstory to be a real
request. Should-trigger queries cover phrasings that never name the skill.
Should-not queries are near-misses that share vocabulary but need something
else; an obviously irrelevant negative tests nothing. Claude only consults
skills for tasks it can't trivially handle, so one-step queries are poor test
cases regardless of description quality.

**Keep the detail in the task, not in a premise about the repo.** A query like
"package up the invoice-parser skill" sends Claude hunting the filesystem for an
`invoice-parser` that the probe project doesn't contain; it searches, finds
nothing, reports back, and never consults any skill. The query scores as a miss
and tells you nothing about the description. Describe the situation instead of
naming files that have to exist.

**Every probe run gets its own throwaway project, and that isolation is load-
bearing in three ways.** Don't collapse it back to a shared or in-repo root:

- A skill already installed where the probe runs carries the same description
  and a real body, so Claude consults that one and every query scores as a miss.
- Concurrent workers each plant a uniquely-named probe. Sharing one root puts N
  near-identical skills in the listing at once; each worker only recognizes its
  own name, so the measured rate collapses toward 1/N no matter how good the
  description is.
- `claude -p` runs the query to completion. Pointed at a real repository it will
  *do the task* — writing files and editing memory as a side effect of a test
  that was only ever meant to observe routing.

A run that never completes is reported as unmeasured rather than as a miss;
scoring a timeout as "did not trigger" turns harness flakiness into a phantom
description defect. If you see unmeasured queries, lower `--concurrency`.

Sign the set off with the user through `assets/eval_review.html` — substitute
`__EVAL_DATA_PLACEHOLDER__` (the raw JSON array, unquoted),
`__SKILL_NAME_PLACEHOLDER__`, and `__SKILL_DESCRIPTION_PLACEHOLDER__`, write it
to a temp file, and let them edit and export. Bad queries make bad descriptions.

Then run the search:

```bash
uv run python -m scripts.run_loop \
  --eval-set <skill-dir>/evals/trigger-eval.json \
  --skill-path <skill-dir> \
  --model sonnet --max-iterations 5 \
  --results-dir <workspace>/triggering --verbose
```

It splits 60% train / 40% held-out, runs each query 3 times, proposes
descriptions from the failures, and returns `best_description` chosen on the
held-out score. `sonnet` is enough for this high-volume search; confirm the
winner on the session's model, since triggering is model-sensitive. Apply it and
show the before/after with the scores.
