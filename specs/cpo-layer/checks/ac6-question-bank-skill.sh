#!/usr/bin/env bash
# AC6 — the question bank is a registered skill the roles can invoke, and the coverage
# checker re-derives its dimensions from that skill rather than carrying a copy.
# Run from the repo root. Exit 0 = pass.
set -uo pipefail

root=$(git rev-parse --show-toplevel)
cd "$root" || exit 1
skill=".claude/skills/studio-layer/client-questions/SKILL.md"
checker=".claude/scripts/studio-layer/check_question_coverage.py"
fail=0
note() {
  echo "FAIL: $1"
  fail=1
}

[ -f "$skill" ] || {
  echo "FAIL: $skill does not exist"
  exit 1
}

frontmatter=$(awk 'NR>1 && /^---[[:space:]]*$/{exit} NR>1{print}' "$skill")
grep -q '^name:' <<<"$frontmatter" || note "$skill declares no name:"
grep -q '^description:' <<<"$frontmatter" || note "$skill declares no description:"

# The flag would make the bank user-invocable only, putting it out of reach of the very
# roles meant to invoke it.
grep -q 'disable-model-invocation' <<<"$frontmatter" &&
  note "$skill sets disable-model-invocation — the roles could no longer invoke it"

# The client dimensions the bank must cover.
for dimension in job audience voice reference content constraint budget success; do
  grep -qi "$dimension" "$skill" || note "$skill covers no '$dimension' dimension"
done

[ -f "$checker" ] || note "$checker is missing — the bank is prose without it"
if [ -f "$checker" ]; then
  # Re-derivation is the whole point: the checker must read the skill, not restate it.
  grep -q 'SKILL.md' "$checker" ||
    note "$checker does not read SKILL.md — a second hard-coded dimension list pins nothing"
fi

[ "$fail" -eq 0 ] && echo "AC6 pass: the question bank is invocable and its coverage is re-derived"
exit "$fail"
