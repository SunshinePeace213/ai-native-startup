"""Deterministic spec validator for per-feature-harness-restructure (AC2 + AC4).

The executable contract for the two prose-heavy criteria: asserts the trimmed
`worktree/_common.py` module surface EXACTLY (AST — rejects extra helpers,
constants, or classes) and every harness-build.md clause as a relationship,
not a fragment. Prints every missing clause; exits 1 on any failure.

Run from the repo root (passes only after the build lands):

    uv run python specs/per-feature-harness-restructure/validate.py
"""

import ast
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
COMMON = ROOT / ".claude" / "hooks" / "worktree" / "_common.py"
BUILD_MD = ROOT / ".claude" / "commands" / "harness-layer" / "harness-build.md"

ALLOWED_FUNCS = {"note", "read_payload", "resolve_root", "run", "tail"}
ALLOWED_CONSTS = {"STDIN_TIMEOUT"}

failures: list[str] = []


def phrase(words: str) -> str:
    """A regex for a literal phrase that tolerates markdown line-wrapping."""
    return r"\s+".join(re.escape(w) for w in words.split())


def within(*parts: str, gap: int = 160) -> str:
    """Patterns required in order within `gap` chars of each other."""
    joiner = rf"[\s\S]{{0,{gap}}}?"
    return joiner.join(parts)


# --- AC2: exact trimmed-module surface -------------------------------------
if not COMMON.is_file():
    failures.append(f"AC2: {COMMON.relative_to(ROOT)} missing")
else:
    source = COMMON.read_text()
    tree = ast.parse(source)
    funcs = {n.name for n in tree.body if isinstance(n, ast.FunctionDef | ast.AsyncFunctionDef)}
    consts = {
        target.id
        for node in tree.body
        if isinstance(node, ast.Assign)
        for target in node.targets
        if isinstance(target, ast.Name)
    } | {
        node.target.id
        for node in tree.body
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name)
    }
    if funcs != ALLOWED_FUNCS:
        failures.append(f"AC2: functions {sorted(funcs)} != required {sorted(ALLOWED_FUNCS)}")
    if consts != ALLOWED_CONSTS:
        failures.append(
            f"AC2: module constants {sorted(consts)} != required {sorted(ALLOWED_CONSTS)}"
        )
    if any(isinstance(n, ast.ClassDef) for n in tree.body):
        failures.append("AC2: unexpected top-level class in trimmed _common.py")
    if not re.search(r"^STDIN_TIMEOUT(?:\s*:\s*float)?\s*=\s*5\.0\s*$", source, re.M):
        failures.append("AC2: STDIN_TIMEOUT must be exactly 5.0")

# --- AC4: harness-build.md clauses as relationships -------------------------
# (clause, required patterns, forbidden patterns)
CLAUSES: list[tuple[str, list[str], list[str]]] = [
    (
        "fixer model routing via Agent model param",
        [within(r"\bmodel\b", phrase("per issue difficulty"), gap=80), phrase("`model` param")],
        [r"fixer\s+subagents?\s+\(effort\s+per\s+issue\)"],
    ),
    (
        "effort tier in task brief; inherited session effort; no effort parameter",
        [
            within(phrase("effort tier"), phrase("task brief")),
            within(r"\binherit\w*\b", phrase("reasoning effort"), gap=80),
        ],
        # forbid an effort key on an Agent deployment (Codex's own
        # model_reasoning_effort config line is legitimate and stays)
        [r"Agent\b[\s\S]{0,80}?\beffort\s*[:=]"],
    ),
    (
        "parallel background fixers on disjoint clusters; exactly one fix commit",
        [
            phrase("disjoint clusters"),
            within(r"parallel", r"background\s+fixer", gap=60),
            phrase("ONE fix commit"),
        ],
        [],
    ),
    (
        "concurrent launch of unblocked, file-disjoint implement tasks",
        [within(r"\bunblocked\b", phrase("file-disjoint tasks"), r"concurrent\w*", gap=120)],
        [],
    ),
    (
        "manifest keyed by kebab-case Task ID with autolink warning",
        [phrase("kebab-case Task ID"), phrase("GitHub autolinks")],
        [],
    ),
    (
        "PR assignee plus mirrored type and priority labels read from the issue",
        [
            r"--assignee",
            within(phrase("type label"), r"priority:P", gap=200),
            phrase("--json labels"),
        ],
        [],
    ),
]

if not BUILD_MD.is_file():
    failures.append(f"AC4: {BUILD_MD.relative_to(ROOT)} missing")
else:
    text = BUILD_MD.read_text()
    for clause, required, forbidden in CLAUSES:
        for pat in required:
            if not re.search(pat, text):
                failures.append(f"AC4 [{clause}]: missing /{pat}/")
        for pat in forbidden:
            if re.search(pat, text):
                failures.append(f"AC4 [{clause}]: forbidden /{pat}/ present")

if failures:
    print("SPEC VALIDATION FAILED:")
    for failure in failures:
        print(f"  - {failure}")
    sys.exit(1)
print("spec validation OK: AC2 module surface and all AC4 clauses hold")
