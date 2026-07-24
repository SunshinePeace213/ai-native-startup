# /// script
# requires-python = ">=3.11"
# ///
"""AC7 — /soriza-design:intake carries the clause-exact Rung Contract fields,
the idempotence clause, no sweep clause, and the gitignored session marker
pattern."""

import re
import subprocess
from pathlib import Path

text = Path(".claude/commands/soriza-design/intake.md").read_text()
assert (
    "disable-model-invocation: true" in text
    and "check_intake_readiness.py" in text
    and "Stop" in text.split("---")[1]
)
block = re.search(r"## Rung Contract\n(.*?)(\n## |\Z)", text, re.S)
assert block, "no ## Rung Contract block"
fields = dict(
    re.findall(
        r"\*{0,2}(Staffer|Reads|Writes|First write|DoR gate|Refusal|Commit)\*{0,2}:\s*(.+)",
        block.group(1),
    )
)
assert set(fields) == {
    "Staffer",
    "Reads",
    "Writes",
    "First write",
    "DoR gate",
    "Refusal",
    "Commit",
}, fields
assert "Mira" in fields["Staffer"]
assert "intake-standards" in fields["Reads"], "Reads must name intake-standards.md"
assert (
    ".intake-in-progress." in fields["First write"] and "CLAUDE_SESSION_ID" in fields["First write"]
), "marker not session-scoped"
assert "intake.md" in fields["Writes"]
assert "intake.md" in fields["DoR gate"] and "definition-of-ready" in fields["DoR gate"], (
    "DoR gate must name intake.md + definition-of-ready.md"
)
assert re.search(r"refuse", fields["Refusal"], re.I) and "intake.md" in fields["Refusal"], (
    "Refusal must refuse AND name intake.md"
)
for clause in ["docs(", "Refs #", "engagement branch"]:
    assert clause in fields["Commit"], "Commit missing clause " + clause
assert re.search(r"never clobber|existing|idempotent", text, re.I), "no idempotence clause"
assert "sweep" not in text.lower(), (
    "sweep clause present — no process may touch other sessions markers"
)
ignored = (
    subprocess.run(
        ["git", "check-ignore", "projects/x/.intake-in-progress.abc123"], capture_output=True
    ).returncode
    == 0
)
assert ignored, "marker pattern not gitignored"
print("AC7 ok")
