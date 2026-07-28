---
name: codex-gate
description: Run the cross-model Codex gate over a drafted plan — orchestrator-driven codex exec rounds with a findings ledger, a hard round cap, and a human decision gate. Use from /harness-layer:harness-plan after the spec folder is committed and pushed. Spec flavor only; the implementation flavor lands with the harness-review redesign.
---

# Codex Gate

You (the orchestrator) run every round yourself — `codex exec` via Bash, no runner
subagent. Codex is sandboxed read-only and returns findings; you classify them,
own the ledger, the verdict, all git/gh calls, and the human gate.

## Rounds

- At most **2 new rounds per run**. Round numbers are global: highest existing
  `specs/<name>/reviews/codex-spec-round-*.md` + 1 — revision cycles continue the
  count, never reset it.
- Pick the Codex model + reasoning effort per the model-selection rule from the
  spec's complexity.
- Run each round in background Bash, stdout redirected — read the captured report
  file, never the raw stream:

```bash
codex exec -C "<worktree root>" -s read-only \
  --model <codex-model> -c model_reasoning_effort="<effort>" \
  -o "<worktree root>/specs/<name>/reviews/codex-spec-round-<N>.md" \
  "<round prompt>" > "<worktree root>/specs/<name>/reviews/codex-spec-round-<N>.log" 2>&1
```

- Codex exits non-zero or the report file is missing/empty → re-run the identical
  command once. Still nothing → the human gate, reason `codex-unavailable`. An
  empty or missing report is never an approval.

## Round prompt

```text
You are the cross-model reviewer of an implementation plan (round <N>).
Read .claude/rules/harness-layer/spec-standards.md — the bar this plan must clear.
Read all four files under specs/<name>/ (spec.md, decisions.md, tasks.md,
acceptance-criteria.md), the scripts under specs/<name>/checks/, and — when
decisions.md has a ## KB References section — each ai-docs/ file it lists.
Report EVERY standards violation you find, including low-severity and uncertain
ones. Do not filter for importance or confidence — a separate step classifies.
One line per finding:
- [S:critical|major|minor|info] [C:0-100] <file/section> — <finding> — fix: <concrete fix>
Also challenge the approach: a simpler design that meets the objective is a
finding at S:info. If nothing is found, reply exactly: no findings.
Do not edit files. Do not run git or gh.
```

For round ≥ 2, append:

```text
Read specs/<name>/reviews/findings-ledger.md. This is a delta round: verify the
disposition of each non-advisory finding, and report new findings only where a
fix introduced a regression. Reopening a finding marked fixed requires citing
new evidence from the current files.
```

## Classify & ledger

Codex never issues a verdict — you derive it:

- **Blocking** = severity `critical` or `major` with confidence ≥ 80. Everything
  else is **advisory** (recorded, never fixed this run, never spawns a round).
- Verdict: any blocking finding open → `changes-requested`; none → `approved`.
- Maintain `specs/<name>/reviews/findings-ledger.md` — one row per finding, IDs
  stable across rounds (`R1-F2` = round 1, finding 2):

```markdown
| ID | Sev | Conf | Finding | Disposition | Evidence |
```

Dispositions: `open` → `fixed` (with the fixing commit) | `disputed` (you hold
it's already fixed or wrong — cite why) | `advisory`.

## Loop

1. Round N → classify, append to the ledger, commit the report + ledger (`Refs #N`), push.
2. `changes-requested` → fix the blocking findings, mark them `fixed` with evidence,
   commit the fixes (`Refs #N`), push, run round N+1 as a delta round.
3. **Dispute short-circuit:** Codex reopens a finding you marked `fixed` without new
   evidence, or you judge a finding wrong → mark it `disputed` and go straight to
   the human gate. Never spend a round re-arguing a disputed finding.
4. `approved`, or the round cap is reached → the human gate.
5. After each round, upsert an issue comment `<!-- codex-spec-round-N -->` (per
   pr-process.md § Idempotent Marker Comments): round, verdict, blocking count +
   headline findings, next action.

## Human gate

Always ends the run — on `approved`, cap reached, a dispute, or `codex-unavailable`.
`AskUserQuestion` with the outcome so far, then act on the choice:

- **Proceed to build** — set spec.md `Status: Approved`, record the outcome (and any
  overridden blockers) in `## Codex Verification`; hand off to `/harness-layer:harness-build`.
- **One more round** — run a single extra delta round (still globally numbered), then
  return to this gate.
- **Revise** — recommend `/harness-layer:harness-interview "Resolve: <one line per open
  blocker>. Worktree: <path>"`; leave `Status: Drafted for Review`.
- **Park** — `gh issue edit <N> --add-label status:needs-human`, comment the open
  blockers, record `needs-human` + reason in `## Codex Verification`.

## Self-improve

Before reporting, close the loop on the gate itself: a confirmed finding that exposed
a missing or unclear standard → amend `.claude/rules/harness-layer/spec-standards.md`
in the same commit series; a generalizable process lesson → one line in
`.claude/rules/development-log.md` per the memory-series contract. Skip both when
nothing generalizes — most runs add nothing.
