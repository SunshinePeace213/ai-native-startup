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

# The directory contract survives a clean checkout only if .gitkeep is tracked. This is
# what catches the `clients/` (whole-directory) ignore pattern: git never descends into an
# excluded directory, so `!clients/.gitkeep` cannot re-include it and `git add` fails
# silently. The working pattern is `clients/*` plus the negation.
[ -f clients/.gitkeep ] || note "clients/.gitkeep is missing — the directory contract is not checked in"
git ls-files --error-unmatch clients/.gitkeep >/dev/null 2>&1 ||
  note "clients/.gitkeep is not tracked — a clean checkout would have no clients/ at all"

# Anything else under clients/ must be ignored, so client work never enters history.
git check-ignore -q clients/acme/site/project-brief.md ||
  note "clients/acme/site/project-brief.md is NOT ignored — client data would be committable"

probe_dir="clients/.ac1-probe"
mkdir -p "$probe_dir"
printf 'probe\n' >"$probe_dir/notes.md"
if [ -n "$(git status --porcelain clients/ 2>/dev/null)" ]; then
  note "a file written under clients/ shows in git status — the ignore rule is too narrow"
fi
# Safe-delete: non-recursive removal of exactly what this script created (AGENTS.md forbids
# `rm -rf`, and a recursive delete under a path built from a variable is the reason why).
rm -f "$probe_dir/notes.md"
rmdir "$probe_dir" 2>/dev/null

# The spec gate walks specs/ only. Take a NO-CLIENT baseline on a COMPLETE plan folder, so
# the expected verdict is a real 0 rather than "blocked for some other reason" — then add
# client projects and require it to still be 0. Comparing two already-clienty runs would let
# a hook that wrongly blocks whenever any client exists return 2 twice and pass.
probe=$(mktemp -d)
trap 'chmod -R u+w "$probe" 2>/dev/null; find "$probe" -type f -delete; find "$probe" -depth -type d -exec rmdir {} +' EXIT

plan="$probe/specs/demo-plan"
mkdir -p "$plan"
write_section() { printf '## %s\n\ncontent\n\n' "$1" >>"$2"; }
: >"$plan/spec.md"
for s in Tracking "Task Description" Objective Non-Goals "Requirements & Decisions" \
  "Relevant Files" "Edge Cases" "Risk & Rollback" Guardrails "Codex Verification"; do
  write_section "$s" "$plan/spec.md"
done
: >"$plan/tasks.md"
write_section "Step by Step Tasks" "$plan/tasks.md"
: >"$plan/acceptance-criteria.md"
for s in "Acceptance Criteria" "Validation Commands"; do
  write_section "$s" "$plan/acceptance-criteria.md"
done
: >"$plan/decisions.md"
for s in Summary "Resolved Decisions" Assumptions "Open Questions / Out of Scope"; do
  write_section "$s" "$plan/decisions.md"
done

gate() {
  CLAUDE_PROJECT_DIR="$probe" uv run --script .claude/hooks/check_spec_completeness.py \
    <<<'{"stop_hook_active": false}' >/dev/null 2>&1
  echo $?
}

baseline=$(gate)
[ "$baseline" -eq 0 ] ||
  note "baseline: a complete plan folder with no clients/ should pass the spec gate, got exit $baseline"

mkdir -p "$probe/clients/acme/site/sign-off" "$probe/clients/beta/shop/sign-off"
printf 'x\n' >"$probe/clients/acme/site/sign-off/p2.md"
printf 'x\n' >"$probe/clients/beta/shop/sign-off/p6.md"

after=$(gate)
[ "$after" -eq 0 ] ||
  note "the spec gate returned exit $after once client folders existed — it must never see them"

[ "$fail" -eq 0 ] && echo "AC1 pass: clients/ is contracted, ignored, and invisible to the spec gate"
exit "$fail"
