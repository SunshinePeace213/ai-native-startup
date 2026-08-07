---
name: codex-gate
description: Run the cross-model Codex gate — a deterministic lint first, then three parallel codex exec lenses merged into one findings ledger under a citation contract, one full-context fix batch, and a verification delta, capped at two cycles. Spec flavor gates a drafted plan from /harness-layer:harness-plan; implementation flavor gates a build diff from /harness-layer:harness-review.
---

# Codex Gate

You (the lead) run every round yourself — `codex exec` via Bash, no runner
subagent. Codex is sandboxed read-only and returns findings; you merge them,
classify them, and own the ledger, the verdict, all git/gh calls, and the
terminal outcome. Codex never issues a verdict.

## Flavors

| | Spec | Implementation |
| --- | --- | --- |
| Caller | `/harness-layer:harness-plan` | `/harness-layer:harness-review` |
| Standards file | `.claude/rules/harness-layer/spec-standards.md` | `.claude/rules/harness-layer/impl-standards.md` |
| Lint — first, free | `uv run scripts/spec_lint.py specs/<name>/` from the worktree root; fix failures yourself and re-run to green before any lens | `uv run scripts/impl_lint.py specs/<name>/` from the worktree root; each FAIL line enters the ledger as a finding (Lens `lint`, Conf 100, STD from the check) |
| Panel target | the spec folder at HEAD | the diff `<BASE_SHA>..HEAD` (BASE_SHA from the caller) |
| Report files | panel `reviews/codex-spec-round-<N>-<lens>.md` · delta `reviews/codex-spec-round-<N>.md` | same, `codex-impl-` |
| Ledger IDs | `R<N>-F<M>` | `I<N>-F<M>` — caller-fed security findings join the same round sequence |
| Fixes | edit the spec files yourself | ONE full-context `opus` fixer subagent |
| Round comment | issue, `<!-- codex-spec-round-N -->` | PR, `<!-- report:codex-round-N -->` |
| Clean terminal | always the human gate | return to the caller's terminal step — no question |

## Lens clusters

Round 1 is three parallel lenses. Each lens prompt carries ONLY its cluster's
standards text, copied verbatim from the standards file.

| Lens | Spec flavor | Implementation flavor |
| --- | --- | --- |
| `fidelity` | S4 · S5 · S6 | I1 · I6 · I5 · I9 |
| `evidence` | S1 · S2 (semantic: does the command prove the AC?) | I2 · I3 · I8 |
| `simplicity` | S8 · S3 · design challenge | I4 · simplification challenge |
| `lint` — not a lens | S7 · S2 exist-and-collect · template completeness | I7 · I2 run-and-pass · orphan scan |

## Cycles

- A cycle = one review round plus its fix batch. At most **2 cycles per run**.
  Round numbers are global per flavor: highest existing report number + 1 —
  revision cycles continue the count, never reset it.
- Cycle 1's round is the panel; cycle 2's round is a single delta reviewer
  scoped to the fix diff.
- Pick the Codex model + effort per the model-selection rule from the plan's
  complexity; all three lenses run the same pick, and the delta runs the same
  model one effort step down, never below `medium`.
- Snapshot `REVIEWED_HEAD=$(git rev-parse HEAD)` when you launch a round. If
  HEAD has moved when it returns, discard and re-run on the new head. The
  delta's range starts at the last reviewed head.
- Launch all three lenses in one message as background Bash, stdout redirected —
  read each captured report file, never the raw stream:

```bash
codex exec -C "<worktree root>" -s read-only \
  --model <codex-model> -c model_reasoning_effort="<effort>" \
  -o "<worktree root>/specs/<name>/reviews/<report-file>" \
  "<lens prompt>" > "<worktree root>/specs/<name>/reviews/<report-file>.log" 2>&1
```

- Write each lens prompt to its file in a separate prior step — a heredoc
  bundled into the launch command leaves codex reading stdin forever.
- **Dead lens** — codex exits non-zero or its report file is missing/empty:
  re-run that lens once. Still dead → run that lens's rubric yourself, inline,
  reading only its cluster's standards; write its report file and record the
  substitution in the ledger's round note and the metrics counts. Coverage never
  silently drops, and a Codex outage never blocks the panel. A dead **delta**
  after one retry → the human gate, reason `codex-unavailable` — you never
  verify your own fixes.

## Round prompts

Every prompt ends with this shared contract block:

```text
One line per finding:
- [STD:<id>] [S:critical|major|minor|info] [C:0-100] <file/section>
  — <defect CLASS: the property violated and its boundary, not one instance>
  — evidence: <quote or line> — fix: <concrete fix>
<id> is exactly one standard from the list above, e.g. [STD:S2]. A finding that
cites no standard will be recorded as advisory.
If nothing is found, reply exactly: no findings.
Do not edit files. Git is read-only for you — diff/log/show only. Never run gh.
```

**Lens prompt (round 1).** The flavor head, then the lens block, then the
contract block.

Spec head:

```text
You are one of three cross-model review lenses on an implementation plan
(round <N>, lens: <lens>).
Read all four files under specs/<name>/ (spec.md, decisions.md, tasks.md,
acceptance-criteria.md), any scripts under specs/<name>/checks/, and — when
decisions.md has a ## KB References section — each ai-docs/ file it lists.
```

Implementation head:

```text
You are one of three cross-model review lenses on an implementation
(round <N>, lens: <lens>).
Read the plan under specs/<name>/ (spec.md, tasks.md, acceptance-criteria.md,
implementation-notes.md), then review `git diff <BASE_SHA>..<REVIEWED_HEAD>` —
the diff is the review target; the plan is what it must satisfy. Do not run the
check scripts; the caller runs them.
```

Lens block:

```text
Judge ONLY against these standards. Report every violation of them you find,
including low-severity and uncertain ones — a separate step classifies:

<the cluster's standards text, verbatim from the standards file>
```

For the `simplicity` lens, append: `Also challenge the approach: a simpler
design that meets the objective is a finding — cite S8 (spec) or I4 (impl).`

**Delta prompt (round ≥ 2).** This REPLACES the lens prompt — never append the
two. The head below, then the contract block only.

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

## Merge, classify & ledger

You derive everything; Codex only reports.

- **Merge** the three lens reports into one set: the same defect class on the
  same target from two lenses is one row, both lenses noted.
- **Blocking** = cites a standard AND severity `critical`/`major` AND confidence
  ≥ 80. **No citation → advisory, always** — never promote by inferring the
  standard yourself.
- Advisories are recorded, never fixed this run, and never spawn a cycle; the
  impl flavor mirrors them to the PR's `## Follow-ups` checklist. They never
  ride a fix diff.
- Verdict: any blocking finding open → `changes-requested`; none → `approved`.
- Maintain `specs/<name>/reviews/findings-ledger.md` — one ledger per plan, one
  row per finding, IDs stable across rounds and flavors:

```markdown
| ID | STD | Lens | Sev | Conf | Finding | Disposition | Evidence |
```

`STD` is the cited standard (`—` when uncited). `Lens` is `fidelity` /
`evidence` / `simplicity` / `lint` / `sec` / `delta`; a lead-substituted lens is
`<lens>*` with a round note naming the substitution.

Dispositions: `open` → `fixed` (with the fixing commit) | `disputed` (you hold
it's already fixed or wrong — cite why) | `advisory` | `overridden` (human gate
only, with the user's reason).

## Loop

1. Run the flavor's lint (see Flavors).
2. Launch the round — cycle 1 the panel, cycle 2 the delta. Merge, classify,
   append to the ledger, commit the report file(s) + ledger (`Refs #N`), push.
3. `changes-requested` → fix the blocking set only, per the flavor's fix row.
   The impl fixer is ONE `opus` subagent whose prompt carries the whole blocking
   set, the spec's locked decisions, and each cited standard's text verbatim.
   Mark rows `fixed` with evidence; all fixes land as ONE fix commit
   (`Refs #N`), pushed.
4. Re-run the lint — plus, impl flavor, every `## Validation Commands` entry —
   after every fix commit: the deterministic floor. The next cycle's delta is
   the preferred verification. No run ends on a fix commit that skipped the
   floor.
5. **Dispute short-circuit:** Codex reopens a finding you marked `fixed` without
   new evidence, or you judge a finding wrong → mark it `disputed` and go
   straight to the human gate. Never spend a cycle re-arguing a disputed
   finding.
6. `approved`, or the cap is reached → the flavor's terminal. Fixes landed in
   cycle 2 are Codex-unverified — the human gate states exactly that; the
   deterministic floor is not a Codex verification.
7. After each round, upsert the flavor's marker comment (per pr-process.md
   § Idempotent Marker Comments): round, verdict, blocking count + headline
   findings, any lens substitutions, next action.

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
still open at the cap, cycle-2 fixes unverified, a dispute, or
`codex-unavailable` → the human gate:

- **One more delta round** — a single extra delta round (still globally numbered),
  then return to this terminal.
- **Override & ready** — mark each open blocker `overridden` with the user's
  reason, then return to the caller's terminal step as approved.
- **Park** — `gh issue edit <N> --add-label status:needs-human`, comment the open
  blockers on the PR; the caller's terminal step still runs, but the PR stays draft.

Either flavor: hand the caller the counts its `summary.md` `## Metrics` block
needs — cycles, blocking/advisory, findings by standard, uncited→advisory, fix
commits, unverified tail, disputed/overridden, lint catches, lens substitutions.

## Self-improve

Before the terminal outcome lands, close the loop on the gate itself: a
confirmed finding that exposed a missing or unclear standard → amend the
flavor's standards file in the same commit series (a new standard takes the next
free ID — never renumber). An uncited finding class recurring 2+ times in
`specs/lessons/digest.md` → the same amendment path. A generalizable process
lesson → route it per the memory-series contract. Skip all of it when nothing
generalizes — most runs add nothing.
