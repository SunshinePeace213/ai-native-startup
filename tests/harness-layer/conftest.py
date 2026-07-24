"""Fixtures shared across every tests/harness-layer/ subdirectory.

`load_hook_module` lives here (promoted from hooks/conftest.py) so the
prompts suite can import a hook module -- e.g. check_spec_completeness.py's
REQUIRED_SECTIONS, for the hook<->template cross-consistency asserts -- with
the same collision-safe loader the hooks suite uses, without sys.path
tricks or a package import that doesn't exist for these standalone scripts.
"""

import importlib.util
import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
HOOKS_ROOT = REPO_ROOT / ".claude" / "hooks"


@pytest.fixture(scope="session")
def load_hook_module():
    """Import a hook module under a name derived from its hooks-relative path
    (auto-format/_common.py -> auto_format__common), cached per worker."""
    cache: dict = {}

    def _load(rel_path: str):
        if rel_path not in cache:
            name = re.sub(r"\W", "_", rel_path.removesuffix(".py"))
            spec = importlib.util.spec_from_file_location(name, HOOKS_ROOT / rel_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            cache[rel_path] = module
        return cache[rel_path]

    return _load
