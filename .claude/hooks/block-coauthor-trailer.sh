#!/usr/bin/env bash
# PreToolUse guard: block git/gh commands that carry the Claude Co-Authored-By trailer.
# Exit 2 => deny the tool call; stderr is fed back to Claude so it retries clean.
set -euo pipefail
payload="$(cat)"

# Act only on Bash tool calls that invoke git or gh.
printf '%s' "$payload" | grep -Eq '"tool_name"[[:space:]]*:[[:space:]]*"Bash"' || exit 0
printf '%s' "$payload" | grep -Eq '\b(git|gh)\b' || exit 0

# Block when the forbidden trailer is present.
if printf '%s' "$payload" | grep -q 'Co-Authored-By: Claude'; then
  {
    echo "Blocked: this git/gh command includes a 'Co-Authored-By: Claude ...' trailer."
    echo "Repo policy (GIT-COMMIT-PR-MESSAGE.md): commit/PR messages must NOT carry the Claude attribution trailer."
    echo "Remove the 'Co-Authored-By: Claude ...' line from the message and run the command again."
  } >&2
  exit 2
fi
exit 0
