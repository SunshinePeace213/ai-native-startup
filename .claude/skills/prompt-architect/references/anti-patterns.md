# Anti-Patterns: Older-Model Holdovers + Thariq-Derived Patterns

Hard filter during Phase 3 (REVIEW). Scan the draft for every pattern; replace each one. If the user explicitly asks for one, explain the cost once and only comply if they confirm.

Two groups:

1. **Older-model holdovers** — Patterns 1–10 below. Covered in full here.
2. **Thariq-derived patterns** — canonical in `thariq-principles.md`; summary at the bottom.

## Pattern 1 — Fake monetary incentives

**Looks like:** *"I'll tip you $100 for a clean commit message."*

**Why deprecated:** 4.8's literal interpretation strips the social-pressure signal. At worst, asks about payment terms.

**Replacement:** A **Success Brief** stating what good looks like concretely (subject under 72 chars, Conventional Commits format, body explains why not what, no emoji, no trailing period).

## Pattern 2 — Competitive framing

**Looks like:** *"I bet you can't keep the subject under 72 chars. Most models fail. Show me."*

**Why deprecated:** Same root as P1. No ego to bait.

**Replacement:** State the constraint and its *why*: *"Keep the subject under 72 chars so it displays cleanly in `git log --oneline`."*

## Pattern 3 — Reasoning-permission phrases

**Looks like:** *"Take a deep breath and work step by step."* / *"Think carefully before answering."*

**Why deprecated:** On 4.8 thinking is off unless adaptive thinking is explicitly enabled, and reasoning depth is governed by the `effort` parameter — not by prose. The phrase is a no-op at best and encourages over-thinking on simple tasks at worst.

**Replacement:** Nothing, or set the right effort. For a subagent, set `effort: xhigh` in frontmatter for hard multi-step work; for a skill/command, note the recommended session effort if quality depends on deep reasoning. Effort — not "think harder" prose — is the lever.

## Pattern 4 — All-caps MUSTs without reasoning

**Looks like:** *"You MUST always Read before answering."* / *"NEVER make changes without approval."*

**Why deprecated:** Aggressive language now causes over-triggering, or on review tasks, over-filtering. The bar for keeping caps: *will the model do the wrong thing without them?* If no, drop them.

**Replacement:** Explain the *why* in sentence case: *"Read the relevant files before answering — speculation is unreliable and file contents may have changed."*

## Pattern 5 — Inflated persona specifics

**Looks like:** *"You are a senior dev who has reviewed 10,000+ PRs at a FAANG."*

**Why deprecated:** 4.8 reads literally; inflated numbers add no value.

**Replacement:** One focused sentence (*"You are a code reviewer specializing in security and concurrency."*), or invoke `tech-company-personas` for a real persona.

## Pattern 6 — Over-triggering tool guidance

**Looks like:** *"If in doubt, use the Read tool."* / *"When uncertain, search the web."*

**Why deprecated:** Vague "in doubt" triggers waste tool calls without improving results. On 4.8 the lever for more tool use is raising effort (`high`/`xhigh` show substantially more tool use); 4.8 otherwise favors reasoning over tool calls, so vague trigger phrasing won't reliably get it there.

**Replacement:** Describe specifically *when* the tool fits: *"Use Read when the user references a specific file by path, when reasoning depends on file contents you haven't seen, or when the user asks 'what does X do' about something in the codebase."*

## Pattern 7 — Vague stakes / consequence framing

**Looks like:** *"If you get this wrong, the team has to redo weeks of work."*

**Why deprecated:** Vague threats without actionable content. Mild form (explaining *why* a constraint matters) is fine.

**Replacement:** Fold the consequence into the *why* clause for the relevant constraint: *"Vague subjects ('fixed stuff') make `git bisect` and `git blame` slower because reviewers can't tell what each commit did without reading the diff."*

## Pattern 8 — Unspecified output length

**Looks like:** *"Provide a thorough analysis."* / *"Write a detailed summary."*

**Why deprecated:** 4.8 calibrates length to complexity. *"Thorough"* leaves the calibration unanchored.

**Replacement:** Specify length or structure: *"200-300 word analysis covering: architecture overview, top three risks, recommended next steps."* Or a table: *"columns: file, issue type, severity, suggested fix."* To *reduce* verbosity, a positive example of the desired concision beats negative "don't over-explain" instructions.

## Pattern 9 — Overly nested headings inside artifacts

**Looks like:** A command file with 6 heading levels, one line each.

**Why a problem:** Suggests the artifact is trying to be a reference doc. That content belongs in `references/`.

**Replacement:** Artifact body ≤ 200 lines where possible; 2-3 heading levels max; push detail into `references/<topic>.md`.

## Pattern 10 — Frontend "AI slop" defaults

**Looks like:** Frontend output that ships with Inter, white bg, purple gradient cards.

**Why a problem:** 4.8's house defaults (warm cream ~`#F4F1EA`, serif display, terracotta/amber accent) don't fit dev tools, dashboards, fintech — and they appear in slide decks too. A second trap: piling on a long anti-slop styling block. 4.8 needs *less* frontend prompting than older models, and generic negations ("don't use cream") just shift it to a different fixed palette.

**Replacement:** Point at `frontend-design` skill with minimal inline guidance, or specify a concrete palette + typeface (the model follows explicit specs precisely), or instruct the model to propose 3-4 distinct directions first and let the user pick (this replaces `temperature` for design variety).

## Pattern 11 — Forced progress-update scaffolding

**Looks like:** *"After every 3 tool calls, summarize what you've done so far."* / *"Emit a status line before each step."*

**Why a problem:** 4.8 provides regular, higher-quality user-facing progress updates on long agentic traces without prompting. Forced cadence is redundant and adds rigidity that fights the model's own pacing.

**Replacement:** Remove the scaffolding. If the length or content of the model's updates isn't calibrated to the use case, describe what a good update looks like and give one example — don't mandate a fixed cadence.

## Pattern 12 — Prompting around under-thinking instead of raising effort

**Looks like:** *"Think very hard about this."* / *"Be extremely thorough and consider every edge case."* sprinkled through the body to force depth.

**Why a problem:** On 4.8, reasoning depth and tool usage are governed primarily by the `effort` parameter — more so than on any prior Opus. At `low`/`medium`, 4.8 deliberately scopes work to what was asked; piling on "think harder" prose doesn't reliably override that and just adds tokens.

**Replacement:** Set the right effort. For a subagent, use `effort: xhigh` (hard coding/agentic) or `high` (reasoning-sensitive) in frontmatter. For a skill/command, recommend the session effort in user-facing notes. Reserve prose for *steering* thinking (when to think, when to respond directly), not for *forcing* it.

---

## Thariq-derived patterns (canonical: `thariq-principles.md`)

- **Stating the obvious** (Tip 1) — paragraphs that tell Claude what it already does well. Test: would deleting this change Claude's output? If no, delete.
- **Railroading** (Tip 4) — rigid step-by-step where goal + constraints would generalize better. Exception: workflows where order is genuinely load-bearing.
- **Generic, summary-style descriptions** (Tip 6) — descriptions written for human README-readers rather than for Claude scanning a listing. Must name specific user phrasings; be slightly emphatic.

---

## Review checklist (use during Phase 3 REVIEW)

### Older-model holdovers
- [ ] No "$100 tip" or other fake incentive (P1)
- [ ] No "I bet you can't" or competitive framing (P2)
- [ ] No "take a deep breath" / reasoning-permission phrases (P3)
- [ ] No all-caps MUSTs/NEVERs/ALWAYSs without a *why* clause (P4)
- [ ] No inflated persona specifics ("10,000+ PRs") (P5)
- [ ] No "if in doubt, use X" over-triggering (P6)
- [ ] Vague stakes converted into specific consequences tied to behaviors (P7)
- [ ] Output length/structure is specified (P8)
- [ ] Body uses 2-3 heading levels max; long reference lives in `references/` (P9)
- [ ] If frontend is involved, `frontend-design` referenced or concrete palette given; no long anti-slop block (P10)
- [ ] No forced progress-update cadence ("summarize every N tool calls") (P11)
- [ ] Reasoning depth set via `effort`, not "think harder" prose; subagents that need depth carry `effort` (P12)
- [ ] No "be warm/conversational/enthusiastic" tone instruction unless a customer-facing voice is a deliberate decision — 4.8 defaults to a direct, low-validation voice (4-8-principles §8)

### Thariq-derived
- [ ] Nothing states what Claude already does well (Tip 1)
- [ ] Workflow gives goal + constraints, not a rigid script (Tip 4)
- [ ] Description names specific user phrasings, slightly emphatic, not a summary (Tip 6)

### Positive checks
- [ ] Skill has a Gotchas section if it has any production history (Tip 2)
- [ ] Bundled-script opportunities captured (Tip 8)
- [ ] State persisted to `${CLAUDE_PLUGIN_DATA}` if state matters (Tip 7)
- [ ] Per-installation setup uses the `config.json` pattern (Tip 5)
- [ ] If the build request is workflow-shaped (recognition-catalog match), the dynamic-workflow option was surfaced with its cost rather than silently defaulted to inline (`dynamic-workflows.md`)

If any check fails, fix it; then re-read the draft fresh to catch what the checklist missed.
