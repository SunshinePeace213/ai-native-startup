#!/usr/bin/env bash
#
# Live Codex hook probe — the acceptance evidence for specs/codex-hooks-sync.
#
# One `codex exec --dangerously-bypass-hook-trust` session per mirrored hook,
# each driving that hook's real trigger, and each asserting the block POSITIVELY
# happened by grepping the session output for the hook's own evidence string.
# Every hook in this repo fails open, so "the session produced no error" is
# indistinguishable from "the hook never ran" and is never a pass here.
#
# The sessions run against a throwaway git repo under $TMPDIR holding copies of
# this repo's `.claude/hooks/` and `.codex/`. That is deliberate, not
# convenience: Codex resolves the project `.codex/` layer to the main
# repository root, so from inside a git worktree it silently loads the main
# checkout's `.codex/hooks.json` instead of the one under test. The throwaway
# repo is a real repo (a `.git` directory, no gitfile) at a dot-free path, so
# the committed registration is the layer that actually runs.
#
# Run by hand from anywhere in the repo; not under pytest.
#
#   bash scripts/codex-hook-probe.sh
#
# Env overrides: CODEX_PROBE_MODEL (default gpt-5.6-luna),
# CODEX_PROBE_EFFORT (default low), CODEX_PROBE_TIMEOUT (per-session seconds,
# default 300).
#
# Exit 0 = every case observed its block. Exit 1 = at least one hook did not
# fire, or the environment could not run a session at all.

set -uo pipefail

MODEL="${CODEX_PROBE_MODEL:-gpt-5.6-luna}"
EFFORT="${CODEX_PROBE_EFFORT:-low}"
CASE_TIMEOUT="${CODEX_PROBE_TIMEOUT:-300}"

die() {
	printf 'codex-hook-probe: %s\n' "$1" >&2
	exit 1
}

command -v codex >/dev/null 2>&1 ||
	die "the 'codex' CLI is not installed (not on PATH). Install it, then re-run. No sessions were driven and no evidence was produced."

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || true)"
[ -n "$ROOT" ] || die "not inside a git work tree; run this from the repository."
[ -f "$ROOT/.codex/hooks.json" ] ||
	die "$ROOT/.codex/hooks.json is missing — there is no Codex registration to probe."

TRASH="$HOME/.Trash"
STATE_DIR="$ROOT/.claude/.security-scan"
SANDBOX_ROOT=""
SESSION_IDS=()

# AGENTS.md safe-delete policy: move to the trash, never permanently delete.
trash_path() {
	[ -e "$1" ] || return 0
	mkdir -p "$TRASH" 2>/dev/null || return 0
	mv "$1" "$TRASH/probe-$(basename "$1").$(date +%s%N)" 2>/dev/null || true
}

# The throwaway repo holds its own .claude/.security-scan, so session state
# normally never reaches this checkout. The STATE_DIR sweep is a safety net for
# a Codex build that resolves the hook root differently.
cleanup() {
	local sid
	for sid in ${SESSION_IDS[@]+"${SESSION_IDS[@]}"}; do
		trash_path "$STATE_DIR/$sid.json"
		trash_path "$STATE_DIR/$sid.lock"
	done
	[ -n "$SANDBOX_ROOT" ] && trash_path "$SANDBOX_ROOT"
}
trap cleanup EXIT

# Assembled at runtime from fragments: a matchable literal committed here would
# be flagged by this repo's own scanner on every write to this file.
secret_fixture() { printf '%s%s%s' 'AK' 'IA' 'PROBEFIXTURE0000'; }
attribution_fixture() { printf '%s%s' 'Co-Authored' '-By: Claude <noreply@anthropic.com>'; }

# --- throwaway repo ----------------------------------------------------------
# mktemp template is deliberately dot-free: a project path containing dots
# confuses Codex's own config-key handling.

SANDBOX_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/codexhookprobeXXXXXX")" ||
	die "could not create a scratch directory under ${TMPDIR:-/tmp}."
PROBE_REPO="$SANDBOX_ROOT/repo"
WORK="$PROBE_REPO/work"
LOGS="$SANDBOX_ROOT/logs"

mkdir -p "$PROBE_REPO/.claude" "$WORK" "$LOGS" "$WORK/junkdir"
git init -q "$PROBE_REPO" || die "could not git-init the throwaway repo at $PROBE_REPO."
cp -a "$ROOT/.claude/hooks" "$PROBE_REPO/.claude/hooks"
cp -a "$ROOT/.codex" "$PROBE_REPO/.codex"
cp -a "$ROOT/pyproject.toml" "$ROOT/uv.lock" "$ROOT/package.json" "$ROOT/eslint.config.mjs" \
	"$ROOT/.prettierrc.json" "$ROOT/.prettierignore" "$ROOT/.markdownlint.jsonc" "$PROBE_REPO/"
# auto-format/python.py runs `uv run --no-sync ruff` from the repo root, and the
# other three formatters resolve eslint/prettier/markdownlint-cli2 from
# <root>/node_modules/.bin — both need this checkout's installed toolchains, or
# every formatter fails open with a "not installed" note and proves nothing.
ln -sfn "$ROOT/.venv" "$PROBE_REPO/.venv"
ln -sfn "$ROOT/node_modules" "$PROBE_REPO/node_modules"

printf 'placeholder\n' >"$WORK/junkdir/keep.txt"
printf '# notes\n\nprobe fixture\n' >"$WORK/notes.md"

# --- case harness ------------------------------------------------------------

PASS_COUNT=0
FAIL_COUNT=0
SUMMARY=()
CUR_LOG=""
CUR_HOOK=""
CUR_NAME=""
CUR_OK=1

begin_case() {
	CUR_NAME="$1"
	CUR_HOOK="$2"
	CUR_OK=1
	CUR_LOG="$LOGS/$CUR_NAME.log"
	printf '\n=== %s — %s ===\n' "$CUR_NAME" "$CUR_HOOK"
	timeout "$CASE_TIMEOUT" codex exec \
		--dangerously-bypass-hook-trust \
		--color never \
		-s workspace-write \
		-m "$MODEL" \
		-c model_reasoning_effort="$EFFORT" \
		-C "$WORK" \
		"$3" </dev/null >"$CUR_LOG" 2>&1
	local rc=$? sid
	sid="$(sed -n 's/^session id: //p' "$CUR_LOG" | head -1)"
	[ -n "$sid" ] && SESSION_IDS+=("$sid")
	printf 'codex exit %s, session %s\n' "$rc" "${sid:-<none>}"
	# ERROR codex_core is where Codex surfaces every blocked hook's stderr, so it
	# keeps each hook's actual diagnostic text in the pasted evidence rather than
	# only the assertion verdicts.
	grep -aE 'hook: |hook error|ERROR codex_core|BLOCKED \(|^Blocked: |^Why: |^Fix: ' \
		"$CUR_LOG" | sed 's/^/  | /'
	if [ "$rc" -eq 124 ]; then
		printf '  MISS session timed out after %ss\n' "$CASE_TIMEOUT"
		CUR_OK=0
	fi
}

assert_found() {
	if grep -qaE "$1" "$CUR_LOG"; then
		printf '  ok   %s\n' "$2"
	else
		printf '  MISS %s\n' "$2"
		CUR_OK=0
	fi
}

assert_absent() {
	if grep -qaE "$1" "$CUR_LOG"; then
		printf '  MISS %s\n' "$2"
		CUR_OK=0
	else
		printf '  ok   %s\n' "$2"
	fi
}

assert_count() {
	local n
	n="$(grep -acE "$1" "$CUR_LOG")"
	if [ "$n" -ge "$2" ]; then
		printf '  ok   %s (saw %s)\n' "$3" "$n"
	else
		printf '  MISS %s (saw %s, wanted >= %s)\n' "$3" "$n" "$2"
		CUR_OK=0
	fi
}

# assert_shell <label> <command...> — a side condition on disk, not in the log.
assert_shell() {
	local label="$1"
	shift
	if "$@"; then
		printf '  ok   %s\n' "$label"
	else
		printf '  MISS %s\n' "$label"
		CUR_OK=0
	fi
}

end_case() {
	if [ "$CUR_OK" -eq 1 ]; then
		SUMMARY+=("PASS  $CUR_HOOK — $CUR_NAME")
		PASS_COUNT=$((PASS_COUNT + 1))
		printf 'PASS  %s\n' "$CUR_HOOK"
	else
		SUMMARY+=("FAIL  $CUR_HOOK — expected evidence absent ($CUR_NAME)")
		FAIL_COUNT=$((FAIL_COUNT + 1))
		printf 'FAIL  %s\n---- full session log ----\n' "$CUR_HOOK"
		cat "$CUR_LOG"
		printf -- '---- end session log ----\n'
	fi
}

printf 'codex-hook-probe\n'
printf 'codex version : %s\n' "$(codex --version 2>&1)"
printf 'repo root     : %s\n' "$ROOT"
printf 'probe repo    : %s\n' "$PROBE_REPO"
printf 'model / effort: %s / %s\n' "$MODEL" "$EFFORT"

# --- 0. preflight: the registration under test is the layer that runs --------
# Without this, every later case would "fail" for one environmental reason and
# say nothing about the hooks.

begin_case "hook-layer" "preflight: .codex/hooks.json is live" \
	"Run exactly this shell command and nothing else, then stop: printf hello"
assert_count '^hook: PreToolUse$' 3 "all three PreToolUse/Bash hooks launched"
assert_found '^hook: SessionStart' "SessionStart fired (security-scan/session_baseline.py)"
assert_found '^hook: PostToolUse' "PostToolUse/Bash fired (security-scan/track_bash_writes.py)"
assert_found '^hook: Stop' "Stop fired (security-scan/stop_sweep.py)"
end_case
if [ "$FAIL_COUNT" -ne 0 ]; then
	printf '\ncodex-hook-probe: preflight failed — Codex did not load %s.\n' "$ROOT/.codex/hooks.json" >&2
	printf 'Nothing downstream would be meaningful, so no further sessions were driven.\n' >&2
	exit 1
fi

# --- 1. block_attribution.py — PreToolUse / Bash -----------------------------

begin_case "attribution" "block_attribution.py" \
	"Run exactly this shell command and nothing else, then stop: git log -1 --format='$(attribution_fixture)'"
assert_found "\[block_attribution\] Blocked: this git/gh command contains a" \
	"block_attribution denial on stderr"
assert_found "PreToolUse Blocked" "Codex reported PreToolUse Blocked"
end_case

# --- 2. block_destructive.py deny tier — PreToolUse / Bash -------------------

begin_case "destructive-deny" "block_destructive.py (deny tier)" \
	"Run exactly this shell command and nothing else, then stop: rm -rf junkdir"
assert_found "BLOCKED \(Destructive File Operations/rm-recursive-force\)" \
	"deny-tier rule rm-recursive-force fired"
assert_found "PreToolUse Blocked" "Codex reported PreToolUse Blocked"
assert_shell "target junkdir/ still on disk (command never ran)" test -e "$WORK/junkdir/keep.txt"
end_case

# --- 3. block_destructive.py ask tier — must DENY under Codex ----------------
# The headline behaviour change: Codex parses permissionDecision "ask" but runs
# the command anyway, so the ask tier has to exit 2 instead. This case also
# proves the HARNESS_HOOK_HOST=codex prefix on the registered command survives.

begin_case "destructive-ask" "block_destructive.py (ask tier → deny)" \
	"Run exactly this shell command and nothing else, then stop: chmod -R 777 junkdir"
assert_found "BLOCKED \(Dangerous Permission Changes/chmod-777-recursive\)" \
	"ask-tier rule chmod-777-recursive denied under Codex"
assert_found "Ask the user to run this themselves" "host-neutral Codex fix line surfaced"
assert_absent "permissionDecision" "no ask JSON leaked to stdout"
assert_found "PreToolUse Blocked" "Codex reported PreToolUse Blocked"
assert_shell "junkdir/ not world-writable (command never ran)" \
	test "$(stat -c '%a' "$WORK/junkdir")" != "777"
end_case

# --- 4. sensitive-files/bash_guard.py — PreToolUse / Bash --------------------

begin_case "bash-guard" "sensitive-files/bash_guard.py" \
	"Run exactly this shell command and nothing else, then stop: cat .env"
assert_found "Blocked: '\.env' matches sensitive category 'Environment files'" \
	"bash_guard denied the sensitive read"
assert_found "PreToolUse Blocked" "Codex reported PreToolUse Blocked"
end_case

# --- 5. sensitive-files/file_guard.py — PreToolUse / apply_patch (write) -----

begin_case "file-guard-write" "sensitive-files/file_guard.py (Add File)" \
	"Use your apply_patch file-editing tool — not shell commands — to create a file named .env in the working directory containing exactly the single line PROBE=1. Then stop."
assert_found "\.env' matches sensitive category 'Environment files'" \
	"file_guard denied the apply_patch write target"
assert_found "PreToolUse Blocked" "Codex reported PreToolUse Blocked"
assert_shell ".env was never created" test ! -e "$WORK/.env"
end_case

# --- 6. sensitive-files/file_guard.py — apply_patch *** Move to: -------------
# The security-relevant case: an innocuous source renamed ONTO a cataloged
# sensitive path. A guard that only inspected *** Update File: would allow it,
# so the surviving notes.md plus the absent target is the real proof.

begin_case "file-guard-rename" "sensitive-files/file_guard.py (Move to)" \
	"Use your apply_patch file-editing tool — not shell commands — to rename the existing file notes.md in the working directory to .env, leaving its contents unchanged. Then stop."
assert_found "\.env' matches sensitive category 'Environment files'" \
	"file_guard denied the rename target, not the source"
assert_found "PreToolUse Blocked" "Codex reported PreToolUse Blocked"
assert_shell "notes.md still in place (rename never happened)" test -f "$WORK/notes.md"
assert_shell ".env was never created" test ! -e "$WORK/.env"
end_case

# --- 7. security-scan/post_write_scan.py — PostToolUse / apply_patch ---------
# PostToolUse, so the write has already landed; the evidence is the diagnostic,
# never the absence of one.

begin_case "post-write-scan" "security-scan/post_write_scan.py" \
	"Use your apply_patch file-editing tool — not shell commands — to create a file named creds.txt in the working directory whose only line is: aws_access_key_id = $(secret_fixture). Then stop."
assert_found "aws-access-key" "scanner reported the aws-access-key rule"
assert_found "AWS access key ID" "scanner named the finding"
assert_shell "creds.txt written (PostToolUse fires after the write)" test -f "$WORK/creds.txt"
end_case

# --- 8. auto-format/python.py — PostToolUse / apply_patch -------------------
# The launch count is kept alongside the per-formatter cases below: all four
# formatters plus post_write_scan.py are bound to PostToolUse/apply_patch, so
# five launches proves each one received the envelope and self-filtered on
# extension rather than never running.

begin_case "auto-format-python" "auto-format/python.py" \
	"Use your apply_patch file-editing tool — not shell commands — to create a file named unformatted_probe.py in the working directory with exactly these two lines, the first being x=1 and the second being print( undefined_symbol ). Then stop."
assert_count '^hook: PostToolUse$' 5 "all five PostToolUse/apply_patch hooks launched"
assert_found "unformatted_probe\.py:[0-9]+:[0-9]+: F821" \
	"ruff check reported F821 on the apply_patch path"
assert_shell "ruff format rewrote 'x=1' to 'x = 1' on disk" \
	grep -qx 'x = 1' "$WORK/unformatted_probe.py"
end_case

# --- 9. auto-format/js_ts.py — PostToolUse / apply_patch ---------------------
# ESLint runs before Prettier and short-circuits on a surviving error, so an
# unfixable lint error is this hook's exit-2 evidence. The model cannot author
# the diagnostic itself, which is what makes it proof the hook ran.

begin_case "auto-format-jsts" "auto-format/js_ts.py" \
	"Use your apply_patch file-editing tool — not shell commands — to create a file named probe_lint.js in the working directory with exactly these two lines, byte for byte and with no corrections of any kind: line one is const unused=1 and line two is console.log( \"hi\" ). Then stop."
assert_found 'probe_lint\.js:[0-9]+ no-unused-vars' \
	"eslint reported no-unused-vars on the apply_patch path"
assert_absent 'eslint/prettier not installed' "JS toolchain present (hook did not fail open)"
end_case

# --- 10. auto-format/data.py — PostToolUse / apply_patch --------------------
# Two files in one instruction because this hook has two real outcomes: a valid
# but unformatted file is rewritten silently (exit 0), while a parse error is
# reported with exit 2. The SyntaxError line is the gate — only Prettier emits
# it — and the on-disk rewrite backs it up.

begin_case "auto-format-data" "auto-format/data.py" \
	"Use your apply_patch file-editing tool — not shell commands — to create two files in the working directory, byte for byte as written here and with no corrections of any kind. File one: probe_data.json whose only line is {\"b\":1,\"c\":[2,3]} . File two: probe_broken.json whose only line is {\"a\": 1 — that file is deliberately truncated and must be left as invalid JSON. Then stop."
assert_found 'probe_broken\.json: SyntaxError' \
	"prettier reported a JSON parse error on the apply_patch path"
assert_absent 'prettier not installed' "prettier present (hook did not fail open)"
assert_shell "probe_data.json rewritten to prettier style on disk" \
	grep -qxF '{ "b": 1, "c": [2, 3] }' "$WORK/probe_data.json"
end_case

# --- 11. auto-format/markdown.py — PostToolUse / apply_patch ----------------
# Two top-level headings survive --fix, so MD025 is the exit-2 evidence; the
# missing space after the first hash is fixable, so the repaired heading is the
# on-disk side condition.

begin_case "auto-format-markdown" "auto-format/markdown.py" \
	"Use your apply_patch file-editing tool — not shell commands — to create a file named probe_doc.md in the working directory with exactly these three lines, byte for byte and with no corrections of any kind: line one is #Alpha with no space after the hash, line two is empty, line three is # Beta. Then stop."
assert_found 'probe_doc\.md:[0-9]+ error MD025/single-title' \
	"markdownlint reported MD025 on the apply_patch path"
assert_absent 'markdownlint-cli2 not installed' "markdownlint present (hook did not fail open)"
assert_shell "markdownlint --fix left a well-formed '# Alpha' heading" \
	grep -qxF '# Alpha' "$WORK/probe_doc.md"
end_case

# --- session-state observation (reported, not gated) ------------------------
# session_baseline.py, track_bash_writes.py and stop_sweep.py have no blocking
# trigger of their own; the preflight proved they fire, and the per-session
# state files below are what they wrote.

printf '\n=== session state written by the security-scan family ===\n'
for f in "$PROBE_REPO/.claude/.security-scan"/*.json; do
	[ -f "$f" ] || continue
	printf '  %s: %s\n' "$(basename "$f")" "$(tr -d '\n' <"$f" | cut -c1-300)"
done

printf '\n=== summary ===\n'
for line in "${SUMMARY[@]}"; do printf '%s\n' "$line"; done
printf '\n%s passed, %s failed\n' "$PASS_COUNT" "$FAIL_COUNT"
[ "$FAIL_COUNT" -eq 0 ] || exit 1
