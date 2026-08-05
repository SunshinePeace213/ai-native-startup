---
description: Runs P3 of a Soriza studio engagement — structure. Produces annotated lo-fi wireframes, the content model and copy outline, and the component inventory the handoff checks are measured against, closing on a hard gate whose sign-off must list that inventory.
argument-hint: [client/project]
model: fable
effort: xhigh
disable-model-invocation: true
hooks:
  Stop:
    - hooks:
        - type: command
          command: uv run --script "$CLAUDE_PROJECT_DIR"/.claude/hooks/check_gate_signoff.py p3
---

# P3 — Structure

Decide what is on each page and in what order, and what the real content is — still without a visual direction. The phase's load-bearing output is `structure/inventory.md`: the complete list of components P6's matrix and contrast checks quantify over. The client signs it here, which is what stops P6 from writing its own denominator.

## Variables

PROJECT: $1 — the engagement, as `client/project`
PROJECT_DIR: `$(git rev-parse --show-toplevel)/clients/$1/`
IDENTITY: `$(git rev-parse --show-toplevel)/.claude/rules/studio-layer/studio-identity.md` — studio, voice, letterhead, sign-off shape
ARTIFACT_RULES: `$(git rev-parse --show-toplevel)/.claude/rules/studio-layer/client-artifacts.md` — craft, palette source, and publish rules

## Instructions

- No `PROJECT` → stop and ask for it as `client/project`. P2 must be signed.
- `PROJECT` must be exactly two segments, neither starting with `.` nor containing another `/` — anything else can write outside `clients/`. Reject it the same way and ask again.
- Read `IDENTITY` and `ARTIFACT_RULES` before authoring anything.
- Write only under `PROJECT_DIR`. `clients/` is gitignored — never stage, commit, or push client files.
- Spawn `studio-ux-architect` and `studio-content-strategist` as ordinary subagents, one level deep. Never teammates.
- Structure only: no colour, type, or imagery decisions — those are P4's.
- Only you talk to the client; a subagent cannot.

## Workflow

1. Spawn `studio-ux-architect` for `structure/wireframes.md` — annotated lo-fi, one per template, each annotation saying what the region is for and why it sits there.
2. Spawn `studio-content-strategist` for `structure/content-model.md` (the content types, their fields, and what varies) and `structure/copy-outline.md` (what each section actually says, in outline).
3. Spawn `studio-ux-architect` again for `structure/inventory.md`, enumerated from the wireframes and the content model — every component, not the interesting ones.
4. Walk the wireframes and the inventory with the client and amend from what comes back.
5. Take the signature into `sign-off/p3.md` per `IDENTITY`, listing `structure/inventory.md` as an artifact row alongside the wireframes, each with the `sha256sum` of its current content.
6. Report.

## The component inventory

```markdown
| Component | Breakpoints | Colour tokens used |
| --- | --- | --- |
| PrimaryButton | mobile, desktop | `--accent`, `--on-accent` |
| SearchResults | mobile, desktop | `--text`, `--bg` |
```

`check_states_matrix.py` needs a matrix row for every component × breakpoint pair listed here and `check_contrast.py` needs every colour token here to appear in a checked pair, so an incomplete inventory is a design measured against less than itself. Over-declaring costs work; under-declaring hides it. After this signature it changes only through a change order and a re-signature — the p6 gate re-hashes the file against what `sign-off/p3.md` recorded.

## Gate — hard

The Stop hook blocks the phase until `sign-off/p3.md` has a filled Approver and Date, every artifact row resolves and still matches its SHA-256, and `structure/inventory.md` exists, is non-empty, and appears in that table. It resolves the project from the session cwd, or the sole project under `clients/`, so with several projects open run this phase from inside `PROJECT_DIR`.

## Report

```text
🧱 P3 Complete — <client>/<project>

Signed: sign-off/p3.md — <approver>, <date>
Documents: structure/wireframes.md · content-model.md · copy-outline.md · inventory.md
Inventory: <N> components × <M> breakpoints — signed at <sha256 prefix>

Next: /studio-layer:p4-art-direction <client>/<project>
```
