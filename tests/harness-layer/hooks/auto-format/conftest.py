"""Auto-format feature fixtures: the linter_root sandbox and project_env overlay."""

import shutil
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[4]


@pytest.fixture
def project_env():
    """Env overlay pointing a format hook at a given project root."""
    return lambda root: {"CLAUDE_PROJECT_DIR": str(root)}


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
