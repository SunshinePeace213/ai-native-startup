---
name: grilling
description: Grill the user relentlessly about a plan, decision, or idea — frontier rounds over the design tree, every question carrying a recommended answer, facts looked up rather than asked. Use when the user wants to stress-test their thinking, clear the unknowns in a vague or ambiguous request, or uses any grill/interview/ask-me-questions phrasing. Not for the pipeline's own question sites (/harness-layer:harness-interview owns its page-based rounds; the plan's Readiness Gate its one bounded round) and not for menu-style confirmations.
argument-hint: [topic or plan to grill]
---

Interview the user relentlessly until you reach a shared understanding. Map the
topic as a **design tree**: every decision branches into the decisions that hang
off it.

Work the tree in **rounds**. The **frontier** is every decision whose
prerequisites are already settled — the questions you can ask *now* without
guessing at answers you haven't heard yet. Ask the whole frontier in one round,
each question with your recommended answer; a question whose answer depends on
another still open this round belongs to a later round. Wait for the user's
answers — each round reshapes the tree and pushes the frontier outward — then
recompute and ask the next round.

Round mechanics in this repo: a frontier of up to 4 → one AskUserQuestion call,
the recommended option first, labeled "(Recommended)". A larger frontier → one
message of numbered questions:

```text
❓ **Q1** - **<question title>**: <question body, may include multiple choices>

➡️ <your recommended answer>
```

Finding **facts** is your job, never the user's: a frontier question needing a
fact from the environment (files, tools, the KB) gets a dispatched subagent,
not a question — and don't block on it: only the questions downstream of it
wait; ask the rest of the frontier now. The **decisions** are the user's — put
each to them and wait.

The session is done when the frontier is empty — every branch of the tree
visited, nothing left silently assumed. Land the locked answers where the work
lives: the active plan chain's decisions file when one exists, otherwise a
decision summary in the conversation. Do not act on the design until the user
confirms you have reached a shared understanding.
