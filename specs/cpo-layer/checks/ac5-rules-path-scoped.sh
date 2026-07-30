#!/usr/bin/env bash
# AC5 — every studio rule is path-scoped to clients/**, so none of them load during
# ordinary harness work or count against the always-loaded budget.
# Run from the repo root. Exit 0 = pass.
set -uo pipefail

root=$(git rev-parse --show-toplevel)
cd "$root" || exit 1
dir=".claude/rules/studio-layer"
fail=0
note() {
  echo "FAIL: $1"
  fail=1
}

[ -d "$dir" ] || {
  echo "FAIL: $dir does not exist"
  exit 1
}

for expected in roster.md client-artifacts.md studio-identity.md; do
  [ -f "$dir/$expected" ] || note "$dir/$expected is missing"
done

for file in "$dir"/*.md; do
  [ -f "$file" ] || continue
  head -1 "$file" | grep -q '^---' ||
    note "$file has no frontmatter — an unscoped rule loads at session start"
  frontmatter=$(awk 'NR>1 && /^---[[:space:]]*$/{exit} NR>1{print}' "$file")
  grep -q '^paths:' <<<"$frontmatter" || note "$file declares no paths: — it would load every session"
  grep -q 'clients/\*\*' <<<"$frontmatter" || note "$file is not scoped to clients/**"
done

[ "$fail" -eq 0 ] && echo "AC5 pass: every studio rule is path-scoped to clients/**"
exit "$fail"
