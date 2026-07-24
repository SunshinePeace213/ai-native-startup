# /// script
# requires-python = ">=3.11"
# ///
"""AC10 — wireframe.md and section-briefs.md carry the locked format, delivery,
reactions, inventory, copy, packet, and sign-off clauses as parsed contract
fields."""

import re
from pathlib import Path


def contract(name):
    text = Path(f".claude/commands/soriza-design/{name}.md").read_text()
    block = re.search(r"## Rung Contract\n(.*?)(\n## |\Z)", text, re.S)
    return text, dict(re.findall(r"\*{0,2}([A-Z][\w -]+)\*{0,2}:\s*(.+)", block.group(1)))


w, wf = contract("wireframe")
for req in ["Format", "Publish", "Reactions"]:
    assert req in wf, "wireframe: missing field " + req
for clause in ["grayscale", "self-contained", "no external dependencies", "one page per screen"]:
    assert clause in wf["Format"], "wireframe Format missing: " + clause
for clause in [
    "best-effort",
    "never block",
    "org share",
    "consent",
    "public link",
    "HTML file",
    "decision-log",
]:
    assert clause in wf["Publish"], "wireframe Publish missing: " + clause
for clause in ["copy-as-prompt", "decision-log", "change request"]:
    assert clause in wf["Reactions"], "wireframe Reactions missing: " + clause
s, sf = contract("section-briefs")
for req in ["Inventory", "Copy", "Packet", "Sign-off"]:
    assert req in sf, "section-briefs: missing field " + req
for clause in ["inline", "fan-out", "large"]:
    assert clause in sf["Inventory"], "section-briefs Inventory missing: " + clause
for clause in ["slogan", "headline", "body", "copywriting"]:
    assert clause in sf["Copy"], "section-briefs Copy missing: " + clause
for item in ["brief", "sitemap-ia", "wireframes", "typography", "asset", "decision log"]:
    assert item in sf["Packet"], "Packet missing: " + item
assert "Vera" in sf["Sign-off"]
print("AC10 ok")
