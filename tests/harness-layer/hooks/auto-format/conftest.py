"""Auto-format feature fixtures: hook_dir plus the linter_root sandbox."""

import shutil
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[4]


@pytest.fixture
def hook_dir():
    return REPO_ROOT / ".claude" / "hooks" / "auto-format"


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
