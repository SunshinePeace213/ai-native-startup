# /// script
# requires-python = ">=3.11"
# ///
"""AC5 — the soriza-design rules family exists, projects/**-scoped, with real
starter content and no stub markers."""

import re
from pathlib import Path

fam = Path(".claude/rules/soriza-design")
names = [
    "client-communication",
    "intake-standards",
    "definition-of-ready",
    "brief-format",
    "section-anatomy",
    "copywriting",
    "lessons",
]
for n in names:
    text = (fam / (n + ".md")).read_text()
    assert re.search(r"paths:\s*\n?\s*-?\s*.projects/\*\*", text), n + ": no paths scope"
    assert len(text.splitlines()) >= 15, n + ": suspiciously thin"
    assert not re.search(r"TBD|TODO|fill me|placeholder", text, re.I), n + ": stub marker"
print("AC5 ok")
