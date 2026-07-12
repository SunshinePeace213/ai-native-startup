"""Contract tests for the Markdown format hook (markdown.py).

Markdown is the repo's memory and spec medium, so the hook's job is to
keep agent-written docs lint-clean without agent effort: fixable rules
(blank-line runs, spacing) are fixed silently with exit 0, while rules
--fix cannot solve (like heading-increment) come back as exit 2 with the
rule id so the agent can rewrite the structure itself. Plumbing problems
-- wrong extension, garbage stdin, missing binary -- exit 0 untouched.
"""

import json
import os


def edit_payload(path) -> str:
    return json.dumps({"tool_name": "Edit", "tool_input": {"file_path": str(path)}})


def env_for(root) -> dict:
    return {**os.environ, "CLAUDE_PROJECT_DIR": str(root)}


def test_fixable_violation_is_fixed_in_place(linter_root, run_hook):
    """MD012 (multiple blank lines) is autofixable: the file is repaired
    silently, exit 0, no agent involvement."""
    fixture = linter_root / "doc.md"
    fixture.write_text("# Title\n\n\n\ntext\n")
    proc = run_hook("markdown.py", edit_payload(fixture), env_for(linter_root))
    assert proc.returncode == 0
    assert "\n\n\n" not in fixture.read_text()


def test_unfixable_violation_exits_2_with_rule_id(linter_root, run_hook):
    """MD001 (heading increment) cannot be autofixed -- the agent must
    restructure, so stderr must carry the rule id and location."""
    fixture = linter_root / "bad.md"
    fixture.write_text("# A\n\n### B\n")
    proc = run_hook("markdown.py", edit_payload(fixture), env_for(linter_root))
    assert proc.returncode == 2
    assert "MD001" in proc.stderr
    assert "bad.md:3" in proc.stderr


def test_non_matching_extension_is_ignored(linter_root, run_hook):
    """Extension filtering is the hook's job: .rst is not this hook's file."""
    fixture = linter_root / "doc.rst"
    fixture.write_text("# A\n\n### B\n")
    proc = run_hook("markdown.py", edit_payload(fixture), env_for(linter_root))
    assert proc.returncode == 0
    assert fixture.read_text() == "# A\n\n### B\n"


def test_malformed_stdin_fails_open(linter_root, run_hook):
    """Garbage stdin is a harness bug, not a lint error -- never exit 2."""
    proc = run_hook("markdown.py", "not json {", env_for(linter_root))
    assert proc.returncode == 0


def test_missing_binary_notes_meta_install(tmp_path, run_hook):
    """A fresh clone has no node_modules: skip with a note naming the
    meta-install skill, file untouched."""
    bare = tmp_path / "bare"
    bare.mkdir()
    fixture = bare / "doc.md"
    fixture.write_text("# A\n\n### B\n")
    proc = run_hook("markdown.py", edit_payload(fixture), env_for(bare))
    assert proc.returncode == 0
    assert "meta-install" in proc.stderr
    assert fixture.read_text() == "# A\n\n### B\n"
