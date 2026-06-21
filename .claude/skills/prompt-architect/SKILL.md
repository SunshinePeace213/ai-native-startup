---
name: prompt-architect
disable-model-invocation: true
description: |
  Design, draft, test, and iterate on Claude Code skills, slash commands, and subagents end-to-end. Use for "build me a /commit command", "create a skill for X", "make a code-reviewer agent", "my skill isn't triggering", "test/optimize my skill", "rewrite this prompt for 4.8".
when_to_use: |
  Also fires when the build-an-artifact meta-intent is buried under a long excerpt or task spec (e.g. "develop a workflow for <domain task>"), to upgrade existing prompts to 4.8 best practices, and as the natural follow-up to /grill-me on artifact-building topics.
---

# Prompt Architect

A meta-skill for the full artifact lifecycle: design → draft → review → place → validate → trigger → ship. Covers skills (directory format, recommended), legacy single-file commands, and subagents. Forks `/skill-creator`'s executable apparatus and generalizes it for all three artifact types.

**Architectural reality:** Commands and skills have been merged. `.claude/commands/deploy.md` (single file) and `.claude/skills/deploy/SKILL.md` (directory) both create `/deploy` and use the **same frontmatter**. Directory format is recommended whenever bundled resources help.

## When this skill applies

- **"Build me a `/commit` command"** → skill (directory) or command (single-file) if trivial
- **"Write a skill that helps me draft SQL migrations"** → skill (directory)
- **"Make a `security-reviewer` subagent"** → subagent
- **"Help me design a code-review workflow"** → may be skill, subagent, or both
- **"Add hooks to this skill to enforce X"** → skill update with hooks frontmatter
- **"Rewrite this prompt for Opus 4.8"** → upgrade existing artifact (Phase 3 review)
- **"Test my skill with example prompts"** → run the validation loop (Phase 5)
- **"My skill isn't triggering when it should"** → run description optimization (Phase 6)
- **"What kind of skill is this — runbook? library reference?"** → use 9-category framework (Phase 1)

One-off tasks ("review this PR right now") are the wrong fit — just do the task. This skill is for building *reusable* artifacts.

## Entry paths

**Case 1 — post `/grill-me`:** User typed `/grill-me I want to create a skill for X`. `/grill-me` walked the design tree and reached shared understanding. Prompt-architect activates with grilled context in conversation; Phase 1 detects this and SKIPS its internal interview.

**Case 2 — cold trigger:** User typed something like "create a skill for X". Prompt-architect auto-triggers from the description; Phase 1 runs an INTERNAL grill-me-style interview (one question at a time, recommended answers, codebase-first) scoped to artifact-building decisions.

Both paths converge at Phase 2 (DRAFT) with the same shared understanding. See `references/composition-rules.md` for the chain.

## Workflow — 7 checkpoints (goals + constraints, not a rigid script)

Each checkpoint has a clear goal. The *how* is your judgment unless a script invocation is named.

### Phase 1 — DESIGN

**Goal:** Shared understanding of: intent + artifact type + Thariq category + persona need + hooks need + scope.

If conversation already contains a `/grill-me` transcript on this artifact-building topic, **skip this phase entirely** — the design contract is already established.

Otherwise, run an internal grill-me-style interview:

- One question at a time
- For each question, state your recommended answer with reasoning
- Walk down the decision tree resolving dependencies — intent first, then artifact type, then category, then persona, then hooks, then scope
- Explore the codebase before asking (filenames, conventions, existing patterns)

The 9-category framework in `references/skill-categories.md` is the first reference to consult — the category answer drives most downstream decisions (auto-trigger vs user-invoked, hooks helpfulness, state needs, bundled resources).

Decision rules at a glance:

- **Artifact type** — see `references/decision-tree.md`. Skill (directory) is the default; subagent for context isolation / tool restrictions / memory; command (single-file) only for genuinely trivial cases.
- **Dynamic workflow** — when the work smells like *orchestration* (deterministic fan-out, multi-stage pipeline, adversarial verification, scale beyond one context, loop-until-dry), see `references/dynamic-workflows.md`. It's an orthogonal layer usually fronted by a thin skill, not a fifth artifact type. Two separate decisions: **recognizing** a workflow-shaped build request (migration, triage, ranking/sorting, deep research/verification, rule-checking, root-cause — see the recognition catalog) and surfacing the option with its cost is the *default*; the high bar (fan-out must be load-bearing) governs only whether the tool *fires*, not whether you raise it. Don't let the caution suppress the offer.
- **Persona** — invoke `tech-company-personas` only when artifact quality depends on judgment (review/recommendation/voice) AND domain is tech-flavored. See `references/composition-rules.md`.
- **Hooks** — see `references/hooks.md`. Add hooks when 3+ of these are yes: hard requirement independent of model behavior, verification against actual state needed, tool calls that must never happen, ships to others where you can't trust manual enforcement.

If the work cleanly spans multiple categories, **consider splitting into composable skills** rather than one mega-skill.

### Phase 2 — DRAFT

**Goal:** Artifact draft conforming to the right template, with Thariq's 9 tips applied throughout.

Read the relevant template and the canonical Thariq source:

| Artifact type | Template |
|---|---|
| Skill (directory) | `references/skill-template.md` |
| Command (single-file legacy) | `references/command-template.md` |
| Subagent | `references/subagent-template.md` |
| Combination | All relevant templates + `references/composition-rules.md` |

Every draft: also read `references/thariq-principles.md`. The 9 tips at a glance:

1. Don't state the obvious — if a paragraph could be deleted with no output change, delete it
2. Build a Gotchas section — high-signal items not in public docs
3. Use the file system for progressive disclosure — split long content into `references/<topic>.md`
4. Don't railroad — goal + constraints, not a rigid script
5. Think through setup — `config.json` for per-installation context
6. Write the description for the model — name specific user phrasings; be slightly emphatic
7. Use `${CLAUDE_PLUGIN_DATA}` for persistent state
8. Bundle scripts for operations Claude would otherwise re-derive every invocation
9. On-demand hooks for opinionated enforcement scoped to the artifact

**4.8 baseline** (full detail in `references/4-8-principles.md` — read it for any non-trivial draft, not just upgrades): the model is more literal, uses tools and subagents more conservatively, and updates the user well on its own. The single biggest shift is that **`effort` is the dominant lever** — reach for it before "think harder" prose. For subagents, set `effort` deliberately in frontmatter (`xhigh` for hard coding/agentic, `high` for reasoning-sensitive). Don't add progress-update scaffolding or reasoning-permission phrases; they're no-ops or worse.

**Persona substitution:** if Phase 1 decided a persona is warranted and the domain is tech-flavored, invoke `tech-company-personas` (actual skill call) with `task=` and `domain=`. Paste the returned persona text verbatim into the artifact. Never leave a `[Invoke tech-company-personas]` placeholder.

**Concrete reference examples** sit at `assets/examples/`:

- `assets/examples/skill-example-format-error/` — realistic skill in directory format
- `assets/examples/command-example-commit-readme.md` — realistic single-file command
- `assets/examples/subagent-example-security-reviewer.md` — realistic subagent with persona, memory, and a read-only-enforcing hook
- `assets/examples/commit-command-before-after.md` — old-style → 4.8-tuned conversion

Each example has a header comment naming the Thariq tips it demonstrates. Read at least one of them during drafting to anchor voice and shape.

### Phase 3 — REVIEW

**Goal:** Draft passes anti-patterns gate + smoke-test checklist before validation.

Read `references/anti-patterns.md` and run the full checklist against the draft. This is a hard filter — every check must pass. The checklist covers:

- Older-model holdovers (`$100 tip`, capital-letter MUSTs without *why*, reasoning-permission phrases, inflated persona specifics, over-triggering tool guidance, vague stakes, unspecified output length, deeply nested headings, frontend defaults, forced progress-update cadence, "think harder" prose in place of `effort`)
- Thariq-derived patterns (stating the obvious, railroading, generic descriptions)
- Positive checks (Gotchas section if production history; bundled-script opportunities; `${CLAUDE_PLUGIN_DATA}` for state; `config.json` for per-install setup)

Also read `references/4-8-principles.md` if upgrading an existing pre-4.8 artifact — the per-implication notes guide what to change.

If the user explicitly asks for a refused pattern, explain the cost once and only comply if they confirm. Default to refusing.

**Smoke-test checklist** before moving on:

- [ ] Artifact type matches the work
- [ ] Thariq category is identified
- [ ] Frontmatter complete — needed fields present, none unused
- [ ] No anti-patterns
- [ ] Description written for the model (Tip 6) — names user phrasings
- [ ] Nothing states the obvious (Tip 1)
- [ ] Workflow gives goal + constraints (Tip 4)
- [ ] Persona substitution complete (no placeholders left)
- [ ] Hooks decision documented (added with rationale, or rationale for skipping)
- [ ] If the build request is workflow-shaped (recognition-catalog match: migration / triage / ranking / deep research / verification / rule-checking / root-cause), the dynamic-workflow option was surfaced with its cost — not silently defaulted to inline (`references/dynamic-workflows.md`)
- [ ] Scope explicit (what's in, what's out)
- [ ] Output specification concrete (length, format, structure)
- [ ] `description` field under 300 chars (keyword-dense, front-loaded triggers) and `description` + `when_to_use` within the 1,536-char hard cap — the listing eats shared per-session budget (Tip 6; see `references/skill-template.md` → "Description budget")
- [ ] `when_to_use` adds only the gate + NOT-boundaries — it does NOT repeat trigger phrases already in `description` (omit the field if it would just echo)
- [ ] Reasoning depth set via `effort` (subagents carry it; no "think harder" prose forcing it); no forced progress-update cadence (4.8)

### Phase 4 — PLACE

**Goal:** Artifact at correct path; sibling workspace initialized.

| Artifact | Path |
|---|---|
| Skill (directory), project | `.claude/skills/<name>/SKILL.md` |
| Skill (directory), user-level | `~/.claude/skills/<name>/SKILL.md` |
| Command (single-file), project | `.claude/commands/<name>.md` |
| Command (single-file), user-level | `~/.claude/commands/<name>.md` |
| Subagent, project | `.claude/agents/<name>.md` |
| Subagent, user-level | `~/.claude/agents/<name>.md` |

Skill takes precedence over a same-named command — adding `.claude/skills/<name>/SKILL.md` is a non-breaking upgrade.

Ask the user about project vs user scope if it isn't obvious. Project scope is the default for team-shared artifacts; user scope for personal workflows.

**Initialize the sibling workspace:**

```
<artifact-parent>/<name>-workspace/
└── evals/
    └── evals.json   ← created in Phase 5 from drafted test prompts
```

The workspace pattern is uniform across all three artifact types (skills, commands, subagents). Iteration results land in `<name>-workspace/iteration-N/eval-<descriptive-name>/`.

### Phase 5 — VALIDATE

**Goal:** Artifact tested against realistic prompts; iterated until satisfied.

This is the executable eval loop, run as a **dynamic workflow** so spawning is deterministic. Read `references/schemas.md` for the JSON shapes used by the scripts and `meta-skill-grader`.

#### Step 1 — Draft realistic test prompts

2-3 prompts that mirror what a real user would actually type. Confirm with the user before running.

For skills/commands (auto-discoverable), the prompts should cover both the canonical use case AND a near-miss case (something where the artifact *might* or *might not* fire — useful for tuning the description later).

For subagents (user-invoked), the prompts go via direct delegation; near-miss testing isn't meaningful.

Save to `<name>-workspace/evals/evals.json` following the schema in `references/schemas.md`. Skip writing assertions yet — draft them in Step 2 while runs are in progress.

#### Step 2 — Draft assertions, then run the `artifact-eval` workflow

Write quantitative assertions for objectively verifiable outputs (file transforms, code generation, data extraction); skip them for subjective artifacts (writing style, design) — those get qualitative review only. Give each eval a descriptive `name`.

Then run the eval as a **dynamic workflow** rather than spawning subagents in prose. On 4.8 a prose "spawn N subagents" instruction under-fires (the model spawns fewer subagents by default — `4-8-principles.md §5`), whereas a workflow's `agent()` calls execute deterministically — this is the fix for "my new artifact never spawns anything". Invoke the bundled workflow:

```
Workflow({ name: 'artifact-eval', args: {
  artifactPath, artifactType, artifactName,
  iterationDir: '<workspace>/iteration-<N>',
  graderRubricPath: '<this-skill-dir>/agents/meta-skill-grader.md',
  evals: [{ name, prompt, assertions, files }]
}})
```

It runs with-artifact + baseline per eval in parallel, then spawns `meta-skill-grader` to score each run against its assertions (writing `grading.json` per run), and returns per-eval pass-rate deltas. For a **subagent** artifact the with-run worker *is* the subagent (spawned via its `agentType`); for a **skill/command** the worker is told to use it by name. If you want timing in the benchmark, save `total_tokens`/`duration_ms` from the task notification into `timing.json` per run dir.

**Fallback (workflows disabled — claude.ai, or `disableWorkflows`):** run the evals sequentially yourself — for each, execute with-artifact and baseline, then spawn `meta-skill-grader` via the Agent tool (or grade inline by following `agents/meta-skill-grader.md`). Same outputs; only the orchestration differs.

#### Step 3 — Aggregate and review

Grading is done inside the workflow. Aggregate and open the viewer with the kept compute scripts (these need the filesystem, which workflows can't touch — hence the split):

```bash
python3 -m scripts.aggregate_benchmark <workspace>/iteration-N \
  --artifact-type <skill|command|subagent> --artifact-name <name>

nohup python3 eval-viewer/generate_review.py <workspace>/iteration-N \
  --skill-name <name> --benchmark <workspace>/iteration-N/benchmark.json \
  > /dev/null 2>&1 &
```

For iteration 2+, also pass `--previous-workspace <workspace>/iteration-<N-1>`. Tell the user: *"Two tabs in the viewer — 'Outputs' for per-test feedback, 'Benchmark' for the quantitative comparison. Submit reviews when done."*

#### Step 4 — Iterate based on feedback

Read `feedback.json`. Improve the artifact applying these principles (all proven from `/skill-creator`'s loop):

1. **Generalize from the feedback** — don't overfit to the 2-3 test cases; find the underlying principle
2. **Keep the artifact lean** — read transcripts not just outputs; cut what's not pulling weight
3. **Explain the why** — replace MUSTs with reasons; the model is smart and benefits from understanding
4. **Look for repeated work across test cases** — if all runs independently wrote the same helper script, bundle it (Tip 8)
5. **Don't add rigid structure to compensate for ambiguity** — fix the ambiguity

Bump iteration number, re-run. Stop when user is satisfied, all feedback is empty, or progress is diminishing (usually by iteration 3). If iterations aren't landing, **step back and reconsider Phase 1** — the artifact may be the wrong type or scope.

### Phase 6 — TRIGGER (auto-trigger artifacts only)

**Goal:** Description optimized for reliable triggering. Only meaningful for skills and commands (both auto-discoverable). **Skip for subagents** — they're user-invoked, so triggering accuracy isn't a thing.

When to offer this:

- Artifact auto-triggers (not `disable-model-invocation: true`)
- Artifact will be invoked across varied phrasings
- Phase 5 surfaced cases where the artifact *should* have triggered but didn't

#### Step 1 — Generate 20 eval queries

8-10 should-trigger + 8-10 should-not-trigger (near-misses, not trivially irrelevant). Realistic substantive queries with backstory, file paths, real context. Save as JSON:

```json
[
  {"query": "the user prompt", "should_trigger": true},
  {"query": "another prompt", "should_trigger": false}
]
```

Bad: `"Format this data"`. Good: `"my boss sent me a Q4 sales xlsx and wants a profit margin column — revenue is column C, costs column D"`. Negative cases should be tricky near-misses, not trivially irrelevant ones.

#### Step 2 — Review eval set with user via the HTML template

Read `assets/eval_review.html`. Replace placeholders:
- `__EVAL_DATA_PLACEHOLDER__` → JSON array of eval items (no quotes — it's a JS assignment)
- `__SKILL_NAME_PLACEHOLDER__` → artifact name
- `__SKILL_DESCRIPTION_PLACEHOLDER__` → current description

Write to `/tmp/eval_review_<name>.html` and `open` it. User edits queries, toggles should-trigger, exports as `eval_set.json`.

#### Step 3 — Run the `description-optimize` workflow

Run the bundled workflow — it replaces the retired `claude -p` loop (no separate CLI billing; it uses your in-session token budget, and you can route to a cheaper model via `/model`):

```
Workflow({ name: 'description-optimize', args: {
  artifactName, artifactType,            // 'skill' | 'command'
  currentDescription: '<current description>',
  queries: [{ query, should_trigger }],  // the 20 from Step 2
  maxIterations: 4, runsPerQuery: 3
}})
```

It splits 60% train / 40% held-out test, scores the current description by majority vote across `runsPerQuery` judgments per query, proposes improvements, and returns `best_description` selected by **held-out test** score (avoiding overfit). Watch it in `/workflows`.

#### Step 4 — Apply

Update the artifact's frontmatter with `best_description`. Show user before/after and report scores.

### Phase 7 — SHIP

**Goal:** Report deliverable; package if applicable.

Tell the user:

- Where the artifact lives
- What test cases were validated and outcomes
- Whether description optimization ran, with before/after if so
- Any opt-outs the user took
- If the artifact bundles a workflow `.js` for distribution, note it ships as a *template to adapt*, not a verbatim script, and that `/loop` + `/goal` pair well with it for the repeatable rows (`references/dynamic-workflows.md` → "Shipping a workflow inside a skill")
- Follow-ups worth considering (e.g., "no Gotchas section yet — add one the first time something bites")

**Optional packaging (skill-only, if `present_files` tool available):**

```bash
python3 -m scripts.package_skill <path-to-skill>
```

Produces a `.skill` file. Skip for commands and subagents — they don't get packaged.

## Bundled apparatus

Forked from `/skill-creator` (commit `690f15cac7f7b4c055c5ab109c79ed9259934081`) and parameterized for all three artifact types; Phases 5–6 have since diverged to native **dynamic workflows** (replacing the `claude -p` subprocess loop). See `references/upstream-sync.md` for the sync record.

### Workflows (`.claude/workflows/`)

- `artifact-eval` — runs the artifact vs baseline across evals, grades each run with `meta-skill-grader`, returns pass-rate deltas (Phase 5). Deterministic spawning — replaces the prose "spawn subagents" instruction that 4.8 under-fires.
- `description-optimize` — train/test trigger-optimization loop for skills/commands (Phase 6). Replaces the retired `claude -p` apparatus; uses the in-session token budget, not separate CLI billing.

### Scripts (`scripts/`) — pure compute, kept

- `aggregate_benchmark.py` — aggregates iteration runs into benchmark.json + benchmark.md
- `quick_validate.py` — frontmatter validation for skill / command / subagent
- `package_skill.py` — `.skill` packaging (skill-only)
- `utils.py` — shared utilities (artifact path resolution, frontmatter parsing)

Invocation: `python3 -m scripts.<name> ...` (or `uv run python -m scripts.<name> ...`) from the prompt-architect directory. These need the filesystem; workflows can't touch it, so the split is deliberate.

**Retired** (2026-06-03): `run_eval.py`, `run_loop.py`, `improve_description.py`, `generate_report.py` — the `claude -p` subprocess apparatus, replaced by the two workflows above.

### Eval agents (`agents/`) — bundled, spawned by the workflows

- `meta-skill-grader.md` — grades a run's outputs against its assertions + critiques the assertions (Phase 5)
- `meta-skill-comparator.md` — blind A/B comparison between artifact versions (improve path)
- `meta-skill-analyzer.md` — post-hoc "why did A beat B" + benchmark pattern surfacing (improve path)

Upgraded to the subagent standard (least-privilege tools, deliberate `effort`, the `subagent-template.md` body skeleton). Kept bundled — the workflows spawn them by reading these files, so they need no `.claude/agents/` registration.

### Eval viewer (`eval-viewer/`)

- `generate_review.py` — HTML reviewer with Outputs + Benchmark tabs; supports `--static` for headless environments
- `viewer.html` — viewer template

### Assets

- `assets/eval_review.html` — description-optimization eval set review UI
- `assets/examples/` — 4 illustrative-but-functional examples (skill, command, subagent, before/after)

### Setup

The kept scripts run on the Python 3 standard library — **no install is needed to validate or test artifacts**. Phases 5–6 now run as **dynamic workflows** (no `claude -p` subprocess), which require Claude Code v2.1.154+ with dynamic workflows enabled in `/config` (research preview). The kept compute scripts (`aggregate_benchmark`, `quick_validate`, `package_skill`) are pure stdlib and shell out to nothing.

Run any script with [uv](https://docs.astral.sh/uv/) — no manual venv:

```bash
cd .claude/skills/prompt-architect
uv run python -m scripts.quick_validate <artifact-path> --artifact-type subagent
```

Optional: `PyYAML` hardens frontmatter parsing (the validator falls back to a stdlib parser without it). It's listed, commented, in the project-root `requirements.txt`:

```bash
uv run --with pyyaml python -m scripts.quick_validate <artifact-path>
```

## Environment adaptations

| Environment | Adaptations |
|---|---|
| **Claude Code (workflows enabled)** | Run Phases 5–6 as the `artifact-eval` / `description-optimize` workflows — deterministic spawning; watch via `/workflows` |
| **Workflows disabled / Claude.ai** | Fallback: run evals sequentially; spawn `meta-skill-grader` via the Agent tool (or grade inline per its rubric); outputs to the workspace / `/mnt/user-data/outputs/`; inline review |
| **Cowork (subagents, no display)** | Workflows or sequential; `generate_review.py --static <path>` for HTML; feedback downloads as `feedback.json` |

The loop is the same — only the mechanics of running and reviewing change.

## Composition with other skills

- **`/grill-me`** — the on-ramp. Walks the design tree; suggests prompt-architect at the end for artifact-building topics.
- **`tech-company-personas`** — call in Phase 2 when persona is warranted (tech-flavored, judgment-driven).
- **`frontend-design`** — if the drafted artifact involves frontend output, *the artifact* references it at runtime (not prompt-architect during drafting).
- **Other domain skills** (`pdf-reading`, `docx`, etc.) — drafted artifact references them at runtime; don't duplicate logic.

Full composition guidance: `references/composition-rules.md`.

## What this skill is NOT

- Not a code generator — produces prompt artifacts, not application code
- Not a wrapper around `/skill-creator` — the apparatus is forked and self-contained
- Not a way to bypass user preferences — if they want their old template patterns back, explain the tradeoffs once and comply

## Reference files

### Design & drafting
- `references/4-8-principles.md` — what changed in 4.8 affecting artifact design (effort as the dominant lever, thinking off by default, etc.)
- `references/thariq-principles.md` — **canonical source** for Thariq's 9 tips
- `references/skill-categories.md` — Thariq's 9-category framework
- `references/anti-patterns.md` — older-model patterns to refuse + Thariq-derived patterns + review checklist
- `references/decision-tree.md` — skill vs command vs subagent vs combination
- `references/dynamic-workflows.md` — when a task wants a dynamic workflow (the conservative bar, the shape ladder, house conventions); orthogonal to the type choice
- `references/skill-template.md` — skill (directory) anatomy + frontmatter + Gotchas pattern
- `references/command-template.md` — command (single-file) for trivial cases
- `references/subagent-template.md` — subagent YAML + body + 5 common shapes
- `references/hooks.md` — when and how to add hooks for deterministic verification
- `references/composition-rules.md` — when to call tech-company-personas, /grill-me chain, runtime references

### Validation apparatus (forked from /skill-creator)
- `references/schemas.md` — JSON shapes for evals.json, grading.json, benchmark.json, feedback.json
- `references/upstream-sync.md` — skill-creator fork SHA + what was modified post-fork

### Examples (for voice and shape)
- `assets/examples/skill-example-format-error/` — realistic skill
- `assets/examples/command-example-commit-readme.md` — realistic command
- `assets/examples/subagent-example-security-reviewer.md` — realistic subagent
- `assets/examples/commit-command-before-after.md` — old-style → 4.8 conversion
