# Engagement Ledger — <Client Name>

The single source of truth for where this engagement stands. The stage commands read and
write it on every run.

Legend:

- Stage state (`intake`, `prd`, `brief`): `not-started | in-progress | blocked-on-client | stale | done`.
- Engagement state: add `engagement: handed-off` when the brief stage completes.
- Real mode fills `issue`, `branch`, and `PR`, and writes `hosting-branch: none`.
- Fixture mode (an `_example-` slug) writes `issue: none`, `branch: none`, `PR: none`,
  puts the current local branch under `hosting-branch:`, and records each stage's commit
  SHA in that stage's run log.
- Run-log `lessons=<result>` is the lessons-check outcome for that run (`none` allowed).

## Engagement

mode: <real | fixture>
issue: <#N | none>
branch: <feat/N-client-slug | none>
hosting-branch: <none | current-local-branch>
PR: <url | none>

## Stage state

intake: <state>
prd: <state>
brief: <state>
engagement: <not-yet | handed-off>

## Run log

intake-run: date=<date>; sha=<sha>; lessons=<result>
prd-run: date=<date>; sha=<sha>; lessons=<result>
brief-run: date=<date>; sha=<sha>; lessons=<result>
