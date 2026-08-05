---
description: Runs P1 of a Soriza studio engagement — discovery. Interviews the client round by round through an interactive page until every question-bank dimension is closed, then writes the discovery notes, glossary, competitive audit and reference audit the definition phase is drafted from.
argument-hint: [client/project]
model: fable
effort: xhigh
disable-model-invocation: true
---

# P1 — Discovery

Find out what is actually true about this project. Run client rounds against the question bank's dimensions — one round at a time, each through a page the client reacts to — until the coverage ledger is clear, then close with the coverage check and a review of the notes. The gate is soft: the notes are reviewed with the client, not signed.

## Variables

PROJECT: $1 — the engagement, as `client/project`
PROJECT_DIR: `$(git rev-parse --show-toplevel)/clients/$1/`
IDENTITY: `$(git rev-parse --show-toplevel)/.claude/rules/studio-layer/studio-identity.md` — studio, voice, letterhead
ARTIFACT_RULES: `$(git rev-parse --show-toplevel)/.claude/rules/studio-layer/client-artifacts.md` — craft, palette source, and publish rules for the round page

## Instructions

- No `PROJECT` → stop and ask for it as `client/project`. P0 must have said go.
- `PROJECT` must be exactly two segments, neither starting with `.` nor containing another `/` — anything else can write outside `clients/`. Reject it the same way and ask again.
- Read `IDENTITY` and `ARTIFACT_RULES` before authoring anything.
- Write only under `PROJECT_DIR`. `clients/` is gitignored — never stage, commit, or push client files.
- **You conduct every client round.** `AskUserQuestion` is unavailable to subagents, so no spawned role can ask the client anything. `studio-discovery-lead` prepares the question set beforehand and writes up the answers afterward.
- Spawn `studio-discovery-lead` and `studio-research-analyst` as ordinary subagents, one level deep. Never teammates.
- Ask in the client's vocabulary. Reading the bank aloud produces a survey, not a conversation.

## Coverage Ledger

Track every dimension the question bank declares — each `###` heading under `## Dimensions` in `studio-client-questions` — as resolved, open, or N/A, and keep going until none are open. Carry anything P0 already answered in as resolved. A dimension is resolved when `discovery/notes.md` holds a written statement of what is true, not a transcript; a genuine non-applicable is written as `N/A, because …`.

## Round Loop

1. Build the ledger from the bank's dimensions plus the intake form. Order the open ones by blast radius — the answers that would most change the design go first.
2. Spawn `studio-discovery-lead` to prepare this round's question set from `studio-client-questions`. Spawn `studio-research-analyst` once, early, for `discovery/competitive-audit.md` and `discovery/reference-audit.md`; its reference read feeds every later round.
3. Author the round's page per `ARTIFACT_RULES` — reference examples and option chips the client reacts to, free text per card, and a copy-as-prompt block returning their answers. Publish best-effort and redeploy the same URL each round; on failure note "publish skipped" and continue from the local file.
4. Conduct the round yourself in ONE `AskUserQuestion`: options "Take the recommended reading" and "Stop discovery here", with the client pasting the page's copy-as-prompt output via "Other".
5. Hand the answers to `studio-discovery-lead` for `discovery/notes.md` — one `## dimension` heading per bank dimension, text matching the bank verbatim — and `discovery/glossary.md`, the client's own words for the things they name — every service, product and location they list by name, the words they ban, and the words they insist on. Update the ledger.
6. **Bounded stop.** A round that resolves nothing new — the client defers, repeats, or disengages — ends discovery. Record what is left as assumptions in the notes and go to the gate. A residue of one or two follow-ups skips the page: ask them directly.

## Gate — soft

Run `uv run --script $(git rev-parse --show-toplevel)/.claude/scripts/studio-layer/check_question_coverage.py $(git rev-parse --show-toplevel)/clients/$1/discovery/notes.md` and report the exit code with what it named. Exit 1 lists each unanswered dimension — answer it or write `N/A, because …`; exit 2 means the notes or the bank could not be read at all. Only then review the notes with the client. No signature and no sign-off file: P1's output is agreed, not approved.

## Report

```text
🔍 P1 Complete — <client>/<project>

Rounds: <N>
Page: <published URL — or local path (publish skipped)>
Coverage: <check_question_coverage.py exit code and verdict>
Ledger: <resolved> resolved · <n/a> N/A · <open> open
Documents: discovery/notes.md · discovery/glossary.md · discovery/competitive-audit.md · discovery/reference-audit.md
Assumptions: <one line each, or "none">

Next: /studio-layer:p2-definition <client>/<project>
```
