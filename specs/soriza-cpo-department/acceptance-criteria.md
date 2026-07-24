# Acceptance Criteria: Soriza design department — slice 1 (soriza-design)

> The definition of "done" for [spec.md](./spec.md). Every criterion is observable and testable, and
> every task in tasks.md should map to at least one criterion here. Epic-level: AC2–AC11 are
> verified child by child as each ships, then all together on `main` by `validate-all`.

## Acceptance Criteria

- **AC1** — The epic planning docs (`specs/soriza-cpo-department/` including discovery/ and
  artifacts/) are merged to `main` via a docs PR referencing #43, before any child pipeline
  starts.
- **AC2** — `.worktreeinclude` contains an `ai-docs/*` pattern, and a freshly created worktree
  receives the cached mirrors (untracked-and-ignored files under `ai-docs/`).
- **AC3** — `ai-docs/sources.yaml` carries a `design` group with five entries (WCAG 2.2
  quickref, web.dev Learn Design, NN/g homepage cornerstone, NN/g writing-for-the-web, Google
  Fonts Knowledge) plus an `anthropic` entry for the memory docs page — each with a canonical
  `url`, a `file` under its group folder, and a non-null `fetched` date; `ai-docs/index.md`
  lists them; no mirror was hand-authored.
- **AC4** — `projects/_template/` contains exactly the client scaffold: `intake.md`,
  `brief.md`, `sitemap-ia.md`, `asset-checklist.md`, `decision-log.md`, `wireframes/README.md`,
  `section-briefs/README.md`, and `section-briefs/_library/` with nine skeletons
  (header-navigation, hero, logo-tape, features-solutions, testimonials, pricing-plans,
  content-blog, footer, cta-band) — every skeleton carrying a "One job" and a "One desired
  action" field.
- **AC5** — `.claude/rules/soriza-design/` holds `client-communication.md`,
  `intake-standards.md`, `definition-of-ready.md`, `brief-format.md`, `section-anatomy.md`,
  `copywriting.md`, and `lessons.md`, each with `paths:` frontmatter scoping to
  `projects/**/*`, each with real starter content (no TBD/stub markers); `lessons.md` follows
  the development-log.md contract.
- **AC6** — `.claude/rules/soriza/roster.md` lists all six staff (Vera, Mira, Elias, Ivo, Juno,
  Lior) with name, position, deliverable owned, and status; `AGENTS.md` points to the roster
  and the rules family and carries a `projects/` structure row; no new root-level markdown
  memory file exists.
- **AC7** — `/soriza-design:intake` exists with `disable-model-invocation: true` and the Stop
  hook registered in its frontmatter; the command scaffolds `projects/<client>/` from the
  template idempotently (never clobbers) and writes `intake.md`.
- **AC8** — `check_intake_readiness.py` blocks (exit 2, per-section stderr diagnostics) on a
  missing or incomplete newest `projects/<client>/intake.md`, passes (exit 0) on a complete
  one, ignores `_`-prefixed folders, and fails open on malformed stdin/plumbing errors; its
  required-section tuple matches `definition-of-ready.md`'s checklist headings (sync test); all
  hook tests and the wiring pin pass.
- **AC9** — The four ladder commands exist under `/soriza-design:*`; each names its staffer,
  reads the previous rung's file, refuses on unmet DoR naming what's missing, and commits per
  rung on the engagement branch.
- **AC10** — `wireframe.md` mandates lo-fi grayscale self-contained HTML (one page per screen,
  no external dependencies) in `projects/<client>/wireframes/`, best-effort private artifact
  publishing, and copy-as-prompt reactions appended to `decision-log.md` as structured change
  requests; `section-briefs.md` mandates the inline inventory loop with parallel fan-out only
  for large inventories, draft copy (slogan/headline/body) held to `copywriting.md`, a
  typography-direction page, and Vera's sign-off before hand-off.
- **AC11** — `.claude/rules/soriza-design/git-lane.md` exists, `projects/**`-scoped, defining
  the engagement issue/branch model, per-rung commits, gate-point-only PRs, and the evidence
  swap (DoR checklist + decision-log entry + client sign-off replace Test Evidence).
- **AC12** — Every child issue #44–#48 is closed by its own merged PR (one pipeline run per
  child); epic #43's checklist is fully ticked.

## Validation Commands

Run these to prove the criteria above. Map each command to the criteria it verifies.

- `git log --oneline origin/main -- specs/soriza-cpo-department/ | head -3` — verifies AC1. Non-empty after the epic docs PR merges.
- `grep -n "ai-docs" .worktreeinclude` — verifies AC2. Shows the `ai-docs/*` line.
- `uv run --script .claude/hooks/worktree/worktree_create.py < /dev/null; echo ok` — AC2 plumbing sanity only (fail-open); the real check is a fresh `EnterWorktree` containing `ai-docs/*/…` mirrors.
- `uv run python -c "import yaml,sys; m=yaml.safe_load(open('ai-docs/sources.yaml')); d=m.get('design',[]); assert len(d)==5 and all(e['fetched'] for e in d), d; print('design ok')"` — verifies AC3.
- `grep -c "code.claude.com/docs/en/memory" ai-docs/sources.yaml` — verifies AC3 (≥1).
- `ls projects/_template/ projects/_template/section-briefs/_library/ | wc -l` && `grep -rL "One desired action" projects/_template/section-briefs/_library/` — verifies AC4. Nine library files; the `-L` list is empty.
- `for f in client-communication intake-standards definition-of-ready brief-format section-anatomy copywriting lessons; do head -5 ".claude/rules/soriza-design/$f.md" | grep -q "projects/\*\*" && echo "$f ok"; done` — verifies AC5 scoping; `grep -rn "TBD\|TODO\|fill me" .claude/rules/soriza-design/` returns nothing.
- `grep -c "Vera\|Mira\|Elias\|Ivo\|Juno\|Lior" .claude/rules/soriza/roster.md` — verifies AC6 (≥6); `grep -n "roster\|soriza-design\|projects/" AGENTS.md` shows the pointers.
- `head -20 .claude/commands/soriza-design/intake.md | grep -E "disable-model-invocation|check_intake_readiness"` — verifies AC7.
- `uv run pytest tests/harness-layer/hooks/ -k "intake or wiring"` — verifies AC8. All green.
- `ls .claude/commands/soriza-design/` — verifies AC9. Five files: intake, brief, sitemap, wireframe, section-briefs.
- `grep -ln "grayscale\|copy-as-prompt" .claude/commands/soriza-design/wireframe.md && grep -ln "typography\|sign-off\|fan-out" .claude/commands/soriza-design/section-briefs.md` — verifies AC10.
- `head -5 .claude/rules/soriza-design/git-lane.md | grep "projects/\*\*"` && `grep -n "Test Evidence" .claude/rules/soriza-design/git-lane.md` — verifies AC11.
- `gh issue list --search "44 45 46 47 48" --state closed --json number,closedByPullRequestsReferences` and `gh issue view 43` — verifies AC12. Five closed children, each with its own PR; epic checklist ticked.
