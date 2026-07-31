---
description: Runs P5 of a Soriza studio engagement — prototype. Writes the prompt pack for the chosen prototype tool, builds something the client can click, and settles each revision round against the allowance the signed brief bought, raising a change order when a round goes past it.
argument-hint: "[client/project] [prototype tool]"
model: fable
effort: xhigh
disable-model-invocation: true
---

# P5 — Prototype

Turn the picked direction into something the client can click, then revise it in rounds that are counted. The gate is the allowance: rounds are free until the signed brief runs out, after which a round needs a change order the client approved. No signature closes this phase — P6 does.

## Variables

PROJECT: $1 — the engagement, as `client/project`
TOOL: $2 — the prototype tool this project drives
PROJECT_DIR: `clients/$1/`
IDENTITY: `.claude/rules/studio-layer/studio-identity.md` — studio, voice, letterhead
ARTIFACT_RULES: `.claude/rules/studio-layer/client-artifacts.md` — craft, palette source, and publish rules for the feedback page

## Instructions

- No `PROJECT` → stop and ask for it as `client/project`. P4 must be signed.
- No `TOOL` → pick it by the rules below and say which rule decided, before writing the prompt pack.
- Read `IDENTITY` and `ARTIFACT_RULES` before authoring anything.
- Write only under `PROJECT_DIR`. `clients/` is gitignored — never stage, commit, or push client files.
- Spawn `studio-prototype-engineer` and `studio-art-director` as ordinary subagents, one level deep. Never teammates.
- Everything the prototype shows comes from the signed structure, copy and style tile. A prototype that invents a section is a scope change, not a round.
- Only you talk to the client; a subagent cannot.

## Choosing the tool

In order, first match wins: a tool the client already pays for; otherwise one that can export, or be re-driven from, the prompt pack, so the engagement is not locked to it; otherwise Claude Design. Record the choice and the rule that decided it in `prototype/prompt-pack.md`.

## Workflow

1. Spawn `studio-prototype-engineer` for `prototype/prompt-pack.md` — the tool and why, the style tile's tokens, the screens to build and the content each carries — then for the prototype itself. Record its link in the pack.
2. Spawn `studio-art-director` to judge the build against the picked direction before the client sees it, and revise until it holds.
3. Show it to the client and triage their feedback per `ARTIFACT_RULES`, one card per item with the remaining allowance visible.
4. Log the round in `prototype/revision-log.md` before building it:

   ```markdown
   | Round | Date | Requested | Change order |
   | --- | --- | --- | --- |
   | 3 | 2026-08-14 | swap hero video for a still | `change-orders/1.md` |
   ```

5. Close the round with `uv run --script .claude/scripts/studio-layer/check_revision_count.py clients/$1/` and report its verdict. Exit 1 names each round past the allowance whose change order is missing or incomplete — write `change-orders/N.md` (Requested, an integer `Cost — rounds`, `Cost — time`, and `Approved by` with a name and date), get the client's approval into it, and re-run. Exit 2 means the brief declares no allowance: that is a missing baseline, so go back to P2 rather than assuming a number.
6. Repeat from step 3 while the client has rounds left and wants one. Report when the prototype is settled.

## Report

```text
🖱️ P5 Complete — <client>/<project>

Tool: <tool> — <the rule that chose it>
Prototype: <link>
Rounds: <used> of <allowance> (plus polish)
Change orders: <paths, or "none">
Revision count: <check_revision_count.py exit code and verdict>

Next: /studio-layer:p6-handoff <client>/<project>
```
