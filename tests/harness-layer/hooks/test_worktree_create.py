"""Contract tests for the WorktreeCreate hook (worktree_create.py).

Registering a WorktreeCreate hook REPLACES Claude Code's default worktree
creation, so these tests pin the whole contract: stdout must be EXACTLY
the absolute worktree path (Claude Code parses it -- one stray line breaks
every worktree launch), the worktree lands at .claude/worktrees/<name> on
branch worktree-<name>, deps are installed INSIDE the new worktree so the
format hooks work there, and both documented payload shapes (worktreeName
from the hooks reference, name from the reference implementation) are
accepted because the two sources disagree. Install failures must never
abort creation, and a nameless payload must fail open.
"""

import json

import pytest


def wt_path(root, name):
    return root.resolve() / ".claude" / "worktrees" / name


def test_kb_payload_shape_creates_worktree_and_branch(wt_repo, run_hook):
    """The documented shape (worktreeName) must yield a worktree on branch
    worktree-<name>, with stdout carrying the absolute path and nothing else."""
    proc = run_hook("worktree_create.py", json.dumps({"worktreeName": "alpha"}), wt_repo.env)
    worktree = wt_path(wt_repo.root, "alpha")
    assert proc.returncode == 0
    assert proc.stdout == f"{worktree}\n"  # the hard contract: one line, path only
    assert worktree.is_dir()
    head = wt_repo.git("rev-parse", "--abbrev-ref", "HEAD", cwd=worktree)
    assert head.stdout.strip() == "worktree-alpha"
    assert wt_repo.git("rev-parse", "--verify", "refs/heads/worktree-alpha").returncode == 0


def test_reference_payload_shape_is_also_accepted(wt_repo, run_hook):
    """The reference implementation sends `name`; until a live payload settles
    the question, the hook must work with either field."""
    proc = run_hook("worktree_create.py", json.dumps({"name": "beta"}), wt_repo.env)
    worktree = wt_path(wt_repo.root, "beta")
    assert proc.returncode == 0
    assert proc.stdout == f"{worktree}\n"
    assert worktree.is_dir()


def test_deps_are_installed_inside_the_new_worktree(wt_repo, run_hook):
    """The whole point of owning creation: bun install + uv sync must run with
    the NEW worktree as cwd, not the main checkout, or format hooks stay dead
    exactly where builds happen."""
    run_hook("worktree_create.py", json.dumps({"worktreeName": "deps"}), wt_repo.env)
    worktree = wt_path(wt_repo.root, "deps")
    log = wt_repo.stub_log.read_text().splitlines()
    assert f"bun install {worktree}" in log
    assert f"uv sync {worktree}" in log


def test_install_failure_still_prints_the_path(wt_repo, run_hook):
    """A broken install must degrade to a worktree without deps (format hooks
    skip with a note), never to a failed worktree launch: the path still goes
    to stdout and the failure to stderr."""
    wt_repo.fail_installs()
    proc = run_hook("worktree_create.py", json.dumps({"worktreeName": "gamma"}), wt_repo.env)
    worktree = wt_path(wt_repo.root, "gamma")
    assert proc.returncode == 0
    assert proc.stdout == f"{worktree}\n"
    assert worktree.is_dir()
    assert "exited 1" in proc.stderr


def test_payload_without_a_name_fails_open(wt_repo, run_hook):
    """Neither worktreeName nor name: nothing to create, exit 0 with a note
    naming the fields so a payload-shape drift is diagnosable, no stdout."""
    proc = run_hook("worktree_create.py", json.dumps({"foo": "x"}), wt_repo.env)
    assert proc.returncode == 0
    assert proc.stdout == ""
    assert "worktreeName" in proc.stderr
    assert not (wt_repo.root / ".claude" / "worktrees").exists()


def test_existing_worktree_branch_is_reused(wt_repo, run_hook):
    """Re-creating a worktree whose worktree-<name> branch survives (kept at
    session exit) must resume that branch's state, not fail on a name clash
    or silently fork a second lineage."""
    wt_repo.git("branch", "worktree-reuse")
    pinned = wt_repo.git("rev-parse", "worktree-reuse").stdout.strip()
    (wt_repo.root / "later.txt").write_text("moves HEAD past the branch\n")
    wt_repo.git("add", ".")
    wt_repo.git("commit", "-m", "advance HEAD")

    proc = run_hook("worktree_create.py", json.dumps({"worktreeName": "reuse"}), wt_repo.env)
    worktree = wt_path(wt_repo.root, "reuse")
    assert proc.returncode == 0
    assert proc.stdout == f"{worktree}\n"
    head = wt_repo.git("rev-parse", "HEAD", cwd=worktree).stdout.strip()
    assert head == pinned  # the branch tip, not the advanced local HEAD


def test_new_branch_bases_on_origin_default_not_local_head(wt_repo, run_hook):
    """Worktrees must start from a clean tree matching the remote (the
    documented default-base contract), so local unpushed commits must NOT
    leak into a fresh worktree when an origin exists."""
    origin = wt_repo.tmp / "origin-repo"
    origin.mkdir()
    wt_repo.git("init", cwd=origin)
    (origin / "a.txt").write_text("a\n")
    wt_repo.git("add", ".", cwd=origin)
    wt_repo.git("commit", "-m", "base", cwd=origin)
    base_sha = wt_repo.git("rev-parse", "HEAD", cwd=origin).stdout.strip()

    clone = wt_repo.tmp / "clone"
    wt_repo.git("clone", str(origin), str(clone), cwd=wt_repo.tmp)
    (clone / "b.txt").write_text("unpushed\n")
    wt_repo.git("add", ".", cwd=clone)
    wt_repo.git("commit", "-m", "local ahead", cwd=clone)
    local_sha = wt_repo.git("rev-parse", "HEAD", cwd=clone).stdout.strip()

    env = {**wt_repo.env, "CLAUDE_PROJECT_DIR": str(clone)}
    proc = run_hook("worktree_create.py", json.dumps({"worktreeName": "fresh"}), env)
    worktree = wt_path(clone, "fresh")
    assert proc.returncode == 0
    assert proc.stdout == f"{worktree}\n"
    wt_sha = wt_repo.git("rev-parse", "HEAD", cwd=worktree).stdout.strip()
    assert wt_sha == base_sha
    assert wt_sha != local_sha


@pytest.mark.parametrize("bad_name", ["/tmp/abs", "../escape", "a/b", "a\\b", ".", ".."])
def test_path_shaped_names_are_rejected(wt_repo, run_hook, bad_name):
    """A worktree name is a NAME, not a path: absolute values discard the
    .claude/worktrees prefix entirely and traversal segments escape it, so
    every separator- or dot-shaped value must be refused up front."""
    proc = run_hook("worktree_create.py", json.dumps({"worktreeName": bad_name}), wt_repo.env)
    assert proc.returncode == 0
    assert proc.stdout == ""
    assert "invalid worktree name" in proc.stderr
    assert not (wt_repo.root / ".claude" / "worktrees").exists()


def test_worktreeinclude_copies_gitignored_files(wt_repo, run_hook):
    """The hook replaces default creation, so it owns the .worktreeinclude
    contract too: gitignored files matching a pattern must appear in the
    new worktree (a fresh checkout otherwise lacks .env and friends)."""
    (wt_repo.root / ".gitignore").write_text(".env\n")
    (wt_repo.root / ".env").write_text("SECRET=1\n")
    (wt_repo.root / ".worktreeinclude").write_text("# env files\n.env\n")
    proc = run_hook("worktree_create.py", json.dumps({"worktreeName": "inc"}), wt_repo.env)
    worktree = wt_path(wt_repo.root, "inc")
    assert proc.returncode == 0
    assert proc.stdout == f"{worktree}\n"  # the copy step must not pollute stdout
    assert (worktree / ".env").read_text() == "SECRET=1\n"


def test_worktreeinclude_never_copies_tracked_files(wt_repo, run_hook):
    """Only files that match AND are gitignored are copied: a tracked file
    matching a pattern arrives via checkout (committed state), never as a
    copy of the main checkout's uncommitted edits."""
    (wt_repo.root / "settings.txt").write_text("committed\n")
    wt_repo.git("add", "settings.txt")
    wt_repo.git("commit", "-m", "track settings")
    (wt_repo.root / "settings.txt").write_text("uncommitted local edit\n")
    (wt_repo.root / ".worktreeinclude").write_text("settings.txt\n")
    proc = run_hook("worktree_create.py", json.dumps({"worktreeName": "tracked"}), wt_repo.env)
    worktree = wt_path(wt_repo.root, "tracked")
    assert proc.returncode == 0
    assert (worktree / "settings.txt").read_text() == "committed\n"


def test_absent_worktreeinclude_is_a_noop(wt_repo, run_hook):
    """No .worktreeinclude, no copy step, no complaints -- the base contract
    is unchanged."""
    proc = run_hook("worktree_create.py", json.dumps({"worktreeName": "plain"}), wt_repo.env)
    worktree = wt_path(wt_repo.root, "plain")
    assert proc.returncode == 0
    assert proc.stdout == f"{worktree}\n"
    assert worktree.is_dir()
