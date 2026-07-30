#!/usr/bin/env bash
# AC5 — every studio rule is path-scoped to clients/**, studio-identity.md actually carries
# the four things it exists to supply, and AGENTS.md points at the studio rules while the
# always-loaded budget still holds. Run from the repo root. Exit 0 = pass.
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

# Rules are discovered recursively, so a nested unscoped rule would load every session.
# Scanning only the top level would miss it.
mapfile -t rules < <(find "$dir" -type f -name '*.md' | sort)
[ "${#rules[@]}" -ge 3 ] || note "expected at least 3 studio rules, found ${#rules[@]}"

for file in "${rules[@]}"; do
  head -1 "$file" | grep -q '^---' || {
    note "$file has no frontmatter — an unscoped rule loads at session start"
    continue
  }
  frontmatter=$(awk 'NR>1 && /^---[[:space:]]*$/{exit} NR>1{print}' "$file")
  grep -q '^paths:' <<<"$frontmatter" || note "$file declares no paths: — it would load every session"
  grep -q 'clients/\*\*' <<<"$frontmatter" || note "$file is not scoped to clients/**"
done

# The identity rule is the one file whose content is load-bearing for every client-facing
# document; valid frontmatter over empty prose would pass a scope-only check.
identity="$dir/studio-identity.md"
if [ -f "$identity" ]; then
  grep -qi 'soriza' "$identity" || note "$identity does not name the studio"
  grep -qi 'voice\|tone' "$identity" || note "$identity defines no client-facing voice"
  grep -qi 'letterhead' "$identity" || note "$identity defines no document letterhead"
  grep -qi 'sign-off\|signature' "$identity" || note "$identity carries no sign-off block"
  body=$(awk 'f{print} !f && NR>1 && /^---[[:space:]]*$/{f=1}' "$identity" | tr -d '[:space:]')
  [ "${#body}" -ge 400 ] ||
    note "$identity body is ${#body} chars — too thin to supply a letterhead and sign-off block"
fi

# The hub must point at the new rules (memory-series.md). The real invariant for this build
# is that it adds NO unscoped rule — all three studio rules are path-scoped — so the
# always-loaded set gains only AGENTS.md's pointer section.
grep -q 'studio-layer' AGENTS.md || note "AGENTS.md has no pointer to the studio-layer rules"

# Unscoped = a .md directly at the rules root (no paths: frontmatter, loads every session).
mapfile -t unscoped < <(find .claude/rules -maxdepth 1 -type f -name '*.md' | sort)
for file in "${unscoped[@]}"; do
  case "$(basename "$file")" in
    git-workflow.md | memory-series.md | model-selection.md | orchestration.md) ;;
    *) note "$file is a new unscoped rule — every studio rule must be path-scoped to clients/**" ;;
  esac
done

# memory-series.md caps the unscoped rules at ~250 lines; they stand at 254 today, so this
# build must not add to them. The bar allows the existing set plus a small edit, nothing more.
rules_lines=$(cat "${unscoped[@]}" 2>/dev/null | wc -l)
[ "$rules_lines" -le 280 ] ||
  note "unscoped rules are $rules_lines lines — over the memory-series.md budget"

[ "$fail" -eq 0 ] && echo "AC5 pass: studio rules are scoped, identity is real, and the hub points at them"
exit "$fail"
