---
paths:
  - "specs/**/*"
---

# Pipeline Artifacts

The single home for crafting pipeline artifacts — interactive HTML pages under
`specs/<slug>/`: discovery pages (unknowns, brainstorm, prototypes, interview) in
`discovery/`, plan/build/review pages in `artifacts/`. All are committed in the
chain's worktree; nothing is pushed until the plan's first push. Author pipeline
pages for medium/complex work only; simple plans skip them. The pipeline commands
carry only a one-line pointer here.

## Craft

- Before authoring any page, invoke the `frontend-design` skill (visual direction)
  then the `playground` skill (interactive mechanics) via the Skill tool. Follow
  them there — do not re-summarize either here.
- Each page is one self-contained HTML file: inline CSS/JS, zero external
  dependencies.
- Each page is two-way: interactive controls + a live preview + a **copy-as-prompt**
  output block with a copy button. The prompt is natural language (not a value
  dump), mentions only non-default choices, and carries enough context to act on
  without seeing the page.

## Palette — Warm Neutral

Commit every page to this single light look (it overrides the playground skill's
dark-theme default).

| Role | Hex |
| --- | --- |
| Background | `#FAF8F5` |
| Surface | `#F0EDE5` |
| Border | `#D4CFC7` |
| Text | `#2C2825` |
| Accent | `#B8602A` |
| Muted | `#8A837A` |

## Publish

- Discovery pages are authored under `specs/<slug>/discovery/` inside the chain
  worktree and committed by their pass (`📝 docs(discovery): …`, no issue footer).
  The interview page is redeployed to the same URL every round.
- Plan and build pages are authored in the same worktree under
  `specs/<slug>/artifacts/` and committed with a `Refs #N` footer; the
  implementation-plan page is authored after the Codex gate settles, from the
  final spec state.
- Publish each page best-effort via the Artifact tool from the file. Never use `open`
  (macOS-only; the playground skill suggests it — skip that step). On any publish
  failure: note "publish skipped" and continue — publishing never blocks the pipeline.

## Page inventory

| Stage | Page | Interaction |
| --- | --- | --- |
| Unknowns pass / codebase gap | **Unknowns board** | One card per codebase unknown with resolve / accept / needs-discussion controls; copy-as-prompt assembles the improved plan prompt from the dispositions (playground `document-critique` pattern) |
| Unknowns pass / domain gap | **Vocabulary explainer** | Mental-model steps, a vocabulary ladder, the quality bar, and payoff prompts; copy-as-prompt returns a vocabulary-rich improved plan prompt |
| Brainstorm pass | **Intervention ladder** | ~10 intervention cards ordered cheapest → most ambitious, each with a size badge (S/M/L/XL), real code pointers, an impact line, and a resonate toggle; copy-as-prompt returns the resonating picks as the refined plan prompt |
| Prototypes pass / mockup | **Mockup** | A single throwaway mock of the feature with realistic fake data; copy-as-prompt returns the user's reactions and requested changes |
| Prototypes pass / directions | **Design directions** | 2–4 rendered alternatives side by side with tweak controls; copy-as-prompt returns the chosen direction plus tweaks (playground `design-playground` pattern) |
| Interview pass | **Interview rounds** | One card per open question (2–4 option chips, the recommended pick badged, free text per card), an accept-all-recommendations control, and the coverage ledger as a resolved/open/N/A sidebar; copy-as-prompt returns the round's answers; redeployed to the same URL each round |
| Plan / spec reader | **Implementation plan** | Spec content ordered by likelihood-of-tweaking — volatile decisions first, each with its chosen path and a toggled alternative; build order next; mechanical work collapsed last; copy-as-prompt offers ready-made tweak prompts that trigger a plan revision |
| Plan / reference port | **Reference map** | Side-by-side reference↔target code pairs with linked hover notes, a preserved/changed/dropped behavior table, and an edge-case table; copy-as-prompt returns "semantics confirmed" or per-row corrections |
| Build / checkpoints | **Deviations board** | The `implementation-notes.md` deviations as cards with accept / needs-follow-up controls; copy-as-prompt returns dispositions; linked from the PR |
| Review / completion | **Findings page** | Diff excerpts with margin annotations, findings color-coded by severity; linked from the PR's Review Reports section |

## Beyond the inventory

These patterns extend the inventory — when work matches a shape, propose the page; the craft, palette, and copy-as-prompt rules above always apply.

| Shape | Pattern |
| --- | --- |
| Triaging many items (findings, dataset rows, feedback) | Approve/reject/tag cards that export the dispositions |
| A tunable decision (design tokens, config values, algorithm parameters) | Controls + live preview |
| Explaining code or architecture (tricky logic, module relationships) | Annotated diagram / code-map page |
| Ordering or prioritization (tickets, tasks) | Draggable board that exports the final order |
| Multi-source report (research, status, incident) | Tabbed explainer with navigation |
| Reviewing a document or spec | Inline suggestions with approve/reject/comment |

Full pattern source mirrored at `ai-docs/anthropic/html-artifacts-workflows.md`.
