# Sitemap & Flows — Bluebird Bakery

Source: prd/prd.md (§4 Scope & non-goals, §6 Functional requirements). Every page here has a
matching entry in section-briefs.md and a wireframe under design/wireframes/ (legal pages are
covered in section-briefs.md; they have no dedicated wireframe this wave — see Notes).

## Sitemap

```mermaid
graph TD
  Home[Home]
  Menu[Menu]
  OurStory[Our Story]
  CustomCakes[Custom Cakes — gallery + inquiry form]
  VisitUs[Visit Us / Contact]
  Footer{{Footer — present on every page}}
  Privacy[Privacy Policy]
  Terms[Terms of Use]

  Home --> Menu
  Home --> OurStory
  Home --> CustomCakes
  Home --> VisitUs
  Menu --> CustomCakes
  OurStory --> CustomCakes
  CustomCakes --> VisitUs

  Home --> Footer
  Menu --> Footer
  OurStory --> Footer
  CustomCakes --> Footer
  VisitUs --> Footer
  Footer --> Privacy
  Footer --> Terms
```

## Primary user flows

### Flow 1 — Cake inquiry (primary action, US-1 + US-2)

The site's one job: get a cake customer from landing to a submitted, acknowledged inquiry.
Covers the empty, validation-error, submitting, success, and failure states from PRD §6.

```mermaid
flowchart TD
  L1[Land on Home] --> C1[Tap cake CTA - reaches Custom Cakes in one click, US-1 AC1]
  C1 --> P1[Custom Cakes page loads]
  P1 --> G1[Browse past-cakes gallery by size and style - US-2]
  G1 --> F1[Inquiry form - Empty state]
  F1 --> D1[Enter event type/date, size, flavor, design, allergy notes, contact info]
  D1 --> S1[Submit]
  S1 --> V1{Required fields and contact info valid}
  V1 -- No --> E1[Validation error - inline messages, submission blocked]
  E1 --> D1
  V1 -- Yes --> SU1[Submitting state]
  SU1 --> R1{Email delivered to Maria}
  R1 -- No --> FL1[Failure - error shown with retry path, request never silently dropped]
  FL1 --> S1
  R1 -- Yes --> OK1[Success - on-screen confirmation]
  OK1 --> OK2[Auto-confirmation email sent to customer]
```

### Flow 2 — Hours check (regular, US-3)

The secondary-but-frequent path: a regular confirming hours/location, then optionally
leaving the site for directions or reviews.

```mermaid
flowchart LR
  L2[Land on Home or Visit Us] --> H2[View hours and location block at top - US-3 AC1]
  H2 --> Q2{Need directions or reviews}
  Q2 -- No --> D2[Done - plan the visit]
  Q2 -- Yes --> GL2[Tap Google Business Profile link-out]
  GL2 --> EX2[Leaves site to Google - directions and reviews, US-3 AC3]
```

### Flow 3 — New-visitor orientation (US-4)

A supporting flow: someone who found Bluebird via Google search deciding whether to visit,
before either the hours path or the cake-inquiry path.

```mermaid
flowchart LR
  L3[Arrive via Google search - mobile] --> B3[Browse Home hero and brand story]
  B3 --> B4[Browse Our Story and Menu]
  B4 --> DEC3{Ready to visit, or order a cake}
  DEC3 -- Visit --> V3[Visit Us - hours, location, parking]
  DEC3 -- Custom cake --> CC3[Custom Cakes - gallery, then inquiry form]
```

## Notes

- **Nav is a full mesh, not a tree.** The sitemap diagram shows site hierarchy for
  readability; in practice the primary nav (in the shared header) exposes all five pages
  from every page, and the Custom Cakes CTA is reachable from Home in one click per PRD §6.
- **Footer is shared.** Every page renders the same footer with legal links (Privacy,
  Terms), secondary nav, and contact — modeled once as a shared `Footer` node above rather
  than repeated per page.
- **Gallery is folded into Custom Cakes, not a separate page** — the client's leaning
  answer to the PRD's open question (§10); the sitemap reflects that resolution.
- **Validation error and failure are both loop-backs, not dead ends.** Validation error
  returns the customer to the same filled-in form (inline errors); failure returns to the
  Submit action itself (retry), per PRD §6 form states — neither silently drops the
  request.
- **Allergy/dietary notes** entered in the Flow 1 form are sensitive: captured, then routed
  only to Maria's inbox — never displayed on-screen back to the customer beyond the generic
  success confirmation, and never stored elsewhere (PRD §6, §8).
- **Google Business Profile is link-out only** — no embedded map, no site-side directions
  logic. Flow 2 treats leaving the site as the intended end state, not a failure.
- Legal pages (Privacy, Terms) are static and reached only via the footer; no dedicated user
  flow is drawn for them.
