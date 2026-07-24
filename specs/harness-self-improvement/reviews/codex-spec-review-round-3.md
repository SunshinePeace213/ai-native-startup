### Round 3 — Verdict: changes-requested

Scope: delta
Base SHA: 57cd02dc83d6b060e50927d36335c637346bd014
Reviewed head SHA: 4ff9f29912fddab7da5998a8ae120a74cc4045aa
Validation:
- [plan-time] `uv run --script specs/harness-self-improvement/checks/ac5_inventory.py` → PASS
- deferred: 3 child-build-time, 0 post-merge
Prior blockers:
- CX2-1 fixed

- **CX3-1 (new) — A subagent description cannot make the effort executors “explicit-deployment-only.”** The changed spec requires a description that “prevents automatic delegation,” and decisions.md says the definitions never auto-delegate, but `ai-docs/anthropic/subagents.md` (“Understand automatic delegation”) says Claude automatically selects subagents from their `description` and provides no disable-auto-delegation field. The five definitions’ negative wording can discourage selection but cannot enforce the absolute promise. Fix: remove the explicit-only/prevention guarantee from spec.md and decisions.md, describe the narrow wording as best-effort routing, and revise the executor descriptions’ “Never select” language accordingly; otherwise name a documented enforcement mechanism.

**Recommendations (advisory, non-blocking):**

- Ship only the `low`, `medium`, and `high` executors this plan uses; defer `xhigh` and `max` until a stamped task needs them.

**Issue-comment digest:** Round 3, changes-requested — 1 blocking (0 repeats): descriptions cannot enforce the new explicit-deployment-only guarantee for the effort executors. Next: make that routing claim best-effort or supply a documented enforcement mechanism, then re-review.
