# Grading Contract

`scripts/run_behavior_eval.py` grades every run automatically: assertions with a
`check` run as shell commands, the rest go to a fresh-context judge. This
document is the contract that judge works to — read it when grading by hand, or
when a run's verdicts look wrong and you need to know what the bar was.

## What the judge sees

The task prompt and the files the run produced. Not the transcript. A model
grading its own narration of what it did will confirm claims the files don't
support, so the files are the only evidence that counts.

## The bar

A verdict passes when the produced files show the assertion satisfied in
substance. It fails when they don't, and when they don't settle it.

The failure mode worth guarding against is surface compliance: the right
filename with empty or wrong contents, a document that mentions the required
term in an unrelated sentence, output that matches the shape of success without
doing the work. When the assertion is technically satisfied but the underlying
outcome is wrong, that is a fail.

No partial credit — each assertion is pass or fail.

## Output shape

```json
{"verdicts": [
  {"id": "a1", "passed": true, "evidence": "what in the files decided it"}
]}
```

Merged into `grading.json` as `expectations[]` with `text`, `passed`, and
`evidence` — those exact names, because the aggregator and the viewer read them.

## Critique the evals while you're in there

A passing grade on a weak assertion is worse than no assertion at all: it
manufactures confidence. Worth raising, when you see it:

- An assertion that passed but would also pass for a clearly wrong output.
- An outcome you observed — good or bad — that no assertion covers.
- An assertion the available files can't settle either way.

Keep the bar high enough that each note is one the eval's author would thank you
for. These go to the human, not into `grading.json`.
