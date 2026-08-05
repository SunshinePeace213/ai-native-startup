---
description: Runs P4 of a Soriza studio engagement — art direction. Builds the moodboard and style tile, puts two or three genuinely distinct directions in front of the client on real content, and closes on a hard gate where one direction is picked and signed.
argument-hint: [client/project]
model: fable
effort: xhigh
disable-model-invocation: true
hooks:
  Stop:
    - hooks:
        - type: command
          command: uv run --script "$CLAUDE_PROJECT_DIR"/.claude/hooks/check_gate_signoff.py p4
---

# P4 — Art Direction

Give the project a look. Two or three directions, each a different answer to the creative brief rather than the same answer in three colours, shown on the real structure and copy from P3. The client picks exactly one, and its tokens become the palette every client-facing page wears from here on.

## Variables

PROJECT: $1 — the engagement, as `client/project`
PROJECT_DIR: `$(git rev-parse --show-toplevel)/clients/$1/`
IDENTITY: `$(git rev-parse --show-toplevel)/.claude/rules/studio-layer/studio-identity.md` — studio, voice, letterhead, sign-off shape
ARTIFACT_RULES: `$(git rev-parse --show-toplevel)/.claude/rules/studio-layer/client-artifacts.md` — craft, palette source, and publish rules

## Instructions

- No `PROJECT` → stop and ask for it as `client/project`. P3 must be signed.
- `PROJECT` must be exactly two segments, neither starting with `.` nor containing another `/` — anything else can write outside `clients/`. Reject it the same way and ask again.
- Read `IDENTITY` and `ARTIFACT_RULES` before authoring anything.
- Write only under `PROJECT_DIR`. `clients/` is gitignored — never stage, commit, or push client files.
- Spawn `studio-art-director` and `studio-content-strategist` as ordinary subagents, one level deep. Never teammates.
- Directions, not versions. Each one names what it is betting on and what it gives up; a direction nobody would argue against is filler.
- Never show a direction on lorem ipsum — real sections, real copy from `structure/copy-outline.md`.
- Only you talk to the client; a subagent cannot.

## Workflow

1. Spawn `studio-art-director` for `art-direction/moodboard.md` — the visual territory, sourced from the reference audit and what the client said each reference was about.
2. Spawn `studio-art-director` for `art-direction/directions.md` — two or three distinct directions, each with its type, colour and imagery decisions rendered on P3's real sections; spawn `studio-content-strategist` alongside so each direction carries the copy it is meant to hold.
3. Write `art-direction/rationale.md` — what each direction is betting on, what it costs, and which audience read it serves.
4. Show the directions to the client per `ARTIFACT_RULES` and take exactly one pick plus its tweaks. A "some of each" answer is not a pick — re-present.
5. Spawn `studio-art-director` for `art-direction/style-tile.md` on the picked direction: the named tokens — colour, type scale, spacing, radius, elevation — the prototype and the handoff are built from. From here, client pages take their palette from this file, not from the studio default.
6. Take the signature into `sign-off/p4.md` per `IDENTITY`, listing the style tile and the direction rationale with their current SHA-256 values. Report.

## Gate — hard

The Stop hook blocks the phase until `sign-off/p4.md` has a filled Approver and Date and every artifact row names an existing file whose SHA-256 still matches. It resolves the project from the session cwd, or the sole project under `clients/`, so with several projects open run this phase from inside `PROJECT_DIR`.

## Report

```text
🎨 P4 Complete — <client>/<project>

Signed: sign-off/p4.md — <approver>, <date>
Picked: <direction name> — <what it bets on>
Tweaks: <what the client asked of it, or "none">
Documents: art-direction/moodboard.md · directions.md · rationale.md · style-tile.md
Palette from here: art-direction/style-tile.md

Next: /studio-layer:p5-prototype <client>/<project> <prototype tool>
```
