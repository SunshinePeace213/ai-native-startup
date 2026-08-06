#!/usr/bin/env bash
# AC1 — wiki tracked, personal domain and Obsidian workspace ignored.
# Pattern semantics via git check-ignore (works before pages exist) plus a
# git ls-files proof that the personal namespace contains zero tracked files.
set -uo pipefail

fail() { echo "FAIL: $1"; exit 1; }

# Personal domain must be ignored (never reaches the remote or cloud clones) —
# including its own index, log, and assets.
for p in \
  "ai-docs/wiki/personal/journal.md" \
  "ai-docs/wiki/personal/index.md" \
  "ai-docs/wiki/personal/log.md" \
  "ai-docs/wiki/personal/assets/photo.png"; do
  git check-ignore -q "$p" || fail "$p is not gitignored"
done

# The personal namespace must contain zero tracked files — the hard proof.
if [ -n "$(git ls-files -- ai-docs/wiki/personal/)" ]; then
  fail "tracked files exist under ai-docs/wiki/personal/ — privacy boundary broken"
fi

# Wiki core and every shared domain must be tracked (NOT ignored).
for p in \
  "ai-docs/wiki/index.md" \
  "ai-docs/wiki/log.md" \
  "ai-docs/wiki/assets/diagram.png" \
  "ai-docs/wiki/engineering/example-topic.md" \
  "ai-docs/wiki/business/example-topic.md" \
  "ai-docs/wiki/development/example-topic.md" \
  "ai-docs/wiki/books/example-topic.md" \
  "ai-docs/wiki/articles/example-topic.md"; do
  git check-ignore -q "$p" && fail "$p is gitignored — wiki layer namespace untracked"
done

# Obsidian: config tracked, volatile workspace state ignored (both variants).
git check-ignore -q "ai-docs/.obsidian/app.json" \
  && fail "ai-docs/.obsidian/app.json is gitignored — vault config is untracked"
git check-ignore -q "ai-docs/.obsidian/appearance.json" \
  && fail "ai-docs/.obsidian/appearance.json is gitignored"
git check-ignore -q "ai-docs/.obsidian/workspace.json" \
  || fail "ai-docs/.obsidian/workspace.json is not ignored"
git check-ignore -q "ai-docs/.obsidian/workspace-mobile.json" \
  || fail "ai-docs/.obsidian/workspace-mobile.json is not ignored"

# Mirrors must stay device-local (regression guard on the existing rule).
git check-ignore -q "ai-docs/anthropic/skills.md" \
  || fail "mirror files are no longer gitignored — ai-docs/* rule was broken"
git check-ignore -q "ai-docs/index.md" \
  || fail "generated ai-docs/index.md is no longer gitignored"

echo "PASS: gitignore semantics correct for wiki layer"
