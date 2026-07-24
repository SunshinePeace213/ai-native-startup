"""Cross-feature fixtures shared by every hook test dir.

Every hook is a uv script, and `run_hook` is the ONE launcher: it runs the
script through the REAL uv (absolute path, resolved before any test touches
PATH) exactly as Claude Code would, addressed RELATIVE to .claude/hooks
("auto-format/python.py") so no per-feature launcher can drift. The base
environment is git-isolated -- the developer's git config is shut out and
the repo-routing GIT_* variables are scrubbed -- so a hook under test can
never read or touch the host's git state by accident. Tests express intent
with `env_overrides` / `unset_env` instead of hand-building environments.

`load_hook_module` (the blessed way to import a hook module in-process)
lives in the parent tests/harness-layer/conftest.py so the prompts suite
can share it too; hook tests keep resolving it there via pytest's normal
conftest lookup.
"""

import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
HOOKS_ROOT = REPO_ROOT / ".claude" / "hooks"
UV = shutil.which("uv")  # absolute, so PATH stubs can never hijack the hook launcher
assert UV, "uv is required to run the hook tests"

# Vars that would route git at the developer's own repo/index: never inherited.
GIT_ROUTING_VARS = ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE")


def base_env() -> dict:
    """Copied process env with git configuration isolated out."""
    env = os.environ.copy()
    env["GIT_CONFIG_GLOBAL"] = os.devnull
    env["GIT_CONFIG_SYSTEM"] = os.devnull
    for var in GIT_ROUTING_VARS:
        env.pop(var, None)
    return env


@pytest.fixture
def run_hook():
    """Feed a stdin payload to a hook exactly as Claude Code would run it."""

    def _run(
        script: str,
        payload: str,
        *,
        env_overrides: dict | None = None,
        unset_env: tuple = (),
        cwd: Path = REPO_ROOT,
    ) -> subprocess.CompletedProcess:
        env = base_env()
        for name in unset_env:
            env.pop(name, None)
        env.update(env_overrides or {})
        return subprocess.run(
            [UV, "run", "--script", str(HOOKS_ROOT / script)],
            input=payload,
            capture_output=True,
            text=True,
            timeout=45,  # under pytest-timeout's 60s, so the test still reports
            env=env,
            cwd=cwd,
        )

    return _run


@pytest.fixture
def edit_payload():
    """The Write/Edit payload shape the harness sends to file-scoped hooks."""

    def _payload(path, tool_name: str = "Edit") -> str:
        return json.dumps({"tool_name": tool_name, "tool_input": {"file_path": str(path)}})

    return _payload
