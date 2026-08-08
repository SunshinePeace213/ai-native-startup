#!/usr/bin/env bash
# Build this repo's qmd search index. Idempotent — safe to re-run.
#
#   bash .claude/scripts/qmd-setup.sh
#
# Requires the qmd CLI: bun install -g @tobilu/qmd
#
# Two disjoint collections over the ai-docs vault. The masks must stay disjoint:
# `sources` excludes wiki/ so a page is never indexed twice, and so a search can
# be scoped to one layer with -c.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
VAULT="$REPO_ROOT/ai-docs"

command -v qmd >/dev/null 2>&1 || {
  echo "qmd not found. Install it with: bun install -g @tobilu/qmd" >&2
  exit 1
}
[ -d "$VAULT" ] || { echo "No ai-docs/ vault at $VAULT" >&2; exit 1; }

# Re-adding is how this stays idempotent. Embeddings are keyed by content hash,
# so dropping and re-adding a collection does not re-embed unchanged text.
for name in wiki sources; do
  qmd collection remove "$name" >/dev/null 2>&1 || true
done

qmd collection add "$VAULT/wiki" --name wiki    --mask "**/*.md"
qmd collection add "$VAULT"      --name sources --mask "!(wiki)/**/*.md"

qmd context add qmd://wiki "Compiled synthesis layer: LLM-maintained wiki pages over the raw-source archives. Pages carry type/domain/status frontmatter, [[wikilinks]], and cite raw archives in sources:. This is the answer layer."
qmd context add qmd://sources "Immutable raw-source archives: faithful markdown captures of web pages and PDFs, grouped by site or topic. Cited by wiki pages, never edited by hand. This is the evidence layer."

qmd update
qmd embed

qmd status
