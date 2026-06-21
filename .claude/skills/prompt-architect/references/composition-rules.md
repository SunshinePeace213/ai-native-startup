# Composition Rules

`/prompt-architect` runs end-to-end on its own. It captures intent, picks the artifact type, drafts the artifact, runs anti-pattern review, validates outputs against test prompts via the bundled apparatus (`scripts/`, `agents/`, `eval-viewer/`), and optimizes the description for reliable triggering.

It still composes with other skills for work they do better.

## /grill-me — the on-ramp

`/grill-me` is the recommended **entry point** when the user wants rigorous interview-style intent capture before building. Two cases:

- **Case 1:** User types `/grill-me I want to create a skill for X`. `/grill-me` walks the design tree, reaches shared understanding, then suggests invoking `/prompt-architect`. Phase 1 (DESIGN) of prompt-architect detects post-grill context and skips its internal interview.
- **Case 2:** User types `Create a skill for X` cold. `/prompt-architect` auto-triggers from its description and runs an internal grill-me-style interview as Phase 1 — same one-question-at-a-time pattern, scoped to artifact-building decisions.

Both paths converge at Phase 2 (DRAFT) with the same shared understanding. Don't duplicate `/grill-me` inline — it's a separate composable skill.

## tech-company-personas — Phase 2 substitution

Call it during Phase 2 (DRAFT) when the artifact needs a persona.

### Call it when

- The artifact's quality depends on **judgment**: review, evaluation, recommendation, writing in a voice
- The domain is **tech-flavored**: software engineering, product management, DevOps, security, ML, infrastructure, data, design at tech companies
- The artifact is a subagent that benefits from a consistent persona across invocations

### Skip it when

- The artifact is **pure transformation**: format X to Y, summarize, extract. Clear instructions suffice.
- The domain is **non-tech**: legal, medical, hospitality, finance. Write a focused one-sentence role inline.
- The artifact is **trivial**: `/lint`, `/format`, `/help` — persona is bloat.

### How to call it

Runtime substitution, not a literal placeholder:

1. Recognize during drafting that the artifact needs a persona
2. Invoke `tech-company-personas` (actual skill call) with `task=` and `domain=`
3. Receive a concrete persona block (e.g., *"You are a Stripe Staff Engineer on the Payments Reliability team. You've shipped four large-scale incident postmortems in the past year and care about idempotency and graceful degradation."*)
4. Paste the returned persona verbatim into the artifact

The final artifact contains the full persona text — never a placeholder like `[Invoke tech-company-personas]`.

### Persona placement by artifact type

| Artifact | Where the persona goes |
|---|---|
| Skill | In the SKILL.md body where the workflow needs the lens — under "Approach" or "Reviewing", not always at the top |
| Command | `## Role` section, one paragraph |
| Subagent | The opening sentences of the body (system prompt) — the body *is* the persona's voice |

## frontend-design — runtime reference, not a drafting call

If the artifact produces frontend output (HTML, React, dashboards, marketing pages), the drafted artifact should **reference** `frontend-design` at *its* runtime, not have prompt-architect call it during drafting.

Include language in the drafted artifact like:

> "For visual design decisions (typography, palette, layout, motion), invoke the frontend-design skill. Avoid the 4.8 default house style (warm cream ~#F4F1EA, serif display, terracotta/amber) unless the brief fits editorial/hospitality contexts."

## Other domain skills (pdf, docx, xlsx, etc.)

If the artifact's work overlaps with an existing domain skill, the drafted artifact should reference that skill rather than reinvent its work:

> "For PDF reading, invoke the pdf-reading skill rather than parsing the PDF directly."

Keeps each artifact focused; avoids duplicate logic that drifts over time.

## Order of operations for a typical build

1. **`/grill-me`** (optional, recommended) — interview-style intent capture; reach shared understanding
2. **`/prompt-architect` Phase 1** — DESIGN: artifact type, Thariq category, persona need, hooks need (skipped if post-grill)
3. **`/prompt-architect` Phase 2** — DRAFT: pick template, apply Thariq's 9 tips. **Invoke `tech-company-personas` here** if persona warranted; paste returned persona verbatim.
4. **`/prompt-architect` Phase 3** — REVIEW: anti-patterns gate + smoke-test checklist
5. **`/prompt-architect` Phase 4** — PLACE: write artifact to correct path; create sibling workspace
6. **`/prompt-architect` Phase 5** — VALIDATE: `artifact-eval` workflow (with-artifact vs baseline + `meta-skill-grader`), then `aggregate_benchmark` + eval-viewer
7. **`/prompt-architect` Phase 6** — TRIGGER (skill/command only): `description-optimize` workflow
8. **`/prompt-architect` Phase 7** — SHIP: report deliverable, package as `.skill` if applicable

Steps 1-8 cover the full lifecycle without leaving prompt-architect after Phase 1. `/skill-creator` is no longer needed as a handoff — prompt-architect's bundled apparatus began as skill-creator's (forked, parameterized for all 3 artifact types); Phases 5–6 have since migrated to native dynamic workflows.

## What this skill does NOT do

- Generate personas from scratch → invoke `tech-company-personas`
- Provide frontend styling guidance → the drafted artifact references `frontend-design` at *its* runtime
- Provide PDF/docx/xlsx workflow guidance → the drafted artifact references the respective skills

## What it DOES do (this version)

- Drafts skills, commands, and subagents from a single workflow (3 templates)
- Runs the executable eval loop on the draft (the `artifact-eval` workflow + `meta-skill-grader`)
- Runs description optimization via the `description-optimize` workflow
- Applies Thariq's 9 tips during drafting (canonical: `thariq-principles.md`)
- Classifies against Thariq's 9 categories before drafting (`skill-categories.md`)
- Enforces the 4.8 anti-pattern checklist (`anti-patterns.md`)
- Composes with `/grill-me`, `tech-company-personas`, and other domain skills
