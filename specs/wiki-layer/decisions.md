# Decisions: Wiki Layer

> The interview record for [spec.md](./spec.md) — why the plan is the way it is. Lifecycle
> tracking and the Codex review record live in spec.md, NOT here; this file is the
> immutable decision history.

## Summary

Build the wiki layer: an LLM-maintained synthesis wiki at `ai-docs/wiki/` above the
immutable mirrors, following the Karpathy LLM-wiki pattern, shipped as its own layer
separate from harness-layer. Multi-domain content (engineering, business, development,
books, articles, personal) over one shared core schema, with the personal domain
gitignored and local-only. Surface: a `/wiki:*` command family (ingest, query, lint,
status) plus a path-scoped standards rule. AGENTS.md gains a wiki-first task-start
protocol and a gated crystallization amendment to the durability rule. Obsidian is the
human reading IDE over the same folder. No vector/RAG infrastructure; scale upgrades
sit behind recorded triggers. Full interview: `discovery/decisions-draft.md`.

## Resolved Decisions

- **Q:** Where does the synthesis wiki live?
  - **A:** `ai-docs/wiki/`, with domain folders under one shared core schema.
  - **Why:** One KB tree and one Obsidian vault root; mirrors stay siblings as
    immutable layer 1. Separation from harness-layer is expressed in commands and
    rules, not folders. Naming alternatives (`synthesis/`, `garden/`) rejected — the
    KB reference docs all call this layer "the wiki".
- **Q:** `ai-docs/*` is gitignored (mirrors are regenerable, device-local) — how do
  wiki pages get tracked? *(codebase-resolved at plan time)*
  - **A:** Gitignore negations: `!ai-docs/wiki/` re-includes the wiki;
    `ai-docs/wiki/personal/` re-ignores the private domain; `!ai-docs/.obsidian/`
    tracks the vault config with `workspace*` ignored.
  - **Why:** Synthesis is compiled knowledge, not regenerable cache — it must be
    tracked. The same mechanism implements the privacy boundary: `personal/` never
    has tracked files, so it cannot reach the remote or cloud clones.
- **Q:** What does the wiki cover, and where does private data live?
  - **A:** Multi-domain — personal, engineering, business, development, books,
    articles — each a folder with its own page types over the shared core schema.
    `ai-docs/wiki/personal/` exists only locally (gitignored). Secret/PII stripping
    applies to every ingest in every domain.
  - **Why:** User override of the engineering-only recommendation; the repo pushes
    to GitHub, so personal content needs a hard boundary before any schema exists.
- **Q:** Commands or skill?
  - **A:** A command family at `.claude/commands/wiki/` (`/wiki:ingest`, `/wiki:query`,
    `/wiki:lint`, `/wiki:status`) plus a path-scoped rule at
    `.claude/rules/wiki-layer/wiki-standards.md`.
  - **Why:** Operations are deliberate user-triggered passes → commands, like `/kb`.
    The rule teaches any session touching `ai-docs/wiki/**` the schema. The official
    docs note new skills should prefer `.claude/skills/`, but `.claude/commands/`
    remains supported and is this repo's established convention (`harness-layer/`);
    conformance wins — flagged, not forked.
- **Q:** Which operations ship in v1, and when do more get added?
  - **A:** ingest · query · lint · status. Trigger-based expansion, each via the
    direct lane: `absorb` when the unprocessed-source backlog exceeds ~10;
    `breakdown` when lint repeatedly flags the same missing pages; `cleanup`
    graduates out of lint when its fix list needs its own pass.
  - **Why:** Karpathy trio + a cheap readout is the smallest surface that still
    schedules lint; expansion follows demonstrated need.
- **Q:** Do plan-time findings file back into the wiki?
  - **A:** Yes, through a quality gate (cited, non-duplicative) — the AGENTS.md
    durability rule is amended accordingly. Manual trigger in v1: crystallization
    runs as an ordinary `/wiki:ingest` over the qualifying artifact.
  - **Why:** Plan-scoped research dying with its plan is the exact "nothing
    accumulates" failure this layer exists to fix; the gate keeps junk out. No
    pipeline-command changes in v1 — separation of layers.
- **Q:** How does "check the wiki first" become real?
  - **A:** Amend the AGENTS.md Knowledge Base task-start protocol: wiki index →
    mirror index → web. A session-start context hook is deferred behind the
    "sessions demonstrably skip the wiki" trigger.
  - **Why:** Karpathy grounds the workflow in the schema document; rohitg00 places
    session-start injection in the automation stage — matching trigger-based
    expansion.
- **Q:** How does lint run unattended?
  - **A:** A weekly cloud routine (created via `/schedule` post-ship, documented in
    the lint command) runs `/wiki:lint` against a fresh clone and lands fixes as a
    `claude/`-branch PR; the command also runs on demand locally. `/loop` rejected.
  - **Why:** `/loop`/cron tasks are session-scoped and expire after 7 days; routines
    run on Anthropic-managed infrastructure on weekly cron and can open PRs. The
    fresh clone cannot see `personal/` (gitignored) — the privacy boundary holds by
    construction; personal-domain lint is on-demand local only.
- **Q:** Linking style?
  - **A:** `[[wikilinks]]` between wiki pages; standard markdown links for citations
    to mirrors and repo files.
  - **Why:** Graph view and backlinks become first-class in Obsidian; mirror
    citations stay GitHub-renderable.
- **Q:** Core frontmatter and status vocabulary?
  - **A:** `type`, `domain`, `status: current | superseded | disputed`, `created`,
    `updated`, `sources`, `related`. Status travels into query answers — a disputed
    claim is flagged inline, never silently dropped.
  - **Why:** Dataview and lint depend on consistent fields; status propagation is
    the graphwiki doc's tested convention.
- **Q:** Obsidian config in the repo?
  - **A:** Commit a minimal `ai-docs/.obsidian/` (attachment folder → `wiki/assets`,
    sane defaults); ignore `workspace*`. Web Clipper, Dataview, and Marp documented
    as the supported plugin set in the standards rule — recommended, never required.
  - **Why:** Every clone opens identically as a vault; plugins stay a documented
    choice, not a dependency.
- **Q:** Existing prior art?
  - **A:** Fresh authoring. Study `ai-docs/knowledge-base/farzaa-wiki-gen-skill.md`
    for command shapes, writing standards (theme-over-chronology,
    anti-cramming/anti-thinning, quote discipline), checkpoint audits, and
    concurrency rules — customize for this repo, do not port.
  - **Why:** User override; the farzaa taxonomy is personal-life-shaped and needs
    adaptation anyway.
- **Q:** Pilot migration?
  - **A:** A fresh web article the user clips via Obsidian Web Clipper after the
    layer ships, then ingests themselves with `/wiki:ingest`. Pass criteria in
    acceptance-criteria.md AC7.
  - **Why:** User override — exercises the capture path end to end on a resource
    they choose.
- **Q:** Metrics targets and archetype staffing (layer requirements)?
  - **A:** Targets: 100% of ingests update index + log; lint clean or triaged within
    7 days; every wiki claim cites ≥1 source; once seeded, each new plan cites ≥1
    wiki page. Archetypes: Prototyper + Builder now; Maintainer when lint automation
    lands. Lane fit: page edits and single-source ingests are direct-lane; new
    operations, schema changes, and anything touching commands/rules take the full
    lane.
  - **Why:** AGENTS.md requires a new layer to ship metrics, archetypes, and lane
    fit; targets map to the pattern's known failure modes.
- **Q:** Search and scale?
  - **A:** Index-first navigation; no vector/RAG infrastructure. A local
    hybrid-search CLI is deferred until the wiki approaches ~150–200 pages; the
    enterprise stack (connectors, pgvector, planner/executor) is out of scope with
    the Cerebras mirror as the blueprint if ever needed.
  - **Why:** Agentic search is competitive at ~50 docs; the KB docs put the
    index-first ceiling at 100–200 pages.
- **Q:** What happens to the mirrors?
  - **A:** Unchanged — immutable layer 1, fix-by-refetch via `kb-fetcher`. Ingest
    reads them; nothing moves or is edited. External URLs become mirrors via
    `/harness-layer:kb add` before ingest; local/personal files are read in place.
  - **Why:** Existing KB rule; the pattern requires immutable raw sources.

## Assumptions

- The wiki keeps `log.md` with grep-able entry prefixes (Karpathy convention),
  extended at gate round 1 to `## [YYYY-MM-DD] <op> | <title> | <source-path>`
  with `<op>` ∈ `ingest|lint` — see Locked Boundaries. Invalidated if a structured
  log becomes necessary.
- Secret/PII stripping is a standards-rule obligation checked by lint, not a hook,
  in v1. Invalidated if lint findings show leaks reaching pages.
- Single-user writes; farzaa-style re-read-before-edit discipline is sufficient
  concurrency control. Invalidated when team sharing or parallel wiki-writing agents
  arrive.
- The weekly lint routine is account-bound and cannot be committed; shipping
  documents its exact prompt in the lint command and the user creates it once via
  `/schedule`. Invalidated if routines gain committed/IaC configuration.
- Domain folders other than `personal/` are created by the first ingest that needs
  them (farzaa: don't pre-create); `personal/` is created lazily on the user's
  machine only.
- Test tier: drift (new registrations/frontmatter) per test-tiers.md; command
  behavior is covered at the eval tier by the AC7 fixture eval — a rubric scored
  over three repeated fresh-session runs (3/3 required). Full meta-skills eval
  automation is deferred; invalidated if command regressions slip past the
  three-run rubric.

## KB References

| Doc | Fetched | Grounds |
| --- | --- | --- |
| `ai-docs/knowledge-base/karpathy-llm-wiki.md` | 2026-08-07 | Three layers, ingest/query/lint, index.md + log.md conventions, Obsidian-as-IDE tips |
| `ai-docs/knowledge-base/farzaa-wiki-gen-skill.md` | 2026-08-07 | Command shapes, writing standards, checkpoint audits, concurrency rules (studied, not ported) |
| `ai-docs/knowledge-base/lucianfialho-graphwiki-pattern.md` | 2026-08-07 | `status` vocabulary + propagation into answers; drift as dominant failure mode; lint classes |
| `ai-docs/knowledge-base/rohitg00-llm-wiki.md` | 2026-08-07 | Lifecycle/expansion triggers, session-start hook deferred to automation stage, implementation spectrum |
| `ai-docs/cerebras/how-we-built-our-knowledge-base.md` | 2026-08-07 | The deferred enterprise-RAG blueprint (grounds the non-goal) |
| `ai-docs/anthropic/skills.md` | 2026-08-07 (refreshed this run) | Commands merged into skills; `.claude/commands/` still supported; the frontmatter reference (`description`, `argument-hint`, `allowed-tools`, `model`, `effort`, `disable-model-invocation`, `paths`); the command-naming table incl. nested namespaced invocation (`/apps/web:deploy`) |
| `ai-docs/anthropic/routines.md` | 2026-08-07 (gap-filled this run) | Weekly-lint mechanism: routines run on Anthropic-managed infrastructure against a fresh clone of the default branch (gitignored files never present), push `claude/`-prefixed branches / open PRs, weekly cron presets with 1-hour minimum interval, account-bound configuration |
| `ai-docs/anthropic/memory.md` | 2026-07-21 | `.claude/rules/` recursive discovery; `paths:` frontmatter loads on matching reads; no-`paths` loads at session start |
| `ai-docs/anthropic/scheduled-tasks.md` | 2026-07-21 | `/loop`/cron tasks are session-scoped with 7-day expiry — rules them out for weekly lint |

Cross-check (2026-08-07): the `claude-code-guide` subagent was unavailable in this
context (Agent tool not enabled at that step), so the cross-check ran as direct
WebFetches of the official pages; `memory` and `skills` confirmed the mirror claims
with no conflicts, and the stale skills mirror plus the missing routines mirror
were both fixed at gate round 1 (R1-F8/R1-F9): skills refreshed, routines mirrored
and registered. Scope note for R1-F10: subdirectory-command invocation as
`/<dir>:<name>` is grounded by the skills mirror's namespaced-invocation naming
table together with this repo's own convention (the working `/harness-layer:*`
command family — a repo artifact, locked as convention in this plan);
`/harness-layer:kb add` is likewise this repo's own command, whose source of truth
is its committed command file, not external platform behavior.

## Locked Boundaries

- Gate round 1 (R1-F6/R1-F14): AC7 restructured — the gating pilot is a pre-ship
  fixture eval (two committed related articles + rubric under `checks/fixtures/`)
  run by the build lead in a real session; the user's fresh-article Web Clipper
  migration moved to a post-ship follow-up on issue #88, outside the definition of
  done. Pending the user's confirmation at the spec human gate.
- Gate round 1 (R1-F18/R1-F19/R1-F21): personal domain keeps its own local-only
  `personal/index.md` + `personal/log.md`; the shared index/log never name
  personal content; log entries carry the canonical source path
  (`## [date] <op> | <title> | <source-path>`, `<op>` ∈ `ingest|lint`) as the
  idempotency identity.

## Open Questions / Out of Scope

- **Out of scope:** `absorb` / `breakdown` commands (triggers recorded above).
- **Out of scope:** hybrid-search CLI (qmd or custom) — deferred to the
  ~150–200-page trigger.
- **Out of scope:** session-start wiki-context hook — deferred behind the
  "sessions skip the wiki" trigger.
- **Out of scope:** team sharing, mesh sync, shared/private promotion, multi-agent
  wiki writes.
- **Out of scope:** enterprise RAG stack (connectors, embeddings tables,
  planner/executor).
- **Out of scope:** any edit to mirrors, `ai-docs/sources.yaml` semantics, or the
  `/harness-layer:kb` command.
- **Open question:** whether `related:` frontmatter plus `[[wikilinks]]` is enough
  cross-referencing, or a backlinks index file earns its place — owner: first lint
  cycles after the pilot.
