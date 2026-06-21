# Skill Categories (Thariq's 9-Category Framework)

After cataloging hundreds of internal skills at Anthropic, Thariq's team noticed they cluster into 9 recurring categories. The best skills fit cleanly into one; the more confusing ones straddle several.

Use this taxonomy in **Phase 1** to scope what the skill is for. A clean category answer tells you what to bundle, whether to auto-trigger or user-invoke, whether hooks help, and whether state matters.

**If a request spans multiple categories cleanly, consider splitting into composable skills** rather than one mega-skill — Claude's planning is sharper when each skill has a clear job.

## At a glance

| # | Category | Trigger style | Hooks common? | State? | Examples |
|---|---|---|---|---|---|
| 1 | Library & API Reference | Auto on lib/path keywords | No | No | `billing-lib`, `frontend-design` |
| 2 | Product Verification | User-invoked or chained | Yes (`Stop`, `PostToolUse`) | Sometimes (fixtures) | `signup-flow-driver`, `checkout-verifier` |
| 3 | Data Fetching & Analysis | Auto on metric/source keywords | Rarely | Cache results | `funnel-query`, `grafana` |
| 4 | Business Process & Team Automation | User-invoked | Sometimes (`Stop` to confirm) | Log of prior runs | `standup-post`, `weekly-recap` |
| 5 | Code Scaffolding & Templates | Auto on "new X" / "scaffold" | Sometimes (lint) | No | `new-migration`, `create-app` |
| 6 | Code Quality & Review | Auto on review, or via PR hook | Yes (`PostToolUse`) | Project exceptions | `adversarial-review`, `code-style` |
| 7 | CI/CD & Deployment | User-invoked (`disable-model-invocation: true`) | Yes (`PreToolUse` blockers) | Pipeline state | `deploy-<service>`, `cherry-pick-prod` |
| 8 | Runbooks | Auto on alert/error keywords | Sometimes (`Stop` to save report) | Heavy (past incidents) | `oncall-runner`, `log-correlator` |
| 9 | Infrastructure Operations | User-invoked | Yes (`PreToolUse` on destructive ops) | Audit log | `<resource>-orphans`, `dependency-management` |

## Per-category notes (what makes each one different)

**1. Library & API Reference** — The category where Thariq Tip 1 (don't state the obvious) matters most. Public-API content Claude already knows doesn't earn its place; internal quirks, deprecations, and rate-limit details do. Bundle a Gotchas section.

**2. Product Verification** — Worth real engineering investment. Thariq: *"it can be worth having an engineer spend a week just making your verification skills excellent."* The difference between "Claude says it works" and "we have proof."

**3. Data Fetching & Analysis** — Use the `config.json` setup pattern (Tip 5); hardcoding dashboard IDs makes the skill non-shareable. Cache results in `${CLAUDE_PLUGIN_DATA}` (Tip 7) to avoid hammering data sources.

**4. Business Process & Team Automation** — Memory of prior runs keeps voice and format stable. Resist railroading — frame as "produce a standup post in our format," not "do these 8 steps."

**5. Code Scaffolding & Templates** — Composition matters. Often pairs with Code Quality (validation), CI/CD (committing the result), and Library Reference (using the scaffolded framework correctly). The skill produces a known-correct skeleton; the model fills the variables.

**6. Code Quality & Review** — Watch the severity-filter pitfall: don't say "only report high-severity issues" (the model will filter at the finding stage). Say "report all findings with severity tags; filtering happens downstream." Often better as a **subagent** for context isolation.

**7. CI/CD & Deployment** — Almost always `disable-model-invocation: true`. Treat like a `/careful` mode: the *only* path to production, paranoid by default. `allowed-tools` is doing real work here — pre-approve specific deploy commands, deny everything else.

**8. Runbooks** — Heavy `${CLAUDE_PLUGIN_DATA}` use; accumulating past incidents makes the runbook smarter. Prime candidates for the Gotchas section — every postmortem contributes a gotcha.

**9. Infrastructure Operations** — The point is making destructive operations easier to do correctly than wrong. Default to `--dry-run`, require explicit confirmation for irreversible steps, log everything. Strongest candidates for `/careful`-style on-demand hooks (Tip 9).

## How to use this in Phase 1

After capturing intent, ask:

1. **Which category fits cleanest?**
2. If multiple, **does it really need to be one skill, or two composable ones?**
3. **What does that category suggest** for bundled resources, triggers, and hooks?

Most categories above point to skills. Code Quality & Review is sometimes better as a subagent. Library Reference is occasionally a command if it's truly trivial.

## When it doesn't fit any category

Two possibilities:
- **Wrong scope** — zoom in to the actual atomic workflow; it probably fits one
- **Genuinely novel** — fine. The taxonomy is a heuristic, not a gatekeeper

Before declaring novelty, double-check by re-reading the table. Most apparent novelty is an unusual combination of two categories.
