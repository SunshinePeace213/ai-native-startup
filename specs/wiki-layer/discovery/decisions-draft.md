# Wiki Layer Redesign — Interview Decisions

## Summary

A new **wiki layer**: an LLM-maintained synthesis wiki at `ai-docs/wiki/` above the
immutable mirrors, following the Karpathy LLM-wiki pattern (KB:
`ai-docs/knowledge-base/`), with Obsidian as the human reading IDE. It ships as its
own layer separate from harness-layer: a `/wiki:*` command family, path-scoped rules,
multi-domain content (including a gitignored personal domain), gated crystallization
of plan-time research, and a wiki-first task-start protocol. No vector/RAG
infrastructure in v1; scale upgrades sit behind recorded triggers.

## Resolved Decisions

1. **Q:** Where does the synthesis wiki live? **A:** `ai-docs/wiki/`. **Why:** One KB
   tree and one Obsidian vault root; mirrors stay siblings as layer 1. Separation
   from harness-layer is expressed in commands/rules, not folders. Naming
   alternatives (`synthesis/`, `garden/`) rejected — every KB reference doc calls
   this layer "the wiki".
2. **Q:** What does the wiki cover? **A:** Multi-domain — personal, engineering,
   business, development, books, articles — with domain-specific page types.
   **Why:** User override of the engineering-only recommendation; the foundation
   doc's purpose modes all apply.
3. **Q:** Where does private data live? **A:** `ai-docs/wiki/personal/` exists
   locally but is gitignored — never pushed. Secret/PII stripping applies to every
   ingest in every domain. **Why:** The repo pushes to GitHub; personal content
   needs a hard boundary before any schema exists.
4. **Q:** How do domains structure the wiki? **A:** Domain folders under one shared
   core schema; each domain adds its own page types (engineering: topic / decision /
   comparison; personal & books seeded from the farzaa taxonomy). The wiki index
   groups by domain. **Why:** Shared schema keeps agents and lint consistent;
   folders keep browsing and scoping clean.
5. **Q:** Commands or skill? **A:** New command family `.claude/commands/wiki/`
   (`/wiki:ingest`, `/wiki:query`, `/wiki:lint`, `/wiki:status`) plus a path-scoped
   rule folder `.claude/rules/wiki-layer/` for ambient schema knowledge. **Why:**
   Operations are deliberate user-triggered passes → commands (like `/kb`); a
   path-scoped rule teaches any session touching `ai-docs/wiki/**` the schema. An
   auto-triggering skill is a later addition only if manual invocation proves
   too frequent.
6. **Q:** Which operations ship in v1? **A:** ingest · query · lint · status.
   cleanup and breakdown fold into lint as fix-what-it-can sub-steps. **Why:**
   Karpathy trio + a cheap readout; smallest surface that still schedules lint.
7. **Q:** When do operations expand? **A:** Trigger-based, each via the direct lane:
   `absorb` when the unprocessed-source backlog exceeds ~10; `breakdown` when lint
   repeatedly flags the same missing pages; `cleanup` graduates out of lint when its
   fix list needs its own pass. **Why:** Expansion follows demonstrated need, not
   ambition.
8. **Q:** Do plan-time findings file back into the wiki? **A:** Yes, through a
   quality gate (cited, non-duplicative) — amends the AGENTS.md durability rule.
   **Why:** Today plan-scoped research dies with its plan — the exact "nothing
   accumulates" failure the redesign exists to fix; the gate keeps junk out.
9. **Q:** How does "check the wiki first" become real? **A:** Amend the AGENTS.md
   Knowledge Base section: task-start check order = wiki index → mirror index → web.
   The rohitg00 session-start context hook is recorded as an automation-stage
   upgrade, added only if sessions demonstrably skip the wiki despite the rule.
   **Why:** Karpathy grounds the workflow in the schema document ("the schema is
   what makes the LLM a disciplined maintainer"; query = index-first); rohitg00
   places session-start injection in the automation stage — matching our
   trigger-based expansion policy.
10. **Q:** Linking style? **A:** `[[wikilinks]]` between wiki pages; standard
    markdown links for citations to mirrors. **Why:** Graph view and backlinks
    become first-class in Obsidian; mirror citations stay GitHub-renderable.
11. **Q:** Core frontmatter? **A:** `type`, `domain`, `status`
    (`current | superseded | disputed`), `created`, `updated`, `sources`, `related`.
    Status travels into query answers — disputed claims are flagged inline, never
    silently dropped. **Why:** Dataview and lint both depend on consistent fields;
    status propagation is the graphwiki doc's tested convention.
12. **Q:** How does lint run unattended? **A:** Weekly scheduled routine running
    `/wiki:lint` (fixes what it can — links, index rows; reports contradictions and
    staleness) plus on-demand invocation. **Why:** Drift is the #1 reported failure
    mode across every KB doc; lint must not depend on memory.
13. **Q:** Obsidian config in the repo? **A:** Commit a minimal `.obsidian/`
    (attachment folder → `assets/`, sane defaults); gitignore workspace/cache files.
    Supported plugin set documented in the layer standards: Web Clipper, Dataview,
    Marp. **Why:** Every clone opens identically; plugins stay a documented choice,
    not a hard dependency.
14. **Q:** Existing prior art? **A:** Fresh authoring. Study
    `ai-docs/knowledge-base/farzaa-wiki-gen-skill.md` for command shapes, writing
    standards (theme-over-chronology, anti-cramming/anti-thinning, quote
    discipline), and checkpoint audits — customize for this repo, do not port.
    **Why:** User override; the farzaa taxonomy is personal-life-shaped and needs
    adaptation anyway.
15. **Q:** Pilot migration? **A:** A fresh web article the user clips via Web
    Clipper after the layer ships, then ingests themselves. Pass criteria: valid
    frontmatter, ≥1 wikilink + ≥1 mirror/source citation, listed in the wiki index,
    visible in the Obsidian graph, `/wiki:query` answers a question about it with a
    citation, lint clean. **Why:** User override — tests the capture path end to
    end on a resource they choose.
16. **Q:** Metrics targets? **A:** 100% of ingests update index + log; lint clean or
    triaged within 7 days; every wiki claim cites ≥1 source; once seeded, each new
    plan cites ≥1 wiki page. **Why:** AGENTS.md layer requirement; targets map to
    the pattern's known failure modes.
17. **Q:** Archetype staffing? **A:** Prototyper + Builder now; Maintainer when lint
    automation lands. **Why:** AGENTS.md layer requirement; matches the layer's
    stage.
18. **Q:** Search & scale? **A:** Index-first navigation; no vector/RAG
    infrastructure in v1. Local hybrid-search CLI (qmd-style: BM25 + vectors + RRF)
    deferred until the wiki approaches ~150–200 pages. **Why:** Resolved
    pre-interview from the KB docs and confirmed by the user; agentic search is
    competitive at ~50 docs.
19. **Q:** What happens to the mirrors? **A:** Unchanged — immutable layer 1,
    fix-by-refetch via kb-fetcher. Ingest reads them; nothing moves or is edited.
    **Why:** Existing KB rule; the pattern requires immutable raw sources.
20. **Q:** Non-web source formats? **A:** PDFs use the existing `kind: pdf` +
    directory/index.md manifest pattern; websites via kb-fetcher / Web Clipper;
    images stored locally under `assets/` and read text-first-then-images.
    **Why:** All three already exist or follow the Karpathy tips directly.

## Assumptions

- The layer's standards file lives under `.claude/rules/wiki-layer/` (exact name at
  plan time) and the layer's KB group requirement is already satisfied by
  `knowledge-base` + `cerebras` in `sources.yaml`.
- The wiki keeps a `log.md` with grep-able `## [date] op | title` entry prefixes,
  per the Karpathy convention.
- Test tier per `test-tiers.md` and model/effort stamps per `model-selection.md`
  are resolved by the plan, not the interview.
- Single-user for now; multi-agent write coordination and shared/private promotion
  are deferred until team sharing becomes real.
- Secret/PII stripping is a schema rule checked by lint in v1, not a hook.

## Open Questions / Out of Scope

- Hybrid-search CLI selection (qmd vs. custom script) — deferred until the
  ~150–200-page trigger fires.
- Session-start wiki-context hook — deferred behind the "sessions skip the wiki"
  trigger.
- `absorb` / `breakdown` commands — out of scope for v1; triggers recorded in
  decision 7.
- Team sharing, mesh sync, shared/private promotion — out of scope for v1.
- Enterprise RAG stack (connectors, pgvector, planner/executor) — out of scope;
  `ai-docs/cerebras/how-we-built-our-knowledge-base.md` is the blueprint if that
  future ever arrives.
