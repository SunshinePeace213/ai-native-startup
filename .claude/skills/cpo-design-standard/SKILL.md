---
name: cpo-design-standard
description: Design-handoff standard for Soriza client engagements — the page-section catalog (hero, navigation, social proof, features, case study, pricing, FAQ, CTA, footer, about, contact), lo-fi grayscale offline-only wireframe conventions, the copy-deck and brand-inputs formats, and the Design-Lead six-file package-review checklist. Loaded by the /c-suite cpo stage commands (cpo-brief) when producing the design brief package or reviewing it. Use when building sitemaps, section briefs, wireframes, copy decks, or brand-input inventories for a client website, or reviewing a design package before handoff to a human designer.
autoInvoke: false
---

# CPO Design Standard

The design-handoff expertise for a client engagement. The output is a six-file package a
human designer can pick up and run with: project brief, sitemap and flows, section briefs,
copy deck, brand inputs, and lo-fi wireframes. This skill is loaded by the `/c-suite cpo`
stage commands; it is never auto-invoked.

## Section catalog

Each page is assembled from these sections. For each: what it's for, the content it needs,
and its common variants.

- **Hero** — purpose: land the primary value proposition and drive the main action above the fold. Fields: headline, subhead, primary CTA, supporting visual, optional trust cue. Variants: centered text, split text-and-image, full-bleed background, video.
- **Navigation** — purpose: reach any primary destination and the main action. Fields: logo, nav links, primary CTA, mobile menu. Variants: top bar, sticky, mega-menu, minimal hamburger.
- **Social proof** — purpose: reduce risk with third-party validation. Fields: logos, testimonials, ratings, counts. Variants: logo strip, testimonial cards, single featured quote, stats row.
- **Features** — purpose: explain what it does and why it matters. Fields: feature title, description, icon or visual, optional link. Variants: grid, alternating rows, tabbed, accordion.
- **Case study** — purpose: prove outcomes with a concrete story. Fields: subject, challenge, approach, result/metric, visual. Variants: single deep-dive, carousel, metric-led summary.
- **Pricing** — purpose: present cost and tiers so visitors self-qualify. Fields: plan name, price, feature list, CTA, highlight flag. Variants: tiered columns, single price, monthly/annual toggle, comparison table.
- **FAQ** — purpose: resolve objections and cut support load. Fields: question, answer, optional category. Variants: accordion, two-column list, grouped by topic.
- **CTA** — purpose: a focused prompt to take the next step. Fields: headline, supporting line, button, optional secondary action. Variants: banner, centered block, split with image.
- **Footer** — purpose: secondary navigation, legal, and contact catch-all. Fields: nav columns, legal links, contact, social, newsletter, copyright. Variants: minimal, multi-column, fat footer with newsletter.
- **About** — purpose: build trust through story, people, and mission. Fields: mission, story, team, values, milestones. Variants: narrative, team grid, timeline.
- **Contact** — purpose: let visitors reach the business. Fields: form fields, contact details, map/location, hours, response expectation. Variants: form-only, form plus details, form plus map.

## Wireframe conventions

Wireframes are lo-fi HTML, one file per page/screen, that a designer reads for layout — not
look:

- **Grayscale only.** No brand color, no imagery styling — greys, boxes, and type weight
  carry the hierarchy. Color is the human designer's job, not the wireframe's.
- **Layout and hierarchy only.** Boxes for regions, real section labels, placeholder or
  greeked copy, labeled gray boxes for images.
- **Self-contained and offline.** Inline CSS only; no external reference of any kind — no
  CDN, no web fonts, no remote images, no links to URLs. Placeholder images are inline SVG
  or a labeled gray `div`. This is what lets a wireframe open offline with no network.
- **Annotated.** HTML comments (`<!-- note: ... -->`) explain intent, interactions, and
  which section brief and copy-deck entry each region draws from.

## Copy-deck format

One entry per section per page, keyed to the sitemap and section briefs. For each section,
list every text string it needs — headline, subhead, body, CTA label, microcopy, image alt
text — and mark each string's source: `client-provided`, `to-write`, or `placeholder`. Copy
must match the PRD's content requirements and tone; it never invents claims beyond the PRD.

## Brand-inputs format

Two parts:

- **Inventory** — the brand tokens and assets the client provided: logo files, color palette
  (hex), typography, imagery, tone/voice notes, existing guidelines.
- **Gap list** — everything the human designer still needs, stated explicitly so nothing is
  silently invented. Each gap: what's missing, why it's needed, and who can provide it.

## Design-Lead package-review checklist

The Design Lead reviews the full package against these, returning blocking findings or
approval:

1. **Completeness** — all six files present: `project-brief.md`, `sitemap-and-flows.md`, `section-briefs.md`, `copy-deck.md`, `brand-inputs.md`, and at least one wireframe page under `design/wireframes/`.
2. **Internal consistency** — sitemap pages, section briefs, wireframes, and copy deck agree; no orphan sections and no missing pages.
3. **Wireframes open offline** — every wireframe is self-contained and grayscale with no external reference or URL; it renders fully with no network.
4. **Copy matches the PRD** — the copy deck reflects the PRD's content requirements and tone; no claims beyond the PRD.
5. **Brand gaps explicit** — `brand-inputs.md` lists every missing token or asset as a gap for the human designer; nothing critical is silently assumed.
6. **Traceable** — every section traces back to a PRD requirement; no scope beyond the PRD.

## Templates

Build the package from these bundled files:

- `${CLAUDE_SKILL_DIR}/templates/project-brief.md` — the project brief, including a design-constraints section.
- `${CLAUDE_SKILL_DIR}/templates/sitemap-and-flows.md` — the sitemap and primary flows as a mermaid skeleton.
- `${CLAUDE_SKILL_DIR}/templates/section-briefs.md` — per page, per section: purpose, content, chosen variant, visual guidance.
- `${CLAUDE_SKILL_DIR}/templates/copy-deck.md` — every text string per section, with its source.
- `${CLAUDE_SKILL_DIR}/templates/brand-inputs.md` — the token/asset inventory and the gap list.

Wireframes have no template — hand-author one lo-fi HTML file per page under
`design/wireframes/` following the wireframe conventions above.
