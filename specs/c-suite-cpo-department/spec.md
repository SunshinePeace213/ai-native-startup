# Spec: c-suite CPO department — client discovery → PRD → design package pipeline

- **Owner:** @SunshinePeace213
- **Status:** Drafted for Review
  <!-- Lifecycle, set by /harness-layer:harness-plan: Drafted for Review → Approved (on a Codex
       `approved` verdict). If round 2 is still changes-requested, the over-cap gate records the exit
       status in ## Codex Verification — approved | accepted-with-unverified-fixes | needs-human. One value only. -->

## Task Description

Soriza is being run like a real company, and this plan builds its first operating department: the CPO (product) department of the new **c-suite** series. Clients arrive with vague requests ("I want a website"); the department's job is to turn that into buildable product definition through two AI-owned workflows, then hand a complete design package to the human designer:

- **Workflow 1 — discovery → PRD.** `/c-suite:cpo-intake` interviews the client until every requirement dimension is locked — live (grilling protocol via AskUserQuestion) or async (a client-ready question-list document to send out, with re-entrant runs when answers return). `/c-suite:cpo-prd` then has the PM persona draft the PRD and gates it with a Codex cross-model review (`prd-review`: two automatic rounds, then an over-cap user gate that may authorize at most one final delta round).
- **Workflow 2 — design package.** `/c-suite:cpo-brief` produces the six-file design handoff package (project brief, sitemap & user flows, section briefs, copy deck, brand inputs, lo-fi HTML wireframes), reviewed for coherence by the Design Lead persona.
- **Workflow 3 — human.** The human designer prototypes in Claude Design (a Claude App feature the human drives). The department's output must be complete enough that this needs no further client contact. Nothing past the design package is automated.

The department is staffed by named persona subagents (Ethan Park/PM, Priya Nair/UX Researcher, Jonas Weber/UX Designer, Yuki Tanaka/UI Designer, Daniel Osei/Design Lead) with the CPO (Sofia Reyes) as the orchestrating session itself. Knowledge lives in three skills — each bundling the templates for the files it teaches, per the meta-skills supporting-files standard — memory lives in `.claude/rules/c-suite/` (roster, operations, lessons-learned), and each client engagement lives in `products/<client-slug>/` with its own GitHub issue and branch.

## Objective

A fresh session can run a fictional client through `/c-suite:cpo-intake` → `/c-suite:cpo-prd` → `/c-suite:cpo-brief` and end with a locked `requirements.md`, a Codex-approved `prd.md`, and all six design-package files in the engagement folder — with the status ledger, engagement issue, and lessons file updated at every stage.

## Non-Goals

- No automation of Workflow 3: the prototype work in Claude Design is human-owned; the department never generates hi-fi prototypes or design variants.
- Nothing after the final prototype — no CTO handoff packet, no build phase (a future CTO-department plan).
- No CTO/CMO/CEO departments — this plan establishes the pattern they will copy, nothing more.
- No real client engagement content under `products/` — only the dry-run fixture ships there; engagement templates live inside their owning skills.
- No two-level command namespacing (`/c-suite:cpo:intake`) — unverified in official docs; one proven directory level only.
- No changes to the existing harness-layer pipeline, hooks, or Codex plugin configuration.

## Problem Statement

The repo has a mature pipeline for building its own tooling (harness-plan/build/ship) but no structure for serving clients. Without a product department, every engagement would improvise its discovery questions, PRD shape, and design handoff — exactly the class of inconsistency the harness layer eliminated for internal work. The user also needs the client-facing side to survive real-world friction: clients who aren't available live, answers that arrive weeks later, and documents that must be complete enough for a human designer to work from without another round trip.

## Solution Approach

Mirror the harness-layer architecture the repo already trusts, one layer per concern — **commands own sequence, skills own knowledge and the blank forms that express it (bundled `templates/`), rules own memory, agents own labor, Codex owns cross-model QA, `products/` owns client work**:

- Three stage commands at `.claude/commands/c-suite/cpo-*.md` (one proven directory level → `/c-suite:cpo-intake|prd|brief`), each a fresh-session SOP that reads the previous stage's committed files plus the engagement `status.md` ledger — the context-management answer: no state lives only in a chat.
- Because subagents cannot use AskUserQuestion (KB-verified), all client interviewing happens in the main session; personas do the isolated heavy work (drafting, gap analysis, wireframes) and return files.
- Persona subagents get their department knowledge deterministically: each declares the knowledge skill(s) it depends on in `skills:` frontmatter (KB: "Preload skills into subagents"), and every delegation brief additionally passes the explicit template paths — so a fresh-context subagent never depends on skills loaded only in the parent session.
- The PRD is gated exactly like harness specs: a Codex skill (`.agents/skills/prd-review/`) with the same verdict-file contract, round cap, digest relay, and over-cap user gate as `spec-review`.
- The main alternative — one centralized department command — lost on context exhaustion and the impossibility of pausing for an async client mid-session.

## Requirements & Decisions

- **AI/human boundary (most volatile):** AI owns Workflow 1 + Workflow 2; the human owns prototyping in Claude Design. Alternative still live: automating wireframe→prototype variants later, if Claude Design's workflow changes.
- **W2 package is six files** — `project-brief.md` (incl. design-constraints section), `sitemap-and-flows.md` (mermaid), `section-briefs.md`, `copy-deck.md`, `brand-inputs.md`, `wireframes/<page>.html` (lo-fi, unstyled, self-contained). Why: what a professional design team actually needs; copy deck and brand inventory prevent the most common re-contact with clients. Alternative: 3-file core, rejected as designer-hostile.
- **Command naming:** files live at `.claude/commands/c-suite/cpo-intake.md`, `cpo-prd.md`, `cpo-brief.md`. The canonical slash prefix is settled by a deterministic **naming probe** (tasks.md `naming-probe`) BEFORE the commands are authored: this repo's live behavior resolves one-level command dirs as `/c-suite:<file>`, while the cached SDK contract (`ai-docs/anthropic/agent-sdk/slash-commands.md`) predicts a bare `/<file>`. Both candidates (`/c-suite:cpo-intake` or `/cpo-intake`) are unique and workable; the probe's winner is recorded in `cpo-operations.md` and used in every user-facing mention, and AC2 asserts it. Two-level nesting (`/c-suite:cpo:intake`) stays a non-goal.
- **Engagement git flow:** one issue + branch `feat/<N>-<client-slug>` per engagement, stage commits with `Refs #N`, Codex digests as issue comments, ONE PR opened after the Design Lead approves the W2 package; the PR closes the issue. Fixture exception: `_example-` slugs run in fixture mode — no engagement issue/branch/PR; stages run on the current branch and the ledger records `mode: fixture`, the hosting branch, and stage commit SHAs. Why: durable tracking without a weeks-open draft PR, and fixture outputs that land on the implementation branch instead of a stranded engagement branch.
- **Persona economics:** five AI persona subagents + the CPO as the session's own hat; persona names sign reports, documents stay professional (no role-play dialogue in deliverables).
- **Knowledge skills never auto-fire** (`autoInvoke: false`); only the commands load them. Why: client-domain knowledge must not leak into unrelated sessions' context.

## Tracking

<!-- Recorded by /harness-layer:harness-plan. The Issue field is the SINGLE SOURCE OF TRUTH
     /harness-layer:harness-build reads — it NEVER re-derives #N from the local `worktree-<slug>`
     branch name. spec.md is the single home for this block; decisions.md does not duplicate it. -->

- **Issue:** #35
- **Branch:** feat/35-c-suite-cpo-department
- **Worktree:** /home/ringo/ai-native-startup/.claude/worktrees/c-suite-cpo-department
- **Review profile:** kb-grounded
- **PR:** <#M — filled by /harness-layer:harness-build>

## Relevant Files

Use these files to complete the task:

- `.claude/commands/harness-layer/harness-plan.md` / `harness-build.md` — the SOP style, gate mechanics, and report shape the stage commands mirror (grilling, review rounds, over-cap gate, idempotent issue comments).
- `.agents/skills/spec-review/SKILL.md` — the Codex review skill whose mechanics (inputs, verdict contract, terse return, never-touch rules) `prd-review` mirrors with PRD criteria.
- `.claude/skills/meta-skills/references/command-format.md` — the house five-section command template every new command follows.
- `.claude/skills/meta-agent/` — the subagent authoring standard + `scripts/validate_agent.py` used to validate the five personas.
- `.claude/skills/grilling/SKILL.md` — the interview pattern `cpo-intake`'s live mode adapts for clients.
- `.claude/rules/memory-series.md` — governs how the new `.claude/rules/c-suite/` family is created and pointed to from AGENTS.md.
- `.claude/rules/git-workflow.md` — commit/PR conventions engagement commits follow.
- `AGENTS.md` — hub file; gains the c-suite/products pointers.

### New Files

- `.claude/commands/c-suite/cpo-intake.md` — Workflow 1a SOP: engagement scaffold, mode check, live grilling / async question list, re-entrant answer ingestion, requirements lock.
- `.claude/commands/c-suite/cpo-prd.md` — Workflow 1b SOP: PM draft, CPO pass, Codex `prd-review` rounds, over-cap gate, issue digests.
- `.claude/commands/c-suite/cpo-brief.md` — Workflow 2 SOP: parallel persona drafting of the six-file package, Design Lead review gate, engagement PR.
- `.claude/skills/cpo-question-bank/SKILL.md` — discovery dimensions for websites/software, per-dimension question templates and "locked when" criteria; `templates/` bundles `question-list.md`, `requirements.md`, `status.md` (intake scaffolds the engagement).
- `.claude/skills/cpo-prd-standard/SKILL.md` — the Soriza PRD structure and quality bar; `templates/` bundles `prd.md`.
- `.claude/skills/cpo-design-standard/SKILL.md` — section catalog (hero, nav, social proof, features, case study, CTA, footer…), wireframe conventions, copy-deck and brand-inputs formats, Design-Lead review checklist; `templates/` bundles `project-brief.md`, `sitemap-and-flows.md`, `section-briefs.md`, `copy-deck.md`, `brand-inputs.md`.
- `.agents/skills/prd-review/SKILL.md` — Codex cross-model PRD review skill.
- `.claude/rules/c-suite/roster.md` — org chart: seat, persona name, human/AI, model, what they own.
- `.claude/rules/c-suite/cpo-operations.md` — engagement folder schema, status-ledger states, stage gates, git flow.
- `.claude/rules/c-suite/cpo-lessons.md` — seeded lessons-learned file with append format.
- `.claude/agents/cpo/cpo-pm.md`, `cpo-ux-researcher.md`, `cpo-ux-designer.md`, `cpo-ui-designer.md`, `cpo-design-lead.md` — the five persona subagents (one agents folder per department; identity stays in the `name` field).

## Edge Cases

- **Async client never answers** — the engagement stays `blocked-on-client` in `status.md`; re-running `cpo-intake` reports the outstanding question list instead of re-scaffolding. No timeout logic.
- **Late answers contradict locked requirements** — `cpo-intake` re-opens the affected dimension, re-locks it, and marks downstream stages (`prd`, `brief`) stale in `status.md`; those commands refuse to run on a stale predecessor without explicit user confirmation.
- **Stage run out of order** — every command preflights the ledger: `cpo-prd` STOPs unless intake is `done`; `cpo-brief` STOPs unless the PRD is approved.
- **Re-running a completed stage** — the command detects the done state and asks (AskUserQuestion) before overwriting prior outputs.
- **Duplicate engagement slug** — `cpo-intake` detects the existing `products/<slug>/` and resumes it rather than scaffolding a second copy.
- **Malformed client slug** — `cpo-intake` validates `<client-slug>` against the canonical rule `^[a-z0-9][a-z0-9-]{0,38}[a-z0-9]$` (fixtures: `_example-` + a valid slug) BEFORE any filesystem, branch, worktree, or `gh` use; an invalid slug STOPs with guidance, and slugs are always quoted in shell commands.
- **Fixture engagement (`_example-` slug)** — runs entirely on the current branch: no engagement issue, branch, worktree, or PR is created; the ledger records `mode: fixture`, the hosting branch, and per-stage commit SHAs instead of the real GitHub trail.
- **`gh`/`codex` unavailable** — preflight STOP with fix guidance, mirroring the harness commands; never proceed degraded.
- **Codex round writes no verdict line** — re-run the round; never treat silence as approval (same rule as harness-plan).
- **Wireframes must open offline** — self-contained HTML, no external assets; a page with remote references fails the Design-Lead checklist.

## Red Flags

- Starting to write code without any written requirements
- Asking "should I just start building?" before clarifying what "done" means
- Implementing features not mentioned in any spec or task list
- Making architectural decisions without documenting them
- Skipping the spec because "it's obvious what to build"
- A persona subagent trying to interview the user directly (AskUserQuestion is unavailable to subagents — interviewing is the session's job)
- Deliverables written in role-play voice instead of client-grade professional prose
- Knowledge skills auto-firing in sessions unrelated to client work

## Notes

- No new runtime dependencies: `gh` and `codex` are already required by the harness pipeline; wireframes and templates are plain files.
- The dry-run engagement ships as a fixture at `products/_example-bluebird-bakery/` (underscore prefix = not a real client) so acceptance stays re-checkable and doubles as documentation.
- Follow-ups intentionally deferred: CTO department (consumes the design package + final prototype), question-bank tuning after the first real engagement, and an optional chore to test two-level command namespacing.

## Codex Verification

<!-- CLAUDE-OWNED. The outcome summary Claude records after the Codex loop. -->

- **Outcome:** <approved at round N | accepted-with-unverified-fixes | needs-human>
- **Rejected findings:** <any Codex finding Claude chose not to act on, each with a one-line rationale; "none" if all warranted findings were applied>

## References

<a tree of the sibling plan files and their purpose, so the four files trace to each other:>

```text
specs/c-suite-cpo-department/
├── spec.md                 # this file — what & why, tracking, review record
├── decisions.md            # grilling record: resolved decisions, assumptions, out-of-scope
├── tasks.md                # how & who: phases, team, step-by-step tasks
├── acceptance-criteria.md  # done: acceptance criteria + validation commands
└── artifacts/              # blindspot board (final state)
```

## Self Validation

- [x] Objective, Task Description, and Non-Goals are filled in (no placeholders left)
- [x] Requirements trace to tasks in tasks.md and to checks in acceptance-criteria.md
- [x] Acceptance criteria are specific and testable
- [x] All four files exist under specs/c-suite-cpo-department/ and are saved in the repository
- [ ] Codex has reviewed the spec and Status reflects the outcome
