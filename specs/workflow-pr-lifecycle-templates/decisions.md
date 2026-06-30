# Decisions: Unify the lifecycle on one PR + standardize workflow templates

> The grilling record for [spec.md](./spec.md) — why the plan is the way it is. Lifecycle tracking and
> the Codex review record live in spec.md, NOT here; this file is the immutable decision history.

## Summary

The owner opened a discussion (not a fixed feature request) about enhancing the
`plan-w-team → build → ship` lifecycle across four questions: the workflow standard & PR
timing (Q1), maximizing PR tracking to match plan-w-team's issue tracking (Q2),
standardizing every template/handoff (Q3), and cleaning up expired prompts in
build/ship/implementation-review (Q4). After exploring the codebase, the agreed scope is:
**open the draft PR at plan time** so a single PR threads the whole lifecycle; **advance the
Epic issue's lifecycle marker end-to-end**; centralize **all canonical templates in one
shared catalog** (`WORKFLOW-TEMPLATES.md`); **source the Agent Task Manifest from `tasks.md`**
with no false `#N` links; and apply a **narrow cleanup** (two stale refs) while **retaining**
the live legacy `plan.md` fallback. This is a Markdown harness-layer change — planning-only
here; the edits land via `/build`.

## Resolved Decisions

- **Q:** When should the PR be created, and how many tracking surfaces should the lifecycle use?
  - **A:** Open the **draft PR at the end of `/plan-w-team`** (right after the first plan
    push); single PR surface plan→build→ship; `/build` resumes it; the Epic issue stays the
    durable spine.
  - **Why:** Eliminates the branch-but-no-PR gap, makes the plan a reviewable PR diff from
    minute one, and matches PR-early (GitHub-flow) practice — directly answering the owner's
    "it seems a bit weird."
  - **Pros:** one continuous diff (plan→code→merge); single review surface; no orphan branch.
    **Cons:** the PR's "Files changed" is markdown-only until build begins; `/build` must
    resume rather than create (small added branch in the logic). **Rejected alternative:**
    keep PR creation at `/build` start (leaves the gap + frozen issue unaddressed).

- **Q:** Should the Epic issue's lifecycle advance during build/ship, or stay PR-owned?
  - **A:** `/build` advances the issue marker to **Build**, `/ship` to **Done** — the issue
    mirrors the whole lifecycle live.
  - **Why:** Today the issue freezes at "Approved" until `Closes #N` fires at merge, so Build
    and Ship are invisible on the spine.
  - **Pros:** the spine reflects real status end-to-end. **Cons:** two extra `gh` edits
    (build start, ship merge), each behind the existing graceful-`gh` skip.

- **Q:** Now that the PR exists at plan time, where does the Codex spec-review verdict go?
  - **A:** **Issue authoritative, PR mirrors state.** Canonical verdict comment + status
    block stay on the issue (history); the PR body's Spec-review status block mirrors only
    the latest verdict (state).
  - **Why:** The issue _is_ the spec surface; the PR shows single-glance state without a
    duplicate comment thread.
  - **Pros:** clean history/state split; no double-posting. **Cons:** the verdict state is
    written in two places per round (issue body + PR body) — mitigated by both reusing the
    same catalog snippet. **Rejected:** consolidating spec-review fully onto the PR (mixes
    spec and code discussion); keeping it issue-only (PR has no spec-review visibility).

- **Q:** The Agent Task Manifest uses `#<taskId>` (numeric from `TaskList`), which
  auto-links the PR to random GitHub issues/PRs. What should it reference?
  - **A:** **Source the manifest from `tasks.md`** — kebab-case Task IDs (non-linking by
    nature), grouped by Implementation Phase, each citing the AC it satisfies; tick each on
    `Task*` completion. **No bare `#<number>`; `Closes #N` stays the only GitHub reference.**
  - **Why:** Fixes the false auto-links _and_ the `tasks.md`-kebab vs runtime-numeric ID
    mismatch in one move, and ties the PR audit checklist directly to the plan.
  - **Pros:** correct links, stable IDs, AC traceability. **Cons:** `/build` constructs the
    manifest from `tasks.md` instead of a verbatim `TaskList` copy (slightly more logic);
    legacy flat specs without `tasks.md` degrade to the runtime board with non-`#` IDs.
    **Rejected:** backtick-wrapping `#3` (still reads like a GitHub ref to humans).

- **Q:** Where do the canonical templates live?
  - **A:** **One shared catalog** — `WORKFLOW-TEMPLATES.md` at repo root, cited from
    `AGENTS.md` like `GIT-COMMIT-PR-MESSAGE.md`; all three commands and both skills reference
    it; commands stop embedding duplicate snippets.
  - **Why:** DRY single source of truth; leaner command context (the owner's point — "commands
    not required to record them, better context management").
  - **Pros:** one edit point; no drift between plan/build snippets. **Cons:** one level of
    indirection (commands cite a file) — acceptable, since commands already cite `AGENTS.md`.
    **Rejected:** inline-in-each-command (duplication/drift); a `.claude/rules/` doc
    (auto-loads into every session → context bloat).

- **Q:** What is genuinely expired and should be cleaned up?
  - **A:** **Narrow cleanup.** Fix `GIT-COMMIT-PR-MESSAGE.md` (`epic-plan.md`→`epic-spec.md`,
    `specs/<feature>/plan.md`→`spec.md`) and `ship.md` ("Workstream C" dangling ref); update
    the manifest description. **Retain** the legacy `plan.md` fallback in `build.md`.
  - **Why:** A scan found no large dead bodies of prompt text. The `plan.md` fallback is
    **live** — 7 existing `specs/*/plan.md` folders depend on it — so removing it would break
    `/build` for archived work.
  - **Pros:** honest, low-risk cleanup. **Cons:** none material. **Rejected:** removing the
    fallback (breaks 7 folders); migrating the 7 historical folders (archival, out of scope).

## Assumptions

- **Catalog location** — recorded as repo-root `WORKFLOW-TEMPLATES.md` (sibling to
  `GIT-COMMIT-PR-MESSAGE.md`). _Invalidated if_ the owner prefers `.github/` or a `docs/` home.
- **Validation is structural** — prompt/Markdown changes are validated by grep-based
  structural checks + the Codex spec-review gate, not a runtime test suite. _Invalidated if_
  a behavioral dry-run of the full lifecycle is required as a gate.
- **Skill edits are light-touch** — only the Claude-owned _relay_ note in each skill points
  at the catalog; the finding bar / verdict rule / output contract are untouched.
  _Invalidated if_ the owner wants the skills' own report formats centralized too.
- **PR type = branch type** — the plan-time draft PR uses the same `<type>` as the
  convention branch (here `chore`). _Invalidated if_ a plan's eventual implementation type
  should differ from its branch type.

## Open Questions / Out of Scope

- **Out of scope:** altering the Codex skills' core review logic / finding bars / verdict rules.
- **Out of scope:** changing `/ship`'s squash-merge mechanics or guard set.
- **Out of scope:** CI / GitHub Actions / any automation beyond command & skill prompts.
- **Out of scope:** migrating the 7 historical `specs/*/plan.md` folders to the four-file layout.
- **Out of scope:** changing the worktree-mangled-branch / Option-B push-refspec convention.
- **Open question:** exact catalog file path (root vs `.github/`) — owner to confirm if the
  root sibling is not preferred; default proceeds with repo-root.
