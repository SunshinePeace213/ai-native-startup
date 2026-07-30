#!/usr/bin/env bash
# AC1 — clients/ is a real directory contract, ignored by git, and invisible to the
# spec-completeness gate. Run from the repo root. Exit 0 = pass.
set -uo pipefail

root=$(git rev-parse --show-toplevel)
cd "$root" || exit 1
fail=0
note() {
  echo "FAIL: $1"
  fail=1
}

# The directory contract survives a clean checkout only if .gitkeep is tracked.
[ -f clients/.gitkeep ] || note "clients/.gitkeep is missing — the directory contract is not checked in"
git ls-files --error-unmatch clients/.gitkeep >/dev/null 2>&1 ||
  note "clients/.gitkeep is not tracked — a clean checkout would have no clients/ at all"

# Anything else under clients/ must be ignored, so client work never enters history.
git check-ignore -q clients/acme/site/project-brief.md ||
  note "clients/acme/site/project-brief.md is NOT ignored — client data would be committable"

scratch="clients/.ac1-probe/notes.md"
mkdir -p "$(dirname "$scratch")"
printf 'probe\n' >"$scratch"
if [ -n "$(git status --porcelain clients/ 2>/dev/null)" ]; then
  note "a file written under clients/ shows in git status — the ignore rule is too narrow"
fi
rm -rf clients/.ac1-probe

# The spec gate walks specs/ only: a client folder must not change its verdict.
probe=$(mktemp -d)
trap 'rm -rf "$probe"' EXIT
mkdir -p "$probe/specs" "$probe/clients/acme/site/sign-off"
printf 'x\n' >"$probe/clients/acme/site/sign-off/p2.md"
CLAUDE_PROJECT_DIR="$probe" uv run --script .claude/hooks/check_spec_completeness.py \
  <<<'{"stop_hook_active": false}' >/dev/null 2>&1
before=$?
mkdir -p "$probe/clients/beta/shop/sign-off"
printf 'x\n' >"$probe/clients/beta/shop/sign-off/p6.md"
CLAUDE_PROJECT_DIR="$probe" uv run --script .claude/hooks/check_spec_completeness.py \
  <<<'{"stop_hook_active": false}' >/dev/null 2>&1
after=$?
[ "$before" -eq "$after" ] ||
  note "check_spec_completeness.py changed its verdict ($before -> $after) when a client folder was added"

[ "$fail" -eq 0 ] && echo "AC1 pass: clients/ is contracted, ignored, and invisible to the spec gate"
exit "$fail"
