# Decisions: Soriza design department — first slice

> The interview record for the soriza-design department slice — why the plan is the way it is.
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

## Resolved Decisions — codex round-2 blocker pass (2026-07-24)

> Verification interview after commit 46f9f80; zero open questions — all three answered by the
> branch state and signed off directly.

- **Q:** How is the intake Stop-hook race between concurrent client intakes resolved?
  - **A:** Per-client markers: the intake command's first write drops
    `projects/<client>/.intake-in-progress` (pattern gitignored); the hook gates until every
    marked client's `intake.md` is complete and sweeps markers on already-complete clients. No
    shared `.intake-target` file remains. AC8 carries the cross-client regression plus a
    two-marker concurrent-intake test.
  - **Why:** A single shared target file is overwritten by whichever invocation runs last;
    per-client markers make the gate invocation-scoped without needing session identity.

- **Q:** What does the final rung read as its predecessor?
  - **A:** `section-briefs` (Lior) reads `wireframes/` — the approved layouts plus
    `decision-log.md` change requests — with `sitemap-ia.md` retained only as inventory
    context. Task 5 and AC9's chain mapping both assert it.
  - **Why:** The ladder's contract is each rung consumes the previous rung's output; mapping
    the final rung to `sitemap-ia.md` let a build skip the wireframe output and still pass.

- **Q:** How do AC7 and AC9–AC11 avoid passing on loose keyword presence?
  - **A:** Each command carries a `## Rung Contract` block; the validation commands regex-parse
    the block and assert individual fields — `Staffer:`, `First write:` (marker-first),
    `Reads:`/`Writes:`, `DoR gate:`, `Refusal:`, `Commit:`, `Publish:` (best-effort + all
    three delivery modes, no external dependencies), `Packet:` contents, `Sign-off:` Vera, the
    git lane's exactly-two gate points, and the evidence-swap clause — failing when any
    required instruction is absent or contradicted.
  - **Why:** Keyword checks pass on mentions; field assertions fail when the contract is
    missing or contradicted, which is what the review demanded.

## Assumptions

- Per-file skeleton headings in `projects/_template/` are settled at plan time — invalidated if
  Ringo supplies a preferred brief format before the plan.
- The Definition-of-Ready checklist content is authored at build time inside
  `definition-of-ready.md` — invalidated if intake doctrine turns out to need Ringo's sign-off
  before any command can be built.
- Epic child-issue slicing is proposed at plan time (roughly: KB/worktree seed · template + rules
  family + roster · intake + DoR hook · ladder commands · git lane) — the plan may reshape it.
- The existing worktree/spec slug `soriza-cpo-department` stays as-is (cosmetic); only the
  shipped folder/namespace names use `soriza-design`.

## Open Questions / Out of Scope

- **Out of scope:** delivery/production — a future CTO department.
- **Out of scope:** agent team per engagement — revisit after the ladder proves out.
- **Out of scope:** styled design directions for wireframes — lo-fi only in slice 1.
- **Out of scope:** client-facing intake surface — Ringo relays; no client-visible pages beyond
  shared wireframe links.
- **Out of scope:** subagent specialists (brief-writer, wireframer as agents) — the roster's
  named personas keep the door open.
