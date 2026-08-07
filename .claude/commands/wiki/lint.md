---
description: Health-check the ai-docs wiki — orphans, broken links, schema violations, staleness, contradictions; fixes what it can, reports the rest, logs the pass. Run weekly by routine and on demand.
model: opus
effort: high
---

# Purpose

Sweep the wiki for drift, repair what is mechanical, and report what needs judgment.

## Scope

Every domain folder present on this machine, plus `ai-docs/wiki/index.md` and
`ai-docs/wiki/log.md`. `ai-docs/wiki/personal/` is gitignored, so a run against a fresh
clone never sees it — such a run lints the shared domains only and must not claim to
have checked personal. Personal lint happens locally, on demand.

Read `.claude/rules/wiki-layer/wiki-standards.md` first; it defines the schema, the
length bounds, and the privacy obligations every check below tests against. A wiki
holding only the seed files is clean, not broken — report clean and stop.

## Checks

- **Orphans** — pages no index row and no `[[wikilink]]` reaches.
- **Broken wikilinks** — `[[targets]]` with no page behind them.
- **Index ↔ page drift** — index rows with no page, pages with no row, and rows whose
  Type, Status, or Updated cell disagrees with the page's frontmatter.
- **Schema violations** — a missing or malformed field among the seven, an illegal
  `type`, `domain`, or `status` value, or `related:` out of sync with the page's own
  inline links.
- **Staleness** — a page whose cited source has changed since its `updated:` date, and a
  `disputed` page whose sources now settle the dispute.
- **Contradictions** — claims across pages that cannot both hold. Flag both sides
  `disputed`, each cross-referencing the other.
- **Secret or PII leakage** — keys, tokens, credentials, addresses, phone numbers,
  account numbers, unpublished third-party names in page content, in every domain.
- **Missing mirrors** — a cited `ai-docs/` mirror absent here. Mirrors are device-local:
  report it as "run `/harness-layer:kb`", never as a broken citation.
- **Personal boundary** — a personal page referencing any file outside `personal/`, or
  personal content named in the shared index or log.
- **Cramming and thinning** — pages over the length bound or structured as a timeline;
  pages under it or grown only by tacked-on sentences.

## Fix or report

Fix mechanical findings in place and count them: index rows, link targets, frontmatter
format and field order, `related:` sync. Redact a leaked secret or PII immediately and
report the page. Report everything that needs judgment — contradictions, staleness that
needs a re-read of the source, cramming and thinning, missing mirrors — without
rewriting the pages yourself.

## Log the pass

Append to the shared log: the heading, then a blank line, then the payload line on the
next non-blank line (the auto-formatter keeps a blank line between them).

```text
## [YYYY-MM-DD] lint | <scope> | <summary>
missing-pages: <comma-list or none> · mechanical-fixes: <N>
```

`<scope>` names the domains covered. `missing-pages` lists the page names the findings
call for — broken-wikilink targets and index rows with no page. `mechanical-fixes` is
the count of fixes applied. Both fields feed `/wiki:status`, so write them in exactly
this shape. A run that also covered personal logs that half to
`ai-docs/wiki/personal/log.md`; the shared log never names personal content.

## Weekly routine

The unattended pass is a cloud routine the user creates once with `/schedule`. Routines
are account-bound and cannot be committed, so this is the prompt to give it:

```text
Weekly wiki lint. Run /wiki:lint over ai-docs/wiki/ in this repository, apply the
mechanical fixes, and open a pull request carrying them. Put the judgment findings and
the log payload line in the PR body. The personal domain is gitignored and absent from
this clone — do not lint or report on it.
```

Configure it as a weekly schedule trigger on this repository. Each run clones the
default branch fresh and pushes to a `claude/`-prefixed branch, which is why the fixes
arrive as a PR and the personal domain is out of reach.

## Report

```text
✅ Wiki Lint — <scope>
Pages checked: <N> · mechanical fixes: <N> · findings for review: <N>
Fixed: <one line per class>
Review: <one line per judgment finding, with page paths>
Log: <the entry appended>
```
