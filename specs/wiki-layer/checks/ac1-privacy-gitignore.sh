#!/usr/bin/env bash
# AC1 — wiki tracked, personal domain and Obsidian workspace ignored.
# Uses git pattern semantics (git check-ignore), so it works before pages exist.
set -uo pipefail

fail() { echo "FAIL: $1"; exit 1; }

# Personal domain must be ignored (never reaches the remote or cloud clones).
git check-ignore -q "ai-docs/wiki/personal/journal.md" \
  || fail "ai-docs/wiki/personal/** is not gitignored"
git check-ignore -q "ai-docs/wiki/personal/assets/photo.png" \
  || fail "ai-docs/wiki/personal/assets/** is not gitignored"

# Wiki core and shared domains must be tracked (NOT ignored).
git check-ignore -q "ai-docs/wiki/index.md" \
  && fail "ai-docs/wiki/index.md is gitignored — wiki layer is untracked"
git check-ignore -q "ai-docs/wiki/log.md" \
  && fail "ai-docs/wiki/log.md is gitignored"
git check-ignore -q "ai-docs/wiki/engineering/example-topic.md" \
  && fail "shared-domain pages under ai-docs/wiki/ are gitignored"
git check-ignore -q "ai-docs/wiki/assets/diagram.png" \
  && fail "ai-docs/wiki/assets/** is gitignored"

# Obsidian: config tracked, volatile workspace state ignored.
git check-ignore -q "ai-docs/.obsidian/app.json" \
  && fail "ai-docs/.obsidian/app.json is gitignored — vault config is untracked"
git check-ignore -q "ai-docs/.obsidian/workspace.json" \
  || fail "ai-docs/.obsidian/workspace.json is not ignored"

# Mirrors must stay device-local (regression guard on the existing rule).
git check-ignore -q "ai-docs/anthropic/skills.md" \
  || fail "mirror files are no longer gitignored — ai-docs/* rule was broken"
git check-ignore -q "ai-docs/index.md" \
  || fail "generated ai-docs/index.md is no longer gitignored"

echo "PASS: gitignore semantics correct for wiki layer"
