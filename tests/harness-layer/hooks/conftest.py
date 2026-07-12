"""Cross-feature fixtures shared by every hook test dir.

Every hook is launched through the REAL uv (absolute path, resolved before
any PATH games) exactly as Claude Code would run it, so the production
entry path is what gets exercised. `run_hook` resolves scripts against the
`hook_dir` fixture below -- declared here with no default so each feature
dir (auto-format/, attribution/, worktree/) must override it to say where
its own scripts live.
"""

import shutil
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
UV = shutil.which("uv")  # absolute, so PATH stubs can never hijack the hook launcher
assert UV, "uv is required to run the hook tests"


@pytest.fixture
def hook_dir():
    raise NotImplementedError("hook_dir has no default -- override it in a feature conftest.py")


@pytest.fixture
def run_hook(hook_dir):
    """Feed a stdin payload to a hook exactly as Claude Code would run it."""

    def _run(script_name: str, payload: str, env: dict) -> subprocess.CompletedProcess:
        return subprocess.run(
            [UV, "run", "--script", str(hook_dir / script_name)],
            input=payload,
            capture_output=True,
            text=True,
            timeout=120,
            env=env,
        )

    return _run
