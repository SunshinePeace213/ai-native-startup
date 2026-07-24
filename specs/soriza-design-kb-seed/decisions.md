# Decisions: Seed the design KB group + worktree availability (child #44 of epic #43)

> The interview record for [spec.md](./spec.md) — why the plan is the way it is. Lifecycle tracking and
> the Codex review record live in spec.md, NOT here; this file is the immutable decision history.
> Every decision below is **transcribed from the epic ledger**
> ([specs/soriza-cpo-department/decisions.md](../soriza-cpo-department/decisions.md) and
> issue #44's body) — nothing was re-litigated and nothing was asked (ledger-complete).

## Summary

Child #44 of epic #43 seeds the KB for the soriza-design department: `.worktreeinclude`
gains an `ai-docs/*` pattern so gitignored mirrors reach every fresh worktree, a new
`design/` group gets five official sources (structure, accessibility, IA, copy, typography),
and the `anthropic` group gains the official memory/rules docs page found missing at epic
plan time. All registration flows through `/harness-layer:kb add`; mirrors are fetched,
never hand-authored; only `.worktreeinclude` and `ai-docs/sources.yaml` are tracked changes.

## Resolved Decisions

- **Q:** How do KB mirrors reach fresh worktrees?
  - **A:** Add a single `ai-docs/*` pattern (with a one-line comment) to `.worktreeinclude`.
  - **Why:** Epic ledger decision "KB — worktree availability and the design/ first cut".
    Gap confirmed at `.gitignore` (`ai-docs/*` + `!ai-docs/sources.yaml`): mirrors are
    ignored, so a fresh worktree gets only the manifest. Rules out tracking mirrors in git
    and out per-worktree manual syncs as the default path.

- **Q:** Does `.worktreeinclude` even apply, given the repo's `WorktreeCreate` hook?
  - **A:** Yes — the hook replaces stock processing but re-implements the copy itself
    (`copy_worktree_includes()` in `worktree_create.py`: `fnmatch` of each pattern against
    the relative path or basename of every `git ls-files -oi --exclude-standard` file).
    `fnmatch`'s `*` crosses `/`, so `ai-docs/*` covers nested mirrors.
  - **Why:** Conflict reconciled at epic plan time (official caveat vs. ledger decision) —
    resolved in repo source; re-verified against `worktree_create.py` lines 45–87 and the
    KB mirrors this run. Rules out needing `ai-docs/**` or per-folder patterns.

- **Q:** Which sources seed the `design/` group?
  - **A:** Exactly five: W3C WCAG 2.2 quickref, web.dev Learn Design, one NN/g homepage
    cornerstone, NN/g writing-for-the-web, Google Fonts Knowledge (identity table in
    spec.md `## Requirements & Decisions`).
  - **Why:** Epic ledger — the lean trio grounds structure/accessibility; the two additions
    ground copy and typography per Ringo's client-feedback experience. Rules out the broad
    sweep and deferring the seed.

- **Q:** How are sources registered?
  - **A:** `/harness-layer:kb add <url> design` per source — six sequential `add` runs, the
    group argument always explicit; fetching fans out to `kb-fetcher` subagents per the kb
    command's contract.
  - **Why:** The manifest is the source of truth and `add` registers-then-syncs just the new
    entry. Host-based group defaulting would misfile w3.org/web.dev/nngroup/fonts.google.com
    (issue #44 body). Rules out hand-editing sources.yaml followed by a bulk sync, and rules
    out `--force`.

- **Q:** What about the missing official memory docs page?
  - **A:** Register `https://code.claude.com/docs/en/memory` under `anthropic` in this child.
  - **Why:** Epic ledger "Memory-doc gap folded into #44" — gap-fill by subagent was
    permission-denied at epic plan time and mirrors are never hand-written, so the gap rides
    with this child's kb runs.

- **Q:** What happens when a source refuses fetching or mirrors thin?
  - **A:** `/kb` reports `FAIL` and leaves `fetched: null`; the build substitutes the
    canonical same-topic page (WCAG fallback: `https://www.w3.org/TR/WCAG22/`) and records
    the swap here as a build addendum. Never hand-author a mirror, never fake a `fetched`
    date. NN/g blocked entirely → stop and propose a different official source to Ringo.
  - **Why:** Epic edge case "KB source refuses fetching" + plan-time assumptions.

- **Q:** Child pipeline mechanics?
  - **A:** Issue #44 pre-filed (no issue creation); branch `chore/44-soriza-design-kb-seed`
    linked via `gh issue develop 44`; worktree
    `.claude/worktrees/soriza-design-kb-seed`; builders kb-builder (`sonnet`/`low`) and
    validator (`sonnet`/`low`) per the epic's stamps; one pipeline run for this child, its
    PR closes #44.
  - **Why:** Epic plan-level decisions (child slugs/branches, one run per child) and task 2's
    launch prompt.

- **Q:** Who hydrates the main checkout after this merges?
  - **A:** The epic driver — `/harness-layer:kb` in the main checkout after #44's PR merges,
    before any dependent child worktree is created. Out of this child's scope.
  - **Why:** `.worktreeinclude` copies only files present in the creating checkout; this
    worktree's mirrors never land on `main` (epic hydration hand-off).

### Plan-level decisions

- **Complexity: simple** — a one-line include edit plus six guarded kb runs. Conditional
  spec sections (Problem Statement / Solution Approach / Implementation Phases) are omitted
  per the templates, and no implementation-plan artifact page is authored (simple plans skip
  artifacts).
- **Validation simulates the hook in-place** instead of creating a scratch worktree: a live
  `WorktreeCreate` run resolves its root to the main checkout (`CLAUDE_PROJECT_DIR`), which
  won't carry this branch's `.worktreeinclude` until merge — so the child asserts the exact
  `fnmatch`-against-`git ls-files -oi` semantics from `worktree_create.py` against this
  worktree's real mirror paths. The end-to-end scratch-worktree check belongs to the epic's
  `validate-all` on `main` (epic AC2).
- **AC mapping to the epic:** child AC1 realizes epic AC2's pre-merge half (pattern +
  matching semantics); child AC2–AC5 realize epic AC3; child AC6 keeps the PR surface exactly
  scoped. Epic AC2's worktree-receives-mirrors half lands with the epic driver's hydration.

### Build addendum — kb run record

Appended by kb-builder at build time — the observable provenance record validation parses.
One line per `/harness-layer:kb add` run, verbatim from the kb report:

- `- OK <file> <canonical url>` for every successfully mirrored source (six lines when done);
- additionally, for any identity-table substitution:
  `- FAIL <original url> → swapped to <substitute url>: <reason>`.

No lines yet — the build appends them. A mirror without its OK line here fails AC2.

## Assumptions

- **NN/g exact URLs are picked at build** — proposed homepage cornerstone:
  `https://www.nngroup.com/articles/top-10-guidelines-for-homepage-usability/`; the
  writing-for-the-web pick must be a canonical `nngroup.com/articles/…` page so the epic's
  AC3 check (exactly two `articles/` URLs, one containing `homepage`) passes. Invalidated if
  NN/g blocks mirroring entirely — then a different official IA/copy source is proposed to
  Ringo before the build proceeds.
- **WCAG 2.2 quickref may mirror thin** (JS-heavy app) — fallback is the spec page
  `https://www.w3.org/TR/WCAG22/`, recorded as a swap. Invalidated only if both refuse.
- **The memory page is registered extensionless** (`https://code.claude.com/docs/en/memory`)
  matching the manifest's uniform convention for the 18 existing code.claude.com entries;
  kb canonicalization may rewrite it (the docs server also serves a raw `memory.md` form —
  cross-check note below). Validation matches by substring, so either canonical form passes.
- **Each `add` syncs only its own entry** (kb contract: `add` selects just the new entry;
  existing entries are < 30 days old, so no stale work set). Invalidated if the build runs
  land after the existing entries go stale — then the sync grows a refresh work set, which
  is acceptable but must be reported, not hidden.

## Open Questions / Out of Scope

- **Out of scope:** hydrating the main checkout (`/harness-layer:kb` there) — epic driver,
  after this PR merges (epic task 2 hand-off).
- **Out of scope:** doctrine authoring from these sources — #45.
- **Out of scope:** refreshing or evicting existing KB entries — all fresh, count stays
  under the ≈40 cap (32 after this child).
- **Out of scope:** any edit to `worktree_create.py`, `.gitignore`, or `ai-docs/index.md`.
- **Open question:** none — the epic ledger closed every decision this child needs.

## KB References

Docs consulted for this plan's harness claims (review profile: **kb-grounded**):

- `ai-docs/anthropic/worktrees.md` (fetched 2026-07-23) — `.worktreeinclude` contract
  (gitignore syntax; only pattern-matching AND gitignored files copy; §"Copy gitignored
  files into worktrees") and the caveat that a configured `WorktreeCreate` hook skips stock
  processing (§"Non-git version control").
- `ai-docs/anthropic/hooks.md` (fetched 2026-07-23) — §WorktreeCreate: the hook replaces
  default git behavior entirely; `.worktreeinclude` is not processed; copying happens inside
  the hook script.

Read-path note: this worktree predates the very pattern this child adds, so it holds no
mirrors — the docs above were read from the main checkout
(`/Users/ringo/Desktop/ai-native-startup/ai-docs/`, whose manifest records the 2026-07-23
refresh). Neither doc is stale (< 30 days). Repo source consulted alongside:
`worktree_create.py` (the fnmatch copy), `.claude/commands/harness-layer/kb.md` (the add
contract), `.gitignore` (the ignore gap).

Cross-check (`claude-code-guide` subagent, this run):

- `.worktreeinclude` contract — **confirmed**.
- WorktreeCreate replaces default processing — **confirmed**.
- Memory-page URL — the guide reports the canonical fetchable form as
  `code.claude.com/docs/en/memory.md` (the raw-markdown variant). **Resolved:** register the
  extensionless page URL per the manifest's uniform convention for all existing
  code.claude.com entries and let kb's canonicalization settle the final stored form;
  validation matches by substring either way. Non-blocking; logged here.
- Command-driven subagent fan-out — partially documented officially; the operative ground is
  this repo's own working `/harness-layer:kb` command and `kb-fetcher` agent (precedent, not
  a new capability claim).

### Follow-ups (advisories, future plans)

- None yet — appended by the Codex review rounds if advisories arrive.
