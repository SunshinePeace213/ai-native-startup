### Round 2 — Verdict: changes-requested

Scope: delta
Base SHA: 976d18f0d90aae25ab2293930558995883ea60b2
Reviewed head SHA: 57cd02dc83d6b060e50927d36335c637346bd014
Validation:
- [plan-time] `uv run --script specs/harness-self-improvement/checks/ac5_inventory.py` → PASS
- deferred: 3 child-build-time, 0 post-merge
Prior blockers:
- CX1-1 fixed
- CX1-2 fixed
- CX1-3 fixed
- CX1-4 not fixed

- **CX2-1 (repeat of CX1-4) — The effort-deployment fix violates the repository's mandatory per-task model/effort contract.** The changed tasks replace every concrete `medium`/`high`/`low` stamp with `session-inherited`, but `.claude/rules/model-selection.md` requires plans to stamp a model and effort per task. Session inheritance can vary with the runner session and cannot preserve the distinct effort assignments across concurrent builders. `ai-docs/anthropic/subagents.md` (“Supported frontmatter fields” and “Choose a model”) confirms that `effort` is available on subagent definitions while only `model` has a per-invocation override. Fix: restore concrete effort stamps and deploy effort-bearing subagent definitions, or specify another mechanism that accepts and preserves each task's assigned effort.

**Issue-comment digest:** Round 2, changes-requested — 1 blocking (1 repeat): the revised Agent deployment still cannot preserve mandatory per-task effort assignments. Next: give each task a concrete effort-capable deployment mechanism, then re-review.
