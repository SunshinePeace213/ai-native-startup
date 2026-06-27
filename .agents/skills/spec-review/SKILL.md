---
name: spec-review
description: "Review a plan-w-team implementation spec (the plan.md a planning run drafts under specs) before execution and append a Codex Findings verdict plus blocking findings to that file. Use when asked to review, verify, or gate a plan-w-team spec or plan.md before /build or hand-off; typically invoked non-interactively via codex exec once per review round. Judges the spec against a blocking-issue bar only (missing or contradictory requirements, infeasible or mis-ordered steps, untestable acceptance criteria, security or data risks, scope drift past the locked decisions) and appends a per-round approved or changes-requested verdict block ONLY inside the existing '## Codex Findings' section, editing nothing else."
---

# Spec Review

You are the independent second reviewer of a `plan-w-team` implementation spec,
standing between Claude's draft and `/build`. Read the spec, judge it against a
blocking-only bar, and record a per-round verdict in the spec's own
`## Codex Findings` section. Append only — the rest of the file is Claude-owned.

## Procedure

1. Read the inputs (below) in full.
2. Judge the spec against the finding bar — blocking issues only, grounded in the text.
3. Determine the round number N (scan existing `### Round K` headers).
4. Write the verdict block under `## Codex Findings`, appending to the end of the file.
5. Touch nothing else.

## Inputs

- The spec's `plan.md` path is given in the prompt. Read it in full.
- Read the sibling `decisions.md` in the same folder (the planning run writes both
  next to each other, e.g. `specs/<plan-name>/plan.md` and
  `specs/<plan-name>/decisions.md`). `decisions.md` holds the locked requirements,
  assumptions, and out-of-scope / non-goal items. Judge the plan against these: a
  step that contradicts a locked decision, or work the decisions ruled out of scope,
  is a finding. Read `decisions.md`; never edit it.

## Finding bar

Report ONLY blocking issues you can ground in the actual text of `plan.md` /
`decisions.md` — issues that would cause `/build` to produce the wrong thing or get
stuck. The categories:

- **Missing or contradictory requirements** — a stated objective/requirement with no
  implementing step, or two requirements (or a requirement and a locked decision)
  that conflict.
- **Infeasible or mis-ordered steps** — a step that cannot work as written, depends
  on something not yet produced, or is sequenced before its prerequisite.
- **Untestable / unmeasurable acceptance criteria** — a criterion with no observable
  pass/fail check, or validation commands that don't actually verify the criterion
  they claim to.
- **Security or data risks** — destructive operations, secret/credential exposure, or
  data-loss paths introduced by the plan.
- **Scope drift** — work in the plan that exceeds the locked decisions, or that the
  decisions explicitly marked out of scope / as a non-goal.

Do NOT report: style nits, wording or formatting polish, optional nice-to-haves,
speculative "you could also" suggestions, or anything you cannot tie to a specific
line of the spec. No speculation. When in doubt, leave it out — a spec that clears
the bar should be approved.

## Round numbering

Before writing, scan the `## Codex Findings` section for existing headers matching
`### Round K` (K an integer). Let **N = (highest existing K) + 1**. If there are
none, **N = 1**. Each invocation appends the next round; never overwrite a prior one.

## Output contract — reproduce exactly

Append your review to the END of the spec file, under its existing
`## Codex Findings` heading. The block's first line MUST be exactly one of the
following (the dash is a literal em-dash "—", U+2014, with one space on each side;
substitute the integer N from above):

- `### Round N — Verdict: approved`
- `### Round N — Verdict: changes-requested`

Verdict rule:

- Use `approved` ONLY when zero blocking findings remain this round.
- Otherwise use `changes-requested`.

Under the header:

- For `changes-requested`: one bullet per finding. Each bullet states the problem AND
  a concrete recommendation — what to change and where (which section / step of the
  plan). Ground every finding in the spec text.
- For `approved`: a single short line stating the spec meets the bar with no blocking
  findings this round. Invent no findings to pad an approval.

Example of an appended block:

```
### Round 2 — Verdict: changes-requested

- **Acceptance criterion 3 is untestable.** "System should feel fast" has no
  measurable check. Recommend: replace with a concrete threshold and add a validation
  command that asserts it (e.g. p95 latency under a stated ms budget).
- **Step 4 depends on the migration in Step 6.** Step 4 reads the new column before
  Step 6 creates it. Recommend: reorder so the migration runs before any step that
  reads the column.
```

## Never-touch rule

- Edit NOTHING in `plan.md` except appending your block within / after the
  `## Codex Findings` section.
- The rest of the file is Claude-owned. Do not reorder, reword, reformat, or
  "improve" any other line. Leave any existing scaffolding (e.g. a
  `_Pending Codex review._` placeholder) in place and append after it.
- `decisions.md` is read-only — never edit it.

## Missing Codex Findings section

The `## Codex Findings` section is scaffolded by `plan-w-team`; do NOT create it
yourself. If it is absent from `plan.md`, make NO edits to the file. Instead, report
in your response that the `## Codex Findings` section is missing and must be
scaffolded before a verdict can be recorded — that absence is itself a blocking
condition. Do not write a verdict block anywhere else in the file.

## Verdict relay (orchestrator-only)

The orchestrator (Claude) — not this skill — relays each round's verdict and
findings to the tracking GitHub issue via `gh`. This skill MUST NOT call `gh` or
otherwise touch GitHub; it only appends its verdict to the `## Codex Findings`
section per the output contract above. Claude reads that verdict and does the relay.
