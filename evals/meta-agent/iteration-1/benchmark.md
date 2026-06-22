# Skill Benchmark: meta-agent (iteration-1)

**Builder model**: sonnet (both configurations, for a clean delta)
**Evals**: eval-1 (diff reviewer), eval-2 (test runner), eval-3 (researcher), eval-4 (fix broken agent) — 1 run each per configuration
**Grading**: deterministic frontmatter/body checks + `validate_agent.py`, against the assertions in `.claude/skills/meta-agent/evals/evals.json`

## Output-quality summary

| Metric | With Skill | Without Skill | Delta |
|--------|------------|---------------|-------|
| Assertion pass rate | 96% (25/26) | 65% (17/26) | **+31%** (+8) |
| Validator PASS | 4/4 | 4/4 | 0 |
| `effort` set in frontmatter | 4/4 | 1/4 | **+3** |
| `use proactively` in description | 4/4 | 1/4 | **+3** |
| NOT-boundary in description | 4/4 | 2/4 | **+2** |
| Mean tokens / run | ~30,176 | ~15,535 | +94% |
| Mean wall time / run | ~64.3s | ~34.7s | +85% |

The skill roughly **doubles** token/time cost (the agent reads references + runs the
validator) in exchange for a **+31-point** quality lift on a one-time authoring task that
produces a durable artifact.

## Per-eval assertion scores

| Eval | With skill | Baseline |
|------|-----------|----------|
| eval-1 read-only diff reviewer | 7/7 | 5/7 |
| eval-2 proactive test runner | 6/6 | 4/6 |
| eval-3 read-only researcher | 5/6 | 3/6 |
| eval-4 fix broken agent | 7/7 | 5/7 |

## Triggering summary (real `claude -p` routing, sonnet, 2 runs/query)

| Metric | Value |
|--------|-------|
| Accuracy | 86% (19/22) |
| Recall (should-trigger fired) | 0.70 (7/10) |
| Precision (no false fires) | 1.00 |
| Specificity (should-not held) | 1.00 (12/12) |

Boundary with `meta-skill` / `meta-commands` is crisp (0 false positives). The 3 misses are
all "fix/advise on an *existing* agent" intents the model answered directly.
