# Implementation Notes: Seed the design KB group + worktree availability (child #44 of epic #43)

> Chronological dev log for [spec.md](./spec.md), created from this template at
> `/harness-layer:harness-build` implement start and appended by both
> `/harness-layer:harness-build` and `/harness-layer:harness-review` as the work
> proceeds.
>
> Boundary: per-plan phases, hand-offs, deviations, fixes, and lessons live here.
> Cross-plan one-liners go to `.claude/rules/development-log.md` instead.

## Log

- **2026-07-24 · build start** — build lead entered the recorded worktree at head `7d17a0d`
  (clean, branch `worktree-soriza-design-kb-seed` tracking
  `origin/chore/44-soriza-design-kb-seed`). Plan files read in full; kb-grounded checks done:
  `copy_worktree_includes()` in `worktree_create.py` re-verified (fnmatch vs
  `git ls-files -oi --exclude-standard`, rel path or basename), WorktreeCreate-replaces-stock
  confirmed against `ai-docs/anthropic/worktrees.md` + `hooks.md` (main-checkout mirrors,
  fresh).
- **2026-07-24 · deviation (process)** — plan-said use the shared Task* board
  (TaskCreate/TaskUpdate/TaskList) / did track tasks via builder hand-offs and this log /
  why: the Task board tools are not available in this session's harness (only TaskStop and
  SendMessage exist). No locked decision or acceptance criterion touches the board; task
  order, ownership, and dependencies from tasks.md are enforced by sequential deployment.
- **2026-07-24 · worktreeinclude-pattern hand-off** — kb-builder appended the comment +
  `ai-docs/*` lines; AC1 baseline check green (`AC1 ok: one pattern, comment above,
  baseline preserved`); no deviations. Checkpoint commit `5f17db3` pushed.
- **2026-07-24 · deviation (resolved under epic pre-authorization)** — plan-said NN/g
  homepage cornerstone `nngroup.com/articles/top-10-guidelines-for-homepage-usability/`
  (spec row 3, marked "proposed"; both NN/g URLs are build-time picks) / did register
  `nngroup.com/articles/113-design-guidelines-homepage-usability/` / why: the proposed URL
  is a genuine HTTP 404 (curl-verified). kb-builder honored the spec's stop condition
  (halted after sources 1–2, deleted the provisional `fetched: null` entry); the epic
  driver returned an authorized substitute — the canonical superset of the dead Top-10
  digest, same topic — which satisfies the locked epic constraint verbatim (nngroup.com +
  `homepage` in URL, exactly two `articles/` URLs once source 4 lands) and passes every AC
  validation script unchanged. Recorded: FAIL/swap line in decisions.md build addendum;
  spec.md identity-table row 3 updated to the registered URL with a swap note.
  Surfaced for review in the PR Dev Notes.
- **2026-07-24 · process note** — builders must hand off in their final message; the
  kb-builder's mid-task SendMessage attempt failed (no such recipient) and its state came
  back via the epic driver. Later resumes instructed final-message hand-off explicitly.
- **2026-07-24 · kb-seed-design partial hand-off** — sources 3–4 registered and mirrored
  after the authorized NN/g swap: `design/nngroup-homepage-usability.md`
  (113-design-guidelines-homepage-usability) and `design/nngroup-writing-for-the-web.md`
  (how-users-read-on-the-web). Design group at 4/5 fully-fetched entries; manifest, index,
  and build addendum internally consistent; provisional entry for the failed source 5
  cleanly deleted per the replacement contract's hygiene rule.
- **2026-07-24 · BUILD HALTED — locked-AC deviation needs user approval** — source 5
  `https://fonts.google.com/knowledge` is a genuine fetch failure (JS-only SPA: kb-fetcher
  and curl both get a script shell with zero static text; Knowledge sub-pages and
  m3.material.io/styles/typography verified as SPA shells too). The spec's stop condition
  fired: AC2 makes the fonts.google.com identity **unconditional** ("their fetch failure is
  a build stop, never a swap") and the round-3 Codex fix locked substitution to the WCAG
  quickref only. The epic driver directed a swap to `https://web.dev/learn/design/typography`
  plus rewriting AC2's identity assertions to exact-URL equality (the substring marker
  `web.dev/learn/design` would double-match). That edit touches a Codex-locked acceptance
  criterion and a locked resolved decision ("exactly five: … Google Fonts Knowledge";
  "any other source → stop and propose an official alternative to Ringo") — per the build
  command this STOPS for explicit user approval; an agent directive cannot stand in for it.
  Build paused before kb-seed-memory/validator/tidy/PR; partial state committed and pushed.
  Resume paths (all need a plan-level amendment): (a) approve the web.dev/typography swap +
  AC2 marker adjustment, (b) pick a different official static typography source, (c) drop
  or redefine source 5.
- **2026-07-24 · build resumed after gated amendment** — the halt was resolved through the
  proper gate: spec amendment `efac876` (authored by Ringo, Codex round 5 approved,
  0 blocking — `reviews/codex-spec-review-round-5.md`) resolves source 5 to
  `https://web.dev/learn/design/typography`, moves AC2 to exact-URL equality over the
  resolved five, requires one FAIL/swap line per authorized swap, and CLOSES substitution
  (any new failure of the final five is a hard stop). Build resumed on head `b36b756`.
- **2026-07-24 · kb-seed-design complete (5/5) + kb-seed-memory hand-off** — kb-builder
  registered `design/learn-design-typography.md` (typography swap FAIL/OK pair appended)
  and `anthropic/memory.md` (canonical URL unchanged, 461-line mirror). Verified on disk:
  design group equals the resolved identity set exactly, manifest 32 entries / 32 unique
  URLs, zero `fetched: null`, all six mirrors carry matching frontmatter + In-here lines,
  index.md lists all six. Builder deviations flagged: memory fetcher wrapped its OK line in
  extra prose (verified independently, harmless); markdown formatter angle-bracketed the
  addendum URLs (non-breaking — validation matches by substring). No blockers.
- **2026-07-24 · validate-all hand-off** — validator (fresh agent) ran all 9 validation
  commands from the worktree root: all green, AC1–AC6 PASS, no deviations, no fixes needed.
  Notable: AC1 fnmatch simulation matched 7 KB files; AC6 exact-surface confirmed the
  tracked diff outside `specs/` is exactly `.worktreeinclude` + `ai-docs/sources.yaml` with
  no stray untracked files.
- **2026-07-24 · tidy** — harness-simplifier (opus) reviewed the two touched files vs
  `origin/main` at head `b46b05e`: clean, 0 auto-fixes; one non-defect flagged (double
  em-dash in the typography entry's machine-managed topic line, left untouched).
  code-simplifier skipped — no app code in this change. No tidy commit needed.
- **2026-07-24 · draft PR** — #50 opened
  (<https://github.com/SunshinePeace213/ai-native-startup/pull/50>), labels `chore` +
  `priority:P2` mirroring issue #44, body from the chore template with Plan links,
  Closes #44, stage table (Implementation + Tidy ticked), Agent Task Manifest from the
  hand-offs, tidy report posted as the `<!-- report:tidy -->` comment and linked under
  Review Reports.
- **2026-07-24 · memory step** — the memory-marked task (worktreeinclude-pattern) called
  for a dev-log lesson on the worktree-include/WorktreeCreate-hook interplay only if it bit
  during the build. It did not bite: the single `ai-docs/*` pattern worked first try under
  the hook's fnmatch semantics (AC1 simulation green, 7 files). No dev-log entry recorded.
