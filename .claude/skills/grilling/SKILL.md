---
name: grilling
description: Interview the user to clear the unknowns in a plan, design, or vague request — one question per round, each carrying a recommended answer, with the codebase explored first for anything it can answer. Use when proceeding would mean guessing — requirements ambiguous, several defensible designs, a decision the user must own — or when the user says grill me, interview me, ask me questions, or help me firm this up. Not for the pipeline's own question sites (/harness-layer:harness-interview owns its page-based rounds; the plan's Readiness Gate its one bounded round) and not for menu-style confirmations.
argument-hint: [topic or plan to grill]
---

Interview the user about the topic until you reach shared understanding. Walk
the design tree branch by branch, resolving decisions in dependency order — a
question whose wording depends on an unanswered one waits its turn.

- Explore first: never ask what the codebase, the KB, or the conversation
  already answers.
- One question per AskUserQuestion round — batches are bewildering and let
  answers contradict each other unnoticed. Put your recommended answer first,
  labeled "(Recommended)".
- Stop when nothing open remains or the user stops engaging; record what's
  still open as explicit assumptions.
- Land the locked answers where the work lives: the active plan chain's
  decisions file when one exists, otherwise a decision summary in the
  conversation.
