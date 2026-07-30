#!/usr/bin/env bash
# AC7 — eight phase commands exist, and exactly the four hard gates register the sign-off
# hook in frontmatter, each with its own phase argument.
# Run from the repo root. Exit 0 = pass.
set -uo pipefail

root=$(git rev-parse --show-toplevel)
cd "$root" || exit 1
dir=".claude/commands/studio-layer"
fail=0
note() {
  echo "FAIL: $1"
  fail=1
}

[ -d "$dir" ] || {
  echo "FAIL: $dir does not exist"
  exit 1
}

phases=(p0-intake p1-discovery p2-definition p3-structure p4-art-direction p5-prototype p6-handoff p7-retro)
for phase in "${phases[@]}"; do
  [ -f "$dir/$phase.md" ] || note "$dir/$phase.md is missing"
done

count=$(find "$dir" -name '*.md' | wc -l)
[ "$count" -eq 8 ] || note "expected 8 phase commands, found $count"

# Only the hard gates register the hook. Firing it on a soft gate is the thing the
# eight-command shape exists to prevent.
gated=(p2 p3 p4 p6)
for file in "$dir"/*.md; do
  [ -f "$file" ] || continue
  stem=$(basename "$file" .md)
  token=${stem%%-*}
  frontmatter=$(awk 'NR>1 && /^---[[:space:]]*$/{exit} NR>1{print}' "$file")

  if grep -q 'check_gate_signoff\.py' <<<"$frontmatter"; then
    registered=yes
  else
    registered=no
  fi

  if [[ " ${gated[*]} " == *" $token "* ]]; then
    [ "$registered" = yes ] || note "$file is a hard gate but does not register check_gate_signoff.py"
    grep -qE "check_gate_signoff\.py[[:space:]]+$token([[:space:]]|\"|'|$)" <<<"$frontmatter" ||
      note "$file registers the hook without its own phase argument '$token'"
    grep -q '^hooks:' <<<"$frontmatter" ||
      note "$file names the hook outside a hooks: block — prose is not a registration"
  else
    [ "$registered" = no ] ||
      note "$file is a soft gate but registers check_gate_signoff.py"
  fi
done

[ "$fail" -eq 0 ] && echo "AC7 pass: eight phase commands, four gate registrations, each with its phase"
exit "$fail"
