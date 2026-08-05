#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Check discovery notes against the question bank's own dimension list.

Usage: check_question_coverage.py <discovery/notes.md>

The dimensions are re-derived from the question-bank skill on every run -- every '###'
heading under its '## Dimensions' section is one dimension, and the heading text is its
name -- so adding a dimension to the skill adds one the notes must answer. This script
carries no copy of that list. The notes answer a dimension with a '## <name>' heading
whose section holds non-whitespace prose; 'N/A, because ...' is an answer too. Exit 0
pass; 1 with file:line diagnostics naming each unanswered dimension; 2 when the check
cannot run -- unreadable notes, or a skill that declares no dimensions.
"""

import re
import sys
from pathlib import Path

SKILL_PATH = (
    Path(__file__).resolve().parents[2]
    / "skills"
    / "studio-layer"
    / "studio-client-questions"
    / "SKILL.md"
)
HEADING_RE = re.compile(r"^#{1,2} ")


class ParseError(Exception):
    """The check cannot run its arithmetic on this input."""


def read_lines(path: Path, what: str) -> list[str]:
    try:
        return path.read_text(encoding="utf-8").splitlines()
    except OSError as err:
        raise ParseError(f"cannot read the {what} at {path}: {err}") from err


def dimensions(path: Path) -> list[str]:
    """Every '###' heading under the skill's '## Dimensions' section, in order."""
    names = []
    inside = False
    for line in read_lines(path, "question bank"):
        if line.startswith("## "):
            inside = line[3:].strip().casefold() == "dimensions"
        elif inside and line.startswith("### "):
            names.append(line[4:].strip())
    if not names:
        raise ParseError(
            f"the question bank at {path} declares no dimensions under '## Dimensions' -- "
            "there is nothing to hold the notes to"
        )
    return names


def sections(lines: list[str]) -> dict[str, tuple[int, str]]:
    """{casefolded '## ' heading: (line_no, body)} for the discovery notes."""
    found: dict[str, tuple[int, str]] = {}
    heads = [(i, line[3:].strip()) for i, line in enumerate(lines) if line.startswith("## ")]
    for start, name in heads:
        end = next(
            (i for i in range(start + 1, len(lines)) if HEADING_RE.match(lines[i])),
            len(lines),
        )
        found[name.casefold()] = (start + 1, "\n".join(lines[start + 1 : end]))
    return found


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: check_question_coverage.py <discovery/notes.md>")
        return 2
    notes_path = Path(argv[1])
    try:
        required = dimensions(SKILL_PATH)
        notes = sections(read_lines(notes_path, "discovery notes"))
    except ParseError as err:
        print(err)
        return 2

    failures = []
    for name in required:
        entry = notes.get(name.casefold())
        if entry is None:
            failures.append(
                f"{notes_path}:1: no '## {name}' section -- the dimension is unanswered"
            )
        elif not entry[1].strip():
            failures.append(
                f"{notes_path}:{entry[0]}: '{name}' is unanswered -- write what is "
                "true, or 'N/A, because ...'"
            )

    if failures:
        for failure in failures:
            print(failure)
        print(f"{len(failures)} of {len(required)} dimensions from {SKILL_PATH} are unanswered")
        return 1
    print(f"all {len(required)} dimensions from {SKILL_PATH} are answered")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
