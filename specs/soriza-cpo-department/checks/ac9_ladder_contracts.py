# /// script
# requires-python = ">=3.11"
# ///
"""AC9 — the four ladder commands assert the exact rung chain, with clause-exact
DoR/refusal/commit fields per rung."""

import re
from pathlib import Path


def contract(name):
    text = Path(f".claude/commands/soriza-design/{name}.md").read_text()
    block = re.search(r"## Rung Contract\n(.*?)(\n## |\Z)", text, re.S)
    assert block, name + ": no ## Rung Contract block"
    return dict(re.findall(r"\*{0,2}([A-Z][\w -]+)\*{0,2}:\s*(.+)", block.group(1)))


chain = {
    "brief": ("Elias", "intake.md", "brief.md"),
    "sitemap": ("Ivo", "brief.md", "sitemap-ia.md"),
    "wireframe": ("Juno", "sitemap-ia.md", "wireframes/"),
    "section-briefs": ("Lior", "wireframes/", "section-briefs/"),
}
for name, (who, src, dst) in chain.items():
    f = contract(name)
    for req in ["Staffer", "Reads", "Writes", "DoR gate", "Refusal", "Commit"]:
        assert req in f, f"{name}: missing field {req}"
    assert who in f["Staffer"] and src in f["Reads"] and dst in f["Writes"], (name, f)
    assert src in f["DoR gate"], name + ": DoR gate does not name the exact predecessor artifact"
    assert re.search(r"refuse", f["Refusal"], re.I) and src in f["Refusal"], (
        name + ": refusal must refuse AND name the missing artifact"
    )
    for clause in ["docs(", "Refs #", "engagement branch"]:
        assert clause in f["Commit"], f"{name}: Commit missing clause {clause}"
f = contract("section-briefs")
assert "sitemap-ia.md" in f["Reads"] and "decision-log" in f["Reads"], (
    "section-briefs: inventory/change-request inputs missing"
)
print("AC9 ok")
