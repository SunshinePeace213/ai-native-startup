---
source: Graph-Engineering-Andrew-Ng-Playbook.pdf
fetched: 2026-08-05
pages: 9-10
---
> **In here:** Production readiness checklist by stage (Table VII) · Code-review assistant walked from zero-shot to graph · 55% → 72% → 84% → 88% → 95%

# Appendix B — Production Readiness Checklist

### Table VII — Production Readiness Checklist by Stage

| Stage | Element | Ask Yourself |
| --- | --- | --- |
| Reflection | Rubric | Is the evaluation criterion explicit and stable? |
| | Iteration cap | Is there a maximum number of revision rounds? |
| | Artifact log | Is every draft, critique, and revision stored? |
| Tool Use | Schema | Are tool names, arguments, and return types validated? |
| | Permissions | Are read and write permissions separated? |
| | Fallback | What happens when the tool fails or rate-limits? |
| Planning | Plan format | Are plans structured JSON with dependencies? |
| | Step budget | Is total step count bounded? |
| | Replan policy | Does successful work survive replanning? |
| Multi-Agent | Artifact contracts | Does every handoff use typed schemas? |
| | Role differentiation | Do roles catch genuinely different error classes? |
| | Orchestrator budget | Does the orchestrator receive bounded summaries? |
| Graph Arch. | Provenance | Does every edge trace to a source document? |
| | Versioning | Are overwrites replaced by supersession links? |
| | Entity resolution | Are resolution decisions inspectable? |

# Appendix C — Worked Example: From Zero-Shot to Graph in Five Steps

Consider a team building a code-review assistant. The progression follows the staged build path exactly.

**Day 0 — Zero-shot baseline:** The team sends code to the LLM with the prompt "review this code for bugs." The output is a free-form paragraph that sometimes catches real issues and sometimes praises correct code. Measured accuracy: 55%.

**Day 1 — Add reflection:** The team adds a second call: "Here is your review. Does it cite specific line numbers? Does it distinguish severity levels? Revise." The revised review is measurably better: specific line numbers, severity labels, fewer false positives. Measured accuracy: 72%.

**Day 2 — Add tool use:** The reviewer agent can now execute the code against a test suite and read linter output. Reviews cite concrete test failures instead of hypothetical bugs. Measured accuracy: 84%.

**Week 1 — Add planning:** For large PRs (>500 lines), the agent writes a plan: "review security-sensitive files first, then business logic, then tests." Each section gets a focused review with the right rubric. Measured accuracy on large PRs: 79% (up from 61% with reflection alone).

**Week 2 — Add multi-agent:** A security reviewer (system prompt: "you are a security auditor, assume every input is malicious") runs alongside the general reviewer. The security agent catches injection vulnerabilities the general agent missed. Combined accuracy: 88%.

**Month 1 — Add graph:** Review findings are stored as entities (vulnerability, code pattern, affected file) with typed relations (found_in, similar_to, fixed_by). When a new PR touches a file that previously had a vulnerability, the reviewer agent queries the graph and flags the pattern. The graph accumulates institutional knowledge across hundreds of PRs — knowledge that no single context window could hold. Measured accuracy on repeat patterns: 95%.

The progression illustrates two principles. First, each stage earns the right to the next by addressing a specific, measured failure of the previous stage. Second, the compound effect — 55% → 72% → 84% → 88% → 95% — is far greater than any single stage's contribution. The architecture, not the model, is doing the heavy lifting.
