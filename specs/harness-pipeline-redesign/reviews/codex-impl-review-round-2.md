### Round 2 — Verdict: changes-requested

Scope: delta
Base SHA: cbe0b5fc27743b4b75c369ecde298d30d905dc49
Reviewed head SHA: b8f53edd8d08d9825b3cf1d9c242c47ff6f5e2f6
Prior reviewed head: 02c0a8d2a8b799cbf5e62f8334dca94fc89aebef
Mode: spawn
Lenses: plan-adherence, KB-grounding, code-standards, comment-accuracy, type-design | skipped: silent-failure — no hook script or other executable code changed; test-coverage — no executable hook or test changed; simplification — Round 1 records the existing tidy pass
Validation:
- `.codex/agents/*.toml` parsed with `uv run --no-project --offline` + `tomllib` using an isolated writable uv cache → PASS
- `.github/ISSUE_TEMPLATE/*.yml` parsed with `uv run --no-project --offline` + cached PyYAML using an isolated writable uv cache → PASS
- `grep -r "origin/main...HEAD" .codex/agents/` found no forbidden range → PASS
- All three exact report markers are present in both build commands → PASS
- Stage-row grep → carried forward: PASS in Round 1 and no `.github/PULL_REQUEST_TEMPLATE/*.md` file changed in `02c0a8d2a8b799cbf5e62f8334dca94fc89aebef..b8f53edd8d08d9825b3cf1d9c242c47ff6f5e2f6`

Prior blockers:
- B1 internal review not runnable — **not fixed**. Both build commands add the Sonnet review lead, draft override, and build-lead comment ownership, but simultaneously require the lead to follow the official workflow with exactly two adaptations and never call `gh`; required PR retrieval inputs are not supplied another way.
- B2 unsupported `gh api --body-file` upserts — **fixed**. Both build commands and both plan commands paginate marker discovery, PATCH with `-F body=@<file>`, and create with `gh pr comment` / `gh issue comment --body-file`.
- B3 accepted advice lacked re-review — **not fixed**. The delta adds invalidation and cap-exempt N+1 review language, but R3+ cannot be represented by the fixed R1/R2 PR stage/report schema; the plan commands also do not explicitly require the separate advice commit to carry `Refs #N` and be pushed before review.
- B4 delta-validation contradiction — **fixed**. Both implementation-review skills allow recorded prior-PASS/unchanged carry-forward skips and block only affected, previously failing, newly required, or unjustifiably omitted validation.
- B5 type-design scope mismatch — **fixed**. The harness selector includes types, schemas, and contracts, and the worker now reviews that same scope and stops only when all three are absent.
- B6 issue-form label invariant — **fixed**. The label policy distinguishes the complete agent-created label set from manual form labels completed at maintainer triage and documents `status:needs-human` removal on recovery.

Digest: 2 blocking findings — B1 remains operationally contradictory, and B3's cap-exempt advice path cannot be represented or fully checkpointed. The affected validations pass, B2/B4/B5/B6 are fixed, and the fresh model catalog grounds `gpt-5.6-terra`. No blocking KB contradiction was found.

## Blocking findings

1. **B1's review lead still cannot execute the required plugin workflow without its GitHub inputs.** `.claude/commands/build.md:59` and `.claude/commands/harness-layer/harness-build.md:61` tell the lead to follow the installed `code-review` workflow with exactly two adaptations while also saying it never calls `gh`. The installed `~/.claude/plugins/cache/claude-plugins-official/code-review/unknown/commands/code-review.md:11-28,47` requires GitHub-backed eligibility, PR summary/view, prior-PR context, final eligibility, and posting. The draft and posting adaptations cover only two of those uses; neither build command has the build lead collect and inject the remaining PR data. This leaves the Round 1 B1 runnability contract unmet. Fix: have the build lead gather and pass every required PR input to the read-only lead and explicitly map those inputs onto the plugin steps, or permit read-only `gh` retrieval while retaining build-lead-only posting.

2. **B3's cap-exempt advice transition has no valid R3+ evidence/checkpoint path.** `.claude/commands/build.md:16,31,43,70` and `.claude/commands/harness-layer/harness-build.md:17,33,45,72` can now require round N+1 after an approval at the two-round cap, but every PR template still has only `Codex R1` / `Codex R2 delta` stage rows and R1/R2 report entries (for example `.github/PULL_REQUEST_TEMPLATE/chore.md:56-68`). For R3+, the command cannot record the required `Codex R{N}` evidence or replace that round's report-list entry; updating only `Ready` also conflicts with `.claude/commands/ship.md:26-30,46-48`, which reads the final Codex/Ready evidence as the merge guard. In addition, `.claude/commands/plan-w-team.md:123` and `.claude/commands/harness-layer/harness-plan.md:135` say only `NEW commit`, omitting the contract's explicit `Refs #N` footer and push before the delta review. Fix: define dynamic R<N> stage/report entries (or one repeatable final-Codex slot), explicitly commit with `Refs #N` and push accepted advice before review in both plan commands, and make the advice-mode exemption govern follow-up fix rounds until approval.

## KB grounding

No blocking contradiction was found. `ai-docs/openai/codex/models.md:33-45,103-109`, registered in `ai-docs/sources.yaml` and `ai-docs/index.md`, freshly grounds the `gpt-5.6-terra` model and medium reasoning effort. The cached Claude subagent documentation also grounds Sonnet model selection, read-only tool restriction, and nested reviewer subagents; it does not resolve the missing PR-input handoff in B1.

## Advisory findings (non-blocking)

- **The delta checkpoint violates the repository's commit-subject rules.** Commit `b8f53edd8d08d9825b3cf1d9c242c47ff6f5e2f6` has a 114-character nominal subject, contrary to the imperative and ≤72-character rules in `GIT-COMMIT-PR-MESSAGE.md:17-20`. This is non-blocking under the caller's no-style-block rule; do not rewrite pushed history, but keep later checkpoint and squash subjects compliant.
- **The expanded type-design worker still formats every result as a type.** `.codex/agents/review-type-design.toml:37-48` now reviews schemas/contracts but requires a “type name,” “Per type,” and `<TypeName>`. Use a generic design/schema/contract identifier so the output contract matches the fixed scope.

Round 1's other advisories are addressed in the delta: report-comment URLs are placed in `Review Reports`, `/ship` separates local and remote branch names, the chore-form wording is accurate, and the harness-build lens summary delegates to the review skill.
