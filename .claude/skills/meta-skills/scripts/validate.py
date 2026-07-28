#!/usr/bin/env python3
"""
Validate a Claude Code slash command (.claude/commands/<name>.md) or a skill
(.../SKILL.md): the YAML frontmatter against the Claude Code field surface and
char caps, and the body against the Claude 5 anti-patterns.

Usage:
    uv run --with pyyaml python scripts/validate.py <path-to-command-or-SKILL.md>
"""

import re
import sys
from pathlib import Path

import yaml

NAME_RE = re.compile(r"^[a-z][a-z0-9-]*$")

MODELS = {"sonnet", "opus", "haiku", "fable", "inherit"}
EFFORTS = {"low", "medium", "high", "xhigh", "max"}
CONTEXTS = {"fork"}

DESC_MAX = 1024
DESC_PLUS_WTU_MAX = 1536

# Claude Code command/skill frontmatter keys (hyphenated), plus the
# public Agent-Skills packaging keys (license, metadata, compatibility).
KNOWN_KEYS = {
    "name",
    "description",
    "when_to_use",
    "argument-hint",
    "arguments",
    "allowed-tools",
    "disallowed-tools",
    "disable-model-invocation",
    "user-invocable",
    "model",
    "effort",
    "context",
    "agent",
    "shell",
    "hooks",
    "paths",
    "license",
    "metadata",
    "compatibility",
}

BOOL_KEYS = ("disable-model-invocation", "user-invocable")

# Claude Code-only keys that the packaging validator (quick_validate /
# package_skill) rejects — fine in-repo, flagged for distribution.
NON_PACKAGEABLE_KEYS = KNOWN_KEYS - {
    "name",
    "description",
    "license",
    "allowed-tools",
    "metadata",
    "compatibility",
}

# 'argument-hint' is a display-only field conventionally written with bracketed
# placeholders (e.g. `argument-hint: [user prompt] [orchestration prompt]`).
# That is not valid YAML flow syntax, but Claude Code tolerates it. Quote the
# value before parsing so the hint convention doesn't break the whole document.
ARG_HINT_RE = re.compile(r"^(\s*argument-hint:\s*)(\[.*)$")

BODY_MAX_LINES = 500

# A skill body loads into a session whose model the author does not control, so
# these are checked against the union of Claude 5 behaviors. Asking the model to
# surface its OWN reasoning can trigger the reasoning_extraction refusal on Fable
# 5 and silently fall back to Opus 4.8.
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
    (r"\bdouble[-\s]?check\b", "Claude 5 self-verifies; cut it or use a hook"),
    (r"\bre-?verif(y|ies|ying)\b", "Claude 5 self-verifies; cut it or use a hook"),
    (r"\bverify\s+your\s+(own\s+)?work\b", "Claude 5 self-verifies; cut it or use a hook"),
    (r"\bcheck\s+your\s+(own\s+)?work\b", "Claude 5 self-verifies; cut it or use a hook"),
    (
        r"\bshow\s+your\s+work\b",
        "reads as a reasoning-echo instruction; state the output shape instead",
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


def check_body(body, fails, warns):
    if not body.strip():
        fails.append("FAIL: body is empty — nothing loads when the skill triggers")
        return

    for pattern, reason in BODY_FAIL_PATTERNS:
        m = re.search(pattern, body, re.IGNORECASE)
        if m:
            fails.append(f"FAIL: body {reason}: {m.group(0)!r}")

    for pattern, reason in BODY_WARN_PATTERNS:
        m = re.search(pattern, body, re.IGNORECASE)
        if m:
            warns.append(f"WARN: body {reason}: {m.group(0)!r}")

    lines = len(body.splitlines())
    if lines > BODY_MAX_LINES:
        warns.append(
            f"WARN: body is {lines} lines (over {BODY_MAX_LINES}) — split the overflow "
            "into references/ and point at it"
        )


def validate(path):
    fails, warns = [], []
    p = Path(path)

    try:
        content = p.read_text()
    except OSError as e:
        return [f"FAIL: cannot read file: {e}"], []

    if not content.startswith("---"):
        fails.append(
            "FAIL: no YAML frontmatter at start of file (must begin with '---'; "
            "not fenced in a code block)"
        )
        return fails, warns

    m = re.match(r"^---\n(.*?)\n---\n?(.*)$", content, re.DOTALL)
    if not m:
        fails.append("FAIL: malformed frontmatter (no closing '---' delimiter)")
        return fails, warns

    try:
        fm = yaml.safe_load(_normalize_arg_hint(m.group(1)))
    except yaml.YAMLError as e:
        return [f"FAIL: frontmatter is not valid YAML: {e}"], []

    if not isinstance(fm, dict):
        return ["FAIL: frontmatter must be a YAML mapping/dict"], []

    # name (optional — flat commands take it from the filename, skills from the directory)
    if "name" in fm:
        name = fm.get("name")
        if not isinstance(name, str) or not name.strip():
            fails.append("FAIL: 'name' is present but must be a non-empty string")
        else:
            n = name.strip()
            if not NAME_RE.match(n) or n.startswith("-") or n.endswith("-") or "--" in n:
                fails.append(
                    "FAIL: 'name' must match ^[a-z][a-z0-9-]*$ (lowercase, hyphens; no "
                    f"underscores/uppercase/leading-trailing-double hyphen): {name!r}"
                )

    # description (recommended — WARN if absent)
    desc = fm.get("description")
    wtu = fm.get("when_to_use")
    if "description" not in fm:
        warns.append(
            "WARN: no 'description' field (allowed, but without one the command/skill "
            "only fires on manual /name invocation)"
        )
    elif not isinstance(desc, str) or not desc.strip():
        fails.append("FAIL: 'description' is present but must be a non-empty string")
    else:
        if "<" in desc or ">" in desc:
            fails.append("FAIL: 'description' must not contain angle brackets ('<' or '>')")
        if len(desc) > DESC_MAX:
            fails.append(f"FAIL: 'description' is too long ({len(desc)} chars; max {DESC_MAX})")
        if isinstance(wtu, str) and len(desc) + len(wtu) > DESC_PLUS_WTU_MAX:
            fails.append(
                f"FAIL: 'description' + 'when_to_use' too long "
                f"({len(desc) + len(wtu)} chars; max {DESC_PLUS_WTU_MAX})"
            )

    # model — alias or inherit only (AGENTS.md: never a dated id)
    if "model" in fm:
        model = str(fm["model"]).strip()
        if model not in MODELS:
            fails.append(
                f"FAIL: 'model' must be an alias or inherit — one of {sorted(MODELS)}: {model!r}"
            )

    # effort — optional; validate the value only when present
    if "effort" in fm and str(fm["effort"]).strip() not in EFFORTS:
        fails.append(f"FAIL: 'effort' must be one of {sorted(EFFORTS)}: {fm['effort']!r}")

    # boolean-typed fields
    for field in BOOL_KEYS:
        if field in fm and not isinstance(fm[field], bool):
            fails.append(f"FAIL: '{field}' must be a boolean: {fm[field]!r}")

    # context (WARN — surface may grow)
    if "context" in fm and str(fm["context"]).strip() not in CONTEXTS:
        warns.append(f"WARN: 'context' is usually one of {sorted(CONTEXTS)}: {fm['context']!r}")

    # heads-up for skills that will be packaged for distribution
    non_packageable = sorted(set(fm.keys()) & NON_PACKAGEABLE_KEYS)
    if non_packageable and p.name == "SKILL.md":
        warns.append(
            f"WARN: Claude Code-only key(s) {non_packageable} are fine in-repo but fail "
            "the packaging validator (quick_validate/package_skill)"
        )

    # unknown top-level keys
    for key in sorted(set(fm.keys()) - KNOWN_KEYS):
        warns.append(f"WARN: unknown top-level frontmatter key (surface may have evolved): {key!r}")

    check_body(m.group(2), fails, warns)

    return fails, warns


def main(argv):
    if len(argv) != 2:
        print(
            "Usage: uv run --with pyyaml python scripts/validate.py <path-to-command-or-SKILL.md>"
        )
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
