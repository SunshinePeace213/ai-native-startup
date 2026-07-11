"""End-to-end subprocess tests for the four security-scan hook scripts.

Contract under test: the per-write gate blocks secrets (exit 2, stderr
diagnostics) and warns on vulns (exit 0, hookSpecificOutput JSON on stdout,
never both channels at once) BECAUSE secrets must never land silently while
heuristics must never wedge legitimate work; session tracking attributes only
agent-era changes (baseline-dirty files are the user's and stay excluded);
and the stop sweep blocks the turn at most once per turn (stop_hook_active).

Each test pipes a payload JSON into the real script via ``uv run --script``
(run from the repo root so uv resolves), with CLAUDE_PROJECT_DIR pointed at
the test's own tmp_path fake project so no test ever touches the real
worktree state dir. Parallel-safe: every fixture is per-test, git repos are
hermetic (global/system config disabled), and nothing depends on order.
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

REPO_ROOT = Path(__file__).resolve().parents[2]
HOOKS_DIR = REPO_ROOT / ".claude" / "hooks" / "security-scan"
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


def run_hook(script: str, stdin_text: str, project_dir: Path) -> subprocess.CompletedProcess:
    """Pipe ``stdin_text`` into a hook script with CLAUDE_PROJECT_DIR isolated."""
    env = os.environ.copy()
    env["CLAUDE_PROJECT_DIR"] = str(project_dir)
    # Hermetic git for the hook's own subprocess calls too.
    env["GIT_CONFIG_GLOBAL"] = os.devnull
    env["GIT_CONFIG_SYSTEM"] = os.devnull
    return subprocess.run(
        ["uv", "run", "--script", str(HOOKS_DIR / script)],
        input=stdin_text,
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
        env=env,
        timeout=45,
    )


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


def test_post_write_secret_blocks_with_diagnostics(project):
    target = project / "config.py"
    target.write_text(secret_line())
    res = run_hook("post_write_scan.py", write_payload("s1", target), project)
    assert res.returncode == 2
    assert f"{target}:1 aws-access-key" in res.stderr
    assert res.stdout == ""  # exit 2 never carries stdout JSON
    # The scanned file is tracked even though it was blocked.
    assert str(target) in read_state(project, "s1")["tracked"]


def test_post_write_vuln_only_warns_via_stdout_json(project):
    target = project / "loader.py"
    target.write_text(VULN_LINE)
    res = run_hook("post_write_scan.py", write_payload("s2", target), project)
    assert res.returncode == 0
    out = json.loads(res.stdout)
    hso = out["hookSpecificOutput"]
    assert hso["hookEventName"] == "PostToolUse"
    assert "yaml-unsafe-load" in hso["additionalContext"]


def test_post_write_secret_plus_vuln_blocks_with_both_no_stdout(project):
    target = project / "mixed.py"
    target.write_text(secret_line() + VULN_LINE)
    res = run_hook("post_write_scan.py", write_payload("s3", target), project)
    assert res.returncode == 2
    assert "aws-access-key" in res.stderr
    assert "yaml-unsafe-load" in res.stderr  # vulns ride along in the same report
    assert res.stdout == ""


def test_post_write_pragma_suppresses(project):
    target = project / "doc.py"
    target.write_text(secret_line().rstrip("\n") + "  # security-scan: allow\n")
    res = run_hook("post_write_scan.py", write_payload("s4", target), project)
    assert res.returncode == 0
    assert res.stdout == ""
    assert "aws-access-key" not in res.stderr


def test_post_write_placeholder_suppresses(project):
    target = project / "sample.py"
    # Placeholder heuristics: "your..." values never count as credentials.
    target.write_text("api_key = " + Q + "your-key-goes-here" + Q + "\n")
    res = run_hook("post_write_scan.py", write_payload("s5", target), project)
    assert res.returncode == 0
    assert res.stdout == ""


def test_post_write_diagnostics_are_capped(project):
    target = project / "many.py"
    target.write_text("".join(secret_line(f"v{i}") for i in range(14)))
    res = run_hook("post_write_scan.py", write_payload("s6", target), project)
    assert res.returncode == 2
    assert "... and 4 more" in res.stderr  # 14 findings, cap 10 + tail


# --- Session tracking: baseline exclusion + round-2 cases (AC4) ----------------


def test_baseline_exclusion_new_file_tracked_dirty_file_not(git_project):
    sid = "t1"
    # Pre-dirty the committed file (user-owned work) before the session starts.
    (git_project / "README.md").write_text("hello\nuser edit\n")
    res = run_hook("session_baseline.py", json.dumps({"session_id": sid}), git_project)
    assert res.returncode == 0
    state = read_state(git_project, sid)
    assert str(git_project / "README.md") in state["baseline"]
    assert state["last_head"]  # HEAD recorded

    # A Bash call creates a new file AND modifies the baseline-dirty file.
    (git_project / "created.txt").write_text("made by bash\n")
    (git_project / "README.md").write_text("hello\nuser edit\nbash edit\n")
    res = run_hook("track_bash_writes.py", bash_payload(sid), git_project)
    assert res.returncode == 0
    tracked = read_state(git_project, sid)["tracked"]
    assert str(git_project / "created.txt") in tracked
    # The documented attribution exclusion: baseline-dirty stays untracked.
    assert str(git_project / "README.md") not in tracked


def test_failed_bash_leftover_is_tracked_and_swept(git_project):
    sid = "t2"
    run_hook("session_baseline.py", json.dumps({"session_id": sid}), git_project)
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
    res = run_hook("track_bash_writes.py", payload, git_project)
    assert res.returncode == 0
    assert str(leftover) in read_state(git_project, sid)["tracked"]

    res = run_hook("stop_sweep.py", stop_payload(sid), git_project)
    assert res.returncode == 2
    assert f"{leftover}:1 aws-access-key" in res.stderr


def test_commit_within_bash_call_is_tracked_via_head_diff_and_swept(git_project):
    sid = "t3"
    run_hook("session_baseline.py", json.dumps({"session_id": sid}), git_project)
    old_head = read_state(git_project, sid)["last_head"]

    # One Bash call writes AND commits the file: the tree is clean afterwards,
    # so only the last_head commit diff can attribute it.
    committed = git_project / "committed.py"
    committed.write_text(secret_line())
    git(git_project, "add", "committed.py")
    git_commit(git_project, "agent commit")

    res = run_hook("track_bash_writes.py", bash_payload(sid), git_project)
    assert res.returncode == 0
    state = read_state(git_project, sid)
    assert str(committed) in state["tracked"]
    assert state["last_head"] != old_head  # last_head advanced

    res = run_hook("stop_sweep.py", stop_payload(sid), git_project)
    assert res.returncode == 2
    assert "aws-access-key" in res.stderr


# --- Stop sweep: block-then-pass, stop_hook_active, fail-open (AC5) ------------


def test_sweep_blocks_then_passes_after_fix(project):
    target = project / "tracked.py"
    target.write_text(secret_line())
    write_state(project, "w1", [str(target)])

    res = run_hook("stop_sweep.py", stop_payload("w1"), project)
    assert res.returncode == 2
    assert f"{target}:1 aws-access-key" in res.stderr
    assert res.stdout == ""  # the sweep never writes stdout

    target.write_text("value = 1\n")  # secret removed
    res = run_hook("stop_sweep.py", stop_payload("w1"), project)
    assert res.returncode == 0


def test_sweep_stop_hook_active_warns_loudly_but_allows_stop(project):
    target = project / "tracked.py"
    target.write_text(secret_line())
    write_state(project, "w2", [str(target)])
    res = run_hook("stop_sweep.py", stop_payload("w2", stop_hook_active=True), project)
    assert res.returncode == 0  # blocks at most once per turn
    assert "SECURITY WARNING" in res.stderr
    assert "aws-access-key" in res.stderr  # the surviving finding is named
    assert res.stdout == ""


def test_sweep_vuln_only_does_not_block(project):
    target = project / "loader.py"
    target.write_text(VULN_LINE)
    write_state(project, "w3", [str(target)])
    res = run_hook("stop_sweep.py", stop_payload("w3"), project)
    assert res.returncode == 0
    assert res.stdout == ""  # Stop has no additionalContext channel
    assert "yaml-unsafe-load" in res.stderr  # brief non-blocking note


def test_sweep_missing_state_fails_open(project):
    res = run_hook("stop_sweep.py", stop_payload("never-written"), project)
    assert res.returncode == 0


def test_sweep_corrupt_state_fails_open(project):
    path = state_file(project, "w4")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("{ not valid json")
    res = run_hook("stop_sweep.py", stop_payload("w4"), project)
    assert res.returncode == 0


def test_sweep_tracked_file_deleted_fails_open(project):
    write_state(project, "w5", [str(project / "gone.py")])
    res = run_hook("stop_sweep.py", stop_payload("w5"), project)
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
def test_fail_open_matrix(project, script, case):
    stdin_text = bad_stdin_cases(project)[case]
    res = run_hook(script, stdin_text, project)
    assert res.returncode == 0
    assert res.stdout == ""  # no stray stdout on the fail-open path
