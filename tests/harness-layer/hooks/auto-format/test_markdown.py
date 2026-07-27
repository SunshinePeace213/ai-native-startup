"""Contract tests for the Markdown format hook (markdown.py).

Markdown is the repo's memory and spec medium, so the hook's job is to
keep agent-written docs lint-clean without agent effort: fixable rules
(blank-line runs, spacing) are fixed silently with exit 0, while rules
--fix cannot solve (like heading-increment) come back as exit 2 with the
rule id so the agent can rewrite the structure itself. Plumbing problems
-- wrong extension, garbage stdin, missing binary -- exit 0 untouched.
"""

import json


def test_two_file_apply_patch_envelope_formats_both(
    linter_root, run_hook, apply_patch_payload, project_env
):
    """AC11: a two-file apply_patch payload where both files match this
    hook's extension must format both, not just the first."""
    a, b = linter_root / "a.md", linter_root / "b.md"
    a.write_text("# Title\n\n\n\ntext\n")
    b.write_text("# Other\n\n\n\ntext\n")
    payload = apply_patch_payload(f"*** Add File: {a}", f"*** Add File: {b}")
    proc = run_hook("auto-format/markdown.py", payload, env_overrides=project_env(linter_root))
    assert proc.returncode == 0
    assert "\n\n\n" not in a.read_text()
    assert "\n\n\n" not in b.read_text()


def test_malformed_apply_patch_envelope_fails_open(linter_root, run_hook, project_env):
    """AC14: an unparseable apply_patch envelope must format nothing and
    exit 0 on the Codex host, mirroring the Claude-side fail-open contract."""
    payload = json.dumps({"tool_name": "apply_patch", "tool_input": {"command": "not a patch"}})
    proc = run_hook("auto-format/markdown.py", payload, env_overrides=project_env(linter_root))
    assert proc.returncode == 0


def test_fixable_violation_is_fixed_in_place(linter_root, run_hook, edit_payload, project_env):
    """MD012 (multiple blank lines) is autofixable: the file is repaired
    silently, exit 0, no agent involvement."""
    fixture = linter_root / "doc.md"
    fixture.write_text("# Title\n\n\n\ntext\n")
    proc = run_hook(
        "auto-format/markdown.py", edit_payload(fixture), env_overrides=project_env(linter_root)
    )
    assert proc.returncode == 0
    assert "\n\n\n" not in fixture.read_text()


def test_unfixable_violation_exits_2_with_rule_id(linter_root, run_hook, edit_payload, project_env):
    """MD001 (heading increment) cannot be autofixed -- the agent must
    restructure, so stderr must carry the rule id and location."""
    fixture = linter_root / "bad.md"
    fixture.write_text("# A\n\n### B\n")
    proc = run_hook(
        "auto-format/markdown.py", edit_payload(fixture), env_overrides=project_env(linter_root)
    )
    assert proc.returncode == 2
    assert "MD001" in proc.stderr
    assert "bad.md:3" in proc.stderr


def test_non_matching_extension_is_ignored(linter_root, run_hook, edit_payload, project_env):
    """Extension filtering is the hook's job: .rst is not this hook's file."""
    fixture = linter_root / "doc.rst"
    fixture.write_text("# A\n\n### B\n")
    proc = run_hook(
        "auto-format/markdown.py", edit_payload(fixture), env_overrides=project_env(linter_root)
    )
    assert proc.returncode == 0
    assert fixture.read_text() == "# A\n\n### B\n"


def test_malformed_stdin_fails_open(linter_root, run_hook, project_env):
    """Garbage stdin is a harness bug, not a lint error -- never exit 2."""
    proc = run_hook("auto-format/markdown.py", "not json {", env_overrides=project_env(linter_root))
    assert proc.returncode == 0


def test_missing_binary_notes_meta_install(tmp_path, run_hook, edit_payload, project_env):
    """A fresh clone has no node_modules: skip with a note naming the
    meta-install skill, file untouched."""
    bare = tmp_path / "bare"
    bare.mkdir()
    fixture = bare / "doc.md"
    fixture.write_text("# A\n\n### B\n")
    proc = run_hook(
        "auto-format/markdown.py", edit_payload(fixture), env_overrides=project_env(bare)
    )
    assert proc.returncode == 0
    assert "meta-install" in proc.stderr
    assert fixture.read_text() == "# A\n\n### B\n"
