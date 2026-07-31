#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Count the filled cells of a handoff states matrix against the signed inventory.

Usage: check_states_matrix.py <handoff/states-matrix.md>

The component inventory at <project>/structure/inventory.md is the baseline: every
component x breakpoint pair it names needs a matrix row, and every row needs all six
of hover, focus, disabled, loading, empty and error filled. Exit 0 pass; 1 with
file:line diagnostics naming each missing pair and each unfilled cell; 2 when the
check cannot run its arithmetic -- an unreadable target, an unparseable table, or a
missing or empty inventory, without which a one-component matrix would pass a
ten-component design.
"""

import re
import sys
from pathlib import Path

STATES = ("hover", "focus", "disabled", "loading", "empty", "error")
UNFILLED = {"", "-", "tbd"}
DELIMITER_RE = re.compile(r":?-{3,}:?")


class ParseError(Exception):
    """The check cannot run its arithmetic on this input."""


def cells(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def is_delimiter(row: list[str]) -> bool:
    return bool(row) and all(DELIMITER_RE.fullmatch(cell) for cell in row)


def tables(lines: list[str], start: int = 0, end: int | None = None):
    """(header, rows) per pipe table in lines[start:end]; rows are (line_no, cells)."""
    end = len(lines) if end is None else end
    found = []
    i = start
    while i < end:
        head = lines[i].lstrip()
        if head.startswith("|") and i + 1 < end and is_delimiter(cells(lines[i + 1])):
            header = cells(lines[i])
            rows = []
            j = i + 2
            while j < end and lines[j].lstrip().startswith("|"):
                rows.append((j + 1, cells(lines[j])))
                j += 1
            found.append((header, rows))
            i = j
        else:
            i += 1
    return found


def cell_at(row: list[str], index: int | None) -> str:
    """The cell at index, or empty when the column is absent or the row is short."""
    return row[index] if index is not None and index < len(row) else ""


def read_lines(path: Path, what: str) -> list[str]:
    try:
        return path.read_text(encoding="utf-8").splitlines()
    except OSError as err:
        raise ParseError(f"cannot read the {what} at {path}: {err}") from err


def read_inventory(path: Path) -> list[tuple[int, str, list[str]]]:
    """(line_no, component, breakpoints) per row of the client-signed inventory."""
    lines = read_lines(path, "component inventory")
    for header, rows in tables(lines):
        index = {name.casefold(): i for i, name in enumerate(header)}
        if "component" not in index:
            continue
        if "breakpoints" not in index:
            raise ParseError(f"the component inventory at {path} declares no Breakpoints column")
        entries = []
        for line_no, row in rows:
            component = row[index["component"]].strip("` ")
            breakpoints = [
                bp.strip("` ") for bp in row[index["breakpoints"]].split(",") if bp.strip("` ")
            ]
            if component:
                entries.append((line_no, component, breakpoints))
        if entries:
            return entries
    raise ParseError(
        f"the component inventory at {path} names no components -- without that baseline "
        "the matrix would only be measured against itself"
    )


def read_matrix(path: Path) -> dict[tuple[str, str], tuple[int, str, str, dict[str, str]]]:
    """{casefolded (component, breakpoint): (line_no, component, breakpoint, states)}."""
    lines = read_lines(path, "states matrix")
    matrix: dict[tuple[str, str], tuple[int, str, str, dict[str, str]]] = {}
    heads = [(i, line[4:].strip()) for i, line in enumerate(lines) if line.startswith("### ")]
    for n, (start, breakpoint_name) in enumerate(heads):
        end = heads[n + 1][0] if n + 1 < len(heads) else len(lines)
        for header, rows in tables(lines, start + 1, end):
            index = {name.casefold(): i for i, name in enumerate(header)}
            if "component" not in index:
                continue
            for line_no, row in rows:
                component = row[index["component"]].strip("` ")
                if not component:
                    continue
                states = {state: cell_at(row, index.get(state)) for state in STATES}
                key = (component.casefold(), breakpoint_name.casefold())
                matrix[key] = (line_no, component, breakpoint_name, states)
    return matrix


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: check_states_matrix.py <handoff/states-matrix.md>")
        return 2
    target = Path(argv[1])
    inventory_path = target.resolve().parent.parent / "structure" / "inventory.md"
    try:
        inventory = read_inventory(inventory_path)
        matrix = read_matrix(target)
    except ParseError as err:
        print(err)
        return 2

    failures: list[str] = []
    for line_no, component, breakpoints in inventory:
        if not breakpoints:
            failures.append(
                f"{inventory_path}:{line_no}: {component} declares no breakpoints to specify"
            )
        for breakpoint_name in breakpoints:
            entry = matrix.get((component.casefold(), breakpoint_name.casefold()))
            if entry is None:
                failures.append(
                    f"{inventory_path}:{line_no}: no matrix row for {component} "
                    f"at breakpoint {breakpoint_name}"
                )

    for _key, (line_no, component, breakpoint_name, states) in sorted(matrix.items()):
        for state in STATES:
            if states[state].strip("` ").casefold() in UNFILLED:
                failures.append(
                    f"{target}:{line_no}: {component} at {breakpoint_name} "
                    f"leaves '{state}' unfilled"
                )

    if failures:
        for failure in failures:
            print(failure)
        print(f"{len(failures)} unmet cells or pairs in the states matrix")
        return 1
    print(f"states matrix covers every component x breakpoint in {inventory_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
