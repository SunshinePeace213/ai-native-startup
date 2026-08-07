---
type: tool
domain: engineering
status: current
created: 2026-08-07
updated: 2026-08-07
sources: ["specs/wiki-layer/checks/fixtures/article-b-obsidian-vaults.md", ".claude/rules/wiki-layer/wiki-standards.md"]
related: ["[[llm-wiki-pattern]]"]
---

# Obsidian Vault

A vault is a folder of plain markdown files; Obsidian renders what is in it — links,
backlinks, and a graph view of how the pages connect
([article B](../../../specs/wiki-layer/checks/fixtures/article-b-obsidian-vaults.md)).
Obsidian is usually described as a note-taking app, but the property that matters here is
that nothing about the notes lives inside the application
([article B](../../../specs/wiki-layer/checks/fixtures/article-b-obsidian-vaults.md)).
Files on disk, not an application database, are the system of record.

## Viewer, not owner

Because the notes are only files, another program can maintain the folder while a human
reads it
([article B](../../../specs/wiki-layer/checks/fixtures/article-b-obsidian-vaults.md)).
That makes Obsidian a front end for machine-maintained knowledge bases, including wikis
kept current by an LLM rather than by their owner
([article B](../../../specs/wiki-layer/checks/fixtures/article-b-obsidian-vaults.md)).
The division of labor is explicit: the human follows links and watches the graph, while
the maintainer updates pages, fixes cross-references, and keeps an index current in the
same directory
([article B](../../../specs/wiki-layer/checks/fixtures/article-b-obsidian-vaults.md)).
This is the reading half of the two-programs-one-folder split the
[[llm-wiki-pattern]] describes
([article A](../../../specs/wiki-layer/checks/fixtures/article-a-llm-wiki-pattern.md)).

## Affordances for a maintained vault

Three affordances carry weight in that setup. The Web Clipper browser extension converts
an article into markdown and drops it into the vault, giving new sources a one-click
capture path
([article B](../../../specs/wiki-layer/checks/fixtures/article-b-obsidian-vaults.md)).
A fixed attachment folder keeps images on local disk, so they survive link rot and stay
readable by tools
([article B](../../../specs/wiki-layer/checks/fixtures/article-b-obsidian-vaults.md)).
The graph view doubles as a health dashboard — hub pages, clusters, and orphans are
visible at a glance, a visual complement to any automated consistency check
([article B](../../../specs/wiki-layer/checks/fixtures/article-b-obsidian-vaults.md)),
which is the same drift that the [[llm-wiki-pattern]]'s lint operation sweeps for
([article A](../../../specs/wiki-layer/checks/fixtures/article-a-llm-wiki-pattern.md)).

## Plain files version cleanly

A vault of plain files versions in git, so history, branches, and review come free, and
one folder can hold both the raw captured sources and the synthesized pages built on top
of them
([article B](../../../specs/wiki-layer/checks/fixtures/article-b-obsidian-vaults.md)).
That is the arrangement this repository uses: the vault root is `ai-docs/`, so the
mirrors and the wiki open as one vault, and the committed config lives in
`ai-docs/.obsidian/`
([wiki-standards.md](../../../.claude/rules/wiki-layer/wiki-standards.md)). The
attachment folder is set to `wiki/assets`, with personal pages excepted
([wiki-standards.md](../../../.claude/rules/wiki-layer/wiki-standards.md)).

Plugin support stops short of dependence. Web Clipper, Dataview, and Marp are supported
and recommended, but no page, command, or lint check may depend on a plugin being
installed ([wiki-standards.md](../../../.claude/rules/wiki-layer/wiki-standards.md)).
The vault stays legible to anything that reads markdown, which is the same property that
let a non-Obsidian maintainer write it in the first place.
