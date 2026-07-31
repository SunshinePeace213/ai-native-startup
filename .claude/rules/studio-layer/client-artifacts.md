---
paths:
  - "clients/**/*"
---

# Client Artifacts

Interactive pages the client reacts to — one per phase that needs a client decision.
They are authored under `clients/<client>/<project>/<phase>/` and, unlike pipeline
pages, never committed: `clients/` is gitignored.

## Craft and publish

Follow [artifacts.md](../harness-layer/artifacts.md) `## Craft` and `## Publish`
unchanged — the `frontend-design` then `playground` skills before authoring, one
self-contained HTML file, controls plus live preview plus a copy-as-prompt block, and
best-effort publishing that never blocks the phase.

Its palette lock is the one thing that does not carry over. Client pages take their
colors from the phase's palette source below, and that source is also what overrides the
playground skill's dark default.

## Palette source

Never dress a client page in the harness pipeline's Warm Neutral. Client deliverables
that look like our internal pages are the whole failure this fork exists to prevent, and
a locked table would guarantee it.

| Phase band | Colors come from |
| --- | --- |
| P0–P3 | The Soriza studio default — the studio's own brand look, since the client has picked no direction yet. |
| P4 onward | The tokens of the direction the client picked at P4, read from that project's style tile. |

## Page patterns

| Client moment | Page | Copy-as-prompt returns |
| --- | --- | --- |
| Brief review (P2) | The project and creative brief rendered statement by statement, each with approve / change / discuss controls and a free-text note. | Every statement's disposition plus the client's own rewording, so the brief is amended before it is signed. |
| Sitemap (P2) | An ordering board of the proposed pages and sections, draggable, with a keep-or-cut toggle per row. | The final order and every cut row, ready to write straight into the sitemap. |
| Art direction (P4) | The two or three directions rendered side by side on real page content, each with type and color tweak controls. | The picked direction and the tweaks asked of it — the input to the style tile whose tokens then set the palette from P4 onward. |
| Feedback triage (P5) | One card per piece of client feedback, dispositioned this round / next round / needs a change order, with the round's remaining allowance shown. | Each item's disposition, so the revision-log row and any change order are written from the client's own answer. |
