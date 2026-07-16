---
description: Produce the six-file design package (PM + UX + UI personas), gate it through the Design Lead, and open the engagement PR; Workflow 2 of the c-suite CPO pipeline
argument-hint: <client-slug>
---

# CPO Brief

Turn the approved PRD into the six-file design-brief package a human designer can run with,
gate it through `DESIGN_LEAD` (Daniel Osei), then hand off. Deploy `PM`, `UX_DESIGNER`, and
`UI_DESIGNER` against the `cpo-design-standard` skill — parallel where file-disjoint,
Jonas→Yuki sequenced on the shared files. Real mode opens exactly one engagement PR that
closes the issue; fixture mode commits on the hosting branch. Workflow 2.

## Variables

CLIENT_SLUG: $1 — engagement slug; same rule as intake
DESIGN_STANDARD_SKILL: `${CLAUDE_PROJECT_DIR}/.claude/skills/cpo-design-standard/SKILL.md`
TEMPLATE_PROJECT_BRIEF: `${CLAUDE_PROJECT_DIR}/.claude/skills/cpo-design-standard/templates/project-brief.md`
TEMPLATE_SITEMAP: `${CLAUDE_PROJECT_DIR}/.claude/skills/cpo-design-standard/templates/sitemap-and-flows.md`
TEMPLATE_SECTION_BRIEFS: `${CLAUDE_PROJECT_DIR}/.claude/skills/cpo-design-standard/templates/section-briefs.md`
TEMPLATE_COPY_DECK: `${CLAUDE_PROJECT_DIR}/.claude/skills/cpo-design-standard/templates/copy-deck.md`
TEMPLATE_BRAND_INPUTS: `${CLAUDE_PROJECT_DIR}/.claude/skills/cpo-design-standard/templates/brand-inputs.md`
PM: `cpo-pm` — Ethan Park
UX_DESIGNER: `cpo-ux-designer` — Jonas Weber
UI_DESIGNER: `cpo-ui-designer` — Yuki Tanaka
DESIGN_LEAD: `cpo-design-lead` — Daniel Osei
LESSONS_FILE: `.claude/rules/c-suite/cpo-lessons.md`

## Instructions

- **Preflight.** The PRD must be approved — an `approved` verdict report exists under
  `products/<client-slug>/prd/reviews/` — else STOP. If any stage is `stale`, get explicit
  user confirmation (AskUserQuestion) before proceeding.
- **Validate the slug** with intake's rule `^[a-z0-9][a-z0-9-]{0,38}[a-z0-9]$` (fixture
  `_example-` exception) before any side effect, and double-quote every interpolation.
- **Every delegation brief** carries `DESIGN_STANDARD_SKILL` plus the exact template paths
  that persona drafts from, and instructs the persona to Read `DESIGN_STANDARD_SKILL` FIRST
  — the complete fallback when `skills:` preloading is unavailable.
- **Wireframes are lo-fi, grayscale, self-contained** — inline CSS only, no external
  reference of any kind (no CDN, web font, remote image, or URL), so every wireframe opens
  offline.
- The `cpo-design-standard` skill holds the section catalog, wireframe conventions, and the
  Design-Lead checklist. Deliverables stay professional client-grade prose; persona names
  sign reports only.

## Workflow

1. **Preflight and validate.** PRD-approved gate + slug validation per Instructions. STOP
   on any failure.
2. **Draft the package — wave one (parallel, file-disjoint).**
   - Deploy `PM` (Ethan Park): `design/project-brief.md` (structure) and
     `design/copy-deck.md`, brief carrying `TEMPLATE_PROJECT_BRIEF` and `TEMPLATE_COPY_DECK`.
   - Deploy `UX_DESIGNER` (Jonas Weber): `design/sitemap-and-flows.md`, the structural
     skeleton of `design/section-briefs.md`, and one lo-fi `design/wireframes/<page>.html`
     per page, brief carrying `TEMPLATE_SITEMAP` and `TEMPLATE_SECTION_BRIEFS`.
3. **Draft the package — wave two (`UI_DESIGNER`, after wave one).** Deploy `UI_DESIGNER`
   (Yuki Tanaka): `design/brand-inputs.md`, the visual-direction section appended to
   `design/project-brief.md`, and the visual-guidance notes added into
   `design/section-briefs.md` — Jonas writes the section-brief structure first, Yuki adds
   visual guidance after; brief carrying `TEMPLATE_BRAND_INPUTS` and `TEMPLATE_PROJECT_BRIEF`.
4. **Design-Lead gate.** Deploy `DESIGN_LEAD` (Daniel Osei) to review the full six-file
   package against the design-standard checklist. Route any blocking finding back to the
   owning persona ONCE, then re-review.
5. **Exit per mode.** On approval run the lessons check and record `lessons=<result>` in
   the `brief-run` log (`none` allowed).
   - **Real mode:** set `engagement: handed-off`, update the real trail, commit with a
     `Refs #N` footer, push the explicit engagement refspec, open exactly ONE engagement PR
     with `Closes #N` in its body, and record its URL in the ledger. Create no issue comment
     or label.
   - **Fixture mode:** create no issue, comment, label, or PR and run no `gh` action; set
     `engagement: handed-off`; keep `issue: none`, `branch: none`, `PR: none`; commit on the
     recorded hosting branch WITHOUT `Refs #N` or push; record the commit SHA in the
     `brief-run` log.

## Trail contract

`Real trail: issue=existing; comments=none; labels=none; commit=Refs #N; push=engagement branch; PR=open once`
`Fixture trail: issue=none; comments=none; labels=none; commit=current branch + recorded SHA; push=none; PR=none`

## Report

Print: the mode, the engagement folder, the six design files by name, the Design-Lead
verdict, the `brief` stage state and `engagement: handed-off`, the recorded `brief-run` log
line, and — real mode — the engagement PR URL.
