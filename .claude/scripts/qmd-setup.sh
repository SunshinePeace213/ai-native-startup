#!/usr/bin/env bash
# Build this repo's qmd search index. Idempotent — safe to re-run.
#
#   bash .claude/scripts/qmd-setup.sh
#
# Requires the qmd CLI: bun install -g @tobilu/qmd
#
# The index is project-local: config and database live in <root>/.qmd/, not in
# the global ~/.config + ~/.cache. qmd finds it by walking up from the current
# directory, so every command run anywhere inside the repo uses this index —
# and a worktree carrying its own .qmd/ shadows it (see
# .claude/hooks/worktree/worktree_create.py).
#
# Two disjoint collections over the ai-docs vault. The masks must stay disjoint:
# `sources` excludes wiki/ so a page is never indexed twice, and so a search can
# be scoped to one layer with -c.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
VAULT="$REPO_ROOT/ai-docs"
QMD_DIR="$REPO_ROOT/.qmd"

command -v qmd >/dev/null 2>&1 || {
  echo "qmd not found. Install it with: bun install -g @tobilu/qmd" >&2
  exit 1
}
[ -d "$VAULT" ] || { echo "No ai-docs/ vault at $VAULT" >&2; exit 1; }

# Ask qmd itself where the global index lives, before .qmd/ exists to shadow it.
# Parsing beats guessing at XDG paths, and this is qmd's own answer.
global_index=""
global_config=""
if [ ! -d "$QMD_DIR" ]; then
  # Readers consume their input to EOF: closing qmd's pipe early would kill it
  # with SIGPIPE, and `pipefail` would then abort the whole script.
  global_index="$(cd "$REPO_ROOT" && qmd status 2>/dev/null | awk '/^Index:/ && !seen {print $2; seen=1}')" || true
  config_home="${QMD_CONFIG_DIR:-${XDG_CONFIG_HOME:+$XDG_CONFIG_HOME/qmd}}"
  config_home="${config_home:-$HOME/.config/qmd}"
  [ -f "$config_home/index.yml" ] && global_config="$config_home/index.yml"
fi

# Models: an explicit env var wins; otherwise inherit whatever built the global
# index. This ordering is load-bearing — seeding below reuses the global
# vectors, and a vector's dimension is fixed by the model that produced it, so
# silently falling back to qmd's smaller defaults would break the seeded index.
if [ -n "$global_config" ]; then
  for role in embed generate rerank; do
    var="QMD_$(echo "$role" | tr '[:lower:]' '[:upper:]')_MODEL"
    if [ -z "${!var:-}" ]; then
      inherited="$(awk -v role="$role:" '$1 == role && !seen {print $2; seen=1}' "$global_config")"
      [ -n "$inherited" ] && export "$var=$inherited"
    fi
  done
fi

# Seed from the global index so unchanged documents keep their vectors. Paths in
# the main checkout do not move, so this is a straight reuse: `qmd embed` below
# only has to cover documents the global index never saw.
mkdir -p "$QMD_DIR"
if [ -n "$global_index" ] && [ -f "$global_index" ] && [ ! -f "$QMD_DIR/index.sqlite" ]; then
  cp "$global_index" "$QMD_DIR/index.sqlite"
  echo "Seeded $QMD_DIR/index.sqlite from $global_index"
fi

cd "$REPO_ROOT"

# `qmd init` writes .qmd/index.yml using qmd's own serializer, resolving models
# from the environment prepared above. On re-runs it keeps the recorded models.
qmd init

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
