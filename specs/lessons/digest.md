# Lessons Digest

Rolling process memory for the pipeline. `/harness-layer:harness-plan` reads the
category table for the touched surface before drafting; `/harness-layer:harness-ship`'s
light pass folds each shipped plan's findings ledger and metrics row in here; the
deep pass (`/harness-layer:harness-lessons`) turns recurring rows into standard,
template, or lint amendments. An uncited finding class seen 2+ times is a candidate
new standard.

## Categories

One row per recurring finding class — the class, not an instance. `Seen` counts
occurrences across all shipped ledgers; `Disposition` is `watching` until an
amendment lands, then `amended (<file>)` or `lint added (<script>)`.

| Surface | Category | Seen | Plans | Disposition |
| --- | --- | --- | --- | --- |
| specs/checks | false-passing-validator — a check that passes without proving its criterion (extra rows, substring matches, vacuous quantifiers) | 10× | #80 | watching |
| specs | unrunnable-validation-command — a named runner cannot reach, collect, or grade its target | 3× | #80 | lint added (`scripts/spec_lint.py` command-runnable) |
| specs/checks | path-containment-missing — a validator joins caller-supplied paths without containment, so traversal or symlinks escape the project root | 3× | #80 | watching |
| outcome docs | stale-counts — summary, dev report, or spec carrying counts and statuses that contradict the ledger they summarize | 5× | #80 | watching |
| fix rounds | regression-in-fix — a fix commit introducing new blocking defects the delta round then finds | 4× | #80 | watching |
| eval harness | unfaithful-environment — a staged scratch copy missing what the code resolves against (git repo, env, referenced files) | 1× | #80 | watching |

## Metrics log

One row per shipped plan, appended at ship time from its `summary.md` `## Metrics`
block — the trailing-5 window the production-ready targets are measured over.
`—` marks fields that predate the field's introduction.

| Plan | Lane | Spec cycles (blk/adv) | Impl cycles (blk/adv) | By standard | Uncited→adv | Fix commits | Unverified tail | Disputed | Overridden | Lint catches |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| cpo-layer (#80, backfilled) | full | 4 (32/20) | 4 (23/11) | — | — | 10 | yes | 0 | 1 | — |
| focus-typo (#85) | direct | — | 1 (0/0) | none | 0 | 0 | no | 0 | 0 | spec —, impl 0 |
