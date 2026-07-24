# /// script
# requires-python = ">=3.11"
# ///
"""AC6 — the roster has exactly one four-column row per staffer, AGENTS.md
points to the roster/rules/projects structure, and no new root markdown file
appeared. Adjust the expected root-md list only if main already tracks another
root file at merge time."""

import subprocess
from pathlib import Path

text = Path(".claude/rules/soriza/roster.md").read_text()
rows = [
    [c.strip() for c in line.strip().strip("|").split("|")]
    for line in text.splitlines()
    if line.strip().startswith("|")
]
body = [
    r
    for r in rows
    if r and r[0] and not set("".join(r)) <= set("-: ") and r[0] not in ("Name", "Staffer")
]
for who in ["Vera", "Mira", "Elias", "Ivo", "Juno", "Lior"]:
    mine = [r for r in body if r[0] == who]
    assert len(mine) == 1, who + ": expected exactly one roster row keyed by name"
    assert len(mine[0]) >= 4 and all(mine[0][:4]), who + ": all four columns must be non-empty"
agents = Path("AGENTS.md").read_text()
assert "soriza/roster.md" in agents and "soriza-design" in agents and "projects/" in agents
root_md = sorted(
    p
    for p in subprocess.run(
        ["git", "ls-files", "*.md"], capture_output=True, text=True
    ).stdout.splitlines()
    if "/" not in p
)
assert root_md == ["AGENTS.md", "CLAUDE.md"], root_md
print("AC6 ok")
