---
description: Builds and syncs the ai-docs/ knowledge base of official harness-layer docs. Reads ai-docs/sources.yaml, fetches every source that is missing or older than 30 days, writes faithful markdown mirrors, and regenerates the ai-docs/index.md catalog. Use when the user asks to sync, refresh, or add AI docs, set up the harness knowledge base, or mentions ai-docs being stale or missing a topic — even without naming /kb.
argument-hint: [add url [group] | --force]
allowed-tools: Bash(curl *), WebFetch
---

# Purpose

Keep the `ai-docs/` knowledge base in sync with its manifest: fetch whatever `ARGS` and staleness demand, mirror each source faithfully, and regenerate the index so agents can navigate the cache.

## Variables

ARGS: $ARGUMENTS — empty (normal sync), `--force` (refetch everything), or `add <url> [group]` (register a new source, then sync it)
MANIFEST: `ai-docs/sources.yaml` — entries of url / file / topic / fetched
INDEX: `ai-docs/index.md` — the agent-facing catalog
STALE_AFTER: `30` days

## Instructions

- The MANIFEST is the source of truth. Never fetch a URL that isn't in it; `add` registers first, then syncs.
- **Mirror format** — every cached doc is: YAML frontmatter (`source:` canonical URL, `fetched:` today), a `> **In here:**` line with 3 short bullets, then a faithful markdown conversion of the page. No commentary, no summarizing away detail.
- **Fetching is delegated** — spawn one `kb-fetcher` subagent per work-set entry, in parallel; each delegation message is just the entry's `url` and the absolute target path. The agent canonicalizes redirects, mirrors the page, and returns `OK <file> <canonical url>` plus a one-line summary (or `FAIL <file>: <reason>`). Fetched pages never enter this context.
- **Dedupe on canonicalization** — write each returned canonical URL back to the MANIFEST; if two entries resolve to the same canonical URL, keep one, drop the other, and say so in the report.
- Only the `## Cached official docs` table in INDEX is generated; leave `## Project notes` untouched. The INDEX table regenerates from the MANIFEST alone.

## Workflow

1. Parse ARGS. For `add <url> [group]`: append a MANIFEST entry (group defaults by host — anthropic/claude hosts → `anthropic`, Agent SDK pages → `anthropic/agent-sdk`, else the site's name; group keys are path-like and double as the folder under `ai-docs/`; derive `file` from the group + page slug, draft a `topic`, `fetched: null`).
2. Read MANIFEST. Work set = entries whose `fetched` is null, whose `file` is missing, or whose `fetched` is more than STALE_AFTER days old; `--force` selects all; `add` selects just the new entry. Empty work set → report "all fresh" and stop.
3. Fetch the work set: fan out `kb-fetcher` subagents per the Instructions and collect their OK/FAIL lines.
4. Update MANIFEST: canonical `url`, today's `fetched` date — only for entries that returned OK.
5. Regenerate the INDEX table from the MANIFEST: one row per entry — topic, file link, fetched date.
6. Report.

## Report

- Counts: newly fetched / refreshed (stale) / skipped (fresh) / failed.
- Any URL canonicalized to a new address, and any entries deduped.
- On failures: which URLs, the error, and that their `fetched` was left unchanged — never mark a failed fetch as fresh.
