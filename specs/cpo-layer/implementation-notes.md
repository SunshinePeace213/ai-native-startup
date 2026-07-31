# Implementation Notes: studio-layer — design-delivery studio through signed handoff

> Chronological dev log for [spec.md](./spec.md), created from this template at
> `/harness-layer:harness-build` implement start and appended by both
> `/harness-layer:harness-build` and `/harness-layer:harness-review` as the work
> proceeds. Entries land at each checkpoint commit, the moment the event happens;
> the PR body and build brief are derived from these notes — never reconstructed.
>
> Boundary: per-plan phases, hand-offs, deviations, fixes, and lessons live here.
> A lesson worth keeping beyond this plan is routed to its rule-file home by the
> memory step per memory-series.md.

## Log

<!-- Append-only; one entry per phase, hand-off, deviation, fix, or lesson — never edit or
     delete a prior entry. "No entries yet" is a valid starting body. -->

- **2026-08-01 · build start** — worktree `.claude/worktrees/cpo-layer` on branch
  `worktree-cpo-layer` (remote `feat/80-cpo-layer`), plan approved at the human gate,
  review profile `kb-grounded`.
  - `uv run pytest -q` → `875 passed, 2 skipped in 22.62s` — baseline before any build change.
- **2026-08-01 · phase 1 (ground the namespace)** — launched `studio-namespace`, `studio-roster`,
  `studio-client-artifacts`, `studio-question-bank` and `gate-signoff-hook` as concurrent
  builders; their **Files** fields are the disjointness contract.
- **2026-08-01 · hand-off `studio-namespace`** — `.gitignore`, `clients/.gitkeep`,
  `.claude/rules/studio-layer/studio-identity.md`, `AGENTS.md`
  - `git check-ignore -v clients/acme/site/brief.md` → `.gitignore:378:clients/* clients/acme/site/brief.md`
  - `git check-ignore -q clients/.gitkeep; echo $?` → `1` — the negation re-includes the contract file.
  - `bash specs/cpo-layer/checks/ac1-client-data-home.sh` → `AC1 pass: clients/ is contracted,
    ignored, and invisible to the spec gate`, exit 0. The builder's own run of this check
    returned exit 1 on two counts, both because `clients/.gitkeep` was still untracked — the
    builder is barred from `git add`, so the lead staged and committed it and the check went
    green with no file change.
  - `bash specs/cpo-layer/checks/ac5-rules-path-scoped.sh` → exit 1, reporting only
    `roster.md is missing` / `client-artifacts.md is missing` / `expected at least 3 studio
    rules, found 1`. No failure against `studio-identity.md`: it cleared the scope, name,
    voice, letterhead, sign-off and ≥400-char body assertions. Pending the two concurrent rules.
  - Deviations: none.
