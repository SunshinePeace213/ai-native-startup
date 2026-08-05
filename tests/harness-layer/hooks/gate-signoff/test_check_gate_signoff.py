"""Contract tests for the studio sign-off Stop gate (check_gate_signoff.py).

The gate is command-scoped -- registered by /studio-layer:p2-definition,
p3-structure, p4-art-direction and p6-handoff, each passing its own phase token
as argv[1] -- so it must be invisible in any project with no clients/ dir, and
it must gate the phase it was given rather than whichever phase folder happens
to be newest. A client project holds all eight phase folders at once, which is
why mtime inference was rejected.

Exit 2 must name the exact missing field, row or document, because stderr is
the only repair instruction the agent gets. Everything unresolvable -- an
unknown phase token, an unidentifiable project, malformed stdin -- exits 0 per
the repo's fail-open hook contract.

p4 is the pure sign-off gate (no extra document), so the general sign-off cases
run against it; the per-phase extras get their own cases.
"""

import hashlib
import json
import os
from pathlib import Path

import pytest

INVENTORY = "structure/inventory.md"
TRIAGE = "definition/cold-designer-triage.md"
QA_REPORT = "handoff/qa-report.md"

# The deliverables each gated phase's sign-off table must carry, stated here
# rather than imported from the hook: deriving them from the code under test
# would make a wrong set unfalsifiable.
REQUIRED = {
    "p2": ("definition/project-brief.md", "definition/sitemap.md"),
    "p3": ("structure/wireframes.md", INVENTORY),
    "p4": ("art-direction/rationale.md", "art-direction/style-tile.md"),
    "p6": ("handoff/pack.md", "handoff/states-matrix.md", "handoff/tokens.md"),
}

INVENTORY_BODY = (
    "| Component | Breakpoints | Colour tokens used |\n"
    "| --- | --- | --- |\n"
    "| PrimaryButton | mobile, desktop | `--accent`, `--on-accent` |\n"
)


def sha256_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_artifact(project: Path, rel: str, body: str | None = None) -> str:
    """A client document, returning the hash a sign-off row would record for it."""
    if body is None:
        body = INVENTORY_BODY if rel == INVENTORY else "an approved document\n"
    path = project / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body)
    return sha256_of(path)


def write_signoff(
    project: Path,
    phase: str,
    *,
    approver: str = "Jordan Reyes, Head of Marketing, Acme Co.",
    date: str = "2026-07-31",
    artifacts: list[tuple[str, str]] | None = None,
) -> Path:
    """A sign-off in the documented shape; by default it approves exactly the
    phase's required deliverables, which is the state that opens the gate."""
    if artifacts is None:
        artifacts = [(rel, write_artifact(project, rel)) for rel in REQUIRED[phase]]
    rows = "".join(f"| `{path}` | `{sha}` |\n" for path, sha in artifacts)
    signoff = project / "sign-off" / f"{phase}.md"
    signoff.parent.mkdir(parents=True, exist_ok=True)
    signoff.write_text(
        f"# Sign-off: {phase.upper()}\n\n"
        f"- **Approver:** {approver}\n"
        f"- **Date:** {date}\n\n"
        "## Approved artifacts\n\n"
        "| Artifact | SHA-256 |\n"
        "| --- | --- |\n" + rows
    )
    return signoff


def write_triage(project: Path, dispositions=("acceptable variance — tiering is a P4 call",)):
    rows = "".join(
        f"| Section {i} | three tiers | two tiers plus contact | {disposition} |\n"
        for i, disposition in enumerate(dispositions)
    )
    path = project / TRIAGE
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "# Cold-designer triage\n\n"
        "| Section | Cold designer produced | Signed sitemap says | Disposition |\n"
        "| --- | --- | --- | --- |\n" + rows
    )
    return path


def write_qa_report(project: Path, findings=(("Empty state has no copy", "blocking", "resolved"),)):
    rows = "".join(
        f"| {finding} | {severity} | {status} | states-matrix.md row 4 |\n"
        for finding, severity, status in findings
    )
    path = project / QA_REPORT
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "# Design QA report\n\n"
        "| Finding | Severity | Status | Evidence |\n"
        "| --- | --- | --- | --- |\n" + rows
    )
    return path


def sign_p3_over_inventory(project: Path, body: str = INVENTORY_BODY) -> str:
    """P3 signed with the component inventory in its artifact table -- the state
    p6 re-verifies the inventory against."""
    sha = write_artifact(project, INVENTORY, body)
    write_signoff(
        project,
        "p3",
        artifacts=[
            (rel, sha if rel == INVENTORY else write_artifact(project, rel))
            for rel in REQUIRED["p3"]
        ],
    )
    return sha


def prepare_phase(project: Path, phase: str) -> None:
    """Every document the phase's gate reads apart from its own sign-off, so a
    case about the sign-off table is not confounded by a missing side document."""
    for rel in REQUIRED[phase]:
        write_artifact(project, rel)
    if phase == "p2":
        write_triage(project)
    elif phase == "p6":
        sign_p3_over_inventory(project)
        write_qa_report(project)


def make_p6_ready(project: Path) -> None:
    """Everything the p6 gate needs: its own sign-off, a clean QA report, and a
    P3 signature over the inventory exactly as it stands now."""
    sign_p3_over_inventory(project)
    write_signoff(project, "p6")
    write_qa_report(project)


@pytest.fixture
def project(tmp_path):
    """One client project under tmp_path, which stands in as the project root."""
    path = tmp_path / "clients" / "acme" / "site"
    path.mkdir(parents=True)
    return path


def gate(run_hook, root: Path, phase: str | None, *, cwd: Path | None = None, reentry=False):
    payload = json.dumps(
        {
            "hook_event_name": "Stop",
            "cwd": str(cwd if cwd is not None else root),
            "stop_hook_active": reentry,
        }
    )
    return run_hook(
        "check_gate_signoff.py",
        payload,
        args=() if phase is None else (phase,),
        env_overrides={"CLAUDE_PROJECT_DIR": str(root)},
    )


def test_missing_signoff_file_blocks(tmp_path, project, run_hook):
    """The common first-run case: no signature yet. It has to read as an
    instruction naming the expected path, not as a crash."""
    proc = gate(run_hook, tmp_path, "p4")
    assert proc.returncode == 2
    assert "sign-off/p4.md: MISSING FILE" in proc.stderr
    assert proc.stdout == ""


def test_empty_approver_blocks(tmp_path, project, run_hook):
    """A sign-off with no approver names nobody: an unattributed approval is not
    an approval, and blank reads identically to missing."""
    write_signoff(project, "p4", approver="")
    proc = gate(run_hook, tmp_path, "p4")
    assert proc.returncode == 2
    assert "'Approver' is empty or still a template placeholder" in proc.stderr


def test_placeholder_date_blocks(tmp_path, project, run_hook):
    """An unreplaced template slot renders as prose in the file and would sail
    past a presence-only check, so the leftover must count as missing."""
    write_signoff(project, "p4", date="<date the client signed>")
    proc = gate(run_hook, tmp_path, "p4")
    assert proc.returncode == 2
    assert "'Date' is empty or still a template placeholder" in proc.stderr


def test_empty_artifact_table_blocks(tmp_path, project, run_hook):
    """A signature over nothing approves nothing -- the table must carry at
    least one row for the phase to have been signed."""
    write_signoff(project, "p4", artifacts=[])
    proc = gate(run_hook, tmp_path, "p4")
    assert proc.returncode == 2
    assert "the artifact table has no rows" in proc.stderr


def test_artifact_path_that_does_not_exist_blocks(tmp_path, project, run_hook):
    """An approval of a deleted or renamed document is not an approval; the row
    is named so the repair is unambiguous."""
    write_signoff(project, "p4", artifacts=[("art-direction/gone.md", "a" * 64)])
    proc = gate(run_hook, tmp_path, "p4")
    assert proc.returncode == 2
    assert "'art-direction/gone.md' does not exist" in proc.stderr


def test_sha_mismatch_blocks(tmp_path, project, run_hook):
    """The client approved something, and it was not this file. The hash is of
    file content, never a git SHA -- clients/ is gitignored."""
    rel = "art-direction/direction.md"
    write_signoff(project, "p4", artifacts=[(rel, write_artifact(project, rel))])
    (project / rel).write_text("edited after the client signed\n")
    proc = gate(run_hook, tmp_path, "p4")
    assert proc.returncode == 2
    assert f"'{rel}' no longer matches what was approved" in proc.stderr


def test_absolute_artifact_path_blocks(tmp_path, project, run_hook):
    """A signature covers the engagement it names. An absolute path would let any
    file on the machine carry it -- and it hashes correctly, so the row would
    otherwise sail through the whole check."""
    outside = tmp_path / "somebody-elses.md"
    outside.write_text("a document this client never saw\n")
    write_signoff(project, "p4", artifacts=[(str(outside), sha256_of(outside))])
    proc = gate(run_hook, tmp_path, "p4")
    assert proc.returncode == 2
    assert "resolves outside the project" in proc.stderr


def test_parent_traversal_artifact_path_blocks(tmp_path, project, run_hook):
    """`../` climbs out of the project while still reading as a relative path, so
    a neighbouring engagement's approved document could close this one's gate."""
    outside = project.parent / "other-project-doc.md"
    outside.write_text("approved on a different engagement\n")
    write_signoff(project, "p4", artifacts=[("../other-project-doc.md", sha256_of(outside))])
    proc = gate(run_hook, tmp_path, "p4")
    assert proc.returncode == 2
    assert "resolves outside the project" in proc.stderr


def test_symlinked_artifact_outside_the_project_blocks(tmp_path, project, run_hook):
    """The path stays inside the project and the hash matches, so only resolving
    the link catches it: containment has to be judged on the real target."""
    outside = tmp_path / "template-rationale.md"
    outside.write_text("a boilerplate rationale kept outside the project\n")
    link = project / "art-direction" / "borrowed.md"
    link.parent.mkdir(parents=True, exist_ok=True)
    link.symlink_to(outside)
    write_signoff(project, "p4", artifacts=[("art-direction/borrowed.md", sha256_of(outside))])
    proc = gate(run_hook, tmp_path, "p4")
    assert proc.returncode == 2
    assert "resolves outside the project" in proc.stderr


def test_complete_signoff_allows(tmp_path, project, run_hook):
    """The allow path: a filled Approver and Date and every artifact row
    resolving to a file that still hashes to what was signed."""
    write_signoff(project, "p4")
    proc = gate(run_hook, tmp_path, "p4")
    assert proc.returncode == 0
    assert proc.stderr == ""


@pytest.mark.parametrize(
    "phase, dropped", [(phase, rel) for phase, rels in REQUIRED.items() for rel in rels]
)
def test_signoff_missing_a_required_artifact_blocks(tmp_path, project, run_hook, phase, dropped):
    """Hashing whatever rows the table happens to carry proves only that somebody
    signed something. Each hard gate exists to get its own deliverables approved,
    so a sign-off that omits one has not closed the phase -- P2 without its brief
    or sitemap, P3 without wireframes, P4 without the picked direction, P6
    without the handoff pack."""
    prepare_phase(project, phase)
    kept = [(rel, write_artifact(project, rel)) for rel in REQUIRED[phase] if rel != dropped]
    write_signoff(project, phase, artifacts=kept)
    proc = gate(run_hook, tmp_path, phase)
    assert proc.returncode == 2
    assert f"does not list {dropped}" in proc.stderr


def test_no_clients_dir_allows_silently(tmp_path, run_hook):
    """The gate rides four studio commands but fires in whatever session runs
    them; with no client work at all it must be invisible, exactly as the spec
    gate is in a project with no specs/."""
    proc = gate(run_hook, tmp_path, "p4")
    assert proc.returncode == 0
    assert proc.stderr == ""


def test_unknown_phase_argument_fails_open(tmp_path, project, run_hook):
    """A missing or unrecognized phase token is a registration mistake, and the
    repo's hook contract fails configuration failures open -- test_wiring.py
    catches them at CI time rather than mid-engagement."""
    for phase in (None, "p5", "definition"):
        proc = gate(run_hook, tmp_path, phase)
        assert proc.returncode == 0, phase
        assert proc.stderr == "", phase


def test_phase_comes_from_argv_not_mtime(tmp_path, project, run_hook):
    """A client project holds all eight phase folders at once, so a newer
    unsigned phase folder must not change the verdict for the phase actually
    being closed -- inference from mtime would gate the wrong phase."""
    write_signoff(project, "p4")
    (project / "handoff").mkdir()
    (project / "handoff" / "pack.md").write_text("later work\n")
    os.utime(project / "sign-off" / "p4.md", (1_000_000_000, 1_000_000_000))
    os.utime(project / "handoff", (2_000_000_000, 2_000_000_000))

    assert gate(run_hook, tmp_path, "p4").returncode == 0
    later = gate(run_hook, tmp_path, "p6")
    assert later.returncode == 2
    assert "sign-off/p6.md: MISSING FILE" in later.stderr


def test_cwd_selects_the_project_when_two_exist(tmp_path, project, run_hook):
    """A studio holds several engagements at once. The payload's cwd is the
    first rule in the targeting order, so the gate follows the session into the
    project it is working in rather than the one that happens to be signed."""
    other = tmp_path / "clients" / "globex" / "app"
    other.mkdir(parents=True)
    write_signoff(project, "p4")

    blocked = gate(run_hook, tmp_path, "p4", cwd=other / "art-direction")
    assert blocked.returncode == 2
    assert "sign-off/p4.md: MISSING FILE" in blocked.stderr
    assert "clients/globex/app" in blocked.stderr

    allowed = gate(run_hook, tmp_path, "p4", cwd=project)
    assert allowed.returncode == 0


def test_two_projects_and_outside_cwd_fails_open(tmp_path, project, run_hook):
    """A gate that cannot identify its target must not guess: gating the wrong
    engagement is worse than not gating, so it exits 0 and says why."""
    (tmp_path / "clients" / "globex" / "app").mkdir(parents=True)
    proc = gate(run_hook, tmp_path, "p4")
    assert proc.returncode == 0
    assert "2 client projects" in proc.stderr


def test_project_without_signoff_dir_still_blocks(tmp_path, project, run_hook):
    """A project is any directory two levels under clients/, never one that has
    a sign-off/ folder: a brand-new unsigned project is precisely what the gate
    must block, and defining it away would fail open on the first hard gate."""
    assert not (project / "sign-off").exists()
    proc = gate(run_hook, tmp_path, "p4")
    assert proc.returncode == 2
    assert "clients/acme/site" in proc.stderr


def test_stop_hook_active_allows_with_warning(tmp_path, project, run_hook):
    """A client signature will not appear because Claude tried again, and Claude
    Code force-ends the turn after 8 consecutive blocks -- so re-blocking burns
    the turn and lands in the same place. The gate stays visibly unresolved."""
    first = gate(run_hook, tmp_path, "p4", reentry=False)
    assert first.returncode == 2

    reentry = gate(run_hook, tmp_path, "p4", reentry=True)
    assert reentry.returncode == 0
    assert "the p4 gate for clients/acme/site is still unsigned" in reentry.stderr
    assert "sign-off/p4.md: MISSING FILE" in reentry.stderr


def test_malformed_stdin_fails_open(tmp_path, project, run_hook):
    """Unparseable stdin is a plumbing failure, not an agent-fixable finding --
    the contract fails those open rather than wedging the session."""
    for payload in ("", "not json", "[]"):
        proc = run_hook(
            "check_gate_signoff.py",
            payload,
            args=("p4",),
            env_overrides={"CLAUDE_PROJECT_DIR": str(tmp_path)},
        )
        assert proc.returncode == 0, payload


def test_p2_missing_triage_blocks(tmp_path, project, run_hook):
    """The cold-designer test only exists as a mechanism if the phase cannot
    close without its triage document."""
    write_signoff(project, "p2")
    proc = gate(run_hook, tmp_path, "p2")
    assert proc.returncode == 2
    assert f"{TRIAGE}: MISSING FILE" in proc.stderr


def test_p2_untriaged_row_blocks(tmp_path, project, run_hook):
    """A row nobody dispositioned is a difference nobody decided about -- the
    document exists but the triage did not happen."""
    write_signoff(project, "p2")
    write_triage(project, dispositions=("acceptable variance — pricing is a P4 call", "TBD"))
    proc = gate(run_hook, tmp_path, "p2")
    assert proc.returncode == 2
    assert "is untriaged" in proc.stderr
    assert "Section 1" in proc.stderr


def test_p2_fully_triaged_allows(tmp_path, project, run_hook):
    """The diff itself is advisory and never gates: two competent designers
    given one brief produce different section plans, so a zero-diff gate would
    never open. Every row carrying a disposition is the bar."""
    write_signoff(project, "p2")
    write_triage(
        project,
        dispositions=("brief unclear — amended", "acceptable variance — tiering is a P4 call"),
    )
    proc = gate(run_hook, tmp_path, "p2")
    assert proc.returncode == 0
    assert proc.stderr == ""


def test_p3_p4_p6_do_not_require_triage(tmp_path, project, run_hook):
    """The cold-designer test belongs to P2 alone; demanding its document at the
    other gates would block three phases on a document they never produce."""
    write_signoff(project, "p4")
    make_p6_ready(project)
    assert not (project / TRIAGE).exists()
    for phase in ("p3", "p4", "p6"):
        proc = gate(run_hook, tmp_path, phase)
        assert proc.returncode == 0, f"{phase}: {proc.stderr}"


def test_p3_missing_inventory_blocks(tmp_path, project, run_hook):
    """The inventory is what P6's matrix and contrast checks quantify over. If
    P3 could close without it, P6 would author the very list it is then measured
    against -- a one-component matrix agreeing with a one-component list."""
    write_signoff(project, "p3")
    (project / INVENTORY).unlink()
    proc = gate(run_hook, tmp_path, "p3")
    assert proc.returncode == 2
    assert f"{INVENTORY}: MISSING FILE" in proc.stderr


def test_p3_empty_inventory_blocks(tmp_path, project, run_hook):
    """An empty baseline is not a pass: an inventory with no components would
    let every P6 check quantify over nothing and succeed vacuously."""
    sha = write_artifact(project, INVENTORY, "")
    write_signoff(project, "p3", artifacts=[(INVENTORY, sha)])
    proc = gate(run_hook, tmp_path, "p3")
    assert proc.returncode == 2
    assert f"{INVENTORY}: is empty" in proc.stderr


def test_p3_inventory_absent_from_signoff_table_blocks(tmp_path, project, run_hook):
    """Existing is not the same as approved. The inventory must be a client-signed
    P3 artifact, because a hash the client never saw pins nothing at P6."""
    wireframes = "structure/wireframes.md"
    write_artifact(project, INVENTORY, INVENTORY_BODY)
    write_signoff(project, "p3", artifacts=[(wireframes, write_artifact(project, wireframes))])
    proc = gate(run_hook, tmp_path, "p3")
    assert proc.returncode == 2
    assert f"does not list {INVENTORY}" in proc.stderr


def test_p3_signed_inventory_allows(tmp_path, project, run_hook):
    """The allow path: a non-empty inventory listed in P3's own artifact table,
    hashing to what the client approved."""
    sign_p3_over_inventory(project)
    proc = gate(run_hook, tmp_path, "p3")
    assert proc.returncode == 0
    assert proc.stderr == ""


def test_p6_inventory_mutated_after_p3_signoff_blocks(tmp_path, project, run_hook):
    """The case a P3-only check misses entirely: deleting rows between P3 and P6
    shrinks the denominator P6 is measured against while the P3 signature sits
    untouched in a file nobody re-reads. P6 re-hashes it instead of trusting it."""
    make_p6_ready(project)
    (project / INVENTORY).write_text(
        "| Component | Breakpoints | Colour tokens used |\n| --- | --- | --- |\n"
    )
    proc = gate(run_hook, tmp_path, "p6")
    assert proc.returncode == 2
    assert f"{INVENTORY}: changed since the P3 sign-off" in proc.stderr


def test_p6_missing_from_p3_signoff_blocks(tmp_path, project, run_hook):
    """P6 has nothing to re-verify against when P3 never listed the inventory,
    which is the same defect as a mutation: the denominator is unsigned."""
    wireframes = "structure/wireframes.md"
    write_artifact(project, INVENTORY, INVENTORY_BODY)
    write_signoff(project, "p3", artifacts=[(wireframes, write_artifact(project, wireframes))])
    write_signoff(project, "p6")
    write_qa_report(project)
    proc = gate(run_hook, tmp_path, "p6")
    assert proc.returncode == 2
    assert f"never listed {INVENTORY}" in proc.stderr


def test_p6_inventory_matching_p3_sha_allows(tmp_path, project, run_hook):
    """The allow path: the inventory at P6 is byte-for-byte the one the client
    signed at P3, so the design is measured against the approved list."""
    make_p6_ready(project)
    proc = gate(run_hook, tmp_path, "p6")
    assert proc.returncode == 0
    assert proc.stderr == ""


def test_p6_open_blocking_qa_finding_blocks(tmp_path, project, run_hook):
    """studio-design-qa blocks handoff as a mechanism rather than a claim: its
    report is what the gate reads, so an unresolved blocking finding keeps the
    phase open."""
    make_p6_ready(project)
    write_qa_report(
        project, findings=(("SearchResults empty state has no copy", "blocking", "open"),)
    )
    proc = gate(run_hook, tmp_path, "p6")
    assert proc.returncode == 2
    assert "blocking finding still open — SearchResults empty state has no copy" in proc.stderr


def test_p6_all_blocking_findings_resolved_allows(tmp_path, project, run_hook):
    """Resolving the findings is what opens the gate -- deleting the report is
    not, since a missing report blocks too."""
    make_p6_ready(project)
    write_qa_report(
        project,
        findings=(
            ("SearchResults empty state has no copy", "blocking", "resolved"),
            ("Focus ring is faint on the accent surface", "blocking", "resolved"),
        ),
    )
    proc = gate(run_hook, tmp_path, "p6")
    assert proc.returncode == 0
    assert proc.stderr == ""


def test_p6_unreadable_qa_status_blocks(tmp_path, project, run_hook):
    """A status outside the documented enum is a finding nobody closed. Matching
    only the exact pair blocking/open would read `blocking | TBD` as resolved and
    hand over an engagement the QA agent said was not ready."""
    make_p6_ready(project)
    write_qa_report(project, findings=(("Focus ring is invisible on accent", "blocking", "TBD"),))
    proc = gate(run_hook, tmp_path, "p6")
    assert proc.returncode == 2
    assert "unreadable Status 'tbd'" in proc.stderr


def test_p6_misspelled_qa_severity_blocks(tmp_path, project, run_hook):
    """`blocker` is what a writer types for `blocking`, and an enum matched by
    equality silently downgrades the typo to something the gate ignores."""
    make_p6_ready(project)
    write_qa_report(project, findings=(("Error copy says 'Error'", "blocker", "open"),))
    proc = gate(run_hook, tmp_path, "p6")
    assert proc.returncode == 2
    assert "unreadable Severity 'blocker'" in proc.stderr


def test_p6_blank_qa_cell_blocks(tmp_path, project, run_hook):
    """An empty cell is the absence of a judgment, not a resolution -- a row the
    gate cannot read must never be the reason the gate opens."""
    make_p6_ready(project)
    write_qa_report(project, findings=(("Empty state has no copy", "blocking", ""),))
    proc = gate(run_hook, tmp_path, "p6")
    assert proc.returncode == 2
    assert "unreadable Status '(blank)'" in proc.stderr


def test_p6_advisory_finding_does_not_block(tmp_path, project, run_hook):
    """Advisory findings are judgment the QA agent records for the next project;
    blocking on them would make every open note a gate and teach the agent to
    stop writing them."""
    make_p6_ready(project)
    write_qa_report(project, findings=(("Consider a lighter caption weight", "advisory", "open"),))
    proc = gate(run_hook, tmp_path, "p6")
    assert proc.returncode == 0
    assert proc.stderr == ""


def test_p6_missing_qa_report_blocks(tmp_path, project, run_hook):
    """No report is not a clean report: without it the handoff would close with
    nobody having looked at the states, focus order, or error copy."""
    make_p6_ready(project)
    (project / QA_REPORT).unlink()
    proc = gate(run_hook, tmp_path, "p6")
    assert proc.returncode == 2
    assert f"{QA_REPORT}: MISSING FILE" in proc.stderr
