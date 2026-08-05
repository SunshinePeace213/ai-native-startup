---
description: The direct lane — ship a small, low-risk change in one session with an issue, convention branch, impl lint, one single-reviewer Codex round, PR with a metrics row, CI, and merge. Router-checked at intake; anything failing a check takes the full pipeline.
argument-hint: [request]
model: sonnet
effort: high
disable-model-invocation: true
---

# Harness Direct

Ship `REQUEST` end to end in this session. The lane exists so small changes have
a path cheaper than bypassing the pipeline — it still produces an issue, a
convention branch, an impl-lint pass, one Codex round under the citation
contract, a PR with a metrics row, and CI. It skips the spec folder, discovery,
artifacts, and the lens panel.

## Variables

REQUEST: $ARGUMENTS — the change to ship
ISSUE_NUMBER: `#N`, created in step 2 — the `Refs #N` footer and `Closes #N` key

## Router rule

Take this lane only when ALL four hold — any failure, or any doubt, → STOP and
recommend `/harness-layer:harness-plan "<request>"`:

| Check | Direct lane requires |
| --- | --- |
| Size | ≤ 2 files and roughly ≤ 80 changed lines |
| Type | `docs` / `chore` / `style` / `fix` with an obvious, local cause |
| Surface | No executable surface (`.claude/hooks/`, `settings.json`, `checks/`, `scripts/`, `.github/workflows/`) and no security boundary |
| Novelty | Creates no new command, skill, agent, or rule file |

## Workflow

1. **Route** — evaluate the rule above; record which checks passed as one line
   for the issue body. Failing → stop with the full-lane recommendation.
2. **Issue & branch** — fill `specs/_templates/issues/<kind>.md` (usually
   `chore`), then `gh issue create --title "<emoji> <type>: <title>"
   --body-file <tmp> --label <type> --label priority:P<n> --assignee <login>`,
   with the router line in the body. Link the branch:
   `gh issue develop <N> --base main --name <type>/<N>-<slug>` and check it out.
3. **Implement** — make the change; run the tests the change touches. Commit
   per git-workflow.md with the `Refs #N` footer.
4. **Impl lint** — `uv run scripts/impl_lint.py --direct --base origin/main`
   from the repo root (commit format + orphan scan; there is no plan folder).
   Fix every FAIL and re-run to green.
5. **Codex round** — ONE single reviewer, read-only, model + effort per the
   model-selection rule for a simple change:

   ```bash
   codex exec -C "<repo root>" -s read-only \
     --model <codex-model> -c model_reasoning_effort="<effort>" \
     -o "<scratch>/direct-round-1.md" \
     "<prompt>" > "<scratch>/direct-round-1.md.log" 2>&1
   ```

   Prompt: `You are the single cross-model reviewer of a small direct-lane
   change. Read .claude/rules/harness-layer/impl-standards.md, then review
   git diff origin/main..HEAD.` plus the codex-gate skill's finding-contract
   block. Dead run → retry once; still dead → review the diff against the
   standards yourself and note the substitution in the metrics row. Classify
   per the gate: blocking = cited standard + critical/major + confidence ≥ 80;
   uncited → advisory. Fix blocking findings yourself, commit, and re-run the
   lint — the deterministic floor. Advisories go to the PR `## Follow-ups`.
6. **PR** — `gh pr create` (not draft) from the matching type template per
   pr-process.md: `Closes #N`, findings + dispositions, `## Follow-ups`, and the
   one-line metrics row in `## Summary`:
   `Lane: direct · 1 cycle · <X> blocking fixed / <Y> advisory · lint <clean|N fixed> · substitutions <none|lead>`
7. **CI & merge** — wait for `gh pr checks` to pass, then
   `gh pr merge <PR> --squash --match-head-commit <head-sha>` with the
   normalized subject and `Refs #N` body; confirm `MERGED`.
8. **Lessons (light)** — on `main` after the merge: append the PR's metrics row
   to `specs/lessons/digest.md` `## Metrics log` (and bump a `## Categories`
   row only if a finding repeats a recorded class); commit
   `📝 docs(lessons): fold #<N> into the digest` with `Refs #N`, push to main.
9. **Cleanup & report** — delete the remote and local branch; end with the
   `## Report` output.

## Report

```text
✅ Direct Lane Shipped
Issue: #<N> · PR: #<M> — squash-merged, <merge sha> on main
Router: <the four checks, one line>
Metrics: Lane: direct · 1 cycle · <X> blocking fixed / <Y> advisory · lint <clean|N fixed>
Digest: metrics row appended <· category bumped: <class> | — no recurring class>
```
