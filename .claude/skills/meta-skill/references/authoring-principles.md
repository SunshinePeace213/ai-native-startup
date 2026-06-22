# Authoring Principles

One merged list. Where Thariq's craft advice and the Opus 4.8 model behavior point the same way, it's stated once. Apply these while drafting; the pre-ship checklist in `anti-patterns.md` re-checks them.

## 1. Don't state the obvious

Claude is already smart. If deleting a paragraph wouldn't change Claude's output, delete it. The high-signal content is what pushes Claude *out of its defaults* — the canonical example is `frontend-design`, which exists only to steer away from Inter / white / purple-gradient defaults Claude reaches for unprompted. Cut "use clear variable names," "write good tests," "handle edge cases." The context window is shared, and a loaded body costs tokens every turn it stays in context.

**Test:** read each paragraph, ask "if I deleted this, would the output meaningfully change?" If no, delete.

## 2. Add a Gotchas section

The highest-signal section in a mature skill — specific things that bit someone and aren't in any official doc. The framing: a senior engineer whispering "this will bite you." Flat bullets, one or two sentences each: silent failures, order-of-operations not enforced by tooling, env vars that must be set/unset, rate limits, naming conventions downstream tools depend on. Put it near the top, after the overview. Skip it for brand-new skills with no production history; add the first gotcha the first time something breaks. The section compounds.

## 3. Use the filesystem for progressive disclosure

A skill is a folder; treat the whole filesystem as context engineering. Split detailed reference material into `references/<topic>.md`, organize by domain when there are variants, bundle deterministic work as `scripts/`. Tell Claude explicitly where to look. Keep references one level deep. (Mechanics in `structure.md`.) Don't split content that's short, needed every run, or clearer inline.

## 4. Don't railroad — give goals + constraints, not a script

A skill is reused across many requests the author never imagined. A rigid step-by-step procedure handles the imagined cases and breaks for the rest. Give Claude the **goal and the constraints** and let it find the path:

```markdown
Compose a commit message and create the commit. Push only if the user asked.
Constraints:
- Subject under 72 chars, Conventional Commits format
- Body explains *why*; the diff already shows *what*
- Don't push to a branch the user hasn't named
```

This compounds with Opus 4.8's autonomy. **Exception:** workflows where order is genuinely load-bearing — irreversible production ops, regulatory/legal procedures. There, be specific (low freedom). Match specificity to fragility: narrow bridge → exact steps; open field → direction + trust.

## 5. The setup/config.json pattern

Skills needing per-installation context (a Grafana URL, an account ID, a Slack channel) shouldn't hardcode it. Read `${CLAUDE_SKILL_DIR}/config.json`; if absent, ask the user (use `AskUserQuestion` for choices), write it, then proceed; if present, use it. Useful for data-fetching, business-process, and runbook skills. Skip when the skill is pure transformation or the info already lives in the codebase.

## 6. Write the description for the model

The description is a trigger document Claude scans to decide whether to load the skill — not a human README line. Third person, front-loaded, names the user's actual vocabulary, slightly pushy (Claude under-triggers — see principle 8). This is the single field that decides triggering; full guidance and the character caps are in `frontmatter.md`.

## 7. Persist state for skills that should improve over time

Append-only logs, JSON caches, or SQLite let a business-process or runbook skill get better across runs (e.g. log each run, read the last few at startup for consistency). Use a stable per-plugin data folder rather than writing inside the skill directory, which may be wiped on upgrade. **Caveat:** the specific variable for that folder (`${CLAUDE_PLUGIN_DATA}`) is not confirmed in current official docs — see the Unverified note in `frontmatter.md` before relying on it. Skip memory entirely for stateless skills.

## 8. Effort is the dominant capability lever — raise it, don't prompt around it

On Opus 4.8, reasoning depth and tool usage are governed primarily by `effort`, more than on any prior Opus. If a skill shows shallow reasoning or under-uses a needed tool, **raise effort** (`high`/`xhigh` show substantially more tool use), don't sprinkle "think harder." Set `effort` in frontmatter for skills whose quality depends on it; for user-invoked skills, note the recommended session effort in user-facing text. Thinking is off unless `thinking: {type: "adaptive"}` is set — reasoning-permission prose ("take a deep breath," "think step by step") is a no-op and encourages overthinking on simple tasks. At `max`/`xhigh`, recommend a large max-output budget (start 64k) so there's room to act across tool calls and subagents.

## 9. Be literal about scope

Opus 4.8 follows instructions literally, especially at lower effort — it won't silently generalize from one item to all, and won't infer requests you didn't make. State what's in and what's out. When something should apply broadly, say so: "Apply this to every section, not just the first." This is precision, not pedantry, and it's load-bearing at `low`/`medium`.

## 10. Be conservative with tools and subagents by default — explicit when you want fan-out

Opus 4.8 favors reasoning over tool calls and spawns fewer subagents by default. Usually correct. Don't fight it with aggressive "MUST USE" language. When fan-out is genuinely wanted, say so concretely:

```text
Spawn subagents in parallel when fanning out across multiple files or
independent items. For single-file work you can do directly, do it inline.
```

When parallel fan-out is *load-bearing* (independent verification panel, sweep that floods one context, loop-until-dry), prose under-fires — escalate to a deterministic workflow harness rather than relying on a "spawn N" instruction.

## 11. Remove forced progress-update scaffolding

Opus 4.8 emits regular, well-calibrated progress updates on long agentic traces on its own. Delete "after every 3 tool calls, summarize" — it's redundant and fights the model's pacing. If the *content* of updates isn't right for your use case, describe what a good update looks like and give one example; don't mandate a cadence.

## 12. Drop older-model prose

Cut `$100 tip`, "I bet you can't," inflated personas ("10,000+ PRs reviewed"), all-caps `MUST`/`NEVER` without a *why*, and vague stakes ("the team redoes weeks of work"). Opus 4.8 reads literally — these add tokens, not behavior, and at worst over-trigger or over-filter. Replace each with a concrete success brief: state what good looks like (exact constraints, length, structure) and the *why* behind each constraint. Bake-in tone too: 4.8 defaults to direct, low-validation prose — don't instruct "be warm/enthusiastic" unless a customer-facing voice is a deliberate decision.

## On output length and examples

When output shape matters, specify it (word count, bullet count, sections, or a table schema) — 4.8 calibrates length to perceived complexity, so "thorough" leaves it unanchored. To *reduce* verbosity, a positive example of the right concision beats negative "don't over-explain" instructions.

## Reference Docs
- https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-4-8
- https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices
- https://github.com/shanraisshan/claude-code-best-practice/blob/main/tips/claude-thariq-tips-17-mar-26.md, Thariq Shihipar (@trq212), "Lessons from Building Claude Code: How We Use Skills"