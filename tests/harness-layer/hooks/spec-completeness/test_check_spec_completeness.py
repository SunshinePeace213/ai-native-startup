"""Contract tests for the spec-completeness Stop gate (check_spec_completeness.py).

The gate is command-scoped (registered by /harness-layer:harness-plan, NOT in
settings.json), so it must never fire outside a planning run -- a root with no
specs/ dir passes silently. Inside a run it gates the NEWEST plan folder across
the main specs/ AND every worktree's specs/ (plans draft in a worktree; missing
the worktree dirs was a real shipped bug), excluding _templates. Exit 2 must
name exactly what is missing -- file or '## section' -- because stderr is the
agent's only repair instruction. Complete plans are built from the hook's own
REQUIRED_SECTIONS via load_hook_module, so a rule change cannot silently
diverge from the tests.
"""

import json
import os
from pathlib import Path

import pytest

STOP_PAYLOAD = json.dumps({"stop_hook_active": False})


@pytest.fixture
def sections(load_hook_module):
    return load_hook_module("check_spec_completeness.py").REQUIRED_SECTIONS


def write_plan(specs: Path, name: str, sections: dict) -> Path:
    """A plan folder whose four files carry every required section."""
    folder = specs / name
    folder.mkdir(parents=True)
    for fname, secs in sections.items():
        body = "\n\n".join(f"## {sec}\n\ncontent" for sec in secs)
        (folder / fname).write_text(f"# {name}\n\n{body}\n")
    return folder


def set_mtime(folder: Path, epoch: float) -> None:
    os.utime(folder, (epoch, epoch))


def gate(run_hook, root: Path):
    return run_hook(
        "check_spec_completeness.py",
        STOP_PAYLOAD,
        env_overrides={"CLAUDE_PROJECT_DIR": str(root)},
    )


def test_no_specs_dir_allows_stop(tmp_path, run_hook):
    """Command-scoped or not, a project without specs/ has nothing to gate --
    the hook must be invisible there."""
    proc = gate(run_hook, tmp_path)
    assert proc.returncode == 0
    assert proc.stderr == ""


def test_specs_with_only_templates_blocks_as_no_plan(tmp_path, run_hook):
    """_templates is scaffolding, not a plan: a planning run that produced no
    plan folder must not be allowed to end."""
    (tmp_path / "specs" / "_templates").mkdir(parents=True)
    proc = gate(run_hook, tmp_path)
    assert proc.returncode == 2
    assert "no plan folder found" in proc.stderr


def test_complete_plan_allows_stop(tmp_path, run_hook, sections):
    """All four files present with every required section: the gate opens."""
    write_plan(tmp_path / "specs", "my-plan", sections)
    proc = gate(run_hook, tmp_path)
    assert proc.returncode == 0
    assert proc.stderr == ""


def test_missing_file_blocks_naming_it(tmp_path, run_hook, sections):
    """A absent spec file is named outright so the agent knows what to write."""
    folder = write_plan(tmp_path / "specs", "my-plan", sections)
    (folder / "tasks.md").unlink()
    proc = gate(run_hook, tmp_path)
    assert proc.returncode == 2
    assert "MISSING FILE: tasks.md" in proc.stderr
    assert "compare against specs/_templates/" in proc.stderr


def test_missing_section_blocks_naming_file_and_heading(tmp_path, run_hook, sections):
    """A gutted section is named as file + '## heading' -- the exact repair."""
    folder = write_plan(tmp_path / "specs", "my-plan", sections)
    spec = folder / "spec.md"
    spec.write_text(spec.read_text().replace("## Red Flags", "## Renamed"))
    proc = gate(run_hook, tmp_path)
    assert proc.returncode == 2
    assert "spec.md: missing section '## Red Flags'" in proc.stderr


def test_newest_plan_folder_is_the_gated_one(tmp_path, run_hook, sections):
    """Only the plan being drafted NOW is gated: an old complete plan must not
    mask a fresh incomplete one, and vice versa the old one is never re-gated."""
    specs = tmp_path / "specs"
    old = write_plan(specs, "old-complete", sections)
    fresh = write_plan(specs, "fresh-incomplete", sections)
    (fresh / "decisions.md").unlink()
    set_mtime(old, 1_000_000_000)
    set_mtime(fresh, 2_000_000_000)
    proc = gate(run_hook, tmp_path)
    assert proc.returncode == 2
    assert "fresh-incomplete" in proc.stderr


def test_worktree_specs_are_discovered(tmp_path, run_hook, sections):
    """/harness-layer:harness-plan drafts inside a worktree: a plan folder under
    .claude/worktrees/*/specs must be gated exactly like one in the main specs/
    (missing this was the bug the hook was recently fixed for)."""
    main = write_plan(tmp_path / "specs", "main-complete", sections)
    wt_specs = tmp_path / ".claude" / "worktrees" / "draft-wt" / "specs"
    wt = write_plan(wt_specs, "wt-incomplete", sections)
    (wt / "acceptance-criteria.md").unlink()
    set_mtime(main, 1_000_000_000)
    set_mtime(wt, 2_000_000_000)
    proc = gate(run_hook, tmp_path)
    assert proc.returncode == 2
    assert "wt-incomplete" in proc.stderr
    assert "MISSING FILE: acceptance-criteria.md" in proc.stderr


def test_no_main_specs_dir_skips_even_with_worktree_specs(tmp_path, run_hook, sections):
    """The main specs/ dir is the gate's on-switch: without it the hook exits 0
    even if a worktree carries spec folders -- pinned so the guard's scope
    cannot silently widen."""
    wt_specs = tmp_path / ".claude" / "worktrees" / "draft-wt" / "specs"
    wt = write_plan(wt_specs, "wt-incomplete", sections)
    (wt / "spec.md").unlink()
    proc = gate(run_hook, tmp_path)
    assert proc.returncode == 0
