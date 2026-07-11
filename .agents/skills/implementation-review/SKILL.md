---
name: implementation-review
description: "Orchestrate a Codex cross-model review of a /build implementation against its saved plan, then write ONE consolidated, committed report per round and return only a terse verdict summary. Use to review, verify, or gate the implemented code of a /build run against its spec.md before the final report or hand-off; typically invoked non-interactively via codex exec once per round under -s workspace-write. Reads spec.md + its siblings (tasks.md, decisions.md, acceptance-criteria.md), reviews the injected commit range (BASE_SHA..REVIEWED_HEAD_SHA, or a delta range on later rounds), runs the plan's Validation Commands and records real PASS/FAIL, then spawns a deterministically selected set of read-only .codex/agents review lenses (from pr-review-toolkit: code-standards, silent-failure, type-design, test-coverage, comment-accuracy, and advisory simplification) chosen by what the diff touched — or, if headless spawn is unavailable, runs the selected lenses as sequential passes (the report states which mode). The orchestrator owns the pipeline: it runs the eligibility gate, collects and dedups the lens findings together with its own plan-adherence findings (acceptance criteria, tasks, locked decisions, scope drift), classifies blocking vs advisory, then writes one digest-first report to specs/<plan>/reviews/codex-impl-review-round-N.md and returns only a terse summary. Reports only blocking issues plus advisory notes, emits a per-round approved or changes-requested verdict, writes only that one report, and edits no source."
---

# Implementation Review — Codex orchestrator

You are the independent cross-model reviewer of a `/build` **implementation**,
standing between the builders' work and `/build`'s final Report. You review the
injected commit range: you read the plan, run its Validation Commands, spawn the
deterministically selected read-only review subagents (or run their lenses
sequentially when spawn is unavailable), fold their findings together with your own
plan-adherence findings, and write **one consolidated, committed report** per round.
You then return only a terse verdict summary — Claude reads the full report **from the
file**, never from your stdout.

You run under `-s workspace-write`, but that grant exists for exactly two purposes:
**running the plan's Validation Commands** and **writing your one report file**. You
edit NO source and write NO file other than this round's report.

## Inputs

- The plan's `spec.md` path is given in the prompt. Read it in full — especially its
  **Acceptance Criteria**, **Step-by-Step Tasks**, and **Validation Commands**. The
  plan folder is `spec.md`'s parent, `specs/<plan>/`.
- Read the siblings `tasks.md`, `decisions.md`, and `acceptance-criteria.md` in the
  same folder. `decisions.md` holds the locked decisions, assumptions, and
  out-of-scope / non-goal items — judge the build against these: code that
  contradicts a locked decision, or work the decisions ruled out of scope, is a
  finding. Read them; **never edit them**.
- The review target is the **injected commit range**. The prompt supplies `BASE_SHA`
  and `REVIEWED_HEAD_SHA`; review exactly `BASE_SHA..REVIEWED_HEAD_SHA` (round 1) or,
  on later rounds, the delta range in "Round scoping". **Never infer a SHA** — both are
  injected, and both are mandatory report fields. On round N>1 the prompt also supplies
  the **prior round's reviewed-head SHA**.
- Require a **clean working tree**. Run `git status --porcelain --untracked-files=all`;
  if it is empty, review only the injected range. A **dirty tree forces a full-scope
  review** of the range plus the uncommitted work (`git diff` and `git diff --staged`),
  and you note the dirty tree in the report.
- The review **round number N** is given in the prompt. Do NOT scan files or prior
  output to infer it — it is injected. Use it verbatim.

## Procedure (the orchestrator owns the pipeline)

1. **Read the plan.** Read `spec.md`, `tasks.md`, `decisions.md`, and
   `acceptance-criteria.md` in full.
2. **Set the scope.** Round 1 is `Scope: full` over `BASE_SHA..REVIEWED_HEAD_SHA`.
   Round N>1 is `Scope: delta` over `<prior-reviewed-head>..REVIEWED_HEAD_SHA` — unless
   an escalation trigger fires, which forces `Scope: full` (see "Round scoping" and
   "Full-review escalation").
3. **Eligibility gate.** If the range under review is empty, STOP and write a
   `changes-requested` report noting there is nothing implemented to review — an empty
   range is never an approval.
4. **Select the lenses** the diff warrants (see "Lens selection"). Plan-adherence and
   `review-code-standards` always run; the rest are gated by what changed.
5. **Run lenses + Validation Commands.** Round 1: spawn the selected lens workers FIRST,
   then run the plan's Validation Commands concurrently while they work. Round N>1:
   re-run only the Validation Commands that failed last round or whose inputs changed,
   and invoke only the originating lens when a judgment call is needed. Record every
   command as `PASS` or `FAIL` from its **real** output — **never fabricate or assume a
   pass**. Any FAIL forces a `changes-requested` verdict (see Verdict rule).
6. **Add your own plan-adherence findings** — the build-gate-unique work the lenses do
   not do (acceptance criteria, step-by-step tasks, locked decisions, scope drift). On
   delta rounds, also **disposition every prior blocker** (fixed / not fixed /
   regressed). See "Finding bar" and "Round scoping".
7. **Collect, dedup, and classify.** Merge duplicates that one root cause produced
   across lenses into a single finding. Classify each as **blocking** or **advisory**
   (see "Finding bar"); keep only findings you can ground in both a location AND a
   plan line or lens.
8. **Write ONE consolidated report** to
   `specs/<plan>/reviews/codex-impl-review-round-N.md` (create `reviews/` if absent).
   Use the exact format in "Report format".
9. **Return only a terse summary** to the caller (see "Return to the caller").

## Lens selection (deterministic)

Do not run a fixed set — select by what the range under review actually touched:

- **plan-adherence** (your own findings) and **`review-code-standards`** — ALWAYS run.
- **`review-silent-failure`** — only when executable or error-path code changed.
- **`review-type-design`** — only when types, schemas, or contracts changed.
- **`review-test-coverage`** — only when executable code or tests changed.
- **`review-comment-accuracy`** — only when comments, docs, or contracts changed.
- **`review-simplification`** (advisory) — SKIPPED by default whenever a tidy report
  exists (a PR comment from the tidy pass, or the caller stating one ran); run it only
  as an explicit fallback when no tidy pass happened.

Name every lens you skip, with its reason, on the report's `Lenses:` line — a skip
with no stated reason is a contract violation.

## Round scoping

**Round 1 — `Scope: full`.** Review `BASE_SHA..REVIEWED_HEAD_SHA`. Spawn the selected
lens workers FIRST, then run the plan's Validation Commands concurrently while they
work (never fabricate results).

**Round N>1 — `Scope: delta`.** Read the prior round's report. Review exactly
`<prior-reviewed-head>..REVIEWED_HEAD_SHA`. **Disposition every prior blocker** as
fixed / not fixed / regressed. Re-run only the Validation Commands that failed last
round or whose inputs changed. Invoke only the originating lens when a judgment call is
needed — do not re-run the full set.

## Full-review escalation

Any of these forces the round to `Scope: full` (say which in the report): the base
moved, the working tree is dirty, the delta is unrelated to prior findings or is
high-risk, the prior SHA or prior report is missing, or a validation impact you cannot
classify.

## Review mode — spawn (default) or sequential (fallback)

The review subagents are defined in `.codex/agents/*.toml` and auto-discovered by the
Codex runtime. Each is read-only (`sandbox_mode = "read-only"`), inspects the injected
range (plus any uncommitted work on a dirty tree), and returns grounded findings — it
edits nothing. The lenses, ported 1:1 from pr-review-toolkit:

- `review-code-standards` — violations of this repo's standards (AGENTS.md + global
  `~/.codex/AGENTS.md` + `.claude/rules/*` + `GIT-COMMIT-PR-MESSAGE.md`) and obvious bugs.
- `review-silent-failure` — swallowed errors, overbroad catches, unjustified fallbacks.
- `review-type-design` — encapsulation and invariant expression/enforcement of types.
- `review-test-coverage` — untested critical paths, error handling, edge/negative cases.
- `review-comment-accuracy` — comment/docstring accuracy and comment rot.
- `review-simplification` — **advisory** complexity/redundancy suggestions (non-blocking).

**SPAWN mode (default).** Spawn the selected named subagents (via the Codex
subagent-spawn capability) to review the range, then wait for every one to return. The
default `[agents]` limits (`max_threads = 6`, `max_depth = 1` in `.codex/config.toml`)
cover the full lens set. Collect each subagent's findings tagged with its lens name.

**SEQUENTIAL mode (fallback, fail loud).** If a runtime check shows headless spawn is
unavailable — the subagent-spawn capability is not exposed in this `codex exec`
runtime, the `.codex/agents/*.toml` are not discoverable, or a spawn attempt errors —
do NOT silently skip the lenses. Instead run the selected lenses yourself as
**sequential review passes within this single Codex context**: for each, read its
`.codex/agents/<name>.toml` `developer_instructions` and apply that lens to the range,
one at a time, tagging findings with the lens name.

**State the mode in the report (mandatory).** The report MUST carry a `Mode:` line —
`Mode: spawn` or `Mode: sequential (headless spawn unavailable — lenses run as
sequential passes)`. Omitting the mode is a failure; never let a degraded run look like
a clean one.

## Finding bar

Report ONLY findings you can ground in a specific plan line / criterion or review
lens AND a location in the diff. Two sources feed the set:

**A. Your own plan-adherence findings (blocking, the build-gate-unique work).** The
lenses do not check these — they are why this is a *build gate*, not a generic review:

- **Unmet acceptance criteria** — an Acceptance Criterion the implementation does not satisfy.
- **Incomplete / missing step-by-step tasks** — a task left undone or only partly done.
- **Failing or not-run Validation Commands** — a plan Validation Command that fails when run, or could not be run.
- **Plan / decision violations or scope drift** — code that contradicts a locked decision in `decisions.md`, or work the plan didn't call for.

**B. The selected-lens findings.** Real bugs, standards violations, silent failures,
missing critical test coverage, dangerous type designs, and comment rot surfaced by
the subagents (or your sequential passes) are **blocking**. `review-simplification` is
**advisory** — list its findings under a non-blocking heading; they never change the verdict.

Do NOT report: style nits, wording/formatting polish, optional nice-to-haves,
speculative "you could also" suggestions, or anything you cannot tie to both a plan
line / lens AND a code location. When in doubt, leave it out — a build that clears the
bar should be **approved**.

## Round number

N is supplied in the prompt for this run. Use it verbatim in the verdict header and
the report filename. Do not infer or recompute it. The caller (`/build`) enforces the
**max 2 rounds** cap and suffixes each report by N, so a re-run never overwrites a
prior round — you simply honor the injected N.

## Verdict rule

- Use `approved` ONLY when **zero blocking findings remain this round AND every
  Validation Command either passed this round or carries a recorded carry-forward
  skip** — on a delta round, a command that passed last round and whose inputs are
  unchanged is a conforming skip, recorded with its reason in the `Validation:` field.
- Otherwise use `changes-requested`. Any FAILing Validation Command, or one omitted
  without a recorded carry-forward reason (affected by the delta, previously failing,
  or newly required), or any blocking finding from section A or B, forces
  `changes-requested`. Advisory (`review-simplification`) findings never change the verdict.

## Report format — write to the file, reproduce exactly

Write the consolidated report to
`specs/<plan>/reviews/codex-impl-review-round-N.md` (create `reviews/` if absent),
**digest-first** so Claude's context sees the summary, not 6 raw transcripts. The
file's **first line** MUST be exactly one of the following (the dash is a literal
em-dash "—", U+2014, one space each side; substitute the integer N):

- `### Round N — Verdict: approved`
- `### Round N — Verdict: changes-requested`

Then, in order:

1. A `Scope:` line — `full` or `delta`, per "Round scoping".
2. A `Base SHA:` line and a `Reviewed head SHA:` line — the injected SHAs, verbatim.
   Both are mandatory.
3. A `Mode:` line — `spawn` or `sequential`, per "Review mode".
4. A `Lenses:` line — the lenses that ran, then `| skipped: <name — reason>` for each
   one you skipped. A skipped lens with no stated reason is a contract violation.
5. A `Validation:` line/block — one line per plan Validation Command run, ending in
   `PASS` or `FAIL` (or `Validation: all PASS`), then `| skipped: <name — reason>` for
   any not re-run this round. A skipped validation with no stated reason is a contract
   violation.
6. On delta rounds, a `Prior blockers:` list — every blocker from the prior report
   dispositioned as fixed / not fixed / regressed.
7. A short **Digest** — blocking-finding count by lens/category and the headline
   issues, BEFORE the raw detail, so a findings-heavy round never floods Claude's context.
8. **Findings**, grouped by lens / category, each anchored to the plan section /
   acceptance criterion or lens AND the file or location, with a concrete fix. Put
   `review-simplification` (advisory) findings under a clearly non-blocking heading.
   For `approved`, state that no blocking findings remain — invent none to pad.

Example (`changes-requested`):

```
### Round 2 — Verdict: changes-requested

Scope: delta
Base SHA: a1b2c3d
Reviewed head SHA: f6e5d4c
Mode: spawn
Lenses: plan-adherence, review-code-standards, review-silent-failure | skipped: review-type-design — no types changed; review-test-coverage — no code/tests changed; review-comment-accuracy — no comments/docs changed; review-simplification — tidy pass already ran
Validation:
- bun run build → FAIL
- skipped: uv run pytest -q — passed last round, inputs unchanged
Prior blockers:
- "login returns a JWT" unmet — not fixed
- swallowed error in refresh.ts:40 — fixed

Digest: 2 blocking — 1 unmet acceptance criterion (still open), 1 failing validation command.

Findings:

**Plan adherence**
- **Acceptance criterion "login returns a JWT" is unmet.** `src/auth/login.ts`
  returns a session cookie, contradicting Acceptance Criteria bullet 2. Fix: issue
  and return a signed JWT as the plan specifies.
- **Validation command `bun run build` fails** on a missing export in
  `src/auth/index.ts:12`. Fix: export `verifyToken` so the build passes.
```

Example (`approved`):

```
### Round 1 — Verdict: approved

Scope: full
Base SHA: 9f8e7d6
Reviewed head SHA: 1a2b3c4
Mode: spawn
Lenses: plan-adherence, review-code-standards, review-silent-failure, review-test-coverage | skipped: review-type-design — no types changed; review-comment-accuracy — no comments/docs changed; review-simplification — tidy pass already ran
Validation: all PASS

Digest: no blocking findings across the selected lenses or plan adherence.

No blocking findings remain this round.
```

## Return to the caller (keep it short)

The full verdict + findings you wrote ARE the durable record — they live in the
report file. Your FINAL CLI message back to the orchestrator (Claude) MUST be a
**terse summary** only, so a findings-heavy round never floods Claude's context:

- **Line 1** — the verdict line, verbatim.
- **Line 2** — a one-line count + the report path, e.g.
  `3 blocking findings — specs/<plan>/reviews/codex-impl-review-round-2.md` or
  `no blocking findings — specs/<plan>/reviews/codex-impl-review-round-1.md`.

Do NOT repeat the finding bullets, validation output, or subagent transcripts in the
return message — Claude reads those from the report **file**, not from your stdout.

## Never-touch rules

- **Write ONLY this round's report** at
  `specs/<plan>/reviews/codex-impl-review-round-N.md`. **Edit NO source.** The
  `-s workspace-write` grant exists solely to RUN the plan's Validation Commands and
  WRITE that one report — not to mutate any other file. Leave the rest of the working
  tree exactly as you found it.
- `spec.md`, `tasks.md`, `decisions.md`, and `acceptance-criteria.md` are read-only —
  never edit them.
- You report; Claude's builders apply every fix. Do not attempt to fix findings yourself.
- A round that **cannot run, times out, or writes no report** is **re-run by the
  caller** — it is NEVER treated as an approval. Never emit `approved` to paper over a
  run that did not complete.
- Never call `gh` or touch GitHub — the orchestrator (`/build`) relays every verdict.
