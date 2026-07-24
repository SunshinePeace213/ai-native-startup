# /// script
# requires-python = ">=3.11"
# ///
"""AC12 — every child issue #44–#48 is closed with at least one closing PR and
epic #43's checklist is fully ticked."""

import json
import re
import subprocess


def q(args):
    return json.loads(
        subprocess.run(["gh"] + args, capture_output=True, text=True, check=True).stdout
    )


body = q(["issue", "view", "43", "--json", "body"])["body"]
for n in ["44", "45", "46", "47", "48"]:
    assert re.search(rf"- \[x\] #{n}\b", body), f"epic checkbox for #{n} not ticked"
    ch = q(["issue", "view", n, "--json", "state,closedByPullRequestsReferences"])
    assert ch["state"] == "CLOSED", f"#{n} is not closed"
    assert len(ch["closedByPullRequestsReferences"]) >= 1, f"#{n} has no closing PR"
print("AC12 ok")
