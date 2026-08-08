---
type: tool
domain: engineering
status: current
created: 2026-08-07
updated: 2026-08-08
sources: ["ai-docs/llm-wiki/karpathy/llm-wiki.md", ".claude/rules/wiki-layer/wiki-standards.md"]
related: ["[[llm-wiki-pattern]]"]
---

# Obsidian Vault

A vault is a folder of plain markdown files, with nothing about the pages living inside the
application ([Karpathy](../../llm-wiki/karpathy/llm-wiki.md)).
Obsidian is usually described as a note-taking app, but the property that matters here is
that it renders what is already in the folder: the pages, the links between them, and a
graph view of how they connect ([Karpathy](../../llm-wiki/karpathy/llm-wiki.md)).
Files on disk, not an application database, are the system of record.

## Viewer, not owner

Because the notes are only files, another program can maintain the folder while a human
reads it. Karpathy runs exactly that arrangement — the LLM agent open on one side making
edits from their conversation, Obsidian on the other for browsing the results in real time
([Karpathy](../../llm-wiki/karpathy/llm-wiki.md)).
That makes Obsidian a front end for machine-maintained knowledge bases, including wikis
kept current by an LLM rather than by their owner; the framing the gist gives it is that
Obsidian is the IDE, the LLM is the programmer, and the wiki is the codebase
([Karpathy](../../llm-wiki/karpathy/llm-wiki.md)).
The division of labor is explicit: the human follows links, checks the graph view, and
reads the updated pages, while the maintainer does the summarizing, cross-referencing,
filing, and bookkeeping ([Karpathy](../../llm-wiki/karpathy/llm-wiki.md)).
This is the reading half of the two-programs-one-folder split the
[[llm-wiki-pattern]] describes.

## Affordances for a maintained vault

The Web Clipper browser extension converts web articles to markdown, which is the quick
path for getting new sources into the raw collection
([Karpathy](../../llm-wiki/karpathy/llm-wiki.md)).
The graph view doubles as a health dashboard — it is the best way to see the shape of the
wiki, what is connected to what, which pages are hubs and which are orphans
([Karpathy](../../llm-wiki/karpathy/llm-wiki.md)) —
which is the same drift that the [[llm-wiki-pattern]]'s lint operation sweeps for
([Karpathy](../../llm-wiki/karpathy/llm-wiki.md)).

## Getting images onto disk

Keeping clipped images on local disk is a two-step workflow. Setting Files and links →
"Attachment folder path" to a fixed directory pins where attachments land, and binding
"Download attachments for current file" from the Hotkeys settings gives a single keystroke
that pulls every image in the open note to local disk after clipping
([Karpathy](../../llm-wiki/karpathy/llm-wiki.md)). The point is not tidiness: local files let the
maintaining LLM view and reference the images directly rather than depending on URLs that
may break ([Karpathy](../../llm-wiki/karpathy/llm-wiki.md)).

Images then hit a limit of the maintainer, not the vault. An LLM cannot read markdown with
inline images in a single pass; the working method is to read the text first and then view
some or all of the referenced images separately as a second step
([Karpathy](../../llm-wiki/karpathy/llm-wiki.md)). Karpathy describes the whole image path as
optional — a text-only source collection needs none of it
([Karpathy](../../llm-wiki/karpathy/llm-wiki.md)).

## Plain files version cleanly

A vault of plain files versions in git: the wiki is just a git repo of markdown files, so
version history, branching, and collaboration come for free
([Karpathy](../../llm-wiki/karpathy/llm-wiki.md)).
That is the arrangement this repository uses: the vault root is `ai-docs/`, so the
raw sources and the wiki open as one vault, and the committed config lives in
`ai-docs/.obsidian/`
([wiki-standards.md](../../../.claude/rules/wiki-layer/wiki-standards.md)). The
attachment folder is set to `wiki/assets`, with personal pages excepted
([wiki-standards.md](../../../.claude/rules/wiki-layer/wiki-standards.md)).

Two plugins turn pages into other formats without changing what is on disk. Marp is a
markdown-based slide format with an Obsidian plugin, which makes presentations generable
straight from wiki content ([Karpathy](../../llm-wiki/karpathy/llm-wiki.md)). Dataview runs queries
over page frontmatter, so a maintainer that writes YAML fields — tags, dates, source
counts — gets dynamic tables and lists out of them at no extra cost
([Karpathy](../../llm-wiki/karpathy/llm-wiki.md)). This wiki's seven mandatory frontmatter fields
are what such a query would run against
([wiki-standards.md](../../../.claude/rules/wiki-layer/wiki-standards.md)).

Plugin support stops short of dependence. Web Clipper, Dataview, and Marp are supported
and recommended, but no page, command, or lint check may depend on a plugin being
installed ([wiki-standards.md](../../../.claude/rules/wiki-layer/wiki-standards.md)).
The vault stays legible to anything that reads markdown, which is the same property that
let a non-Obsidian maintainer write it in the first place.
