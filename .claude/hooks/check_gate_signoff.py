#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Stop hook for the studio-layer hard gates: keep a phase open until the client
has signed it.

Registered in the frontmatter of /studio-layer:p2-definition, p3-structure,
p4-art-direction and p6-handoff, each passing its own phase token as argv[1]. A
client project holds all eight phase folders at once, so the phase can never be
inferred from mtime the way the spec gate infers its plan folder.

Exit 2 denies the stop and stderr comes back as the repair instruction.
Everything the gate cannot resolve -- no clients/ dir, an unknown phase token,
an unidentifiable project, malformed stdin -- exits 0 per the repo's fail-open
hook contract; a bad registration is caught by test_wiring.py at CI time rather
than mid-engagement.

The sign-off at clients/<client>/<project>/sign-off/<phase>.md needs a filled
Approver and Date plus an artifact table whose every row names an existing
project-relative file whose SHA-256 still matches the recorded hash (a content
hash -- clients/ is gitignored, so no commit object exists). p2 additionally
needs a fully triaged cold-designer document, p3 a client-signed component
inventory, and p6 a QA report with no open blocking finding plus that same
inventory still hashing to what the P3 sign-off recorded.
"""

import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

GATED_PHASES = ("p2", "p3", "p4", "p6")

INVENTORY = "structure/inventory.md"
TRIAGE = "definition/cold-designer-triage.md"
QA_REPORT = "handoff/qa-report.md"

SHA_RE = re.compile(r"^[0-9a-f]{64}$")
SEPARATOR_CELL_RE = re.compile(r"^:?-{2,}:?$")
# A whole-value angle span (`<approver name>`) is a template slot, never content.
ANGLE_SPAN_RE = re.compile(r"^<[^<>]*>$")
PLACEHOLDER_VALUES = {"-", "--", "tbd", "tba", "todo", "n/a", "na", "yyyy-mm-dd"}
DASH_RE = re.compile(r"\s*[-–—]+\s*")


def unwrap(cell: str) -> str:
    """A field value or table cell with markdown emphasis and code ticks removed."""
    return cell.strip().strip("`*_ ").strip()


def is_placeholder(value: str) -> bool:
    """Empty, whitespace-only and leftover template values all read as unsigned."""
    text = unwrap(value)
    return not text or text.lower() in PLACEHOLDER_VALUES or ANGLE_SPAN_RE.match(text) is not None


def field_value(text: str, name: str) -> str | None:
    """The value of a '- **<name>:** …' line, or None when the line is absent."""
    pattern = re.compile(rf"^[-*+\s]*{re.escape(name)}\s*:\s*(.*)$", re.IGNORECASE)
    for raw in text.splitlines():
        line = raw.replace("*", "").replace("_", "")
        if (match := pattern.match(line)) is not None:
            return match.group(1)
    return None


def tables(text: str) -> list[list[list[str]]]:
    """Every markdown table in the document as cell rows, separator rows dropped."""
    found: list[list[list[str]]] = []
    current: list[list[str]] = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("|"):
            row = [cell.strip() for cell in stripped.strip("|").split("|")]
            if not all(SEPARATOR_CELL_RE.match(cell) for cell in row):
                current.append(row)
        elif current:
            found.append(current)
            current = []
    if current:
        found.append(current)
    return found


def find_table(text: str, *header_terms: str) -> list[list[str]] | None:
    """The first table whose header names every term, header row included."""
    for rows in tables(text):
        header = [cell.lower() for cell in rows[0]]
        if all(any(term in cell for cell in header) for term in header_terms):
            return rows
    return None


def column(header: list[str], term: str) -> int:
    """Index of the first header cell naming `term`, or -1."""
    return next((i for i, cell in enumerate(header) if term in cell.lower()), -1)


def cell(row: list[str], index: int) -> str:
    return unwrap(row[index]) if 0 <= index < len(row) else ""


def sha256_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def relative(value: str) -> str:
    """A project-relative artifact path as written in a sign-off row."""
    return unwrap(value).removeprefix("./")


def resolve_root() -> Path:
    env_root = os.environ.get("CLAUDE_PROJECT_DIR")
    if env_root:
        return Path(env_root)
    proc = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True)
    if proc.returncode == 0 and proc.stdout.strip():
        return Path(proc.stdout.strip())
    return Path.cwd()


def projects_under(clients: Path) -> list[Path]:
    """Every clients/<client>/<project>/ directory.

    Never conditioned on sign-off/ existing: a project that has never been signed
    is precisely the case the gate must block, so defining it away would make a
    brand-new project look like no project and fail open on its first hard gate.
    """
    return sorted(
        project
        for client in clients.iterdir()
        if client.is_dir() and not client.name.startswith(".")
        for project in client.iterdir()
        if project.is_dir() and not project.name.startswith(".")
    )


def resolve_project(projects: list[Path], cwd: str | None) -> Path | None:
    """The project being gated: the payload's cwd when it sits inside one, else
    the sole project. Two projects and a cwd inside neither means guessing, and a
    gate that guesses gates the wrong engagement."""
    if cwd:
        here = Path(cwd).resolve()
        for project in projects:
            if here.is_relative_to(project.resolve()):
                return project
    return projects[0] if len(projects) == 1 else None


def artifact_rows(text: str) -> list[tuple[str, str]] | None:
    """(path, sha) pairs from a sign-off's artifact table, or None when absent."""
    table = find_table(text, "artifact", "sha")
    if table is None:
        return None
    header, *rows = table
    path_at, sha_at = column(header, "artifact"), column(header, "sha")
    return [(relative(cell(row, path_at)), cell(row, sha_at).lower()) for row in rows]


def check_signoff(project: Path, phase: str, problems: list[str]) -> list[tuple[str, str]]:
    """Approver, Date, and an artifact table every row of which still resolves."""
    rel = f"sign-off/{phase}.md"
    path = project / rel
    if not path.is_file():
        problems.append(f"{rel}: MISSING FILE — the phase has no client sign-off")
        return []

    text = path.read_text(errors="replace")
    for name in ("Approver", "Date"):
        value = field_value(text, name)
        if value is None:
            problems.append(f"{rel}: no '{name}' line")
        elif is_placeholder(value):
            problems.append(f"{rel}: '{name}' is empty or still a template placeholder")

    rows = artifact_rows(text)
    if rows is None:
        problems.append(f"{rel}: no artifact table with 'Artifact' and 'SHA-256' columns")
        return []
    if not rows:
        problems.append(f"{rel}: the artifact table has no rows — nothing was approved")

    for artifact, sha in rows:
        if is_placeholder(artifact):
            problems.append(f"{rel}: an artifact row names no file")
            continue
        target = project / artifact
        if not SHA_RE.match(sha):
            problems.append(f"{rel}: '{artifact}' carries no 64-hex SHA-256")
        elif not target.is_file():
            problems.append(f"{rel}: '{artifact}' does not exist — an approval of a missing file")
        elif (actual := sha256_of(target)) != sha:
            problems.append(
                f"{rel}: '{artifact}' no longer matches what was approved "
                f"(signed {sha}, current {actual})"
            )
    return rows


def is_triaged(value: str) -> bool:
    """A disposition per the documented schema, tolerating either dash spelling."""
    text = DASH_RE.sub(" - ", unwrap(value).lower()).strip()
    return text == "brief unclear - amended" or text.startswith("acceptable variance - ")


def check_triage(project: Path, problems: list[str]) -> None:
    """p2: the cold-designer diff is advisory — the triaged document is the gate."""
    path = project / TRIAGE
    if not path.is_file():
        problems.append(f"{TRIAGE}: MISSING FILE — the cold-designer test has not been triaged")
        return
    table = find_table(path.read_text(errors="replace"), "disposition")
    if table is None:
        problems.append(f"{TRIAGE}: no triage table with a 'Disposition' column")
        return
    header, *rows = table
    at = column(header, "disposition")
    section_at = column(header, "section")
    for row in rows:
        if not is_triaged(cell(row, at)):
            label = cell(row, section_at) or cell(row, 0) or "(unnamed row)"
            problems.append(
                f"{TRIAGE}: row '{label}' is untriaged — a disposition reads "
                "'brief unclear — amended' or begins 'acceptable variance —'"
            )


def check_inventory_signed(
    project: Path, approved: list[tuple[str, str]], problems: list[str]
) -> None:
    """p3: the inventory P6 measures the design against is approved here, not
    authored at P6 alongside the matrix that would then agree with it."""
    path = project / INVENTORY
    if not path.is_file():
        problems.append(f"{INVENTORY}: MISSING FILE — P3 enumerates it from the signed wireframes")
    elif not path.read_text(errors="replace").strip():
        problems.append(f"{INVENTORY}: is empty — a missing baseline is never a pass")
    if not any(artifact == INVENTORY for artifact, _sha in approved):
        problems.append(
            f"sign-off/p3.md: the artifact table does not list {INVENTORY} — "
            "the client must approve the list P6 is measured against"
        )


def check_inventory_unchanged(project: Path, problems: list[str]) -> None:
    """p6: re-hash the inventory against the SHA the P3 sign-off recorded.

    A signature three phases back says nothing about the file P6 quantifies over:
    deleting rows between P3 and P6 would leave a one-component matrix passing
    against a one-component list with the P3 signature sitting untouched.
    """
    rel = "sign-off/p3.md"
    signoff = project / rel
    if not signoff.is_file():
        problems.append(
            f"{rel}: MISSING FILE — P6 re-verifies {INVENTORY} against the P3 signature"
        )
        return
    rows = artifact_rows(signoff.read_text(errors="replace")) or []
    signed = next((sha for artifact, sha in rows if artifact == INVENTORY), None)
    if signed is None:
        problems.append(
            f"{rel}: never listed {INVENTORY}, so P6 has no signed list to measure against"
        )
        return
    path = project / INVENTORY
    if not path.is_file():
        problems.append(f"{INVENTORY}: MISSING FILE — it was signed at P3 and is gone at P6")
        return
    if (actual := sha256_of(path)) != signed:
        problems.append(
            f"{INVENTORY}: changed since the P3 sign-off (signed {signed}, current {actual}) — "
            "amend it with a change order and re-sign P3"
        )


def check_qa_report(project: Path, problems: list[str]) -> None:
    """p6: design QA blocks handoff as a mechanism — an open blocking finding
    keeps the phase open."""
    path = project / QA_REPORT
    if not path.is_file():
        problems.append(f"{QA_REPORT}: MISSING FILE — design QA has not reported")
        return
    table = find_table(path.read_text(errors="replace"), "finding", "severity", "status")
    if table is None:
        problems.append(f"{QA_REPORT}: no findings table with 'Severity' and 'Status' columns")
        return
    header, *rows = table
    finding_at = column(header, "finding")
    severity_at = column(header, "severity")
    status_at = column(header, "status")
    for row in rows:
        if cell(row, severity_at).lower() == "blocking" and cell(row, status_at).lower() == "open":
            problems.append(f"{QA_REPORT}: blocking finding still open — {cell(row, finding_at)}")


def main(argv: list[str]) -> int:
    phase = argv[1] if len(argv) > 1 else ""
    if phase not in GATED_PHASES:
        return 0  # a bad registration is a config failure; test_wiring.py catches it

    try:
        payload = json.loads(sys.stdin.read())
    except ValueError:
        return 0
    if not isinstance(payload, dict):
        return 0

    clients = resolve_root() / "clients"
    if not clients.is_dir():
        return 0  # no client work in this project: the gate is invisible

    projects = projects_under(clients)
    project = resolve_project(projects, payload.get("cwd"))
    if project is None:
        print(
            f"check_gate_signoff: {len(projects)} client projects under clients/ and no cwd "
            f"inside one, so the {phase} gate cannot tell which engagement to gate. Not gating.",
            file=sys.stderr,
        )
        return 0

    problems: list[str] = []
    approved = check_signoff(project, phase, problems)
    if phase == "p2":
        check_triage(project, problems)
    elif phase == "p3":
        check_inventory_signed(project, approved, problems)
    elif phase == "p6":
        check_qa_report(project, problems)
        check_inventory_unchanged(project, problems)
    if not problems:
        return 0

    label = project.relative_to(clients.parent)
    listing = "\n".join(f"  - {problem}" for problem in problems)
    if payload.get("stop_hook_active"):
        # A client signature will not appear because Claude tried again, and the
        # turn is force-ended after 8 consecutive blocks anyway.
        print(
            f"check_gate_signoff: the {phase} gate for {label} is still unsigned:\n{listing}",
            file=sys.stderr,
        )
        return 0

    print(f"Stop blocked: the {phase} gate for {label} is not signed off:", file=sys.stderr)
    print(f"\n{listing}", file=sys.stderr)
    print(
        f"\nWrite the missing documents and collect the client's signature into "
        f"{label}/sign-off/{phase}.md — every artifact row names an existing file and its "
        "current sha256sum — then stop again.",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv))
    except Exception as exc:  # a plumbing failure must never wedge a session
        print(f"check_gate_signoff: skipped after an internal error: {exc}", file=sys.stderr)
        sys.exit(0)
