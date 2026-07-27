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

REPO_ROOT = Path(__file__).resolve().parents[4]


def test_two_file_apply_patch_envelope_formats_both(
    tmp_path, run_hook, apply_patch_payload, project_env
):
    """AC11: a two-file apply_patch payload where both files match this
    hook's extension must format both, not just the first."""
    a, b = tmp_path / "a.py", tmp_path / "b.py"
    a.write_text("import os\nx = 'a'\n")
    b.write_text("import sys\ny = 'b'\n")
    payload = apply_patch_payload(f"*** Add File: {a}", f"*** Add File: {b}")
    proc = run_hook("auto-format/python.py", payload, env_overrides=project_env(REPO_ROOT))
    assert proc.returncode == 0
    assert "import os" not in a.read_text()
    assert "import sys" not in b.read_text()


def test_failure_on_one_path_does_not_skip_the_rest(
    tmp_path, run_hook, apply_patch_payload, project_env
):
    """AC11: an unfixable violation in one envelope file must not stop a
    sibling file in the same envelope from being formatted -- the whole
    point of looping over every edited path instead of just the first."""
    bad, good = tmp_path / "bad.py", tmp_path / "good.py"
    bad.write_text("print(undefined_name)\n")
    good.write_text("import os\nx = 'a'\n")
    payload = apply_patch_payload(f"*** Add File: {bad}", f"*** Add File: {good}")
    proc = run_hook("auto-format/python.py", payload, env_overrides=project_env(REPO_ROOT))
    assert proc.returncode == 2
    assert "F821" in proc.stderr
    assert "import os" not in good.read_text()  # good.py still formatted despite bad.py's failure


def test_rename_formats_the_new_path_not_the_old(
    tmp_path, run_hook, apply_patch_payload, project_env
):
    """A rename's old path no longer exists on disk once apply_patch has
    run, so the deleted-file guard drops it and the new path -- the one
    that exists -- is the one formatted, with no rename-specific code."""
    old, new = tmp_path / "old.py", tmp_path / "new.py"
    new.write_text("import os\nx = 'a'\n")  # only the new path exists post-rename
    payload = apply_patch_payload(f"*** Update File: {old}", f"*** Move to: {new}")
    proc = run_hook("auto-format/python.py", payload, env_overrides=project_env(REPO_ROOT))
    assert proc.returncode == 0
    assert "import os" not in new.read_text()


def test_malformed_apply_patch_envelope_fails_open(tmp_path, run_hook, project_env):
    """AC14: an unparseable apply_patch envelope must format nothing and
    exit 0 on the Codex host, mirroring the Claude-side fail-open contract."""
    payload = json.dumps({"tool_name": "apply_patch", "tool_input": {"command": "not a patch"}})
    proc = run_hook("auto-format/python.py", payload, env_overrides=project_env(REPO_ROOT))
    assert proc.returncode == 0


def test_fixable_file_is_formatted_and_autofixed(tmp_path, run_hook, edit_payload, project_env):
    """Both ruff stages must land: format (quote style) and check --fix
    (unused import removed) -- the agent's edit is normalized for free."""
    fixture = tmp_path / "fix.py"
    fixture.write_text("import os\nx = 'a'\n")
    proc = run_hook(
        "auto-format/python.py", edit_payload(fixture), env_overrides=project_env(REPO_ROOT)
    )
    content = fixture.read_text()
    assert proc.returncode == 0
    assert 'x = "a"' in content  # ruff format applied
    assert "import os" not in content  # ruff check --fix removed F401


def test_unfixable_violation_exits_2_with_rule_code(tmp_path, run_hook, edit_payload, project_env):
    """An undefined name is the agent's bug to fix: exit 2 with the ruff
    rule code and a file:line:col locator."""
    fixture = tmp_path / "bad.py"
    fixture.write_text("print(undefined_name)\n")
    proc = run_hook(
        "auto-format/python.py", edit_payload(fixture), env_overrides=project_env(REPO_ROOT)
    )
    assert proc.returncode == 2
    assert "F821" in proc.stderr
    assert "bad.py:1:" in proc.stderr


def test_diagnostics_are_capped_with_tail(tmp_path, run_hook, edit_payload, project_env):
    """Exit-2 stderr goes straight to the agent: past ten findings the list
    is cut and the remainder summarized, so feedback stays actionable."""
    fixture = tmp_path / "many.py"
    fixture.write_text("".join(f"print(undefined_{i})\n" for i in range(15)))
    proc = run_hook(
        "auto-format/python.py", edit_payload(fixture), env_overrides=project_env(REPO_ROOT)
    )
    assert proc.returncode == 2
    lines = proc.stderr.strip().splitlines()
    assert len(lines) == 11  # 10 diagnostics + the tail
    assert lines[-1] == "... and 5 more"


def test_non_matching_extension_is_ignored(tmp_path, run_hook, edit_payload, project_env):
    """Extension filtering is the hook's job: .txt is not this hook's file."""
    fixture = tmp_path / "notes.txt"
    fixture.write_text("x = 'a'\n")
    proc = run_hook(
        "auto-format/python.py", edit_payload(fixture), env_overrides=project_env(REPO_ROOT)
    )
    assert proc.returncode == 0
    assert fixture.read_text() == "x = 'a'\n"


def test_malformed_stdin_fails_open(tmp_path, run_hook, project_env):
    """Garbage stdin is a harness bug, not a lint error -- never exit 2."""
    proc = run_hook("auto-format/python.py", "not json {", env_overrides=project_env(REPO_ROOT))
    assert proc.returncode == 0


def venvless(root, project_env) -> dict:
    """Env overlay modelling a fresh clone: no venv on PATH (pytest's own venv
    would otherwise leak ruff into the hook's environment)."""
    path = os.pathsep.join(
        p for p in os.environ.get("PATH", "").split(os.pathsep) if ".venv" not in p
    )
    return {**project_env(root), "PATH": path}


def test_missing_toolchain_fails_open_untouched(tmp_path, run_hook, edit_payload, project_env):
    """A root with no Python project (uv cannot run ruff there) is
    infrastructure, not lint: exit 0, file untouched, and the note names
    the meta-install skill -- never bogus exit-2 diagnostics."""
    bare = tmp_path / "bare"
    bare.mkdir()
    fixture = bare / "x.py"
    fixture.write_text("x = 'a'\n")
    proc = run_hook(
        "auto-format/python.py",
        edit_payload(fixture),
        env_overrides=venvless(bare, project_env),
        unset_env=("VIRTUAL_ENV",),
    )
    assert proc.returncode == 0
    assert fixture.read_text() == "x = 'a'\n"
    assert "meta-install" in proc.stderr


def test_ruff_missing_from_project_notes_meta_install(
    tmp_path, run_hook, edit_payload, project_env
):
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
    proc = run_hook(
        "auto-format/python.py",
        edit_payload(fixture),
        env_overrides=venvless(proj, project_env),
        unset_env=("VIRTUAL_ENV",),
    )
    assert proc.returncode == 0
    assert fixture.read_text() == "x = 'a'\n"
    assert "meta-install" in proc.stderr
