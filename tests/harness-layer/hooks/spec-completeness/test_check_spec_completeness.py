"""Contract tests for the spec-completeness Stop gate (check_spec_completeness.py).

The gate is command-scoped (registered by /harness-layer:harness-plan, NOT in
settings.json), so it must never fire outside a planning run -- a root with no
specs/ dir passes silently. It is ALSO session-scoped: it resolves the invoking
session's root from the Stop payload's `cwd` and gates only the NEWEST plan
folder under THAT root's specs/ -- never another worktree's. A concurrent
planning session in a different root can neither steal nor mask the target
(regression-tested both directions below); scanning across every worktree's
specs/ was the soriza wrong-target defect class this rework removes. _templates
and discovery-only chain folders are excluded. Exit 2 must name exactly what is
missing -- file or '## section' -- because stderr is the agent's only repair
instruction. Complete plans are built from the hook's own REQUIRED_SECTIONS via
load_hook_module, so a rule change cannot silently diverge from the tests.
Malformed/empty stdin and a cwd outside any git repo fail open (exit 0), never
crash.
"""

import json
import os
from pathlib import Path

import pytest


def payload(cwd: Path) -> str:
    """A Stop payload carrying the session's cwd -- the field the gate reads to
    resolve its root."""
    return json.dumps({"stop_hook_active": False, "cwd": str(cwd)})


@pytest.fixture
def sections(load_hook_module):
    return load_hook_module("check_spec_completeness.py").REQUIRED_SECTIONS


def write_plan(specs: Path, name: str, sections: dict) -> Path:
    """A plan folder whose four files carry every required section."""
    folder = specs / name
    folder.mkdir(parents=True)
    for fname, secs in sections.items():
        body = "\n\n".join(f"## {sec}\n\ncontent" for sec in secs)
        (folder / fname).write_text(f"# {name}\n\n{body}\n")
    return folder


def set_mtime(folder: Path, epoch: float) -> None:
    os.utime(folder, (epoch, epoch))


def gate(run_hook, root: Path):
    """Run the hook as a session rooted at `root`: `root` is a real directory
    outside any git repo (pytest tmp), so the gate's git-toplevel step fails and
    it falls to the stdin cwd itself -- making `root` the gated root."""
    return run_hook("check_spec_completeness.py", payload(root))


def test_no_specs_dir_allows_stop(tmp_path, run_hook):
    """Command-scoped or not, a session whose root has no specs/ has nothing to
    gate -- the hook must be invisible there."""
    proc = gate(run_hook, tmp_path)
    assert proc.returncode == 0
    assert proc.stderr == ""


def test_underscore_and_discovery_only_folders_block_as_no_plan(tmp_path, run_hook):
    """_templates is scaffolding and a folder holding only discovery/ pages is
    a pre-plan chain still in progress — neither is a plan: a planning run that
    produced no spec files must not be allowed to end, and discovery pages must
    never be gated as a spec."""
    (tmp_path / "specs" / "_templates").mkdir(parents=True)
    discovery = tmp_path / "specs" / "some-chain" / "discovery"
    discovery.mkdir(parents=True)
    (discovery / "page.html").write_text("<p>mock</p>")
    proc = gate(run_hook, tmp_path)
    assert proc.returncode == 2
    assert "no plan folder found" in proc.stderr


def test_newer_discovery_only_folder_does_not_mask_the_plan(tmp_path, run_hook, sections):
    """A parallel chain's discovery-only folder can be newer than the plan
    being drafted; picking it as "newest" would gate HTML pages as a spec and
    block every planning run — the newest folder with spec files must win."""
    specs = tmp_path / "specs"
    plan = write_plan(specs, "the-plan", sections)
    discovery = specs / "newer-chain" / "discovery"
    discovery.mkdir(parents=True)
    (discovery / "page.html").write_text("<p>mock</p>")
    set_mtime(plan, 1_000_000_000)
    set_mtime(specs / "newer-chain", 2_000_000_000)
    proc = gate(run_hook, tmp_path)
    assert proc.returncode == 0


def test_plan_folder_with_discovery_pages_is_gated_normally(tmp_path, run_hook, sections):
    """After the chain, discovery/ lives INSIDE the plan folder; its presence
    must not exempt a folder that already has spec files from the completeness
    gate, or an incomplete post-chain plan would slip through."""
    folder = write_plan(tmp_path / "specs", "my-plan", sections)
    (folder / "discovery").mkdir()
    (folder / "discovery" / "interview.html").write_text("<p>page</p>")
    (folder / "tasks.md").unlink()
    proc = gate(run_hook, tmp_path)
    assert proc.returncode == 2
    assert "MISSING FILE: tasks.md" in proc.stderr


def test_complete_plan_allows_stop(tmp_path, run_hook, sections):
    """All four files present with every required section: the gate opens."""
    write_plan(tmp_path / "specs", "my-plan", sections)
    proc = gate(run_hook, tmp_path)
    assert proc.returncode == 0
    assert proc.stderr == ""


def test_missing_file_blocks_naming_it(tmp_path, run_hook, sections):
    """A absent spec file is named outright so the agent knows what to write."""
    folder = write_plan(tmp_path / "specs", "my-plan", sections)
    (folder / "tasks.md").unlink()
    proc = gate(run_hook, tmp_path)
    assert proc.returncode == 2
    assert "MISSING FILE: tasks.md" in proc.stderr
    assert "compare against specs/_templates/" in proc.stderr


def test_missing_section_blocks_naming_file_and_heading(tmp_path, run_hook, sections):
    """A gutted section is named as file + '## heading' -- the exact repair."""
    folder = write_plan(tmp_path / "specs", "my-plan", sections)
    spec = folder / "spec.md"
    spec.write_text(spec.read_text().replace("## Red Flags", "## Renamed"))
    proc = gate(run_hook, tmp_path)
    assert proc.returncode == 2
    assert "spec.md: missing section '## Red Flags'" in proc.stderr
    # exit-2 blocking must not be mixed with structured stdout (hooks-guide contract)
    assert proc.stdout == ""


def test_newest_plan_folder_is_the_gated_one(tmp_path, run_hook, sections):
    """Only the plan being drafted NOW is gated: an old complete plan must not
    mask a fresh incomplete one, and vice versa the old one is never re-gated."""
    specs = tmp_path / "specs"
    old = write_plan(specs, "old-complete", sections)
    fresh = write_plan(specs, "fresh-incomplete", sections)
    (fresh / "decisions.md").unlink()
    set_mtime(old, 1_000_000_000)
    set_mtime(fresh, 2_000_000_000)
    proc = gate(run_hook, tmp_path)
    assert proc.returncode == 2
    assert "fresh-incomplete" in proc.stderr


# --- Session-scoping / concurrency regression tests -------------------------
# Two roots stand in for two concurrent planning sessions in different
# worktrees. Only the session root is passed as the payload cwd; the foreign
# root must never influence the verdict. These replace the former
# `test_worktree_specs_are_discovered` /
# `test_no_main_specs_dir_skips_even_with_worktree_specs`, which pinned the now
# deleted cross-worktree scan.


def two_roots(tmp_path: Path) -> tuple[Path, Path]:
    """A session root and a foreign root, each a self-contained tree outside any
    git repo so each resolves to itself via the stdin-cwd fallback."""
    session = tmp_path / "session"
    foreign = tmp_path / "foreign"
    session.mkdir()
    foreign.mkdir()
    return session, foreign


def test_foreign_root_complete_plan_never_opens_the_session_gate(tmp_path, run_hook, sections):
    """(a) Session root's plan is incomplete while a foreign root carries a
    complete, NEWER plan. A cross-root scan would pick the foreign complete plan
    and wrongly open the gate; session-scoped, the session's own incomplete plan
    is gated -- exit 2 naming the session's folder, foreign never mentioned."""
    session, foreign = two_roots(tmp_path)
    sess_plan = write_plan(session / "specs", "session-plan", sections)
    (sess_plan / "acceptance-criteria.md").unlink()
    foreign_plan = write_plan(foreign / "specs", "foreign-plan", sections)
    set_mtime(sess_plan, 1_000_000_000)
    set_mtime(foreign_plan, 2_000_000_000)  # newer -- would win a cross-root scan
    proc = gate(run_hook, session)
    assert proc.returncode == 2
    assert "session-plan" in proc.stderr
    assert "MISSING FILE: acceptance-criteria.md" in proc.stderr
    assert "foreign-plan" not in proc.stderr


def test_foreign_root_incomplete_plan_never_blocks_the_session(tmp_path, run_hook, sections):
    """(b) The opposite direction: the session's plan is complete while a
    foreign root carries an incomplete, NEWER plan. A cross-root scan would pick
    the foreign incomplete plan and wrongly block; session-scoped, the session's
    complete plan opens the gate -- exit 0."""
    session, foreign = two_roots(tmp_path)
    sess_plan = write_plan(session / "specs", "session-plan", sections)
    foreign_plan = write_plan(foreign / "specs", "foreign-plan", sections)
    (foreign_plan / "spec.md").unlink()
    set_mtime(sess_plan, 1_000_000_000)
    set_mtime(foreign_plan, 2_000_000_000)  # newer -- would win a cross-root scan
    proc = gate(run_hook, session)
    assert proc.returncode == 0
    assert proc.stderr == ""


def test_mtime_decoy_in_foreign_root_never_changes_the_selection(tmp_path, run_hook, sections):
    """(c) The session root itself holds an older complete plan and a newer
    incomplete plan; a foreign root holds a decoy that is newer than BOTH and
    complete. The selection must stay the session's own newest folder
    (within-root mtime still wins) and never jump to the foreign decoy -- exit 2
    naming the session's incomplete plan, proving the foreign mtime was ignored."""
    session, foreign = two_roots(tmp_path)
    old = write_plan(session / "specs", "session-old-complete", sections)
    target = write_plan(session / "specs", "session-new-incomplete", sections)
    (target / "decisions.md").unlink()
    decoy = write_plan(foreign / "specs", "foreign-decoy-complete", sections)
    set_mtime(old, 1_000_000_000)
    set_mtime(target, 2_000_000_000)
    set_mtime(decoy, 3_000_000_000)  # newest of all -- must be invisible
    proc = gate(run_hook, session)
    assert proc.returncode == 2
    assert "session-new-incomplete" in proc.stderr
    assert "foreign-decoy-complete" not in proc.stderr
    assert "session-old-complete" not in proc.stderr


def test_no_session_specs_dir_skips_even_with_foreign_specs(tmp_path, run_hook, sections):
    """The session root's own specs/ is the gate's on-switch: without it the
    hook exits 0 even though a foreign root carries a (newer, incomplete) plan --
    replaces the old worktree-scoped on-switch test; the scope is now per-root."""
    session, foreign = two_roots(tmp_path)
    foreign_plan = write_plan(foreign / "specs", "foreign-plan", sections)
    (foreign_plan / "spec.md").unlink()
    proc = gate(run_hook, session)  # session has no specs/ at all
    assert proc.returncode == 0
    assert proc.stderr == ""


# --- Fail-open on plumbing --------------------------------------------------


def test_malformed_stdin_fails_open(tmp_path, run_hook):
    """(d) Garbage on stdin is plumbing noise, not an agent-fixable finding: the
    gate degrades down the fallback chain (here to a specs-less process cwd) and
    exits 0 without a traceback -- never crash, never exit 2 on plumbing."""
    proc = run_hook("check_spec_completeness.py", "not json {{{", cwd=tmp_path)
    assert proc.returncode == 0
    assert "Traceback" not in proc.stderr


def test_empty_stdin_fails_open(tmp_path, run_hook):
    """Empty stdin (no payload) is the same plumbing case as malformed input:
    fall back without crashing, exit 0."""
    proc = run_hook("check_spec_completeness.py", "", cwd=tmp_path)
    assert proc.returncode == 0
    assert "Traceback" not in proc.stderr


def test_cwd_outside_git_repo_uses_cwd_and_exits_when_no_specs(tmp_path, run_hook):
    """A stdin cwd that exists but is outside any git repo: git rev-parse fails,
    so the cwd path itself serves as the root; with no specs/ there the gate
    exits 0 -- the documented outside-git edge, resolved without crashing."""
    outside = tmp_path / "outside"
    outside.mkdir()
    proc = gate(run_hook, outside)
    assert proc.returncode == 0
    assert proc.stderr == ""
    assert "Traceback" not in proc.stderr
