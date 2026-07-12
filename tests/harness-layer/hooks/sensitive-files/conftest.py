"""Fixtures local to the sensitive-files guard tests.

``load_guard`` loads a guard SCRIPT (``file_guard.py`` / ``bash_guard.py``)
in-process so a test can force an engine call to raise and prove the guard's
top-level ``run()`` wrapper still fails open (AC6's injected-exception clause).

A guard does ``import _common``; under ``uv run --script`` that resolves to the
sibling engine, but in-process the bare name is unbound, so we register the
engine -- loaded through the same blessed ``load_hook_module`` -- under
``_common`` just long enough for the guard to bind to it. The monkeypatch
reverts at teardown, so nothing bleeds into another family's ``sys.modules``
when the suite runs under ``-n auto``.
"""

import sys

import pytest


@pytest.fixture
def load_guard(load_hook_module, monkeypatch):
    """Return ``(guard_module, engine_module)`` for a hooks-relative guard path.

    The engine is the guard's own ``_common`` object, so monkeypatching e.g.
    ``engine.match_path`` makes the guard's real call raise.
    """

    def _load(script_rel: str):
        engine = load_hook_module("sensitive-files/_common.py")
        monkeypatch.setitem(sys.modules, "_common", engine)
        return load_hook_module(script_rel), engine

    return _load
