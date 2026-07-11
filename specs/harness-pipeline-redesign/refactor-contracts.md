# Harness Pipeline Refactor — Shared Contracts (PR #18)

Binding for every builder. When your file states one of these values, use it VERBATIM — cross-file consistency is an acceptance criterion.

## Ground rules

- Edit ONLY inside the worktree: `/Users/ringo/Desktop/ai-native-startup/.claude/worktrees/chore+17-harness-pipeline-redesign/` — use absolute paths; never `cd`.
- Builders never run `git commit`/`push`, never call `gh`, never delete files — the lead owns git and deletions.
- House style (AGENTS.md Harness Development): fluent KISS prose, say it once, instructions not rationale, no stray cross-refs, model aliases only (`opus`, `sonnet`, `haiku`, `fable`).
- Command structure: frontmatter → `# Title` → intro paragraph → `## Variables` → `## Instructions` → `## Workflow` → specialized sections → `## Report`.
- NO "node N" references anywhere. Refer to workflow steps by name (e.g. "the Cross-check step"), never by number.

## The pipeline (universal — application code AND harness work)

`/harness-layer:harness-plan` → `/harness-layer:harness-build` → `/harness-layer:harness-ship`.
Internal review = `/harness-layer:harness-review`, invoked within harness-build (also user-invocable standalone). The retiring `plan-w-team`, `build`, `ship` commands and the `code-review@claude-plugins-official` plugin are gone — never reference them.

## Domain-expert (KB) layer — conditional, any signal wins

- Plan time: harness-plan runs its Domain Knowledge section only when the task touches `.claude/`, `.agents/`, `.codex/`, `ai-docs/`, the root memory files (CLAUDE.md, AGENTS.md, HARNESS-LAYER.md, GIT-COMMIT-PR-MESSAGE.md), or a domain with an `ai-docs/index.md` entry. Otherwise it states the layer is skipped and proceeds without KB grounding.
- harness-plan records the chosen profile in spec.md `## Tracking` as a line: `Review profile: kb-grounded` or `Review profile: standard`.
- Review time (both Codex skills): run the KB-grounding pass when profile = `kb-grounded`, OR decisions.md has `## KB References`, OR the reviewed range/target paths touch the surfaces above. A mismatch between profile and signals → run the KB pass AND report the mismatch as a blocking contract defect.

## Worktree naming

`EnterWorktree(name: "<slug>")` — directory `.claude/worktrees/<slug>`, local branch `worktree-<slug>`. The GitHub convention branch `<type>/<N>-<slug>` is still created by `gh issue develop` and is ONLY reached via the explicit refspec `git push origin HEAD:refs/heads/<type>/<N>-<slug>` (bare `git push` refuses from the local worktree branch). Update every example that shows the old `chore+17-` style mangling.

## Review rounds — caps, commits, exits

- Hard cap: 2 Codex rounds for spec review AND implementation cross-check. EVERY Codex invocation counts — advisory-induced rounds included. No exemptions.
- Advisories never spawn in-build rounds: they are recorded as a follow-up checklist (PR comment section for builds; decisions.md follow-ups list for plans) to feed a future plan.
- Per-round commits: the report gets its own commit, fixes get their own commit; on a changes-requested round push both together (one push). Tracked SHAs: `REVIEWED_HEAD_SHA` (input), report SHA, fix SHA. **Approved head = the approval round's report commit.** Delta ranges exclude `specs/<plan>/reviews/`.
- Exit statuses: `approved` | `accepted-with-unverified-fixes` | `needs-human`.
- Over-cap gate (round 2 still changes-requested), in harness-plan and harness-build: STOP and present ONE AskUserQuestion — why a further round would be needed, what it would do, and the detailed next steps per option: (a) run one more delta round; (b) `accepted-with-unverified-fixes` — allowed only when remaining blockers are non-severe and mechanically verifiable, the plan's validation commands pass after the fixes, and the user explicitly picks it; recorded in the PR/issue; (c) `needs-human` — add `status:needs-human` label + an issue comment naming the blockers. The user's selection is final and recorded.

## harness-build review flow (concurrent R1)

1. Freeze: clean tree, snapshot `BASE_SHA` (merge-base with origin/main) and `REVIEWED_HEAD_SHA`.
2. Launch BOTH reviews concurrently on that frozen SHA: the internal review (a read-only `sonnet` review-lead subagent that reads `.claude/commands/harness-layer/harness-review.md` and follows it, returning findings) and Codex round 1 (`codex exec` with the `implementation-review` skill). Neither writes to the tree until both return; the lead commits afterward.
3. Both approve / zero findings → skip round 2 entirely; the round-1 report commit is the approved head → Ready.
4. Otherwise: lead merges the two finding sets (dedup by root cause, keep source IDs), posts reports, makes the report commit, applies ONE combined fix pass, makes the fix commit, pushes both, then Codex round 2 reviews the delta and dispositions findings from BOTH reports. Round 2 is the last automatic round (see over-cap gate).

## Review packet (injected into every codex exec prompt by the caller)

`BASE_SHA`, `REVIEWED_HEAD_SHA`, round `N`, prior reviewed head + prior finding IDs (N>1), clean-tree attestation, `git diff --numstat`/`--name-status` summary, the review profile, internal-review findings for dedup (N>1; "running concurrently" on round 1), validation results keyed to the frozen SHA, a KB claim map (claim → ai-docs path → excerpt → fetched date) when the KB layer is active, and the caller's EXPECTED lens list — Codex re-verifies lens selection independently and reports disagreement.

## implementation-review execution mode

Sequential single-context lens passes by DEFAULT. Spawn `.codex/agents/*.toml` subagents ONLY when ≥3 lenses are selected AND the range exceeds 1,000 changed lines or 20 files or touches high-risk executable code. Delta rounds never re-read the full plan/KB — they consume the injected packet and the prior report.

## Report files & markers

- Spec review verdicts: `specs/<plan>/reviews/codex-spec-review-round-N.md` (NEW — no longer appended inside spec.md; `## Codex Findings` leaves the spec template).
- Implementation review verdicts: `specs/<plan>/reviews/codex-impl-review-round-N.md` (unchanged).
- Verdict first line (both): `### Round N — Verdict: approved` or `### Round N — Verdict: changes-requested` (em-dash U+2014).
- PR comment markers (unchanged): `<!-- report:tidy -->`, `<!-- report:code-review -->`, `<!-- report:codex-round-N -->`. Upsert mechanics unchanged (paginated `gh api` search → PATCH `-F body=@<file>`, else `--body-file` create).
- PR body: seeded at creation with a `## Plan` links block — blob URLs (on the convention branch) to the four spec files, the `reviews/` folder, and `Closes #N` — plus the existing stage table, Agent Task Manifest, and `## Review Reports` list.

## harness-review (internal review command)

6 parallel `sonnet` reviewers — standards, bugs, history, prior-art, comment-accuracy, memory-sync — with `haiku` utility agents (eligibility, context, summary, per-finding confidence scoring), confidence floor 80, read-only (`gh` reads only), returns findings to the caller, never posts. Draft-PR input is expected, never a reason to decline.

## Memory sync standard

Root ALL-CAPS files are the memory series; `AGENTS.md` is the hub (CLAUDE.md only `@`-imports it). Ownership: AGENTS.md = agent/pipeline conventions; HARNESS-LAYER.md = hook/format mechanics; GIT-COMMIT-PR-MESSAGE.md = git/PR/issue policy; a genuinely new series → new root `ALL-CAPS.md` referenced from AGENTS.md. Severity: diff falsifies a documented statement → blocking; explicit new repo-wide convention with no memory home → blocking; inferred/one-off convention → advisory; memory in the wrong home (CLAUDE.md, or duplicated) → advisory.

## harness-ship

From ship.md semantics: user-typed only (`disable-model-invocation: true`), runs end-to-end with zero confirmation once invoked: verify ready PR + passing checks + head equals approved SHA → squash-merge with `--match-head-commit` → confirm MERGED → cleanup (worktree remove, local branch delete, remote convention branch delete, prune). Local branch examples use the new `worktree-<slug>` naming.
