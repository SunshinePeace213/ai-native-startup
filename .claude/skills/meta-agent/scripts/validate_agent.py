#!/usr/bin/env python3
"""
Validate the YAML frontmatter of a Claude Code subagent file
(.claude/agents/<name>.md) against the documented field surface.

Usage:
    uv run --with pyyaml python scripts/validate_agent.py <path-to-agent.md>
"""

import re
import sys
from pathlib import Path

import yaml

NAME_RE = re.compile(r"^[a-z][a-z0-9-]*$")
FULL_MODEL_RE = re.compile(r"^claude-[a-z0-9.-]+$")
MCP_RE = re.compile(r"^mcp__(\*|[a-z0-9_-]+(__(\*|[a-z0-9_*-]+))?)$")
AGENT_CALL_RE = re.compile(r"^Agent\(.*\)$")

MODELS = {"sonnet", "opus", "haiku", "fable", "inherit"}
EFFORTS = {"low", "medium", "high", "xhigh", "max"}
PERMISSION_MODES = {"default", "acceptEdits", "auto", "dontAsk", "bypassPermissions", "plan"}
MEMORIES = {"user", "project", "local"}
COLORS = {"red", "blue", "green", "yellow", "purple", "orange", "pink", "cyan"}
BUILTIN_TOOLS = {
    "Read", "Write", "Edit", "Bash", "Grep", "Glob", "WebFetch", "WebSearch",
    "Task", "TodoWrite", "NotebookEdit", "SlashCommand", "Agent",
}
KNOWN_KEYS = {
    "name", "description", "tools", "disallowedTools", "model", "permissionMode",
    "maxTurns", "skills", "mcpServers", "hooks", "memory", "background",
    "effort", "isolation", "color", "initialPrompt", "prompt",
}


def tool_recognized(tok):
    tok = tok.strip()
    if tok in BUILTIN_TOOLS or AGENT_CALL_RE.match(tok) or MCP_RE.match(tok):
        return True
    return False


def as_tool_list(value):
    if isinstance(value, str):
        return [t.strip() for t in value.split(",") if t.strip()]
    if isinstance(value, list):
        return [str(t).strip() for t in value if str(t).strip()]
    return []


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
        fm = yaml.safe_load(m.group(1))
    except yaml.YAMLError as e:
        return [f"FAIL: frontmatter is not valid YAML: {e}"], []

    if not isinstance(fm, dict):
        return ["FAIL: frontmatter must be a YAML mapping/dict"], []

    # name (required)
    name = fm.get("name")
    if not isinstance(name, str) or not name.strip():
        fails.append("FAIL: 'name' is required and must be a non-empty string")
    elif not NAME_RE.match(name.strip()) or name.strip().startswith("-") \
            or name.strip().endswith("-") or "--" in name.strip():
        fails.append(f"FAIL: 'name' must match ^[a-z][a-z0-9-]*$ (lowercase, hyphens; no underscores/uppercase/leading-trailing-double hyphen): {name!r}")

    # description (required)
    desc = fm.get("description")
    if not isinstance(desc, str) or not desc.strip():
        fails.append("FAIL: 'description' is required and must be a non-empty string")

    # model
    if "model" in fm:
        model = str(fm["model"]).strip()
        if model not in MODELS and not FULL_MODEL_RE.match(model):
            fails.append(f"FAIL: 'model' must be one of {sorted(MODELS)} or a full id like claude-opus-4-8: {model!r}")

    # effort
    if "effort" in fm and str(fm["effort"]).strip() not in EFFORTS:
        fails.append(f"FAIL: 'effort' must be one of {sorted(EFFORTS)}: {fm['effort']!r}")

    # permissionMode
    if "permissionMode" in fm and str(fm["permissionMode"]).strip() not in PERMISSION_MODES:
        fails.append(f"FAIL: 'permissionMode' must be one of {sorted(PERMISSION_MODES)}: {fm['permissionMode']!r}")

    # memory
    if "memory" in fm and str(fm["memory"]).strip() not in MEMORIES:
        fails.append(f"FAIL: 'memory' must be one of {sorted(MEMORIES)}: {fm['memory']!r}")

    # color
    if "color" in fm and str(fm["color"]).strip() not in COLORS:
        fails.append(f"FAIL: 'color' must be one of {sorted(COLORS)}: {fm['color']!r}")

    # isolation
    if "isolation" in fm and str(fm["isolation"]).strip() != "worktree":
        fails.append(f"FAIL: 'isolation' must be 'worktree': {fm['isolation']!r}")

    # background
    if "background" in fm and not isinstance(fm["background"], bool):
        fails.append(f"FAIL: 'background' must be a boolean: {fm['background']!r}")

    # maxTurns
    if "maxTurns" in fm:
        mt = fm["maxTurns"]
        if not isinstance(mt, int) or isinstance(mt, bool) or mt <= 0:
            fails.append(f"FAIL: 'maxTurns' must be a positive integer: {mt!r}")

    # tools / disallowedTools (warnings only)
    for field in ("tools", "disallowedTools"):
        if field in fm:
            for tok in as_tool_list(fm[field]):
                if not tool_recognized(tok):
                    warns.append(f"WARN: '{field}' entry not a known tool or MCP pattern: {tok!r}")

    # plugin-ignored fields
    for field in ("hooks", "mcpServers", "permissionMode"):
        if field in fm:
            warns.append(f"WARN: '{field}' is ignored when the agent is loaded from a plugin")

    # unknown top-level keys
    for key in sorted(set(fm.keys()) - KNOWN_KEYS):
        warns.append(f"WARN: unknown top-level frontmatter key (surface may have evolved): {key!r}")

    return fails, warns


def main(argv):
    if len(argv) != 2:
        print("Usage: uv run --with pyyaml python scripts/validate_agent.py <path-to-agent.md>")
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
