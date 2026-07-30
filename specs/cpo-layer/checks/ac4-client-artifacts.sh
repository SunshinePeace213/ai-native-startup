#!/usr/bin/env bash
# AC4 — client-artifacts.md forks artifacts.md rather than copying it: inherits craft and
# publish by reference, drops the palette lock, names a palette source per phase, and
# carries the four-row page-pattern table. Run from the repo root. Exit 0 = pass.
set -uo pipefail

root=$(git rev-parse --show-toplevel)
cd "$root" || exit 1
file=".claude/rules/studio-layer/client-artifacts.md"
fail=0
note() {
  echo "FAIL: $1"
  fail=1
}

[ -f "$file" ] || {
  echo "FAIL: $file does not exist"
  exit 1
}

grep -q 'clients/\*\*' "$file" || note "$file is not path-scoped to clients/**"
grep -q 'artifacts\.md' "$file" ||
  note "$file does not reference artifacts.md — craft and publish must be inherited, not restated"

# The whole reason to fork is that a client mockup must not wear our pipeline colors.
if grep -qiE '#[0-9a-f]{6}\b' "$file"; then
  note "$file declares a hex color — it must name the palette's SOURCE per phase, not a palette"
fi

# The palette source changes at the P4 direction pick.
grep -qE 'P0|P1|P2|P3' "$file" || note "$file names no early-phase palette source (studio default, P0-P3)"
grep -q 'P4' "$file" || note "$file does not name P4 as where the picked direction's tokens take over"

# The four page patterns, one row each.
for row in 'brief review' 'sitemap' 'art direction' 'feedback triage'; do
  grep -qi "$row" "$file" || note "$file page-pattern table is missing the '$row' row"
done

rows=$(awk '/^\|/ && !/^\|[[:space:]]*-/ {n++} END {print n+0}' "$file")
[ "$rows" -ge 5 ] ||
  note "$file has $rows table lines; the page-pattern table needs a header plus four rows"

grep -qi 'copy-as-prompt' "$file" ||
  note "$file does not state what each pattern's copy-as-prompt returns"

# The fork must leave the original alone.
git diff --quiet HEAD -- .claude/rules/harness-layer/artifacts.md 2>/dev/null ||
  note "artifacts.md was modified — this is a fork, not an edit"

[ "$fail" -eq 0 ] && echo "AC4 pass: client-artifacts.md forks craft/publish, unlocks the palette, names four patterns"
exit "$fail"
