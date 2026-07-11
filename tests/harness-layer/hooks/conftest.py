"""Shared fixtures for the auto-format hook tests.

Every hook is launched through the REAL uv (absolute path, resolved before
any PATH games) exactly as Claude Code would run it, so the production
entry path is what gets exercised. The worktree tests get a hermetic
sandbox: a temp git repo with one commit (host git config shut out via
GIT_CONFIG_GLOBAL/SYSTEM) and stub ``bun``/``uv`` executables first on
PATH that log their invocation instead of installing anything -- fast,
offline, and observable. The format-hook tests get ``linter_root``: an
isolated "project root" wired to the repo's real linters, so fixtures
never touch the actual working tree.
"""

import os
import shutil
import subprocess
from pathlib import Path
from types import SimpleNamespace

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
HOOK_DIR = REPO_ROOT / ".claude" / "hooks" / "auto-format"
UV = shutil.which("uv")  # absolute, so PATH stubs can never hijack the hook launcher
assert UV, "uv is required to run the hook tests"

STUB_TEMPLATE = """#!/bin/sh
printf '%s %s %s\\n' "{tool}" "$*" "$PWD" >> "{log}"
exit {code}
"""


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


@pytest.fixture
def linter_root(tmp_path):
    """Isolated 'project root' with the repo's real linters: node_modules is
    symlinked and the formatter configs copied, so hooks resolve binaries and
    configs exactly as in the repo while fixtures stay out of the working tree."""
    root = tmp_path / "project"
    root.mkdir()
    (root / "node_modules").symlink_to(REPO_ROOT / "node_modules", target_is_directory=True)
    for cfg in ("eslint.config.mjs", ".prettierrc.json", ".markdownlint.jsonc"):
        shutil.copy(REPO_ROOT / cfg, root / cfg)
    return root


@pytest.fixture
def run_hook():
    """Feed a stdin payload to a hook exactly as Claude Code would run it."""

    def _run(script_name: str, payload: str, env: dict) -> subprocess.CompletedProcess:
        return subprocess.run(
            [UV, "run", "--script", str(HOOK_DIR / script_name)],
            input=payload,
            capture_output=True,
            text=True,
            timeout=120,
            env=env,
        )

    return _run
