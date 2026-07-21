---
description: Pre-plan discovery pass — finds your unknown unknowns in the codebase and/or teaches the domain's vocabulary, then hands back an improved prompt ready for the next pass
argument-hint: [description]
model: fable
effort: high
disable-model-invocation: true
disallowed-tools: Task, EnterPlanMode
---

# Harness Unknowns

Turn a blind spot into a better prompt. Before any spec exists, scan for what the user doesn't know they don't know — in this codebase, in the domain, or both — explain each finding, and hand back an improved prompt for the next pass. Discovery only: the interactive page lives in `DISCOVERY_DIR` inside the chain worktree, committed locally and published best-effort; the improved prompt is the hand-off.

## Variables

DESCRIPTION: $1
DISCOVERY_DIR: `specs/<slug>/discovery/` — the chain's committed discovery home inside the worktree
ARTIFACT_RULES: `.claude/rules/harness-layer/artifacts.md` — craft, palette, and publish rules for the page

## Instructions

- **DISCOVERY ONLY** — no spec files, no issues, no pushes; write only under `DISCOVERY_DIR`. The improved prompt travels by copy-paste.
- If no `DESCRIPTION` is provided, stop and ask the user for one.
- Worktree: when `DESCRIPTION` carries a `Worktree:` line, `EnterWorktree(path: ...)` into it; otherwise derive a kebab-case `<slug>` and `EnterWorktree(name: "<slug>")`. Never write outside the worktree.
- Classify the gap (see `Modes`) and run the matching pass; when both fire, one page carries both sections.
- Ground every finding in what you actually read — real files, real conventions, real history. A finding that could be written without opening the codebase is filler; cut it.
- Do not interview the user or lock decisions; this pass only surfaces and explains.
- Commit the pass locally — `📝 docs(discovery): unknowns pass for <slug>`, no issue footer (no issue exists yet). Never push; the plan's first push carries the discovery commits.
- End by recommending exactly one next hop (first match wins), with the improved prompt as its input: scope still rough with several plausible interventions → `/harness-layer:harness-brainstorm`; a look-and-feel decision surfaced → `/harness-layer:harness-prototypes`; open decisions only the user can answer (including needs-discussion cards) → `/harness-layer:harness-interview`; otherwise → `/harness-layer:harness-plan`.

## Modes

- **Codebase gap** — the user knows what they want but not this code ("I've never touched the auth module"). Do a blindspot pass on the touched surface: find the unknown unknowns — landmines, unwritten conventions, relevant history (reverted attempts, half-done migrations), missing concepts — explain each one, and say how to prompt better for the implementation.
- **Domain gap** — the user knows the ask but not the field's language ("I don't know what color grading is"). Teach the domain well enough that the user understands their unknown unknowns and can prompt with real vocabulary: mental model first, then a vocabulary ladder (plain definition, mechanism, professional usage), the quality bar professionals judge by, and the payoff prompts the user can now write.
- **Both** — the description signals both gaps ("adding SSO but I've never touched the auth module"): run both passes into one page.

## Workflow

1. Parse `DESCRIPTION`; classify the gap (codebase | domain | both); enter the worktree (see Instructions).
2. Scan — read the modules the task touches plus their immediate callers, and check `git log` on those paths for reverted or abandoned attempts; for a domain gap, draw on domain knowledge and any relevant KB docs. Collect ~4–7 codebase findings (each: what it is / why it bites / what to do instead) and/or the domain's mental model, a ~6-term vocabulary ladder, and its quality bar.
3. Author the page per `ARTIFACT_RULES` into `DISCOVERY_DIR` — codebase gap → **Unknowns board** (one card per finding with resolve / accept / needs-discussion controls); domain gap → **Vocabulary explainer** (mental-model steps, vocabulary ladder, quality checklist, payoff prompts); both → both sections. The copy-as-prompt block assembles the improved prompt live from the user's dispositions and selections.
4. Publish the page best-effort via the Artifact tool; on failure note "publish skipped" and continue with the local file.
5. Commit the pass (see Instructions).
6. Report per `Report` — findings digest, the baseline improved prompt, and the hand-off line.

## Improved Prompt

The deliverable. It must stand alone without the page: restate the task with every surfaced constraint folded in as an explicit work order — what to walk through before coding, sequenced steps naming real files and real vocabulary, and where to stop for confirmation. Natural language, carrying only what the pass surfaced — no generic advice. Always end it with the chain line `Worktree: .claude/worktrees/<slug>` so the next pass continues in place.

## Report

```text
🔍 Unknowns Pass Complete

Mode: <codebase | domain | both>
Page: <published URL — or local path (publish skipped)>
Worktree: .claude/worktrees/<slug>
Findings: <one line per card / term group, concise>

Improved prompt (baseline — the page's copy-as-prompt refines it with your dispositions):

<the improved prompt>

Next (<one-line reason for the recommended hop>):
/harness-layer:<harness-brainstorm | harness-prototypes | harness-interview | harness-plan> "<improved prompt>"
```
