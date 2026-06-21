# Claude Opus 4.8 Principles for Artifact Design

What changed in Opus 4.8 that affects how you write commands, skills, and subagents. Apply these throughout drafting; double-check during anti-pattern review.

4.8 performs well out of the box on prompts that were already tuned for 4.7 — the direction of travel (literal following, conservative tool/subagent use, calibrated verbosity, direct tone) is the same, only stronger. The behaviors below are the ones that most often need tuning when an artifact moves from 4.7 to 4.8. The single biggest change: **effort is now the primary lever**, more so than for any prior Opus.

## 1. Effort is the dominant lever

Effort matters more for 4.8 than for any previous Opus model — experiment with it actively when upgrading an artifact. 4.8 respects effort levels strictly, especially at the low end: at `low` and `medium` it scopes work to exactly what was asked rather than going above and beyond, which is good for latency and cost but risks under-thinking on moderately complex tasks. The levels:

- `max` — intelligence-demanding tasks; can show diminishing returns and is sometimes prone to overthinking.
- `xhigh` — best setting for most coding and agentic use cases.
- `high` — balances token usage and intelligence; the minimum for most intelligence-sensitive work.
- `medium` — cost-sensitive use cases that trade off some intelligence.
- `low` — short, scoped, latency-sensitive tasks that are not intelligence-sensitive.

**Implication for artifact design:** When an artifact's quality depends on deep reasoning or more tool use, the first lever is effort, not prose. If you observe shallow reasoning or under-tooling, *raise effort* rather than prompting around it with "think harder" language.

- For **subagents**, set `effort` deliberately in frontmatter: `xhigh` for hard coding/agentic work, `high` as a sensible default for reasoning-sensitive subagents, `low`/`medium` only for scoped, latency-sensitive helpers (e.g. a cheap read-only researcher).
- For **skills and commands** (invoked by the user, effort set by the session), mention the recommended effort in user-facing notes when quality depends on it.
- At `high`, `xhigh`, or `max`, recommend a large max output token budget (start at 64k) so the model has room to think and act across tool calls and subagents.

## 2. Thinking is off by default

On 4.8, thinking is off unless `thinking: {type: "adaptive"}` is explicitly enabled. When enabled, adaptive thinking decides on its own when and how deeply to reason based on query complexity and the `effort` parameter — you do not grant it "permission" to think. The adaptive triggering behavior is steerable: large or complex system prompts can make the model think more often than you want.

**Implication for artifact design:** Drop reasoning-permission phrases — they are no-ops at best, and on simple tasks they encourage over-thinking:
- ❌ "Take a deep breath and work through this step by step"
- ❌ "Think carefully before responding"
- ❌ "Let's solve this step by step"

The lever for reasoning depth is effort, not prose. If an artifact (especially a large skill) causes the model to think more than warranted on simple requests, add a short steer: *"Thinking adds latency and should only be used when it meaningfully improves answer quality — typically multi-step reasoning. When in doubt, respond directly."*

## 3. Even more literal instruction following

4.8 interprets prompts literally and explicitly, particularly at lower effort levels. It does not silently generalize an instruction from one item to another, and it does not infer requests you didn't make. The upside is precision and less thrash — it's well-suited to structured extraction and predictable pipelines.

**Implication for artifact design:** State scope explicitly — every artifact should answer "what's in" and "what's out" rather than leaving it implicit. When you want the model to apply something broadly, say so: *"Apply this convention to every commit, not just the first one"* / *"Apply this formatting to every section, not just the first."* This was true on 4.7 and is even more load-bearing on 4.8 at `low`/`medium` effort.

## 4. Tool use favors reasoning even more

4.8 favors reasoning over tool calls more strongly than 4.7 — this produces better results in most cases. Higher effort is the main lever that increases tool usage; `high` and `xhigh` show substantially more tool use in agentic search and coding.

**Implication for artifact design:** If an artifact under-triggers a needed tool (e.g. a web-search or file-read tool the workflow depends on), the first fix is raising effort, and the second is clearly describing *when and why* the tool is appropriate. Aggressive "MUST USE" language is not the fix and tends to backfire.

## 5. Fewer subagents by default

4.8 spawns fewer subagents than prior models. This is usually correct — fewer unnecessary fan-outs — but it is steerable through prompting.

**Implication for artifact design:** If an artifact genuinely benefits from parallel subagent work, give explicit guidance about when fan-out is desirable: *"Spawn subagents in parallel when fanning out across multiple files or independent items. For single-file edits or work you can complete directly, do it inline rather than delegating."*

When the fan-out is not just desirable but **load-bearing** — it must reliably spawn N, run an independent verification panel, sweep at a scale that floods one context, or loop until dry — a prose "spawn N subagents" instruction under-fires here, and the fix is to escalate from inline spawning to a **dynamic workflow**, whose `agent()` calls execute deterministically. The bar and the shape ladder live in `decision-tree.md` → `dynamic-workflows.md`. Keep the conservative default otherwise: parallelism alone is not the bar.

## 6. Higher-quality progress updates — remove the scaffolding

4.8 provides more regular, higher-quality user-facing updates throughout long agentic traces, without prompting.

**Implication for artifact design:** Remove interim-status scaffolding from older artifacts — instructions like *"After every 3 tool calls, summarize progress"* are now redundant and add unnecessary rigidity. If the length or content of the model's updates isn't calibrated to your use case, describe what a good update looks like and give an example, rather than forcing a fixed cadence.

## 7. Response length calibrates to complexity — positive examples win

4.8 calibrates response length to how complex it judges the task to be, rather than defaulting to a fixed verbosity: short answers on simple lookups, much longer ones on open-ended analysis.

**Implication for artifact design:** Specify desired output length and structure explicitly when it matters (the "Success Brief" pattern: exact word count, bullet count, section structure). To *reduce* verbosity, a positive example showing the right level of concision is more effective than negative "do not over-explain" instructions or a list of what to avoid.

## 8. Tone is direct, less validation-forward

4.8's default voice is direct and opinionated, with minimal validation-forward phrasing ("great question!") and sparing emoji.

**Implication for artifact design:** Match this voice in templates. Don't instruct artifacts to "be warm and conversational" unless that's a deliberate product decision (customer-facing chat). For internal tooling, direct is the right default — and if you do need warmth, state it explicitly and re-check it against the new baseline.

## 9. Frontend defaults — strong house style, but less prompting needed now

4.8 has strong design instincts with a persistent default house style: warm cream/off-white backgrounds (~`#F4F1EA`), serif display type (Georgia, Fraunces, Playfair), italic word-accents, and a terracotta/amber accent. This reads well for editorial, hospitality, and portfolio briefs but feels off for dashboards, dev tools, fintech, healthcare, or enterprise apps — and it shows up in slide decks too.

Importantly, 4.8 needs **less** frontend prompting than previous models to avoid generic "AI slop" output — a long styling snippet is no longer necessary and can be counterproductive. Generic negations ("don't use cream," "make it clean") tend to shift the model to a *different* fixed palette rather than producing variety. Two approaches break the default reliably: (1) specify a concrete alternative palette/typeface — the model follows explicit specs precisely; (2) have the model propose 3–4 distinct visual directions first and let the user pick (this replaces `temperature` for design variety).

**Implication for artifact design:** If the artifact produces frontend output, point it at the `frontend-design` skill at *its* runtime rather than duplicating a long styling block. Keep any inline guidance minimal. If the default house style doesn't fit the domain, specify a concrete alternative or instruct the artifact to propose directions before building.

## 10. Code review harnesses interpret severity filters literally

4.8 is meaningfully better at finding bugs (higher recall *and* precision in internal evals). But if a review artifact was tuned for an earlier model, you may see *lower* measured recall — a harness effect, not a regression. When a review prompt says "only report high-severity issues," "be conservative," or "don't nitpick," 4.8 follows that instruction more faithfully: it investigates just as thoroughly, then declines to report findings it judges below your stated bar.

**Implication for artifact design:** For review-flavored artifacts, separate finding from filtering. Instruct the model that its job at the finding stage is *coverage*, with confidence and severity tags, and move filtering to a downstream step:

> "Report every issue you find, including ones you are uncertain about or consider low-severity. Do not filter for importance or confidence at this stage — a separate verification step will do that. For each finding, include your confidence level and an estimated severity so a downstream filter can rank them."

If the artifact must self-filter in a single pass, be concrete about the bar rather than qualitative ("important"): e.g. "report any bug that could cause incorrect behavior, a test failure, or a misleading result; only omit pure style or naming nits."

## 11. Interactive coding — specify upfront, reduce turns

4.8 tends to use more tokens in interactive, multi-turn coding sessions than in single-turn autonomous runs, because it reasons more after each user turn. This improves long-horizon coherence but costs tokens, and ambiguous prompts spread across many turns reduce both efficiency and sometimes performance.

**Implication for artifact design:** For artifacts that drive interactive coding workflows, front-load the spec — capture task, intent, and constraints in the first turn — and minimize the number of required back-and-forth interactions (e.g. design in an "auto" mode that proceeds on sensible defaults). Pair this with `xhigh`/`high` effort.

## Summary table

| Pattern from older models | 4.8-tuned replacement |
|---|---|
| "Take a deep breath and work through this step by step" | Drop it; thinking is off by default and depth comes from `effort` |
| "Think harder / be more thorough" sprinkled to force depth | Raise `effort` (subagent frontmatter) or recommend a higher session effort |
| "CRITICAL: You MUST use this tool" | Raise effort first; otherwise "Use this tool when [specific condition]" |
| "If in doubt, use [tool]" | Describe specifically when the tool is appropriate |
| "After every N tool calls, summarize progress" | Remove — 4.8 gives good progress updates natively |
| "You are a senior X with 10,000+ Y" | One focused sentence on the relevant lens |
| "I'll tip you $100" / "I bet you can't" | Explicit success brief with concrete criteria |
| Implicit scope | Explicit "what's in / what's out" (even more important at low/medium effort) |
| "Provide a thorough analysis" | Concrete length target + a positive example of the desired concision |
| Long frontend styling block | Minimal pointer to `frontend-design`; specify a concrete palette or propose-directions-first |
| "Only report high-severity issues" (in review prompts) | "Report all findings with confidence + severity tags; filtering happens downstream" |
