# Decisions: c-suite CPO department

> The grilling record for [spec.md](./spec.md) — why the plan is the way it is. Lifecycle tracking and
> the Codex review record live in spec.md, NOT here; this file is the immutable decision history.

## Summary

Soriza's first c-suite department. The AI owns Workflow 1 (client discovery → cross-reviewed PRD) and Workflow 2 (six-file design handoff package); the human owns Workflow 3 (prototyping in Claude Design) and everything after it. The department ships as three stage commands, three knowledge skills (each bundling the templates for the files it teaches), one Codex review skill, three rules files (roster/operations/lessons), and five persona subagents — the six-layer pattern every future department copies. Each client engagement lives in `products/<client-slug>/` with its own issue, branch, status ledger, and end-of-department PR.

## Resolved Decisions

- **Q:** What does this plan ship — the whole CPO pipeline or a slice?
  - **A:** The AI-owned pipeline only: Workflow 1 (intake → PRD) and Workflow 2 (design package). Workflow 3 (prototyping) is human-owned in Claude Design; everything after the final prototype is out of scope.
  - **Why:** The user clarified Claude Design is a Claude App feature they drive themselves; the department's value is preparing documents good enough that the human designer needs no further client contact. Rules out prototype/variant automation and any CTO handoff packet.
- **Q:** What files does the design team actually need (Workflow 2 output)?
  - **A:** Six files: `project-brief.md` (with design-constraints section), `sitemap-and-flows.md` (mermaid), `section-briefs.md`, `copy-deck.md`, `brand-inputs.md`, `wireframes/<page>.html` (lo-fi, unstyled, self-contained).
  - **Why:** Matches a professional product→design handoff; the copy deck and brand-inputs inventory are the two most commonly skipped files and the top cause of designer→client re-contact. Rules out the 3-file minimum.
- **Q:** How many stage commands, and how are they named?
  - **A:** Three — `.claude/commands/c-suite/cpo-intake.md`, `cpo-prd.md`, `cpo-brief.md` → `/c-suite:cpo-intake`, `/c-suite:cpo-prd`, `/c-suite:cpo-brief`.
  - **Why:** One directory level is the only namespacing proven in this repo (`/harness-layer:*`); two-level (`/c-suite:cpo:intake`) appears in no official doc. Three commands = one fresh session per stage (context management) and a pause point for async clients. Rules out a centralized mega-command and two-level nesting.
- **Q:** How are commands, skills, rules, templates, and agents divided so future departments don't accrue debt?
  - **A:** The six-layer architecture: commands own sequence, skills own knowledge, rules own memory, agents own labor, Codex owns cross-model QA, `products/` owns client work. Locked as the department pattern.
  - **Why:** The user explicitly asked for a clear commands-vs-skills division now "for preventing the debt in the future"; each layer has exactly one kind of content, so a CTO department adds files beside CPO's with zero collisions.
- **Q:** Where do the nine engagement templates live — a top-level `products/_templates/` or inside the skills?
  - **A:** Inside their owning skill's `templates/` directory, per the meta-skills supporting-files standard: `cpo-question-bank/templates/` carries `question-list.md`, `requirements.md`, `status.md`; `cpo-prd-standard/templates/` carries `prd.md`; `cpo-design-standard/templates/` carries `project-brief.md`, `sitemap-and-flows.md`, `section-briefs.md`, `copy-deck.md`, `brand-inputs.md`. Commands reference them via `${CLAUDE_SKILL_DIR}`.
  - **Why:** User revision during spec drafting — knowledge and its blank form travel together, so a stage command loads one skill and gets both. Rules out the originally proposed `products/_templates/` (a second location to keep in sync).
- **Q:** Where do the persona subagent files live?
  - **A:** `.claude/agents/cpo/` — one agents folder per department (`cto/`, `cmo/` later), filenames matching the `name` field (`cpo-pm.md` → `name: cpo-pm`).
  - **Why:** User revision during spec drafting, for better management. Safe per the KB: `.claude/agents/` is scanned recursively and identity comes only from the `name` frontmatter; the `cpo-` name prefix prevents cross-department collisions.
- **Q:** How does an engagement flow through git/GitHub?
  - **A:** One issue + branch `feat/<N>-<client-slug>` per engagement; every stage commits and pushes with `Refs #N`; Codex PRD digests land as issue comments; ONE PR opens after the Design Lead approves the W2 package and closes the issue.
  - **Why:** Durable tracking (the user's "hard to track" worry) without a draft PR sitting open for weeks while an async client answers. Rules out committing to main and the intake-time draft PR.
- **Q:** How does intake handle vague input and unavailable clients?
  - **A:** Dual-mode. LIVE → grilling protocol via AskUserQuestion until every dimension locks. ASYNC → the UX Researcher persona generates `discovery/question-list.md`, a client-ready document (grouped by topic, each question with a why-we-ask line); re-running `cpo-intake` ingests returned answers into `discovery/client-answers.md` and continues until `requirements.md` locks.
  - **Why:** The user's two explicit cases; interviews ensure the design team has enough information before any design work. Re-entrancy is what makes async possible at all.
- **Q:** How is the PRD quality-gated?
  - **A:** A new Codex skill `.agents/skills/prd-review/` mirroring `spec-review` mechanics — `### Round N — Verdict:` first line, report file `products/<slug>/prd/reviews/codex-prd-review-round-N.md`, terse CLI return, issue-comment digest relayed by the orchestrator, max 2 rounds, over-cap AskUserQuestion gate (one more round / accept-with-noted-gaps / needs-human).
  - **Why:** The user wants Claude-created files cross-reviewed by another model against domain knowledge, "like what we have mentioned before" — the same trust model as harness specs. Rules out reusing `spec-review` (wrong criteria) and unbounded rounds.
- **Q:** How does the department remember mistakes?
  - **A:** Every CPO command ends with a lessons check: a pitfall hit during the run is appended as a one-line prevention rule to `.claude/rules/c-suite/cpo-lessons.md`.
  - **Why:** The user asked for the harness-layer memory pattern applied to the department — "what issues are found and write it to rules for preventing errors again".
- **Q:** Who is on the roster, and how much role-play?
  - **A:** AI staff: Ethan Park (PM), Priya Nair (UX Researcher), Jonas Weber (UX Designer), Yuki Tanaka (UI Designer), Daniel Osei (Design Lead). Sofia Reyes (CPO) is the orchestrating session, not a subagent. The human holds the prototype-owner seat (Workflow 3, Claude Design), recorded in `roster.md`. Persona names sign reports; deliverables stay plain and professional.
  - **Why:** The user wants a company-structure file for management and confirmed the UI Designer is an AI persona who brainstorms W2 materials WITH the UX Designer, while the human owns the prototype itself. No VP/Head of Product (span-of-control layer with one PM) and no Product Owner (Scrum backlog role folded into PM).
- **Q:** How is the department proven done?
  - **A:** Structural checks (files, frontmatter, agent/skill validation scripts) plus an end-to-end dry run with a fictional client (Bluebird Bakery) covering intake → Codex-gated PRD → six-file design package, kept as the fixture `products/_example-bluebird-bakery/`.
  - **Why:** A department that has never served a client isn't done; the fixture keeps acceptance re-checkable and doubles as documentation.

## Assumptions

- Model/effort stamps in tasks.md follow `.claude/rules/model-selection.md`; the build lead may escalate a tier when output misses the bar — invalidated only if that rule file changes.
- Knowledge skills use the currently documented frontmatter (`autoInvoke: false`) and are loaded by the commands (Skill tool or `dependencies:`); the repo's older `disable-model-invocation` field is left untouched in existing skills. Invalidated if the build's smoke check shows `autoInvoke` unsupported in this Claude Code version — fall back to the repo's proven `disable-model-invocation: true`.
- The question bank's dimension list (business & goals, audience, brand & voice, content & assets, structure & pages, features, integrations & data, technical/hosting constraints, budget & timeline, success metrics, references & competitors, legal/compliance) is authored at build time from industry practice — tuned after the first real engagement.
- Status-ledger stage states are `not-started | in-progress | blocked-on-client | stale | done` per stage (`intake`, `prd`, `brief`), plus the engagement-level `handed-off` marker — invalidated if the dry run shows a needed state is missing.
- Engagement work happens on the engagement's own worktree/branch with the explicit push refspec, mirroring `.claude/rules/git-workflow.md`'s worktree rule.
- The dry-run fixture is allowed under `products/` despite "no real client content" — it is a fictional client marked by the `_example-` prefix.
- `status.md`'s template lives in `cpo-question-bank/templates/` because intake is the stage that scaffolds an engagement — invalidated if a later department needs the ledger without the question bank (then it moves to a shared location).

## Blindspots

- **Where does client work live?** — engagement outputs need a durable home; `specs/` is reserved for harness plans. Resolved: `products/<client-slug>/` with `discovery/`, `prd/`, `design/` subfolders + `status.md`; one issue/branch per engagement (user accepted).
- **The client interview can't be delegated to a persona subagent** — AskUserQuestion is unavailable to subagents (ai-docs/anthropic/subagents.md), so the interviewer fantasy breaks. Resolved: the session interviews; Priya (UX Researcher) generates question lists and analyzes answer gaps between rounds (user accepted; noted the interview exists so the design team has enough information).
- **Two-level command namespacing is unverified** — `/c-suite:cpo:intake` appears in no official doc; only one directory level is proven here. Resolved: flat one-level naming `/c-suite:cpo-<stage>` locked; two-level testing deferred to an optional future chore.
- **Stage handoffs and the final CTO packet** — one session can't hold a multi-week engagement; downstream needs defined inputs. Resolved: one command per stage, committed artifacts + `status.md` ledger between sessions, preflight gates on predecessor state; the CTO packet fell out of scope entirely (post-prototype).
- **The PRD needs its own Codex review skill** — `spec-review` judges harness specs, not product documents. Resolved: `prd-review` mirrors the mechanics with PRD-specific criteria (user confirmed cross-model, domain-knowledge judging).
- **What "Claude Design" actually is here** — it is a Claude App feature the human uses; DesignSync/claude.ai-design integration is NOT part of the department. Resolved: the department ends at the design package; the human prototypes from it (user clarified).
- **Persona economics and theater level** — over-casting burns context; role-play voice risks unprofessional deliverables. Resolved: five working personas + CPO-as-session; names sign reports, documents stay professional; roster records human vs AI seats (user confirmed, adding Yuki Tanaka as the AI UI Designer who co-authors W2 materials).

## KB References

- `ai-docs/anthropic/subagents.md` (fetched 2026-07-05) — AskUserQuestion (with EnterPlanMode, ScheduleWakeup…) is unavailable to subagents even when listed in `tools`; `.claude/agents/` is scanned recursively with identity from the `name` field (subfolder `c-suite/` is safe); model frontmatter accepts aliases with documented resolution order.
- `ai-docs/anthropic/skills.md` (fetched 2026-07-05) — custom commands are merged into skills (both create `/name`); skill frontmatter surface: `description`, `autoInvoke`, `invoke`, `runAs`, `model`, `dependencies`, `tags`; project skills override personal; `.claude/commands/` files keep working.
- Live re-fetch of <https://code.claude.com/docs/en/skills> (2026-07-17) — the command-name table maps `.claude/commands/<file>.md` → `/<file>` and documents no subdirectory namespacing for the commands dir, while this repo's live behavior resolves `.claude/commands/harness-layer/harness-plan.md` as `/harness-layer:harness-plan`. **Conflict resolution:** treat one-level `dir:name` as proven-by-observation in this repo, treat two-level as unsupported until tested, and keep a build-time resolution smoke check (AC2). KB mirror is 12 days old (not stale) and consistent with the live page — no refresh committed.
- `ai-docs/anthropic/html-artifacts-workflows.md` (fetched 2026-07-16) — interactive-page patterns backing the blindspot board artifact.
- Field-name conflict: this repo's existing skills use the legacy `disable-model-invocation: true`, the current doc documents `autoInvoke`/`invoke`. Resolution: new skills use the current documented fields with a build-time fallback to the legacy field (see Assumptions); existing files untouched.

## Open Questions / Out of Scope

- **Out of scope:** Workflow 3 (human prototyping in Claude Design) and anything after the final prototype, including any CTO handoff packet.
- **Out of scope:** CTO, CMO, CEO departments — future plans that copy this pattern.
- **Out of scope:** real client engagements under `products/` (only `_templates/` and the `_example-bluebird-bakery/` fixture ship).
- **Out of scope:** two-level command namespacing — optional future chore to test `/c-suite:cpo:intake` empirically.
- **Open question:** question-bank depth per project type (brochure site vs web app) — owner: first real engagement's lessons check.
- **Open question:** whether the design package later gains a moodboard/inspiration file — owner: the human designer after the first Workflow 3 run.
