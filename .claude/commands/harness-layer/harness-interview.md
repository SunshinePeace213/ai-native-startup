---
description: Pre-plan interview pass — grills the user round by round through an interactive page until every decision needed to plan is locked, then hands back a finalized prompt and decisions ledger ready for /harness-layer:harness-plan
argument-hint: [detailed ideas or a prior pass's improved prompt]
model: fable
effort: high
disallowed-tools: Task, EnterPlanMode
---

# Harness Interview

Lock every open decision before planning. Take detailed ideas (or a prior discovery pass's improved prompt), answer from the codebase what it can answer, and interview the user on the rest — round by round through an interactive page — until the coverage ledger is clear. The deliverable is a finalized prompt plus a decisions ledger that `/harness-layer:harness-plan` drafts from without asking anything.

## Variables

DESCRIPTION: $1 — the detailed ideas, or a prior pass's improved prompt (may carry a `Worktree:` line)
DISCOVERY_DIR: `specs/<slug>/discovery/` — the chain's committed discovery home inside the worktree
ARTIFACT_RULES: `.claude/rules/harness-layer/artifacts.md` — craft, palette, and publish rules for the page
KNOWLEDGE_BASE: `ai-docs/` — cached official docs; catalog in `ai-docs/index.md`

## Instructions

- **INTERVIEW ONLY** — no spec files, no issues, no pushes; write only under `DISCOVERY_DIR`.
- If no `DESCRIPTION` is provided, stop and ask the user for one.
- Worktree: when `DESCRIPTION` carries a `Worktree:` line, `EnterWorktree(path: ...)` into it; otherwise derive a kebab-case `<slug>` and `EnterWorktree(name: "<slug>")`. Never write outside the worktree.
- **Explore first.** Answer from the codebase — and the relevant `KNOWLEDGE_BASE` docs when the task touches the harness surface (`.claude/`, `.agents/`, `.codex/`, `ai-docs/`, the memory files) — whatever they can answer; interview the user only on what they can't.
- **References early.** Always ask: "Is there existing code — a library, a vendor folder, prior art — that already does what you want? Point me at the path instead of describing it." Record any answer as a decision naming the path and what to take from it; the plan authors the Reference map from it.
- **One round at a time, biggest blast radius first.** Each round carries the open questions whose wording doesn't depend on unanswered ones, ordered by how much the answer would change the architecture.
- **Adaptive depth.** Match complexity — a light pass for chores, a deep pass for complex features. Don't interrogate trivial tasks.
- Commit the pass locally — `📝 docs(discovery): interview pass for <slug>`, no issue footer (no issue exists yet). Never push; the plan's first push carries the discovery commits.

## Coverage Ledger

Track each decision dimension as resolved, open, or N/A, and keep interviewing until none are open. Cover as applicable: scope & non-goals, users, success criteria & acceptance tests, data model, interfaces/APIs, edge cases & errors, performance & scale, security & authz, observability, rollout/migration, dependencies, testing, references. When the task touches the harness surface, also cover: invocation & trigger control, context budget (what loads always vs on demand), frontmatter (tools, model alias, effort), hook lifecycle & exit-code semantics, artifact choice (skill vs command vs subagent), and distribution (project vs user vs plugin). Mark irrelevant ones N/A.

## Round Loop

1. Build the ledger from `DESCRIPTION`; resolve what the codebase/KB answers; order the rest by blast radius.
2. Author the **Interview rounds** page per `ARTIFACT_RULES` into `DISCOVERY_DIR` — question cards (2–4 option chips with your pick badged "Recommended", free text per card), an "accept all recommendations" master control, and the ledger as a resolved/open/N/A sidebar. Publish best-effort; redeploy the same URL every round; on publish failure note "publish skipped" and continue with the local file.
3. Receive via ONE AskUserQuestion: options "Accept all remaining recommendations" and "Stop the interview here"; the user pastes the page's copy-as-prompt output via "Other".
4. Parse the answers, update the ledger, generate the next round. A residue of one or two simple follow-ups skips the page — ask directly via AskUserQuestion.
5. Ledger clear → final round: the page replays every decision for sign-off; on approval write the ledger, commit, and report.

## Output

- `DISCOVERY_DIR/decisions-draft.md` — the ledger in the decisions template's sections (Summary, Resolved Decisions with Q/A/Why, Assumptions, Open Questions / Out of Scope) so the plan transcribes it verbatim.
- The finalized prompt — standalone: the task with every locked decision folded in, the ledger path, and the chain line `Worktree: .claude/worktrees/<slug>` at the end.

## Report

```text
🎤 Interview Complete

Rounds: <N>
Page: <published URL — or local path (publish skipped)>
Worktree: .claude/worktrees/<slug>
Ledger: specs/<slug>/discovery/decisions-draft.md
Decisions: <resolved count> · Assumptions: <count> · Out of scope: <count>

Finalized prompt:

<the finalized prompt>

When you're ready, plan with:
/harness-layer:harness-plan "<finalized prompt>"
```
