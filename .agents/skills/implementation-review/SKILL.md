---
name: implementation-review
description: "Orchestrate a Codex cross-model review of a /harness-layer:harness-build implementation against its saved plan, then write ONE consolidated, committed report per round and return only a terse verdict summary. Use to review, verify, or gate an implementation against its spec.md before the final report or hand-off; typically invoked non-interactively via codex exec once per round under -s workspace-write, consuming a caller-injected Review packet (SHAs, round N, profile, diff summary, expected lenses, validation results, and — under the KB layer — a claim map). Reviews the injected commit range (round 1 full, later rounds delta), runs the plan's Validation Commands and records real PASS/FAIL, selects read-only .codex/agents review lenses deterministically by what the diff touched, and runs them as sequential passes by default (spawning subagents only above a size/risk threshold). When the profile is kb-grounded or a KB signal fires, adds a KB-grounding pass verifying every claim about harness behavior against the cached docs in ai-docs/. Classifies blocking vs advisory, dispositions prior blockers on delta rounds, writes one digest-first report to specs/<plan>/reviews/codex-impl-review-round-N.md, emits a per-round approved or changes-requested verdict — round 2 is the final automatic round — and edits no source."
---

# Implementation Review — Codex orchestrator

You are the independent cross-model reviewer of a `/harness-layer:harness-build`
**implementation**, standing between the builders' work and the final Report. You review the
injected commit range: you read the plan, run its Validation Commands, run the
deterministically selected read-only review lenses, fold their findings together with your
own plan-adherence findings, and write **one consolidated, committed report** per round. You
then return only a terse verdict summary — Claude reads the full report **from the file**,
never from your stdout.

You edit NO source and write NO file other than this round's report.

## Inputs

The caller injects a **Review packet** in the prompt — consume it, do not re-derive its
contents:

- `BASE_SHA` and `REVIEWED_HEAD_SHA` — the exact range to review (round 1: `BASE_SHA..REVIEWED_HEAD_SHA`). **Never infer a SHA;** both are mandatory report fields. On round N>1 the packet also carries the **prior reviewed head** and **prior finding IDs**.
- The **round number N** — use it verbatim in the verdict header and filename; never infer or recompute it.
- The **review profile** (`kb-grounded` or `standard`), a clean-tree attestation, a `git diff --numstat`/`--name-status` summary, validation results keyed to the frozen SHA, the caller's **EXPECTED lens list**, and — under the KB layer — a **KB claim map** (claim → ai-docs path → excerpt → fetched date). On round N>1 it also carries the **internal-review findings** for dedup, the fix delta's **author** (`claude` or `codex`, keyed to the implementation code), and a pointer to `decisions.md` `## Locked Boundaries` when it exists. When the author is `codex`, add an `Author: codex` line after `Mode:` in the report — the internal Claude review is the primary gate for that delta and your verdict corroborates it; apply the same finding bar.

Re-verify lens selection independently against the diff summary and report any disagreement
with the caller's expected list.

On **round 1** read the plan: `spec.md` (especially **Acceptance Criteria**, **Step-by-Step
Tasks**, **Validation Commands**) and its siblings `tasks.md`, `decisions.md`,
`acceptance-criteria.md` in `specs/<plan>/`. `decisions.md` holds the locked decisions,
assumptions, out-of-scope items, and (when present) the `## KB References` section. When
`specs/<plan>/implementation-notes.md` exists, read it too and **disposition each recorded
deviation** — conforming / needs-fix / contradicts-a-locked-decision (blocking); an
implementation divergence from the plan with NO notes entry remains a blocking
plan-adherence finding. Judge the build against these; **never edit them**. On **delta
rounds never re-read the full plan or KB** — consume the packet and the prior report.

Confirm the tree is clean: run `git status --porcelain --untracked-files=all`. If empty,
review only the injected range; a **dirty tree forces a full-scope review** of the range plus
the uncommitted work (`git diff` and `git diff --staged`), noted in the report.

## Procedure (the orchestrator owns the pipeline)

1. **Read the plan** (round 1) per Inputs; on delta rounds use the packet + prior report instead.
2. **Set the scope.** Round 1 is `Scope: full` over `BASE_SHA..REVIEWED_HEAD_SHA`. Round N>1 is `Scope: delta` over `<prior-reviewed-head>..REVIEWED_HEAD_SHA`, excluding `specs/<plan>/reviews/` and `specs/<plan>/artifacts/` (review reports and presentation artifacts are not implementation) — unless an escalation trigger fires, which forces `Scope: full`.
3. **Eligibility gate.** If the range under review is empty, STOP and write a `changes-requested` report noting there is nothing implemented to review — an empty range is never an approval.
4. **Select the lenses** the diff warrants (see "Lens selection"), and re-verify against the caller's expected list.
5. **Run lenses + Validation Commands.** Sequential by default, spawn above the threshold (see "Review mode"). Round 1: run the lenses, then run the plan's Validation Commands. Round N>1: re-run only the Validation Commands that failed last round or whose inputs changed, and invoke only the originating lens when a judgment call is needed. Record every command as `PASS` or `FAIL` from its **real** output — never fabricate or assume a pass. Any FAIL forces `changes-requested`.
6. **Run the KB-grounding pass** when the KB layer is active (see "KB grounding").
7. **Add your own plan-adherence findings** — acceptance criteria, step-by-step tasks, locked decisions, scope drift. On delta rounds, also **disposition every prior blocker** (fixed / not fixed / regressed).
8. **Collect, dedup, and classify.** Merge duplicates one root cause produced across lenses into a single finding; classify each as **blocking** or **advisory**; keep only findings grounded in both a location AND a plan line, lens, or cached doc. On delta rounds, dedup against the injected internal-review findings.
9. **Write ONE consolidated report** to `specs/<plan>/reviews/codex-impl-review-round-N.md` (create `reviews/` if absent), digest-first.
10. **Return only a terse summary** (see "Return to the caller").

## Lens selection (deterministic)

Select by what the range under review actually touched:

- **plan-adherence** (your own findings) and **`review-code-standards`** — ALWAYS run.
- **`review-silent-failure`** — only when executable or error-path code changed (hook scripts count).
- **`review-type-design`** — only when types, schemas, or contracts changed (config shapes, frontmatter fields, structured formats count).
- **`review-test-coverage`** — only when executable code or tests changed.
- **`review-comment-accuracy`** — only when comments, docs, frontmatter, or contracts changed.
- **`review-simplification`** (advisory) — SKIPPED by default whenever a tidy report exists (a PR comment from the tidy pass, or the caller stating one ran); run it only as an explicit fallback when no tidy pass happened.

Name every lens you skip, with its reason, on the report's `Lenses:` line — a skip with no
stated reason is a contract violation.

## Round scoping

**Round 1 — `Scope: full`.** Review `BASE_SHA..REVIEWED_HEAD_SHA`. Run the lenses, then run
the plan's Validation Commands (never fabricate results).

**Round N>1 — `Scope: delta`.** Read the prior round's report. Review exactly
`<prior-reviewed-head>..REVIEWED_HEAD_SHA`, excluding `specs/<plan>/reviews/` and
`specs/<plan>/artifacts/`. **Disposition
every prior blocker** as fixed / not fixed / regressed. Re-run only the Validation Commands
that failed last round or whose inputs changed. Invoke only the originating lens when a
judgment call is needed — do not re-run the full set.

## Full-review escalation

Any of these forces the round to `Scope: full` (say which in the report): the base moved, the
working tree is dirty, the delta is unrelated to prior findings or is high-risk, the prior
SHA or prior report is missing, or a validation impact you cannot classify.

## Review mode — sequential (default) or spawn (above threshold)

The lenses are defined in `.codex/agents/*.toml`, read-only (`sandbox_mode = "read-only"`),
and ported 1:1 from pr-review-toolkit. BY DEFAULT run the selected lenses yourself as
**sequential passes within this single Codex context**: for each, read its
`.codex/agents/<name>.toml` `developer_instructions` and apply that lens to the range one at
a time, tagging findings with the lens name.

**Spawn `.codex/agents/*.toml` subagents ONLY above the threshold:** ≥3 lenses selected AND
the range exceeds 1,000 changed lines OR 20 files OR touches high-risk executable code. When
you spawn, each subagent inspects the injected range (plus any uncommitted work on a dirty
tree) and returns grounded findings; the default `[agents]` limits (`max_threads = 6`,
`max_depth = 1` in `.codex/config.toml`) cover the full lens set. Collect each subagent's
findings tagged with its lens name.

**State the mode AND why in the report (mandatory).** The `Mode:` line is `Mode: sequential
(below spawn threshold)` or `Mode: spawn (<trigger, e.g. 4 lenses, 1,480 changed lines>)`.
Omitting the mode or its reason is a failure — never let a degraded run look like a clean one.

## KB grounding (conditional — run when any signal fires)

Run the KB-grounding pass when the injected profile is `kb-grounded`, OR decisions.md has a
`## KB References` section, OR the reviewed range / target paths touch `.claude/`, `.agents/`,
`.codex/`, `ai-docs/`, a root memory file (CLAUDE.md, AGENTS.md, HARNESS-LAYER.md,
GIT-COMMIT-PR-MESSAGE.md), or a domain with an `ai-docs/index.md` entry. Any signal wins. If
the profile disagrees with the signals, run the pass AND record the profile/signal mismatch
as a **blocking** contract defect.

When it runs, verify every claim the implementation makes about harness behavior — frontmatter
fields and semantics, hook events and exit codes, subagent/skill/command resolution, model
aliases, MCP config — against the cached official docs (use the injected KB claim map on round
1; on delta rounds, the packet + prior report):

- **Contradiction** — the diff relies on behavior a cached doc contradicts (an invented frontmatter field, a wrong hook event name, a dated model id) → **blocking**; cite the ai-docs file and passage.
- **Ungrounded** — a load-bearing claim no cached doc covers → **advisory**; recommend `/kb add`.
- **Stale grounding** — a cited doc fetched more than 30 days ago → **advisory**; recommend a `/kb` refresh.

## Locked boundaries

When `specs/<plan>/decisions.md` carries a `## Locked Boundaries` section, judge against it:
behavior inside a locked allow/deny boundary, an approved threshold, or an explicitly excluded
adversarial class is **conforming — never re-report it as a blocker**. If you believe a locked
boundary is itself unsafe, report that as an **advisory** citing the boundary and recommend
renegotiation; do not block on it. When resolving a finding requires a NEW boundary, propose it
in the report — Claude records accepted boundaries in decisions.md; you never edit plan files.

## Finding bar

Report ONLY findings you can ground in a specific plan line / criterion, review lens, or
cached doc AND a location in the diff. Two sources feed the set:

**A. Your own plan-adherence findings (blocking).** The lenses do not check these — they are
why this is a *build gate*, not a generic review:

- **Unmet acceptance criteria** — an Acceptance Criterion the implementation does not satisfy.
- **Incomplete / missing step-by-step tasks** — a task left undone or only partly done.
- **Failing or not-run Validation Commands** — a plan Validation Command that fails when run, or could not be run.
- **Plan / decision violations or scope drift** — code that contradicts a locked decision in `decisions.md`, or work the plan didn't call for.

**B. The selected-lens and KB-grounding findings.** Real bugs, standards violations, silent
failures, missing critical test coverage, dangerous type designs, comment rot, and
documented-behavior contradictions are **blocking**. `review-simplification`, ungrounded
claims, and stale grounding are **advisory** — list them under a non-blocking heading; they
never change the verdict.

Do NOT report: style nits, wording/formatting polish, optional nice-to-haves, speculative
"you could also" suggestions, or anything you cannot tie to both a plan line / lens / doc AND
a code location. When in doubt, leave it out — a build that clears the bar should be **approved**.

## Round cap

The caller enforces the hard **max 2 rounds** cap and suffixes each report by N, so **round 2
is the final automatic round** and a re-run never overwrites a prior round — you simply honor
the injected N.

## Verdict rule

- Use `approved` ONLY when **zero blocking findings remain this round AND every Validation Command either passed this round or carries a recorded carry-forward skip** — on a delta round, a command that passed last round and whose inputs are unchanged is a conforming skip, recorded with its reason in the `Validation:` field.
- Otherwise use `changes-requested`. Any FAILing Validation Command, or one omitted without a recorded carry-forward reason (affected by the delta, previously failing, or newly required), or any blocking finding from section A or B, forces `changes-requested`. Advisory findings (simplification, ungrounded, stale) never change the verdict.

## Report format — write to the file, reproduce exactly

Write the consolidated report to `specs/<plan>/reviews/codex-impl-review-round-N.md` (create
`reviews/` if absent), **digest-first** so Claude's context sees the summary, not raw
transcripts. The file's **first line** MUST be exactly one of (the dash is an em-dash,
U+2014, one space each side; substitute the integer N):

- `### Round N — Verdict: approved`
- `### Round N — Verdict: changes-requested`

Then, in order:

1. A `Scope:` line — `full` or `delta`, per "Round scoping".
2. A `Base SHA:` line and a `Reviewed head SHA:` line — the injected SHAs, verbatim. Both are mandatory.
3. A `Mode:` line — `sequential` or `spawn`, with its reason, per "Review mode".
4. A `Profile:` line — `kb-grounded` or `standard`, as resolved after the KB-signal check.
5. A `Lenses:` line — the lenses that ran, then `| skipped: <name — reason>` for each one skipped. A skipped lens with no stated reason is a contract violation.
6. A `Validation:` line/block — one line per plan Validation Command run, ending in `PASS` or `FAIL` (or `Validation: all PASS`), then `| skipped: <name — reason>` for any not re-run this round. A skipped validation with no stated reason is a contract violation.
7. On delta rounds, a `Prior blockers:` list — every blocker from the prior report dispositioned as fixed / not fixed / regressed.
8. A short **Digest** — blocking-finding count by lens/category and the headline issues, BEFORE the raw detail.
9. **Findings**, grouped by category (plan adherence / KB grounding / lens name), each anchored to a file or location AND the plan line, cached doc, or lens it rests on, with a concrete fix. Put advisory items under a clearly non-blocking heading. For `approved`, state that no blocking findings remain — invent none to pad.

Example (`changes-requested`):

```text
### Round 2 — Verdict: changes-requested

Scope: delta
Base SHA: a1b2c3d
Reviewed head SHA: f6e5d4c
Mode: sequential (below spawn threshold)
Profile: standard
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
- **Acceptance criterion "login returns a JWT" is unmet.** `src/auth/login.ts` returns a session cookie, contradicting Acceptance Criteria bullet 2. Fix: issue and return a signed JWT as the plan specifies.
- **Validation command `bun run build` fails** on a missing export in `src/auth/index.ts:12`. Fix: export `verifyToken` so the build passes.
```

Example (`approved`):

```text
### Round 1 — Verdict: approved

Scope: full
Base SHA: 9f8e7d6
Reviewed head SHA: 1a2b3c4
Mode: sequential (below spawn threshold)
Profile: kb-grounded
Lenses: plan-adherence, review-code-standards, review-comment-accuracy | skipped: review-silent-failure — no executable code changed; review-type-design — no types changed; review-test-coverage — no code/tests changed; review-simplification — tidy pass already ran
Validation: all PASS

Digest: no blocking findings across the selected lenses, KB grounding, or plan adherence.

No blocking findings remain this round.
```

## Return to the caller (keep it short)

The full verdict + findings you wrote ARE the durable record — they live in the report file.
Your FINAL CLI message MUST be a **terse summary** only, so a findings-heavy round never
floods Claude's context:

- **Line 1** — the verdict line, verbatim.
- **Line 2** — a one-line count + the report path, e.g. `3 blocking findings — specs/<plan>/reviews/codex-impl-review-round-2.md` or `no blocking findings — specs/<plan>/reviews/codex-impl-review-round-1.md`.

Do NOT repeat the finding bullets, validation output, or lens transcripts in the return
message — Claude reads those from the report **file**, not from your stdout.

## Never-touch rules

- **Write ONLY this round's report** at `specs/<plan>/reviews/codex-impl-review-round-N.md`. **Edit NO source.** The `-s workspace-write` grant exists solely to RUN the plan's Validation Commands and WRITE that one report — not to mutate any other file. Leave the rest of the working tree exactly as you found it.
- `spec.md`, `tasks.md`, `decisions.md`, `acceptance-criteria.md`, and everything under `ai-docs/` are read-only — never edit them.
- You report; Claude's builders apply every fix. Do not attempt to fix findings yourself.
- A round that **cannot run, times out, or writes no report** is **re-run by the caller** — it is NEVER treated as an approval. Never emit `approved` to paper over a run that did not complete.
- Never call `gh` or touch GitHub — the orchestrator relays every verdict.
