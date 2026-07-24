# Decisions: Soriza design department — first slice

> The interview record for [spec.md](./spec.md) — why the plan is the way it is. Sections
> `## Summary` through `## Open Questions / Out of Scope` are transcribed verbatim from the
> locked discovery ledger ([discovery/decisions-draft.md](./discovery/decisions-draft.md));
> nothing there is re-litigated. Plan-time additions live in `### Plan-level decisions`,
> `### Plan-time assumptions`, and `## KB References`.
> Interview: 2 page rounds + 2 direct follow-up rounds; sign-off approved with three naming/roster
> amendments folded in. Page: specs/soriza-cpo-department/discovery/interview.html.

## Summary

Soriza's design department — **soriza-design**, headed by the CPO persona — runs a client
web-design studio on top of this repo's harness layer. The client owns "what"; the department
owns discover → define → design and hands Ringo a brief packet. Slice 1 is a per-rung command
chain (`/soriza-design:intake → :brief → :sitemap → :wireframe → :section-briefs`) operating on
`projects/<client>/`, gated by a client intake questionnaire and a Definition of Ready, with
real starter doctrine in a path-scoped rules family, a company-wide staff roster, a design-shaped
git lane (PR per gate), lo-fi published wireframes, and a KB seeded with five official
design/UX/copy/typography sources. Pilot engagement: Soriza's own site. Delivery/production is a
future CTO department, out of scope.

## Resolved Decisions

- **Q:** What is the org unit called — is "CPO" a department?
  - **A:** The department is **soriza-design** (rules family `.claude/rules/soriza-design/`,
    command namespace `/soriza-design:*`). The CPO is the C-suite persona who heads it, not the
    department name.
  - **Why:** Correct org semantics; a future CTO heads their own department the same way. Rules
    out `soriza-cpo` as a folder/namespace name.

- **Q:** Where does the client project live?
  - **A:** `projects/<client>/` in this repo — brief, section briefs, IA, wireframes, asset
    checklist, decision log. The folder structure (via `projects/_template/`) is the first
    deliverable; the first client folder is a copy, not an invention.
  - **Why:** Locked pre-interview; mirrors the proven `specs/_templates/` pattern.

- **Q:** Human/agent boundary?
  - **A:** Agents draft every file intake → brief packet; Ringo owns asset/template collection
    and Claude Design prototyping. The department's output is the brief packet handed to Ringo.
  - **Why:** Locked pre-interview.

- **Q:** Org shape — command chain, orchestrator + specialists, or agent team?
  - **A:** Per-rung command chain: `/soriza-design:intake → :brief → :sitemap → :wireframe →
    :section-briefs`. Each rung reads the previous rung's file in `projects/<client>/`, is gated
    by its DoR, and commits as it goes.
  - **Why:** Mirrors the proven discovery-chain shape; one session's judgment end to end;
    cheapest context. Specialists and teams stay easy upgrades once the ladder proves out. Rules
    out subagent specialists and the engagement team for slice 1. (Nesting fact-check closed:
    Claude Code subagents nest since v2.1.172 with a fixed depth cap — `ai-docs/anthropic/subagents.md`
    — so all shapes were viable; the chain won on judgment, not capability.)

- **Q:** Do staff positions get names, and where is the roster?
  - **A:** Yes — the roster is **company-wide** at `.claude/rules/soriza/roster.md`: name,
    position, deliverable owned, status (active/planned). Names locked in the interview:
    - **Vera** — CPO, heads soriza-design; signs every packet before it reaches Ringo.
    - **Mira** — intake lead (`:intake`); patient questioner, nothing vague clears the DoR.
    - **Elias** — brief writer (`:brief`); narrative-first, briefs read like the client's story.
    - **Ivo** — IA architect (`:sitemap`); inventory-keeper, every section earns its place.
    - **Juno** — wireframer (`:wireframe`); spatial thinker, grayscale layouts that argue for themselves.
    - **Lior** — copywriter / section-brief author (`:section-briefs`); conversion-minded, writes
      backwards from each section's one desired action.
  - **Why:** Ringo wants a visible org chart — how many staff Soriza has and their status. Names
    are personas attached to roles, so they survive a later move from command rung to subagent.
    Company scope already fits the future CTO department; department doctrine stays in the
    department family.

- **Q:** Department memory?
  - **A:** Path-scoped rules family `.claude/rules/soriza-design/` scoped to `projects/**/*`:
    client-communication, intake-standards, definition-of-ready, brief-format, section-anatomy,
    **copywriting** (six doctrine files), plus a lessons log on the development-log.md contract.
    Pointed to from AGENTS.md. No parallel memory system, no new root markdown files.
  - **Why:** Locked pre-interview per the memory-series contract; copywriting added in round 2.

- **Q:** Doctrine files — real content day one, or stubs lessons fill?
  - **A:** All doctrine files carry real starter content day one — drafted at build from the KB
    and this discovery chain, reviewed by Ringo in the PR.
  - **Why:** Stubs gate nothing: an empty DoR can't gate intake, an empty section-anatomy can't
    shape a brief. Lessons refine real content instead of filling voids.

- **Q:** How does the department address "clients reject pages over weak copy and fonts"?
  - **A:** Copywriting is first-class doctrine: `copywriting.md` covers slogans, headlines, and
    section copy. Section briefs deliver draft copy held to that doctrine; the brief packet
    carries a typography-direction page for Ringo's prototyping.
  - **Why:** Ringo's field experience — attractiveness complaints trace to copywriting and fonts,
    not just structure. The department must know how to write, not only how to structure.

- **Q:** Page & section inventory — fixed five sections?
  - **A:** Dynamic per client: the sitemap/IA rung locks how many pages and which sections per
    page with the client. The template ships a **nine-skeleton starter library** of the essential
    modern-layout sections — header/navigation (logo, primary links, main action button), hero
    (headline, subheadline, imagery/video, primary CTA), logo tape (client/partner/media logos),
    features/solutions (grid or bento layout, short text blocks + iconography), testimonials
    (quotes, case studies, ratings), pricing/plans (tiered packages, per-tier feature list + CTA),
    content/blog (latest articles for engagement and SEO), footer (site map, legal/privacy,
    social, contact), plus a standalone CTA band — a starter library, not a fixed set; each
    skeleton carries "one job" and "one desired action" fields. The `:section-briefs` rung loops
    the locked inventory inline, with parallel fan-out as the escape hatch for large inventories.
  - **Why:** Ringo's essential-sections list for modern web layouts, supplied at sign-off. Scope
    is set at the IA rung, not assumed. Rules out a hardcoded five-section brief.

- **Q:** How do the client's answers reach `/soriza-design:intake`?
  - **A:** Ringo relays the client: intake interviews Ringo, who holds the client's raw materials
    (call notes, emails, existing site). A uv-script Stop hook verifies every Definition-of-Ready
    section exists in `projects/<client>/intake.md` before the run may end.
  - **Why:** Keeps client-communication doctrine simple; no client-facing surface in slice 1. The
    gate is code, not model memory (precedent: harness-plan's check_spec_completeness.py).

- **Q:** Git lane for client-work deliverables (briefs, wireframes)?
  - **A:** PR per gate. Rungs commit straight to the engagement branch; a `📝 docs(<client>)` PR
    only at gate points (brief approved, packet hand-off). A `projects/**`-scoped rule swaps the
    PR evidence block: DoR checklist + decision-log entry + client sign-off replace Test Evidence.
  - **Why:** Audit where it matters without PR ceremony per draft. Rules out PR-per-deliverable
    and the no-PR lane. (The harness build itself still uses the normal pipeline.)

- **Q:** Wireframe fidelity and client visibility?
  - **A:** Lo-fi grayscale, one self-contained HTML page per screen in
    `projects/<client>/wireframes/`, published as private artifact links Ringo shares. Each
    page's copy-as-prompt returns client reactions as structured change requests appended to
    `decision-log.md`.
  - **Why:** Structure-only keeps feedback on layout, not colors; styled directions would overlap
    Ringo's Claude Design prototyping lane. Rules out styled directions for slice 1.

- **Q:** KB — worktree availability and the design/ first cut?
  - **A:** Add an `ai-docs/` pattern to `.worktreeinclude` so cached mirrors copy into every
    fresh worktree (gap confirmed: `.gitignore:362` ignores `ai-docs/*` except sources.yaml).
    Seed a `design/` group with five official sources via `/harness-layer:kb add`: W3C WCAG 2.2
    quickref, web.dev Learn Design, one NN/g cornerstone (homepage/IA), NN/g writing-for-the-web,
    Google Fonts Knowledge. Homegrown doctrine stays in the rules family — never fake mirrors.
  - **Why:** The lean trio grounds structure/accessibility; the two additions ground copy and
    typography per Ringo's client-feedback experience. Rules out the broad sweep and deferring
    the seed.

- **Q:** Scoping shape?
  - **A:** One epic with child issues, one pipeline run per child (`epic.yml` and
    `specs/_templates/issues/epic.md` exist) — never one giant spec.
  - **Why:** Locked pre-interview.

- **Q:** Pilot engagement?
  - **A:** Soriza's own site — Ringo is the client. No external prior-art paths were named.
  - **Why:** Real stakes and a real reviewer while the ladder shakes out; no external deadline.

### Plan-level decisions

Locked at plan time, within the ledger's boundaries:

- **Epic realization.** This spec folder is the **epic master plan** bound to issue **#43**;
  it is not itself a buildable code plan. Each child issue gets its **own** pipeline run
  (plan → build → review → ship), its own small spec folder transcribed from this one, its own
  convention branch, and its own PR — because `/harness-layer:harness-build` binds one spec
  folder to one issue/branch/PR (`## Tracking`), so per-child PRs require per-child specs.
  Children filed now (issue creation is mandatory at plan time): **#44** KB seed · **#45**
  foundations · **#46** intake + DoR gate · **#47** ladder rungs · **#48** git lane.
- **Landing the epic docs.** No build run ever owns the epic branch, and child worktrees branch
  fresh from `origin/main` — so the epic planning docs land on `main` via a draft
  `📝 docs(spec)` PR (`Refs #43`, never `Closes`) opened after the Codex gate settles. This is a
  documented deviation from "harness-build opens PRs"; it exists only for the epic branch.
- **Child slugs and branches.** #44 `chore/44-soriza-design-kb-seed` · #45
  `feat/45-soriza-design-foundations` · #46 `feat/46-soriza-design-intake-gate` · #47
  `feat/47-soriza-design-ladder` · #48 `chore/48-soriza-design-git-lane`. Child plan runs skip
  issue creation (already filed) and link their branch with `gh issue develop <N>`.
- **Skeleton library home.** The nine section skeletons live at
  `projects/_template/section-briefs/_library/<section>.md` — the `:section-briefs` rung copies
  a skeleton per locked section; underscore prefix keeps the library out of the client's own
  brief listing.
- **Roster scope.** `.claude/rules/soriza/roster.md` carries `paths: ["projects/**/*"]` — it
  loads for client work, where the personas act; humans reach it via the AGENTS.md pointer. Not
  a flat always-loaded rule (memory-series reserves those for rules every session needs).
- **Git-lane file.** The `projects/**` git-lane rule is the family's **seventh** file,
  `.claude/rules/soriza-design/git-lane.md` — process, not doctrine, so the ledger's "six
  doctrine files" count stands.
- **Engagement ticket model.** One GitHub issue per engagement (the ticket), engagement branch
  `docs/<N>-<client>` via `gh issue develop`, rung commits `📝 docs(<client>): … / Refs #N`,
  gate-point PRs `Refs #N`, the packet hand-off PR carries `Closes #N`. Zero new machinery on
  top of git-workflow.md.
- **DoR gate source of truth.** `check_intake_readiness.py` hard-codes its required-sections
  tuple (precedent: `check_spec_completeness.py`); `definition-of-ready.md` carries the same
  checklist for humans and rungs; a sync test asserts the two match so they cannot drift.
- **DoR gate targeting is deterministic** *(round-1 fix)*. The intake command's first write
  records the invoked client slug in `projects/.intake-target` (gitignored, transient,
  overwritten per run); the hook reads it and gates exactly `projects/<target>/intake.md`.
  Missing/invalid target, `_`-prefixed target, or a target folder without `intake.md` → exit 2
  with a clear message (inside the command a target must exist, so blocking is correct);
  malformed stdin / unreadable files still fail open. The newest-modified heuristic is dropped —
  a complete client A can never release an incomplete client B (cross-client regression test
  required).
- **Wireframe delivery modes** *(round-1 fix)*. Publishing an artifact makes it visible only to
  its author (Ringo — the relay); "private links" are Ringo's review surface, not a client
  surface. Client-facing delivery is locked per engagement and recorded in `decision-log.md`:
  (a) pilot — Ringo *is* the client, the private artifact suffices; (b) external clients —
  organization sharing on Team/Enterprise, or an explicit public link with client consent
  recorded, or sending the self-contained HTML files directly (they are dependency-free by
  design, so the file *is* the deliverable). The rung must treat publishing as best-effort and
  never promise a private URL to someone outside the author's account.
- **Issue types.** #44 and #48 are `chore` (tooling/process); #45–#47 are `feat`; the epic
  carries `feat` + `epic`. All `priority:P2` (no external deadline).
- **Memory-doc gap folded into #44.** The official memory/rules docs page
  (`code.claude.com/docs/en/memory`) is missing from the KB; #44 registers it under `anthropic`
  alongside the five design sources (gap-fill by subagent was unavailable this run — see
  `## KB References`).

## Assumptions

- Per-file skeleton headings in `projects/_template/` are settled at plan time — invalidated if
  Ringo supplies a preferred brief format before the plan.
- The Definition-of-Ready checklist content is authored at build time inside
  `definition-of-ready.md` — invalidated if intake doctrine turns out to need Ringo's sign-off
  before any command can be built.
- Epic child-issue slicing is proposed at plan time (roughly: KB/worktree seed · template + rules
  family + roster · intake + DoR hook · ladder commands · git lane) — the plan may reshape it.
  *(Plan kept the five-child shape as proposed; filed as #44–#48.)*
- The existing worktree/spec slug `soriza-cpo-department` stays as-is (cosmetic); only the
  shipped folder/namespace names use `soriza-design`.

### Plan-time assumptions

- Exact NN/g article URLs are picked at #44's build (proposed: "Top 10 Guidelines for Homepage
  Usability" and the canonical writing-for-the-web article). If a source refuses fetching or
  turns out to be a hub page, the build substitutes the closest canonical article and records
  the swap in #44's decisions — invalidated only if NN/g blocks mirroring entirely, in which
  case a different official IA/copy source is proposed to Ringo.
- The W3C WCAG 2.2 quickref is a JS-heavy app; if its mirror comes back thin, #44 falls back to
  the WCAG 2.2 spec page and records the substitution.
- Publishing wireframe artifacts prompts for permission once per artifact; in non-interactive
  runs a denied/skipped publish leaves the HTML files as the canonical deliverable — the rung
  must treat publish as best-effort (mirrors the pipeline's own artifact rule).
- Child plan runs are near-mechanical transcriptions of this spec (ledger-complete → ask
  nothing) and should settle in one Codex round each — invalidated if a child's Codex review
  surfaces a real design gap, which then flows back here as a revision.

## Open Questions / Out of Scope

- **Out of scope:** delivery/production — a future CTO department.
- **Out of scope:** agent team per engagement — revisit after the ladder proves out.
- **Out of scope:** styled design directions for wireframes — lo-fi only in slice 1.
- **Out of scope:** client-facing intake surface — Ringo relays; no client-visible pages beyond
  shared wireframe links.
- **Out of scope:** subagent specialists (brief-writer, wireframer as agents) — the roster's
  named personas keep the door open.

## KB References

Docs consulted for this plan's harness claims (review profile: **kb-grounded**):

- `ai-docs/anthropic/skills.md` (fetched 2026-07-23) — commands merged into skills;
  `.claude/commands/` files keep working with the same frontmatter (`description`,
  `argument-hint`, `disable-model-invocation`); skill/command precedence and namespacing.
- `ai-docs/anthropic/hooks.md` (fetched 2026-07-23) — hooks declared in skill/command
  frontmatter are scoped to the component's lifecycle, all events supported (§"Hooks in skills
  and agents"); `Stop` fires when Claude finishes responding; `InstructionsLoaded` confirms
  `.claude/rules/*.md` files lazy-load; `WorktreeCreate` **replaces** default git behavior, so
  stock `.worktreeinclude` processing is skipped when a hook is configured.
- `ai-docs/anthropic/worktrees.md` (fetched 2026-07-23) — `.worktreeinclude` contract and the
  same not-processed-under-a-WorktreeCreate-hook caveat.
- `ai-docs/anthropic/artifacts.md` (fetched 2026-07-23) — "A new artifact is visible only to
  you"; sharing happens from the page header — grounds the private-wireframe-links flow.
- `ai-docs/anthropic/subagents.md` (fetched 2026-07-23) — carried from the discovery ledger's
  closed nesting fact-check; no subagents ship in slice 1.
- `ai-docs/anthropic/html-artifacts-workflows.md` (fetched 2026-07-23) — the copy-as-prompt
  two-way page pattern the wireframe rung's reaction loop is built on *(added at round 1 on
  Codex's recommendation)*.

Conflicts reconciled:

- The ledger's `.worktreeinclude` decision vs. the official caveat that a configured
  `WorktreeCreate` hook skips stock `.worktreeinclude` processing: **resolved in repo source** —
  this repo's `worktree/worktree_create.py` re-implements the copy itself
  (`copy_worktree_includes`, `fnmatch` against `git ls-files -oi`), and `fnmatch`'s `*` crosses
  `/`, so a single `ai-docs/*` pattern covers nested mirrors. Decision unchanged; mechanism now
  documented.

Process notes:

- The `claude-code-guide` cross-check and `kb-fetcher` gap-fill subagents were **permission-denied**
  in this session; claims above rest on the 1-day-old mirrors plus repo source
  (`worktree_create.py`, `check_spec_completeness.py`, `test_wiring.py`). The missing official
  memory/rules page mirror is folded into #44 rather than hand-authored (mirrors are never
  hand-written).
- No doc consulted was older than STALE_AFTER (30 days); no `/kb` refresh needed for this plan.
- The `sonnet` review-runner subagent was also permission-denied, so the lead ran the exact
  `codex exec` review command via Bash itself (same worktree, model, effort, prompt, and verdict
  file) — a documented deviation preserving the gate's substance; digests were still relayed to
  the issue by the lead, and Codex still never called `gh`.

### Follow-ups (advisories, future plans)

- After the ladder proves out in the pilot, revisit subagent specialists / engagement teams
  (out-of-scope ledger items) as their own discovery chain.
- Round-1 advisory (applied): `html-artifacts-workflows.md` added to KB References above — no
  further action.
- Rung-prompt *runtime* behavior (idempotent scaffold, DoR refusal wording, per-rung commits)
  is validated structurally at build, by each child's harness-review, and live at the pilot's
  first intake — if the pilot exposes gaps, they land in `soriza-design/lessons.md` and, if
  structural, as a revision of #46/#47.
