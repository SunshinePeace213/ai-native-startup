# /// script
# requires-python = ">=3.11"
# ///
"""AC11 — git-lane.md asserts the engagement issue/branch model, per-rung
commits, exactly the two gate points with the locked reference keywords, the
no-PR-per-deliverable clause, and the evidence swap."""

import re
from pathlib import Path

text = Path(".claude/rules/soriza-design/git-lane.md").read_text()
assert re.search(r"paths:\s*\n?\s*-?\s*.projects/\*\*", text), "no paths scope"
for needle in ["docs/<N>-<client>", "gh issue develop", "docs(<client>)", "Refs #N"]:
    assert needle in text, "git-lane.md missing: " + needle
lines = text.splitlines()
gates = [line for line in lines if line.strip().startswith("- Gate:")]
assert len(gates) == 2, f"expected exactly two - Gate: bullets, got {len(gates)}"
norm = set()
for line in gates:
    assert not ("Refs #" in line and "Closes #" in line), (
        "gate bullet carries both reference keywords"
    )
    name = (
        "brief approved"
        if "brief approved" in line
        else ("packet hand-off" if "packet hand-off" in line else "?")
    )
    ref = "Refs" if "Refs #" in line else ("Closes" if "Closes #" in line else "?")
    norm.add((name, ref))
assert norm == {("brief approved", "Refs"), ("packet hand-off", "Closes")}, norm
assert re.search(
    r"(replace|instead of).{0,60}Test Evidence|Test Evidence.{0,60}(replaced|swap)", text, re.S
), "no evidence-swap clause"
for needle in ["DoR checklist", "decision-log", "sign-off"]:
    assert needle in text, "evidence swap incomplete: " + needle
assert re.search(
    r"(no|never).{0,40}PR.{0,40}(per|each).{0,20}(draft|deliverable)|only.{0,30}gate",
    text,
    re.I | re.S,
), "PR-per-deliverable not excluded"
print("AC11 ok")
