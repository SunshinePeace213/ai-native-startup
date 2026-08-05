---
description: Runs P7 of a Soriza studio engagement — retro and lesson routing. Writes the project retro from what the phases actually recorded, then routes each lesson to the file where it will load again the next time it is relevant.
argument-hint: [client/project]
model: fable
effort: xhigh
disable-model-invocation: true
---

# P7 — Retro and Lesson Routing

Close the engagement by writing down what it taught and putting each lesson where it will be read again. The gate is soft: it closes when every lesson has a home, not when a document exists.

## Variables

PROJECT: $1 — the engagement, as `client/project`
PROJECT_DIR: `$(git rev-parse --show-toplevel)/clients/$1/`
IDENTITY: `$(git rev-parse --show-toplevel)/.claude/rules/studio-layer/studio-identity.md` — studio, voice, letterhead

## Instructions

- No `PROJECT` → stop and ask for it as `client/project`. P6 must be signed.
- `PROJECT` must be exactly two segments, neither starting with `.` nor containing another `/` — anything else can write outside `clients/`. Reject it the same way and ask again.
- Spawn `studio-retro-scribe` as an ordinary subagent, one level deep. Never a teammate.
- The retro itself is client data and stays under `PROJECT_DIR`. The only writes outside it are the routed lessons, and only into the three `studio-layer` directories step 2 names — never another namespace, a hook, a settings file, or `AGENTS.md`.
- A routed lesson is the studio's own conclusion in the studio's own words. Never carry client-supplied or third-party text into a `.claude/` file — those load into every later session, while `clients/` does not.
- Build the retro from evidence — the revision log and change orders, the QA report's findings, which gates blocked and why, and where a phase's documents had to be rewritten. A retro from memory records the last week only.
- **Route, do not graduate.** No lesson becomes a new skill, command, or agent here. Promoting a repeated lesson is a separate decision with its own plan.
- A lesson that names no file it would change is an observation. Keep it in the retro and route nothing.

## Workflow

1. Spawn `studio-retro-scribe` for `retro/retro.md` — what the engagement cost against what was sold, where each gate blocked, what the client changed their mind about and when, and what would be done differently.
2. Route each lesson to where it loads when it is relevant:
   - About one phase's own conduct → that phase's command under `.claude/commands/studio-layer/`.
   - About a role's judgment or boundary → that role's agent file under `.claude/agents/studio-layer/`.
   - About client-facing documents, pages, or the studio's voice → the matching rule under `.claude/rules/studio-layer/`.
   - Specific to this client → `retro/retro.md` only; it never leaves the project folder.
3. Make each routed edit in place, keeping the target's existing shape and brevity — a lesson appended as a log entry is a lesson nobody reads.
4. Report every routed edit by path and one line, and every lesson deliberately left unrouted.

## Report

```text
🧾 P7 Complete — <client>/<project>

Retro: retro/retro.md
Routed: <path> — <lesson in one line>   (one row per edit, or "none")
Kept local: <lessons that stayed with this client, or "none">
Not graduated: <repeated lessons worth promoting later, or "none">

Engagement closed. The handoff pack is what a builder takes from here.
```
