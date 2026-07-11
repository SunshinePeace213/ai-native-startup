"""Contract tests for the JSON/YAML format hook (data.py).

YAML belongs to this hook by decision record: markdownlint cannot process
YAML at all, Prettier is the repo's YAML formatter -- so the tests pin
both families. Exit 2 is reserved for genuine parse errors (the one data
defect an agent must go fix); every plumbing problem -- wrong extension,
garbage stdin, missing Prettier -- exits 0 with the file untouched.
"""

import json
import os


def edit_payload(path) -> str:
    return json.dumps({"tool_name": "Write", "tool_input": {"file_path": str(path)}})


def env_for(root) -> dict:
    return {**os.environ, "CLAUDE_PROJECT_DIR": str(root)}


def test_json_is_formatted_in_place(linter_root, run_hook):
    """Compact JSON comes back in Prettier style with exit 0 -- the agent
    never has to think about data formatting."""
    fixture = linter_root / "config.json"
    fixture.write_text('{"a":1}')
    proc = run_hook("data.py", edit_payload(fixture), env_for(linter_root))
    assert proc.returncode == 0
    assert fixture.read_text() == '{ "a": 1 }\n'


def test_yaml_is_formatted_in_place(linter_root, run_hook):
    """YAML rides the data hook (Prettier formats it; markdownlint cannot)."""
    fixture = linter_root / "config.yaml"
    fixture.write_text("a:   1\n")
    proc = run_hook("data.py", edit_payload(fixture), env_for(linter_root))
    assert proc.returncode == 0
    assert fixture.read_text() == "a: 1\n"


def test_invalid_json_exits_2_with_parse_error(linter_root, run_hook):
    """A parse error is a real defect the agent must fix: exit 2 with
    Prettier's SyntaxError naming the offending file."""
    fixture = linter_root / "broken.json"
    fixture.write_text('{"a":,}')
    proc = run_hook("data.py", edit_payload(fixture), env_for(linter_root))
    assert proc.returncode == 2
    assert "SyntaxError" in proc.stderr
    assert "broken.json" in proc.stderr


def test_broken_prettier_config_is_infrastructure_not_exit_2(linter_root, run_hook):
    """Prettier config errors name the target file too ("Invalid configuration
    for file ..."), but they are tooling trouble the agent cannot fix by
    editing its data file: exit 0 with a note, never exit 2."""
    (linter_root / ".prettierrc.json").write_text("{not json")
    fixture = linter_root / "sample.json"
    fixture.write_text('{"a":1}')
    proc = run_hook("data.py", edit_payload(fixture), env_for(linter_root))
    assert proc.returncode == 0
    assert fixture.read_text() == '{"a":1}'  # untouched
    assert "[data]" in proc.stderr


def test_non_matching_extension_is_ignored(linter_root, run_hook):
    """Extension filtering is the hook's job: .toml is not this hook's file."""
    fixture = linter_root / "config.toml"
    fixture.write_text("a=1\n")
    proc = run_hook("data.py", edit_payload(fixture), env_for(linter_root))
    assert proc.returncode == 0
    assert fixture.read_text() == "a=1\n"


def test_malformed_stdin_fails_open(linter_root, run_hook):
    """Garbage stdin is a harness bug, not a parse error -- never exit 2."""
    proc = run_hook("data.py", "not json {", env_for(linter_root))
    assert proc.returncode == 0


def test_missing_prettier_notes_meta_install(tmp_path, run_hook):
    """A fresh clone has no node_modules: skip with a note naming the
    meta-install skill, file untouched."""
    bare = tmp_path / "bare"
    bare.mkdir()
    fixture = bare / "x.json"
    fixture.write_text('{"a":1}')
    proc = run_hook("data.py", edit_payload(fixture), env_for(bare))
    assert proc.returncode == 0
    assert "meta-install" in proc.stderr
    assert fixture.read_text() == '{"a":1}'
