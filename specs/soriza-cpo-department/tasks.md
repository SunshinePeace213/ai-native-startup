# Tasks: Soriza design department — slice 1 (soriza-design)

> Execution plan for [spec.md](./spec.md). Owner and scope are defined there; this file is how & who.
>
> **Epic shape**: this plan executes as **five child pipeline runs** (one per issue #44–#48),
> not as one build on this branch. Each "task" below is a child pipeline launch: its scope, its
> build team with model/effort stamps (which the child's plan run transcribes into its own
> tasks.md), and the ready-made plan prompt. Task 1 lands this spec on `main` first.

## Implementation Phases

### Phase 1: Foundation

Land the epic planning docs on `main` (task 1), seed the design KB + worktree availability
(#44), then the department substrate — template, doctrine family, roster (#45).

### Phase 2: Core Implementation

The rungs: `/soriza-design:intake` with the DoR Stop gate (#46), then the four ladder rungs
brief → sitemap → wireframe → section-briefs (#47).

### Phase 3: Integration & Polish

The client git lane rule (#48, parallel with Phase 2 after #45), then epic validation:
all children closed by their PRs, validation commands green, ladder pilot-ready (task 7).

## Team Orchestration

- You operate as the team lead and orchestrate the team to execute the plan.
- IMPORTANT: You NEVER operate directly on the codebase. You use the `Task*` tools to deploy team
  members to build, validate, test, and deploy. Your job is to direct, not to build.
- Keep the shared task list (TaskCreate/TaskUpdate) as the single source of truth for who is doing
  what; verify each task on the board before marking it complete.
- Note the session id / name of each team member — that is how you reference them.
- **Epic-specific**: the "team members" of this epic are the child pipeline runs. Launch each
  child with its prompt from the task below (one `/harness-layer:harness-plan` run, then
  `/harness-layer:harness-build <child-slug>` when its spec approves, then review/ship). Within
  each child's build, the child's tasks.md deploys the builders stamped here.

## Team Members

- **Pipeline driver**
  - **Name:** epic-driver
  - **Role:** launches each child pipeline run in dependency order and tracks the epic board;
    this is Ringo or a lead session — never a code-writing builder.
  - **Agent Type:** n/a (pipeline commands; harness-plan/build run on their own frontmatter models)
  - **Resume:** true
- **kb-builder** — #44's single builder
  - **Role:** `.worktreeinclude` edit + `/harness-layer:kb add` runs (fetching fans out to
    `kb-fetcher` subagents per the kb command's own contract).
  - **Agent Type:** general-purpose · **Model / Effort:** `sonnet` / `low` (guarded mechanical flow)
  - **Resume:** true
- **doctrine-writer** — #45's content builder
  - **Role:** the six doctrine files + the nine-skeleton library + template skeletons — client-
    shaping copy, taste-critical.
  - **Agent Type:** general-purpose · **Model / Effort:** `opus` / `high` (user-facing taste ≥ 7)
  - **Resume:** true
- **structure-builder** — #45's scaffold builder
  - **Role:** `projects/_template/` folder shape, roster.md, AGENTS.md pointers.
  - **Agent Type:** general-purpose · **Model / Effort:** `sonnet` / `medium`
  - **Resume:** true
- **gate-builder** — #46's hook + tests builder
  - **Role:** `check_intake_readiness.py`, contract/wiring/doctrine-sync tests.
  - **Agent Type:** general-purpose · **Model / Effort:** `sonnet` / `medium` (strong precedent to copy)
  - **Resume:** true
- **rung-author** — #46's and #47's command author
  - **Role:** the five `/soriza-design:*` command files — persona voice, DoR gates, rung
    contracts; the department's operating surface.
  - **Agent Type:** general-purpose · **Model / Effort:** `opus` / `high` (harness-core prompts, taste-critical)
  - **Resume:** true
- **lane-writer** — #48's builder
  - **Role:** `git-lane.md` rule.
  - **Agent Type:** general-purpose · **Model / Effort:** `sonnet` / `medium`
  - **Resume:** true
- **validator** — every child's close-out + epic validation
  - **Role:** runs the child's / epic's validation commands and verifies ACs.
  - **Agent Type:** general-purpose · **Model / Effort:** `sonnet` / `low`
  - **Resume:** false

## Step by Step Tasks

- Execute every step in order, top to bottom. Each task maps directly to one `TaskCreate` call.
- Before starting, run `TaskCreate` for every task below so all team members can see the board.
- Each task names the acceptance criteria (from acceptance-criteria.md) it satisfies, so work traces to "done".

### 1. Land the epic planning docs on main

- **Task ID:** land-epic-spec
- **Depends On:** none
- **Assigned To:** epic-driver (Ringo merges)
- **Agent Type:** n/a
- **Model / Effort:** n/a — human review + merge
- **Parallel:** false
- **Satisfies:** AC1
- Review the draft `📝 docs(spec)` PR on `feat/43-soriza-cpo-department` (opened after the
  Codex gate; `Refs #43`) and merge it — children branch from `origin/main` and must see this
  spec folder there.
- Do not start any child before this merges.

### 2. Child #44 — seed design KB group + worktree availability

- **Task ID:** child-44-kb-seed
- **Depends On:** land-epic-spec
- **Assigned To:** epic-driver → kb-builder, validator
- **Agent Type:** general-purpose
- **Model / Effort:** `sonnet` / `low` (build); plan/build/review commands run on their own frontmatter models
- **Parallel:** false
- **Satisfies:** AC2, AC3
- **Memory:** record the worktree-include/WorktreeCreate-hook interplay as a dev-log lesson if
  it bites during the build.
- Scope: `.worktreeinclude` gains `ai-docs/*` (one-line comment above it); register via
  `/harness-layer:kb add <url> design` — W3C WCAG 2.2 quickref
  (`https://www.w3.org/WAI/WCAG22/quickref/`), web.dev Learn Design
  (`https://web.dev/learn/design`), NN/g homepage cornerstone (proposed:
  `https://www.nngroup.com/articles/top-10-guidelines-for-homepage-usability/`), NN/g
  writing-for-the-web (canonical article picked at build), Google Fonts Knowledge
  (`https://fonts.google.com/knowledge`); plus `add https://code.claude.com/docs/en/memory`
  (anthropic group). Fetch failures → substitute canonical page, record swap; never hand-author.
- Launch prompt for the child plan run:

  ```text
  /harness-layer:harness-plan "Child #44 of epic #43 (soriza-design slice 1). Scope: exactly
  task 2 of specs/soriza-cpo-department/tasks.md — .worktreeinclude ai-docs pattern + design/
  KB group (5 sources) + anthropic memory page. Transcribe decisions from
  specs/soriza-cpo-department/ (spec.md, decisions.md); ask nothing. Issue #44 already filed —
  skip issue creation; link the branch with: gh issue develop 44 --base main --name
  chore/44-soriza-design-kb-seed. Plan name: soriza-design-kb-seed. Builders: kb-builder
  (sonnet/low), validator (sonnet/low) per the epic tasks.md."
  ```

### 3. Child #45 — foundations: template, doctrine family, roster

- **Task ID:** child-45-foundations
- **Depends On:** child-44-kb-seed
- **Assigned To:** epic-driver → doctrine-writer, structure-builder, validator
- **Agent Type:** general-purpose
- **Model / Effort:** `opus` / `high` (doctrine + skeletons), `sonnet` / `medium` (scaffold/roster/AGENTS.md)
- **Parallel:** false (doctrine-writer and structure-builder run concurrently inside the child build; the child itself is sequential in the epic)
- **Satisfies:** AC4, AC5, AC6
- Scope: `projects/_template/` (intake.md, brief.md, sitemap-ia.md, asset-checklist.md,
  decision-log.md, wireframes/README.md, section-briefs/README.md + `_library/` with the nine
  skeletons, each carrying "One job" and "One desired action" fields);
  `.claude/rules/soriza-design/` six doctrine files + `lessons.md` (all
  `paths: ["projects/**/*"]`, real starter content drafted from the design KB);
  `.claude/rules/soriza/roster.md` (Vera, Mira, Elias, Ivo, Juno, Lior — name, position,
  deliverable owned, status); AGENTS.md pointers (+ `projects/` row in Project Structure).
- The `definition-of-ready.md` checklist headings authored here are the contract #46's hook
  hard-codes — write them as gate-able `##` sections for `intake.md`.
- Launch prompt:

  ```text
  /harness-layer:harness-plan "Child #45 of epic #43 (soriza-design slice 1). Scope: exactly
  task 3 of specs/soriza-cpo-department/tasks.md — projects/_template/ + nine-skeleton library,
  .claude/rules/soriza-design/ doctrine family (6 files + lessons.md), .claude/rules/soriza/
  roster.md, AGENTS.md pointers. Transcribe decisions from specs/soriza-cpo-department/; ask
  nothing. Issue #45 already filed — skip issue creation; link the branch with: gh issue
  develop 45 --base main --name feat/45-soriza-design-foundations. Plan name:
  soriza-design-foundations. Builders: doctrine-writer (opus/high), structure-builder
  (sonnet/medium), validator (sonnet/low) per the epic tasks.md."
  ```

### 4. Child #46 — intake rung + Definition-of-Ready stop gate

- **Task ID:** child-46-intake-gate
- **Depends On:** child-45-foundations
- **Assigned To:** epic-driver → rung-author, gate-builder, validator
- **Agent Type:** general-purpose
- **Model / Effort:** `opus` / `high` (intake command), `sonnet` / `medium` (hook + tests)
- **Parallel:** false
- **Satisfies:** AC7, AC8
- Scope: `.claude/commands/soriza-design/intake.md` (Mira; **first write** drops the
  session-scoped per-client marker
  `projects/<client>/.intake-in-progress.${CLAUDE_SESSION_ID}`; sweeps markers — any
  session — only from already-complete clients; idempotent scaffold from `_template` — never
  clobbers; interviews Ringo per `intake-standards.md`; writes `projects/<client>/intake.md`;
  commits per the git lane; Stop hook registered in frontmatter; carries a `## Rung Contract`
  block with labeled fields `Staffer:` / `Reads:` / `Writes:` / `First write:` /
  `DoR gate:` / `Refusal:` / `Commit:`); `.claude/hooks/check_intake_readiness.py` (matches
  stdin `session_id` against the marker suffix and gates **only its own session's markers** —
  blocks until every own-marked client's `intake.md` is complete, then removes only its own
  markers on exit 0; fails toward blocking; no own-session marker → block with a clear
  message; `_`-prefixed folders never valid; hard-coded DoR tuple matching
  `definition-of-ready.md`; exit-2 per-section diagnostics; fail-open only on malformed
  stdin/plumbing); a `.gitignore` line for `projects/*/.intake-in-progress.*`; tests under
  `tests/harness-layer/hooks/intake-readiness/` (block/allow/fail-open, wiring expectations,
  doctrine-sync test, session-independence regression — session A with complete client A
  exits 0 while session B's incomplete client-B marker exists, and session B still exits 2 —
  and the same-client two-session concurrent case, plus own-marker cleanup on exit 0);
  catalog row in `.claude/rules/harness-layer/hooks.md`.
- Launch prompt:

  ```text
  /harness-layer:harness-plan "Child #46 of epic #43 (soriza-design slice 1). Scope: exactly
  task 4 of specs/soriza-cpo-department/tasks.md — /soriza-design:intake command +
  check_intake_readiness.py Stop gate + tests + hooks.md catalog row. Transcribe decisions
  from specs/soriza-cpo-department/; ask nothing. Issue #46 already filed — skip issue
  creation; link the branch with: gh issue develop 46 --base main --name
  feat/46-soriza-design-intake-gate. Plan name: soriza-design-intake-gate. Builders:
  rung-author (opus/high), gate-builder (sonnet/medium), validator (sonnet/low) per the epic
  tasks.md."
  ```

### 5. Child #47 — the ladder: brief, sitemap, wireframe, section-briefs

- **Task ID:** child-47-ladder
- **Depends On:** child-46-intake-gate
- **Assigned To:** epic-driver → rung-author, validator
- **Agent Type:** general-purpose
- **Model / Effort:** `opus` / `high`
- **Parallel:** true (may run alongside child-48-git-lane)
- **Satisfies:** AC9, AC10
- **Memory:** after this child ships, append the "command-chain department" pattern lesson to
  the dev log (one line, cross-plan value).
- Scope: four commands under `.claude/commands/soriza-design/` — `brief.md` (Elias, reads
  intake.md, writes brief.md per brief-format.md), `sitemap.md` (Ivo, locks page + section
  inventory from the skeleton library into sitemap-ia.md), `wireframe.md` (Juno, one
  self-contained lo-fi grayscale HTML per screen in `wireframes/`, artifact publish
  best-effort — private to Ringo, with the client-delivery mode locked per engagement (org
  share / consented public link / the HTML file itself) and recorded in decision-log.md,
  copy-as-prompt reactions appended to decision-log.md), `section-briefs.md`
  (Lior, **reads `wireframes/`** — the approved layouts plus the change requests in
  decision-log.md — with `sitemap-ia.md` as the inventory source; inline loop over the locked
  inventory with parallel fan-out escape hatch, draft copy per copywriting.md,
  typography-direction page, packet assembly + Vera sign-off). Every rung: reads its actual
  predecessor's output, refuses on unmet DoR naming what's missing, commits per rung, and
  carries a `## Rung Contract` block whose fields the validation asserts clause by clause:
  `Staffer:` / `Reads:` / `Writes:`; `DoR gate:` naming the exact gated predecessor artifact
  (intake.md / brief.md / sitemap-ia.md / wireframes/); `Refusal:` stating refuse **and**
  naming that same missing artifact; `Commit:` stating all three of `📝 docs(<client>)`,
  `Refs #N`, and the engagement branch. Wireframe adds `Format:` (lo-fi grayscale,
  self-contained, no external dependencies, one page per screen), `Publish:` (best-effort +
  the three delivery modes recorded in decision-log.md), and `Reactions:` (copy-as-prompt
  reactions appended to decision-log.md as structured change requests). Section-briefs adds
  `Inventory:` (inline loop by default, parallel fan-out only for large inventories),
  `Copy:` (slogan/headline/body held to copywriting.md), `Packet:`, and `Sign-off:` Vera.
- Launch prompt:

  ```text
  /harness-layer:harness-plan "Child #47 of epic #43 (soriza-design slice 1). Scope: exactly
  task 5 of specs/soriza-cpo-department/tasks.md — the four ladder rungs
  /soriza-design:brief, :sitemap, :wireframe, :section-briefs. Transcribe decisions from
  specs/soriza-cpo-department/; ask nothing. Issue #47 already filed — skip issue creation;
  link the branch with: gh issue develop 47 --base main --name feat/47-soriza-design-ladder.
  Plan name: soriza-design-ladder. Builders: rung-author (opus/high), validator (sonnet/low)
  per the epic tasks.md."
  ```

### 6. Child #48 — client git lane rule

- **Task ID:** child-48-git-lane
- **Depends On:** child-45-foundations
- **Assigned To:** epic-driver → lane-writer, validator
- **Agent Type:** general-purpose
- **Model / Effort:** `sonnet` / `medium`
- **Parallel:** true (alongside child-46/child-47)
- **Satisfies:** AC11
- Scope: `.claude/rules/soriza-design/git-lane.md` (`paths: ["projects/**/*"]`): one issue per
  engagement; engagement branch `docs/<N>-<client>` via `gh issue develop`; engagement worktree
  named after the client; rung commits `📝 docs(<client>): … / Refs #N`; PRs at exactly two
  gate points, each stated as its own bullet pairing the gate name with its reference keyword
  on one line — one bullet for "brief approved" carrying `Refs #N` (and no `Closes`), one for
  "packet hand-off" carrying `Closes #N` — plus an explicit no-PR-per-deliverable clause; for
  `projects/**` PRs the DoR checklist + decision-log entry + client sign-off replace the docs
  template's Test Evidence block.
- Launch prompt:

  ```text
  /harness-layer:harness-plan "Child #48 of epic #43 (soriza-design slice 1). Scope: exactly
  task 6 of specs/soriza-cpo-department/tasks.md — the projects/** git-lane rule. Transcribe
  decisions from specs/soriza-cpo-department/; ask nothing. Issue #48 already filed — skip
  issue creation; link the branch with: gh issue develop 48 --base main --name
  chore/48-soriza-design-git-lane. Plan name: soriza-design-git-lane. Builders: lane-writer
  (sonnet/medium), validator (sonnet/low) per the epic tasks.md."
  ```

### 7. Validate Everything

- **Task ID:** validate-all
- **Depends On:** land-epic-spec, child-44-kb-seed, child-45-foundations, child-46-intake-gate, child-47-ladder, child-48-git-lane
- **Assigned To:** validator
- **Agent Type:** general-purpose
- **Model / Effort:** `sonnet` / `low`
- **Parallel:** false
- Run every command in acceptance-criteria.md → `## Validation Commands` on `main` after all
  child PRs merge.
- Verify each acceptance criterion is met; tick the child checkboxes on epic #43 and flip its
  Lifecycle line to **Done**; declare the ladder pilot-ready (the pilot itself is a new
  engagement issue, out of this epic's scope).
