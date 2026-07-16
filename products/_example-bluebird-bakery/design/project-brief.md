# Project Brief — Bluebird Bakery

Date: 2026-07-17 · Source: prd.md · For: the human designer picking up this package.

## Summary

Bluebird Bakery is a neighborhood Portland bakery, open since 2018, with no website today — only a Google Business listing and Instagram. We're designing a warm, simple, mobile-first brochure site of **five pages — Home, Menu, Our Story, Custom Cakes, and Visit Us / Contact — plus one working feature: the custom-cake inquiry form** that emails the owner, Maria Chen, directly and auto-confirms to the customer. The site's one job is to stop losing custom cake orders in buried Instagram DMs by sending cake customers straight from the homepage to a form that actually gets answered. Everything should feel homey and welcoming — the personal opposite of an impersonal supermarket-bakery page. (Privacy Policy and Terms of Use pages are also required as agency-drafted utility pages — see Design constraints.)

## Goals

- **Shift cake inquiries from Instagram DMs to the site form.** Baseline ~10 inquiries/month via DM → target **15+/month through the form**. Tracked by form-submission count; checked one month post-launch and again after the holiday season. → The design must make the inquiry form the homepage's single most prominent path.
- **End "I messaged and never heard back" complaints.** Every submission is auto-acknowledged and routed straight to Maria. Tracked by the auto-confirmation on every submit plus Maria's qualitative report; same two check-ins. → The form's submitting / success / confirmation states must reassure the customer clearly that the request arrived.

## Audience

- **Cake customers (birthday / wedding / baby shower) — the priority.** Top task: work out how to place a custom-cake order. Primary desired action: **submit the inquiry form** — the one action that matters most for this project. Discover on mobile, but often complete the full order later on desktop; willing to travel across town.
- **Neighborhood regulars.** Top task: today's hours, what's fresh, and where to park. Desired action: find hours and location (secondary — Google already covers this). Mostly on a phone.
- **New / visiting people.** Top task: understand what the bakery is about before walking in. Desired action: browse Home, Our Story, and Menu, then check hours or send an inquiry. Arrive via Google on a phone.

## Brand direction

- Tone: **warm, homey, welcoming** (explicitly **not** fancy or upscale).
- Assets provided: see brand-inputs.md (authored by Yuki Tanaka, UI Designer, in wave two). In short — client-owned professional photos of sourdough loaves, cakes, and the shop interior; brand colors **robin's-egg blue and cream**, in use since opening. The logo is a gap: it exists only hand-painted on the physical shop sign, with no digital file (see Design constraints and brand-inputs.md).
- Must-use messaging: none verbatim. "Since 2018" may be used where it helps. The differentiator to carry throughout: everything is made from scratch with a sourdough starter as old as the bakery itself, and every custom cake is hand-decorated by Maria — no mixes, no two cakes exactly alike.

## Visual direction

- **Mood:** Warm, handmade, neighborhood-personal — the site should feel like walking into a small local bakery run by someone who knows your name, never a chain or a catalog. Confident but never polished-corporate; homey, not fancy or upscale.
- **Palette anchor:** Robin's-egg blue and cream, the colors the shop has used since it opened. No verified hex values exist yet — see brand-inputs.md for proposed candidates and the gap. The wireframes in this package are intentionally grayscale per the design-standard's lo-fi conventions; that grayscale is a layout tool, not the color direction — lean the eventual palette toward a soft, slightly muted blue (not a saturated teal) paired with a warm off-white cream, so it reads gentle and inviting rather than bright or plastic.
- **Typography direction:** No existing type system — open territory for the human designer, not a locked decision (see brand-inputs.md gap). Aim for something friendly and approachable rather than corporate or overly formal: a rounded or humanist sans for body/UI, optionally a warmer display face for headlines that echoes the hand-painted sign's personality without literally imitating it.
- **Imagery rules:** Real client photos only — no stock imagery, ever, under any circumstance (explicit anti-reference). Give loaf, cake, and interior photos generous whitespace rather than cropping tight or tiling densely; a handful of well-chosen images should carry the warmth, not a dense grid. Hours and location stay visually prominent near the top of Home and on Visit Us, never buried in the footer.
- **Positive references:** Miller's Hearth Bakehouse — borrow the mechanics (simple, uncluttered layout; large, real photography; hours prominent at the top), not their specific look. Petal & Crumb Cake Studio — borrow the pattern of showing cake examples by size/style before the inquiry form, reapplied in Bluebird's own warm tone rather than Petal & Crumb's look.
- **Anti-reference:** Impersonal supermarket-bakery and stock-photo-driven sites — anything that reads corporate, generic, or catalog-like is explicitly what this site should not feel like.

This is direction, not final design — the human designer owns the visual execution.

## Design constraints

Hard boundaries the design must respect:

- **Accessibility:** WCAG 2.1 AA baseline for a public-facing food-business site.
- **Responsive:** mobile-first (most discovery is via phone/Google); must also work well on desktop, where cake customers often fill out the full inquiry in advance.
- **Performance:** fast mobile page loads are an explicit requirement — keep hero and image weight lean. No numeric budget was set by the client; keep pages light.
- **Brand:** mandated colors **robin's-egg blue and cream**. Logo usage is constrained by a gap — no digital logo file exists (hand-painted shop sign only); an interim wordmark may be needed so the build isn't blocked. See brand-inputs.md for the gap and its resolution.
- **Technical:** **agency-managed hosting** — the client must never touch servers or infrastructure. The stack is the agency's choice but must support a lightweight self-edit capability (CMS) for simple updates (hours, daily/seasonal specials), so the layout needs clearly editable hours and specials areas. Google Business Profile is **link-out only** (no embedded map required); no other integrations at launch.
- **Content:** **no stock imagery** — client-supplied photos only (impersonal supermarket-bakery styling is an explicit anti-reference). Menu content is client-provided and may arrive late — build the Menu page structure with placeholders. Publish **no allergen claims** until the client supplies a verified list. Allergy/dietary notes captured by the form are **sensitive — visible only to Maria**, never shown publicly. Privacy Policy and Terms of Use pages are required (agency-drafted, Maria signs off; the privacy policy must reflect that the form collects contact details and sensitive dietary notes).
- **Budget:** **$6,000–9,000** (confirmed) — keep the design simple and buildable within it.
- **Timeline:** launch **before the holiday season**; **date wins over scope**. Hold to the core five pages + inquiry form; anything beyond is deferred past launch.

## Deliverables

- This design package (six files): project brief, sitemap & flows, section briefs, copy deck, brand inputs, and lo-fi wireframes.
- Next, for the human designer: hi-fi visual comps for the five pages and each inquiry-form state, built on the wave-two visual direction and the resolved brand assets.

## Out of scope

- Online ordering (pickup/delivery), gift cards, loyalty program, newsletter/email signup — all deferred and quoted separately in a later phase.
- E-commerce, Square POS site integration (Square stays in-store checkout only), and email-marketing tools.
- Instagram feed embed — an optional nice-to-have, not required for launch.
- Data migration (none exists to migrate), additional languages (English only), and the health permit (stays displayed in-store, not on the site).

---

_Prepared by Ethan Park, Product Manager — Soriza (CPO department). Drafted from the approved prd/prd.md; no scope beyond it. The Visual direction section was completed by Yuki Tanaka (UI Designer) in wave two._
