# meta-agent — Comprehensive Evaluation Report

**Date:** 2026-06-23
**Subject:** `.claude/skills/meta-agent/` — the team's standard + workflow for authoring Claude Code subagents
**Verdict:** ✅ **Ship-ready.** The skill is structurally sound, triggers with perfect precision, and produces measurably better subagents than an unaided baseline (+31 points). One actionable recall gap and two minor polish items below.

---

## 1. What was evaluated & how

`meta-agent` is a *skill that authors subagents*, so it was evaluated on the two axes its
sibling `meta-skill` established, plus a structural self-conformance pass:

| Layer | Question | Method |
|---|---|---|
| **1 — Static / self-conformance** | Does the skill pass its own standard? | Deterministic `validate_agent.py` self-tests + budget/structure checks |
| **2 — Triggering** | Does it fire on subagent-authoring, and *not* on skill/command/unrelated work? | Real `claude -p` routing probe over 22 labeled queries (sonnet, 2 runs each), with `meta-skill`/`meta-commands` present as genuine competition |
| **3 — Output quality** | Does *using* the skill produce better subagents than no skill? | 4 realistic prompts built **with-skill vs. baseline** (sonnet both), graded against pre-registered assertions |

A durable **regression suite** was authored and now lives with the skill:
`.claude/skills/meta-agent/evals/{trigger-eval.json, evals.json, inputs/}`. Re-run it on every edit.

---

## 2. Layer 1 — Static / self-conformance: **PASS (clean)**

| Check | Result |
|---|---|
| `SKILL.md` frontmatter parses; `name: meta-agent` | ✅ |
| `description` 583 chars (≤1024), no `<`/`>` | ✅ |
| `description` + `when_to_use` = 911 chars (≤1536) | ✅ |
| Body 159 lines (<500 target) | ✅ |
| References exactly one level deep (4 files) | ✅ |
| No heavy apparatus (eval-viewer/agents/benchmark/package) | ✅ |
| Validator PASSes a valid agent (exit 0) | ✅ |
| Validator catches malformed agent — bad name, empty desc, bad model, bad effort (exit 1) | ✅ |
| Validator rejects fenced ```` ```yaml ```` frontmatter | ✅ |
| The skill's **own worked example** (in `body-structure.md`) validates | ✅ |

The skill practices what it preaches: lean body, progressive disclosure, a working gate.

---

## 3. Layer 2 — Triggering: **86% accuracy — perfect precision, 0.70 recall**

Real routing behavior of the *installed* skill (not a description in isolation):

| Metric | Value | Reading |
|---|---|---|
| Accuracy | 19/22 (86%) | Good |
| **Precision** | **1.00** | Never fires when it shouldn't — the safest failure mode |
| **Specificity** | **1.00** (12/12) | Every should-not query correctly held |
| Recall | 0.70 (7/10) | 3 should-trigger queries answered directly instead of routing |

**Boundary discrimination is excellent.** With `meta-skill` and `meta-commands` both live:
- "Create a skill that formats API errors" → `meta-skill` ✅
- "Make a slash command for commit & push" → `meta-commands` ✅
- "**My skill** isn't triggering, fix its description" → `meta-skill` ✅ (the deliberate near-miss negative — it did **not** confuse "skill" with "agent")
- "Run the test suite and tell me what's failing" → no route ✅ (correctly distinguishes *using* an agent from *authoring* one)

**The 3 misses share one pattern — fix/advise on an *existing* agent:**
1. "Fix the frontmatter on `.claude/agents/db-reader.md` — the tools and effort look wrong"
2. "What effort and model should I set for a code-review agent in its frontmatter?"
3. "Should my researcher subagent get the Write tool, or keep it read-only?"

All three are small-edit or quick-advice intents the model judged it could handle directly.
The `description` *does* list "update or fix an agent's frontmatter, tools, or model," but that
clause is out-weighed by the front-loaded "create a new subagent" framing and by the model's
confidence that a one-line fix or a config question needs no skill.

> **Calibration call, not a pure defect.** Because precision is 1.00 and all misses are
> low-stakes ("just do the small thing"), 0.70 recall may be acceptable. If you want the skill
> to own *edit/debug/advisory* requests too, see Recommendation R1.

---

## 4. Layer 3 — Output quality: **96% with skill vs 65% baseline (+31 points)**

Each prompt was built twice (same model, same prompt) — once told to read & follow the skill,
once on the model's own knowledge. Graded against pre-registered assertions.

| Eval | With skill | Baseline | What the skill added |
|---|---|---|---|
| 1 — read-only diff reviewer | **7/7** | 5/7 | NOT-boundary **in the description**; full scoped read kit |
| 2 — proactive test runner | **6/6** | 4/6 | `effort` set; "use proactively" |
| 3 — read-only researcher | **5/6** | 3/6 | `effort: high`; "use proactively" + NOT-boundary |
| 4 — fix a broken agent | **7/7** | 5/7 | `effort`; trigger-rich description rewrite |
| **Total** | **25/26 (96%)** | **17/26 (65%)** | **+8 assertions** |

**Where the lift comes from (the skill's signature levers):**
- **`effort` in frontmatter:** with-skill **4/4**, baseline **1/4**. The skill's central Opus-4.8 claim — "effort is the dominant capability lever, and a subagent is the one artifact where you set it" — is exactly what the baseline forgets.
- **`use proactively`:** with-skill **4/4**, baseline **1/4**. Drives auto-delegation; baselines omit it.
- **NOT-boundary in the *description*:** with-skill **4/4**, baseline **2/4**. eval-1 is the clearest case — the baseline wrote a NOT-boundary in the *body* (where the router never reads it) while the skill version put it in the `description` (where it actually steers routing).
- **Least-privilege tools:** eval-1 baseline granted `tools: Bash` only — broad shell access, no scoped `Read/Grep/Glob`; the skill version produced the cleaner `Read, Grep, Glob, Bash`.

**Both configs cleared the floor:** 8/8 validator PASS, and *both* correctly unfenced the broken
agent's frontmatter in eval-4 and stripped the persona / "think harder" / forced-cadence
anti-patterns. Modern Claude already knows subagent basics; the skill's value is the **higher-order
discipline** (effort, proactive routing, boundary placement, tool scoping) it applies *consistently*.

**Cost of the lift:** ~2× tokens (~30.2k vs ~15.5k) and ~1.85× wall time (~64s vs ~35s), because
the skill agent reads references and runs the validator. For a one-time authoring task that yields
a durable, reusable agent file, that trade is clearly worth it.

**One with-skill miss (honest):** eval-3 asked for an agent that "must never modify files," yet
*both* the skill and baseline versions included `Bash` (a latent mutation path). The skill's own
reference (shape #1: read-only researcher = `Read, Grep, Glob`, **no Bash**) prescribes the ideal,
but the agent still reflexively added Bash. See Recommendation R2.

---

## 5. Key findings

1. **The skill works and earns its place.** +31-point quality lift over an equally-capable
   baseline, concentrated in the exact disciplines it teaches (effort, proactive routing, boundary
   placement, least-privilege tools).
2. **Triggering is safe by construction.** Precision and specificity are 1.00 — it never hijacks
   skill-authoring, command-authoring, or plain coding requests. The `meta-skill`/`meta-commands`
   boundary holds even on adversarial near-misses.
3. **Recall gap on "edit/advise an existing agent."** The one real triggering weakness; all 3
   misses are fix-frontmatter / config-question intents (R1).
4. **"NOT-boundary in the description, not the body" is the skill's highest-value, least-obvious
   teaching** — baselines reliably misplace it, breaking routing they think they've set up.
5. **The skill is self-consistent** — it passes its own validator and its documented example is valid.
6. **Measurement caveat surfaced:** the repo's `run_eval.py` returned a degenerate all-zero result
   because it keys on a temp-command name while the *real* `meta-agent` skill is installed; the
   model routes to the real skill, which that harness can't see. The direct `claude -p` routing
   probe (`evals/meta-agent/triggering/routing_probe.py`) is the valid measurement for an
   already-installed skill.

---

## 6. Recommendations (prioritized)

- **R1 — Decide the recall calibration (highest leverage).** If the skill should own edit/debug/
  advisory requests, front-load those intents in the `description` rather than burying them after
  the "create" phrasings — e.g. lead a sentence with *"Also use for any change or question about an
  existing agent file: fixing frontmatter, choosing tools/model/effort, or why an agent won't
  delegate."* Then re-run `trigger-eval.json` and confirm recall rises without denting precision.
  If you'd rather the model keep handling trivial one-line fixes itself, document 0.70 recall as
  intended and move on.
- **R2 — Sharpen the read-only-researcher tool guidance.** Both eval-3 agents added `Bash` to an
  agent that "must never modify files." Add one explicit line to `body-structure.md` shape #1 /
  `anti-patterns.md`: *"A pure researcher needs no Bash — `Grep`/`Glob` cover search; `Bash` re-opens
  a mutation path."* This closes the only with-skill quality miss.
- **R3 — Keep the regression suite.** `evals/{trigger-eval.json, evals.json}` are now committed with
  the skill. Re-run both on every edit; treat any precision regression (a new false fire) as a release blocker.
- **R4 — (Optional) Note the harness caveat.** Add a line to the skill's test step that for an
  *installed* skill, triggering must be measured by real routing (the probe here), not `run_eval.py`'s
  temp-command method.

---

## 7. Artifacts

| Path | What |
|---|---|
| `.claude/skills/meta-agent/evals/trigger-eval.json` | 22 labeled triggering queries (regression suite) |
| `.claude/skills/meta-agent/evals/evals.json` | 4 output-quality prompts + assertions |
| `.claude/skills/meta-agent/evals/inputs/broken-reviewer.md` | anti-pattern fixture for eval-4 |
| `evals/meta-agent/triggering/routing_probe.py` | faithful routing probe for an installed skill |
| `evals/meta-agent/triggering/routing_results.json` | triggering results (per-query routes) |
| `evals/meta-agent/triggering/run-1/` | the degenerate `run_eval.py` run (kept as the harness-caveat evidence) |
| `evals/meta-agent/iteration-1/eval-{1..4}/{with_skill,without_skill}/outputs/agent.md` | the 8 produced subagents |
| `evals/meta-agent/iteration-1/benchmark.md` | benchmark table |

---

## 7b. Added rigor — grader, blind comparator, analyzer, HTML report

The first pass graded deterministically; this pass adds the full `meta-skill` apparatus for
independent, model-judgment grading and a reviewable report.

**Independent grader subagents** (`agents/grader.md`) re-graded all 8 runs with cited evidence,
writing per-run `grading.json`. They reproduced the with > without gap on every eval
(with-skill mean **0.915** vs baseline **0.605** = **+0.31**, matching the deterministic +31%).

**Blind comparator subagents** (`agents/comparator.md`) judged each eval's two candidates as
neutral A/B (outputs copied to `blind/` dirs; provenance hidden; a private key decoded afterward):

| Eval | Blind winner | = which config | 
|---|---|---|
| 1 | A | **with_skill** |
| 2 | B | **with_skill** |
| 3 | A | **with_skill** |
| 4 | B | **with_skill** |

**With-skill won 4/4 blind**, citing the skill's own levers ("use proactively", `effort`,
NOT-boundary, correct tool list) without knowing which was which. On eval-4 the comparator noted
the baseline's *prose was better* but it lost on the missing frontmatter levers — the clearest
evidence that the skill's value is structural discipline, not wording.

**Analyzer subagent** (`agents/analyzer.md`, benchmark mode) produced 14 grounded notes, surfacing
a finding the first pass missed (see R5).

**HTML review report:** `evals/meta-agent/iteration-1/review.html` — standalone, per-eval outputs
rendered inline with grades, plus the Benchmark tab. Generated with the meta-skill `eval-viewer`.

### R5 — Calibrate `effort`, don't just set it (new, from the analyzer)
The skill reliably gets agents to **include** `effort` (4/4 vs baseline 1/4) but not to **calibrate**
it: eval-2's with-skill test-runner set `effort: medium` where an agentic test loop wants `high`/
`xhigh`. Add an explicit **archetype→effort table** to `authoring-principles.md` (researcher→high,
coding/agentic→xhigh, mechanical lookup→low/medium) so the lever is set *correctly*, not just present.

---

## 8. Limitations of this evaluation

- **Builder model = sonnet, 1 run/eval.** The with-vs-without delta is clean (same model both
  sides), but absolute quality and the token/time figures would differ on Opus, and n=1 per cell
  means per-eval scores carry run-to-run variance. The aggregate direction (+31) is robust; treat
  individual cells as indicative.
- **Triggering = 2 runs/query.** The 3 misses were deterministic (both runs missed), so they're
  stable, but recall ±0.15 is plausible at this sample size.
- **Grading is mostly deterministic** (frontmatter/body regex + validator). It captures structure
  and the skill's named levers well; it does not deeply judge prose quality of each agent body —
  it spot-confirms (e.g. output contracts, restated constraints) rather than full-reads all 8.
- **One assertion didn't discriminate** (eval-3 strict read-only: both configs failed via Bash) —
  it measures a real gap but not a *skill-vs-baseline* difference.
