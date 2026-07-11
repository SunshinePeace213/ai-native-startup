"""Contract tests for the Python format hook (python.py).

The hook runs the repo's pinned ruff through ``uv run --no-sync``, so the
project root is the REAL repo here (its .venv carries ruff) while fixtures
live in tmp -- which doubles as coverage for formatting files outside the
project root. Fixable problems (quote style, unused imports) are repaired
silently; violations --fix cannot solve exit 2 with the ruff rule code and
a capped diagnostic list; a root with no Python toolchain at all is
infrastructure and must fail open, never masquerade as lint errors.
"""

import json
import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]


def edit_payload(path) -> str:
    return json.dumps({"tool_name": "Edit", "tool_input": {"file_path": str(path)}})


def env_for(root) -> dict:
    return {**os.environ, "CLAUDE_PROJECT_DIR": str(root)}


def test_fixable_file_is_formatted_and_autofixed(tmp_path, run_hook):
    """Both ruff stages must land: format (quote style) and check --fix
    (unused import removed) -- the agent's edit is normalized for free."""
    fixture = tmp_path / "fix.py"
    fixture.write_text("import os\nx = 'a'\n")
    proc = run_hook("python.py", edit_payload(fixture), env_for(REPO_ROOT))
    content = fixture.read_text()
    assert proc.returncode == 0
    assert 'x = "a"' in content  # ruff format applied
    assert "import os" not in content  # ruff check --fix removed F401


def test_unfixable_violation_exits_2_with_rule_code(tmp_path, run_hook):
    """An undefined name is the agent's bug to fix: exit 2 with the ruff
    rule code and a file:line:col locator."""
    fixture = tmp_path / "bad.py"
    fixture.write_text("print(undefined_name)\n")
    proc = run_hook("python.py", edit_payload(fixture), env_for(REPO_ROOT))
    assert proc.returncode == 2
    assert "F821" in proc.stderr
    assert "bad.py:1:" in proc.stderr


def test_diagnostics_are_capped_with_tail(tmp_path, run_hook):
    """Exit-2 stderr goes straight to the agent: past ten findings the list
    is cut and the remainder summarized, so feedback stays actionable."""
    fixture = tmp_path / "many.py"
    fixture.write_text("".join(f"print(undefined_{i})\n" for i in range(15)))
    proc = run_hook("python.py", edit_payload(fixture), env_for(REPO_ROOT))
    assert proc.returncode == 2
    lines = proc.stderr.strip().splitlines()
    assert len(lines) == 11  # 10 diagnostics + the tail
    assert lines[-1] == "... and 5 more"


def test_non_matching_extension_is_ignored(tmp_path, run_hook):
    """Extension filtering is the hook's job: .txt is not this hook's file."""
    fixture = tmp_path / "notes.txt"
    fixture.write_text("x = 'a'\n")
    proc = run_hook("python.py", edit_payload(fixture), env_for(REPO_ROOT))
    assert proc.returncode == 0
    assert fixture.read_text() == "x = 'a'\n"


def test_malformed_stdin_fails_open(tmp_path, run_hook):
    """Garbage stdin is a harness bug, not a lint error -- never exit 2."""
    proc = run_hook("python.py", "not json {", env_for(REPO_ROOT))
    assert proc.returncode == 0


def toolchainless_env(root) -> dict:
    """Env modelling a fresh clone: no venv on PATH, no VIRTUAL_ENV (pytest's
    own venv would otherwise leak ruff into the hook's environment)."""
    env = env_for(root)
    env.pop("VIRTUAL_ENV", None)
    env["PATH"] = os.pathsep.join(p for p in env["PATH"].split(os.pathsep) if ".venv" not in p)
    return env


def test_missing_toolchain_fails_open_untouched(tmp_path, run_hook):
    """A root with no Python project (uv cannot run ruff there) is
    infrastructure, not lint: exit 0, file untouched, and the note names
    the meta-install skill -- never bogus exit-2 diagnostics."""
    bare = tmp_path / "bare"
    bare.mkdir()
    fixture = bare / "x.py"
    fixture.write_text("x = 'a'\n")
    proc = run_hook("python.py", edit_payload(fixture), toolchainless_env(bare))
    assert proc.returncode == 0
    assert fixture.read_text() == "x = 'a'\n"
    assert "meta-install" in proc.stderr


def test_ruff_missing_from_project_notes_meta_install(tmp_path, run_hook):
    """uv present but ruff absent (a project env without ruff): uv fails to
    spawn ruff, and the note must name the meta-install skill -- a generic
    uv error would leave the agent without the actual fix (AC6)."""
    proj = tmp_path / "proj"
    proj.mkdir()
    (proj / "pyproject.toml").write_text(
        '[project]\nname = "t"\nversion = "0.1.0"\nrequires-python = ">=3.12"\n'
    )
    fixture = proj / "x.py"
    fixture.write_text("x = 'a'\n")
    proc = run_hook("python.py", edit_payload(fixture), toolchainless_env(proj))
    assert proc.returncode == 0
    assert fixture.read_text() == "x = 'a'\n"
    assert "meta-install" in proc.stderr
