---
name: cpo-question-bank
description: Client-discovery question bank for website and software engagements — the twelve dimensions to interview a client across (business and goals, audience and users, brand and voice, content and assets, structure and pages, features and functionality, integrations and data, technical and hosting constraints, budget and timeline, success metrics, references and competitors, legal and compliance) with per-dimension question templates, why-we-ask reasons, and lock criteria. Loaded by the /c-suite cpo stage commands (cpo-intake) to run intake and to scaffold the engagement question list, requirements, and status ledger. Use when scoping a new client website or software build, drafting discovery questions, ingesting client answers, or deciding when a requirements dimension is locked.
autoInvoke: false
---

# CPO Question Bank

The discovery expertise for a client website or software engagement. Interview the
client across twelve dimensions until each one **locks** — enough is known that the
dimension can be frozen into `requirements.md` and built against. This skill is loaded
by the `/c-suite cpo` stage commands; it is never auto-invoked.

## How to use it

- Ask questions in the client's language, not ours. Each question below carries a
  one-line *why we ask* — say it if the client wonders why it matters.
- A dimension is **open** until its **locked when** criterion is met, then **locked**.
  Track that state in `requirements.md` (one `- <dimension>: <state>` line per
  dimension) and the stage in `status.md`.
- Never invent an answer. An unanswered dimension stays open; when the client owes the
  answer, the stage state is `blocked-on-client`.
- LIVE intake grills every dimension in one session. ASYNC intake generates a
  client-facing `question-list.md` from these questions and waits for
  `client-answers.md`, then gap-analyzes what is still open.

## The twelve dimensions

### 1. business & goals

- What does your business do, and who does it serve today? — *anchors every later decision to the real offering.*
- What is the single most important thing this build must accomplish in its first six months? — *forces one primary goal to prioritize scope against.*
- How will you know it worked — more leads, more sales, fewer support calls? — *turns "a website" into a business outcome.*
- Is this a new build, a redesign, or a rescue of something that isn't working? — *sets baseline expectations and migration risk.*
- **Locked when:** the primary business goal, the top one to three outcomes, and the build type (new / redesign / rescue) are named and agreed.

### 2. audience & users

- Who are the two or three main types of people who will use this, and what is each trying to get done? — *personas drive structure, copy, and features.*
- How technical are they, and what devices do they use most? — *sets complexity and the mobile-versus-desktop priority.*
- What is the one action you most want each visitor to take? — *defines the primary conversion path.*
- Where are your users, and what languages do they need? — *flags localization, timezone, and jurisdiction early.*
- **Locked when:** the primary user types, each one's top task, the primary desired action, and locale/language needs are agreed.

### 3. brand & voice

- Do you have brand guidelines, a logo, and a palette, or do those need to be created? — *separates "apply the brand" from "define the brand"; the latter is a human-designer gap.*
- In three words, how should the site feel to a first-time visitor? — *gives designers a concrete tone target.*
- Are there brands or sites whose look you admire or want to avoid? — *calibrates aesthetic direction quickly.*
- Is there approved copy, a tagline, or messaging we must use verbatim? — *locks non-negotiable wording before drafting.*
- **Locked when:** brand assets are supplied or explicitly listed as a gap, the desired tone is captured, and any must-use messaging is recorded.

### 4. content & assets

- What content already exists (text, images, video, logos), and who owns it? — *distinguishes reuse from net-new production.*
- Who will write and approve the words — you or us? — *assigns copy responsibility and schedule risk.*
- Do you have professional photography, or will we rely on stock or placeholders? — *image strategy affects design and cost.*
- How often will content change after launch, and who updates it? — *drives CMS and editability requirements.*
- **Locked when:** the content inventory, ownership of copy and media, and post-launch update responsibility are known.

### 5. structure & pages

- What are the must-have pages or screens for launch? — *defines the sitemap's minimum footprint.*
- How do you picture someone moving from landing to the action you want? — *surfaces the primary user flow.*
- Are there sections you're unsure about that we should validate before building? — *flags soft scope for grilling.*
- Is there existing navigation or an old site whose structure we should keep or break from? — *manages migration and habit expectations.*
- **Locked when:** the launch page/screen list and the primary navigation path are agreed.

### 6. features & functionality

- Beyond static content, what must the site DO — forms, booking, search, accounts, payments? — *separates a brochure site from an application.*
- For each feature, is it required for launch or a later phase? — *enforces MVP scope and prevents drift.*
- Are there features you've seen elsewhere that you consider essential? — *grounds expectations in concrete references.*
- What should happen when a user submits a form or completes the key action? — *defines success and failure states and any integration.*
- **Locked when:** the launch feature set is enumerated, each item is marked launch-versus-later, and the key-action outcome is defined.

### 7. integrations & data

- What third-party tools must this connect to — CRM, email, payments, analytics, scheduling? — *integrations carry the biggest hidden technical cost.*
- Where does the data users enter need to end up? — *defines destinations, ownership, and compliance surface.*
- Do you already have accounts for those services, or do they need setting up? — *flags access and credential blockers.*
- Is there existing data to migrate, and in what format? — *migration is a common schedule risk.*
- **Locked when:** required integrations, data destinations, account ownership, and any migration source are known.

### 8. technical & hosting constraints

- Do you have a domain and hosting already, or do those need arranging? — *determines launch logistics and deployment target.*
- Is there a platform or technology you must use or must avoid? — *hard constraints bound the whole solution.*
- Who maintains the site technically after launch? — *sets the maintainability and handoff bar.*
- Are there performance, uptime, or accessibility standards you must meet? — *non-functional requirements shape architecture.*
- **Locked when:** domain/hosting status, mandated or forbidden tech, maintenance ownership, and any performance/accessibility standard are known.

### 9. budget & timeline

- Is there a hard launch date or event this must be ready for? — *a fixed date forces scope tradeoffs.*
- What budget range are we working within? — *budget bounds feasible scope and quality.*
- If we had to choose, is hitting the date or the full feature set more important? — *pre-agrees the tradeoff before pressure hits.*
- Would you accept a phased or staged rollout? — *opens MVP-then-iterate as a path.*
- **Locked when:** the target date (or its absence), the budget range, and the date-versus-scope priority are agreed.

### 10. success metrics

- How will you measure whether this was worth it — what number moves? — *makes success testable, not a vibe.*
- What is that number today, and where do you want it? — *baseline plus target equals a measurable metric.*
- How will we track it — analytics, form submissions, sales data? — *ensures the metric is observable after launch.*
- By when do you expect to see the change? — *sets the evaluation window.*
- **Locked when:** at least one measurable metric with a baseline, a target, a tracking method, and a timeframe is agreed.

### 11. references & competitors

- Who are your main competitors, and what do their sites do well or badly? — *positions the build in its market.*
- Show us two or three sites you'd love yours to stand beside. — *concrete references beat abstract adjectives.*
- What must we NOT copy or resemble? — *negative references sharpen differentiation.*
- What makes you different, in one sentence? — *the differentiator becomes the hero message.*
- **Locked when:** the competitor set, positive references, anti-references, and the one-line differentiator are captured.

### 12. legal/compliance

- Do you need a privacy policy, terms, cookie consent, or accessibility compliance? — *legal pages and consent are easy to forget and costly to retrofit.*
- Do you handle any sensitive or regulated data (health, financial, children's)? — *regulated data changes the entire data-handling design.*
- Are there industry regulations or certifications you must display or meet? — *compliance can be a hard launch gate.*
- Who signs off on legal content before launch? — *assigns approval ownership and schedule risk.*
- **Locked when:** required legal pages, regulated-data status, applicable regulations, and legal sign-off ownership are known.

## Templates

Scaffold a new engagement from these bundled files:

- `${CLAUDE_SKILL_DIR}/templates/question-list.md` — client-ready question document, grouped by the twelve topics, each question with its why-we-ask line.
- `${CLAUDE_SKILL_DIR}/templates/requirements.md` — locked-requirements record, one dimension per section with a `- <dimension>: <state>` marker line.
- `${CLAUDE_SKILL_DIR}/templates/status.md` — the engagement ledger: mode, GitHub trail, per-stage state, and per-stage run log.
