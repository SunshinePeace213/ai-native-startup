#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Deterministic spec gate: lint a plan folder before the Codex panel spends a token.

Owns the mechanical halves of the spec standards — S7 tracking hygiene, template
completeness, S1 AC<->task traceability (both directions), and S2 command
runnability. Semantic judgment (does the command prove the AC?) belongs to the
review lenses, not here.

A validation command's path token passes when it exists from the repo root OR is
named in tasks.md — a plan may cite a test file its own build creates. Existing
pytest targets must also collect (`--collect-only`); execution belongs to
impl_lint.py after the build.

Usage: spec_lint.py specs/<name>/          (run from the repo root)
One line per check: `PASS <check> <detail>` / `FAIL <check> <detail>`. Exit 1 on
any failure.
"""

import re
import subprocess
import sys
from pathlib import Path

REQUIRED_SECTIONS: dict[str, tuple[str, ...]] = {
    "spec.md": (
        "Tracking",
        "Task Description",
        "Objective",
        "Non-Goals",
        "Requirements & Decisions",
        "Relevant Files",
        "Edge Cases",
        "Risk & Rollback",
        "Guardrails",
        "Codex Verification",
    ),
    "tasks.md": ("Step by Step Tasks",),
    "acceptance-criteria.md": ("Acceptance Criteria", "Validation Commands"),
    "decisions.md": (
        "Summary",
        "Resolved Decisions",
        "Assumptions",
        "Open Questions / Out of Scope",
    ),
}

TYPES = "feat|fix|docs|style|refactor|perf|test|chore"
TRACKING_FIELDS = {
    "Type": re.compile(rf"^({TYPES})$"),
    "Complexity": re.compile(r"^(simple|medium|complex)$"),
    "Issue": re.compile(r"#(\d+)"),
    "Branch": re.compile(rf"`?({TYPES})/(\d+)-[a-z0-9-]+`?$"),
    "Worktree": re.compile(r"^`?/"),
    "Review profile": re.compile(r"^`?(grounded|standard)`?$"),
}

COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
# A template slot: an angle-bracket span opening on a word character and holding a
# space. Paths (`<type>/<N>-<slug>`) and autolinks have no inner space.
PLACEHOLDER_RE = re.compile(r"<[A-Za-z#][^<>]*\s[^<>]*>")
COMMAND_RE = re.compile(r"^\s*-\s+`([^`]+)`", re.MULTILINE)
PATH_TOKEN_RE = re.compile(r"\b((?:tests|specs|scripts)/[^\s:`'\"]+)")
WILDCARD_RE = re.compile(r"every AC|all ACs|every criterion", re.IGNORECASE)


def section_body(text: str, section: str) -> str | None:
    """The lines under '## <section>', comments stripped, fenced code respected."""
    heading = f"## {section}"
    body: list[str] = []
    capturing = False
    fenced = False
    for line in COMMENT_RE.sub("", text).splitlines():
        if line.lstrip().startswith("```"):
            fenced = not fenced
        elif not fenced and line.startswith("#"):
            if line.rstrip() == heading:
                capturing = True
                continue
            if capturing and not line.startswith("###"):
                break
            if capturing:
                body.append(line)
            continue
        if capturing:
            body.append(line)
    return "\n".join(body) if capturing else None


def check_tracking(folder: Path) -> list[str]:
    body = section_body((folder / "spec.md").read_text(errors="replace"), "Tracking")
    if body is None:
        return ["spec.md has no ## Tracking section"]
    problems = []
    values: dict[str, str] = {}
    for field, pattern in TRACKING_FIELDS.items():
        match = re.search(rf"\*\*{re.escape(field)}:\*\*\s*(.+)$", body, re.MULTILINE)
        if not match:
            problems.append(f"missing field {field}")
            continue
        value = match.group(1).strip()
        if PLACEHOLDER_RE.search(value) or not pattern.search(value):
            problems.append(f"{field} not real: {value!r}")
        else:
            values[field] = value
    if leftover := PLACEHOLDER_RE.search(body):
        problems.append(f"placeholder in Tracking: {leftover.group()}")
    if "Issue" in values and "Branch" in values:
        issue = TRACKING_FIELDS["Issue"].search(values["Issue"]).group(1)
        branch_type, branch_issue = TRACKING_FIELDS["Branch"].search(values["Branch"]).groups()
        if branch_issue != issue:
            problems.append(f"Branch carries #{branch_issue}, Issue says #{issue}")
        if values.get("Type") and branch_type != values["Type"]:
            problems.append(f"Branch type {branch_type!r} != Type {values['Type']!r}")
    return problems


def check_sections(folder: Path) -> list[str]:
    problems = []
    for name, sections in REQUIRED_SECTIONS.items():
        path = folder / name
        if not path.is_file():
            problems.append(f"{name} missing")
            continue
        text = path.read_text(errors="replace")
        for section in sections:
            body = section_body(text, section)
            if body is None:
                problems.append(f"{name}: no '## {section}'")
            elif not body.strip():
                problems.append(f"{name}: '## {section}' empty")
            elif leftover := PLACEHOLDER_RE.search(body):
                problems.append(f"{name}: '## {section}' holds placeholder {leftover.group()}")
    return problems


def check_traceability(folder: Path) -> list[str]:
    criteria = (folder / "acceptance-criteria.md").read_text(errors="replace")
    tasks = COMMENT_RE.sub("", (folder / "tasks.md").read_text(errors="replace"))
    acs = set(re.findall(r"\*\*(AC\d+)\*\*", criteria))
    if not acs:
        return ["no **AC<n>** criteria parsed from acceptance-criteria.md"]
    satisfies = re.findall(r"\*\*Satisfies:\*\*\s*(.+)$", tasks, re.MULTILINE)
    if not satisfies:
        return ["no **Satisfies:** lines parsed from tasks.md"]
    referenced = {ac for line in satisfies for ac in re.findall(r"AC\d+", line)}
    wildcard = any(WILDCARD_RE.search(line) for line in satisfies)
    problems = [f"{ac} named by no task" for ac in sorted(acs - referenced) if not wildcard]
    problems += [f"task cites {ac}, which does not exist" for ac in sorted(referenced - acs)]
    return problems


def check_commands(folder: Path, root: Path) -> list[str]:
    body = section_body(
        (folder / "acceptance-criteria.md").read_text(errors="replace"), "Validation Commands"
    )
    if body is None:
        return ["acceptance-criteria.md has no ## Validation Commands"]
    commands = COMMAND_RE.findall(body)
    if not commands:
        return ["no `commands` parsed under ## Validation Commands"]
    planned = (folder / "tasks.md").read_text(errors="replace")
    problems = []
    for cmd in commands:
        if cmd.startswith("manual:"):
            continue
        for token in PATH_TOKEN_RE.findall(cmd):
            path = token.split("::")[0]
            if not (root / path).exists() and path not in planned:
                problems.append(f"{path} absent and named by no task: `{cmd}`")
            elif (root / path).exists() and " pytest" in f" {cmd}":
                collect = subprocess.run(
                    f"{cmd} --collect-only -q",
                    shell=True,
                    cwd=root,
                    capture_output=True,
                    text=True,
                    timeout=120,
                )
                if collect.returncode != 0:
                    problems.append(f"pytest target not collectable: `{cmd}`")
    return problems


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__, file=sys.stderr)
        return 2
    folder = Path(sys.argv[1])
    if not (folder / "spec.md").is_file():
        print(f"FAIL folder {folder} has no spec.md", file=sys.stderr)
        return 1

    root = Path.cwd()
    failures = 0
    checks = [
        ("tracking-fields", lambda: check_tracking(folder)),
        ("sections-complete", lambda: check_sections(folder)),
        ("traceability", lambda: check_traceability(folder)),
        ("command-runnable", lambda: check_commands(folder, root)),
    ]
    passed_detail = {
        "tracking-fields": "all 6 fields real",
        "sections-complete": "templates filled, no placeholders",
        "traceability": "AC<->task holds both directions",
        "command-runnable": "every command exists or is planned; existing targets collect",
    }
    for name, run in checks:
        try:
            problems = run()
        except FileNotFoundError as err:
            problems = [f"missing file: {err.filename}"]
        if problems:
            failures += 1
            print(f"FAIL {name} {'; '.join(problems)}")
        else:
            print(f"PASS {name} {passed_detail[name]}")

    if failures:
        print(f"{failures} failures — fix before invoking the gate; the gate re-runs this lint.")
        return 1
    print("all checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
