# Spec: Soriza design department — slice 1 (soriza-design)

- **Owner:** @SunshinePeace213
- **Status:** Drafted for Review
  <!-- Lifecycle, set by /harness-layer:harness-plan: Drafted for Review → Approved (on a Codex
       `approved` verdict). A cycle that ends still changes-requested — or with Codex unavailable —
       records needs-human in ## Codex Verification and keeps this status. One value only. -->

## Task Description

Build the first slice of Soriza's design department — **soriza-design**, headed by the CPO
persona **Vera** — on this repo's harness layer: a client web-design studio whose operations
agents run. The client owns "what"; the department owns discover → define → design and hands
Ringo a brief packet for Claude Design prototyping.

The slice is a per-rung command chain — `/soriza-design:intake → :brief → :sitemap →
:wireframe → :section-briefs` — operating on `projects/<client>/` (scaffolded from
`projects/_template/`). Each rung embodies a named staffer from the company-wide roster, reads
the previous rung's file, is gated by its Definition of Ready, and commits per rung. Intake is
additionally gated by a uv-script Stop hook (code, not model memory). Doctrine lives in a
path-scoped rules family with real starter content day one; copywriting is first-class (section
briefs deliver draft copy; the packet carries a typography-direction page). Wireframes are lo-fi
grayscale HTML pages published as artifacts — private to Ringo by default, with the client-facing
delivery mode locked per engagement (org share, consented public link, or the self-contained HTML
file itself) and recorded in the decision log. The KB gains a `design/` group of five
official sources, plus worktree availability for all mirrors. Client deliverables ride a
design-shaped git lane (PR per gate point, evidence block swapped).

This is an **epic** (#43) with five child issues (#44–#48), one pipeline run per child — this
spec is the epic master plan each child's plan run transcribes from. Pilot engagement: Soriza's
own site, with Ringo as the client.

## Objective

When this epic is done, `/soriza-design:intake <client>` through `/soriza-design:section-briefs
<client>` can run end to end against a real `projects/<client>/` folder — every rung gated by
real doctrine, intake blocked by the DoR hook until complete, wireframes reviewable as artifacts with a locked
client-delivery mode, and the final packet (brief, IA, wireframes, per-section briefs with draft copy,
typography direction, asset checklist, decision log) signed by Vera and handed to Ringo — with
all five children shipped through their own plan → build → review → ship runs (#44–#48 closed
by their PRs).

## Non-Goals

- Delivery/production — a future CTO department.
- Agent team per engagement — revisit after the ladder proves out.
- Styled design directions for wireframes — lo-fi grayscale only in slice 1.
- Client-facing intake surface — Ringo relays; no client-visible pages beyond shared wireframe links.
- Subagent specialists (brief-writer, wireframer as agents) — the roster's named personas keep the door open.
- Running the pilot engagement itself — this epic makes the ladder pilot-ready; the pilot is a
  normal engagement (own issue/branch) that starts after #44–#48 ship.

## Problem Statement

Soriza wants agents to run a web-design studio's operations, but the harness has no
department: no client folder convention, no design doctrine to hold outputs to, no intake gate,
no staff identity, and no design knowledge in the KB. Ringo's field experience says clients
reject pages over weak copy and fonts — so the department must know how to *write*, not only
how to structure. Building it as slice 1 on the proven pipeline (command chains, path-scoped
rules, code gates, KB grounding) gives real stakes via the Soriza-site pilot without betting on
unproven org shapes.

## Solution Approach

A five-rung command chain mirroring the proven discovery-chain shape — one session's judgment
end to end, cheapest context — over a `projects/<client>/` home scaffolded from
`projects/_template/`. Doctrine is a path-scoped rules family (`paths: ["projects/**/*"]`) with
real starter content drafted from a freshly seeded `design/` KB group; the intake gate is a
command-scoped Stop hook (frontmatter registration, `check_spec_completeness.py` precedent);
client work rides its own git lane (engagement branch, PR per gate point). The main alternative
— an orchestrator with subagent specialists — was closed in discovery: viable (subagents nest
since v2.1.172) but declined on judgment; the named-persona roster keeps that upgrade path open.

Execution shape: one epic (#43), five children (#44–#48), **one pipeline run per child** —
because `harness-build` binds one spec folder to one issue/branch/PR, per-child PRs require
per-child spec folders; each child plan transcribes from this master spec and asks nothing.

## Requirements & Decisions

Volatile first — full record in [decisions.md](./decisions.md):

1. **Doctrine content & template skeletons** (most likely to churn): six doctrine files with
   real starter content day one — stubs gate nothing; content drafts from the design KB at #45's
   build and Ringo reviews it in the PR. Live alternative: Ringo supplies a preferred brief
   format first, which reshapes `brief-format.md` and the template skeletons.
2. **Section inventory is dynamic per client**: the sitemap/IA rung locks pages and sections
   with the client from a nine-skeleton starter library (each skeleton carries "One job" and
   "One desired action"). Live alternative rejected: a hardcoded five-section brief.
3. **Intake gate is code, and deterministic**: `check_intake_readiness.py`, a uv-script Stop
   hook in `/soriza-design:intake`'s frontmatter; hard-coded section tuple + doctrine sync
   test; the gate targets per-client `projects/<client>/.intake-in-progress` markers (the
   command's first write) and blocks until **every** marked client's `intake.md` is complete —
   race-free under concurrent runs, never a newest-modified heuristic. Live alternative
   rejected: model-side checklist only.
4. **Epic mechanics**: children #44–#48 already filed; one pipeline run per child in dependency
   order #44 → #45 → {#46 → #47, #48}; epic planning docs land on `main` via a draft
   `📝 docs(spec)` PR (`Refs #43`) so child worktrees (branched fresh from `origin/main`) can
   read this spec.

## Tracking

<!-- Recorded by /harness-layer:harness-plan. The Issue field is the SINGLE SOURCE OF TRUTH
     /harness-layer:harness-build reads — it NEVER re-derives #N from the local `worktree-<slug>`
     branch name. spec.md is the single home for this block; decisions.md does not duplicate it. -->

- **Issue:** #43 (epic) — children #44, #45, #46, #47, #48
- **Branch:** feat/43-soriza-cpo-department
- **Worktree:** /Users/ringo/Desktop/ai-native-startup/.claude/worktrees/soriza-cpo-department
- **Review profile:** kb-grounded
- **PR:** #49 (draft `📝 docs(spec)` epic docs PR, `Refs #43` — merge lands the plan on `main`
  after the verifying round approves); child PRs are opened by each child's own build run and
  recorded in the child specs

## Relevant Files

Use these files to complete the task:

- `.worktreeinclude` — gains the `ai-docs/*` pattern (#44); processed by the repo's own
  WorktreeCreate hook, whose `fnmatch` matching lets `*` cross `/`.
- `.claude/hooks/worktree/worktree_create.py` — the copy mechanism #44 relies on; read-only.
- `ai-docs/sources.yaml` — gains the `design/` group entries + the anthropic memory page (#44);
  mirrors themselves stay gitignored (`.gitignore:362`), which is exactly why the
  `.worktreeinclude` pattern is needed.
- `.claude/hooks/check_spec_completeness.py` — the pattern #46's hook copies (newest-folder
  resolution, hard-coded section tuple, exit-2 diagnostics, fail-open plumbing).
- `tests/harness-layer/hooks/test_wiring.py` — pins every hook registration; already scans
  `.claude/commands/` for command-scoped registrars; #46 extends its expectations.
- `.claude/rules/harness-layer/hooks.md` — authoritative hook catalog; #46 adds its row.
- `.claude/rules/git-workflow.md` — the lane #48's rule specializes for `projects/**`.
- `.claude/rules/memory-series.md` — the contract the rules family and roster follow.
- `.claude/rules/development-log.md` — the contract `soriza-design/lessons.md` copies.
- `.claude/commands/harness-layer/*.md` — frontmatter and rung-shape precedents for the five
  `/soriza-design:*` commands.
- `AGENTS.md` — gains the roster/family pointers and a `projects/` structure row (#45).

### New Files

- `projects/_template/` — `intake.md`, `brief.md`, `sitemap-ia.md`, `asset-checklist.md`,
  `decision-log.md`, `wireframes/README.md`, `section-briefs/README.md`,
  `section-briefs/_library/<9 skeletons>.md` — the client home scaffold (#45).
- `.claude/rules/soriza/roster.md` — company-wide staff roster, `paths: ["projects/**/*"]` (#45).
- `.claude/rules/soriza-design/{client-communication,intake-standards,definition-of-ready,brief-format,section-anatomy,copywriting,lessons}.md`
  — six doctrine files + lessons log, all `paths: ["projects/**/*"]` (#45).
- `.claude/rules/soriza-design/git-lane.md` — the client git lane, `paths: ["projects/**/*"]` (#48).
- `.claude/commands/soriza-design/{intake,brief,sitemap,wireframe,section-briefs}.md` — the five
  rungs (#46, #47).
- `.claude/hooks/check_intake_readiness.py` — the DoR Stop gate (#46); gates the per-client
  `projects/<client>/.intake-in-progress` markers (transient; the pattern gets a `.gitignore`
  line in #46).
- `tests/harness-layer/hooks/intake-readiness/` — contract + doctrine-sync + cross-client
  regression + concurrent two-marker tests (#46).
- `specs/soriza-design-{kb-seed,foundations,intake-gate,ladder,git-lane}/` — the five child spec
  folders, created by each child's own plan run (not by this one).

## Edge Cases

- **KB source refuses fetching** (NN/g robots, WCAG quickref JS app): `/kb` reports FAIL and
  leaves `fetched: null`; #44 substitutes the canonical page for the same topic and records the
  swap — never a hand-authored mirror, never a fake `fetched` date.
- **Worktree copy misses mirrors**: `.worktreeinclude` copies only untracked-and-ignored files —
  correct here since mirrors are gitignored; `sources.yaml` is tracked and arrives via checkout.
  A worktree created before #44 ships simply lacks mirrors → run `/harness-layer:kb` inside it.
- **Re-running `:intake` on an existing client**: scaffold step must be idempotent — never
  clobber an existing `projects/<client>/`; re-interview updates `intake.md` in place.
- **DoR hook resolution**: deterministic and race-free — the intake command's first write drops
  `projects/<client>/.intake-in-progress` (gitignored, transient; no shared file to overwrite);
  the hook blocks until **every** marked client's `intake.md` is complete, so completing client
  A can never release an incomplete marked client B, even under concurrent intake runs (primary
  isolation is one engagement worktree per client; markers are defense-in-depth). No marker
  anywhere → block with a clear message; `_`-prefixed folders never valid; the command sweeps
  markers from already-complete clients; malformed/empty stdin or unreadable files → fail open
  (exit 0), per the hooks contract. Command-scoped registration means other sessions editing
  `projects/` are never gated. Tests: cross-client regression + two-marker concurrent case.
- **Doctrine/hook drift**: the sync test fails if `definition-of-ready.md`'s checklist headings
  and the hook's tuple diverge — the pair ships together or not at all.
- **Large section inventory**: `:section-briefs` loops inline by default; above ~10 sections it
  may fan out parallel subagents per section, with Lior consolidating voice and Vera signing the
  merged packet.
- **Artifact publish fails or is denied**: wireframe HTML files remain the canonical
  deliverable; the rung notes "publish skipped" in `decision-log.md` and never blocks.
- **Client can't open an artifact link**: a fresh artifact is visible only to its author — the
  rung never promises a private URL to an external client; it locks the delivery mode per
  engagement (org share / consented public link / the HTML file itself) and records it in
  `decision-log.md`.
- **Client name collisions / naming**: client folder names are kebab-case; `_`-prefixed folders
  are reserved (template, libraries) and never treated as clients.
- **Concurrent child pipelines**: #46/#47 vs #48 may run in parallel — they touch disjoint
  files; both depend on #45 landing on `main` first (children branch from `origin/main`).
- **`gh` unavailable mid-pipeline**: per git-workflow, stop and surface — never proceed with a
  placeholder issue or unchecked push.

## Red Flags

- Starting to write code without any written requirements
- Asking "should I just start building?" before clarifying what "done" means
- Implementing features not mentioned in any spec or task list
- Making architectural decisions without documenting them
- Skipping the spec because "it's obvious what to build"
- Hand-editing anything under `ai-docs/` other than `sources.yaml` — mirrors are fetched, never written
- Doctrine stubs ("TBD", "fill me in") — an empty DoR gates nothing; that's a build failure, not a placeholder
- A single giant build PR spanning multiple children — the ledger locks one pipeline run per child
- Writing department memory anywhere but `.claude/rules/soriza/` / `.claude/rules/soriza-design/` (no new root markdown, nothing in CLAUDE.md)
- The intake command "checking the DoR itself" instead of relying on the Stop hook — the gate is code

## Notes

- **Child hand-off**: each child's plan run gets a ready-made prompt (see
  [tasks.md](./tasks.md)) that names its issue, branch, and worktree, and instructs it to
  transcribe from this folder and ask nothing. Child plans skip issue creation (#44–#48 exist)
  and link their branch via `gh issue develop <N>`.
- **Order matters**: the epic docs PR must merge before #44 starts (children need this spec on
  `main`); #45 needs #44's KB on disk to draft doctrine; #46 needs #45's doctrine and template;
  #47 needs #46's rung to chain from; #48 only needs #45.
- **No new libraries** anywhere in the slice; the hook is a zero-dependency PEP 723 uv script
  like its precedent.
- The KB manifest stays under its ≈40-entry cap after #44 (26 + 6 = 32).

## Codex Verification

<!-- CLAUDE-OWNED. The outcome summary Claude records after the Codex loop. -->

- **Outcome:** needs-human (blockers) — cycle cap (2 rounds) reached at changes-requested.
  Round 1: 3 blockers (artifact sharing model, gate targeting, weak validation) — fixed and
  re-reviewed. Round 2: 3 blockers (target-file race → per-client markers, section-briefs
  predecessor → wireframes/, AC7/AC9–AC11 keyword-loose → Rung Contract field assertions) —
  **fixes applied on this branch after the cap**; they await a verifying round via a plan
  re-run (Revision Mode, round 3).
- **Rejected findings:** none — every blocking finding from both rounds was applied; round-1
  advisory (add html-artifacts-workflows.md to KB References) also applied.

## References

<a tree of the sibling plan files and their purpose, so the four files trace to each other:>

```text
specs/soriza-cpo-department/
├── discovery/              # unknowns ×2, brainstorm, interview pages + decisions-draft.md (the locked ledger)
├── spec.md                 # this file — what & why, tracking, review record
├── decisions.md            # interview record: resolved decisions, assumptions, out-of-scope, KB references
├── tasks.md                # how & who: per-child scope, teams, model/effort stamps, pipeline prompts
├── acceptance-criteria.md  # done: testable criteria + validation commands
└── artifacts/              # implementation-plan page (authored after the Codex gate)
```

## Self Validation

- [x] Objective, Task Description, and Non-Goals are filled in (no placeholders left)
- [x] Requirements trace to tasks in tasks.md and to checks in acceptance-criteria.md
- [x] Acceptance criteria are specific and testable
- [x] All four files exist under specs/soriza-cpo-department/ and are saved in the repository
- [ ] Codex has reviewed the spec and Status reflects the outcome
