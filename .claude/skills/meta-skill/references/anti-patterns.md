# Anti-Patterns & Pre-Ship Review

Scan every draft for these and replace each before shipping. If the user explicitly wants one, explain the cost once and comply only if they confirm.

## Older-model holdovers to cut

| Pattern | Looks like | Why it's wrong on 4.8 | Replace with |
|---|---|---|---|
| Fake incentives | "I'll tip you $100 for a clean result." | Literal reading strips the social signal; at worst asks about payment. | A success brief: concrete criteria for "good." |
| Competitive framing | "I bet you can't keep it under 72 chars." | No ego to bait. | State the constraint and its *why*. |
| Reasoning-permission prose | "Take a deep breath / think step by step." | Thinking is off unless adaptive is enabled; depth comes from `effort`. No-op at best, overthinking at worst. | Set `effort` (frontmatter or session). |
| All-caps MUST/NEVER without a why | "You MUST always Read first." | Aggressive language now over-triggers, or on review tasks over-filters. | Sentence-case + the reason. Keep caps only if the model would do the wrong thing without them. |
| Inflated personas | "Senior dev, 10,000+ PRs at a FAANG." | Read literally; numbers add nothing. | One focused sentence on the relevant lens. |
| Over-triggering tool guidance | "If in doubt, use the Read tool." | Vague "in doubt" wastes calls; 4.8 favors reasoning. Lever for more tool use is effort. | Describe *when* the tool fits, specifically. |
| Vague stakes | "Get this wrong and we lose weeks." | Threat with no actionable content. | Fold the consequence into the constraint's *why*. |
| Unspecified output length | "Provide a thorough analysis." | 4.8 calibrates length to complexity; "thorough" is unanchored. | Specify length/structure, or give a positive concision example. |
| Forced progress cadence | "Summarize after every 3 tool calls." | 4.8 gives good updates natively; cadence fights its pacing. | Remove. If updates are miscalibrated, describe + show one good one. |
| Prompting around under-thinking | "Think very hard about every edge case." | Depth is governed by `effort`, not prose, especially at low/medium. | Raise `effort`; reserve prose for *steering* when to think. |
| Frontend "AI slop" | Inter, white bg, purple gradients — or a long anti-slop block. | 4.8's house defaults (cream/serif/terracotta) misfit dev tools; 4.8 needs *less* frontend prompting, and generic negations just shift to another fixed palette. | Point at `frontend-design`, or give a concrete palette + typeface, or have it propose 3–4 directions first. |

## Skill-specific anti-patterns

- **Generic / summary descriptions** ("Helps with documents") — won't trigger. Name the user's actual phrasings; be slightly pushy (Claude under-triggers). Write it for the model, not a human reader.
- **Stating the obvious** — paragraphs telling Claude what it already does. Delete if removing them wouldn't change output.
- **Railroading** — rigid step lists where goal + constraints would generalize. Exception: genuinely order-dependent / irreversible ops.
- **Unbroken 500+ line body** — split into `references/`; the body is the recurring per-turn cost.
- **Deeply nested references** — `SKILL.md → a.md → b.md` gets partially read with `head`. Keep one level deep.
- **Windows paths** — `scripts\helper.py` breaks on Unix. Forward slashes only.
- **Unqualified MCP tool names** — use `Server:tool`, not bare `tool`.
- **Description with `< >` or XML tags** — fails the validator. Plain text only.
- **Task skills auto-triggerable** — side-effect skills (`/deploy`, `/commit`) without `disable-model-invocation: true` may run because the code "looks ready."
- **Offering too many options** — "use pypdf or pdfplumber or PyMuPDF or…" Give one default with an escape hatch.
- **Time-sensitive content in the body** — "before August 2025, use the old API." Use a collapsed "old patterns" section instead.

## BAD → GOOD descriptions

| BAD | GOOD |
|---|---|
| `description: A helpful skill for PostgreSQL migrations.` | `description: Drafts safe, reversible PostgreSQL migrations following the project's conventions. Use when the user adds/drops a column, changes a constraint, backfills data, adds an index, or mentions "migration" or "alter table" — even without naming a migration.` |
| `description: I can help you with documents.` | `description: Extracts text and tables from PDFs, fills forms, and merges documents. Use when the user mentions PDFs, forms, or document extraction.` |
| `description: For data analysis.` | `description: Analyzes sales data in Excel and CRM exports. Use for pipeline analysis, revenue tracking, and sales reports — not log/metrics analysis (use /log-analysis for that).` |
| `description: Builds dashboards.` | `description: Builds fast internal dashboards for company data. Use whenever the user mentions dashboards, data visualization, internal metrics, or wants to display company data — even if they don't say "dashboard".` |

The shift each time: vague summary → third person, front-loaded, specific triggers + user vocabulary, slightly pushy, and (where it matters) a NOT-boundary that routes to a sibling.

## Pre-ship review checklist

Run before shipping. Any failure → fix, then re-read the whole draft fresh.

**Triggering & metadata**
- [ ] `description` is third person, front-loaded, names user phrasings, slightly pushy
- [ ] `description` ≤ 1,024 chars, no `< >` / XML; `description` + `when_to_use` ≤ 1,536 combined
- [ ] `when_to_use` is non-redundant (gate/routing) or omitted
- [ ] Directory name is lowercase-hyphen; not relying on `name` to set the command

**Body & structure**
- [ ] Body under 500 lines (target 200–300); nothing states what Claude already does
- [ ] References one level deep; files >~300 lines have a ToC
- [ ] Workflow gives goal + constraints, not a rigid script (unless order is load-bearing)
- [ ] Gotchas section present if the skill has any production history
- [ ] Forward slashes everywhere; MCP tools as `Server:tool`; bundled paths via `${CLAUDE_SKILL_DIR}`

**Model behavior (4.8)**
- [ ] No fake incentives, competitive framing, inflated personas, vague stakes
- [ ] No reasoning-permission prose / "think harder"; depth set via `effort`
- [ ] No all-caps MUST/NEVER without a *why*; no "if in doubt, use X"
- [ ] No forced progress-update cadence
- [ ] Output length/structure specified where it matters
- [ ] Fan-out is conservative by default; explicit only where parallelism is wanted
- [ ] No "be warm/enthusiastic" unless a customer-facing voice is deliberate

**Frontmatter correctness**
- [ ] Task skills with side effects set `disable-model-invocation: true`
- [ ] `allowed-tools` / `disallowed-tools` match what the skill actually needs
- [ ] `context: fork` paired with an `agent`, and used only for skills with a real task
- [ ] Hooks added only where determinism matters (and not for what the model does reliably)

## Reference Docs
- https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-4-8
- https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices#anti-patterns-to-avoid