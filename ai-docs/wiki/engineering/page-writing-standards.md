---
type: pattern
domain: engineering
status: current
created: 2026-08-08
updated: 2026-08-08
sources: ["ai-docs/llm-wiki/farzaa/wiki-gen-skill.md", ".claude/rules/wiki-layer/wiki-standards.md"]
related: ["[[llm-wiki-pattern]]", "[[ingest-pipeline]]", "[[wiki-drift]]", "[[wiki-schema-layer]]"]
---

# Page Writing Standards

The instruction that opens the most prescriptive instantiation of the
[[llm-wiki-pattern]] is a role assignment: the maintainer is a writer compiling a wiki, not
a filing clerk, whose job is to read entries, understand what they mean, and write articles
that capture understanding ([wiki skill](../../llm-wiki/farzaa/wiki-gen-skill.md)). The operational
form of that is a question the maintainer asks of every incoming fact — never "where do I
put this?" but "what does this mean, and how does it connect to what I already know?"
([wiki skill](../../llm-wiki/farzaa/wiki-gen-skill.md)). The standards below are what that role
produces when written down as rules. This repository's own writing rules are a near-direct
descendant ([wiki-standards.md](../../../.claude/rules/wiki-layer/wiki-standards.md)).

## Theme over chronology

The most common structural defect named is diary-driven organization, where individual
events become section headings. The contrast given is between headings like "The March
Meeting", "The April Pivot", "The June Launch" and headings like "Origins", "The Pivot to
Institutional Sales", "Becoming the Product"
([wiki skill](../../llm-wiki/farzaa/wiki-gen-skill.md)). The check offered is the Steve Jobs test:
Wikipedia's article uses "Early life" and "Career" with era subsections, not "The Xerox
PARC Visit" or "The Lisa Project Failure"
([wiki skill](../../llm-wiki/farzaa/wiki-gen-skill.md)). An article that fails it is to be rewritten
rather than patched ([wiki skill](../../llm-wiki/farzaa/wiki-gen-skill.md)).

Every article is also required to have a point. The formulation is that an article is not
"here are four times X appeared" but "X represented Y", and a reader should finish
understanding the significance ([wiki skill](../../llm-wiki/farzaa/wiki-gen-skill.md)).

## Anti-cramming and anti-thinning

Two named failure modes pull in opposite directions and are stated as a matched pair. The
gravitational pull of existing articles is called the enemy: appending a paragraph to a big
article is always easier than creating a new one, and doing so yields five bloated articles
instead of thirty focused ones ([wiki skill](../../llm-wiki/farzaa/wiki-gen-skill.md)). The concrete
trigger is that a third paragraph about a sub-topic means the sub-topic deserves its own
page ([wiki skill](../../llm-wiki/farzaa/wiki-gen-skill.md)).

The opposite failure is treated as equally bad. Creating a page is not the win, enriching
it is; a stub of three vague sentences when four other entries also mentioned the topic is
a failure, and every time a page is touched it should get richer
([wiki skill](../../llm-wiki/farzaa/wiki-gen-skill.md)). The threshold for creating a page at all is
whether three meaningful sentences can be written; below that, the topic is noted in the
article where it appears and the page waits for more material
([wiki skill](../../llm-wiki/farzaa/wiki-gen-skill.md)). The summarizing principle is that 40 stubs
is as bad as 5 bloated articles ([wiki skill](../../llm-wiki/farzaa/wiki-gen-skill.md)). Both rules
are carried into this repository under the same two names
([wiki-standards.md](../../../.claude/rules/wiki-layer/wiki-standards.md)).

## Encyclopedic tone

The target register is Wikipedia, stated as flat, factual, and encyclopedic, with the
article staying neutral while direct quotes from the entries carry the emotional weight
([wiki skill](../../llm-wiki/farzaa/wiki-gen-skill.md)). The prohibitions are enumerated: peacock
words such as "legendary", "visionary", "groundbreaking", "deeply", and "truly"; editorial
voice such as "interestingly", "importantly", and "it should be noted"; rhetorical
questions; progressive narrative such as "would go on to", "embarked on", and "this
journey"; qualifiers such as "genuine", "raw", "powerful", and "profound"; and em dashes
([wiki skill](../../llm-wiki/farzaa/wiki-gen-skill.md)).

The positive instructions are as specific. Lead with the subject and state facts plainly,
one claim per sentence, short sentences, simple past or present tense, and attribution over
assertion — "He described it as energizing" rather than "It was energizing" — letting facts
imply significance and letting dates and specifics replace adjectives
([wiki skill](../../llm-wiki/farzaa/wiki-gen-skill.md)). Quotes are capped at two per article, on the
instruction to pick the line that hits hardest
([wiki skill](../../llm-wiki/farzaa/wiki-gen-skill.md)).

## Length as a structural signal

Length targets are given per article type rather than globally: 20 to 30 lines for a person
appearing once, 40 to 80 for a person appearing three or more times, 20 to 40 for a place,
25 to 50 for a company, 40 to 80 for a philosophy or pattern or relationship, 60 to 100 for
an era, 40 to 70 for a decision or transition, and 25 to 45 for an experiment or idea, with
15 lines as the floor for anything ([wiki skill](../../llm-wiki/farzaa/wiki-gen-skill.md)). Articles
over 120 lines are assessed as bloated and articles over 150 lines are checked for splitting
([wiki skill](../../llm-wiki/farzaa/wiki-gen-skill.md)). Structure is also prescribed per type — a
person by role or relationship phase, a project by conception, development, and outcome, a
decision by the situation, the options, the reasoning, and the choice
([wiki skill](../../llm-wiki/farzaa/wiki-gen-skill.md)).

This repository compresses the same idea into a single band: under 15 lines is a note
rather than a page, over 150 lines it splits by theme, and most pages land between 40 and
100 ([wiki-standards.md](../../../.claude/rules/wiki-layer/wiki-standards.md)).

## Where this repository diverges

The inheritance is close but not total, and the differences are instantiation choices
rather than disagreements. This wiki adopts the theme-over-chronology rule, the
anti-cramming and anti-thinning pair, the flat factual tone with the same peacock-word and
editorial-aside prohibitions, and the two-quote cap
([wiki-standards.md](../../../.claude/rules/wiki-layer/wiki-standards.md)). It does not
adopt the em-dash prohibition, and it does not maintain per-type length targets or a
generated backlinks section on each page. Its citation unit also differs: claims cite
source paths inline at the point of the claim rather than listing entry IDs in frontmatter
alone ([wiki-standards.md](../../../.claude/rules/wiki-layer/wiki-standards.md)), where the
skill spec cites raw entry IDs in a frontmatter field
([wiki skill](../../llm-wiki/farzaa/wiki-gen-skill.md)).
