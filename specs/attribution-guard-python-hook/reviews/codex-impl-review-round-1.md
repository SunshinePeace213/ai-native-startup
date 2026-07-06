### Round 1 — Verdict: changes-requested
Lenses: code-standards, comment-accuracy, silent-failure, simplification, and KB-grounding ran; type-design and test-coverage skipped because this is harness/config code, not application code.

Validation:
- AC1 co-author trailer hook command: PASS
- AC2 Claude Code PR footer hook command: PASS
- AC3 clean git commit hook command: PASS
- AC4 non-git documentation heredoc hook command: PASS
- AC5 non-Bash payload and malformed JSON hook commands: PASS
- AC6 settings JSON attribution/hook/plugins command: PASS
- AC9 scratchpad untracked/ignored/reset command: PASS
- AC9 AGENTS.md settings-sync grep command: PASS
- AC6 old shell hook removed command: PASS
- AC7 pytest hook suite command: PASS
- AC8 HARNESS-LAYER.md documentation command: PASS

Validation note: the first unprefixed `uv` attempt failed because this review sandbox cannot write `/home/ringo/.cache/uv`; the commands were rerun with `UV_CACHE_DIR=/tmp/uv-cache`, and the real outputs matched the pass conditions.

## Digest

2 blocking findings:
- Plan adherence: `.codex/hooks.json` was changed even though Codex-side attribution/config is explicitly out of scope.
- silent-failure: `read_command()` swallows unexpected exceptions silently, so the required fail-open diagnostic path is bypassed.

No KB-grounding contradictions were found for the Claude settings/hook claims. The cited cached docs are fresh: `ai-docs/anthropic/settings.md` fetched 2026-07-06; `ai-docs/anthropic/hooks-guide.md`, `ai-docs/anthropic/hooks.md`, `ai-docs/astral/uv-scripts.md`, and `ai-docs/openai/codex/hooks.md` fetched 2026-07-05.

## Findings

### Plan Adherence

**Blocking — Codex hook config changed outside the approved scope.**

- Location: `.codex/hooks.json:9`
- Grounding: `specs/attribution-guard-python-hook/spec.md:39-40` says "No Codex-side changes"; `specs/attribution-guard-python-hook/decisions.md:100-101` says Codex-side attribution/config is out of scope and Codex sessions are not governed by Claude Code hooks/settings.
- Problem: the implementation rewires the repo-local Codex PreToolUse hook to execute `.claude/hooks/block_attribution.py`. That may be a practical response to deleting `.claude/hooks/block-coauthor-trailer.sh`, but it is still outside the approved written scope.
- Fix: either revert the `.codex/hooks.json` change and handle the old Codex hook reference in a plan-approved way, or reopen/amend the plan to explicitly include Codex hook migration plus Codex-specific validation.

### KB Grounding

No blocking KB-grounding findings.

- `.claude/settings.json` uses the project settings location, `enabledPlugins`, `hooks`, and `attribution` keys grounded by `ai-docs/anthropic/settings.md`.
- The Claude PreToolUse hook shape, `tool_input`, `CLAUDE_PROJECT_DIR`, and exit-2 stderr blocking behavior are grounded by `ai-docs/anthropic/hooks-guide.md` and `ai-docs/anthropic/hooks.md`.
- The `uv run --script` shebang and PEP 723 metadata are grounded by `ai-docs/astral/uv-scripts.md`.
- `.codex/hooks.json` is a valid Codex hook location and Codex can use `tool_input.command` plus exit code 2 per `ai-docs/openai/codex/hooks.md`, but that does not remove the plan-adherence blocker above.

### silent-failure

**Blocking — unexpected read/parse errors are swallowed without the required diagnostic.**

- Location: `.claude/hooks/block_attribution.py:67`
- Grounding: `specs/attribution-guard-python-hook/tasks.md:73-74` requires wrapping `main()` so unexpected exceptions note to stderr and exit 0; the silent-failure lens flagged the inner `except Exception: return None`.
- Problem: `read_command()` catches every exception from stdin readiness, reading, JSON parsing, and payload access, then returns `None` with no stderr note. Expected empty/malformed input should fail open, but unexpected hook/runtime bugs inside this path never reach the outer `main()` wrapper and are indistinguishable from "no command."
- Fix: catch expected fail-open cases narrowly, and for unexpected exceptions emit a short stderr diagnostic before returning `None` or let them reach the existing outer wrapper.

## Advisory Findings

### comment-accuracy

- `.claude/hooks/block_attribution.py:8-10`, `HARNESS-LAYER.md:27-31`, and `specs/attribution-guard-python-hook/spec.md:24-33` use "invoke" language, while `tasks.md:65-67` and `decisions.md` define the implemented gate as a word-boundary `git`/`gh` token. This is not blocking because the implementation matches the locked task detail, but the prose should say "contains a git/gh token" unless real shell invocation parsing is intended.
- `tests/harness-layer/hooks/test_block_attribution.py:123-127` calls the no-`git` heredoc case the old shell hook's false positive. The old shell hook also required a `git`/`gh` token in the full payload, so this specific fixture documents the desired allow behavior but does not reproduce the old hook's exact false positive.

### simplification

- `.claude/hooks/block_attribution.py:6-15` and `tests/harness-layer/hooks/test_block_attribution.py:1-10` can be shortened without losing executable behavior or test intent.
- `specs/attribution-guard-python-hook/spec.md` and `tasks.md` repeat some process/rationale already carried by `decisions.md` or AGENTS.md. This is non-blocking, but trimming would reduce harness context load.
