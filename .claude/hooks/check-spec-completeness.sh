#!/usr/bin/env bash
# Stop hook for /harness-layer:harness-plan: block the run from ending until the per-plan spec folder is complete.
# Two checks only: (1) all four files exist, (2) each file has its required '##' sections.
# Exit 2 => deny stop; stderr is fed back to Claude so it completes the gaps.
set -euo pipefail

root="${CLAUDE_PROJECT_DIR:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}"
specs="$root/specs"
[ -d "$specs" ] || exit 0   # no specs dir at all → nothing to gate

# Newest-modified plan folder, excluding the templates dir. (stat -c is GNU/Linux, stat -f the BSD/macOS fallback.)
folder="$(find "$specs" -mindepth 1 -maxdepth 1 -type d ! -name '_templates' \
  -exec sh -c 'for d; do printf "%s %s\n" "$(stat -c %Y "$d" 2>/dev/null || stat -f %m "$d")" "$d"; done' _ {} + \
  | sort -rn | head -1 | cut -d' ' -f2-)"
[ -n "$folder" ] || { echo "Stop blocked: no plan folder found under specs/." >&2; exit 2; }

missing=""
check() {  # $1=file  $2=newline-separated required section headers
  local f="$folder/$1"
  if [ ! -f "$f" ]; then missing+=$'\n'"  - MISSING FILE: $1"; return; fi
  while IFS= read -r h; do
    [ -z "$h" ] && continue
    grep -qF "## $h" "$f" || missing+=$'\n'"  - $1: missing section '## $h'"
  done <<< "$2"
}

check spec.md "Task Description
Objective
Non-Goals
Requirements & Decisions
Tracking
Relevant Files
Edge Cases
Red Flags
Codex Verification
References
Self Validation"

check tasks.md "Team Orchestration
Team Members
Step by Step Tasks"

check acceptance-criteria.md "Acceptance Criteria
Validation Commands"

check decisions.md "Summary
Resolved Decisions
Assumptions
Open Questions / Out of Scope"

if [ -n "$missing" ]; then
  { echo "Stop blocked: spec folder '$folder' is incomplete:"; echo "$missing";
    echo ""; echo "Complete the missing files/sections (compare against specs/_templates/), then stop again."; } >&2
  exit 2
fi
exit 0
