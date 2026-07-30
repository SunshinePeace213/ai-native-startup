#!/usr/bin/env bash
# AC4 — client-artifacts.md forks artifacts.md rather than copying it: inherits craft and
# publish by reference, drops the palette lock, names a palette source per phase band, and
# carries a four-row page-pattern table where every row states its copy-as-prompt return.
# Run from the repo root. Exit 0 = pass.
set -uo pipefail

root=$(git rev-parse --show-toplevel)
cd "$root" || exit 1
file=".claude/rules/studio-layer/client-artifacts.md"

[ -f "$file" ] || {
  echo "FAIL: $file does not exist"
  exit 1
}

# The "original untouched" guardrail. A missing comparison base must fail, not silently skip
# the only assertion that proves this is a fork rather than an edit.
base=""
for candidate in origin/main main; do
  if git rev-parse --verify --quiet "$candidate" >/dev/null; then
    base=$candidate
    break
  fi
done
if [ -z "$base" ]; then
  echo "FAIL: neither origin/main nor main resolves — cannot prove artifacts.md is untouched"
  exit 1
fi
if ! git diff --quiet "$base" -- .claude/rules/harness-layer/artifacts.md; then
  echo "FAIL: artifacts.md differs from $base — this is a fork, not an edit"
  exit 1
fi

# The table is parsed structurally: row labels must be table cells, not prose anywhere in
# the file, and there must be exactly four of them.
uv run --with pyyaml python - "$file" <<'PY'
import re
import sys
from pathlib import Path

import yaml

path = Path(sys.argv[1])
text = path.read_text(encoding="utf-8")
failures = []


def note(message):
    failures.append(message)


if not text.startswith("---\n"):
    note("no frontmatter — the rule would load every session")
    meta = {}
else:
    end = text.find("\n---", 3)
    meta = yaml.safe_load(text[4:end]) or {}

paths = meta.get("paths") or []
if not any("clients/**" in str(p) for p in paths):
    note("not path-scoped to clients/**")

if "artifacts.md" not in text:
    note("does not reference artifacts.md — craft and publish must be inherited, not restated")

# Forking exists so a client mockup does not wear our pipeline colors.
hexes = re.findall(r"#[0-9A-Fa-f]{6}\b", text)
if hexes:
    note(f"declares hex colors {sorted(set(hexes))} — name the palette SOURCE per phase instead")

# Both palette bands must be named: the studio default early, the picked direction from P4.
early = re.search(r"P0\s*[-–—]\s*P3|P0.{0,12}P3", text)
if not early:
    note("names no early-phase palette source (the studio default across P0-P3)")
if not re.search(r"P4", text):
    note("does not name P4 as where the picked direction's tokens take over")

# Parse markdown tables into row-lists, then find the page-pattern table by its labels.
tables, current = [], []
for line in text.splitlines():
    if line.lstrip().startswith("|"):
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if cells and set("".join(cells)) <= {"-", ":", " "}:
            continue
        current.append(cells)
    elif current:
        tables.append(current)
        current = []
if current:
    tables.append(current)

WANTED = ["brief review", "sitemap", "art direction", "feedback triage"]


def label_of(row):
    return re.sub(r"[`*]", "", row[0]).strip().lower() if row else ""


pattern_tables = [
    t for t in tables if sum(any(w in label_of(r) for w in WANTED) for r in t) >= 2
]

if not pattern_tables:
    note("no page-pattern table found whose first column carries the four pattern labels")
else:
    table = max(pattern_tables, key=len)
    body = [r for r in table[1:] if any(c for c in r)]
    if len(body) != 4:
        note(f"page-pattern table has {len(body)} rows, expected exactly 4: {[label_of(r) for r in body]}")
    # Matched as an exact multiset, one row per label. Substring matching would let one row
    # carry two required labels while an unrelated fourth row rode along.
    labels = [label_of(r) for r in body]
    matched = []
    for label in labels:
        hits = [w for w in WANTED if w in label]
        matched.append(hits[0] if len(hits) == 1 else None)
        if len(hits) > 1:
            note(f"row '{label}' carries more than one required label {hits} — one row each")
    if sorted(m for m in matched if m) != sorted(WANTED):
        note(f"page-pattern rows {labels} do not map one-to-one onto {WANTED}")
    # The return contract is a COLUMN: the header declares it and every row fills it. One
    # generic mention in the surrounding prose is what this rejects.
    header = [re.sub(r"[`*]", "", c).strip().lower() for c in table[0]]
    return_col = next(
        (i for i, c in enumerate(header) if "copy-as-prompt" in c or "return" in c),
        None,
    )
    if return_col is None:
        note(f"page-pattern table has no copy-as-prompt return column (header: {header})")
    else:
        for row in body:
            cell = row[return_col].strip() if return_col < len(row) else ""
            if not cell:
                note(f"row '{label_of(row)}' does not state what its copy-as-prompt returns")

if failures:
    for message in failures:
        print(f"FAIL: {message}")
    sys.exit(1)

print("AC4 pass: forks craft/publish, unlocks the palette, four patterns each with a return")
PY
