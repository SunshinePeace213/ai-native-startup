#!/usr/bin/env python3
"""
Validate a Claude Code subagent file (.claude/agents/<name>.md): its YAML
frontmatter against the documented field surface, and its body against the
Claude 5 authoring contract.

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
PERMISSION_MODES = {
    "default",
    "acceptEdits",
    "auto",
    "dontAsk",
    "bypassPermissions",
    "plan",
    "manual",
}
MEMORIES = {"user", "project", "local"}
COLORS = {"red", "blue", "green", "yellow", "purple", "orange", "pink", "cyan"}
# Mirrors the tool table in ai-docs/anthropic/tools-reference.md. `Task` is kept
# as the documented legacy alias for `Agent`.
BUILTIN_TOOLS = {
    "Read",
    "Write",
    "Edit",
    "Bash",
    "Grep",
    "Glob",
    "WebFetch",
    "WebSearch",
    "Task",
    "TodoWrite",
    "NotebookEdit",
    "Agent",
    "Skill",
    "LSP",
    "PowerShell",
    "ListMcpResourcesTool",
    "ReadMcpResourceTool",
    "ShareOnboardingGuide",
    "SendMessage",
    "SendUserFile",
    "Artifact",
    "Workflow",
    "Monitor",
    "TaskCreate",
    "TaskGet",
    "TaskList",
    "TaskUpdate",
    "TaskStop",
    "TaskOutput",
    "ReportFindings",
    "ToolSearch",
    "CronCreate",
    "CronList",
    "CronDelete",
    "EnterWorktree",
    "ExitWorktree",
    "PushNotification",
    "RemoteTrigger",
}
# Never available to a subagent, whatever `tools` says. ExitPlanMode is the one
# exception: it works when permissionMode is `plan`.
UNAVAILABLE_TOOLS = {
    "AskUserQuestion",
    "EnterPlanMode",
    "ScheduleWakeup",
    "WaitForMcpServers",
    "EndConversation",
}
KNOWN_KEYS = {
    "name",
    "description",
    "tools",
    "disallowedTools",
    "model",
    "permissionMode",
    "maxTurns",
    "skills",
    "mcpServers",
    "hooks",
    "memory",
    "background",
    "effort",
    "isolation",
    "color",
    "initialPrompt",
    "prompt",
}

# Asking the model to surface its OWN reasoning can trigger the
# reasoning_extraction refusal on Fable 5 and silently fall back to Opus 4.8.
BODY_FAIL_PATTERNS = [
    (
        r"\b(explain|show|describe|share|echo|transcribe|reproduce|output)\s+your\s+"
        r"(own\s+)?(reasoning|thinking|thought process|chain of thought)\b",
        "instructs the model to surface its own reasoning (reasoning_extraction "
        "refusal hazard on fable; see references/model-tuning.md)",
    ),
    (
        r"\bwalk\s+(me|us|the user)\s+through\s+your\s+(reasoning|thinking)\b",
        "instructs the model to surface its own reasoning (reasoning_extraction "
        "refusal hazard on fable; see references/model-tuning.md)",
    ),
]

BODY_WARN_PATTERNS = [
    (r"\bdouble[-\s]?check\b", "Claude 5 self-verifies; cut it or use a Stop hook"),
    (r"\bre-?verif(y|ies|ying)\b", "Claude 5 self-verifies; cut it or use a Stop hook"),
    (r"\bverify\s+your\s+(own\s+)?work\b", "Claude 5 self-verifies; cut it or use a Stop hook"),
    (r"\bcheck\s+your\s+(own\s+)?work\b", "Claude 5 self-verifies; cut it or use a Stop hook"),
    (
        r"\bshow\s+your\s+work\b",
        "reads as a reasoning-echo instruction; state the Output shape instead",
    ),
    (r"\bthink\s+(harder|deeply|carefully|step[-\s]by[-\s]step)\b", "depth is `effort`, not prose"),
    (r"\bbe\s+thorough\b", "depth is `effort`, not prose"),
    (r"\btake\s+your\s+time\b", "depth is `effort`, not prose"),
    (r"\bevery\s+\d+\s+tool\s+calls?\b", "forced progress cadence; the model paces itself"),
    (
        r"\b(only\s+report|report\s+only)\s+(high|critical|major|important)",
        "pre-filtering a finder suppresses real findings; ask for coverage and filter later",
    ),
    (
        r"\bbe\s+conservative\b",
        "pre-filtering a finder suppresses real findings; ask for coverage and filter later",
    ),
    (
        r"\bdon'?t\s+nitpick\b",
        "pre-filtering a finder suppresses real findings; ask for coverage and filter later",
    ),
    (r"\b\d+\+?\s*years\b", "persona bloat; one sentence on the relevant lens is enough"),
]


def tool_recognized(tok):
    tok = tok.strip()
    return bool(
        tok in BUILTIN_TOOLS
        or tok in UNAVAILABLE_TOOLS
        or tok == "ExitPlanMode"
        or AGENT_CALL_RE.match(tok)
        or MCP_RE.match(tok)
    )


def as_tool_list(value):
    if isinstance(value, str):
        return [t.strip() for t in value.split(",") if t.strip()]
    if isinstance(value, list):
        return [str(t).strip() for t in value if str(t).strip()]
    return []


def check_frontmatter(fm, fails, warns):
    name = fm.get("name")
    if not isinstance(name, str) or not name.strip():
        fails.append("FAIL: 'name' is required and must be a non-empty string")
    elif not NAME_RE.match(name.strip()) or name.strip().endswith("-") or "--" in name.strip():
        fails.append(
            "FAIL: 'name' must match ^[a-z][a-z0-9-]*$ (lowercase, hyphens; no "
            f"underscores/uppercase/trailing-double hyphen): {name!r}"
        )

    desc = fm.get("description")
    if not isinstance(desc, str) or not desc.strip():
        fails.append("FAIL: 'description' is required and must be a non-empty string")

    if "model" in fm:
        model = str(fm["model"]).strip()
        if model not in MODELS and not FULL_MODEL_RE.match(model):
            fails.append(
                f"FAIL: 'model' must be one of {sorted(MODELS)} or a full id "
                f"like claude-opus-4-8: {model!r}"
            )
        elif FULL_MODEL_RE.match(model):
            warns.append(f"WARN: 'model' pins a dated id; prefer an alias: {model!r}")
    else:
        warns.append("WARN: no 'model' stamped — set it from .claude/rules/model-selection.md")

    if "effort" in fm:
        if str(fm["effort"]).strip() not in EFFORTS:
            fails.append(f"FAIL: 'effort' must be one of {sorted(EFFORTS)}: {fm['effort']!r}")
    else:
        warns.append("WARN: no 'effort' stamped — set it from .claude/rules/model-selection.md")

    if "permissionMode" in fm and str(fm["permissionMode"]).strip() not in PERMISSION_MODES:
        fails.append(
            f"FAIL: 'permissionMode' must be one of {sorted(PERMISSION_MODES)}: "
            f"{fm['permissionMode']!r}"
        )

    if "memory" in fm and str(fm["memory"]).strip() not in MEMORIES:
        fails.append(f"FAIL: 'memory' must be one of {sorted(MEMORIES)}: {fm['memory']!r}")

    if "color" in fm and str(fm["color"]).strip() not in COLORS:
        fails.append(f"FAIL: 'color' must be one of {sorted(COLORS)}: {fm['color']!r}")

    if "isolation" in fm and str(fm["isolation"]).strip() != "worktree":
        fails.append(f"FAIL: 'isolation' must be 'worktree': {fm['isolation']!r}")

    if "background" in fm and not isinstance(fm["background"], bool):
        fails.append(f"FAIL: 'background' must be a boolean: {fm['background']!r}")

    if "maxTurns" in fm:
        mt = fm["maxTurns"]
        if not isinstance(mt, int) or isinstance(mt, bool) or mt <= 0:
            fails.append(f"FAIL: 'maxTurns' must be a positive integer: {mt!r}")

    if "prompt" in fm:
        warns.append(
            "WARN: 'prompt' is for JSON/SDK definitions only; in a file-based "
            "agent the body is the prompt"
        )

    plan_mode = str(fm.get("permissionMode", "")).strip() == "plan"
    for field in ("tools", "disallowedTools"):
        if field not in fm:
            continue
        entries = as_tool_list(fm[field])
        for tok in entries:
            if not tool_recognized(tok):
                warns.append(f"WARN: '{field}' entry not a known tool or MCP pattern: {tok!r}")
        if field != "tools":
            continue
        for tok in entries:
            if tok in UNAVAILABLE_TOOLS:
                fails.append(f"FAIL: 'tools' lists {tok!r}, which never works in a subagent")
            elif tok == "ExitPlanMode" and not plan_mode:
                fails.append(
                    "FAIL: 'tools' lists 'ExitPlanMode', which works only with permissionMode: plan"
                )
        if entries and not any(tool_recognized(t) for t in entries):
            fails.append(
                "FAIL: no entry in 'tools' resolves to a tool — the subagent will refuse to launch"
            )

    for field in ("hooks", "mcpServers", "permissionMode"):
        if field in fm:
            warns.append(f"WARN: '{field}' is ignored when the agent is loaded from a plugin")

    for key in sorted(set(fm.keys()) - KNOWN_KEYS):
        warns.append(f"WARN: unknown top-level frontmatter key (surface may have evolved): {key!r}")


def check_body(body, fails, warns):
    if not body.strip():
        fails.append("FAIL: body is empty — it is the agent's system prompt")
        return

    for pattern, reason in BODY_FAIL_PATTERNS:
        m = re.search(pattern, body, re.IGNORECASE)
        if m:
            fails.append(f"FAIL: body {reason}: {m.group(0)!r}")

    for pattern, reason in BODY_WARN_PATTERNS:
        m = re.search(pattern, body, re.IGNORECASE)
        if m:
            warns.append(f"WARN: body {reason}: {m.group(0)!r}")

    if not re.search(r"^#+\s*Output\b", body, re.IGNORECASE | re.MULTILINE):
        warns.append(
            "WARN: body has no 'Output' section — the return contract is what the caller depends on"
        )


def validate(path):
    fails, warns = [], []
    p = Path(path)

    try:
        content = p.read_text()
    except OSError as e:
        return [f"FAIL: cannot read file: {e}"], []

    if not content.startswith("---"):
        return [
            "FAIL: no YAML frontmatter at start of file (must begin with '---'; "
            "not fenced in a code block)"
        ], []

    m = re.match(r"^---\n(.*?)\n---\n?(.*)$", content, re.DOTALL)
    if not m:
        return ["FAIL: malformed frontmatter (no closing '---' delimiter)"], []

    try:
        fm = yaml.safe_load(m.group(1))
    except yaml.YAMLError as e:
        return [f"FAIL: frontmatter is not valid YAML: {e}"], []

    if not isinstance(fm, dict):
        return ["FAIL: frontmatter must be a YAML mapping/dict"], []

    check_frontmatter(fm, fails, warns)
    check_body(m.group(2), fails, warns)
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
