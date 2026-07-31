---
description: Runs P0 of a Soriza studio engagement — intake and qualification. Captures what the client is asking for as an intake form, then writes the internal go/no-go qualification note that decides whether the studio takes the project.
argument-hint: [client/project]
model: fable
effort: xhigh
disable-model-invocation: true
---

# P0 — Intake and Qualification

Open an engagement: capture the client's request and decide whether Soriza takes it. Both documents land under `PROJECT_DIR`. The gate is soft — an internal go/no-go, no client signature and no sign-off file — and nothing downstream runs until it says go.

## Variables

PROJECT: $1 — the engagement, as `client/project`
PROJECT_DIR: `clients/$1/`
IDENTITY: `.claude/rules/studio-layer/studio-identity.md` — studio, voice, letterhead, sign-off shape

## Instructions

- No `PROJECT` → stop and ask for it as `client/project`.
- Read `IDENTITY` before writing anything. Every client-facing document opens with its letterhead and is written in its voice.
- Write only under `PROJECT_DIR`. `clients/` is gitignored — never stage, commit, or push client files.
- Spawn `studio-client-partner` as an ordinary subagent, one level deep. Never a teammate.
- Only you can ask the client anything — `AskUserQuestion` is unavailable to subagents. Collect what is missing before spawning.

## Workflow

1. Create `PROJECT_DIR/intake/`.
2. In one `AskUserQuestion`, get whatever the request leaves open: the outcome they want, the deadline and what it is tied to, the budget range, and who signs off.
3. Spawn `studio-client-partner` to write `intake/intake-form.md` — the request in the client's own words, contacts and decision-makers, deadline, budget range, what exists today — and `intake/qualification-note.md` — fit, capacity, commercial and delivery risk, and a recommendation with its reason.
4. Make the go/no-go call yourself and record it in the qualification note. A no-go ends the engagement here; say what would change it.
5. Report.

## Report

```text
📋 P0 Complete — <client>/<project>

Verdict: <go | no-go> — <one line>
Documents: intake/intake-form.md · intake/qualification-note.md
Open: <what P1 has to find out first, or "nothing">

Next: /studio-layer:p1-discovery <client>/<project>
```
