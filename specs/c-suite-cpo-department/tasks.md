# Tasks: c-suite CPO department

> Execution plan for [spec.md](./spec.md). Owner and scope are defined there; this file is how & who.

## Implementation Phases

### Phase 1: Foundation

The department's memory and expertise: the `.claude/rules/c-suite/` family (roster, operations, lessons) and the three knowledge skills with their bundled engagement templates. Everything else reads these.

### Phase 2: Core Implementation

The staff and the procedures: five persona subagents, the Codex `prd-review` skill, and the three stage commands that orchestrate them.

### Phase 3: Integration & Polish

Hub wiring (AGENTS.md pointers), the command-resolution and skill-invocation smoke checks, the Bluebird Bakery dry-run fixture, and full validation.

## Team Orchestration

- You operate as the team lead and orchestrate the team to execute the plan.
- IMPORTANT: You NEVER operate directly on the codebase. You use the `Task*` tools to deploy team
  members to build, validate, test, and deploy. Your job is to direct, not to build.
- Keep the shared task list (TaskCreate/TaskUpdate) as the single source of truth for who is doing
  what; verify each task on the board before marking it complete.
- Note the session id / name of each team member — that is how you reference them.
- Effort stamps below are depth guidance for each builder's task brief (subagents inherit the
  session's reasoning effort); model stamps go through the Agent tool's `model` parameter.

## Team Members

- **Builder**
  - **Name:** builder-rules
  - **Role:** The `.claude/rules/c-suite/` family — roster, operations, lessons
  - **Agent Type:** general-purpose
  - **Resume:** true
- **Builder**
  - **Name:** builder-skills
  - **Role:** The three knowledge skills and their bundled `templates/` files
  - **Agent Type:** general-purpose
  - **Resume:** true
- **Builder**
  - **Name:** builder-agents
  - **Role:** The five persona subagent files
  - **Agent Type:** general-purpose
  - **Resume:** true
- **Builder**
  - **Name:** builder-review-skill
  - **Role:** The Codex `prd-review` skill
  - **Agent Type:** general-purpose
  - **Resume:** true
- **Builder**
  - **Name:** builder-commands
  - **Role:** The three `/c-suite:cpo-*` stage commands
  - **Agent Type:** general-purpose
  - **Resume:** true
- **Builder**
  - **Name:** builder-hub
  - **Role:** AGENTS.md hub pointers and structure docs
  - **Agent Type:** general-purpose
  - **Resume:** true
- **Builder**
  - **Name:** validator
  - **Role:** Smoke checks, dry-run support, and final validation sweep
  - **Agent Type:** general-purpose
  - **Resume:** true

## Step by Step Tasks

- Execute every step in order, top to bottom. Each task maps directly to one `TaskCreate` call.
- Before starting, run `TaskCreate` for every task below so all team members can see the board.
- Each task names the acceptance criteria (from acceptance-criteria.md) it satisfies, so work traces to "done".

### 1. Department rules family

- **Task ID:** c-suite-rules
- **Depends On:** none
- **Assigned To:** builder-rules
- **Agent Type:** general-purpose
- **Model / Effort:** `sonnet` / `medium`
- **Parallel:** true
- **Satisfies:** AC6
- Create `.claude/rules/c-suite/roster.md`: the org chart table — seat, persona name, human/AI, model alias, what they own, deployed-as — covering Sofia Reyes (CPO — the orchestrating session), Ethan Park (PM, `opus`), Priya Nair (UX Researcher, `sonnet`), Jonas Weber (UX Designer, `sonnet`), Yuki Tanaka (UI Designer, `sonnet`), Daniel Osei (Design Lead, `opus`), and the human prototype-owner seat (Workflow 3, Claude Design).
- Create `.claude/rules/c-suite/cpo-operations.md`: engagement folder schema (`products/<client-slug>/` with `status.md`, `discovery/`, `prd/`, `design/`), status-ledger stage states (`not-started | in-progress | blocked-on-client | stale | done` per stage + engagement-level `handed-off`), stage preflight gates, and the engagement git flow (issue + branch `feat/<N>-<client-slug>`, `Refs #N` commits, explicit push refspec, one PR after Design-Lead approval closes the issue).
- Create `.claude/rules/c-suite/cpo-lessons.md`: seeded lessons file — one-line intro stating the append format (date, stage, pitfall → prevention rule), no entries yet.
- All three files carry `paths:` frontmatter scoping to `products/**/*` and `.claude/commands/c-suite/**` so they load only for department work. Keep each file short, imperative, KISS per AGENTS.md harness rules.

### 2. Knowledge skills with bundled templates

- **Task ID:** knowledge-skills
- **Depends On:** none
- **Assigned To:** builder-skills
- **Agent Type:** general-purpose
- **Model / Effort:** `opus` / `high`
- **Parallel:** true
- **Satisfies:** AC5, AC7
- Create `.claude/skills/cpo-question-bank/SKILL.md`: the discovery expertise — dimensions (business & goals, audience & users, brand & voice, content & assets, structure & pages, features & functionality, integrations & data, technical & hosting constraints, budget & timeline, success metrics, references & competitors, legal/compliance), per-dimension question templates with why-we-ask lines, and per-dimension "locked when" criteria. Bundle `templates/question-list.md` (client-ready document skeleton, grouped by topic), `templates/requirements.md` (locked-requirements skeleton keyed by the same dimensions), `templates/status.md` (the engagement ledger skeleton).
- `templates/status.md` carries, per stage (`intake`, `prd`, `brief`): the state field, a log line for each run (date, commits pushed, lessons-check result — "none" allowed), plus engagement-level fields for the issue `#N`, branch name, and (after brief) the PR URL — so ledger greps can prove the GitHub trail.
- Create `.claude/skills/cpo-prd-standard/SKILL.md`: the Soriza PRD structure (overview, goals & measurable success metrics, users/personas, scope & non-goals, user stories with acceptance criteria, functional requirements per feature/section, content requirements, technical constraints, risks, open questions), the quality bar, and how each PRD section maps from `requirements.md`. Bundle `templates/prd.md`.
- Create `.claude/skills/cpo-design-standard/SKILL.md`: the section catalog (hero, navigation, social proof, features, case study, pricing, FAQ, CTA, footer, about, contact — each with purpose, content fields, common variants), wireframe conventions (lo-fi HTML: grayscale, layout-only, self-contained, annotation comments), copy-deck format, brand-inputs format (client-provided tokens/assets inventory + gap list for the human designer), and the Design-Lead package-review checklist. Bundle `templates/project-brief.md` (with design-constraints section), `templates/sitemap-and-flows.md` (mermaid skeleton), `templates/section-briefs.md`, `templates/copy-deck.md`, `templates/brand-inputs.md`.
- All three skills: `autoInvoke: false` frontmatter (never auto-fire; loaded by the stage commands), descriptions written per the meta-skills standard, bodies in KISS prose. Skills reference their bundled files via `${CLAUDE_SKILL_DIR}`.

### 3. Persona subagents

- **Task ID:** persona-agents
- **Depends On:** knowledge-skills
- **Assigned To:** builder-agents
- **Agent Type:** general-purpose
- **Model / Effort:** `opus` / `medium`
- **Parallel:** true
- **Satisfies:** AC8
- Create five agents under `.claude/agents/cpo/` (one agents folder per department — user decision) following the meta-agent standard, each with `name`, delegation-tuned `description`, restricted `tools`, and `model`; filenames match the `name` field:
  - `cpo-pm.md` — Ethan Park, PM (`opus`): drafts `prd.md` from `requirements.md` per the cpo-prd-standard skill; also drafts `project-brief.md` and `copy-deck.md` in Workflow 2.
  - `cpo-ux-researcher.md` — Priya Nair, UX Researcher (`sonnet`): generates the client question list from the question bank; between answer rounds, gap-analyzes `client-answers.md` against the dimensions and reports what is still open.
  - `cpo-ux-designer.md` — Jonas Weber, UX Designer (`sonnet`): drafts `sitemap-and-flows.md`, the structural skeleton of `section-briefs.md`, and the lo-fi `wireframes/<page>.html`.
  - `cpo-ui-designer.md` — Yuki Tanaka, UI Designer (`sonnet`): drafts `brand-inputs.md`, the visual-direction section of the project brief, and the visual-guidance notes inside `section-briefs.md` — brainstorming W2 materials with Jonas; never hi-fi design.
  - `cpo-design-lead.md` — Daniel Osei, Design Lead (`opus`): reviews the full six-file package against the cpo-design-standard checklist and returns blocking findings or approval.
- Every persona declares its knowledge skill(s) in `skills:` frontmatter so the content is preloaded into its fresh context (KB: subagents.md "Preload skills into subagents"): cpo-pm → `cpo-prd-standard`, `cpo-design-standard`; cpo-ux-researcher → `cpo-question-bank`; cpo-ux-designer, cpo-ui-designer, cpo-design-lead → `cpo-design-standard`.
- None interviews the user (AskUserQuestion is unavailable to subagents); each returns files plus a short hand-off. Persona voice: name signs the report, content stays professional.

### 4. Codex prd-review skill

- **Task ID:** prd-review-skill
- **Depends On:** knowledge-skills
- **Assigned To:** builder-review-skill
- **Agent Type:** general-purpose
- **Model / Effort:** `opus` / `high`
- **Parallel:** true
- **Satisfies:** AC4, AC9
- Create `.agents/skills/prd-review/SKILL.md` mirroring `.agents/skills/spec-review/SKILL.md` mechanics exactly: caller injects the round number; report file `products/<client-slug>/prd/reviews/codex-prd-review-round-N.md`; first line `### Round N — Verdict: approved|changes-requested` (em-dash); terse two-line CLI return; `**Issue-comment digest:**` closing paragraph; edits only its own report; never calls `gh`.
- PRD-specific blocking criteria: a requirement in `requirements.md` with no PRD coverage; a PRD claim contradicting a locked requirement; unmeasurable success metrics; user stories without acceptance criteria; scope drift beyond the locked requirements; missing PRD sections per the cpo-prd-standard structure; infeasible features given the recorded technical constraints; security/data risks. Advisory (non-blocking): simpler product shape, cut-scope suggestions.
- Inputs it reads: `prd.md`, `discovery/requirements.md`, and the cpo-prd-standard skill for the structure bar.

### 5. Command-naming probe

- **Task ID:** naming-probe
- **Depends On:** none
- **Assigned To:** validator
- **Agent Type:** general-purpose
- **Model / Effort:** `sonnet` / `low`
- **Parallel:** true
- **Satisfies:** AC2
- Create a stub command file `.claude/commands/c-suite/cpo-probe.md` (frontmatter description + one-line body), then read its resolved name from a headless listing: `claude -p 'Reply with only the names of available skills or commands containing "cpo-probe".'`.
- Record the winning canonical prefix (`/c-suite:cpo-<stage>` if the listing shows `c-suite:cpo-probe`, else `/cpo-<stage>`) in the naming section of `.claude/rules/c-suite/cpo-operations.md` (coordinate with builder-rules if it lands first), then delete the stub (`mv` to trash, never `rm -rf`).
- Report the winner in the hand-off — `stage-commands` and all user-facing text use it verbatim.

### 6. Stage commands

- **Task ID:** stage-commands
- **Depends On:** c-suite-rules, knowledge-skills, persona-agents, prd-review-skill, naming-probe
- **Assigned To:** builder-commands
- **Agent Type:** general-purpose
- **Model / Effort:** `opus` / `high`
- **Parallel:** false
- **Satisfies:** AC1, AC2, AC3, AC4, AC12
- Create the three commands in `.claude/commands/c-suite/`, each following the house five-section format (`command-format.md`) with a frontmatter `description` and `argument-hint`:
  - `cpo-intake.md` (`cpo-intake <client-slug> [request…]`): preflight (`gh` auth; validate the slug against `^[a-z0-9][a-z0-9-]{0,38}[a-z0-9]$` — fixtures `_example-` + valid slug — STOP on violation, quote every interpolation; detect existing engagement → resume, else scaffold `products/<client-slug>/` from the question-bank skill's templates, create the engagement issue + linked branch + worktree); mode check via AskUserQuestion (client live vs async); LIVE → grill dimension by dimension from the question bank until each is locked; ASYNC → deploy Priya to generate `discovery/question-list.md` and stop with send-to-client instructions; re-entrant runs ingest answers into `discovery/client-answers.md`, deploy Priya for gap analysis, and continue until `requirements.md` locks; every exit updates `status.md` (state + run log + issue/branch fields), commits and pushes with `Refs #N`, and runs the lessons check.
  - `cpo-prd.md` (`cpo-prd <client-slug>`): preflight (intake `done`, else STOP; stale → confirm); deploy Ethan to draft `prd.md`; CPO (session) consistency pass against `requirements.md`; run the Codex `prd-review` gate — TWO automatic rounds, verdict read from the report file (never stdout, silence ≠ approval), digest upserted as an idempotent engagement-issue comment (`<!-- prd-review-round-N -->`); if round 2 is still `changes-requested`, the over-cap AskUserQuestion gate offers exactly: ONE user-authorized final delta round (round 3 is last — a round-3 `changes-requested` re-presents the gate WITHOUT this option), accept-with-noted-gaps, or needs-human label; update `status.md`, commit+push, lessons check.
  - `cpo-brief.md` (`cpo-brief <client-slug>`): preflight (PRD approved, else STOP); deploy Ethan (project brief, copy deck), Jonas (sitemap & flows, section-brief structure, wireframes), Yuki (brand inputs, visual guidance) — parallel where file-disjoint, Jonas→Yuki sequenced on `section-briefs.md`; Daniel reviews the package against the design-standard checklist (blocking findings routed back once); on approval set `handed-off`, record the PR URL in `status.md`, commit+push, open the engagement PR (`Closes #N`), lessons check.
- Command invocations above are written prefix-less: use the `naming-probe` winner (`/c-suite:cpo-<stage>` or `/cpo-<stage>`) verbatim in every user-facing mention.
- Every delegation brief passes the explicit `${CLAUDE_PROJECT_DIR}`-rooted paths of the skill templates the task needs (fallback channel if `skills:` preloading is unsupported: the persona Reads them first).
- Commands pick Codex model/effort per `.claude/rules/model-selection.md` at run time — never hardcoded. Deliverables stay professional prose; persona names sign reports only.

### 7. Memory hub update

- **Task ID:** memory-hub-update
- **Depends On:** c-suite-rules
- **Assigned To:** builder-hub
- **Agent Type:** general-purpose
- **Model / Effort:** `sonnet` / `low`
- **Parallel:** true
- **Satisfies:** AC10
- Add to `AGENTS.md`: a `products/` line in Project Structure (client engagements; fixture convention), and a c-suite section pointing to the three `.claude/rules/c-suite/` files and the `/c-suite:cpo-*` pipeline — one short block, per the memory-series contract (hub points, rules carry the content).

### 8. Resolution & invocation smoke check

- **Task ID:** resolution-smoke-check
- **Depends On:** stage-commands
- **Assigned To:** validator
- **Agent Type:** general-purpose
- **Model / Effort:** `sonnet` / `low`
- **Parallel:** false
- **Satisfies:** AC2
- Verify the three commands resolve under the probe-confirmed prefix via a headless `claude -p` listing; verify the knowledge skills do NOT auto-fire and ARE loadable by name; verify each persona agent's `skills:` preload takes effect (spot-check one persona sees its skill content). If `autoInvoke: false` is not honored in this Claude Code version, switch the three skills to the repo's proven `disable-model-invocation: true` (the recorded fallback) and note the deviation.

### 9. Dry-run engagement (Bluebird Bakery)

- **Task ID:** dry-run-engagement
- **Depends On:** stage-commands, resolution-smoke-check
- **Assigned To:** team lead (orchestrating session) with the user as the fictional client
- **Agent Type:** n/a — lead-run
- **Model / Effort:** session model / `high`
- **Parallel:** false
- **Satisfies:** AC3, AC11, AC13
- Run the full pipeline for the fictional client `_example-bluebird-bakery` (a bakery wanting a brochure website): one ASYNC intake round (scripted answers file exercises question-list generation + re-entrant ingestion), then LIVE grilling with the user playing the owner until requirements lock; `cpo-prd` through the Codex gate; `cpo-brief` to the full six-file package with Daniel's approval.
- Keep the finished engagement as the fixture; its wireframes must open offline (no external references).

### 10. Validate Everything

- **Task ID:** validate-all
- **Depends On:** c-suite-rules, knowledge-skills, persona-agents, prd-review-skill, naming-probe, stage-commands, memory-hub-update, resolution-smoke-check, dry-run-engagement
- **Assigned To:** validator
- **Agent Type:** general-purpose
- **Model / Effort:** `sonnet` / `medium`
- **Parallel:** false
- Run every command in acceptance-criteria.md → `## Validation Commands`.
- Verify each acceptance criterion is met.
