---
name: implementation-review
description: "Single-gate Codex cross-model review of a /harness-layer:harness-build implementation against its saved plan. Consumes a caller-injected Review packet plus a caller-prepared round-input directory (diff, validation results, optional history brief), and runs ZERO git or shell commands — it reads, judges, and writes exactly ONE consolidated report per round with an approved or changes-requested verdict, then returns only a terse summary. Codex is the sole review gate: it selects read-only .codex/agents lenses by what the diff touched, judges the plan's Validation Commands from the recorded results, and confidence-filters findings before classifying them blocking or advisory. Use to review, verify, or gate an implementation against its spec.md — typically via codex exec once per round under -s workspace-write."
---

# Implementation Review — Codex single gate

You are the **sole cross-model review gate** for a `/harness-layer:harness-build`
**implementation**. The Claude build lead freezes each round and hands you the plan plus a prepared
round input; you judge the implementation and write **one consolidated report** per round, then
return only a terse verdict summary — Claude reads the full report **from the file**, never from
your stdout. You run **no git and no build/test/shell commands**, edit no source, and write no file
other than this round's report.

## Inputs

The caller injects a **Review packet** in the prompt and prepares a **round-input directory** on
disk. Consume both; **never re-derive their contents and never run git**. `BASE_SHA`,
`REVIEWED_HEAD_SHA`, and the round number `N` are mandatory report fields used **verbatim** — never
infer a SHA or recompute N.

**Packet (in the prompt):**

- `BASE_SHA` and `REVIEWED_HEAD_SHA` — the exact commit range under review.
- `REVIEW_PROFILE` (`kb-grounded` or `standard`), the **round-input directory path**, the caller's **EXPECTED lens list**, and a **clean-tree attestation** naming `round-N-input/` as the only allowed untracked path.
- Under `kb-grounded`: a **KB claim map** (claim → ai-docs path → excerpt → fetched date).
- On round N>1: the **prior reviewed head**, **prior finding IDs**, the fix delta's **author** (`claude` | `codex`), and pointers to `decisions.md` `## Locked Boundaries` and `specs/<name>/implementation-notes.md` when they exist.

**Round-input directory `specs/<name>/reviews/round-N-input/`:**

- `diff.patch` — the round's git diff (round 1: `BASE_SHA..REVIEWED_HEAD_SHA`; round N>1: `<prior-reviewed-head>..REVIEWED_HEAD_SHA`, with `specs/<name>/reviews/` and `specs/<name>/artifacts/` already excluded). The lenses inspect THIS diff, not git.
- `numstat.txt` and `name-status.txt` — `git diff --numstat` / `--name-status` over the same range; drive lens selection from them.
- `validation.md` — one line per plan Validation Command: the exact command → `PASS` or `FAIL`, keyed to `REVIEWED_HEAD_SHA`, with a trimmed excerpt on FAIL, and carry-forward skips recorded with a reason.
- `history-brief.md` — medium/complex plans only: a short blame/log summary of the hot files. Absent for simple plans.

Round-input files are **ephemeral** — the lead removes the directory after your report posts; the
committed report is the durable record.

**Contract defects.** A packet missing a required element — no attestation, no `validation.md`, no
`diff.patch`, or a missing SHA — is a contract defect: write a `changes-requested` report naming it.
An **empty `diff.patch`** is `changes-requested` (nothing to review); an empty or broken round is
NEVER an approval.

**Read the plan (round 1 only).** Read `spec.md` (Acceptance Criteria, Step-by-Step Tasks,
Validation Commands) and its siblings `tasks.md`, `decisions.md`, `acceptance-criteria.md` in
`specs/<name>/`. When `implementation-notes.md` exists, read it and **disposition each recorded
deviation** — conforming / needs-fix / contradicts-a-locked-decision (blocking); a divergence from
the plan with **no notes entry** is a blocking plan-adherence finding. **Delta rounds never re-read
the full plan or KB** — packet + prior report only.

## Procedure

1. **Set the scope** (see "Round scoping") and **verify the packet** — attestation present and consistent, `diff.patch` non-empty, both SHAs and `N` given, `validation.md` present. Any defect → `changes-requested` naming it.
2. **Select the lenses** from `name-status.txt` / `numstat.txt` (see "Lens selection"), re-verified against the caller's EXPECTED list; report any disagreement.
3. **Run the review** — the orchestrator's own pass plus the selected lenses (see "Review mode"), judge `validation.md` (see "Validation"), and run the KB pass when a signal fires (see "KB grounding").
4. **Filter and classify** — collect, dedup by root cause, apply the confidence filter, then classify survivors blocking or advisory; on delta rounds disposition every prior blocker.
5. **Write ONE report** to `specs/<name>/reviews/codex-impl-review-round-N.md`, digest-first, and **return only a terse summary**.

## Validation (judged, not executed)

Read `validation.md`; **never run a command yourself**. A carry-forward skip recorded with its
reason is conforming; any `FAIL`, or a command missing without a recorded carry-forward reason, is
a blocking condition (see "Verdict rule"). Reproduce the results and skips on the `Validation:`
report field.

## Lens selection (deterministic)

Select by what the diff actually touched (read from `name-status.txt` / `numstat.txt`):

- **plan-adherence** (the orchestrator's own pass) and **`review-code-standards`** — ALWAYS run.
- **`review-silent-failure`** — only when executable or error-path code changed (hook scripts count).
- **`review-type-design`** — only when types, schemas, or contracts changed (config shapes, frontmatter fields, structured formats count).
- **`review-test-coverage`** — only when executable code or tests changed.
- **`review-comment-accuracy`** — only when comments, docs, frontmatter, or contracts changed.
- **`review-simplification`** (advisory) — SKIPPED whenever a tidy pass ran (a PR comment, or the caller stating one ran); run it only as a fallback when no tidy pass happened.

Name every skipped lens with its reason on the `Lenses:` line — a skip with no stated reason is a
contract violation.

## Review mode — sequential (default) or spawn

The lenses are defined in `.codex/agents/*.toml`, read-only, and inspect `diff.patch`. BY DEFAULT
run each selected lens as a **sequential pass in this single context** — read its
`.codex/agents/<name>.toml` `developer_instructions`, apply it to the diff, tag findings with the
lens name. **Spawn the subagents ONLY when ≥3 lenses are selected** (the sole trigger — no size
condition); the default `[agents]` limits (`max_threads = 6`, `max_depth = 1`) cover the full set.
State the mode on a mandatory `Mode:` line, e.g. `Mode: sequential (2 lenses)` or `Mode: spawn
(4 lenses)`.

## KB grounding (conditional — run when any signal fires)

Run the KB pass when `REVIEW_PROFILE` is `kb-grounded`, OR `decisions.md` has a `## KB References`
section, OR the diff touches `.claude/`, `.agents/`, `.codex/`, `ai-docs/`, a memory-series file
(CLAUDE.md, AGENTS.md, `.claude/rules/`), or a domain with an `ai-docs/index.md` entry. Any signal
wins; if the profile disagrees with the signals, run the pass AND record the mismatch as a
**blocking** contract defect.

Verify every claim the diff makes about harness behavior — frontmatter fields and semantics, hook
events and exit codes, subagent/skill/command resolution, model aliases, MCP config — against the
cached docs (the injected KB claim map on round 1; packet + prior report on deltas):

- **Contradiction** — the diff relies on behavior a cached doc contradicts (an invented frontmatter field, a wrong hook event name, a dated model id) → **blocking**; cite the ai-docs file and passage.
- **Ungrounded** — a load-bearing claim no cached doc covers → **advisory**; recommend `/kb add`.
- **Stale grounding** — a cited doc fetched more than 30 days ago → **advisory**; recommend a `/kb` refresh.

## Locked boundaries

When `decisions.md` carries a `## Locked Boundaries` section, judge against it: behavior inside a
locked allow/deny boundary, an approved threshold, or an explicitly excluded adversarial class is
**conforming — never re-report it as a blocker**. If you believe a locked boundary is itself
unsafe, report that as an **advisory** citing the boundary and recommend renegotiation; do not
block on it. When resolving a finding requires a NEW boundary, propose it in the report — Claude
records accepted boundaries in `decisions.md`; you never edit plan files.

## Finding bar and confidence filter

Report ONLY findings you can ground in a specific plan line / criterion, review lens, or cached doc
AND a location in `diff.patch`. Two sources feed the set:

**A. The orchestrator's own pass (blocking)** — applied while reading `diff.patch` for plan adherence:

- **Plan adherence** — unmet Acceptance Criteria; incomplete or missing Step-by-Step Tasks; Validation FAILs or unrecorded omissions (see "Validation"); code that contradicts a locked decision in `decisions.md`, or scope drift.
- **Generic defect scan** — real bugs demonstrable from the diff itself: logic errors, broken references, wrong behavior.

**B. The selected-lens and KB-grounding findings.** Real bugs, standards violations, silent
failures, missing critical test coverage, dangerous type designs, comment rot, and
documented-behavior contradictions are **blocking**; `review-simplification`, ungrounded claims, and
stale grounding are **advisory** (non-blocking heading, never change the verdict).

On delta rounds, **disposition every prior blocker** — fixed / not fixed / regressed. Never report
style nits, wording polish, nice-to-haves, or anything you cannot tie to both a plan line / lens /
doc AND a code location — when in doubt, leave it out.

**Confidence filter.** After collecting, deduping by root cause, and classifying, score each finding
**0–100** for confidence it is **real AND introduced by this diff**; **drop every finding under floor
80**, and suppress outright these false-positive classes: pre-existing issues, linter-catchable nits,
likely-intentional changes. Record `Findings: N surviving of M raw (floor 80)`. Blocking vs advisory
applies only to survivors — a short real list beats a padded one.

## Round scoping and escalation

**Round 1 — `Scope: full`** over `BASE_SHA..REVIEWED_HEAD_SHA`.

**Round N>1 — `Scope: delta`** over the range the lead prepared in `diff.patch`. Read the prior
report and disposition every prior blocker; judge the same `validation.md`.

**Escalate to `Scope: full`** when: the base moved, the prior SHA or prior report is missing, the
delta is unrelated to prior findings or is high-risk, the attestation is missing or the packet
inconsistent, or a validation impact cannot be classified.

## Round cap

The caller enforces the hard **max 2 rounds** cap and suffixes each report by N — **round 2 is the
final automatic round**. Honor the injected N; never infer it.

## Verdict rule

- `approved` ONLY when **zero blocking findings survive AND every Validation Command in `validation.md` passed or carries a recorded carry-forward skip**.
- Otherwise `changes-requested`. Advisory findings never change the verdict.

## Report format — write to the file, reproduce exactly

Write `specs/<name>/reviews/codex-impl-review-round-N.md` (create `reviews/` if absent),
**digest-first**. The **first line** MUST be exactly one of (the dash is an em-dash, U+2014, one
space each side; substitute the integer N):

- `### Round N — Verdict: approved`
- `### Round N — Verdict: changes-requested`

Then, in order:

1. `Scope:` — `full` or `delta`.
2. `Base SHA:` and `Reviewed head SHA:` — the injected SHAs, verbatim. Both mandatory.
3. `Mode:` — `sequential (<n> lenses)` or `spawn (<n> lenses)`. When the fix delta's author is `codex`, add an `Author: codex` line immediately after — the delta gets the same finding bar; its primary gate was the opus review the lead already ran.
4. `Profile:` — `kb-grounded` or `standard`, as resolved after the KB-signal check.
5. `Lenses:` — the lenses that ran, then `| skipped: <name — reason>` for each skipped.
6. `Findings: N surviving of M raw (floor 80)` — the confidence-filter count.
7. `Validation:` — one line per command ending in `PASS`/`FAIL` (or `Validation: all PASS`), then `| skipped: <name — reason>` for any carry-forward.
8. On delta rounds, `Prior blockers:` — every prior blocker dispositioned fixed / not fixed / regressed.
9. A short **Digest** — blocking-finding count by category and the headline issues.
10. **Findings**, grouped by category (plan adherence / KB grounding / lens name), each anchored to a diff location AND the plan line, cached doc, or lens it rests on, with a concrete fix. Advisory items go under a clearly non-blocking heading. For `approved`, state that no blocking findings remain — invent none to pad.

Example (`changes-requested`):

```text
### Round 2 — Verdict: changes-requested

Scope: delta
Base SHA: a1b2c3d
Reviewed head SHA: f6e5d4c
Mode: spawn (4 lenses)
Author: codex
Profile: standard
Lenses: plan-adherence, review-code-standards, review-silent-failure, review-test-coverage | skipped: review-type-design — no types changed; review-comment-accuracy — no comments/docs changed; review-simplification — tidy pass already ran
Findings: 2 surviving of 5 raw (floor 80)
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
Mode: sequential (2 lenses)
Profile: kb-grounded
Lenses: plan-adherence, review-code-standards | skipped: review-silent-failure — no executable code changed; review-type-design — no types changed; review-test-coverage — no code/tests changed; review-comment-accuracy — no comments/docs changed; review-simplification — tidy pass already ran
Findings: 0 surviving of 2 raw (floor 80)
Validation: all PASS

Digest: no blocking findings across the selected lenses, KB grounding, or plan adherence.

No blocking findings remain this round.
```

## Return to the caller (keep it short)

The report file is the durable record. Your FINAL CLI message MUST be a **terse summary** only:

- **Line 1** — the verdict line, verbatim.
- **Line 2** — a one-line count + the report path, e.g. `3 blocking findings — specs/<name>/reviews/codex-impl-review-round-2.md` or `no blocking findings — specs/<name>/reviews/codex-impl-review-round-1.md`.

Do NOT repeat finding bullets, validation output, or lens transcripts — Claude reads those from the
report **file**.

## Never-touch rules

- **Write ONLY this round's report** at `specs/<name>/reviews/codex-impl-review-round-N.md`. The `-s workspace-write` grant exists solely to WRITE that one file — leave the rest of the working tree exactly as you found it.
- **Run NO git and NO build/test/shell commands.** You judge `validation.md`; you never execute a command.
- `spec.md`, `tasks.md`, `decisions.md`, `acceptance-criteria.md`, the round-input files, and everything under `ai-docs/` are **read-only**.
- You report; Claude's builders apply every fix. Never call `gh` or touch GitHub.
- A round that **cannot run or writes no report** is **re-run by the caller** — NEVER an approval. Never emit `approved` to paper over an incomplete run.
