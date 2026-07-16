---
name: cpo-prd-standard
description: Product Requirements Document structure and quality bar for Soriza client engagements — the PRD sections (overview, goals and measurable success metrics, users and personas, scope and non-goals, user stories with acceptance criteria, functional requirements per feature or section, content requirements, technical constraints, risks, open questions), the traceability quality bar, and how each PRD section maps from the locked discovery requirements. Loaded by the /c-suite cpo stage commands (cpo-prd) when drafting or reviewing a client PRD. Use when turning locked requirements into a PRD, checking a PRD for scope drift, verifying success metrics are measurable, or confirming user stories carry acceptance criteria.
autoInvoke: false
---

# CPO PRD Standard

The structure and quality bar for a Soriza client PRD. A PRD turns the locked
`discovery/requirements.md` into a buildable product definition — nothing more, nothing
invented. This skill is loaded by the `/c-suite cpo` stage commands; it is never
auto-invoked.

## PRD structure

Every PRD carries these sections, in order:

1. **Overview** — what we're building, for whom, and why; the business goal it serves and the one-line positioning.
2. **Goals & measurable success metrics** — the outcomes, each with a baseline, a target, a tracking method, and a timeframe.
3. **Users / personas** — the primary user types, each with their top task and primary desired action.
4. **Scope & non-goals** — what this release includes and, explicitly, what it does not; the phase boundary.
5. **User stories with acceptance criteria** — `As a <user>, I want <goal>, so that <benefit>`, each with concrete, checkable acceptance criteria.
6. **Functional requirements** — per feature or page/section: what it must do, its states, and its inputs/outputs.
7. **Content requirements** — the content each section needs, tone/voice, ownership, and any must-use messaging.
8. **Technical constraints** — mandated or forbidden platforms, hosting, integrations, performance, and accessibility standards.
9. **Risks** — what could derail the build (schedule, dependency, feasibility, data) and the mitigation.
10. **Open questions** — anything not yet resolved; the parking lot for scope that isn't locked.

## Quality bar

- **Traceable.** Every requirement traces to a locked dimension in `requirements.md`. If a
  requirement has no locked source, it is scope drift — move it to Open questions, do not
  smuggle it into the build.
- **Measurable metrics.** Each success metric has a baseline, a target, a tracking method,
  and a timeframe. "Improve engagement" is not a metric; "raise contact-form submissions
  from 5 to 15 per week within 90 days, tracked in analytics" is.
- **Testable stories.** Every user story carries acceptance criteria a reviewer can pass or
  fail. A story with no acceptance criteria is not done.
- **No scope drift.** The PRD stays inside the locked requirements. New needs that surface
  while drafting go to Open questions for the client, never silently into scope.

## How PRD sections map from requirements.md

| requirements.md dimension | PRD section(s) |
| --- | --- |
| business & goals | Overview; Goals & measurable success metrics |
| audience & users | Users / personas; Overview |
| brand & voice | Content requirements (tone/voice) |
| content & assets | Content requirements |
| structure & pages | Functional requirements (per section); User stories |
| features & functionality | Functional requirements; User stories with acceptance criteria |
| integrations & data | Functional requirements; Technical constraints |
| technical & hosting constraints | Technical constraints |
| budget & timeline | Scope & non-goals; Risks |
| success metrics | Goals & measurable success metrics |
| references & competitors | Overview (positioning); Scope & non-goals |
| legal/compliance | Functional requirements; Content requirements; Technical constraints; Risks |

## Template

Draft from `${CLAUDE_SKILL_DIR}/templates/prd.md` — it carries these sections as headings.
Cite the locked requirement behind each requirement so traceability is visible.
