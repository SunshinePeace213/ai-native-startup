---
name: codex-gate
description: Run the cross-model Codex gate — orchestrator-driven codex exec rounds with a findings ledger, a hard round cap, delta rounds scoped to the fix diff, and a dispute short-circuit. Spec flavor gates a drafted plan from /harness-layer:harness-plan; implementation flavor gates a build diff from /harness-layer:harness-review.
---

# Codex Gate

You (the orchestrator) run every round yourself — `codex exec` via Bash, no runner
subagent. Codex is sandboxed read-only and returns findings; you classify them,
own the ledger, the verdict, all git/gh calls, and the terminal outcome. Codex
never issues a verdict.

## Flavors

| | Spec | Implementation |
| --- | --- | --- |
| Caller | `/harness-layer:harness-plan` | `/harness-layer:harness-review` |
| Standards file | `.claude/rules/harness-layer/spec-standards.md` | `.claude/rules/harness-layer/impl-standards.md` |
| Round 1 target | the spec folder at HEAD | the diff `<BASE_SHA>..HEAD` (BASE_SHA from the caller) |
| Report file | `reviews/codex-spec-round-<N>.md` | `reviews/codex-impl-round-<N>.md` |
| Ledger IDs | `R<N>-F<M>` | `I<N>-F<M>` — caller-fed security and check-script findings join the same round sequence |
| Fixes | edit the spec files yourself | fixer subagents per the model-selection rule; a failed fix escalates a tier |
| Round comment | issue, `<!-- codex-spec-round-N -->` | PR, `<!-- report:codex-round-N -->` |
| Clean terminal | always the human gate | return to the caller's terminal step — no question |

## Rounds

- At most **2 new rounds per run**. Round numbers are global per flavor: highest
  existing report file + 1 — revision cycles continue the count, never reset it.
- Pick the Codex model + reasoning effort per the model-selection rule from the
  plan's complexity; a delta round runs the same model one effort step down, never
  below `medium`.
- Snapshot `REVIEWED_HEAD=$(git rev-parse HEAD)` when you launch a round. If HEAD
  has moved when the round returns, discard it and re-run on the new head. The
  next delta round's range starts at the last reviewed head.
- Run each round in background Bash, stdout redirected — read the captured report
  file, never the raw stream:

```bash
codex exec -C "<worktree root>" -s read-only \
  --model <codex-model> -c model_reasoning_effort="<effort>" \
  -o "<worktree root>/specs/<name>/reviews/<report-file>" \
  "<round prompt>" > "<worktree root>/specs/<name>/reviews/<report-file>.log" 2>&1
```

- Codex exits non-zero or the report file is missing/empty → re-run the identical
  command once. Still nothing → the human gate, reason `codex-unavailable`. An
  empty or missing report is never an approval.

## Round prompts

Every round prompt ends with this shared format block:

```text
One line per finding:
- [S:critical|major|minor|info] [C:0-100] <file/section> — <finding> — fix: <concrete fix>
If nothing is found, reply exactly: no findings.
Do not edit files. Do not run git or gh.
```

**Round 1 — comprehensive.** The flavor head, then the coverage block, then the
format block.

Spec head:

```text
You are the cross-model reviewer of an implementation plan (round <N>).
Read .claude/rules/harness-layer/spec-standards.md — the bar this plan must clear.
Read all four files under specs/<name>/ (spec.md, decisions.md, tasks.md,
acceptance-criteria.md), the scripts under specs/<name>/checks/, and — when
decisions.md has a ## KB References section — each ai-docs/ file it lists.
```

Implementation head:

```text
You are the cross-model reviewer of an implementation (round <N>).
Read .claude/rules/harness-layer/impl-standards.md — the bar this diff must clear.
Read the plan under specs/<name>/ (spec.md, tasks.md, acceptance-criteria.md,
implementation-notes.md), then review `git diff <BASE_SHA>..<REVIEWED_HEAD>` —
the diff is the review target; the plan is what it must satisfy. Do not run the
check scripts; the caller runs them.
```

Coverage block — round 1 only, never in a delta round:

```text
Report EVERY standards violation you find, including low-severity and uncertain
ones. Do not filter for importance or confidence — a separate step classifies.
Also challenge the approach: a simpler design that meets the objective is a
finding at S:info.
```

**Delta round (≥ 2).** This prompt REPLACES the comprehensive one — never append
the two: a fresh Codex session given both will re-review everything and surface
new noise each round. The head below, then the format block only.

```text
You are re-reviewing after a fix commit (round <N>).
Read specs/<name>/reviews/findings-ledger.md and <standards file>.
Review ONLY `git diff <prior REVIEWED_HEAD>..<REVIEWED_HEAD>` — the fixes since
the last round. Do not re-review files outside this diff except to verify ledger
dispositions.
For each non-advisory ledger finding, verify its disposition against the current
files. Reopening a finding marked fixed requires citing new evidence from the
current files. New findings are admissible only inside this diff — where a fix
introduced a regression.
```

## Classify & ledger

Codex never issues a verdict — you derive it:

- **Blocking** = severity `critical` or `major` with confidence ≥ 80. Everything
  else is **advisory** (recorded, never fixed this run, never spawns a round).
- Verdict: any blocking finding open → `changes-requested`; none → `approved`.
- Maintain `specs/<name>/reviews/findings-ledger.md` — one ledger per plan, one
  row per finding, IDs stable across rounds and flavors:

```markdown
| ID | Sev | Conf | Finding | Disposition | Evidence |
```

Dispositions: `open` → `fixed` (with the fixing commit) | `disputed` (you hold
it's already fixed or wrong — cite why) | `advisory` | `overridden` (human gate
only, with the user's reason).

## Loop

1. Round N → classify, append to the ledger, commit the report + ledger (`Refs #N`), push.
2. `changes-requested` → fix the blocking findings (per the flavor's fix row), mark
   them `fixed` with evidence, commit the fixes (`Refs #N`), push, run round N+1 as
   a delta round.
3. **Dispute short-circuit:** Codex reopens a finding you marked `fixed` without new
   evidence, or you judge a finding wrong → mark it `disputed` and go straight to
   the human gate. Never spend a round re-arguing a disputed finding.
4. `approved`, or the round cap is reached → the flavor's terminal.
5. After each round, upsert the flavor's marker comment (per pr-process.md
   § Idempotent Marker Comments): round, verdict, blocking count + headline
   findings, next action.

## Terminal

**Spec flavor — always the human gate:** approving a spec is a scope decision the
user owns. `AskUserQuestion` with the outcome so far, then act on the choice:

- **Proceed to build** — set spec.md `Status: Approved`, record the outcome (and any
  overridden blockers) in `## Codex Verification`; hand off to `/harness-layer:harness-build`.
- **One more round** — run a single extra delta round (still globally numbered), then
  return to this gate.
- **Revise** — recommend `/harness-layer:harness-interview "Resolve: <one line per open
  blocker>. Worktree: <path>"`; leave `Status: Drafted for Review`.
- **Park** — `gh issue edit <N> --add-label status:needs-human`, comment the open
  blockers, record `needs-human` + reason in `## Codex Verification`.

**Implementation flavor — autonomous when clean.** `approved` → return to the
caller's terminal step with the ledger settled; no question. Blocking findings
still open at the cap, a dispute, or `codex-unavailable` → the human gate:

- **One more delta round** — a single extra delta round (still globally numbered),
  then return to this terminal.
- **Override & ready** — mark each open blocker `overridden` with the user's
  reason, then return to the caller's terminal step as approved.
- **Park** — `gh issue edit <N> --add-label status:needs-human`, comment the open
  blockers on the PR; the caller's terminal step still runs, but the PR stays draft.

## Self-improve

Before the terminal outcome lands, close the loop on the gate itself: a confirmed
finding that exposed a missing or unclear standard → amend the flavor's standards
file in the same commit series; a generalizable process lesson → route it to its
rule-file home per the memory-series contract. Skip both when nothing generalizes —
most runs add nothing.
