#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Compute contrast ratios and tap-target sizes for a handoff token table.

Usage: check_contrast.py <handoff/tokens.md>

Every foreground/background pair gets its relative-luminance ratio computed and
compared against the Soriza project threshold its Kind selects, and every tap target
against the 24x24 CSS px minimum. The component inventory at
<project>/structure/inventory.md is the baseline: every colour token it names must
appear in at least one checked pair and every component must have a tap-target row,
so one compliant pair cannot stand in for the rest. Exit 0 pass; 1 with file:line
diagnostics naming each failing pair, target, token and component; 2 when the check
cannot run its arithmetic -- an unreadable target, a malformed hex value, an unknown
Kind, an empty pair or target table, or a missing or empty inventory.

The thresholds are Soriza project thresholds, not a conformance claim: this repo has
mirrored no accessibility specification, so the script cites none.
"""

import re
import sys
from pathlib import Path

THRESHOLDS = {"normal-text": 4.5, "large-text": 3.0, "ui-component": 3.0}
MIN_TARGET_PX = 24
THRESHOLD_NOTE = (
    "Soriza project thresholds: 4.5:1 normal text, 3:1 large text and UI components, "
    "24x24 CSS px minimum tap target."
)

DELIMITER_RE = re.compile(r":?-{3,}:?")
HEX_RE = re.compile(r"#([0-9A-Fa-f]{6})(?![0-9A-Fa-f])")


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


def find_table(lines: list[str], required: tuple[str, ...], path: Path, what: str):
    """The first table carrying every required column, as (index, rows)."""
    for header, rows in tables(lines):
        index = {name.casefold(): i for i, name in enumerate(header)}
        if all(name in index for name in required):
            if not rows:
                raise ParseError(f"the {what} in {path} is empty -- nothing to check")
            return index, rows
    raise ParseError(f"{path} carries no {what} with columns {', '.join(required)}")


def cell_at(row: list[str], index: int | None) -> str:
    return row[index] if index is not None and index < len(row) else ""


def hex_value(cell: str, path: Path, line_no: int) -> str:
    """The #RRGGBB value a Foreground or Background cell carries, however it is labelled."""
    match = HEX_RE.search(cell)
    if match is None:
        plain = cell.replace("`", "").strip()
        raise ParseError(f"{path}:{line_no}: '{plain}' is not a #RRGGBB colour value")
    return "#" + match.group(1).upper()


def rgb(value: str) -> tuple[int, int, int]:
    return tuple(int(value[i : i + 2], 16) for i in (1, 3, 5))


def channel(value: float) -> float:
    """An sRGB channel linearised to its light-intensity value."""
    return value / 12.92 if value <= 0.03928 else ((value + 0.055) / 1.055) ** 2.4


def luminance(colour: tuple[int, int, int]) -> float:
    red, green, blue = (channel(part / 255) for part in colour)
    return 0.2126 * red + 0.7152 * green + 0.0722 * blue


def contrast_ratio(fore: tuple[int, int, int], back: tuple[int, int, int]) -> float:
    lighter, darker = sorted((luminance(fore), luminance(back)), reverse=True)
    return (lighter + 0.05) / (darker + 0.05)


def read_inventory(path: Path) -> tuple[list[tuple[int, str]], list[tuple[int, str]]]:
    """(components, colour tokens) of the client-signed inventory, each with its line."""
    lines = read_lines(path, "component inventory")
    for header, rows in tables(lines):
        index = {name.casefold(): i for i, name in enumerate(header)}
        if "component" not in index:
            continue
        token_column = next((i for name, i in index.items() if "token" in name), None)
        if token_column is None:
            raise ParseError(f"the component inventory at {path} declares no colour-token column")
        components, tokens = [], []
        for line_no, row in rows:
            component = cell_at(row, index["component"]).strip("` ")
            if not component:
                continue
            components.append((line_no, component))
            for token in cell_at(row, token_column).split(","):
                token = token.strip("` ")
                if token:
                    tokens.append((line_no, token))
        if components:
            return components, tokens
    raise ParseError(
        f"the component inventory at {path} names no components -- without that baseline "
        "one compliant pair would stand in for the whole design"
    )


def check_pairs(path: Path, lines: list[str]) -> tuple[list[str], list[str]]:
    """(failures, row texts) for the colour-pair table."""
    index, rows = find_table(lines, ("foreground", "background", "kind"), path, "colour-pair table")
    failures, texts = [], []
    for line_no, row in rows:
        texts.append(" ".join(row))
        kind = cell_at(row, index["kind"]).strip("` ").casefold()
        if kind not in THRESHOLDS:
            raise ParseError(
                f"{path}:{line_no}: '{kind}' is not a known Kind "
                f"({', '.join(sorted(THRESHOLDS))}), so no threshold applies"
            )
        fore = hex_value(cell_at(row, index["foreground"]), path, line_no)
        back = hex_value(cell_at(row, index["background"]), path, line_no)
        ratio = contrast_ratio(rgb(fore), rgb(back))
        if ratio < THRESHOLDS[kind]:
            failures.append(
                f"{path}:{line_no}: {fore} on {back} is {ratio:.2f}:1, below the "
                f"{THRESHOLDS[kind]}:1 Soriza project threshold for {kind}"
            )
    return failures, texts


def check_targets(path: Path, lines: list[str]) -> tuple[list[str], set[str]]:
    """(failures, target names) for the tap-target table."""
    index, rows = find_table(lines, ("target", "width (px)", "height (px)"), path, "target table")
    failures, named = [], set()
    for line_no, row in rows:
        name = cell_at(row, index["target"]).strip("` ")
        named.add(name.casefold())
        try:
            width = int(cell_at(row, index["width (px)"]).strip("` "))
            height = int(cell_at(row, index["height (px)"]).strip("` "))
        except ValueError as err:
            raise ParseError(f"{path}:{line_no}: {name} declares a non-integer size") from err
        if width < MIN_TARGET_PX or height < MIN_TARGET_PX:
            failures.append(
                f"{path}:{line_no}: {name} is {width}x{height} px, below the "
                f"{MIN_TARGET_PX}x{MIN_TARGET_PX} px Soriza project minimum tap target"
            )
    return failures, named


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: check_contrast.py <handoff/tokens.md>")
        return 2
    target = Path(argv[1])
    inventory_path = target.resolve().parent.parent / "structure" / "inventory.md"
    try:
        components, tokens = read_inventory(inventory_path)
        lines = read_lines(target, "token table")
        pair_failures, pair_texts = check_pairs(target, lines)
        target_failures, named = check_targets(target, lines)
    except ParseError as err:
        print(err)
        return 2

    failures = pair_failures + target_failures
    for line_no, token in tokens:
        pattern = re.compile(re.escape(token) + r"(?![-\w])")
        if not any(pattern.search(text) for text in pair_texts):
            failures.append(
                f"{inventory_path}:{line_no}: colour token {token} appears in no checked "
                "foreground/background pair"
            )
    for line_no, component in components:
        if component.casefold() not in named:
            failures.append(f"{inventory_path}:{line_no}: {component} has no tap-target row")

    print(THRESHOLD_NOTE)
    if failures:
        for failure in failures:
            print(failure)
        print(f"{len(failures)} pairs, targets or inventory rows fail the Soriza project checks")
        return 1
    print(f"every pair and target meets the thresholds and covers {inventory_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
