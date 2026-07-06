# Spec: Attribution guard — Python hook + attribution settings

- **Owner:** @SunshinePeace213
- **Status:** Approved
  <!-- Lifecycle, set by /plan-w-team: Drafted for Review → Approved (after a Codex `approved`
       verdict) → Needs Human Review (still changes-requested after 2 Codex rounds). One value only. -->

## Task Description

The repo policy ([GIT-COMMIT-PR-MESSAGE.md](../../GIT-COMMIT-PR-MESSAGE.md)) forbids Claude
attribution in commit and PR messages. Today that policy is enforced by a single shell hook,
`.claude/hooks/block-coauthor-trailer.sh`, which greps the entire PreToolUse JSON payload for
`Co-Authored-By: Claude` and exits 2 when found. It works, but it is crude: it false-blocks any
Bash command that merely *mentions* the trailer text (e.g. writing documentation about it), and it
only catches one of the three attribution forms Claude Code produces.

This plan replaces it with two complementary layers:

1. **Prevention** — configure Claude Code's documented attribution settings so no attribution is
   generated in the first place: `"attribution": {"commit": "", "pr": "", "sessionUrl": false}`
   (empty strings hide commit/PR attribution; `sessionUrl: false` drops the `Claude-Session`
   trailer; this supersedes the deprecated `includeCoAuthoredBy`).
2. **Enforcement** — rewrite the hook in Python (`.claude/hooks/block_attribution.py`, run via
   `uv run --script`, stdlib only, same conventions as `lint.py`). It parses the payload JSON
   properly, acts only on Bash commands that actually invoke `git`/`gh`, and blocks all default
   Claude attribution forms — not just the co-author trailer.

## Objective

Claude Code sessions in this repo emit no Claude attribution: settings stop it at the source, and
any `git`/`gh` command that still carries a default Claude attribution string is deterministically
denied (exit 2) with corrective stderr feedback — while non-git commands that merely mention those
strings pass through untouched.

## Non-Goals

- **No custom attribution text.** The user explicitly deferred customizing `attribution.commit` /
  `attribution.pr`; both are set to `""` for now (revisit later).
- **No Codex-side changes** beyond repointing the existing `.codex/hooks.json` PreToolUse
  command at the new guard (build-time amendment: that config executed the deleted shell
  script, and Codex's hook contract — `tool_input.command` payload, exit 2 blocks, per
  `ai-docs/openai/codex/hooks.md` — matches the guard's stdin contract). No other Codex
  config or attribution work.
- **No changes to the other hooks** (`lint.py`, `install_deps.py`, `check-spec-completeness.sh`).
- **No change to GIT-COMMIT-PR-MESSAGE.md** — "no attribution" matches its current text verbatim.
- **No automated enforcement of the settings-sync rule** — it ships as an AGENTS.md rule only;
  a merge-time check (CI or hook) is a possible future chore.

## Problem Statement

Attribution settings exist (documented at
[ai-docs/anthropic/settings.md](../../ai-docs/anthropic/settings.md) § Attribution settings) and
can hide all Claude attribution — which raised the question: is the hook still needed? The grilling
settled it: settings are *prevention* (Claude Code stops auto-appending), but they cannot *block* a
trailer that a model, subagent, or plugin command writes by hand into a commit message. Per the
hooks guide, hooks exist precisely to guarantee rules deterministically "rather than relying on the
LLM to choose." So: settings turn attribution off at the source; the hook stays as the enforcement
backstop — rewritten in Python to fix its false positives and coverage gaps.

## Solution Approach

Migrate the shared config into a tracked `.claude/settings.json` — the documented team scope —
carrying `enabledPlugins`, the hooks block, and the new `attribution` block, and swap the PreToolUse
hook command from the shell script to a new Python guard. `.claude/settings.local.json` becomes an
untracked personal scratchpad (it overrides the project file in-session), governed by a new
AGENTS.md rule: experiment locally, fold shippable changes into `settings.json` before merging to
main. The guard reads the hook payload from
stdin, and only when `tool_name == "Bash"` **and** the command string contains a `git`/`gh` token
does it scan for the three default Claude attribution patterns (case-insensitive):
`Co-Authored-By: Claude …` (any model name), `Claude-Session:`, and `Generated with [Claude Code]`.
A match prints the policy to stderr and exits 2 (PreToolUse deny, stderr fed back to Claude — the
documented blocking mechanism for settings-based hooks); anything else exits 0, including malformed
input (fail-open: a guard must never wedge every Bash call). Subprocess-based pytest tests encode
the block/allow matrix.

*Alternative considered:* settings only, delete the hook — simplest, but leaves the policy
unenforced when a message hand-carries the trailer (e.g. a harness system prompt instructing the
model to add it). Rejected in grilling (Q1).

## Requirements & Decisions

- **Both layers, not one** — attribution settings (prevention) + Python hook (enforcement); the
  settings alone can't block hand-written trailers (user-locked, grilling Q1).
- **No attribution at all for now** — `commit: ""`, `pr: ""`, `sessionUrl: false`; customization
  is explicitly deferred (user-locked, grilling Q2).
- **Precision over paranoia** — the hook must stop false-blocking benign commands: parse JSON,
  inspect only `tool_input.command`, and require a `git`/`gh` token before pattern-matching.
- **Block every default form** — co-author trailer with any model name, `Claude-Session:` trailer,
  and the `🤖 Generated with [Claude Code]` PR footer; exit 2 + stderr guidance on match.
- **settings.json is the shared truth** — plugins, hooks, and attribution migrate to a tracked
  `.claude/settings.json`; `.claude/settings.local.json` becomes an untracked personal scratchpad;
  AGENTS.md gains the sync rule (fold shippable local changes into `settings.json` before merging
  to main). User-locked, post-approval revision extending Codex's advisory.

## Tracking

<!-- Recorded by /plan-w-team. The Issue field is the SINGLE SOURCE OF TRUTH /build reads — /build
     NEVER re-derives #N from the mangled local branch name. spec.md is the single home for this
     block; decisions.md does not duplicate it. -->

- **Issue:** none — deferred
- **Branch:** `chore/attribution-guard-python-hook`
- **Worktree:** `/home/ringo/ai-native-startup/.claude/worktrees/chore+attribution-guard-python-hook`

## Relevant Files

Use these files to complete the task:

- `.claude/hooks/block-coauthor-trailer.sh` — the shell hook being replaced; remove with `git rm`
  once the Python guard is registered (recoverable from git history — never `rm -rf`).
- `.claude/settings.local.json` — migration source: its `enabledPlugins` and `hooks` move into the
  new `settings.json`; the file is then untracked (`git rm --cached`) and reset on disk to `{}`.
- `.gitignore` — gains a `.claude/settings.local.json` line so the scratchpad stays personal.
- `AGENTS.md` — gains the settings-sync rule (experiment in `settings.local.json`, fold shippable
  changes into `settings.json` before merging to main).
- `.claude/hooks/lint.py` — style reference: `uv run --script` shebang, PEP 723 inline metadata,
  stdin-read pattern (`select` with timeout), fail-open `main()` wrapper.
- `pyproject.toml` — add `pytest>=8` to the existing `[dependency-groups] dev` list so
  `uv sync` (SessionStart / `/meta-install`) installs it.
- `HARNESS-LAYER.md` — the "Block Claude Commit Trailer (PreToolUse)" section and the Files tree
  describe the old shell hook; update both.
- `.codex/hooks.json` — Codex PreToolUse registration of the same guard; repointed from the
  deleted shell script to `block_attribution.py` (build-time amendment, see decisions.md).

### New Files

- `.claude/settings.json` — the tracked shared config: `enabledPlugins`, `hooks` (PreToolUse →
  `block_attribution.py`, PostToolUse lint, SessionStart install), and the `attribution` block.
- `.claude/hooks/block_attribution.py` — the Python guard (stdlib only; PEP 723 header with
  `requires-python = ">=3.12"`, empty `dependencies`).
- `tests/harness-layer/hooks/test_block_attribution.py` — subprocess-based pytest suite feeding JSON
  payloads to the script and asserting exit codes + stderr.

## Edge Cases

- **Non-Bash tool payload** (`tool_name` ≠ `"Bash"`) → exit 0 immediately.
- **Empty, missing, or malformed stdin JSON** → exit 0 (fail-open; the guard must never break
  unrelated tool calls — matches `lint.py`'s posture).
- **Command mentions a pattern but never invokes git/gh** (e.g. writing docs about the trailer via
  `cat > file` heredoc) → allowed. This is the false positive the rewrite fixes.
- **Trailer smuggled any way into a git/gh command** — `-m` flag, heredoc, `-F`/`--body-file`
  inline content, `--amend`, `gh pr create/edit/comment --body` → blocked. Matching is on the whole
  command string, so the delivery mechanism doesn't matter.
- **Case variants** (`co-authored-by: claude sonnet 5 <…>`) → blocked (case-insensitive match).
- **Any model name in the trailer** (`Claude Sonnet 5`, `Claude Opus 4.8`, `Claude Fable 5`, bare
  `Claude`) → blocked: match `co-authored-by:\s*claude`, not an exact full string.
- **Non-Claude co-author** (`Co-Authored-By: Alice <alice@example.com>`) → allowed; the policy
  targets Claude attribution only.
- **`github`/`git`-like substrings** in paths or words must not count as a git invocation — use
  word-boundary matching (`\bgit\b` does not match `github`).
- **`uv` missing or script unreadable** → the hook command itself fails; per documented exit-code
  semantics a non-2 failure does not block the tool call. Accepted risk; `install_deps.py` owns
  keeping `uv` present.
- **Stale personal scratchpad** — hooks merge across settings scopes, so a leftover
  `settings.local.json` still registering the deleted shell hook would fail on every Bash call.
  The migration must reset the on-disk file to `{}`; its old content survives in `settings.json`
  and git history.
- **Idempotency / concurrency** — the guard is a pure read-only check on stdin; no state, safe to
  run on every Bash call and in parallel sessions.

## Red Flags

- Starting to write code without any written requirements
- Asking "should I just start building?" before clarifying what "done" means
- Implementing features not mentioned in any spec or task list
- Making architectural decisions without documenting them
- Skipping the spec because "it's obvious what to build"
- Reintroducing whole-payload grep matching "to be safe" — the false-positive fix is a requirement
- Adding config files, pattern allowlists, or CLI flags to the hook — nothing configurable was
  requested; patterns are constants in the script
- Deleting the old hook with `rm` instead of `git rm`, or before the new one is registered

## Notes

- The KB holds two hook docs that describe **different config formats**: `hooks-guide.md` documents
  the settings-based format this repo uses (`hooks.PreToolUse[].matcher/hooks[]`, snake_case
  `tool_input`, exit 2 blocks with stderr fed back); `hooks.md` (reference) documents a
  `hooks.json` format with camelCase fields and stdout-JSON decisions. This plan follows the
  settings-based format — it is what the repo runs today and what the guide's "Block edits to
  protected files" recipe grounds. Do not mix the two.
- New dev dependency: `pytest>=8` via `uv add --dev pytest` (or editing `[dependency-groups]`
  directly, matching how `ruff` is pinned).
- Run tests with `uv run pytest tests/harness-layer/hooks/ -q` after `uv sync`.
- Follow-up (out of scope): revisit custom attribution text once the user decides on wording.

## Codex Findings

<!-- CODEX-OWNED. Written only by the spec-review skill (one `### Round N — Verdict: …` block per
     round). Claude must NEVER edit this section. -->

### Round 1 — Verdict: changes-requested

- `acceptance-criteria.md` AC6's validation command for the removed shell hook is self-failing:
  `git ls-files .claude/hooks/ | grep -c block-coauthor-trailer.sh` prints `0` when the hook is
  gone, but `grep` exits 1 on no match, so the validation step can fail after a correct build.
  Replace it with an exit-status-safe check, for example
  `! git ls-files --error-unmatch .claude/hooks/block-coauthor-trailer.sh` or
  `test "$(git ls-files .claude/hooks/block-coauthor-trailer.sh | wc -l)" -eq 0`.

**Recommendations (advisory, non-blocking):**

- The plan's use of tracked `.claude/settings.local.json` matches the repo's current working
  convention, but `ai-docs/anthropic/settings.md` and `ai-docs/anthropic/hooks-guide.md` describe
  local settings as personal / not shareable and `.claude/settings.json` as the shareable project
  location. Keep the current scope decision if intentional; otherwise move the shared hook and
  attribution settings to `.claude/settings.json`.

### Round 2 — Verdict: approved

The spec meets the harness-build bar with no remaining blocking findings.

### Round 3 — Verdict: approved

The revised settings.json migration and settings-sync rule meet the harness-build bar with no remaining blocking findings.

## Codex Verification

<!-- CLAUDE-OWNED. The outcome summary Claude records after the Codex loop. -->

- **Outcome:** approved at round 2 (round 1 `changes-requested` — the AC6 grep-exit-code
  validation defect — fixed in commit `4bd325f`); the post-approval settings.json migration +
  sync-rule revision (user-directed, extending Codex's advisory) was re-verified and approved at
  round 3
- **Rejected findings:** none — the single blocking finding was applied and the advisory was
  applied in extended form per the user's directive (see decisions.md)

## References

```
specs/attribution-guard-python-hook/
├── spec.md                 # this file — what & why, tracking, review record
├── decisions.md            # grilling record: resolved decisions, assumptions, out-of-scope
├── tasks.md                # how & who: phases, team, step-by-step tasks
└── acceptance-criteria.md  # done: acceptance criteria + validation commands
```

## Self Validation

- [x] Objective, Task Description, and Non-Goals are filled in (no placeholders left)
- [x] Requirements trace to tasks in tasks.md and to checks in acceptance-criteria.md
- [x] Acceptance criteria are specific and testable
- [x] All four files exist under specs/attribution-guard-python-hook/ and are saved in the repository
- [x] Codex has reviewed the spec and Status reflects the outcome
