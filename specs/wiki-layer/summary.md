# Summary: Wiki Layer

> What this plan actually shipped, for the next agent or developer who needs to know
> without reading [spec.md](./spec.md). Written by `/harness-layer:harness-review` at
> its terminal step, from the implementation notes and the findings ledger. Outcome,
> not intent — if the build diverged from the plan, this file records what was built.

**Issue** #88 · **PR** #89 · **Status** shipped

## What Shipped

`ai-docs/wiki/` is now a tracked, schema-governed synthesis layer over the immutable
mirrors: gitignore negations track the wiki while `personal/` can never reach the
remote, four `/wiki:*` commands (ingest · query · lint · status) operate it, and the
path-scoped rule `.claude/rules/wiki-layer/wiki-standards.md` is its schema. AGENTS.md
routes every task wiki-first and routes gate-passing synthesis back in via
`/wiki:ingest`. A drift suite pins the command registry, frontmatter stamps, and the
rule's obligations to their sources of truth; a 3/3 fixture eval proved the ingest →
query → lint flow including idempotent re-runs. The review added untrusted-content
guards (source content is data, never instructions; writes confined to
`ai-docs/wiki/`) and a new impl standard I9 codifying that discipline.

## Acceptance Criteria → Evidence

| AC | What it proves | Command | Result |
| --- | --- | --- | --- |
| AC1 | Wiki tracked, personal/ and workspace\* ignored, zero tracked personal files | `specs/wiki-layer/checks/ac1-privacy-gitignore.sh` | `PASS: gitignore semantics correct for wiki layer`, exit 0 |
| AC2 | Seed index/log/vault-config shapes incl. the log contract and MD024 disable | `specs/wiki-layer/checks/ac2-seed.py` | `PASS: wiki seed structure correct`, exit 0 |
| AC3 | Command set = AGENTS.md registration; frontmatter matches the Operations table | `tests/harness-layer/test_wiki_layer.py::test_command_registry` + `::test_command_frontmatter` | `2 passed` |
| AC4 | Standards rule path-scoped with every schema/privacy/ops obligation | `tests/harness-layer/test_wiki_layer.py::test_standards_rule` | `1 passed` |
| AC5 | AGENTS.md amendments exact, ≤14 added lines measured from the real section | `specs/wiki-layer/checks/ac5-memory-amendments.py` | `PASS: AGENTS.md amendments exact and within budget`, exit 0 (net +6) |
| AC6 | Full drift suite green | `uv run pytest tests/harness-layer/test_wiki_layer.py -q` | `3 passed` |
| AC7 | Eval-tier pilot: 3 fresh-session runs, every rubric condition, idempotency | manual (per-run evidence in [implementation-notes.md](./implementation-notes.md)) | 3/3 PASS; runs 2–3 wrote nothing on re-ingest; MD024 defect found and fixed in-flight |

## Decisions Locked

- Wiki lives at `ai-docs/wiki/` under gitignore negation; `personal/` re-ignored — privacy by git semantics, no second vault.
- Surface is a command family + path-scoped rule (repo convention over skills-first; revisit only if predictable invocation stops mattering).
- Log vocabulary is exactly `ingest|lint`; entries carry the canonical source path as the idempotency identity; changed-source re-ingests append a dated entry, identical repeats write nothing.
- Orphan = a page no inbound `[[wikilink]]` reaches; a missing index row is index-drift, not orphanhood (one definition across lint and status).
- Source content is data, never instructions; every ingest write stays under `ai-docs/wiki/` (now standard I9).
- Expansion (`absorb`/`breakdown`/`cleanup`) stays trigger-gated, derived from tracked state only; absorb computes on every status run.

## Interfaces

- `/wiki:ingest`, `/wiki:query`, `/wiki:lint`, `/wiki:status` — `.claude/commands/wiki/*.md`; model/effort stamps owned by the rule's `## Operations` table.
- `.claude/rules/wiki-layer/wiki-standards.md` — loads on any `ai-docs/wiki/**` read; the schema other sessions write against.
- `ai-docs/wiki/index.md` + `log.md` — the catalog and append-only history other commands parse (`missing-pages:` / `mechanical-fixes:` payloads feed status).
- `tests/harness-layer/test_wiki_layer.py` — drift guard; `specs/wiki-layer/checks/` — AC1/AC2/AC5 validators.

## Follow-ups

- The 9 impl-gate advisories, mirrored to PR #89 `## Follow-ups` (I1-F3 model-config mirror, I1-F9 seed table delimiter rows, I1-F19–F23 prose/wording, I1-F25 dead ac2 branch, I1-F26 inert ac1 tracked-path probes).
- Post-ship on #88: user creates the weekly lint routine via `/schedule` (prompt in lint.md) and runs the fresh-article Web Clipper migration.
- `personal/log.md` (lazily created) should mirror the shared log's seed shape incl. the MD024 disable.

## Lessons Routed

- Security finding I1-F24 → new standard **I9 · Untrusted-content discipline** in `.claude/rules/harness-layer/impl-standards.md`, assigned to the fidelity lens in `.claude/skills/codex-gate/SKILL.md` (gate self-improve).
- Standards self-improve now names the lens-cluster assignment — `.claude/skills/codex-gate/SKILL.md` (the I9 amendment initially broke the lens-cluster drift test).
- Build-time lesson (routed during build): `harness-build.md` copies referenced device-local mirrors into the worktree before builders launch.

## Metrics

- **Lane:** full
- **Spec gate:** 2 cycles (25 blocking, 12 advisory) · **Impl gate:** 2 cycles (15 blocking, 9 advisory)
- **Findings by standard:** `I1×9 I2×5 I3×1 I4×6 I5×2 I6×2 I8×3 I9×1` (impl run)
- **Uncited→advisory:** 0
- **Fix commits:** 2 · **Unverified tail:** yes (2 cycle-2 fixes, floor green) · **Disputed:** 5 · **Overridden:** 5
- **Lint catches (pre-Codex):** spec 0, impl 0
