#!/usr/bin/env bash
# AC3 — nine role agents under .claude/agents/studio-layer/, each function-named, each
# naming its person in the body, none preloading skills, all valid.
# Run from the repo root. Exit 0 = pass.
set -uo pipefail

root=$(git rev-parse --show-toplevel)
cd "$root" || exit 1
dir=".claude/agents/studio-layer"
fail=0
note() {
  echo "FAIL: $1"
  fail=1
}

[ -d "$dir" ] || {
  echo "FAIL: $dir does not exist"
  exit 1
}

mapfile -t files < <(find "$dir" -name '*.md' | sort)
[ "${#files[@]}" -eq 9 ] || note "expected 9 role agents, found ${#files[@]}"

# The roster person each function must name in its body. The principal is deliberately
# absent: Maya Lindqvist is the main session and gets no agent file.
declare -A people=(
  [studio-client-partner]="Daniel Osei"
  [studio-discovery-lead]="Priya Raghavan"
  [studio-ux-architect]="Tomas Vieira"
  [studio-art-director]="Elena Ferraro"
  [studio-content-strategist]="Hana Okabe"
  [studio-prototype-engineer]="Marcus Bramley"
  [studio-design-qa]="Yusuf Demir"
  [studio-research-analyst]="Clara Nyberg"
  [studio-retro-scribe]="Ravi Chandran"
)

[ -f "$dir/studio-principal.md" ] &&
  note "the principal must not have an agent file — Maya Lindqvist is the main session"

for function in "${!people[@]}"; do
  file="$dir/$function.md"
  [ -f "$file" ] || {
    note "$file is missing"
    continue
  }

  frontmatter=$(awk 'NR>1 && /^---[[:space:]]*$/{exit} NR>1{print}' "$file")
  body=$(awk 'f{print} !f && NR>1 && /^---[[:space:]]*$/{f=1}' "$file")

  name=$(grep -m1 '^name:' <<<"$frontmatter" | sed 's/^name:[[:space:]]*//; s/["'\'']//g' | xargs)
  [ "$name" = "$function" ] ||
    note "$file declares name '$name' but its filename stem is '$function' — they must match"
  grep -qE '^studio-[a-z-]+$' <<<"$name" ||
    note "$file name '$name' is not a plain layer-prefixed function name"

  # The persona belongs in the body, never in the routing document.
  grep -qi "${people[$function]}" <<<"$name" &&
    note "$file puts the person in name: — routing must not carry the persona"
  grep -q "${people[$function]}" <<<"$body" ||
    note "$file body does not name its person, ${people[$function]}"

  grep -q '^skills:' <<<"$frontmatter" &&
    note "$file sets skills: — preloading is not access; roles invoke the bank via the Skill tool"

  # Subagents inherit the Agent tool by default, so without an explicit denial "one level
  # deep" is a sentence rather than a property. Parsed as YAML because `tools:` may be a
  # multiline list, which a line-anchored grep would walk straight past.
  uv run --with pyyaml python - "$file" <<'PY' || fail=1
import sys
from pathlib import Path

import yaml

path = Path(sys.argv[1])
text = path.read_text(encoding="utf-8")
end = text.find("\n---", 3)
meta = yaml.safe_load(text[4:end]) if text.startswith("---\n") and end != -1 else {}
meta = meta or {}


def names(value):
    if value is None:
        return []
    if isinstance(value, str):
        return [part.strip() for part in value.split(",") if part.strip()]
    return [str(part).strip() for part in value]


allowed = names(meta.get("tools"))
denied = names(meta.get("disallowedTools"))
granted = [t for t in allowed if t == "Agent" or t.startswith("Agent(")]

if granted:
    print(f"FAIL: {path} grants {granted} — roles must not spawn subagents")
    sys.exit(1)
if not allowed and "Agent" not in denied:
    print(f"FAIL: {path} does not restrict tools: and does not deny Agent — it can nest")
    sys.exit(1)
PY

  uv run --with pyyaml python .claude/skills/meta-agent/scripts/validate_agent.py "$file" \
    >/dev/null 2>&1 || note "$file does not pass the meta-agent validator"
done

[ "$fail" -eq 0 ] && echo "AC3 pass: nine role agents, function-named, person in the body"
exit "$fail"
