# Obsidian Vaults as a Reading Surface for Machine-Maintained Notes

> Pilot fixture B — a clipped-article stand-in, deliberately related to fixture A.
> Source: fixture (committed with the plan); treat as a local file ingest.

Obsidian is often described as a note-taking app, but its more interesting role is
as a viewer: a vault is just a folder of plain markdown files, and Obsidian renders
whatever is in it — links, backlinks, and a graph view of how pages connect.
Nothing about the notes lives inside the application, which means another program
can maintain the folder while a human reads it.

That property makes Obsidian a natural front end for machine-maintained knowledge
bases, including wikis kept current by an LLM rather than by their owner. The
human follows links and watches the graph; the maintainer updates pages, fixes
cross-references, and keeps an index current in the same directory.

A few affordances matter in that setup. The Web Clipper browser extension converts
an article into markdown and drops it into the vault — a one-click capture path
for new sources. A fixed attachment folder keeps images on local disk, so they
survive link rot and can be read by tools. The graph view doubles as a health
dashboard: hub pages, clusters, and orphans are visible at a glance, which is a
quick visual complement to any automated consistency check.

Because a vault is plain files, it versions cleanly in git: history, branches, and
review come free, and the same folder can hold both raw captured sources and the
synthesized pages built on top of them.
