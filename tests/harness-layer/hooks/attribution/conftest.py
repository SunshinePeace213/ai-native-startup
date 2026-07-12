"""Attribution feature fixtures: hook_dir only (the guard sits at the hooks root)."""

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[4]


@pytest.fixture
def hook_dir():
    return REPO_ROOT / ".claude" / "hooks"
