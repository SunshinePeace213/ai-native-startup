# Section Briefs — Bluebird Bakery

Source: prd/prd.md + sitemap-and-flows.md. One block per page; within each page, one entry
per section drawn from the cpo-design-standard section catalog (or the closest catalog
cousin, noted where a section is bakery-specific).

**Wave one (this file, Jonas Weber, UX Designer):** structure only — purpose, content
fields, chosen variant, and the PRD/user-story trace. Visual guidance is Yuki Tanaka's
(UI Designer) pass, filled in during wave two once brand inputs (logo, palette use,
imagery direction) are assembled.

The footer section is identical on every page (shared nav, legal links, contact). It is
specified once, under Home, and referenced by name on every later page rather than
repeated verbatim.

---

## Page — Home

Section order: Hours-location strip → Hero → Fresh-today highlight → Cake CTA → Our Story
teaser → Footer (the strip sits immediately under the shared nav, above the hero, per
US-3 AC1).

### Home / Hours-location strip

- Purpose: Give regulars immediate hours/location visibility at the very top of the page,
  without digging, echoing the competitive cue of "hours prominent at the top."
- Content fields: today's hours (CMS-editable), address, one-line parking note, link through
  to Visit Us for full detail.
- Variant: Contact catalog, lightweight info-strip subset (hours + address only, no form).
- Visual guidance: Compact, scannable strip — treat as a lightweight info bar, not a
  full section; sits directly under the nav, above the hero, but deliberately lower visual
  weight than the hero and cake CTA so it informs without competing for primary attention.
- Traces to: US-3 AC1; PRD §1 Overview (references & competitors), §6 Home.

### Home / Hero

- Purpose: Land the visitor in Bluebird's warm, scratch-made, neighborhood identity and set
  up navigation to the rest of the site — the first read for the "new/visiting" persona.
- Content fields: headline (brand intro; "since 2018" optional per PRD §7), subhead, one
  client-supplied photo (loaves or shop interior; no stock imagery), optional trust cue.
- Variant: Hero catalog, split text-and-image (stacks to a single column on mobile).
- Visual guidance: Heaviest visual weight on the page — the photo half should take at
  least half the desktop viewport, collapsing above the headline on mobile. One real, warm
  photo, boldest type on the page for the headline, and generous whitespace around the
  text block so it reads calm, not crowded.
- Traces to: US-4 AC1, AC3; PRD §1 Overview (positioning); §7 Home content.

### Home / Fresh-today highlight

- Purpose: Give regulars an at-a-glance read of what's fresh today, and surface the
  CMS-editable daily/seasonal specials on the page regulars land on most.
- Content fields: heading and one-line body (static, to-write), a clearly separate
  CMS-editable specials text field (daily/seasonal specials, staff-updated, no developer
  needed), optional small photo, link to the full Menu page.
- Variant: Features catalog, single highlight card.
- Visual guidance: Quiet, secondary weight — a single compact card noticeably smaller
  than the hero above and the cake CTA below; set the CMS-editable specials text field
  visibly apart from the static heading/body (its own bordered treatment) so it reads as
  the one part of this card that changes daily; keep any photo small and secondary to the
  text so it doesn't compete with the cake CTA for attention.
- Traces to: US-5 AC2; US-6; PRD §6 Menu (specials), §6 Simple-content editing (CMS).

### Home / Cake CTA

- Purpose: The PRD's must-have — route cake customers to Custom Cakes and its inquiry form
  in a single click/tap, the site's primary desired action.
- Content fields: headline naming custom cakes, one supporting line, one button, optional
  supporting visual (a decorated-cake photo).
- Variant: CTA catalog, banner or centered block.
- Visual guidance: Second-heaviest weight on the page after the hero — this is the
  site's single most important action, so give the button strong size and contrast; if a
  cake photo is used, let it reinforce warmth without competing with the button for
  attention.
- Traces to: US-1 AC1 (primary); PRD §1 Overview (positioning), §6 Home.

### Home / Our Story teaser

- Purpose: Tease the since-2018, warm/personal story for the new-visitor persona (US-4),
  linking through to the full Our Story page before the footer closes the page.
- Content fields: heading, one-line teaser body, link to Our Story.
- Variant: About catalog, teaser variant (short heading + one line + link — not the full
  narrative, which lives on Our Story).
- Visual guidance: Light, quiet weight — noticeably lighter than the hero and cake CTA
  above it; a short heading and single line of warm, personal text with generous
  whitespace, closing out the page's selling sections before the footer.
- Traces to: US-4 AC1; PRD §1 Overview (differentiator), §7 Our Story.

### Home / Footer

- Purpose: Secondary navigation, legal, and contact catch-all, present unchanged on every
  page.
- Content fields: nav links (Menu, Our Story, Custom Cakes, Visit Us), legal links (Privacy
  Policy, Terms of Use), contact info, Google Business Profile link-out.
- Variant: Footer catalog, minimal footer (no newsletter — deferred per §4 non-goals; no
  social feed required — Instagram embed is a non-launch nice-to-have).
- Visual guidance: Low visual weight, dense but calm — small type, generous spacing
  between the nav/legal/contact groupings, no competing color or imagery; it should feel
  quietly complete, never like another selling section.
- Traces to: §4 Scope & non-goals; §6 Legal pages; §8 Google Business Profile (link-out).

---

## Page — Menu

### Menu / Intro

- Purpose: Frame the page in one line before the listing; keep tone plain and appetizing.
- Content fields: short intro line, optional small photo.
- Variant: Hero catalog, minimal text-only header (no CTA).
- Visual guidance: Minimal, quiet header — a short line of text only, no strong visual
  weight; sets a plain, appetizing tone without competing with the menu listing below.
- Traces to: PRD §7 Menu (tone: plain and appetizing).

### Menu / Menu listing

- Purpose: Display the client-provided menu — a cleaned-up version of the in-shop
  chalkboard.
- Content fields: category headers with item name/price/short description, as supplied by
  the client; edited via CMS or by the agency on request.
- Variant: Features catalog, grid or list grouped by category.
- Visual guidance: The heaviest section on the page — strong weight contrast between
  category headers and item rows, with generous spacing between categories so the list
  stays scannable even before real content arrives.
- Traces to: US-5 AC1; PRD §6 Menu; §9 Risks (menu content on the critical path — build with
  placeholders while awaiting client content).

### Menu / Specials highlight

- Purpose: Surface daily/seasonal specials distinctly from the static menu, and keep them
  editable without a developer.
- Content fields: specials text (CMS-editable), effective date or season note.
- Variant: Features catalog, single callout/banner variant.
- Visual guidance: A distinct callout band (border or shading) clearly separated from
  the static menu list, so it reads as "today, this changes" without competing with the
  main listing for attention.
- Traces to: US-5 AC2; US-6 AC1; PRD §6 Menu, §6 Simple-content editing (CMS).

### Menu / Footer

- Purpose / content / variant: same as Home / Footer (shared across every page).
- Visual guidance: Same treatment as Home / Footer — low weight, consistent across
  pages.
- Traces to: same as Home / Footer.

---

## Page — Our Story

### Our Story / Hero-intro

- Purpose: Open the story page with the warm/homey framing, distinct from Home's brand
  hero.
- Content fields: headline, one-line subhead.
- Variant: Hero catalog, centered text variant.
- Visual guidance: Quiet, centered opener — text-only, generous whitespace above and
  below; noticeably lighter weight than Home's hero, since this page's visual weight
  belongs to the narrative and photos below.
- Traces to: PRD §7 Our Story (tone: warm/personal).

### Our Story / Narrative

- Purpose: Tell the since-2018, sourdough-starter, hand-decorated-cakes story that
  differentiates Bluebird from an impersonal supermarket bakery.
- Content fields: story body copy (agency-drafted, Maria approves), a short personal note
  attributed to Maria.
- Variant: About catalog, narrative variant.
- Visual guidance: Primary reading weight on the page — comfortable line length and
  generous paragraph spacing for a warm, personal read; set Maria's personal note visually
  apart (a light rule or indent) so it reads like a handwritten aside.
- Traces to: US-4 AC1; PRD §1 Overview (differentiator), §7 Our Story.

### Our Story / Photo highlights

- Purpose: Ground the story in real client-supplied photos — no stock imagery is an
  explicit anti-reference.
- Content fields: 3-6 client-supplied photos of loaves, cakes, and shop interior, each with
  a caption/alt text.
- Variant: About catalog, photo-grid variant (repurposed from "team grid" for
  product/place photos).
- Visual guidance: Let the real photos carry the emotional weight here — generous
  whitespace between images rather than a tight grid, so each loaf/cake/interior shot
  breathes and reads as authentic, not stock-catalog.
- Traces to: US-4 AC3; PRD §7 Content requirements (assets and ownership — photography).

### Our Story / Footer

- Purpose / content / variant: same as Home / Footer (shared across every page).
- Visual guidance: Same treatment as Home / Footer — low weight, consistent across
  pages.
- Traces to: same as Home / Footer.

---

## Page — Custom Cakes

### Custom Cakes / Intro

- Purpose: Frame how to inquire and reassure the customer the form reaches Maria directly —
  the direct opposite of a buried Instagram DM.
- Content fields: headline, one how-it-works line.
- Variant: Hero catalog, minimal text-only variant.
- Visual guidance: Short, reassuring header — quiet visual weight that sets up trust
  before the gallery; no heavy visual competition with the gallery or form below.
- Traces to: PRD §1 Overview (positioning); §6 Custom Cakes.

### Custom Cakes / Gallery by size/style

- Purpose: Show past-cakes examples by size and style so the customer knows what's possible
  before filling out the form.
- Content fields: client-supplied past-cakes photos, grouped/labeled by size and style, with
  captions.
- Variant: Features catalog, grid variant grouped by size/style tag.
- Visual guidance: Second-heaviest weight on the page after the form — real photos at a
  generous size so size/style read at a glance; group with clear labels and spacing by
  size/style rather than one undifferentiated grid.
- Traces to: US-2 AC1, AC2, AC3; PRD §6 Custom Cakes.

### Custom Cakes / Inquiry form

- Purpose: The launch feature — capture everything Maria needs to scope a cake or catering
  order and route it reliably to her alone.
- Content fields: event type, event date, size/servings, flavor(s), design description,
  allergy/dietary notes (sensitive — Maria-only), name, email and/or phone. States: Empty,
  Validation error, Submitting, Success, Failure (see sitemap-and-flows.md Flow 1).
- Variant: Contact catalog, form-only variant, with explicit per-state handling per PRD §6.
- Visual guidance: The single heaviest section on the page — the launch feature. Strong
  separation from the gallery above (clear heading, generous top spacing), fields grouped
  with breathing room; give empty/error/submitting/success/failure each a visually distinct,
  unambiguous treatment so the customer always trusts what just happened.
- Traces to: US-1 (all acceptance criteria); PRD §6 Cake inquiry form; §8 data destinations
  (sensitive allergy/dietary data, Maria-only routing).

### Custom Cakes / Expectation-setting note

- Purpose: Set the reply-time and privacy expectation so the customer trusts the form —
  directly supports the "never heard back" goal in PRD §2.
- Content fields: short reassurance copy (expected response time, mention of the
  auto-confirmation email, note that allergy/dietary details stay private to Maria).
- Variant: CTA catalog cousin — small supporting text block adjacent to the form (not a
  full banner).
- Visual guidance: Small, quiet supporting text directly beside or below the form —
  noticeably lighter weight than the form itself; reads as reassurance, not another call
  to action.
- Traces to: PRD §2 Goals & metrics (end missed-inquiry complaints); §6 Cake inquiry form
  (sensitive data handling).

### Custom Cakes / Footer

- Purpose / content / variant: same as Home / Footer (shared across every page).
- Visual guidance: Same treatment as Home / Footer — low weight, consistent across
  pages.
- Traces to: same as Home / Footer.

---

## Page — Visit Us / Contact

### Visit Us / Intro

- Purpose: Brief framing line before the hours/location detail.
- Content fields: headline.
- Variant: Hero catalog, minimal text-only variant.
- Visual guidance: Minimal text-only header, low visual weight, quick framing before
  the hours/location detail below.
- Traces to: PRD §6 Visit Us / Contact.

### Visit Us / Hours-location-parking

- Purpose: Present hours, location, and parking prominently — the page's core job for the
  regulars persona.
- Content fields: full hours table (CMS-editable), address, parking instructions.
- Variant: Contact catalog, form-plus-details variant (details only — the inquiry form lives
  on Custom Cakes, not here).
- Visual guidance: The heaviest section on this page — give hours, address, and parking
  clear individual visual weight rather than one dense paragraph, with enough spacing
  between the three that a regular can scan straight to the one fact they need.
- Traces to: US-3 AC1, AC2; PRD §6 Visit Us / Contact.

### Visit Us / Contact details

- Purpose: Give visitors a way to reach the bakery directly, separate from the cake inquiry
  form.
- Content fields: phone, email, social handles if supplied by the client.
- Variant: Contact catalog, details-block variant.
- Visual guidance: Lighter weight than the hours/location block above — a simple, quiet
  details list, not a competing section.
- Traces to: PRD §6 Visit Us / Contact.

### Visit Us / Google link-out

- Purpose: Send visitors to the Google Business Profile for directions and reviews —
  link-out only, no embedded map.
- Content fields: one link/button label (e.g. "View on Google"); no destination URL is
  represented in design assets — set by the developer/CMS at build time.
- Variant: CTA catalog, small secondary button.
- Visual guidance: Small secondary button, clearly lower visual weight than any
  cake-inquiry CTA elsewhere on the site — this is a supporting exit action, not the
  page's main task.
- Traces to: US-3 AC3; PRD §8 Technical constraints (integrations — Google Business Profile,
  link-out only).

### Visit Us / Footer

- Purpose / content / variant: same as Home / Footer (shared across every page).
- Visual guidance: Same treatment as Home / Footer — low weight, consistent across
  pages.
- Traces to: same as Home / Footer.

---

## Page — Privacy Policy

### Privacy Policy / Legal header

- Purpose: Title and last-updated framing for a legal page.
- Content fields: page title, effective/last-updated date.
- Variant: Hero catalog, minimal text-only variant (no CTA, no image).
- Visual guidance: Minimal, quiet — title and date only, no imagery; low visual weight
  befitting a legal utility page.
- Traces to: PRD §6 Legal pages.

### Privacy Policy / Legal body

- Purpose: Disclose that the inquiry form collects contact details and sensitive
  allergy/dietary notes handled privately by Maria, plus standard brochure-site privacy
  terms.
- Content fields: full privacy policy body copy (agency-drafted, Maria sign-off).
- Variant: static long-form text (no catalog variant; closest cousin is the FAQ catalog's
  plain-list readability, not used verbatim here).
- Visual guidance: Plain long-form text treatment — comfortable line length and
  generous paragraph spacing for readability, no decorative elements; the quietest visual
  weight on the site, befitting a legal utility page.
- Traces to: PRD §6 Legal pages; §8 Technical constraints (data destinations — sensitive
  allergy/dietary data).

### Privacy Policy / Footer

- Purpose / content / variant: same as Home / Footer (shared across every page).
- Visual guidance: Same treatment as Home / Footer — low weight, consistent across
  pages.
- Traces to: same as Home / Footer.

---

## Page — Terms of Use

### Terms of Use / Legal header

- Purpose: Title and last-updated framing for a legal page.
- Content fields: page title, effective/last-updated date.
- Variant: Hero catalog, minimal text-only variant (no CTA, no image).
- Visual guidance: Same treatment as Privacy Policy / Legal header — minimal, quiet,
  low visual weight.
- Traces to: PRD §6 Legal pages.

### Terms of Use / Legal body

- Purpose: Publish standard brochure-site terms of use, agency-drafted with Maria's
  sign-off, on the same approval flow as site copy.
- Content fields: full terms-of-use body copy.
- Variant: static long-form text.
- Visual guidance: Same plain long-form treatment as Privacy Policy — comfortable line
  length, generous paragraph spacing, no decorative elements; the quietest visual weight on
  the site.
- Traces to: PRD §6 Legal pages.

### Terms of Use / Footer

- Purpose / content / variant: same as Home / Footer (shared across every page).
- Visual guidance: Same treatment as Home / Footer — low weight, consistent across
  pages.
- Traces to: same as Home / Footer.
