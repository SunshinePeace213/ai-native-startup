#!/usr/bin/env bash
# AC7 — eight phase commands exist, and exactly the four hard gates register the sign-off
# hook under hooks.Stop, each with its own phase argument.
# Run from the repo root. Exit 0 = pass.
set -uo pipefail

root=$(git rev-parse --show-toplevel)
cd "$root" || exit 1
dir=".claude/commands/studio-layer"

[ -d "$dir" ] || {
  echo "FAIL: $dir does not exist"
  exit 1
}

# Parsed as YAML, not grepped: a top-level `hooks:` key says nothing about the event, so a
# PreToolUse registration would sail past a substring check.
uv run --with pyyaml python - "$dir" <<'PY'
import sys
from pathlib import Path

import yaml

directory = Path(sys.argv[1])
PHASES = [
    "p0-intake", "p1-discovery", "p2-definition", "p3-structure",
    "p4-art-direction", "p5-prototype", "p6-handoff", "p7-retro",
]
GATED = {"p2", "p3", "p4", "p6"}
HOOK = "check_gate_signoff.py"

failures = []


def note(message):
    failures.append(message)


def frontmatter(path):
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    return yaml.safe_load(text[4:end]) or {}


found = sorted(p.stem for p in directory.glob("*.md"))
if found != sorted(PHASES):
    note(f"phase files are {found}, expected {sorted(PHASES)}")

for stem in PHASES:
    path = directory / f"{stem}.md"
    if not path.is_file():
        note(f"{path} is missing")
        continue

    token = stem.split("-", 1)[0]
    meta = frontmatter(path)

    # Every registration under hooks.Stop that runs our hook, with its full command line.
    stop_blocks = (meta.get("hooks") or {}).get("Stop") or []
    commands = [
        hook.get("command", "")
        for block in stop_blocks
        for hook in (block.get("hooks") or [])
        if hook.get("type") == "command" and HOOK in hook.get("command", "")
    ]

    # A registration on any other event is a miswiring that a substring check would miss.
    for event, blocks in (meta.get("hooks") or {}).items():
        if event == "Stop":
            continue
        for block in blocks or []:
            for hook in block.get("hooks") or []:
                if HOOK in hook.get("command", ""):
                    note(f"{path} registers {HOOK} on {event}, not Stop")

    if token in GATED:
        if not commands:
            note(f"{path} is a hard gate but registers no {HOOK} under hooks.Stop")
            continue
        if len(commands) > 1:
            note(f"{path} registers {HOOK} {len(commands)} times under Stop")
        for command in commands:
            argv = command.split()
            if HOOK not in " ".join(argv):
                continue
            index = next(i for i, part in enumerate(argv) if part.endswith(HOOK))
            trailing = argv[index + 1:]
            if trailing != [token]:
                note(f"{path} passes {trailing or 'no argument'} to {HOOK}, expected ['{token}']")
    elif commands:
        note(f"{path} is a soft gate but registers {HOOK} — the gate would fire on a soft phase")

if failures:
    for message in failures:
        print(f"FAIL: {message}")
    sys.exit(1)

print("AC7 pass: eight phase commands, four Stop registrations, each with its own phase")
PY
