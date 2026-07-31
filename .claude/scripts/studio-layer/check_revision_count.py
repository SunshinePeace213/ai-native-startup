#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Count prototype revision rounds against the allowance the signed brief declares.

Usage: check_revision_count.py <project-dir>

The allowance is re-derived from definition/project-brief.md on every run -- the line
'- **Revision rounds:** <integer> (plus polish)' -- never hard-coded. Each round in
prototype/revision-log.md past that allowance must name a change order that exists and
carries all four required fields, so an empty or unsigned document cannot buy a round.
Exit 0 pass; 1 with file:line diagnostics naming each unbought round; 2 when the check
cannot run its arithmetic -- a missing project directory, brief or revision log, an
unparseable log, or a brief that declares no allowance at all, which is a missing
baseline rather than a zero allowance.
"""

import re
import sys
from pathlib import Path

ALLOWANCE_RE = re.compile(r"^\s*-\s*\*\*Revision rounds:?\*\*\s*(\d+)\b", re.MULTILINE)
FIELD_RE = re.compile(r"^\s*-\s*\*\*(?P<name>[^*]+?):?\*\*\s*(?P<value>.*)$")
DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}")
DELIMITER_RE = re.compile(r":?-{3,}:?")
UNFILLED = {"", "-", "tbd", "n/a", "none"}


class ParseError(Exception):
    """The check cannot run its arithmetic on this input."""


def cells(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def is_delimiter(row: list[str]) -> bool:
    return bool(row) and all(DELIMITER_RE.fullmatch(cell) for cell in row)


def tables(lines: list[str]):
    """(header, rows) per pipe table; rows are (line_no, cells)."""
    found = []
    i = 0
    while i < len(lines):
        head = lines[i].lstrip()
        if head.startswith("|") and i + 1 < len(lines) and is_delimiter(cells(lines[i + 1])):
            header = cells(lines[i])
            rows = []
            j = i + 2
            while j < len(lines) and lines[j].lstrip().startswith("|"):
                rows.append((j + 1, cells(lines[j])))
                j += 1
            found.append((header, rows))
            i = j
        else:
            i += 1
    return found


def read_lines(path: Path, what: str) -> list[str]:
    try:
        return path.read_text(encoding="utf-8").splitlines()
    except OSError as err:
        raise ParseError(f"cannot read the {what} at {path}: {err}") from err


def cell_at(row: list[str], index: int | None) -> str:
    return row[index] if index is not None and index < len(row) else ""


def allowance(path: Path) -> int:
    match = ALLOWANCE_RE.search("\n".join(read_lines(path, "signed project brief")))
    if match is None:
        raise ParseError(
            f"the signed brief at {path} declares no '- **Revision rounds:** <integer>' line -- "
            "the baseline is missing, which is not the same as an allowance of zero"
        )
    return int(match.group(1))


def rounds(path: Path) -> list[tuple[int, int, str]]:
    """(line_no, round number, change-order reference) per revision-log row."""
    lines = read_lines(path, "revision log")
    for header, rows in tables(lines):
        index = {name.casefold(): i for i, name in enumerate(header)}
        if "round" not in index:
            continue
        logged = []
        for line_no, row in rows:
            raw = cell_at(row, index["round"]).strip("` ")
            try:
                number = int(raw)
            except ValueError as err:
                raise ParseError(f"{path}:{line_no}: '{raw}' is not a round number") from err
            logged.append((line_no, number, cell_at(row, index.get("change order")).strip("` ")))
        return logged
    raise ParseError(f"the revision log at {path} carries no table with a Round column")


def fields(lines: list[str]) -> dict[str, tuple[int, str]]:
    """{normalised field name: (line_no, value)} for '- **Name:** value' lines."""
    found = {}
    for i, line in enumerate(lines):
        match = FIELD_RE.match(line)
        if match:
            name = re.sub(r"[\s–—-]+", " ", match.group("name")).strip().casefold()
            found[name] = (i + 1, match.group("value").strip())
    return found


def check_change_order(path: Path) -> list[str]:
    """Failures for one change order: absent, or missing any of the four required fields."""
    if not path.is_file():
        return [f"{path}:1: the change order this round names does not exist"]
    declared = fields(read_lines(path, "change order"))
    failures = []
    for name, label in (("requested", "Requested"), ("cost time", "Cost - time")):
        line_no, value = declared.get(name, (1, ""))
        if not value:
            failures.append(f"{path}:{line_no}: '{label}' is missing or empty")
    line_no, value = declared.get("cost rounds", (1, ""))
    if not re.fullmatch(r"\d+", value):
        failures.append(f"{path}:{line_no}: 'Cost - rounds' is not an integer: '{value}'")
    line_no, value = declared.get("approved by", (1, ""))
    date = DATE_RE.search(value)
    if date is None:
        failures.append(f"{path}:{line_no}: 'Approved by' carries no YYYY-MM-DD date")
    elif not (value[: date.start()] + value[date.end() :]).strip(" ·,.-"):
        failures.append(f"{path}:{line_no}: 'Approved by' carries a date but no name")
    return failures


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: check_revision_count.py <project-dir>")
        return 2
    project = Path(argv[1])
    if not project.is_dir():
        print(f"{project} is not a project directory")
        return 2
    log_path = project / "prototype" / "revision-log.md"
    try:
        allowed = allowance(project / "definition" / "project-brief.md")
        logged = rounds(log_path)
    except ParseError as err:
        print(err)
        return 2

    failures = []
    for line_no, number, reference in sorted(logged):
        if number <= allowed:
            continue
        if reference.casefold() in UNFILLED:
            failures.append(
                f"{log_path}:{line_no}: round {number} is past the {allowed}-round allowance "
                "and names no change order"
            )
            continue
        for failure in check_change_order(project / reference):
            failures.append(f"{failure} (round {number}, past the {allowed}-round allowance)")

    if failures:
        for failure in failures:
            print(failure)
        print(f"{len(failures)} unmet change-order requirements past the {allowed}-round allowance")
        return 1
    print(f"{len(logged)} rounds logged against an allowance of {allowed}, all accounted for")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
