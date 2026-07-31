---
description: Runs P6 of a Soriza studio engagement — design QA and handoff. Assembles the states matrix, tokens and handoff pack a builder consumes, computes the coverage and contrast checks, gets an adversarial QA review, and closes the engagement on the client's final signature.
argument-hint: [client/project]
model: fable
effort: xhigh
disable-model-invocation: true
hooks:
  Stop:
    - hooks:
        - type: command
          command: uv run --script "$CLAUDE_PROJECT_DIR"/.claude/hooks/check_gate_signoff.py p6
---

# P6 — Design QA and Handoff

Produce what a builder consumes — tokens, states, breakpoints, copy deck, assets — prove it is complete against the inventory the client signed at P3, and hand it over. Producing the pack ends the engagement: Soriza does not build from it.

## Variables

PROJECT: $1 — the engagement, as `client/project`
PROJECT_DIR: `$(git rev-parse --show-toplevel)/clients/$1/`
IDENTITY: `$(git rev-parse --show-toplevel)/.claude/rules/studio-layer/studio-identity.md` — studio, voice, letterhead, sign-off shape
INVENTORY: `$(git rev-parse --show-toplevel)/clients/$1/structure/inventory.md` — the P3-signed component list every check quantifies over

## Instructions

- No `PROJECT` → stop and ask for it as `client/project`. P4 must be signed and P5 settled.
- `PROJECT` must be exactly two segments, neither starting with `.` nor containing another `/` — anything else can write outside `clients/`. Reject it the same way and ask again.
- Read `IDENTITY` before writing anything. Write only under `PROJECT_DIR`; `clients/` is gitignored — never stage, commit, or push client files.
- Spawn `studio-design-qa` and `studio-client-partner` as ordinary subagents, one level deep. Never teammates.
- **Never author or edit `INVENTORY` here.** It is a P3 deliverable the client signed; the gate re-hashes it against that signature. A component genuinely missing from it needs a change order and a re-signature, not a quiet edit.
- Accessibility results are stated as Soriza project thresholds — 4.5:1 normal text, 3:1 large text and UI components, 24×24 CSS px minimum target — never as conformance to a specification this repo has not mirrored.

## Workflow

1. Spawn `studio-client-partner` to assemble the pack from P3–P5: `handoff/states-matrix.md`, `handoff/tokens.md`, and `handoff/pack.md` (breakpoints, copy deck, assets, and where each lives).
2. `handoff/states-matrix.md` carries one table per breakpoint under a `### breakpoint` heading, rows are components from `INVENTORY`, columns exactly `hover | focus | disabled | loading | empty | error`. A cell says what actually happens; `-` and `TBD` count as unfilled.

   ```markdown
   ### mobile

   | Component | hover | focus | disabled | loading | empty | error |
   | --- | --- | --- | --- | --- | --- | --- |
   | PrimaryButton | darkens 8% | 2px ring | 40% opacity, no pointer | spinner replaces label | n/a — always has a label | inline message below |
   ```

3. `handoff/tokens.md` carries two tables — colour pairs (`Foreground`, `Background`, `Kind` of `normal-text`, `large-text` or `ui-component`, `Used for`) and tap targets (`Target`, `Width (px)`, `Height (px)`) — covering every colour token and every component `INVENTORY` names.
4. Run both checks and fix what they name, never the file they measure against:
   - `uv run --script $(git rev-parse --show-toplevel)/.claude/scripts/studio-layer/check_states_matrix.py $(git rev-parse --show-toplevel)/clients/$1/handoff/states-matrix.md`
   - `uv run --script $(git rev-parse --show-toplevel)/.claude/scripts/studio-layer/check_contrast.py $(git rev-parse --show-toplevel)/clients/$1/handoff/tokens.md`

   Exit 1 lists each missing pair, unfilled cell, failing ratio or undersized target. Exit 2 means the check could not run — a malformed hex, an unparseable table, or a missing inventory — so fix the input, not the design.
5. Spawn `studio-design-qa`, which writes `handoff/qa-report.md` — one row per finding, `Severity` `blocking` or `advisory`, `Status` `open` or `resolved`. Resolve every `blocking` finding and record the evidence; write `handoff/accessibility-check.md` from the computed results plus its judgment on focus order and state copy.
6. Spawn `studio-client-partner` for the final `sign-off/p6.md` per `IDENTITY`, listing the pack, the matrix and the tokens with their current SHA-256 values. Report.

## Gate — hard

The Stop hook blocks the phase until `sign-off/p6.md` has a filled Approver and Date and every artifact row resolves and matches, no `blocking` finding in `handoff/qa-report.md` is still `open`, and `INVENTORY` still hashes to what `sign-off/p3.md` recorded — so rows deleted since P3 are caught rather than shrinking what the design is measured against. It resolves the project from the session cwd, or the sole project under `clients/`, so with several projects open run this phase from inside `PROJECT_DIR`.

## Report

```text
📦 P6 Complete — <client>/<project>

Signed: sign-off/p6.md — <approver>, <date>
Handoff: handoff/pack.md · states-matrix.md · tokens.md · accessibility-check.md
States matrix: <exit code and verdict>
Contrast: <exit code and verdict>
QA: <blocking findings, all resolved> · <advisory count> advisory
Inventory: matches the P3 signature

Next: /studio-layer:p7-retro <client>/<project>
```
