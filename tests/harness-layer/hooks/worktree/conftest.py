"""Worktree feature fixtures: the hermetic wt_repo sandbox.

The worktree tests get a temp git repo with one commit and stub ``bun``/``uv``
executables first on PATH that log their invocation instead of installing
anything -- fast, offline, and observable. ``wt_repo.overrides`` is the env
overlay to pass to ``run_hook`` (the launcher's base env already shuts out
the host git config); ``wt_repo.env`` is the full environment for the
fixture's own direct git calls.
"""

import os
import subprocess
from pathlib import Path
from types import SimpleNamespace

import pytest

STUB_TEMPLATE = """#!/bin/sh
printf '%s %s %s\\n' "{tool}" "$*" "$PWD" >> "{log}"
exit {code}
"""


# qmd gets its own stub so the shared log keeps its "<tool> <args> <pwd>" shape
# while the models the hook exports into qmd's environment stay observable.
QMD_STUB_TEMPLATE = """#!/bin/sh
printf '%s %s %s\\n' "qmd" "$*" "$PWD" >> "{log}"
printf '%s\\n' "${{QMD_EMBED_MODEL:-unset}}" >> "{env_log}"
exit {code}
"""


def _write_stubs(stub_dir: Path, log: Path, env_log: Path, code: int = 0) -> None:
    for tool in ("bun", "uv"):
        stub = stub_dir / tool
        stub.write_text(STUB_TEMPLATE.format(tool=tool, log=log, code=code))
        stub.chmod(0o755)
    qmd = stub_dir / "qmd"
    qmd.write_text(QMD_STUB_TEMPLATE.format(log=log, env_log=env_log, code=code))
    qmd.chmod(0o755)


def _git(env: dict, cwd: Path, check: bool, *args: str) -> subprocess.CompletedProcess:
    proc = subprocess.run(["git", *args], cwd=cwd, env=env, capture_output=True, text=True)
    if check:
        assert proc.returncode == 0, f"git {' '.join(args)} failed: {proc.stderr}"
    return proc


@pytest.fixture
def wt_repo(tmp_path):
    """Temp git repo with one commit, hermetic git env, stub bun/uv on PATH.

    Exposes: .root, .overrides (env overlay for run_hook), .env (full env for
    direct git calls), .tmp, .stub_log, .git(*args, cwd=root, check=True),
    and .fail_installs() to make the bun/uv stubs exit non-zero.
    """
    stub_dir = tmp_path / "stub-bin"
    stub_dir.mkdir()
    stub_log = tmp_path / "stub.log"
    qmd_env_log = tmp_path / "qmd-env.log"
    _write_stubs(stub_dir, stub_log, qmd_env_log)

    root = tmp_path / "repo"
    root.mkdir()
    qmd_config = tmp_path / "qmd-config"
    qmd_config.mkdir()
    overrides = {
        "PATH": f"{stub_dir}{os.pathsep}{os.environ.get('PATH', '')}",
        "CLAUDE_PROJECT_DIR": str(root),
        # Keeps the index bootstrap off the developer's real ~/.config/qmd.
        "QMD_CONFIG_DIR": str(qmd_config),
        "GIT_AUTHOR_NAME": "Test",
        "GIT_AUTHOR_EMAIL": "test@example.com",
        "GIT_COMMITTER_NAME": "Test",
        "GIT_COMMITTER_EMAIL": "test@example.com",
    }
    env = {
        **os.environ,
        **overrides,
        "GIT_CONFIG_GLOBAL": os.devnull,
        "GIT_CONFIG_SYSTEM": os.devnull,
    }
    repo = SimpleNamespace(
        root=root,
        overrides=overrides,
        env=env,
        tmp=tmp_path,
        stub_log=stub_log,
        qmd_env_log=qmd_env_log,
        qmd_config=qmd_config,
        git=lambda *args, cwd=root, check=True: _git(env, cwd, check, *args),
        fail_installs=lambda: _write_stubs(stub_dir, stub_log, qmd_env_log, code=1),
    )
    repo.git("init")
    (root / "README.md").write_text("seed\n")
    repo.git("add", ".")
    repo.git("commit", "-m", "init")
    return repo
