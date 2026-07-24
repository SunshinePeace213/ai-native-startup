# /// script
# requires-python = ">=3.11"
# ///
"""AC1 — epic docs PR #49 merged to main referencing #43, and every child PR's
branch descends from that merge commit (child worktrees branch fresh from
origin/main at plan start, so ancestry proves the pipeline started after the
docs landed)."""

import json
import subprocess


def q(args):
    return json.loads(
        subprocess.run(["gh"] + args, capture_output=True, text=True, check=True).stdout
    )


pr = q(["pr", "view", "49", "--json", "state,body,mergedAt,baseRefName,mergeCommit"])
assert pr["state"] == "MERGED" and pr["baseRefName"] == "main" and pr["mergedAt"], pr
assert "#43" in pr["body"], "epic docs PR does not reference #43"
epic = pr["mergeCommit"]["oid"]
for n in ["44", "45", "46", "47", "48"]:
    for c in q(["issue", "view", n, "--json", "closedByPullRequestsReferences"])[
        "closedByPullRequestsReferences"
    ]:
        head = q(["pr", "view", str(c["number"]), "--json", "headRefOid"])["headRefOid"]
        st = q(["api", f"repos/{{owner}}/{{repo}}/compare/{epic}...{head}"])["status"]
        assert st in ("ahead", "identical"), (
            f"child PR #{c['number']} branch does not contain the epic docs merge "
            f"(status {st}) — its pipeline started before the docs landed"
        )
print("AC1 ok")
