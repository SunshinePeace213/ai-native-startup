---
description: The lessons deep pass — Workflow fan-out over every shipped findings ledger, cluster the recurring classes, adversarially verify each candidate amendment against the record, and land survivors as direct-lane PRs amending a standard, template, or lint. Run monthly (schedule or /loop), or on demand when the digest looks stale.
argument-hint: []
model: opus
effort: xhigh
disable-model-invocation: true
---

# Harness Lessons

Mine the shipped record for amendments the pipeline should carry, and land only
the ones that survive adversarial verification. The light pass at every ship
keeps `specs/lessons/digest.md` current; this deep pass turns its recurring rows
into durable changes.

## Inputs

- Every `specs/*/reviews/findings-ledger.md` and `specs/*/summary.md` `## Metrics` block
- `specs/lessons/digest.md` — current categories and dispositions

## Workflow

1. **Collect** — list the shipped plans that have a ledger; read the digest.
2. **Fan out (Workflow diamond)** — run a Workflow: one agent per shipped
   ledger, each returning TYPED candidates
   `{surface, class, ledger_rows, proposed_target: standard|template|lint, proposed_amendment}` —
   raw ledger prose never crosses the merge.
3. **Cluster** — merge candidates across plans by class; a class needs 2+
   occurrences (or one `critical`) to proceed. Uncited-finding classes recurring
   2+ times are candidate NEW standards.
4. **Adversarial verify** — in the same Workflow, for each candidate spawn a
   verifier prompted to REFUTE: "Would this amendment have prevented a real
   cycle in the record? Cite the ledger row(s) it would have caught, or refute
   it." Unrefuted with cited rows → survivor; everything else → drop or keep
   `watching`.
5. **Land survivors** — each survivor ships as its own direct-lane PR
   (`/harness-layer:harness-direct` flow) amending exactly one thing: a
   standards file (new ID, never renumber), a `specs/_templates/` file, or a
   lint check with its contract test. A lint amendment touches `scripts/` —
   executable surface, so it takes the FULL lane instead.
6. **Update the digest** — flip each landed class's disposition
   (`amended (<file>)` / `lint added (<script>)`), bump `Seen`/`Plans` counts,
   and append a one-line deep-pass note with the date and PR numbers. Commit
   `📝 docs(lessons): deep pass <YYYY-MM>` and push per the branch you are on
   (main → direct commit; otherwise a direct-lane PR).

## Report

```text
✅ Lessons Deep Pass
Ledgers read: <N> · candidates: <M> · survived verification: <K>
Landed: <one line per amendment — target file + PR #>
Watching: <classes left in the digest>
Digest: updated @ <commit sha>
```
