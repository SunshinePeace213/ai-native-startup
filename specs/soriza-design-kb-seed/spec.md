# Spec: Seed the design KB group + worktree availability (child #44 of epic #43)

- **Owner:** @SunshinePeace213
- **Status:** Approved
  <!-- Lifecycle, set by /harness-layer:harness-plan: Drafted for Review → Approved (on a Codex
       `approved` verdict). A cycle that ends still changes-requested — or with Codex unavailable —
       records needs-human in ## Codex Verification and keeps this status. One value only. -->

## Task Description

Execute exactly task 2 of the epic master plan
([specs/soriza-cpo-department/tasks.md](../soriza-cpo-department/tasks.md)): make the
`ai-docs/` knowledge base reach every fresh worktree, and seed the design knowledge the
soriza-design department's doctrine (#45) will draft from.

Three deliverables, all mechanical:

1. **`.worktreeinclude`** gains an `ai-docs/*` pattern with a one-line comment above it, so
   the gitignored KB mirrors copy into every worktree the repo's `WorktreeCreate` hook creates.
2. **`design/` KB group** — five official sources registered and mirrored via
   `/harness-layer:kb add <url> design` (explicit group argument — host-based defaulting would
   misfile them): W3C WCAG 2.2 quickref, web.dev Learn Design, NN/g homepage cornerstone,
   NN/g writing-for-the-web, and the web.dev Learn Design typography module (epic-authorized
   swap — `fonts.google.com/knowledge` is a JS-only SPA shell that mirrors empty).
3. **Anthropic memory page** — `https://code.claude.com/docs/en/memory` registered and
   mirrored under the `anthropic` group (gap found at epic plan time).

Fetch failures are substituted with the canonical same-topic page and the swap recorded in
this plan's decisions.md — mirrors are never hand-authored and `fetched` dates never faked.
This spec transcribes the epic's locked decisions
([spec.md](../soriza-cpo-department/spec.md), [decisions.md](../soriza-cpo-department/decisions.md));
nothing is re-litigated.

## Objective

`.worktreeinclude` carries the `ai-docs/*` pattern, `ai-docs/sources.yaml` carries the five
`design` entries plus the `anthropic` memory entry — each with a canonical `url`, a `file`
under its group folder, and a non-null `fetched` date — the six mirrors and a regenerated
`ai-docs/index.md` exist on disk in this worktree, and the branch's tracked change surface
outside `specs/` is exactly `.worktreeinclude` + `ai-docs/sources.yaml`.

## Non-Goals

- **Hydrating the main checkout** — mirrors are gitignored and never land on `main` via this
  PR; the epic driver runs `/harness-layer:kb` in the main checkout after this PR merges,
  before creating any dependent child's worktree (epic task 2's hydration hand-off).
- **Authoring doctrine from these sources** — that is #45.
- **Refreshing existing KB entries** — the 26 current entries are fresh (< 30 days); no
  `--force` sync, no eviction.
- **Touching the WorktreeCreate hook** — `worktree_create.py` already implements the
  `.worktreeinclude` copy; it is read-only here.
- **Hand-authored mirrors** — a source that refuses fetching gets a canonical substitute,
  never a homegrown file under `ai-docs/`.

## Requirements & Decisions

Volatile first — full record in [decisions.md](./decisions.md):

1. **Source identities** (most likely to change — two NN/g URLs are picked at build):

   | # | Source | Registered URL | Group |
   | --- | --- | --- | --- |
   | 1 | W3C WCAG 2.2 quickref | `https://www.w3.org/WAI/WCAG22/quickref/` | `design` |
   | 2 | web.dev Learn Design | `https://web.dev/learn/design` | `design` |
   | 3 | NN/g homepage cornerstone | `https://www.nngroup.com/articles/113-design-guidelines-homepage-usability/` (build-time swap — proposed Top-10 digest URL 404'd; epic-driver-authorized, recorded in decisions.md build addendum) | `design` |
   | 4 | NN/g writing for the web | `https://www.nngroup.com/articles/how-users-read-on-the-web/` (build-time pick) | `design` |
   | 5 | Typography — web.dev Learn Design module | `https://web.dev/learn/design/typography` (build-time swap — `https://fonts.google.com/knowledge` and its sub-pages are JS-only SPA shells that mirror empty; epic-driver-authorized, recorded in decisions.md build addendum) | `design` |
   | 6 | Claude Code memory docs | `https://code.claude.com/docs/en/memory` | `anthropic` |

   The table is the RESOLVED identity set (build evidence, 2026-07-24): rows 3 and 5 carry
   epic-authorized swaps recorded in the decisions.md build addendum, grounded in the epic
   ledger's "KB source refuses fetching" edge case. Epic constraint holds: exactly two
   `nngroup.com/articles/` URLs, one containing `homepage`. Substitution is now closed —
   any NEW fetch failure among the final five identities is a stop condition: halt the
   build and propose an official alternative to Ringo; never improvise a substitute. (The
   WCAG quickref's anticipated `https://www.w3.org/TR/WCAG22/` fallback was never needed —
   it mirrored OK.)
2. **Registration goes through `/harness-layer:kb add <url> <group>`** — the manifest is the
   source of truth, fetching fans out to `kb-fetcher` subagents per the kb command's own
   contract, and the `design` group is passed explicitly (host-based defaulting would
   misfile w3.org/web.dev/nngroup/fonts.google.com). Six sequential `add` runs; each syncs
   just its new entry, and each run's result is appended verbatim to decisions.md
   `### Build addendum — kb run record` — the observable provenance AC2 parses.
   **Replacement contract on `FAIL`:** kb has no remove operation and a failed `add` leaves
   its provisional entry `fetched: null` in the manifest — the builder deletes that
   provisional entry from `sources.yaml` (the manifest is the one hand-editable tracked
   file; registration itself still flows only through `add`), then runs one extra `add` for
   the epic-authorized substitute, appending both the FAIL/swap line and the substitute's
   OK line to the run record. Exercised twice under epic authorization (rows 3 and 5); the
   identity set is now resolved-final, so any NEW failure among the final five is a stop
   condition — no further substitutes. Final state is exactly five fully-fetched `design`
   entries.
3. **The pattern is a single `ai-docs/*` line** (plus a one-line comment above it). The
   repo's `WorktreeCreate` hook replaces stock `.worktreeinclude` processing and re-implements
   the copy with `fnmatch` against `git ls-files -oi --exclude-standard` — `fnmatch`'s `*`
   crosses `/`, so the one pattern covers every nested mirror. The existing env-file lines
   stay untouched.
4. **Tracked change surface** outside `specs/` is exactly two files: `.worktreeinclude` and
   `ai-docs/sources.yaml`. Mirrors and `ai-docs/index.md` stay gitignored — never `git add -f`.

## Tracking

<!-- Recorded by /harness-layer:harness-plan. The Issue field is the SINGLE SOURCE OF TRUTH
     /harness-layer:harness-build reads — it NEVER re-derives #N from the local `worktree-<slug>`
     branch name. spec.md is the single home for this block; decisions.md does not duplicate it. -->

- **Issue:** #44 (child of epic #43)
- **Branch:** chore/44-soriza-design-kb-seed
- **Worktree:** /Users/ringo/Desktop/ai-native-startup/.claude/worktrees/soriza-design-kb-seed
- **Review profile:** kb-grounded
- **PR:** <filled by /harness-layer:harness-build>

## Relevant Files

Use these files to complete the task:

- `.worktreeinclude` — gains the comment + `ai-docs/*` pattern; currently carries only
  env-file patterns.
- `ai-docs/sources.yaml` — gains the five `design` entries + the `anthropic` memory entry
  (26 → 32 entries, under the ≈40 cap); the only tracked file under `ai-docs/`.
- `.claude/commands/harness-layer/kb.md` — the command the builder runs (read-only): `add`
  registers then syncs just the new entry; failures report `FAIL` and leave `fetched: null`.
- `.claude/hooks/worktree/worktree_create.py` — read-only; `copy_worktree_includes()` is the
  copy mechanism the pattern feeds (`fnmatch` of each pattern against the relative path or
  basename of every untracked-and-ignored file in the creating checkout).
- `.gitignore` — read-only; `ai-docs/*` + `!ai-docs/sources.yaml` is the gap that makes the
  `.worktreeinclude` pattern necessary.

### New Files

All new files are gitignored KB output in this worktree — none are tracked:

- `ai-docs/design/<slug>.md` × 5 — the design mirrors, written by `kb-fetcher` subagents.
- `ai-docs/anthropic/<memory-slug>.md` — the memory-page mirror.
- `ai-docs/index.md` — regenerated catalog (already exists in hydrated checkouts; new to
  this worktree).

## Edge Cases

- **Source refuses fetching**: `/kb` reports `FAIL` and leaves the provisional entry
  `fetched: null` → the builder removes that entry from `sources.yaml`. Both anticipated
  failures are resolved (rows 3 and 5's epic-authorized swaps, recorded in the decisions.md
  build addendum); any NEW failure among the final five identities → stop and propose an
  official alternative to Ringo. Never hand-author, never fake a `fetched` date.
- **Thin mirror from a JS-heavy page**: treat as the `FAIL` case above — remove the entry
  and stop (this is how `fonts.google.com/knowledge` resolved: JS-only SPA shell → the
  epic-authorized `https://web.dev/learn/design/typography` swap).
- **Canonicalization collision**: kb dedupes entries whose URLs canonicalize identically —
  if an NN/g pick collapses into the other, pick a different canonical article so the group
  keeps five entries (two of them NN/g).
- **Re-run idempotency**: re-running `add` for an already-registered URL must not leave a
  duplicate manifest entry — kb's dedupe-on-canonicalization collapses it; the validator
  asserts no duplicate URLs.
- **No accidental mass refetch**: each `add` syncs only its new entry; the 26 existing
  entries are fresh, so no refresh work set exists. `--force` is never passed.
- **Worktree-copy semantics**: `.worktreeinclude` copies only untracked-and-ignored files
  present in the *creating* checkout — this worktree's mirrors never reach `main`, hence the
  epic driver's post-merge hydration (a Non-Goal here). Validation therefore simulates the
  hook's `fnmatch` matching in-place instead of creating a scratch worktree.
- **Partial failure mid-sequence**: each `add` is independent; a failed source leaves only
  its own provisional entry `fetched: null` without disturbing entries already fetched, and
  the replacement contract (remove + locked-fallback `add`, or stop) applies to it alone.

## Red Flags

- Starting to write code without any written requirements
- Asking "should I just start building?" before clarifying what "done" means
- Implementing features not mentioned in any spec or task list
- Making architectural decisions without documenting them
- Skipping the spec because "it's obvious what to build"
- Hand-authoring or hand-editing anything under `ai-docs/` other than `sources.yaml`
- A non-null `fetched` date on a source that was never successfully mirrored
- `git add -f` on mirrors or `ai-docs/index.md`
- Broadening `.worktreeinclude` beyond the one `ai-docs/*` pattern, or touching its env-file lines
- Registering a source outside the locked identity list without a recorded swap
- Editing `worktree_create.py` — the mechanism already works; this task only feeds it a pattern

## Notes

- **Hydration hand-off (epic driver, after this PR merges):** run `/harness-layer:kb` in the
  main checkout so the merged `sources.yaml` fetches mirrors there; only then create
  dependent child worktrees (#45+). Recorded here so the build never mistakes it for its own
  scope.
- Manifest count after this child: 32 = 19 anthropic (18 + memory) + 2 openai +
  6 openai/codex + 5 design — under the ≈40 cap, no eviction candidates.
- No new libraries anywhere in this child.

## Codex Verification

<!-- CLAUDE-OWNED. The outcome summary Claude records after the Codex loop. -->

- **Outcome:** **approved at round 4** — 2026-07-24, revision cycle 2 (rounds 3–4,
  `gpt-5.6-terra`). Cycle 1 history: round 1 (head `6c44157`) AC1/AC6 validation
  diagnostic-not-asserting — fixed; round 2 (head `bfb5c10`) AC2 provenance unobservable +
  AC6 sequenced against `HEAD` pre-commit — fixed; cycle capped at needs-human. Cycle 2:
  pre-round-3 revision fixed the yaml validation scripts' missing PyYAML dep
  (`uv run --with pyyaml`); round 3 (head `9ea0377`) found the substitution flow
  unrealizable (dangling `fetched: null` provisional entry) and AC2 contradicting the
  general substitution rule — fixed by the WCAG-only replacement contract (head `1dccea3`);
  round 4 approved with 0 blocking findings and no advisories. Cycle 3 (round 5,
  `gpt-5.6-terra`): mid-build amendment gated after the build halted on source 5 —
  resolved identity set (web.dev typography swap + applied NN/g homepage swap) and
  exact-URL AC2 assertions (head `efac876`) — **approved at round 5**, 0 blocking
  findings, no advisories. Status stays Approved.
- **Rejected findings:** none — every blocking finding from all five rounds was applied.

## References

<a tree of the sibling plan files and their purpose, so the four files trace to each other:>

```text
specs/soriza-design-kb-seed/
├── spec.md                 # this file — what & why, tracking, review record
├── decisions.md            # transcribed epic decisions + assumptions + KB references
├── tasks.md                # how & who: builders, step-by-step tasks
├── acceptance-criteria.md  # done: testable criteria + validation commands
└── reviews/                # Codex verdicts
```

No `discovery/` (the epic folder `specs/soriza-cpo-department/discovery/` holds the chain)
and no `artifacts/` (simple plan — no implementation-plan page).

## Self Validation

- [x] Objective, Task Description, and Non-Goals are filled in (no placeholders left)
- [x] Requirements trace to tasks in tasks.md and to checks in acceptance-criteria.md
- [x] Acceptance criteria are specific and testable
- [x] All four files exist under specs/soriza-design-kb-seed/ and are saved in the repository
- [x] Codex has reviewed the spec and Status reflects the outcome
