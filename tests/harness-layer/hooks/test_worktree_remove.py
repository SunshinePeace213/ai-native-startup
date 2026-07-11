"""Contract tests for the WorktreeRemove hook (worktree_remove.py).

Removal is the destructive half of the lifecycle, so the guards ARE the
contract: the worktree and its branch go away only when the branch is the
hook's own naming scheme (worktree-*) -- a foreign branch checked out in a
worktree is someone's real work and must survive; a directory git does not
recognize as a worktree is never touched; and a missing path or garbage
payload exits 0 so cleanup can never wedge a session. Both documented
payload shapes (worktreePath / worktree_path) are accepted because the two
sources disagree.
"""

import json


def add_worktree(wt_repo, name: str, branch: str):
    path = wt_repo.root / ".claude" / "worktrees" / name
    wt_repo.git("worktree", "add", "-b", branch, str(path))
    return path


def branch_exists(wt_repo, branch: str) -> bool:
    proc = wt_repo.git("rev-parse", "--verify", f"refs/heads/{branch}", check=False)
    return proc.returncode == 0


def test_kb_payload_shape_removes_worktree_and_its_branch(wt_repo, run_hook):
    """The full cleanup: worktree directory gone AND its worktree-* branch
    deleted, so kept-around branches don't accumulate forever."""
    path = add_worktree(wt_repo, "zap", "worktree-zap")
    proc = run_hook("worktree_remove.py", json.dumps({"worktreePath": str(path)}), wt_repo.env)
    assert proc.returncode == 0
    assert not path.exists()
    assert not branch_exists(wt_repo, "worktree-zap")


def test_reference_payload_shape_is_also_accepted(wt_repo, run_hook):
    """The reference implementation sends worktree_path; the hook must clean
    up with either field."""
    path = add_worktree(wt_repo, "zip", "worktree-zip")
    proc = run_hook("worktree_remove.py", json.dumps({"worktree_path": str(path)}), wt_repo.env)
    assert proc.returncode == 0
    assert not path.exists()
    assert not branch_exists(wt_repo, "worktree-zip")


def test_foreign_branch_is_preserved(wt_repo, run_hook):
    """A worktree checked out on a branch the hook did not name (no worktree-
    prefix) is someone's real work: remove the directory, keep the branch."""
    path = add_worktree(wt_repo, "feat", "feature-keep")
    proc = run_hook("worktree_remove.py", json.dumps({"worktreePath": str(path)}), wt_repo.env)
    assert proc.returncode == 0
    assert not path.exists()
    assert branch_exists(wt_repo, "feature-keep")


def test_missing_path_exits_zero(wt_repo, run_hook):
    """An already-removed worktree is a done job, not an error -- cleanup must
    be idempotent."""
    gone = wt_repo.tmp / "never-existed"
    proc = run_hook("worktree_remove.py", json.dumps({"worktreePath": str(gone)}), wt_repo.env)
    assert proc.returncode == 0


def test_payload_without_a_path_fails_open(wt_repo, run_hook):
    """Neither worktreePath nor worktree_path: nothing to remove, exit 0 with
    a note naming the fields so payload-shape drift is diagnosable."""
    proc = run_hook("worktree_remove.py", json.dumps({"foo": "x"}), wt_repo.env)
    assert proc.returncode == 0
    assert "worktreePath" in proc.stderr


def test_directory_that_is_not_a_worktree_is_left_alone(wt_repo, run_hook):
    """Safe-delete guarantee: if git does not own the path as a worktree, the
    hook must not destroy it -- note the git error and exit 0."""
    plain = wt_repo.tmp / "just-a-dir"
    plain.mkdir()
    (plain / "precious.txt").write_text("do not delete\n")
    proc = run_hook("worktree_remove.py", json.dumps({"worktreePath": str(plain)}), wt_repo.env)
    assert proc.returncode == 0
    assert plain.is_dir()
    assert (plain / "precious.txt").exists()


def test_project_dir_being_the_removed_worktree_still_deletes_branch(wt_repo, run_hook):
    """Claude Code may run the hook with $CLAUDE_PROJECT_DIR pointing at the
    very worktree being removed; git must not run from the dying directory
    or the branch delete fails and worktree-* branches leak forever."""
    path = add_worktree(wt_repo, "selfref", "worktree-selfref")
    env = {**wt_repo.env, "CLAUDE_PROJECT_DIR": str(path)}
    proc = run_hook("worktree_remove.py", json.dumps({"worktreePath": str(path)}), env)
    assert proc.returncode == 0
    assert not path.exists()
    assert not branch_exists(wt_repo, "worktree-selfref")
