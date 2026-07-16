# PRD — Bluebird Bakery

Status: draft · Date: 2026-07-17 · Source: discovery/requirements.md

## 1. Overview

Bluebird Bakery is a neighborhood Portland bakery, open eight years (since 2018),
serving two customer groups: walk-in regulars (daily sourdough, pastries, coffee) and
custom celebration-cake customers (birthdays, weddings, baby showers). It has no wholesale
or restaurant supply, and — today — no website: its only online presence is a Google
Business listing and Instagram.

This release is a new-build brochure website of five pages plus one working feature. Its
one job is to **stop losing custom cake orders to buried Instagram DMs** by giving customers
a real inquiry form that reaches the owner, Maria Chen, directly. The two outcomes that
define success are (1) more cake orders arriving through the form instead of DMs, and (2)
an end to "I messaged and never heard back" complaints.

**One-line positioning:** A warm, simple, scratch-made neighborhood bakery site whose
homepage sends cake customers straight to an inquiry form that actually gets answered —
the personal opposite of an impersonal supermarket-bakery page.

The differentiator to carry throughout: everything is made from scratch with a sourdough
starter as old as the bakery itself, and every custom cake is hand-decorated by Maria — no
mixes, no two cakes exactly alike. Competitively, the site takes the parts of Miller's Hearth
Bakehouse that work (simple layout, large photos, hours prominent at the top) and the idea
behind Petal & Crumb Cake Studio's inquiry form (show examples by size and style before the
customer commits) — the idea, not the exact look — applied to Bluebird's own warm, homey feel.

_Traces to: business & goals; audience & users; references & competitors._

## 2. Goals & measurable success metrics

| Goal | Baseline | Target | Tracking method | Timeframe |
| --- | --- | --- | --- | --- |
| Shift custom cake inquiries from Instagram DMs to the site form | ~10 cake inquiries/month via Instagram DM | 15+ inquiries/month through the site form | Count of cake-inquiry form submissions (emails Maria receives / form log) | Two check-ins: one month post-launch, and again after the holiday season |
| End the "I messaged and never heard back" complaints | Recurring missed-inquiry complaints today | Zero missed-inquiry complaints; every submission auto-acknowledged | Auto-confirmation sent on every submission; Maria's qualitative report | Same two check-ins (1 month post-launch, post-holiday) |

_Traces to: business & goals; success metrics. The core metric is form submissions; the second
goal is the reliability outcome the form's direct-to-Maria routing and auto-confirmation deliver._

## 3. Users / personas

- **Neighborhood regulars** — top task: check today's hours, what's fresh, and where to park;
  primary desired action: find hours and location (secondary overall, since Google already
  covers this); context: mostly on a phone, local, English.
- **Cake customers (birthday / wedding / baby shower)** — top task: work out how to place a
  custom cake order; **primary desired action: submit the custom cake inquiry form** — the one
  action that matters most for this project; context: discover on mobile, but often fill out a
  full order in advance on desktop; willing to travel across town; English.
- **New / visiting people** — top task: understand what the bakery is about before walking in;
  primary desired action: browse Home, Our Story, and Menu (then hours or an inquiry); context:
  arrive via Google on a phone, English.

_Traces to: audience & users; business & goals._

## 4. Scope & non-goals

**In scope (this release):**

- Five launch pages: **Home, Menu, Our Story, Custom Cakes, Visit Us / Contact**.
- The **custom cake / catering inquiry form** — the only feature required for launch — which
  emails Maria directly and sends the customer an automatic confirmation.
- A **past-cakes photo gallery** presented as examples by size/style; folded into the Custom
  Cakes page (the page-vs-section placement is the agency's delegated call — see Open questions).
- **Outbound link to the Google Business Profile** for directions and reviews (link-out only).
- A **lightweight self-edit capability (CMS)** for simple updates such as hours and daily/seasonal
  specials, with the agency retaining primary update responsibility.
- **Domain and hosting** arranged as part of the project (neither exists today), on managed
  hosting the client never has to touch.
- **Privacy policy and terms of use** pages, agency-drafted for Maria's sign-off.
- **Mobile-first design** with fast mobile page loads and a **WCAG 2.1 AA** accessibility baseline.

**Non-goals (explicitly out of this release, deferred, or possibly never):**

- **Online ordering for pickup or delivery** — deferred.
- **Gift cards** — deferred.
- **Loyalty program** — deferred.
- **Newsletter / email signup** — deferred.
- **Instagram feed embed** — an optional nice-to-have, not required for launch (see Open questions).
- No e-commerce, no Square POS site integration (Square stays in-store checkout only), and no
  email-marketing tool.
- No data migration (no email list or menu spreadsheet exists to migrate).
- English only — no additional languages.
- The health permit stays displayed in-store only, not on the site.

**Phase boundary:** date wins over scope. The core five pages plus the cake inquiry form must
launch before the holiday season; anything beyond that core is deferred past launch. Deferred
features are quoted separately in a later phase.

_Traces to: features & functionality; budget & timeline; integrations & data; references & competitors._

## 5. User stories with acceptance criteria

- **US-1 — Submit a cake inquiry (primary action).** As a custom-cake customer, I want to submit
  a cake inquiry through a form on the site, so that my request reaches the bakery reliably instead
  of getting lost in Instagram DMs.
  - Acceptance criteria:
    - [ ] From the homepage I can reach the Custom Cakes inquiry form in a single click/tap.
    - [ ] The form captures the details Maria needs to scope a cake: event type and date, size/servings,
          flavor, design description, allergy/dietary notes, and my contact info.
    - [ ] On submit, the inquiry is emailed to Maria as the sole recipient.
    - [ ] On submit, I receive an automatic "we got it, we'll be in touch" confirmation.
    - [ ] The allergy/dietary notes I enter are treated as sensitive and are visible only to Maria.
    - [ ] The form works on both mobile and desktop.
    - [ ] Submitting without required contact info is prevented, with errors shown inline; a submission
          failure shows a retry message rather than silently dropping the request.

- **US-2 — See examples before committing.** As a cake customer, I want to see examples of past cakes
  by size and style before I fill out the form, so that I know what's possible and can describe what I want.
  - Acceptance criteria:
    - [ ] The Custom Cakes page shows a gallery of past cakes using client-supplied photos.
    - [ ] The examples convey a range of sizes and styles.
    - [ ] The gallery sits on the same page as the inquiry form so the customer can view examples, then inquire.

- **US-3 — Check hours and location.** As a neighborhood regular, I want to quickly see today's hours and
  where to park, so that I can plan my visit.
  - Acceptance criteria:
    - [ ] Hours and location are visible immediately at the top of the homepage and on Visit Us, without digging.
    - [ ] Parking information is included on Visit Us.
    - [ ] An outbound link to the Google Business Profile is available for directions and reviews.
    - [ ] The page loads fast on mobile.

- **US-4 — Understand the bakery before visiting.** As someone who found Bluebird via Google, I want to
  understand what the bakery is and what it makes, so that I can decide whether to visit.
  - Acceptance criteria:
    - [ ] Home and Our Story convey the warm, homey, scratch-made story (since 2018; a sourdough starter as
          old as the bakery; cakes hand-decorated by Maria).
    - [ ] The Menu page shows current offerings.
    - [ ] Client-supplied photos of loaves, cakes, and the shop interior are shown (no stock imagery).

- **US-5 — See the current menu and specials.** As a regular, I want to see the current menu and today's
  specials, so that I know what's fresh.
  - Acceptance criteria:
    - [ ] The Menu page displays the client-provided menu.
    - [ ] Daily specials and seasonal/holiday menu shifts can be updated without a developer.

- **US-6 — Keep simple content current without touching servers.** As the bakery owner (or a part-time
  staff member such as Jenna), I want simple content like hours and specials to be easy to update, so that
  the site stays current without technical help.
  - Acceptance criteria:
    - [ ] Hours and specials can be edited through a simple interface, or by the agency on request.
    - [ ] The client never needs to touch servers or technical infrastructure.
    - [ ] The agency retains primary responsibility for updates and technical upkeep.

_Traces to: features & functionality; structure & pages; content & assets; technical & hosting constraints._

## 6. Functional requirements

### Home

- Must: route cake customers straight to the Custom Cakes page and its inquiry form in one click via a
  prominent call to action; show hours and location immediately at the top for regulars; convey the warm,
  scratch-made brand; and link clearly to Menu, Our Story, Custom Cakes, and Visit Us.
- States: static content; the hours block reflects the current hours (editable via the CMS).
- Inputs / outputs: in — page navigation intent; out — navigation to the four other pages plus an outbound
  link to the Google Business Profile.

### Menu

- Must: display the client-provided menu (a cleaned-up version of the in-shop chalkboard) and accommodate
  frequent daily specials plus a handful of seasonal/holiday shifts per year.
- States: current menu; updated specials.
- Inputs / outputs: in — menu content supplied by the client; out — rendered menu, editable via the CMS/agency.
- Note: no formal ingredient/allergen list exists today (gap — see Risks and legal/compliance). The Menu makes
  no allergen claims until the client provides a verified list.

### Our Story

- Must: tell the warm, homey, welcoming story — explicitly not fancy or upscale — anchored on "since 2018,"
  the sourdough starter as old as the bakery, and cakes hand-decorated by Maria.
- States: static content.
- Inputs / outputs: in — agency-drafted copy (Maria approves) and client-supplied interior/loaf photos; out —
  rendered story page.

### Custom Cakes (with inquiry form + past-cakes gallery)

- Must: be reachable in one click from Home; house the cake inquiry form; and show a past-cakes gallery of
  examples by size/style so the customer can see what's possible before committing.
- States: page renders the gallery and the form; form states are defined below.
- Inputs / outputs: in — client-supplied gallery photos; out — the inquiry form (below) and its email/confirmation.

### Cake inquiry form (the launch feature)

- Must: capture the details Maria needs to scope a custom cake or catering order — event type and date,
  size/servings, flavors, design description, allergy/dietary notes, and customer contact info (name, email
  and/or phone).
- States:
  - Empty — blank form on load.
  - Validation error — required fields missing or contact info invalid; inline errors, submission blocked.
  - Submitting — in-flight after submit.
  - Success — the customer sees a "we got it, we'll be in touch" confirmation on-screen and by email.
  - Failure — submission error is shown with a retry path; the request is never silently dropped.
- Inputs / outputs: in — the customer's cake details; out — an email to **Maria as the sole recipient** (she
  handles all cake orders) **and** an automatic confirmation email to the customer.
- Sensitive data: allergy/dietary notes are treated as sensitive — **visible only to Maria**, never displayed
  publicly and never routed anywhere but her inbox (no spreadsheet, no POS).

### Visit Us / Contact

- Must: present hours, location, and parking prominently; provide contact details; and link out to the Google
  Business Profile for directions and reviews.
- States: static content; hours reflect the current value (editable via the CMS).
- Inputs / outputs: in — hours/address/parking facts from the client; out — rendered page plus an outbound link
  to the Google Business Profile.

### Simple-content editing (CMS)

- Must: let simple content — hours and daily/seasonal specials — be edited without server access; be easy enough
  that part-time staff (Jenna) can optionally make genuinely simple edits; and keep the agency as the primary
  update owner. The client must never need to touch servers or infrastructure.
- States: view/edit of the small set of editable fields.
- Inputs / outputs: in — edited hours/specials text; out — updated public pages.

### Legal pages (Privacy policy + Terms of use)

- Must: publish an agency-drafted privacy policy and terms of use, signed off by Maria on the same approval flow
  as site copy. The privacy policy must reflect that the inquiry form collects contact details and sensitive
  allergy/dietary notes handled privately by Maria.
- States: static content.
- Inputs / outputs: in — agency-drafted legal copy and Maria's sign-off; out — published legal pages.

_Traces to: structure & pages; features & functionality; integrations & data; legal/compliance._

## 7. Content requirements

Tone and voice, everywhere: **warm, homey, welcoming — explicitly not fancy or upscale.** Copy is
**agency-drafted (Soriza); Maria reviews for tone and accuracy and gives final approval before anything goes
live** — this is not word-for-word client control. No verbatim must-use messaging; **"since 2018"** may be used
where it helps. Brand colors are **robin's-egg blue and cream**, in use since opening.

- **Home** — content needed: hero/brand intro and a clear cake-inquiry call to action; tone: warm/homey; owner:
  Soriza drafts, Maria approves; must-use copy: none ("since 2018" optional); media: client-supplied photos.
- **Menu** — content needed: the cleaned-up menu; tone: plain and appetizing; owner: **client provides the menu
  content**, Soriza formats; must-use copy: none; media: client-supplied photos. No allergen list yet (gap).
- **Our Story** — content needed: the scratch-made, sourdough-starter, hand-decorated-cakes narrative; tone:
  warm/personal; owner: Soriza drafts, Maria approves; media: client-supplied interior/loaf photos.
- **Custom Cakes** — content needed: intro/how-to-inquire copy, form field labels, gallery captions, and the
  auto-confirmation email copy; tone: reassuring/warm; owner: Soriza drafts, Maria approves; media:
  client-supplied past-cakes photos.
- **Visit Us / Contact** — content needed: hours, address, parking, contact details; owner: client provides the
  facts, Soriza formats; must-use copy: none.
- **Legal (Privacy + Terms)** — content needed: standard brochure-site privacy policy and terms; owner: Soriza
  drafts, Maria signs off.

**Assets and ownership:**

- **Photography** — professional photos of sourdough loaves, cakes, and the shop interior already exist (shot by
  the client's photographer friend last spring); the client owns the files and will supply them. **No stock
  imagery** — stock/impersonal supermarket-bakery styling is an explicit anti-reference.
- **Logo — gap.** The logo exists only hand-painted on the physical shop sign; **no digital file exists** and it
  likely needs to be recreated as a usable digital asset. Flagged as a Risk and an Open question.

_Traces to: content & assets; brand & voice._

## 8. Technical constraints

- **Platform:** no mandated or forbidden platform — **delegated to the agency's judgment**. The agency chooses
  the stack, provided it supports a lightweight self-edit capability for simple updates. **Hard constraint: the
  client must never need to touch servers or any technical infrastructure herself.**
- **Hosting:** neither a domain nor hosting exists yet — both are **arranged as part of this project**. Hosting
  is **agency-managed**, with an ongoing agency-managed maintenance arrangement after launch; part-timer Jenna
  may make genuinely simple edits (e.g., hours) only if the tooling makes that easy, but the agency owns upkeep.
- **Integrations:** none required for launch. Square POS is **in-store checkout only — no site connection**.
  Google Business Profile is **link-out only** (reviews/directions). An Instagram feed embed is an optional
  nice-to-have, not a requirement. No online-ordering platform and no email-marketing tool. All relevant
  accounts (Square, Google Business Profile, Instagram) already exist; nothing new needs provisioning.
- **Data destinations:** cake inquiry submissions go to **Maria's email inbox only** — no spreadsheet, no POS
  integration. Allergy/dietary notes within them are sensitive and reach only Maria.
- **Performance:** mobile-first; **fast page loads on mobile** are an explicit requirement.
- **Accessibility:** no specific standard was named by the client — delegated to the agency; the recommended
  baseline is **WCAG 2.1 AA** for a public-facing food-business site.
- **Locale:** English only.
- **Budget:** $6,000–9,000 (confirmed). **Timeline:** no fixed date, but launch **before the holiday season**;
  **date wins over scope**.

_Traces to: technical & hosting constraints; integrations & data; budget & timeline; legal/compliance._

## 9. Risks

| Risk | Impact | Likelihood | Mitigation |
| --- | --- | --- | --- |
| Logo exists only hand-painted on the shop sign — no digital file; brand/visual assets depend on recreating it | Med | High | Digitize/recreate the logo as a usable asset in the first week; use an interim wordmark if needed so the build isn't blocked; confirm the desired approach with Maria (Open question) |
| Menu content is a client-owned deliverable (cleaned-up chalkboard) on the critical path; late delivery slows the Menu page | Med | Med | Request the menu at kickoff with a firm due date; build the Menu page structure with placeholders while awaiting content |
| No formal ingredient/allergen list exists — publishing allergen claims without data on a food-business site would be unsafe/misleading | Med | Med | Publish no allergen claims until the client supplies a verified list; capture dietary notes via the form for Maria to handle per order; keep the health permit in-store only |
| Pre-holiday deadline with date-wins-over-scope; feature creep or asset delays could threaten launch | High | Med | Hold scope to the core five pages + inquiry form; defer everything else; sequence content/asset dependencies early |
| Fixed $6,000–9,000 budget; scope beyond the locked core risks overrun | Med | Low | Keep to locked scope; quote deferred features (ordering, gift cards, loyalty, newsletter) separately in a later phase |
| Client-supplied photo handoff timing unconfirmed | Low | Low | Collect all photo files at kickoff |

_Traces to: budget & timeline; content & assets; technical & hosting constraints; legal/compliance._

## 10. Open questions

- **Domain name** to register is not yet chosen — confirm the desired domain with the client.
- **Logo recreation approach** — a faithful digitization of the hand-painted sign, or a lightly refreshed mark?
  Confirm with Maria before visual design.
- **Menu page structure** — finalize once the client delivers the cleaned-up menu content.
- **Past-cakes gallery placement** — its own page vs. a section of the Custom Cakes page is the agency's delegated
  call, to be settled at design; the client leans toward folding it into Custom Cakes.
- **Instagram feed embed** — a nice-to-have, not required for launch; confirm whether to include it at launch.
- **CMS editable scope** — confirm exactly which fields staff self-edit (hours, specials) vs. agency-managed, so
  the tooling stays genuinely simple.

## Requirement traceability

Every one of the twelve locked discovery dimensions is covered above:

| Locked dimension | Covered in |
| --- | --- |
| business & goals | §1 Overview; §2 Goals & metrics |
| audience & users | §3 Users/personas; §1 Overview |
| brand & voice | §7 Content requirements (tone/voice, colors, logo gap) |
| content & assets | §7 Content requirements; §6 Menu/CMS; §9 Risks |
| structure & pages | §6 Functional requirements (per page); §5 User stories |
| features & functionality | §6 Cake inquiry form; §5 User stories; §4 Scope & non-goals (deferred) |
| integrations & data | §8 Technical constraints; §6 Functional requirements (form output, Google link-out) |
| technical & hosting constraints | §8 Technical constraints |
| budget & timeline | §4 Scope & non-goals (phase boundary); §8 Technical constraints; §9 Risks |
| success metrics | §2 Goals & measurable success metrics |
| references & competitors | §1 Overview (positioning); §4 Scope & non-goals |
| legal/compliance | §6 Legal pages + form sensitive-data handling; §7 Content; §8 Technical; §9 Risks |

---

_Prepared by Ethan Park, Product Manager — Soriza (CPO department). Drafted from the locked
`discovery/requirements.md`; no scope beyond the locked requirements._
