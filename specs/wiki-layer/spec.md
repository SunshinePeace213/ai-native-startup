# Spec: Wiki Layer

- **Owner:** @SunshinePeace213
- **Status:** Drafted for Review

## Tracking

- **Type:** feat
- **Complexity:** complex
- **Issue:** #88
- **Branch:** feat/88-wiki-layer
- **Worktree:** /home/ringo/ai-native-startup/.claude/worktrees/wiki-layer
- **Review profile:** kb-grounded
- **PR:** pending — filled by /harness-layer:harness-build

## Task Description

Build the wiki layer: an LLM-maintained synthesis wiki above the immutable `ai-docs/`
mirrors, following the Karpathy LLM-wiki pattern cached in
`ai-docs/knowledge-base/`. The layer ships as its own surface, separate from
harness-layer: a `/wiki:*` command family (ingest · query · lint · status), a
path-scoped standards rule that is the layer's schema, tracked storage at
`ai-docs/wiki/` with a local-only `personal/` domain, minimal committed Obsidian
vault config, AGENTS.md integration (wiki-first task starts, gated crystallization),
and a drift test. The full decision record is in [decisions.md](./decisions.md);
the interview ledger is `discovery/decisions-draft.md`.

## Objective

When this plan is complete, `ai-docs/wiki/` is a tracked, schema-governed synthesis
layer with four working `/wiki:*` operations; AGENTS.md routes every task through the
wiki index first and routes gate-passing synthesis back into the wiki; and the drift
test plus five plan-local checks pass from the repo root.

## Non-Goals

- No `absorb` / `breakdown` commands (expansion triggers recorded in decisions.md).
- No hybrid-search CLI, embeddings, vector store, or enterprise RAG machinery.
- No session-start wiki-context hook.
- No team sharing, mesh sync, or multi-agent wiki-write coordination.
- No changes to mirrors, `ai-docs/sources.yaml` semantics, `/harness-layer:kb`, or
  any harness-layer command.
- No pre-created domain folders beyond the seed (folders appear on first need).

## Problem Statement

The KB is a well-run mirror cache with no synthesis layer: every plan re-reads the
same mirrors and rebuilds the same understanding, and the durability rule scopes
research to the plan that produced it — knowledge evaporates instead of compounding.
The KB docs name this exact failure and supply the pattern to fix it; at ~50 docs the
missing piece is compounding, not search infrastructure.

## Solution Approach

Implement the Karpathy three-layer pattern natively in this repo: mirrors stay the
immutable source layer; `ai-docs/wiki/` becomes the LLM-owned synthesis layer
(tracked via gitignore negation, with `personal/` re-ignored so private content
cannot reach the remote); the schema lives as a path-scoped rule that loads whenever
a session touches wiki files. Operations are deliberate slash commands (repo
convention, like `/kb`), with lint designed to run both on demand and as a weekly
cloud routine against a fresh clone — which structurally cannot see the personal
domain. The main alternative — extending `/harness-layer:kb` — lost because the user
explicitly wants the layers separately maintainable.

## Requirements & Decisions

1. **Page schema & status vocabulary** *(most volatile)* — seven core frontmatter
   fields with `status: current | superseded | disputed`; status travels into every
   answer (disputed/superseded flagged inline, never dropped). Alternative left
   open: a leaner three-field schema if lint shows the rest unused.
2. **Privacy by git semantics** — wiki tracked through gitignore negation;
   `ai-docs/wiki/personal/` re-ignored so it never has tracked files. Alternative:
   a separate personal vault (rejected for v1: two vaults to run).
3. **Surface = commands + path-scoped rule** — `.claude/commands/wiki/*.md` and
   `.claude/rules/wiki-layer/wiki-standards.md`; not `.claude/skills/` (official
   docs prefer skills for new work; repo convention wins, recorded in decisions).
   Alternative: skill-first, revisited only if predictable invocation stops
   mattering.
4. **Memory budget** — AGENTS.md gains ≤14 lines total (wiki-first order,
   crystallization, registration); everything else lives in the path-scoped rule.

## Interfaces & Contracts

### `.gitignore` — append after the existing `ai-docs` block

```gitignore
# ai-docs/wiki/ — the LLM-maintained synthesis layer IS tracked (compiled
# knowledge, not regenerable cache); the personal domain never leaves this machine.
!ai-docs/wiki/
ai-docs/wiki/personal/
# Obsidian vault config: track the minimal shared config, ignore volatile state.
!ai-docs/.obsidian/
ai-docs/.obsidian/workspace*
```

### Wiki page frontmatter (documented in wiki-standards.md, produced by ingest)

```yaml
---
type: topic | entity | comparison | decision | pattern | <domain-specific>
domain: engineering | business | development | books | articles | personal
status: current | superseded | disputed
created: YYYY-MM-DD
updated: YYYY-MM-DD
sources: ["ai-docs/<mirror-path>.md", "<local file or plan artifact>"]
related: ["[[Other Page]]"]
---
```

### Command frontmatter (exact keys; bodies per tasks.md)

```yaml
# .claude/commands/wiki/ingest.md
---
description: Ingest a source into the ai-docs wiki — reads a mirror, local file, or plan artifact, integrates it across wiki pages, and updates the index and log. Use when the user asks to ingest, absorb, file, or crystallize something into the wiki.
argument-hint: <mirror-path | file-or-folder | plan-artifact> [--domain <name>]
model: opus
effort: high
---
```

```yaml
# .claude/commands/wiki/query.md
---
description: Answer a question from the ai-docs wiki — read-only; index → pages → linked pages, synthesized with citations and status flags. Use when the user asks what the wiki knows about a topic.
argument-hint: <question>
model: sonnet
effort: high
---
```

```yaml
# .claude/commands/wiki/lint.md
---
description: Health-check the ai-docs wiki — orphans, broken links, schema violations, staleness, contradictions; fixes what it can, reports the rest, logs the pass. Run weekly by routine and on demand.
model: opus
effort: high
---
```

```yaml
# .claude/commands/wiki/status.md
---
description: Report ai-docs wiki health at a glance — page counts by domain and type, orphans, disputed pages, last lint, and the expansion-trigger readout.
model: haiku
effort: medium
---
```

### Standards rule frontmatter

```yaml
# .claude/rules/wiki-layer/wiki-standards.md
---
paths:
  - "ai-docs/wiki/**"
---
```

### AGENTS.md — exact amendments (≤14 added lines total)

Rewrite the first two `## Knowledge Base` bullets:

```markdown
- `ai-docs/` is the shared KB — the wiki (`ai-docs/wiki/`, compiled synthesis; catalog: `ai-docs/wiki/index.md`) over cached official docs (mirror catalog: `ai-docs/index.md`, manifest: `ai-docs/sources.yaml`).
- Start every task wiki-first: check `ai-docs/wiki/index.md` for pages matching the work, then `ai-docs/index.md` for mirrors; skim a match's summary line before a full read. Nothing relevant → move on.
```

Amend the durability-rule bullet's synthesis clause:

```markdown
- Durability rule: official pages get mirrored via `kb-fetcher` and registered in `sources.yaml`; synthesis that passes the crystallization gate — cited, non-duplicative — files into the wiki via `/wiki:ingest`; synthesis that doesn't stays in that plan's `discovery/research.md`; raw search results go nowhere.
```

Insert a new section after `## Knowledge Base`:

```markdown
## Wiki Layer

- `ai-docs/wiki/` — LLM-maintained synthesis over the mirrors; domain folders over one shared schema; `personal/` is gitignored and local-only.
- Operations: `/wiki:ingest`, `/wiki:query`, `/wiki:lint` (weekly routine + on-demand), `/wiki:status`.
- Standards, schema, lane fit, metrics, archetypes: [wiki-standards.md](.claude/rules/wiki-layer/wiki-standards.md). Mirrors stay immutable; ingest reads, never edits them.
```

### Obsidian vault config

```json
// ai-docs/.obsidian/app.json
{
  "attachmentFolderPath": "wiki/assets",
  "alwaysUpdateLinks": true
}
```

### Wiki seed shapes

`ai-docs/wiki/index.md`: H1, one-line purpose, one `## <Domain>` section per shared
domain (engineering, business, development, books, articles) each holding an empty
`Page | Type | Status | Updated` table, a `## Personal` section holding only the
pointer line "local-only — cataloged in `wiki/personal/index.md`, never tracked",
and a footer noting ingest maintains the file. `ai-docs/wiki/log.md`: H1 plus the
two entry contracts — ingest: `## [YYYY-MM-DD] ingest | <title> | <source-path>`;
lint: `## [YYYY-MM-DD] lint | <scope> | <summary>` followed by the payload line
`missing-pages: <comma-list or none> · mechanical-fixes: <N>` (the fields status
derives its breakdown and cleanup triggers from). Only `ingest` and `lint` write —
query and status never do; crystallizing an answer is an ingest.
The personal domain keeps its own local-only `personal/index.md` and
`personal/log.md`, created lazily with the domain; personal ingests update only
those two files, never the shared index or log.

## Relevant Files

- `.gitignore` — wiki tracking negations (contract above).
- `AGENTS.md` — wiki-first protocol, crystallization, layer registration.
- `ai-docs/sources.yaml` — untouched; named here because the KB group requirement
  for a new layer is already satisfied (`knowledge-base`, `cerebras` groups).
- `tests/harness-layer/` — houses the new drift test beside the existing ones.

### New Files

- `ai-docs/wiki/index.md`, `ai-docs/wiki/log.md` — the wiki seed.
- `ai-docs/.obsidian/app.json`, `ai-docs/.obsidian/appearance.json` — vault config.
- `.claude/commands/wiki/{ingest,query,lint,status}.md` — the operation surface.
- `.claude/rules/wiki-layer/wiki-standards.md` — the layer's schema and standards.
- `tests/harness-layer/test_wiki_layer.py` — drift guard over the new surface:
  expected command set re-derived from the AGENTS.md Wiki Layer registration,
  exact frontmatter contracts, roster parsed from model-selection.md, standards
  rule structure (the single durable home for these assertions).
- `specs/wiki-layer/checks/fixtures/` — two related pilot articles + rubric for
  the pre-ship fixture eval (AC7).

## Edge Cases

- **Missing mirror on a fresh clone** (mirrors are device-local): lint reports a
  cited-but-absent mirror as "run `/harness-layer:kb`", never as a broken citation.
- **External URL passed to ingest**: refused with a pointer to
  `/harness-layer:kb add <url>` — sources become immutable mirrors first.
- **Duplicate ingest of the same source**: idempotent — identity is the canonical
  source path, checked against page `sources:` frontmatter and the log's
  `<source-path>` field; pages are updated in place, never duplicated; a second
  identical run changes nothing.
- **Personal attachments**: Obsidian's global attachment folder is the tracked
  `wiki/assets/` — the standards rule requires personal-page attachments to be
  moved under `wiki/personal/assets/`, and local lint flags any personal page
  referencing files outside `personal/`.
- **Contradiction found during ingest**: both claims flagged `disputed` on their
  pages with cross-references; resolution flips the loser to `superseded` — history
  kept, nothing deleted.
- **Query outside wiki coverage**: say the wiki doesn't cover it; never guess,
  never silently fall back to mirrors.
- **Cloud lint routine vs personal domain**: the fresh clone has no `personal/`
  (gitignored) — routine output must not claim to have linted it; personal lint is
  local-only.
- **Empty wiki (pre-pilot)**: query and status degrade gracefully on the seed
  index; lint on an empty wiki reports clean, not errors.
- **Concurrent edits**: re-read any page immediately before editing (standards
  rule); single-writer assumption recorded in decisions.md.

## Risk & Rollback

- **Blast radius:** AGENTS.md loads every session — a bloated or contradictory
  amendment degrades all work; the gitignore negation, if wrong, could either track
  personal content (privacy leak to remote) or leave the wiki untracked (silent
  data loss on clone). The AC1 script guards both directions; AC5 caps the memory
  addition.
- **Rollback:** revert the commit(s). Wiki pages created after ship survive as
  ordinary files; untracked `personal/` content is never touched by git either
  way. No migrations, no state outside the repo except the user-created routine
  (deleted at claude.ai/code/routines).
- **In-flight work:** existing sessions and worktrees are unaffected — the layer is
  additive; mirrors and `/kb` behavior are unchanged.

## Guardrails

- This is an **additive layer** — do not touch mirrors, `ai-docs/index.md`
  generation, `sources.yaml` semantics, or any `harness-layer` command file.
- Do not move the commands to `.claude/skills/` "because the docs say new skills go
  there" — repo convention is `.claude/commands/<family>/`, locked in decisions.md.
- Do not pre-create empty domain folders or write placeholder wiki pages beyond the
  two seed files — folders appear on first ingest.
- Do not exceed the 14-line AGENTS.md budget or duplicate schema content there —
  the rule file owns the schema.
- Command bodies are instructions, not rationale — no design history, no
  cross-references beyond what the operation needs to run.

## Notes

- Post-ship, one manual step creates the weekly lint routine via `/schedule`
  (account-bound; its exact prompt is documented in lint.md). One follow-up KB gap:
  `/harness-layer:kb add https://code.claude.com/docs/en/routines` (kb-fetcher was
  unavailable during planning; claim verified live — see decisions.md).
- The pilot (AC7) is a pre-ship fixture eval: the build lead ingests the two
  committed fixture articles in a real session and records the evidence. The
  user's own fresh-article migration via Web Clipper is a post-ship follow-up
  tracked on issue #88, outside the definition of done (restructured at gate
  round 1 — reviews/findings-ledger.md R1-F6; surfaced at the spec human gate).

## Codex Verification

- **Outcome:** pending — recorded after the Codex gate settles
- **Rejected findings:** pending — recorded after the Codex gate settles
