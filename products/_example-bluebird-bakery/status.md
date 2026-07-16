# Engagement Ledger — Bluebird Bakery

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

mode: fixture
issue: none
branch: none
hosting-branch: worktree-c-suite-cpo-department
PR: none

## Stage state

intake: done
prd: done
brief: done
engagement: handed-off

## Run log

intake-run: date=2026-07-17; sha=d53956e; lessons=persona-type fallback lesson recorded
intake-run: date=2026-07-17; sha=fa32998; lessons=none
prd-run: date=2026-07-17; sha=b94cc0d; lessons=none
brief-run: date=2026-07-17; sha=78889a3; lessons=fix-pass regression lesson recorded
