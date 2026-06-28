---
name: spec-review
description: "Review a plan-w-team implementation spec — the four files (entry spec.md, plus decisions.md, tasks.md, acceptance-criteria.md) a planning run drafts under specs — before execution and append a Codex Findings verdict plus blocking findings to spec.md. Use when asked to review, verify, or gate a plan-w-team spec before /build or hand-off; typically invoked non-interactively via codex exec once per review round. Judges the spec against a blocking-issue bar only (missing or contradictory requirements, infeasible or mis-ordered steps, untestable acceptance criteria, security or data risks, scope drift past the locked decisions) and appends a per-round approved or changes-requested verdict block ONLY inside the existing '## Codex Findings' section of spec.md, editing nothing else. Writes the full findings into '## Codex Findings' and returns only a terse verdict summary to the caller, so Claude reads detail from spec.md rather than from stdout."
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
4. Insert the verdict block INSIDE the `## Codex Findings` section, immediately before
   the next `##` heading (e.g. `## Codex Verification`) — never below that heading. On
   round 1, replace the `_Pending Codex review._` placeholder with the block; on later
   rounds, add the new `### Round N` block after the previous round's, still above the
   next `##` heading.
5. Touch nothing else.

## Inputs

The planning run writes four files side by side in one folder
(`specs/<plan-name>/`). Read all four in full before judging:

- **`spec.md`** — the entry point; its path is given in the prompt. Holds the what &
  why, tracking, and the `## Codex Findings` section your verdict is appended to.
- **`decisions.md`** — sibling in the same folder. Holds the locked requirements,
  assumptions, and out-of-scope / non-goal items. Judge the spec against these: a
  step that contradicts a locked decision, or work the decisions ruled out of scope,
  is a finding.
- **`tasks.md`** — sibling in the same folder. The phases, team, and step-by-step
  tasks that implement the spec.
- **`acceptance-criteria.md`** — sibling in the same folder. The numbered, testable
  acceptance criteria and their validation commands.

Read all four; edit only `spec.md` (and only its `## Codex Findings` section, per the
output contract). The siblings are read-only — never edit them.

## Finding bar

Report ONLY blocking issues you can ground in the actual text of the four files —
issues that would cause `/build` to produce the wrong thing or get stuck. The
blocking categories:

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

Use this five-category lens to frame _what to look for_ across the four files when
applying the blocking bar above:

| Category     | What to look for                                                                                                                                     |
| ------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| Completeness | TODOs, placeholders, unfilled `<…>` micro-prompts, "TBD", empty required sections across the four files                                              |
| Consistency  | Internal contradictions; a step in tasks.md that conflicts with a locked decision in decisions.md; an acceptance criterion with no implementing task |
| Clarity      | Requirements ambiguous enough to build the wrong thing                                                                                               |
| Scope        | Focused on one plan; work that exceeds or contradicts decisions.md's Non-Goals / Out of Scope                                                        |
| YAGNI        | Unrequested features, speculative over-engineering past the locked decisions                                                                         |

**Calibration.** Only flag issues that would cause real problems during
implementation. A missing required section, a contradiction, or a two-way-ambiguous
requirement are issues. Minor wording, stylistic preference, and "this section is
less detailed than that one" are not. Approve unless there are serious gaps that
would lead to a flawed build.

Do NOT report: style nits, wording or formatting polish, optional nice-to-haves,
speculative "you could also" suggestions, or anything you cannot tie to a specific
line of the spec. No speculation. When in doubt, leave it out — a spec that clears
the bar should be approved.

## Round numbering

Before writing, scan the `## Codex Findings` section for existing headers matching
`### Round K` (K an integer). Let **N = (highest existing K) + 1**. If there are
none, **N = 1**. Each invocation appends the next round; never overwrite a prior one.

## Output contract — reproduce exactly

Append your review within the `## Codex Findings` section, immediately before the
following `##` heading (e.g. `## Codex Verification`) — never below it. On round 1,
replace the section's `_Pending Codex review._` placeholder with your block; on later
rounds, add the new block after the previous round's, still above that `##` heading.
The block's first line MUST be exactly one of the
following (the dash is a literal em-dash "—", U+2014, with one space on each side;
substitute the integer N from above):

- `### Round N — Verdict: approved`
- `### Round N — Verdict: changes-requested`

Verdict rule:

- Use `approved` ONLY when zero blocking findings remain this round.
- Otherwise use `changes-requested`.

Under the header:

- For `changes-requested`: one bullet per blocking finding. Each bullet states the
  problem AND a concrete recommendation — what to change and where (which file and
  section / step). Ground every finding in the spec text. Optionally, after the
  blocking findings, add a `**Recommendations (advisory, non-blocking):**` bullet
  list for improvements that are NOT blocking — these never change the verdict and
  never block a future approval.
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

**Recommendations (advisory, non-blocking):**

- Consider noting the rollback command in tasks.md so a failed migration is reversible.
```

## Return to the caller (keep it short)

The full verdict + findings you wrote above ARE the durable record — they live in
`spec.md`'s `## Codex Findings` section. Your FINAL CLI message back to the
orchestrator (Claude) MUST be short, so a findings-heavy round never floods the
orchestrator's context:

- **Line 1** — the verdict line, verbatim: `### Round N — Verdict: approved` or
  `### Round N — Verdict: changes-requested`.
- **Line 2** — a one-line summary: for `changes-requested`, the count of blocking
  findings plus a pointer, e.g. `3 blocking findings — full detail in spec.md
  ## Codex Findings`; for `approved`, `no blocking findings`.

Do NOT repeat the finding bullets, recommendations, or any validation output in the
return message — the orchestrator reads those from `spec.md`'s `## Codex Findings`
section, not from your stdout.

## Never-touch rule

- Edit NOTHING in `spec.md` except appending your block within / after the
  `## Codex Findings` section.
- The rest of the file is Claude-owned. Do not reorder, reword, reformat, or
  "improve" any other line. Within `## Codex Findings`, replace the
  `_Pending Codex review._` placeholder with your round-1 block; disturb no
  scaffolding or content outside that section.
- `decisions.md`, `tasks.md`, and `acceptance-criteria.md` are read-only — never edit them.

## Missing Codex Findings section

The `## Codex Findings` section is scaffolded by `plan-w-team`; do NOT create it
yourself. If it is absent from `spec.md`, make NO edits to the file. Instead, report
in your response that the `## Codex Findings` section is missing and must be
scaffolded before a verdict can be recorded — that absence is itself a blocking
condition. Do not write a verdict block anywhere else in the file.

## Verdict relay (orchestrator-only)

The orchestrator (Claude) — not this skill — relays each round's verdict and
findings to the tracking GitHub issue via `gh`. This skill MUST NOT call `gh` or
otherwise touch GitHub; it only appends its verdict to the `## Codex Findings`
section per the output contract above. Claude reads that verdict and does the relay.
