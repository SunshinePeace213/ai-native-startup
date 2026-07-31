---
name: studio-client-questions
description: The Soriza studio's client discovery question bank for website engagements. It carries the eight dimensions a project must establish before definition — the job the site does, the audience and their situation, brand voice, references loved and hated, the content that actually exists, hard constraints, budget, and success at six months. Use when preparing or running a client discovery round, drafting intake or kickoff questions, turning a client call into discovery notes, deciding what to ask a client next, or working out which dimensions a project has left unanswered. Also use whenever a studio role needs the question set for a discovery round, or is writing a client project's discovery notes file. Not for internal planning interviews about this repo's own work.
---

# Client Discovery Questions

The bank Soriza's client-facing roles draw from during discovery. Pick the questions a
round needs and ask them in the client's own vocabulary — reading the bank aloud produces
a survey, not a conversation.

A dimension is closed when the notes hold a written statement of what is true, not a
transcript of what was said. When a dimension genuinely does not apply, the notes say
`N/A, because …` — silence reads as unanswered, and the coverage check treats it as one.

## Machine-readable dimension list

Every `###` heading under `## Dimensions` is one dimension, and the heading text is that
dimension's name. Two things depend on that list:

- `check_question_coverage.py` parses those headings and carries no copy of its own.
- `clients/<client>/<project>/discovery/notes.md` carries one `## <dimension>` heading per
  name, matching the text verbatim.

Adding a `###` heading here adds a dimension the check requires; renaming one renames the
section the notes must carry.

## Dimensions

### The job the site does

The single outcome the site exists to produce.

- What should someone do because of this site that they do not do today?
- If it could only do one thing, which one?
- Where does that action go today — a form, a phone, a shop, nowhere?
- Which page would hurt most to lose?
- What does a good week look like, in a number you already watch?

### The audience and their situation

Who arrives, and in what state.

- Who lands here, and what were they doing five minutes earlier?
- What do they already believe about you — including the parts that are wrong?
- Phone or desktop, at work or at home, in a hurry or browsing?
- What do they need to be convinced of before they act?
- Who else is in the room when the decision gets made?

### Brand voice

How the writing should sound, and what it must never sound like.

- Three words you want people to use about you, and three you would hate.
- Show me something of yours that sounds right. What is wrong with the rest?
- Do you say "we", or the company name? First names or titles?
- Which words are banned internally, and why?
- Who signs off on copy, and what do they push back on?

### References loved and hated

The precedents, and what specifically they point at.

- Three sites you would be happy to be compared to — what works in each?
- Three you cannot stand, and what ruins them.
- A competitor's site you quietly prefer to your own?
- Something outside your industry that feels right.
- For each: is it the look, the structure, or the writing you mean?

### The content that actually exists

What is real today, as opposed to intended.

- What copy, photography, video, and logo files exist, and who owns them?
- Which of it survives as-is, and which is placeholder nobody replaced?
- Who writes what is missing, by when, and who approves it?
- How many products, services, case studies, or locations — and how often do they change?
- Who updates the site after launch, and how technical are they?

### Hard constraints

The things the design has to accept rather than solve.

- Are the existing brand guidelines binding, or a starting point?
- Which CMS, hosting, analytics, commerce, or CRM must stay?
- What is the deadline tied to — a launch, an event, a funding round, a season?
- Any legal, accessibility, or regulatory obligation on this site?
- Languages, integrations, or existing URLs that must not break?

### Budget

The range, and what it is allowed to cover.

- What range have you set aside for design, and separately for build?
- What is approved now, and what needs a further sign-off — from whom?
- Is photography, illustration, or licensing inside this number or outside it?
- What is the ongoing budget after launch?
- If something has to give, would you rather cut scope or move the date?

### Success at six months

The measurable outcome the engagement is judged against.

- Six months after launch, which number is different?
- What is that number today, and who measures it?
- What would make you call it a failure even if it looks good?
- Who reports on it internally, and to whom?
- What is the first thing you expect to want to change after launch?
