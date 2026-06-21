# Dynamic Workflows: when a task wants its own harness

A *dynamic workflow* is the `Workflow` tool: Claude writes a JS orchestration script on the
fly (`agent()` / `parallel()` / `pipeline()`) that fans out subagents **deterministically**.
Saved ones live at `.claude/workflows/<name>.js`. The `Workflow` tool's own description is the
authoritative authoring guide and is always in context the moment you'd write one — this file
is about the **decision** (is a workflow the right shape, and which shape), not about
re-teaching `agent()`/`pipeline()`.

*Dynamic* is the operative word: a **static** workflow (a hand-written `claude -p` or Agent-SDK
harness) has to be generic enough for every input it will ever see, so it stays coarse; a
**dynamic** one is written fresh for the task in front of it, so it can be exactly as specific as
that task needs. That's the upgrade that makes the recognition catalog below worth acting on —
and it's why prompt-architect retired its own `claude -p` eval loop in favour of the two saved
workflows at the bottom of this file.

## The reframe — a workflow is an orchestration layer, not a 5th artifact type

`decision-tree.md` routes here when the core of the work is *orchestration* (fan-out,
multi-stage pipeline, verification panel, scale beyond one context). But a dynamic workflow is
**not** a sibling of skill/command/subagent on the "pick one" axis. It runs headless to
completion and returns a value — it is almost never the thing the user invokes. So a workflow
is normally **paired** with one of the other artifacts:

- a thin **skill fronts** a saved workflow (the user-facing trigger), or
- a skill **emits an ad-hoc workflow** at its own runtime ("a harness for every task").

"This should be a workflow" therefore answers a *different* question than "skill vs subagent" —
it's orthogonal. The build target is usually *a saved workflow plus a thin trigger skill*, not
"a workflow instead of a skill."

## Recognize a workflow-shaped build request

The bar below is stated in *mechanism* terms (deterministic fan-out, adversarial verification,
scale, loop-until-dry, multi-stage pipeline). But a user rarely speaks mechanism — they describe
a *job*. This catalog (the "harness for every task" article's use cases) is the bridge: when a
build request sounds like a row here, a workflow is a live candidate, and the shape is half-chosen
already. Most of these are even more valuable for **non-technical** work — sales post-mortems,
résumé ranking, tearing a business plan apart — than for code.

| Build request sounds like… | Shape it implies | Load-bearing signal that would justify it |
|---|---|---|
| "rename our `User` model to `Account` everywhere" / migrate a callsite class | discover sites → transform-per-site (worktree) → adversarially review → merge | scale beyond one context + per-item independence |
| "research <topic> across many sources and give me a cited report" | fan-out searches → fetch → verify each claim → synthesize (the `/deep-research` shape) | deterministic fan-out + adversarial verify |
| "verify every technical claim in this draft against the codebase" | extract claims → check each → verify the source's quality | deterministic fan-out + adversarial verify |
| "rank these 200 support tickets by severity" / sort N items by a qualitative measure | pairwise-comparison tournament, or bucket-rank in parallel then merge | scale beyond one context (comparative judgment beats absolute scoring) |
| "a reviewer that enforces our CLAUDE.md rules" / rules Claude keeps missing | one verifier agent per rule (+ a skeptic to cut false positives) | deterministic fan-out + independent perspectives |
| "figure out why <X> broke" / sales dropped / the pipeline failed | hypotheses from *disjoint* evidence (logs / files / data) → panel of verifiers & refuters | independent perspectives (the structural fix for self-preferential bias) |
| "a bot that triages our bug/support queue" | classify each → dedupe vs already-tracked → act, with a quarantine boundary | scale + loop-until-dry; pair with `/loop` to run continuously |
| "explore design/naming directions and pick the best" | generate many → score against a rubric, or tournament-select | independent perspectives + loop-until-rubric-met |
| "eval / refine this skill against a rubric" | with-artifact-vs-baseline per case → grade (prompt-architect's own Phase 5) | deterministic fan-out + adversarial verify |
| "route each task to the cheapest model that can do it" | a classifier agent that researches complexity, then routes Sonnet vs Opus | classify-and-act (often light enough to stay rung 1–2) |

**Quarantine** (the triage row) is a security pattern worth calling out: the agents that read
untrusted public content are barred from high-privilege actions; a separate acting agent does
those. Carry it into any triage/research workflow that ingests the open web.

Recognizing the shape is the **generative** half — surface the workflow option and its cost
rather than silently defaulting to inline. Whether the tool then *fires* is the conservative
bar's call (next section): plenty of catalog matches are small enough to stay inline at rung 1.
The two halves are separate decisions; don't let the bar's caution suppress the *offer*.

## The conservative bar — escalate from inline-spawn only when fan-out is load-bearing

Two defaults pull against reaching for a workflow, and both are correct:

- **4.8 spawns fewer subagents by default** (`4-8-principles.md §5`) — usually right; most work
  is better done inline than fanned out.
- **The `Workflow` tool must not fire without explicit user opt-in** — it can spawn dozens of
  agents on a large shared token budget. The opt-in exists because the cost is real.

So the bar is high. Escalate from "spawn a couple of subagents inline" to a dynamic workflow
**only when at least one signal below is a correctness requirement** — something the result is
wrong without, not a nice-to-have:

| Load-bearing signal | Why inline / prose fails it |
|---|---|
| **Deterministic fan-out** | "Must reliably spawn N" — a prose "spawn N subagents" instruction under-fires on 4.8 (the exact pain Phase 5 fixes); `agent()` calls execute every time |
| **Adversarial verification / independent perspectives** | Refute-panels and judge-panels need genuinely isolated contexts; one context grading its own work is not independent |
| **Scale beyond one context** | Audits, migrations, broad sweeps whose inputs would flood a single window |
| **Loop-until-dry / loop-until-budget** | Unknown-size discovery that keeps spawning until K dry rounds or a token target |
| **Multi-stage pipeline, per-item independence** | find→verify→synthesize over enough items that inline spawning is unreliable — a couple of stages over a couple of items is still inline work |

Those five signals are the decision face of why isolation and determinism matter; three failure
modes the "harness for every task" article names sit behind them, each one the bar guards against
— though deterministic fan-out and multi-stage independence earn the bar on their own, without a
named mode. **Agentic laziness** (the model declaring done at 35 of 50): decompose into focused
subagents so no single agent faces the whole slog, and loop until the work is actually dry.
**Self-preferential bias** (Claude favouring its own output when it judges it): verify in a
separate, independent context, not the one that produced the work. **Goal drift** (fidelity lost
across many turns and compactions): give each subtask a fresh context window so the original
constraints don't decay. If no load-bearing *signal* from the bar is in play, none of these is
either — inline is fine.

**Hold the line the other way too — do *not* use a workflow when:**

- it's a one-off you can just do now, or the work is linear with no real fan-out;
- the orchestration is conversational / interactive — a workflow runs headless to completion,
  so anything needing a human mid-run belongs in a skill (put the human gate at the boundary,
  the way the idea-stage skills stop at a founder-signature gate);
- each step needs the filesystem *during* orchestration — workflow scripts can't touch it
  (this is exactly why prompt-architect keeps `scripts/` outside its workflows);
- the only justification is "there's some parallelism." Parallelism alone is not the bar; a
  load-bearing signal is.

Whenever a skill launches a workflow — fronted *or* emitted ad hoc — make the fan-out **cost
legible** first: a trigger that silently launches a 30-agent run is a cost surprise. Name the
scale and get explicit opt-in.

## Which shape — picking the rung

Only Rung 1 is free. **Rungs 2–4 all fire the `Workflow` tool, so they require the load-bearing
bar AND explicit opt-in to be cleared *first*** — once you're past the bar, how much the
orchestration *shape varies* run-to-run only chooses *among* the workflow rungs (ad-hoc vs
saved); variability by itself never clears the bar. With that settled, pick the lowest rung that
meets the need:

1. **Inline spawn** — *the case where the bar was not met — including a signal that matched in kind but not at a scale where inline is unreliable.* The skill/subagent body says "spawn
   subagents in parallel when fanning out across independent items; do single-item work inline."
   Light, occasional fan-out. Honors §5; no workflow fires.
2. **Skill emits an ad-hoc workflow at runtime** — the skill body authors a `Workflow({script})`
   per task. Right when the orchestration *shape varies* run-to-run, so there's nothing stable to
   save ("a harness for every task"). This is the most *invisible* launch shape, so the emitting
   skill must still surface the fan-out scale and get explicit opt-in before the tool fires — the
   opt-in gate applies here too, not just to saved workflows.
3. **Thin skill fronts a saved workflow** — `.claude/workflows/<name>.js` holds stable, complex,
   reused orchestration; a dedicated thin skill is the trigger (`Workflow({name})`). The repo's
   `/artifact-eval` → `artifact-eval.js` is exactly this.
4. **Standalone saved workflow** — `.claude/workflows/<name>.js` invoked **by name as an internal
   step from another skill or workflow's body**, rather than fronted by its own dedicated trigger
   skill. prompt-architect's `artifact-eval` and `description-optimize` are this: prompt-architect
   calls them from its Phase 5/6 body via `Workflow({ name })`.

## House conventions for a saved workflow (the build-target case)

- **Placement:** `.claude/workflows/<name>.js` (project). Name it for the job, hyphen-case,
  matching the `meta.name` inside.
- **The `meta` block is required and must be a pure literal** — `name` + `description`, optional
  `phases` whose titles match the `phase()` calls. No variables, calls, or spreads in it.
- **Skill-fronts wiring:** the fronting skill stays thin — its body's job is to gather inputs,
  surface the fan-out cost (per the bar above), then call `Workflow({ name: '<name>', args })`.
  Keep the orchestration in the `.js`; keep judgment/interaction in the skill. `artifact-eval`'s
  SKILL.md is the model.
- **Gate at the boundary, not mid-run:** if a human decision is needed, return up to it and let
  the fronting skill handle it; don't try to pause a headless workflow.

## Shipping a workflow inside a skill (the distribution case)

When the build target is a *portable* skill that carries its own orchestration — not a workflow
checked into one repo's `.claude/workflows/` — the workflow `.js` travels inside the skill folder
(`<skill>/workflows/<name>.js`) and the SKILL.md points at it. This is prompt-architect's own
domain (it builds shareable artifacts), and the Workflow tool description doesn't cover it because
it's a *packaging* question, not an authoring one.

- **Reference it with `${CLAUDE_SKILL_DIR}`** so the path resolves wherever the skill installs:
  the body says `read ${CLAUDE_SKILL_DIR}/workflows/<name>.js`.
- **Ship it as a *template*, not a script to run verbatim.** A bundled workflow can't anticipate
  every caller's task the way a repo-local one can. So the SKILL.md should instruct Claude to
  read the `.js` as a *starting shape* — adapt the agent prompts, stages, and schemas to the task
  at hand, then run via `Workflow({script})` — rather than `Workflow({scriptPath})` it byte-for-byte.
  The bundled file is the skeleton; the live task fills the variables. (prompt-architect's own
  saved workflows are repo-local utilities called by name — the opposite case — so they're *not*
  the model for this; a distributed skill wants the template framing.)
- **Pair with `/loop` and `/goal` for the repeatable rows.** Triage, research, and verification
  workflows are the catalog rows that recur: a fronting skill can note that `/loop` runs the
  workflow on an interval (continuous triage) and `/goal` sets a hard completion gate
  ("don't stop until no new findings"). Mention this in the skill's user-facing notes; don't bake
  a fixed cadence into the workflow itself.

## Authoring — point at the spec and the live exemplars, don't duplicate

The `Workflow` tool description already covers `agent()`, `parallel()`, `pipeline()`, schemas,
resume, the budget object, and the quality patterns (adversarial verify, loop-until-dry,
multi-modal sweep, completeness critic). It's in context whenever you write a workflow — use it
as the reference rather than restating it here. The "harness for every task" article also names
some useful shapes — **classify-and-act**, **tournament**, and **generate-and-filter** — read it
for the details. They're shapes, not bar-clearers: a 3-attempt tournament or a
generate-and-filter over a couple of ideas is still inline (rung 1); reach for a workflow only on
a load-bearing instance at a scale where inline is unreliable. For shape, read the repo's own:

- `.claude/workflows/artifact-eval.js` — skill-fronted (`/artifact-eval`) and also called by name
  from prompt-architect's body: with-artifact-vs-baseline per item + a grader agent, schema-validated.
  The richest in-repo example.
- `.claude/workflows/description-optimize.js` — a compact utility called by name from prompt-architect's
  body. Compact pipeline shape.

Two article notes worth carrying into what you build:

- **`ultracode` forces a workflow.** When a user puts "ultracode" in a prompt, Claude Code builds a
  workflow rather than working inline (the Workflow tool's standing opt-in). It's the user's lever,
  not yours to assume — but a fronting skill's user-facing notes can mention it as the way to
  guarantee the orchestrated path.
- **Quick workflows are legitimate.** A workflow needn't be a 30-agent epic; "a quick adversarial
  review of one assumption" is a fine three-agent ad-hoc emit. The bar is about whether fan-out is
  *load-bearing*, not whether it's *large* — a small load-bearing instance still earns a workflow
  (often the cheapest rung that fires, rung 2), and a large-but-not-load-bearing one still doesn't.

## Validating a drafted workflow (lean — no eval pipeline)

A saved workflow is **not** put through the `meta-skill-grader` loop (that's for
skill/command/subagent artifacts). Validate it lightly:

- **Structural sanity:** the `meta` block satisfies the House-conventions rule above; `phases`
  titles line up with `phase()` calls; concurrent fan-out uses `parallel()`/`pipeline()` rather
  than a hand-rolled loop.
- **One real-input dry-run:** invoke it on the smallest realistic input, watch `/workflows`, and
  confirm it returns the expected shape. Use `resumeFromRunId` for cheap re-runs while iterating
  — an unchanged prefix replays from cache.

## Failure modes

The authoring failure modes live in the `Workflow` tool description (in context whenever you
write a workflow), not here — restating them is the Tip-1 duplication this file is built to
avoid: resume constraints, the `pipeline()`-vs-`parallel()`-barrier choice, loop-until-dry
dedup, and the shared `budget` object. The one constraint that shapes the *artifact boundary* —
workflow scripts can't touch the filesystem — sits in the do-not-use bar above; it's why file
I/O stays in the fronting skill or in kept scripts. Add real gotchas here the first time one
bites in practice.

## Cross-references

- ["A harness for every task" (Anthropic)](https://claude.com/blog/a-harness-for-every-task-dynamic-workflows-in-claude-code) — source for the three failure modes + the named patterns
- `decision-tree.md` — the orthogonal "is the core orchestration?" branch routes here
- `4-8-principles.md §5` — fewer subagents by default; this file is when to override that
- `../../../workflows/artifact-eval.js` — the skill-fronts-workflow + called-by-name exemplar
- `../../../workflows/description-optimize.js` — called-by-name internal-step exemplar
- the `Workflow` tool description — the authoritative authoring reference
