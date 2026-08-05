#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Deterministic implementation gate: lint a built diff before the Codex panel runs.

Owns the mechanical halves of the impl standards — I2 acceptance evidence
(every ## Validation Commands entry executes and passes from the repo root,
judged by its own exit status), I7 convention compliance (commit format plus the
`Refs #N` footer over the branch range), the orphan scan (unused imports and
variables in changed Python), and notes-evidence presence. Semantic judgment
belongs to the review lenses, not here.

Usage: impl_lint.py specs/<name>/ [--base <ref>]   (run from the repo root)
The range is merge-base(<base>, HEAD)..HEAD; <base> defaults to origin/main,
falling back to main. Commits subject-scoped `docs(discovery)` are exempt from
the Refs-footer requirement (discovery predates the issue).
One line per check: `PASS <check> <detail>` / `FAIL <check> <detail>`. Exit 1 on
any failure.
"""

import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_commit_messages as ccm  # noqa: E402

COMMAND_RE = re.compile(r"^\s*-\s+`([^`]+)`", re.MULTILINE)
REFS_RE = re.compile(r"^Refs #\d+", re.MULTILINE)
DISCOVERY_RE = re.compile(r"^\S+ docs\(discovery\):")
COMMAND_TIMEOUT = 600


def sh(args: list[str], **kwargs) -> subprocess.CompletedProcess:
    return subprocess.run(args, capture_output=True, text=True, **kwargs)


def section_body(text: str, section: str) -> str | None:
    match = re.search(rf"^## {re.escape(section)}$(.*?)(?=^## |\Z)", text, re.M | re.S)
    return match.group(1) if match else None


def resolve_range(base: str | None) -> str | None:
    candidates = [base] if base else ["origin/main", "main"]
    for candidate in candidates:
        merge_base = sh(["git", "merge-base", candidate, "HEAD"])
        if merge_base.returncode == 0:
            return f"{merge_base.stdout.strip()}..HEAD"
    return None


def check_validation_commands(folder: Path, root: Path) -> list[str]:
    criteria = folder / "acceptance-criteria.md"
    if not criteria.is_file():
        return ["acceptance-criteria.md missing"]
    body = section_body(criteria.read_text(errors="replace"), "Validation Commands")
    if body is None:
        return ["acceptance-criteria.md has no ## Validation Commands"]
    commands = COMMAND_RE.findall(body)
    if not commands:
        return ["no `commands` parsed under ## Validation Commands"]
    notes_path = folder / "implementation-notes.md"
    notes = notes_path.read_text(errors="replace") if notes_path.is_file() else ""
    problems = []
    for cmd in commands:
        if cmd.startswith("manual:"):
            probe = cmd.removeprefix("manual:").strip()[:40]
            if probe and probe not in notes:
                problems.append(f"manual check has no recorded output in notes: `{cmd}`")
            continue
        try:
            run = subprocess.run(
                cmd, shell=True, cwd=root, capture_output=True, text=True, timeout=COMMAND_TIMEOUT
            )
        except subprocess.TimeoutExpired:
            problems.append(f"timed out after {COMMAND_TIMEOUT}s: `{cmd}`")
            continue
        if run.returncode != 0:
            problems.append(f"exit {run.returncode}: `{cmd}`")
    return problems


def check_commits(rev_range: str) -> list[str]:
    problems = []
    for sha, subject, body in ccm.commits(rev_range):
        for problem in ccm.check_subject(subject) + ccm.check_body(body):
            problems.append(f"{sha[:9]} {problem}")
        if not REFS_RE.search(body) and not DISCOVERY_RE.match(subject):
            problems.append(f"{sha[:9]} missing `Refs #N` footer")
    return problems


def check_orphans(rev_range: str, root: Path) -> list[str]:
    diff = sh(["git", "diff", "--name-only", "--diff-filter=d", rev_range])
    changed = [f for f in diff.stdout.splitlines() if f.endswith(".py") and (root / f).is_file()]
    if not changed:
        return []
    ruff_bin = shutil.which("ruff")
    ruff = [ruff_bin] if ruff_bin else ["uv", "run", "ruff"]
    scan = sh([*ruff, "check", "--select", "F401,F841", "--no-cache", *changed], cwd=root)
    if scan.returncode != 0:
        offenders = [line for line in scan.stdout.splitlines() if ":" in line][:5]
        return offenders or [scan.stdout.strip() or scan.stderr.strip()]
    return []


def check_notes(folder: Path) -> list[str]:
    path = folder / "implementation-notes.md"
    if not path.is_file():
        return ["implementation-notes.md missing"]
    body = section_body(path.read_text(errors="replace"), "Log")
    if body is None or not re.sub(r"<!--.*?-->", "", body, flags=re.DOTALL).strip():
        return ["## Log is missing or empty"]
    if not re.search(r"`[^`]+`\s*(→|->)", body):
        return ["no hand-off entry records a command with its observed result (`cmd` → result)"]
    return []


def main() -> int:
    args = sys.argv[1:]
    base = None
    if "--base" in args:
        i = args.index("--base")
        base = args[i + 1]
        del args[i : i + 2]
    if len(args) != 1:
        print(__doc__, file=sys.stderr)
        return 2
    folder = Path(args[0])
    root = Path.cwd()

    rev_range = resolve_range(base)
    failures = 0
    checks = [
        ("validation-commands", lambda: check_validation_commands(folder, root)),
        (
            "commit-format",
            lambda: check_commits(rev_range) if rev_range else ["no base ref resolves"],
        ),
        ("orphans", lambda: check_orphans(rev_range, root) if rev_range else []),
        ("notes-evidence", lambda: check_notes(folder)),
    ]
    passed_detail = {
        "validation-commands": "every command passes from the repo root",
        "commit-format": f"range {rev_range} conforms to git-workflow.md",
        "orphans": "no unused imports or variables in changed Python",
        "notes-evidence": "hand-off log present with recorded results",
    }
    for name, run in checks:
        problems = run()
        if problems:
            failures += 1
            print(f"FAIL {name} {'; '.join(problems)}")
        else:
            print(f"PASS {name} {passed_detail[name]}")

    if failures:
        print(f"{failures} failures — fix, then re-run before the panel.")
        return 1
    print("all checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
