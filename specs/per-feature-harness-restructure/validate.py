"""Deterministic spec validator for per-feature-harness-restructure (AC2 + AC4).

The executable contract for the two prose-heavy criteria. AC2: AST-asserts the
trimmed `worktree/_common.py` surface EXACTLY (rejects extra functions,
constants, or classes). AC4: each harness-build.md clause is one bounded
relationship — ALL of a clause's required terms must co-occur inside a single
markdown block (one bullet, heading, or paragraph), so fragments scattered
across unrelated sections never pass. Forbidden patterns are document-wide.
Prints every failing clause by name; exits 1 on any failure.

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


def segments(text: str) -> list[str]:
    """Markdown blocks: each list item, heading, or paragraph stands alone.

    Splits at a newline followed by a list marker or heading, and at blank
    lines; wrapped continuation lines stay inside their block.
    """
    parts = re.split(r"\n(?=[-*+] |\d+\. |#{1,6} )|\n{2,}", text)
    return [p for p in parts if p.strip()]


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

# --- AC4: harness-build.md clauses, each bounded to ONE markdown block ------
# (clause, required patterns — all must hit the SAME block, forbidden patterns — document-wide)
CLAUSES: list[tuple[str, list[str], list[str]]] = [
    (
        "fixer model routing via Agent model param",
        [r"\bmodel\b", phrase("per issue difficulty"), phrase("`model` param")],
        [r"fixer\s+subagents?\s+\(effort\s+per\s+issue\)"],
    ),
    (
        "effort tier in task brief; inherited session effort; no effort parameter",
        [
            phrase("effort tier"),
            phrase("task brief"),
            r"\binherit\w*\b",
            phrase("reasoning effort"),
        ],
        # forbid an effort key on an Agent deployment (Codex's own
        # model_reasoning_effort config line is legitimate and stays)
        [r"Agent\b[\s\S]{0,80}?\beffort\s*[:=]"],
    ),
    (
        "parallel background fixers on disjoint clusters; exactly one fix commit",
        [
            phrase("disjoint clusters"),
            r"\bparallel\b",
            r"background\s+fixer",
            phrase("ONE fix commit"),
        ],
        [],
    ),
    (
        "concurrent launch of unblocked, file-disjoint implement tasks",
        [r"\bunblocked\b", phrase("file-disjoint tasks"), r"\bconcurrent\w*"],
        [],
    ),
    (
        "manifest keyed by kebab-case Task ID with autolink warning",
        [phrase("kebab-case Task ID"), phrase("GitHub autolinks")],
        [],
    ),
    (
        "gh pr create carries assignee plus type/priority labels read from the issue",
        [
            phrase("gh pr create"),
            r"--assignee",
            phrase("type label"),
            r"priority:P",
            phrase("--json labels"),
        ],
        [],
    ),
]

if not BUILD_MD.is_file():
    failures.append(f"AC4: {BUILD_MD.relative_to(ROOT)} missing")
else:
    text = BUILD_MD.read_text()
    blocks = segments(text)
    for clause, required, forbidden in CLAUSES:
        if not any(all(re.search(pat, block) for pat in required) for block in blocks):
            failures.append(
                f"AC4 [{clause}]: no single markdown block contains all of: "
                + ", ".join(f"/{pat}/" for pat in required)
            )
        for pat in forbidden:
            if re.search(pat, text):
                failures.append(f"AC4 [{clause}]: forbidden /{pat}/ present")

if failures:
    print("SPEC VALIDATION FAILED:")
    for failure in failures:
        print(f"  - {failure}")
    sys.exit(1)
print("spec validation OK: AC2 module surface and all AC4 clauses hold")
