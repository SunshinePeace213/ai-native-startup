---
description: Runs P2 of a Soriza studio engagement — definition. Turns discovery into the project brief, creative brief, sitemap, section briefs and user flows, runs the cold-designer test against the signed sitemap, and closes on a hard gate the client signs.
argument-hint: [client/project]
model: fable
effort: xhigh
disable-model-invocation: true
hooks:
  Stop:
    - hooks:
        - type: command
          command: uv run --script "$CLAUDE_PROJECT_DIR"/.claude/hooks/check_gate_signoff.py p2
---

# P2 — Definition

Write down what the project is. The project brief is the client agreement — not a PRD — and the sitemap and section briefs are what P3 structures. Close by testing the briefs on a designer who has seen nothing else, triaging every difference, and getting the client's signature.

## Variables

PROJECT: $1 — the engagement, as `client/project`
PROJECT_DIR: `clients/$1/`
IDENTITY: `.claude/rules/studio-layer/studio-identity.md` — studio, voice, letterhead, sign-off shape
ARTIFACT_RULES: `.claude/rules/studio-layer/client-artifacts.md` — craft, palette source, and publish rules for the review pages

## Instructions

- No `PROJECT` → stop and ask for it as `client/project`. P1's notes must exist.
- Read `IDENTITY` and `ARTIFACT_RULES` before authoring anything.
- Write only under `PROJECT_DIR`. `clients/` is gitignored — never stage, commit, or push client files.
- Spawn `studio-discovery-lead`, `studio-ux-architect` and `studio-content-strategist` as ordinary subagents, one level deep. Never teammates.
- The project brief declares the revision allowance on its own line, exactly `- **Revision rounds:** 2 (plus polish)` with the agreed integer. P5's counter re-derives the allowance from this line, so its absence leaves P5 with no baseline.
- Only you talk to the client; a subagent cannot.

## Workflow

1. Spawn `studio-discovery-lead` for `definition/project-brief.md` (goals, audience, scope, constraints, success, revision allowance) and `definition/creative-brief.md` (the feeling, the references and what they point at, what to avoid).
2. Spawn `studio-ux-architect` for `definition/sitemap.md`, `definition/section-briefs.md` and `definition/user-flows.md`; spawn `studio-content-strategist` alongside for each section's copy intent.
3. Review both briefs and the sitemap with the client through their pages per `ARTIFACT_RULES`, and amend from what comes back before anything is signed.
4. Run the **cold-designer test** (below) and write the triage.
5. Take the client's signature into `sign-off/p2.md` in the shape `IDENTITY` carries: a filled Approver and Date, and one artifact row per approved file with the `sha256sum` of its current content — at least the project brief and the sitemap.
6. Report.

## The cold-designer test

Spawn `studio-ux-architect` as a fresh subagent with a prompt carrying **only** the signed project and creative briefs — no sitemap, no notes, no conversation — and ask for its section-level plan. Its own context window is the whole point: a role that can read the signed answer is not testing anything.

Diff its plan against the signed sitemap and triage every row into `definition/cold-designer-triage.md`:

```markdown
| Section | Cold designer produced | Signed sitemap says | Disposition |
| --- | --- | --- | --- |
| Pricing | three tiers | two tiers plus contact | acceptable variance — tiering is a P4 call |
```

Every `Disposition` reads `brief unclear — amended` (then actually amend the brief) or begins `acceptable variance —` with the reason. The diff itself is advisory — two competent designers differ — so never delete a row to shrink it.

## Gate — hard

The Stop hook blocks the phase until `sign-off/p2.md` has a filled Approver and Date, every artifact row names a file that exists whose SHA-256 still matches, and the triage exists with no untriaged row. It resolves the project from the session cwd, or the sole project under `clients/`, so with several projects open run this phase from inside `PROJECT_DIR`.

## Report

```text
✍️ P2 Complete — <client>/<project>

Signed: sign-off/p2.md — <approver>, <date>
Documents: definition/project-brief.md · creative-brief.md · sitemap.md · section-briefs.md · user-flows.md
Revision allowance: <N> rounds (plus polish)
Cold-designer triage: <rows> rows — <amended> amended · <variance> accepted variance

Next: /studio-layer:p3-structure <client>/<project>
```
