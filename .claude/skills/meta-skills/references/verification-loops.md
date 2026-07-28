# Verification Loops

A verification loop is a check the model runs on its own work and fixes before
moving on. Skills are the natural home for one: the check is procedural, it
should run the same way every time, and it costs nothing until it fires.

Write the check the way you'd hand it to a new teammate on day one. The bar is
not "is this qualitative" — "reject any migration that drops a column without a
backfill" is a deterministic rule no generic linter catches. Anything you keep
enforcing by hand qualifies.

## Pick the deployment shape

| Shape | The check runs | Choose when |
| --- | --- | --- |
| **Standalone** | When the user invokes it | Cross-cutting checks that don't apply every time — a pre-commit security scan, a license-header sweep. The cost is remembering to run it |
| **Embedded** | Automatically, at the end of the producing skill | The check belongs to exactly one workflow. Usually a one-line append to that skill's body |
| **Chained** | One skill invokes the next at its end | Several verified handoffs run end to end. Also the way to add a check to a skill you can't edit: wrap it |
| **On every PR** | In CI, for everyone | The chain is stable and you want it applied regardless of who wrote the change |

The signal you've outgrown standalone is running it after every change. The
signal to hold off on a PR-wide gate is a chain still in flux — every adjustment
becomes a team-visible event.

Embedded only works on skills you control. Plugin-managed skills get overwritten
on update; chain those instead.

## Where the guarantee lives

A skill body is a preference — followed most of the time, and least reliably
under pressure, in long sessions, or against a prompt injection. When a check
*must* run, put it in the harness:

- `hooks:` in the skill's own frontmatter — scoped to that skill, active only
  while it runs.
- A `PreToolUse` hook exiting 2 to block a call outright.
- A `Stop` hook that verifies the job is done before the turn can end.

Reach for prose when you want the model's judgment applied; reach for a hook
when you want a fact enforced.

## In this repo

A skill's own eval suite is a verification loop for the skill itself — see
[evaluation.md](evaluation.md). Once `evals/` is committed, re-running it after
an edit is the check, and it chains into
`/harness-layer:harness-review` the same way any other gate does.
