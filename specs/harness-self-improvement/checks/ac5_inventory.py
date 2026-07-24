# /// script
# requires-python = ">=3.12"
# ///
"""AC5 — every row of spec.md's ## Load-Bearing Contract Inventory holds against
the current tree: the named file exists and contains its pinned frontmatter
literal, exact-order-agnostic section presence, or clause substring. Run from
the repo root."""

import re
import sys
from pathlib import Path

SPEC = Path("specs/harness-self-improvement/spec.md")

text = SPEC.read_text()
block = re.search(r"## Load-Bearing Contract Inventory\n(.*?)\nCross-consistency", text, re.S)
assert block, "no ## Load-Bearing Contract Inventory table found"

KINDS = {"frontmatter", "sections", "clause"}

rows: list[tuple[str, str, str]] = []
failures: list[str] = []
for line in block.group(1).splitlines():
    if not line.startswith("|") or set(line) <= {"|", "-", " "}:
        continue
    cells = [c.strip().strip("`") for c in line.strip("|").split("|")]
    if len(cells) != 3:
        failures.append(f"malformed inventory row (expected 3 cells): {line!r}")
        continue
    if cells[0] == "File":
        continue
    rows.append((cells[0], cells[1], cells[2]))

assert len(rows) >= 30 or failures, (
    f"inventory parser matched only {len(rows)} rows — parsing is broken"
)

for file_path, kind, literal in rows:
    if kind not in KINDS:
        failures.append(f"{file_path}: unknown kind '{kind}' — must be one of {sorted(KINDS)}")
        continue
    path = Path(file_path)
    if not path.is_file():
        failures.append(f"{file_path}: file missing")
        continue
    body = path.read_text()
    if kind == "sections":
        for section in [s.strip() for s in literal.split(",")]:
            if f"## {section}" not in body:
                failures.append(f"{file_path}: missing section '## {section}'")
    else:  # frontmatter | clause — plan-time presence check; build-time tests parse precisely
        if literal not in body:
            failures.append(f"{file_path}: missing {kind} literal '{literal}'")

if failures:
    print("AC5 FAIL:\n" + "\n".join(f"  - {f}" for f in failures))
    sys.exit(1)
print(f"AC5 ok — {len(rows)} inventory rows verified")
