---
paths:
  - "products/**/*"
  - ".claude/commands/c-suite/**"
---

# CPO Department Operations

Canonical command prefix: /c-suite:cpo-

## Engagement Folder Schema

Every engagement lives at `products/<client-slug>/`:

```text
products/<client-slug>/
  status.md
  discovery/
  prd/
  design/
```

## Status Ledger

`status.md` tracks one state per stage — `intake`, `prd`, `brief` — from:

`not-started | in-progress | blocked-on-client | stale | done`

Plus one engagement-level field: `engagement: handed-off` once the design
package is approved.

## Stage Preflight Gates

- `cpo-prd` requires `intake: done`, else STOP.
- `cpo-brief` requires `prd: done` AND either `prd-gate: approved` (with an approved `prd-review` verdict report) or `prd-gate: accepted-with-noted-gaps`; `none`/`needs-human` never pass, else STOP.
- If the stage's predecessor is `stale`, ask the user to confirm before
  proceeding — never silently resume on stale input.

## Engagement Git Flow

**Real mode** (ordinary client slug):

- Resume lookup runs before any creation; a new engagement creates the issue, the branch
  `feat/<N>-<client-slug>`, and its worktree, then ENTERS that worktree BEFORE scaffolding
  `products/<client-slug>/`. Every engagement artifact is created and modified only inside
  that worktree.
- One GitHub issue + one branch `feat/<N>-<client-slug>` per engagement.
- Every stage commit carries `Refs #N` in its footer.
- Push with the explicit refspec:
  `git push origin HEAD:refs/heads/feat/<N>-<client-slug>`
- Exactly ONE PR, opened after Design-Lead approval, closes the issue.

**Fixture mode** (`_example-` slug prefix):

- No issue, no branch, no worktree, no PR.
- Stages commit directly on the current (hosting) branch.
- The ledger records `mode: fixture` and the hosting branch.
- Each recorded stage run is two commits on that branch — a deliverable commit carrying the
  stage artifacts, then a ledger commit carrying the state + run-log update; the run-log
  `sha=` names the DELIVERABLE commit, never the ledger commit.
