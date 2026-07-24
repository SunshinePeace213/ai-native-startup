# Acceptance Criteria: Soriza design department — slice 1 (soriza-design)

> The definition of "done" for [spec.md](./spec.md). Every criterion is observable and testable, and
> every task in tasks.md should map to at least one criterion here. Epic-level: AC2–AC11 are
> verified child by child as each ships, then all together on `main` by `validate-all`.
> Rung-prompt *runtime* behavior is validated at three layers: structural assertions below,
> each child's harness-review, and the pilot's first intake (gaps land in
> `soriza-design/lessons.md`).

## Acceptance Criteria

- **AC1** — The epic planning docs (`specs/soriza-cpo-department/` including discovery/ and
  artifacts/) are merged to `main` via a docs PR referencing #43, before any child pipeline
  starts.
- **AC2** — `.worktreeinclude` contains an `ai-docs/*` pattern, and a worktree freshly created
  from the hydrated main checkout receives the cached mirrors (untracked-and-ignored files
  under `ai-docs/`). Mirrors are gitignored and never land on `main` via #44's PR — the epic
  driver's post-merge hydration (`/harness-layer:kb` in the main checkout) is what puts them
  in the creating checkout.
- **AC3** — `ai-docs/sources.yaml` carries a `design` group with five entries (WCAG 2.2
  quickref, web.dev Learn Design, NN/g homepage cornerstone, NN/g writing-for-the-web, Google
  Fonts Knowledge) plus an `anthropic` entry for the memory docs page — each with a canonical
  `url`, a `file` under its group folder, and a non-null `fetched` date; `ai-docs/index.md`
  lists them; no mirror was hand-authored.
- **AC4** — `projects/_template/` contains exactly the client scaffold: `intake.md`,
  `brief.md`, `sitemap-ia.md`, `asset-checklist.md`, `decision-log.md`, `wireframes/README.md`,
  `section-briefs/README.md`, and `section-briefs/_library/` with exactly nine skeletons
  (header-navigation, hero, logo-tape, features-solutions, testimonials, pricing-plans,
  content-blog, footer, cta-band) — every skeleton carrying both a "One job" and a "One desired
  action" field. No extra or missing files.
- **AC5** — `.claude/rules/soriza-design/` holds `client-communication.md`,
  `intake-standards.md`, `definition-of-ready.md`, `brief-format.md`, `section-anatomy.md`,
  `copywriting.md`, and `lessons.md`, each with `paths:` frontmatter scoping to
  `projects/**/*`, each with real starter content (no TBD/stub markers); `lessons.md` follows
  the development-log.md contract.
- **AC6** — `.claude/rules/soriza/roster.md` has one table row per staffer — Vera, Mira, Elias,
  Ivo, Juno, Lior — each row filling all four columns (name, position, deliverable owned,
  status); `AGENTS.md` points to the roster and the rules family and carries a `projects/`
  structure row; the set of root-level markdown files is unchanged (no new root memory file).
- **AC7** — `/soriza-design:intake` exists with `disable-model-invocation: true` and the Stop
  hook registered in its frontmatter, and carries a `## Rung Contract` block whose fields
  assert, clause-exact: `Staffer:` Mira; `Reads:` `intake-standards.md`; `First write:` the
  session-scoped marker `projects/<client>/.intake-in-progress.${CLAUDE_SESSION_ID}`;
  `Writes:` `projects/<client>/intake.md`; `DoR gate:` `intake.md` complete per
  `definition-of-ready.md`; `Refusal:` states refuse and names `intake.md`; `Commit:` states
  all three of `docs(<client>)`, `Refs #`, and the engagement branch. The command body
  asserts an idempotent never-clobber scaffold from `_template` and never touches another
  session's markers (no sweep clause anywhere). The marker pattern
  `projects/*/.intake-in-progress.*` is gitignored.
- **AC8** — `check_intake_readiness.py` scopes to its own session: it matches stdin's
  `session_id` against the marker suffix, exits 2 with per-section stderr diagnostics while
  any **own-session** marked client's `intake.md` is incomplete/missing — a
  **platform-bounded** block (Claude Code overrides after 8 consecutive Stop-hook blocks;
  the hook ignores `stop_hook_active`, never fakes success, and the rungs' DoR refusals
  catch an escaped incomplete intake) — exits 2 with a clear
  message when no own-session marker exists, exits 0 only when every own-marked client is
  complete — **leaving markers in place**: the hook never deletes any marker, so success is
  idempotently re-provable across repeated Stop firings. `_`-prefixed folders are never
  valid; fail-open (exit 0) on malformed stdin/plumbing errors. The session-independence
  regression proves session A (complete client A) exits 0 while session B's incomplete
  client-B marker exists — neither releasing nor stranding the other — and session B still
  exits 2 on its own marker; the same-client test proves two concurrent sessions marking one
  client each gate on their own distinct marker; the re-run regression proves intaking an
  already-complete client leaves the new session's marker in place; the deletion regression
  proves no code path deletes any marker; the cross-hook continuation regression proves two
  successive firings after completion both exit 0 (modeling another parallel Stop hook
  blocking once in between); the block-consistency regression proves an incomplete intake
  yields exit 2 on every firing, including with `stop_hook_active: true`. The hook's
  required-section tuple matches
  `definition-of-ready.md`'s checklist headings (sync test). All hook tests and the wiring
  pin pass.
- **AC9** — The four ladder commands exist under `/soriza-design:*`, and each carries a
  `## Rung Contract` block whose fields assert the exact chain — brief: Elias,
  reads `intake.md`, writes `brief.md`; sitemap: Ivo, reads `brief.md`, writes
  `sitemap-ia.md`; wireframe: Juno, reads `sitemap-ia.md`, writes into `wireframes/`;
  section-briefs: Lior, **reads `wireframes/`** (plus `decision-log.md` change requests, with
  `sitemap-ia.md` as inventory source), writes into `section-briefs/`. Per rung, clause-exact:
  `DoR gate:` names that rung's exact gated predecessor artifact (intake.md / brief.md /
  sitemap-ia.md / wireframes/); `Refusal:` states refuse **and** names that same missing
  artifact; `Commit:` states all three of `docs(<client>)`, `Refs #`, and the engagement
  branch.
- **AC10** — `wireframe.md`'s contract block carries, as parsed fields: `Format:` asserting
  lo-fi grayscale, self-contained, **no external dependencies**, and one page per screen in
  `wireframes/`; `Publish:` asserting best-effort (never blocks) and **all three** locked
  delivery modes (org share / consented public link / the HTML file itself) recorded in
  `decision-log.md`; `Reactions:` asserting copy-as-prompt reactions appended to
  `decision-log.md` as structured change requests. `section-briefs.md`'s contract block
  carries, as parsed fields: `Inventory:` asserting inline loop by default and parallel
  fan-out only for large inventories; `Copy:` asserting draft copy (slogan/headline/body)
  held to `copywriting.md`; a `Packet:` field listing brief + sitemap-ia + wireframes +
  section briefs + typography-direction page + asset checklist + decision log; and
  `Sign-off:` Vera before hand-off.
- **AC11** — `.claude/rules/soriza-design/git-lane.md` exists, `projects/**`-scoped, and
  asserts clause-level: the engagement issue/branch model (`docs/<N>-<client>` via
  `gh issue develop`); per-rung commits (`📝 docs(<client>)` + `Refs #N`); PRs at **exactly
  two gate points**, stated as exactly two one-line `- Gate:` bullets whose normalized
  {gate name → reference keyword} set equals exactly {"brief approved" → `Refs #N`,
  "packet hand-off" → `Closes #N`} — extra gate bullets, missing pairs, bullets carrying
  both keywords, or swapped semantics all fail; an explicit no-PR-per-deliverable clause;
  and the evidence swap sentence (DoR checklist + decision-log entry + client sign-off
  **replace** Test Evidence in `projects/**` PRs).
- **AC12** — Every child issue #44–#48 is closed by its own merged PR (one pipeline run per
  child); epic #43's checklist is fully ticked.

## Validation Commands

Validation logic lives in committed check scripts under [checks/](./checks/) — one script per
criterion, each invoked in exactly one line below; every script exits non-zero on any failure.
Stage tags mark the earliest point a command can pass; reviewers run only the commands whose
stage has been reached and record the rest as deferred. AC2–AC11 are `[child-build-time]` —
verified child by child as each ships, then all together on `main` by `validate-all`; AC1 and
AC12 are `[post-merge]` — provable only after all child PRs merge.

- `[post-merge]` `uv run --script specs/soriza-cpo-department/checks/ac1_epic_docs_merge.py` — verifies AC1 (epic docs PR #49 merged referencing #43; every child PR's branch descends from its merge commit).
- `[child-build-time]` `uv run --script specs/soriza-cpo-department/checks/ac2_worktreeinclude.py` — verifies AC2 (ai-docs pattern present; the script's docstring names the full scratch-worktree check).
- `[child-build-time]` `uv run --script specs/soriza-cpo-department/checks/ac3_kb_sources.py` — verifies AC3 (exact source identities + index entries; run from a KB-hydrated checkout).
- `[child-build-time]` `uv run --script specs/soriza-cpo-department/checks/ac4_template_scaffold.py` — verifies AC4 (exact file set + both fields in all nine skeletons).
- `[child-build-time]` `uv run --script specs/soriza-cpo-department/checks/ac5_rules_family.py` — verifies AC5.
- `[child-build-time]` `uv run --script specs/soriza-cpo-department/checks/ac6_roster.py` — verifies AC6 (adjust the expected root-md list only if `main` already tracks another root file at merge time).
- `[child-build-time]` `uv run --script specs/soriza-cpo-department/checks/ac7_intake_contract.py` — verifies AC7 (clause-exact contract fields; no sweep).
- `[child-build-time]` `uv run pytest tests/harness-layer/hooks/ -k "intake or wiring"` — verifies AC8 (contract, fail-open, doctrine-sync, cross-client regression, wiring pin). All green.
- `[child-build-time]` `uv run --script specs/soriza-cpo-department/checks/ac9_ladder_contracts.py` — verifies AC9 (exact chain; DoR/refusal/commit clause-exact per rung).
- `[child-build-time]` `uv run --script specs/soriza-cpo-department/checks/ac10_wireframe_sectionbriefs.py` — verifies AC10 (format, delivery modes, reactions, inventory, copy, packet, sign-off — all parsed fields).
- `[child-build-time]` `uv run --script specs/soriza-cpo-department/checks/ac11_git_lane.py` — verifies AC11 (both gate points, swap clause, exclusion).
- `[post-merge]` `uv run --script specs/soriza-cpo-department/checks/ac12_children_closed.py` — verifies AC12 (all five checkboxes ticked, every child CLOSED with ≥1 closing PR).
