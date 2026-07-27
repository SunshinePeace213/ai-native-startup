---
description: Builds and syncs the ai-docs/ knowledge base of official docs on any domain. Reads ai-docs/sources.yaml, fetches every source that is missing or older than 30 days, writes faithful markdown mirrors, and regenerates the ai-docs/index.md catalog. Use when the user asks to sync, refresh, or add AI docs, set up the knowledge base, or mentions ai-docs being stale or missing a topic — even without naming /kb.
argument-hint: [add url [group] | --force]
allowed-tools: Bash(curl *), WebFetch
model: opus
effort: high
---

# Purpose

Keep the `ai-docs/` knowledge base in sync with its manifest: fetch whatever `ARGS` and staleness demand, mirror each source faithfully, and regenerate the index so agents can navigate the cache.

## Variables

ARGS: $ARGUMENTS — empty (normal sync), `--force` (refetch everything), or `add <url> [group]` (register a new source, then sync it)
MANIFEST: `ai-docs/sources.yaml` — entries of url / file / topic / fetched; the only tracked KB file
INDEX: `ai-docs/index.md` — the agent-facing catalog
FETCHED: a mirror's own `fetched:` frontmatter — this device's sync date for that page
STALE_AFTER: `30` days

## Instructions

- The MANIFEST is the source of truth. Never fetch a URL that isn't in it; `add` registers first, then syncs.
- **The MANIFEST's `fetched` stays `null`.** It is tracked in git and shared across devices, so a date there conflicts the moment a second device syncs. FETCHED is the device-local truth; read staleness from it and never write a date into the MANIFEST.
- **Mirror format** — every cached doc is: YAML frontmatter (`source:` canonical URL, `fetched:` today), a `> **In here:**` line with 3 short bullets, then a faithful markdown conversion of the page. No commentary, no summarizing away detail.
- **Fetching is delegated** — spawn one `kb-fetcher` subagent per work-set entry, in parallel; each delegation message is just the entry's `url` and the absolute target path. The agent canonicalizes redirects, mirrors the page, and returns `OK <file> <canonical url>` plus a one-line summary (or `FAIL <file>: <reason>`). Fetched pages never enter this context.
- **Dedupe on canonicalization** — write each returned canonical URL back to the MANIFEST; if two entries resolve to the same canonical URL, keep one, drop the other, and say so in the report.
- Only the `## Cached official docs` table in INDEX is generated; leave `## Project notes` untouched. Topic and file link come from the MANIFEST, the fetched date from FETCHED.
- **Cap** — keep the MANIFEST at ≈40 entries; over the cap, report entries no `specs/**/decisions.md` cites as eviction candidates. Never auto-delete.

## Workflow

1. Parse ARGS. For `add <url> [group]`: append a MANIFEST entry (group defaults by host — Anthropic blog posts (claude.com/blog) → `anthropic/blog`, other anthropic/claude hosts → `anthropic`, Codex docs (learn.chatgpt.com) → `openai/codex`, OpenAI cookbook pages → `openai`, else the site's name; group keys are path-like and double as the folder under `ai-docs/`; derive `file` from the group + page slug, draft a `topic`, `fetched: null`).
2. Read MANIFEST. Work set = entries whose `file` is missing, or whose FETCHED is unreadable or more than STALE_AFTER days old; `--force` selects all; `add` selects just the new entry. Empty work set → report "all fresh" and stop.
3. Fetch the work set: fan out `kb-fetcher` subagents per the Instructions and collect their OK/FAIL lines.
4. Update MANIFEST for entries that returned OK: canonical `url` only. Leave `fetched: null` — the subagent already stamped today's date into the mirror's FETCHED.
5. Regenerate the INDEX table: one row per MANIFEST entry — topic, file link, and the mirror's FETCHED (`—` if the mirror is missing on this device).
6. Report.

## Report

- Counts: newly fetched / refreshed (stale) / skipped (fresh) / failed.
- Any URL canonicalized to a new address, and any entries deduped.
- On failures: which URLs, the error, and that their `fetched` was left unchanged — never mark a failed fetch as fresh.
