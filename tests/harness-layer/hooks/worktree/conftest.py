"""Worktree feature fixtures: hook_dir plus the hermetic wt_repo sandbox.

The worktree tests get a temp git repo with one commit (host git config shut
out via GIT_CONFIG_GLOBAL/SYSTEM) and stub ``bun``/``uv`` executables first on
PATH that log their invocation instead of installing anything -- fast,
offline, and observable.
"""

import os
import subprocess
from pathlib import Path
from types import SimpleNamespace

import pytest

REPO_ROOT = Path(__file__).resolve().parents[4]

STUB_TEMPLATE = """#!/bin/sh
printf '%s %s %s\\n' "{tool}" "$*" "$PWD" >> "{log}"
exit {code}
"""


@pytest.fixture
def hook_dir():
    return REPO_ROOT / ".claude" / "hooks" / "worktree"


def _write_stubs(stub_dir: Path, log: Path, code: int = 0) -> None:
    for tool in ("bun", "uv"):
        stub = stub_dir / tool
        stub.write_text(STUB_TEMPLATE.format(tool=tool, log=log, code=code))
        stub.chmod(0o755)


def _git(env: dict, cwd: Path, check: bool, *args: str) -> subprocess.CompletedProcess:
    proc = subprocess.run(["git", *args], cwd=cwd, env=env, capture_output=True, text=True)
    if check:
        assert proc.returncode == 0, f"git {' '.join(args)} failed: {proc.stderr}"
    return proc


@pytest.fixture
def wt_repo(tmp_path):
    """Temp git repo with one commit, hermetic git env, stub bun/uv on PATH.

    Exposes: .root, .env, .tmp, .stub_log, .git(*args, cwd=root, check=True),
    and .fail_installs() to make the bun/uv stubs exit non-zero.
    """
    stub_dir = tmp_path / "stub-bin"
    stub_dir.mkdir()
    stub_log = tmp_path / "stub.log"
    _write_stubs(stub_dir, stub_log)

    root = tmp_path / "repo"
    root.mkdir()
    env = {
        **os.environ,
        "PATH": f"{stub_dir}{os.pathsep}{os.environ.get('PATH', '')}",
        "CLAUDE_PROJECT_DIR": str(root),
        "GIT_CONFIG_GLOBAL": os.devnull,
        "GIT_CONFIG_SYSTEM": os.devnull,
        "GIT_AUTHOR_NAME": "Test",
        "GIT_AUTHOR_EMAIL": "test@example.com",
        "GIT_COMMITTER_NAME": "Test",
        "GIT_COMMITTER_EMAIL": "test@example.com",
    }
    repo = SimpleNamespace(
        root=root,
        env=env,
        tmp=tmp_path,
        stub_log=stub_log,
        git=lambda *args, cwd=root, check=True: _git(env, cwd, check, *args),
        fail_installs=lambda: _write_stubs(stub_dir, stub_log, code=1),
    )
    repo.git("init")
    (root / "README.md").write_text("seed\n")
    repo.git("add", ".")
    repo.git("commit", "-m", "init")
    return repo
