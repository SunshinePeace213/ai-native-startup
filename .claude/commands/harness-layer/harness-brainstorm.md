---
description: Pre-plan discovery pass — searches the codebase and brainstorms ~10 intervention options for a rough problem, cheapest to most ambitious, so the user picks what resonates before planning
argument-hint: [rough problem]
model: fable
effort: high
disable-model-invocation: true
disallowed-tools: Task, EnterPlanMode
---

# Harness Brainstorm

Turn a rough problem into options worth reacting to. Before any spec exists, search the codebase and brainstorm ~10 places to intervene — ordered cheapest to most ambitious — so scope is set by picking what resonates, not by committing to the first idea. Discovery only: the page lives in `DISCOVERY_DIR` inside the chain worktree, committed locally; the refined prompt built from the picks is the hand-off.

## Variables

DESCRIPTION: $1 — the rough problem ("users churn after onboarding"), or a prior pass's improved prompt (may carry a `Worktree:` line)
DISCOVERY_DIR: `specs/<slug>/discovery/` — the chain's committed discovery home inside the worktree
ARTIFACT_RULES: `.claude/rules/harness-layer/artifacts.md` — craft, palette, and publish rules for the page
KNOWLEDGE_BASE: `ai-docs/` — cached official docs; catalog in `ai-docs/index.md`

## Instructions

- **DISCOVERY ONLY** — no spec files, no issues, no pushes; write only under `DISCOVERY_DIR`. The refined prompt travels by copy-paste.
- If no `DESCRIPTION` is provided, stop and ask the user for one.
- Worktree: when `DESCRIPTION` carries a `Worktree:` line, `EnterWorktree(path: ...)` into it; otherwise derive a kebab-case `<slug>` and `EnterWorktree(name: "<slug>")`. Never write outside the worktree.
- Search the codebase before ideating: every intervention must anchor to real code — file paths, existing partial mechanisms, missed opportunities. An idea that needs no codebase knowledge is filler; cut it.
- Spread the ladder from ship-this-afternoon to quarter-long bet — don't cluster in the comfortable middle, and include at least one ambitious bet.
- When `DESCRIPTION` touches the harness surface (`.claude/`, `.agents/`, `.codex/`, `ai-docs/`, the memory files), also read the relevant `KNOWLEDGE_BASE` docs from the catalog.
- Do not interview the user or lock scope; this pass only lays out options.
- Commit the pass locally — `📝 docs(discovery): brainstorm pass for <slug>`, no issue footer (no issue exists yet). Never push; the plan's first push carries the discovery commits.
- End by recommending exactly one next hop (first match wins), with the refined prompt as its input: resonating picks that are user-facing and need to be seen → `/harness-layer:harness-prototypes`; open decisions remain for the user → `/harness-layer:harness-interview`; otherwise → `/harness-layer:harness-plan`.

## Workflow

1. Parse `DESCRIPTION`; enter the worktree (see Instructions).
2. Search — trace the problem through the codebase; collect ~10 interventions, each with a title, a size badge (S/M/L/XL), code pointers, what exists today, and a one-line user-facing impact.
3. Author the **Intervention ladder** page per `ARTIFACT_RULES` into `DISCOVERY_DIR` — one card per intervention ordered cheapest → most ambitious, a "this resonates" toggle per card with a live pick counter; copy-as-prompt returns only the resonating picks as the refined prompt.
4. Publish the page best-effort via the Artifact tool; on failure note "publish skipped" and continue with the local file.
5. Commit the pass (see Instructions).
6. Report per `Report` — the inline ladder, the baseline refined prompt, and the hand-off line.

## Refined Prompt

The deliverable. It must stand alone without the page: the problem restated, the resonating interventions with their code pointers, and what each still needs decided. Only what the search surfaced — no generic advice. When `DESCRIPTION` is a prior pass's improved prompt, carry its constraints forward — enrich them with the picks, never drop them. Always end it with the chain line `Worktree: .claude/worktrees/<slug>` so the next pass continues in place.

## Report

```text
💡 Brainstorm Complete

Problem: <one line>
Page: <published URL — or local path (publish skipped)>
Worktree: .claude/worktrees/<slug>
Ladder: <~10 one-liners, cheapest → most ambitious, each with its size badge>

Refined prompt (baseline — the page's copy-as-prompt narrows it to your picks):

<the refined prompt>

Next (<one-line reason for the recommended hop>):
/harness-layer:<harness-prototypes | harness-interview | harness-plan> "<refined prompt>"
```
