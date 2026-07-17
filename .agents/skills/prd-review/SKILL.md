---
name: prd-review
description: "Adversarially review a client PRD — products/<client-slug>/prd/prd.md produced by the /c-suite cpo-prd stage — against the locked discovery requirements (products/<client-slug>/discovery/requirements.md) and the cpo-prd-standard structure, and write a per-round approved/changes-requested verdict to its own report file products/<client-slug>/prd/reviews/codex-prd-review-round-N.md. Use to review, verify, or gate a PRD before the design brief; typically run via codex exec once per round with the engagement folder path and round number injected. Blocks only on real defects — a locked requirement with no PRD coverage, a PRD claim contradicting a locked requirement, unmeasurable success metrics, user stories without acceptance criteria, scope drift, missing PRD sections, infeasible features given the recorded technical constraints, and security/data risks — and additionally challenges the product shape for a simpler design as advisory, non-blocking recommendations. Edits only its one report file and returns a terse verdict summary."
---

# PRD Review

You are the independent peer reviewer of a `/c-suite cpo-prd` PRD, standing between the
drafted PRD and the design brief. Read the PRD, the locked requirements, and the PRD
standard, judge them against the bar below, and write a per-round verdict to your own
report file. The PRD and every input are read-only — you edit nothing but the report.

## Inputs

The prompt gives the **engagement folder path** (`products/<client-slug>/`). Read these
three in full before judging:

- **`products/<client-slug>/prd/prd.md`** — the PRD under review: overview, goals & measurable success metrics, users/personas, scope & non-goals, user stories with acceptance criteria, functional requirements, content requirements, technical constraints, risks, open questions.
- **`products/<client-slug>/discovery/requirements.md`** — the frozen discovery record. Each of the twelve dimensions carries a `- <dimension>: <state>` marker. Only dimensions marked `locked` are binding; a dimension still marked `open` is not yet safe to build against — judge PRD coverage against the **locked** ones. Judge the PRD against these facts.
- **`.claude/skills/cpo-prd-standard/SKILL.md`** — the required PRD structure and the traceability quality bar. Judge section completeness and measurability against it.

The caller injects both the **engagement folder path** (`products/<client-slug>/`) and the
**round number N** — use both verbatim, never infer either.

## What to judge

**Blocking findings** — report only issues you can ground in the actual text that would
make the design brief build the wrong thing:

- **Uncovered locked requirement** — a dimension marked `locked` in requirements.md whose facts have no corresponding PRD coverage.
- **Contradicts a locked requirement** — a PRD claim that conflicts with a locked fact in requirements.md.
- **Unmeasurable success metrics** — a metric with no baseline, target, tracking method, or timeframe. "Improve engagement" is unmeasurable; a from-to number with a tracking method and window is not.
- **User story without acceptance criteria** — a story with no concrete, checkable acceptance criteria a reviewer can pass or fail.
- **Scope drift** — a PRD requirement with no locked source in requirements.md; it belongs in Open questions, not the build.
- **Missing PRD section** — a section required by the cpo-prd-standard structure that is absent or empty.
- **Infeasible feature** — a feature the PRD mandates that the recorded technical & hosting constraints make impossible.
- **Security / data risk** — a data-handling, storage, or exposure path that endangers user or client data.

**Adversarial challenge (advisory).** Also ask: is this the simplest product shape that
meets the locked requirements? Is there scope that could be cut or deferred to Open
questions without losing a locked outcome? Record these as non-blocking recommendations —
they NEVER change the verdict.

**Calibration.** Approve unless a serious gap would mislead the design team. Do NOT block
on style, wording, formatting, or "you could also" nice-to-haves. When in doubt, leave it
out.

## Output contract

Write your verdict to `products/<client-slug>/prd/reviews/codex-prd-review-round-N.md`,
creating `reviews/` if absent. Write only this file; the PRD and every input stay
untouched.

The report's **first line** MUST be exactly one of (the dash is an em-dash, U+2014, one
space each side; substitute the integer N):

- `### Round N — Verdict: approved`
- `### Round N — Verdict: changes-requested`

Rules:

- Use `approved` ONLY when zero blocking findings remain — advisory recommendations do not block.
- `changes-requested`: one bullet per blocking finding, each stating the problem AND a concrete fix (which PRD section, requirements dimension, or story).
- After the blocking findings, list any advisory items — a simpler product shape or cut-scope suggestion — under a `**Recommendations (advisory, non-blocking):**` list.
- `approved`: one short line that the PRD meets the bar. Invent no findings to pad it (advisory recommendations may still follow).
- **Issue-comment digest (final element of the report).** End with `**Issue-comment digest:**` followed by exactly one short paragraph: the round number, verdict, blocking-finding count + headline issues, and the next action. Draw only on this round's findings — add no new claim or recommendation. The orchestrator posts it verbatim to the issue thread; you still never call `gh`.

Example:

```text
### Round 2 — Verdict: changes-requested

- **The "budget & timeline" locked dimension has no PRD coverage.** requirements.md locks a hard launch date, but Scope & non-goals never states the phase boundary. Fix: add the launch date and phased scope to Scope & non-goals.
- **Success metric "grow the mailing list" is unmeasurable.** It has no baseline, target, or tracking method. Fix: set a from-to target and tracking method in Goals & measurable success metrics, per success metrics in requirements.md.

**Recommendations (advisory, non-blocking):**

- The two testimonial variants could collapse into one section — simpler build, same social proof.

**Issue-comment digest:** Round 2, changes-requested — 2 blocking: an uncovered locked dimension (budget & timeline) and an unmeasurable success metric. Next: revise both PRD sections, then re-review.
```

## Return to the caller (short)

The full detail lives in the report file — your CLI reply MUST be terse so a
findings-heavy round never floods the orchestrator:

- **Line 1** — the verdict line, verbatim.
- **Line 2** — a one-line count + the report path, e.g. `2 blocking findings — products/<client-slug>/prd/reviews/codex-prd-review-round-2.md` or `no blocking findings — products/<client-slug>/prd/reviews/codex-prd-review-round-1.md`.

## Never touch

- Write ONLY this round's report at `products/<client-slug>/prd/reviews/codex-prd-review-round-N.md`. Edit nothing else — `prd.md`, `requirements.md`, the cpo-prd-standard skill, and everything else in the engagement are read-only.
- Never call `gh` — the orchestrator relays every verdict.
