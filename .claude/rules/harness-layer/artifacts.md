---
paths:
  - "specs/**/*"
---

# Pipeline Artifacts

The single home for crafting pipeline artifacts — interactive HTML pages committed
under `specs/<name>/artifacts/`. Author them for medium/complex work only; simple
plans skip them. The pipeline commands carry only a one-line pointer here.

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

- Author pages before a worktree exists (e.g. a plan's blindspot pass) in the
  session temp dir — never write into the repo outside a worktree. Write their final
  state into `specs/<name>/artifacts/` and commit with the spec folder.
- Publish each page best-effort via the Artifact tool from the file. Never use `open`
  (macOS-only; the playground skill suggests it — skip that step). On any publish
  failure: note "publish skipped" and continue — publishing never blocks the pipeline.

## Page inventory

| Stage | Page | Interaction |
| --- | --- | --- |
| Plan / blindspot pass | **Blindspot board** | One card per unknown with resolve / accept / needs-discussion controls; copy-as-prompt returns the user's dispositions to seed the grilling ledger (playground `document-critique` pattern) |
| Plan / taste route | **Design directions** | 2–4 rendered alternatives side by side with tweak controls; copy-as-prompt returns the chosen direction plus tweaks (playground `design-playground` pattern) |
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
