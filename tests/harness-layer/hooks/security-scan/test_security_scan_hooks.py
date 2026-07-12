"""End-to-end subprocess tests for the four security-scan hook scripts.

Contract under test: the per-write gate blocks secrets (exit 2, stderr
diagnostics) and warns on vulns (exit 0, hookSpecificOutput JSON on stdout,
never both channels at once) BECAUSE secrets must never land silently while
heuristics must never wedge legitimate work; session tracking attributes only
agent-era changes (baseline-dirty files are the user's and stay excluded);
and the stop sweep blocks the turn at most once per turn (stop_hook_active).

Each test launches the real script through the shared ``run_hook`` fixture
(the `run_scan` wrapper below just binds the family dir and points
CLAUDE_PROJECT_DIR at the test's own tmp_path fake project), so no test ever
touches the real worktree state dir. Parallel-safe: every fixture is
per-test, git repos are hermetic, and nothing depends on order.
Subprocess-driven code reports 0% coverage -- expected.

CRITICAL: no committed line here may itself match a secret rule. Every
secret-shaped fixture is assembled from fragments at runtime; the on-disk
source never contains a matchable literal, and positive fixtures avoid the
placeholder heuristics (no "example"/"xxx"/same-char values).
"""

import json
import os
import subprocess
from pathlib import Path

import pytest

SCRIPTS = [
    "post_write_scan.py",
    "session_baseline.py",
    "track_bash_writes.py",
    "stop_sweep.py",
]

Q = '"'  # a double quote, so no fixture writes a bare quoted literal in source


def secret_line(var: str = "x") -> str:
    """An AWS-key-shaped assignment, assembled so the source has no literal."""
    return var + " = " + Q + "AKIA" + "IOSFODNN7REALKEY" + Q + "\n"


VULN_LINE = "cfg = yaml.load(text)\n"


@pytest.fixture
def run_scan(run_hook):
    """Launch a security-scan script with CLAUDE_PROJECT_DIR at the fake project."""

    def _run(script: str, stdin_text: str, project_dir: Path) -> subprocess.CompletedProcess:
        return run_hook(
            f"security-scan/{script}",
            stdin_text,
            env_overrides={"CLAUDE_PROJECT_DIR": str(project_dir)},
        )

    return _run


def write_payload(session_id: str, file_path: Path | str) -> str:
    return json.dumps(
        {
            "session_id": session_id,
            "tool_name": "Write",
            "tool_input": {"file_path": str(file_path)},
        }
    )


def bash_payload(session_id: str, command: str = "true") -> str:
    return json.dumps(
        {"session_id": session_id, "tool_name": "Bash", "tool_input": {"command": command}}
    )


def stop_payload(session_id: str, stop_hook_active: bool = False) -> str:
    return json.dumps({"session_id": session_id, "stop_hook_active": stop_hook_active})


def state_file(project: Path, session_id: str) -> Path:
    return project / ".claude" / ".security-scan" / f"{session_id}.json"


def read_state(project: Path, session_id: str) -> dict:
    return json.loads(state_file(project, session_id).read_text())


def write_state(project: Path, session_id: str, tracked: list[str]) -> None:
    path = state_file(project, session_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"baseline": [], "tracked": tracked, "last_head": ""}))


def git(repo: Path, *args: str) -> None:
    env = os.environ.copy()
    env["GIT_CONFIG_GLOBAL"] = os.devnull
    env["GIT_CONFIG_SYSTEM"] = os.devnull
    subprocess.run(
        ["git", "-C", str(repo), *args], check=True, capture_output=True, text=True, env=env
    )


def git_commit(repo: Path, msg: str) -> None:
    git(repo, "-c", "user.email=t@test.invalid", "-c", "user.name=t", "commit", "-q", "-m", msg)


@pytest.fixture
def project(tmp_path):
    """A plain (non-git) fake project dir for CLAUDE_PROJECT_DIR."""
    proj = tmp_path / "proj"
    proj.mkdir()
    return proj


@pytest.fixture
def git_project(project):
    """The fake project as a git repo with one commit and the state dir ignored."""
    git(project, "init", "-q")
    # The hooks' own state dir must not pollute the repo's dirty set.
    (project / ".gitignore").write_text(".claude/\n")
    (project / "README.md").write_text("hello\n")
    git(project, "add", ".")
    git_commit(project, "init")
    return project


# --- Per-write gate: block / warn / suppress (AC1, AC2, AC3) -------------------


def test_post_write_secret_blocks_with_diagnostics(project, run_scan):
    target = project / "config.py"
    target.write_text(secret_line())
    res = run_scan("post_write_scan.py", write_payload("s1", target), project)
    assert res.returncode == 2
    assert f"{target}:1 aws-access-key" in res.stderr
    assert res.stdout == ""  # exit 2 never carries stdout JSON
    # The scanned file is tracked even though it was blocked.
    assert str(target) in read_state(project, "s1")["tracked"]


def test_post_write_vuln_only_warns_via_stdout_json(project, run_scan):
    target = project / "loader.py"
    target.write_text(VULN_LINE)
    res = run_scan("post_write_scan.py", write_payload("s2", target), project)
    assert res.returncode == 0
    out = json.loads(res.stdout)
    hso = out["hookSpecificOutput"]
    assert hso["hookEventName"] == "PostToolUse"
    assert "yaml-unsafe-load" in hso["additionalContext"]


def test_post_write_secret_plus_vuln_blocks_with_both_no_stdout(project, run_scan):
    target = project / "mixed.py"
    target.write_text(secret_line() + VULN_LINE)
    res = run_scan("post_write_scan.py", write_payload("s3", target), project)
    assert res.returncode == 2
    assert "aws-access-key" in res.stderr
    assert "yaml-unsafe-load" in res.stderr  # vulns ride along in the same report
    assert res.stdout == ""


def test_post_write_pragma_suppresses(project, run_scan):
    target = project / "doc.py"
    target.write_text(secret_line().rstrip("\n") + "  # security-scan: allow\n")
    res = run_scan("post_write_scan.py", write_payload("s4", target), project)
    assert res.returncode == 0
    assert res.stdout == ""
    assert "aws-access-key" not in res.stderr


def test_post_write_placeholder_suppresses(project, run_scan):
    target = project / "sample.py"
    # Placeholder heuristics: "your..." values never count as credentials.
    target.write_text("api_key = " + Q + "your-key-goes-here" + Q + "\n")
    res = run_scan("post_write_scan.py", write_payload("s5", target), project)
    assert res.returncode == 0
    assert res.stdout == ""


def test_post_write_diagnostics_are_capped(project, run_scan):
    target = project / "many.py"
    target.write_text("".join(secret_line(f"v{i}") for i in range(14)))
    res = run_scan("post_write_scan.py", write_payload("s6", target), project)
    assert res.returncode == 2
    assert "... and 4 more" in res.stderr  # 14 findings, cap 10 + tail


def test_post_write_tracks_before_scan_survives_formatter_race(project, run_scan):
    # PostToolUse hooks run in parallel with the auto-format hooks, so the
    # scan can race a formatter still writing the file and see it empty (or
    # unreadable). The tracked-set update happens BEFORE the scan, so the
    # path still lands in the tracked set for the Stop sweep even when this
    # write's own scan finds nothing.
    target = project / "racy.py"
    target.write_text("")  # momentarily empty at scan time
    res = run_scan("post_write_scan.py", write_payload("race1", target), project)
    assert res.returncode == 0
    assert str(target) in read_state(project, "race1")["tracked"]

    # The real (secret-bearing) content lands after the racy scan settles.
    target.write_text(secret_line())
    res = run_scan("stop_sweep.py", stop_payload("race1"), project)
    assert res.returncode == 2
    assert f"{target}:1 aws-access-key" in res.stderr


# --- Session tracking: baseline exclusion + round-2 cases (AC4) ----------------


def test_baseline_exclusion_new_file_tracked_dirty_file_not(git_project, run_scan):
    sid = "t1"
    # Pre-dirty the committed file (user-owned work) before the session starts.
    (git_project / "README.md").write_text("hello\nuser edit\n")
    res = run_scan("session_baseline.py", json.dumps({"session_id": sid}), git_project)
    assert res.returncode == 0
    state = read_state(git_project, sid)
    assert str(git_project / "README.md") in state["baseline"]
    assert state["last_head"]  # HEAD recorded

    # A Bash call creates a new file AND modifies the baseline-dirty file.
    (git_project / "created.txt").write_text("made by bash\n")
    (git_project / "README.md").write_text("hello\nuser edit\nbash edit\n")
    res = run_scan("track_bash_writes.py", bash_payload(sid), git_project)
    assert res.returncode == 0
    tracked = read_state(git_project, sid)["tracked"]
    assert str(git_project / "created.txt") in tracked
    # The documented attribution exclusion: baseline-dirty stays untracked.
    assert str(git_project / "README.md") not in tracked


def test_failed_bash_leftover_is_tracked_and_swept(git_project, run_scan):
    sid = "t2"
    run_scan("session_baseline.py", json.dumps({"session_id": sid}), git_project)
    # A failing command still left a newly dirty secret file behind.
    leftover = git_project / "leftover.py"
    leftover.write_text(secret_line())
    payload = json.dumps(
        {
            "session_id": sid,
            "tool_name": "Bash",
            "tool_input": {"command": "false"},
            "tool_response": {"exit_code": 1},  # PostToolUseFailure-shaped
        }
    )
    res = run_scan("track_bash_writes.py", payload, git_project)
    assert res.returncode == 0
    assert str(leftover) in read_state(git_project, sid)["tracked"]

    res = run_scan("stop_sweep.py", stop_payload(sid), git_project)
    assert res.returncode == 2
    assert f"{leftover}:1 aws-access-key" in res.stderr


def test_commit_within_bash_call_is_tracked_via_head_diff_and_swept(git_project, run_scan):
    sid = "t3"
    run_scan("session_baseline.py", json.dumps({"session_id": sid}), git_project)
    old_head = read_state(git_project, sid)["last_head"]

    # One Bash call writes AND commits the file: the tree is clean afterwards,
    # so only the last_head commit diff can attribute it.
    committed = git_project / "committed.py"
    committed.write_text(secret_line())
    git(git_project, "add", "committed.py")
    git_commit(git_project, "agent commit")

    res = run_scan("track_bash_writes.py", bash_payload(sid), git_project)
    assert res.returncode == 0
    state = read_state(git_project, sid)
    assert str(committed) in state["tracked"]
    assert state["last_head"] != old_head  # last_head advanced

    res = run_scan("stop_sweep.py", stop_payload(sid), git_project)
    assert res.returncode == 2
    assert "aws-access-key" in res.stderr


# --- Session-state locking: no lost updates under parallel hook events ---------


def test_concurrent_post_write_hooks_do_not_lose_tracked_updates(project, run_scan):
    # N real post_write_scan.py subprocesses, all for the SAME session, each
    # tracking a distinct file concurrently. Without the per-session file
    # lock this is a classic load-mutate-save race: last writer wins and
    # earlier tracked paths silently vanish.
    import concurrent.futures

    sid = "race1"
    n = 8
    targets = []
    for i in range(n):
        target = project / f"concurrent_{i}.py"
        target.write_text(f"value_{i} = 1\n")
        targets.append(target)

    def _run(target: Path) -> subprocess.CompletedProcess:
        return run_scan("post_write_scan.py", write_payload(sid, target), project)

    with concurrent.futures.ThreadPoolExecutor(max_workers=n) as pool:
        results = list(pool.map(_run, targets))

    for res in results:
        assert res.returncode == 0

    tracked = set(read_state(project, sid)["tracked"])
    assert tracked == {str(t) for t in targets}


def test_session_baseline_merges_without_clobbering_existing_tracked(git_project, run_scan):
    # Simulate an in-flight tracked path already on disk (e.g. a parallel
    # PostToolUse hook) before SessionStart (re-)runs. The baseline write
    # must overwrite baseline/last_head but MERGE tracked, not clobber it.
    sid = "merge1"
    already = git_project / "already-tracked.py"
    write_state(git_project, sid, [str(already)])

    res = run_scan("session_baseline.py", json.dumps({"session_id": sid}), git_project)
    assert res.returncode == 0
    state = read_state(git_project, sid)
    assert str(already) in state["tracked"]
    assert state["last_head"]  # baseline/last_head are still freshly computed


# --- Git path parsing: -z handles spaces, non-ASCII, and renames --------------


def test_bash_tracks_filename_with_spaces(git_project, run_scan):
    sid = "sp1"
    run_scan("session_baseline.py", json.dumps({"session_id": sid}), git_project)
    weird = git_project / "a file with spaces.txt"
    weird.write_text("hi\n")
    res = run_scan("track_bash_writes.py", bash_payload(sid), git_project)
    assert res.returncode == 0
    assert str(weird) in read_state(git_project, sid)["tracked"]


def test_bash_tracks_non_ascii_filename(git_project, run_scan):
    sid = "sp2"
    run_scan("session_baseline.py", json.dumps({"session_id": sid}), git_project)
    weird = git_project / "café.txt"
    weird.write_text("hi\n")
    res = run_scan("track_bash_writes.py", bash_payload(sid), git_project)
    assert res.returncode == 0
    assert str(weird) in read_state(git_project, sid)["tracked"]


def test_bash_tracks_renamed_file_as_new_path(git_project, run_scan):
    sid = "sp3"
    run_scan("session_baseline.py", json.dumps({"session_id": sid}), git_project)
    renamed = git_project / "README-renamed.md"
    git(git_project, "mv", "README.md", "README-renamed.md")
    res = run_scan("track_bash_writes.py", bash_payload(sid), git_project)
    assert res.returncode == 0
    tracked = read_state(git_project, sid)["tracked"]
    assert str(renamed) in tracked


# --- Stop sweep: block-then-pass, stop_hook_active, fail-open (AC5) ------------


def test_sweep_blocks_then_passes_after_fix(project, run_scan):
    target = project / "tracked.py"
    target.write_text(secret_line())
    write_state(project, "w1", [str(target)])

    res = run_scan("stop_sweep.py", stop_payload("w1"), project)
    assert res.returncode == 2
    assert f"{target}:1 aws-access-key" in res.stderr
    assert res.stdout == ""  # the sweep never writes stdout

    target.write_text("value = 1\n")  # secret removed
    res = run_scan("stop_sweep.py", stop_payload("w1"), project)
    assert res.returncode == 0


def test_sweep_stop_hook_active_warns_loudly_but_allows_stop(project, run_scan):
    target = project / "tracked.py"
    target.write_text(secret_line())
    write_state(project, "w2", [str(target)])
    res = run_scan("stop_sweep.py", stop_payload("w2", stop_hook_active=True), project)
    assert res.returncode == 0  # blocks at most once per turn
    assert "SECURITY WARNING" in res.stderr
    assert "aws-access-key" in res.stderr  # the surviving finding is named
    assert res.stdout == ""


def test_sweep_vuln_only_does_not_block(project, run_scan):
    target = project / "loader.py"
    target.write_text(VULN_LINE)
    write_state(project, "w3", [str(target)])
    res = run_scan("stop_sweep.py", stop_payload("w3"), project)
    assert res.returncode == 0
    assert res.stdout == ""  # Stop has no additionalContext channel
    assert "yaml-unsafe-load" in res.stderr  # brief non-blocking note


def test_sweep_missing_state_fails_open(project, run_scan):
    res = run_scan("stop_sweep.py", stop_payload("never-written"), project)
    assert res.returncode == 0


def test_sweep_corrupt_state_fails_open(project, run_scan):
    path = state_file(project, "w4")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("{ not valid json")
    res = run_scan("stop_sweep.py", stop_payload("w4"), project)
    assert res.returncode == 0


def test_sweep_tracked_file_deleted_fails_open(project, run_scan):
    write_state(project, "w5", [str(project / "gone.py")])
    res = run_scan("stop_sweep.py", stop_payload("w5"), project)
    assert res.returncode == 0


# --- Fail-open matrix: 4 scripts x 3 bad inputs (AC6) ---------------------------


def bad_stdin_cases(project: Path) -> dict[str, str]:
    return {
        "empty": "",
        "malformed": "{ not json",
        "nonexistent-file": json.dumps(
            {
                "session_id": "m1",
                "tool_name": "Write",
                "tool_input": {"file_path": str(project / "does" / "not" / "exist.py")},
            }
        ),
    }


@pytest.mark.parametrize("script", SCRIPTS)
@pytest.mark.parametrize("case", ["empty", "malformed", "nonexistent-file"])
def test_fail_open_matrix(project, run_scan, script, case):
    stdin_text = bad_stdin_cases(project)[case]
    res = run_scan(script, stdin_text, project)
    assert res.returncode == 0
    assert res.stdout == ""  # no stray stdout on the fail-open path
