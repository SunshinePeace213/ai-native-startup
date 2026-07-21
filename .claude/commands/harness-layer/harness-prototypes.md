---
description: Pre-plan discovery pass — throwaway HTML prototypes to react to before planning: several wildly different design directions, or a single mock of a feature with fake data
argument-hint: [description]
model: fable
effort: high
disable-model-invocation: true
disallowed-tools: Task, EnterPlanMode
---

# Harness Prototypes

Render it before anyone builds it. Before any spec exists, prototype what the user can only judge by seeing — wildly different design directions, or a throwaway mock with fake data — so taste is exercised while changes are still free. Discovery only: prototypes live in `DISCOVERY_DIR` inside the chain worktree, committed locally; the improved prompt names the chosen direction and the prototype path so the plan can reference it.

## Variables

DESCRIPTION: $1 — the feature to prototype, or a prior pass's improved prompt (may carry a `Worktree:` line)
DISCOVERY_DIR: `specs/<slug>/discovery/` — the chain's committed discovery home inside the worktree
ARTIFACT_RULES: `.claude/rules/harness-layer/artifacts.md` — craft, palette, and publish rules for the page

## Instructions

- **DISCOVERY ONLY** — no spec files, no issues, no pushes; write only under `DISCOVERY_DIR`. Never touch the real app — no backend routes, no frontend state, no real wiring.
- If no `DESCRIPTION` is provided, stop and ask the user for one.
- Worktree: when `DESCRIPTION` carries a `Worktree:` line, `EnterWorktree(path: ...)` into it; otherwise derive a kebab-case `<slug>` and `EnterWorktree(name: "<slug>")`. Never write outside the worktree.
- Classify the mode (see `Modes`).
- Fake data only, but make it plausible: read enough of the real app first (existing UI conventions, real feature names and data shapes) that the prototype reads as native.
- Do not interview the user or lock decisions; this pass only renders prototypes to react to.
- Commit the pass locally — `📝 docs(discovery): prototypes pass for <slug>`, no issue footer (no issue exists yet). Never push; the plan's first push carries the discovery commits.
- End by recommending exactly one next hop (first match wins), with the improved prompt as its input: open decisions remain for the user → `/harness-layer:harness-interview`; otherwise → `/harness-layer:harness-plan`.

## Modes

- **Directions** — the user can't say what they want but will know it when they see it ("I have no visual taste / don't know what's possible"). One page, 2–4 wildly different design directions side by side with tweak controls; copy-as-prompt returns the chosen direction plus tweaks.
- **Mockup** — the user knows roughly what they want and needs to react to it before it touches the real app ("mock the new toolbar with fake data"). A single throwaway mock of the feature; copy-as-prompt returns the user's reactions and requested changes.

## Workflow

1. Parse `DESCRIPTION`; classify the mode (directions | mockup); enter the worktree (see Instructions).
2. Read the real app's surface the prototype imitates — UI conventions, naming, data shapes — and invent realistic fake data from it.
3. Author the page per `ARTIFACT_RULES` into `DISCOVERY_DIR` — directions → **Design directions** page; mockup → **Mockup** page.
4. Publish the page best-effort via the Artifact tool; on failure note "publish skipped" and continue with the local file.
5. Commit the pass (see Instructions).
6. Report per `Report` — the baseline improved prompt and the hand-off line.

## Improved Prompt

The deliverable. It must stand alone without the page: the task, the chosen direction described in words (layout, hierarchy, tone, components), the prototype's `DISCOVERY_DIR` path as the visual reference for the plan, and what still needs deciding. When `DESCRIPTION` is a prior pass's improved prompt, carry its constraints forward — enrich them with the chosen direction, never drop them. Always end it with the chain line `Worktree: .claude/worktrees/<slug>` so the next pass continues in place.

## Report

```text
🎨 Prototypes Ready

Mode: <directions | mockup>
Page: <published URL — or local path (publish skipped)>
Worktree: .claude/worktrees/<slug>
Prototype file: <DISCOVERY_DIR path — reference it in the plan prompt>

Improved prompt (baseline — the page's copy-as-prompt refines it with your reactions):

<the improved prompt>

Next (<one-line reason for the recommended hop>):
/harness-layer:<harness-interview | harness-plan> "<improved prompt>"
```
