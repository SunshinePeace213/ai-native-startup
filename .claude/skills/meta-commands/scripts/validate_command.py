#!/usr/bin/env python3
"""
Validate the YAML frontmatter of EITHER a flat Claude Code slash command
(.claude/commands/<name>.md) OR a skill-as-command (.../SKILL.md) against the
documented command/skill field surface and char caps.

Usage:
    uv run --with pyyaml python scripts/validate_command.py <path-to-command-or-SKILL.md>
"""

import re
import sys
from pathlib import Path

import yaml

NAME_RE = re.compile(r"^[a-z][a-z0-9-]*$")
FULL_MODEL_RE = re.compile(r"^claude-[a-z0-9.-]+$")

MODELS = {"sonnet", "opus", "haiku", "fable", "inherit"}
EFFORTS = {"low", "medium", "high", "xhigh", "max"}
CONTEXTS = {"fork"}

DESC_MAX = 1024
DESC_PLUS_WTU_MAX = 1536

# Documented command/skill frontmatter keys (HYPHENATED, not camelCase).
KNOWN_KEYS = {
    "name", "description", "when_to_use", "argument-hint", "arguments",
    "allowed-tools", "disallowed-tools", "disable-model-invocation",
    "user-invocable", "model", "effort", "context", "agent", "shell",
    "hooks", "paths",
}

BOOL_KEYS = ("disable-model-invocation", "user-invocable", "shell")

# 'argument-hint' is a display-only field conventionally written with bracketed
# placeholders (e.g. `argument-hint: [user prompt] [orchestration prompt]`).
# That is not valid YAML flow syntax, but Claude Code tolerates it. Quote the
# value before parsing so the hint convention doesn't break the whole document.
ARG_HINT_RE = re.compile(r"^(\s*argument-hint:\s*)(\[.*)$")


def _normalize_arg_hint(fm_text):
    out = []
    for line in fm_text.splitlines():
        m = ARG_HINT_RE.match(line)
        if m:
            val = m.group(2).rstrip()
            if '"' not in val:
                line = f'{m.group(1)}"{val}"'
        out.append(line)
    return "\n".join(out)


def validate(path):
    fails, warns = [], []
    p = Path(path)

    try:
        content = p.read_text()
    except OSError as e:
        return [f"FAIL: cannot read file: {e}"], []

    if not content.startswith("---"):
        fails.append("FAIL: no YAML frontmatter at start of file (must begin with '---'; not fenced in a code block)")
        return fails, warns

    m = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not m:
        fails.append("FAIL: malformed frontmatter (no closing '---' delimiter)")
        return fails, warns

    try:
        fm = yaml.safe_load(_normalize_arg_hint(m.group(1)))
    except yaml.YAMLError as e:
        return [f"FAIL: frontmatter is not valid YAML: {e}"], []

    if not isinstance(fm, dict):
        return ["FAIL: frontmatter must be a YAML mapping/dict"], []

    # name (OPTIONAL for commands — flat commands derive it from the filename)
    if "name" in fm:
        name = fm.get("name")
        if not isinstance(name, str) or not name.strip():
            fails.append("FAIL: 'name' is present but must be a non-empty string")
        else:
            n = name.strip()
            if not NAME_RE.match(n) or n.startswith("-") or n.endswith("-") or "--" in n:
                fails.append(f"FAIL: 'name' must match ^[a-z][a-z0-9-]*$ (lowercase, hyphens; no underscores/uppercase/leading-trailing-double hyphen): {name!r}")

    # description (OPTIONAL for flat commands — WARN if absent)
    desc = fm.get("description")
    wtu = fm.get("when_to_use")
    if "description" not in fm:
        warns.append("WARN: no 'description' field (flat commands may omit it, but a description aids model invocation)")
    elif not isinstance(desc, str) or not desc.strip():
        fails.append("FAIL: 'description' is present but must be a non-empty string")
    else:
        if "<" in desc or ">" in desc:
            fails.append("FAIL: 'description' must not contain angle brackets ('<' or '>')")
        if len(desc) > DESC_MAX:
            fails.append(f"FAIL: 'description' is too long ({len(desc)} chars; max {DESC_MAX})")
        if isinstance(wtu, str) and len(desc) + len(wtu) > DESC_PLUS_WTU_MAX:
            fails.append(f"FAIL: 'description' + 'when_to_use' too long ({len(desc) + len(wtu)} chars; max {DESC_PLUS_WTU_MAX})")

    # model
    if "model" in fm:
        model = str(fm["model"]).strip()
        if model not in MODELS and not FULL_MODEL_RE.match(model):
            fails.append(f"FAIL: 'model' must be one of {sorted(MODELS)} or a full id like claude-opus-4-8: {model!r}")

    # effort
    if "effort" in fm and str(fm["effort"]).strip() not in EFFORTS:
        fails.append(f"FAIL: 'effort' must be one of {sorted(EFFORTS)}: {fm['effort']!r}")

    # boolean-typed fields
    for field in BOOL_KEYS:
        if field in fm and not isinstance(fm[field], bool):
            fails.append(f"FAIL: '{field}' must be a boolean: {fm[field]!r}")

    # context (WARN — surface may grow)
    if "context" in fm and str(fm["context"]).strip() not in CONTEXTS:
        warns.append(f"WARN: 'context' is usually one of {sorted(CONTEXTS)}: {fm['context']!r}")

    # unknown top-level keys
    for key in sorted(set(fm.keys()) - KNOWN_KEYS):
        warns.append(f"WARN: unknown top-level frontmatter key (surface may have evolved): {key!r}")

    return fails, warns


def main(argv):
    if len(argv) != 2:
        print("Usage: uv run --with pyyaml python scripts/validate_command.py <path-to-command-or-SKILL.md>")
        return 1

    fails, warns = validate(argv[1])
    for w in warns:
        print(w)
    for f in fails:
        print(f)

    if fails:
        print(f"{len(fails)} failure(s) found in {argv[1]}")
        return 1
    print(f"PASS: {argv[1]}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
