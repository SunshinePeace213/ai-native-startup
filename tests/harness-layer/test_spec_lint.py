"""Contract tests for scripts/spec_lint.py — the deterministic spec gate.

Each seeded defect below is a real class from the shipped ledgers (placeholder
tracking fields, an AC no task implements, a validation command naming a path
that neither exists nor is planned). The lint must go red on each and green on
a compliant folder, or the panel inherits mechanical work the lint exists to
absorb.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SPEC_LINT = REPO_ROOT / "scripts" / "spec_lint.py"

SPEC = """# Spec: Demo

- **Owner:** @ringo
- **Status:** Drafted for Review

## Tracking

- **Type:** chore
- **Complexity:** simple
- **Issue:** {issue}
- **Branch:** {branch}
- **Worktree:** `/tmp/worktrees/demo`
- **Review profile:** standard

## Task Description

Demo plan for lint contract tests.

## Objective

The lint accepts a compliant folder.

## Non-Goals

None.

## Requirements & Decisions

- Keep the fixture minimal.

## Relevant Files

- `specs/demo/checks/ac1.sh` — the only check.

## Edge Cases

- None; this is a fixture.

## Risk & Rollback

- **Blast radius:** none
- **Rollback:** delete the folder
- **In-flight work:** none

## Guardrails

None.

## Codex Verification

- **Outcome:** pending
- **Rejected findings:** none
"""

TASKS = """# Tasks: Demo

## Step by Step Tasks

### 1. Do the thing

- **Task ID:** `do-the-thing`
- **Depends On:** none
- **Agent Type:** general-purpose
- **Model / Effort:** per `.claude/rules/model-selection.md`
- **Files:** {files}
- **Parallel:** false
- **Satisfies:** {satisfies}
- **Verify:** the check exits 0
- Write the check.
"""

CRITERIA = """# Acceptance Criteria: Demo

## Acceptance Criteria

{criteria}

## Validation Commands

### AC1 — the check runs

{commands}
"""

DECISIONS = """# Decisions: Demo

## Summary

Minimal fixture.

## Resolved Decisions

- **Q:** none were open
  - **A:** fixture
  - **Why:** contract test

## Assumptions

- None.

## Open Questions / Out of Scope

- **Out of scope:** everything else.
"""


def make_plan(
    root: Path,
    *,
    issue: str = "#7",
    branch: str = "`chore/7-demo`",
    files: str = "`specs/demo/checks/ac1.sh`",
    satisfies: str = "AC1",
    criteria: str = "- **AC1** — the check script exits 0.",
    commands: str = "- `bash specs/demo/checks/ac1.sh` — pass: exit 0",
    spec: str | None = None,
) -> Path:
    folder = root / "specs" / "demo"
    (folder / "checks").mkdir(parents=True)
    (folder / "spec.md").write_text(spec or SPEC.format(issue=issue, branch=branch))
    (folder / "tasks.md").write_text(TASKS.format(files=files, satisfies=satisfies))
    (folder / "acceptance-criteria.md").write_text(
        CRITERIA.format(criteria=criteria, commands=commands)
    )
    (folder / "decisions.md").write_text(DECISIONS)
    (folder / "checks" / "ac1.sh").write_text("#!/usr/bin/env bash\nexit 0\n")
    return folder


def lint(cwd: Path, folder: str = "specs/demo") -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SPEC_LINT), folder],
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=110,
    )


def test_compliant_folder_passes(tmp_path: Path):
    """The green path: a folder meeting every mechanical standard exits 0."""
    make_plan(tmp_path)
    result = lint(tmp_path)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "all checks passed" in result.stdout
    assert all(line.startswith("PASS") for line in result.stdout.splitlines()[:-1])


def test_placeholder_tracking_field_is_red(tmp_path: Path):
    """A `<placeholder>` issue field is exactly the no-real-tracking defect S7 names."""
    make_plan(tmp_path, issue="<#N — mandatory, filed before the first push>")
    result = lint(tmp_path)
    assert result.returncode == 1
    assert "FAIL tracking-fields" in result.stdout


def test_branch_issue_mismatch_is_red(tmp_path: Path):
    """The branch number is the workflow join key; a mismatch breaks every Refs link."""
    make_plan(tmp_path, branch="`chore/8-demo`")
    result = lint(tmp_path)
    assert result.returncode == 1
    assert "FAIL tracking-fields" in result.stdout
    assert "#8" in result.stdout


def test_ac_named_by_no_task_is_red(tmp_path: Path):
    """An objective with no implementing step is the S1 defect, caught mechanically."""
    make_plan(
        tmp_path,
        criteria="- **AC1** — the check script exits 0.\n- **AC2** — a rollback path exists.",
    )
    result = lint(tmp_path)
    assert result.returncode == 1
    assert "FAIL traceability AC2 named by no task" in result.stdout


def test_task_citing_missing_ac_is_red(tmp_path: Path):
    """The reverse direction: a task satisfying a phantom criterion is untestable."""
    make_plan(tmp_path, satisfies="AC1, AC9")
    result = lint(tmp_path)
    assert result.returncode == 1
    assert "FAIL traceability" in result.stdout
    assert "AC9" in result.stdout


def test_absent_unplanned_command_path_is_red(tmp_path: Path):
    """A command pointing nowhere can never produce evidence — the R3-F1 class."""
    make_plan(tmp_path, commands="- `bash specs/demo/checks/nope.sh` — pass: exit 0")
    result = lint(tmp_path)
    assert result.returncode == 1
    assert "FAIL command-runnable" in result.stdout
    assert "nope.sh" in result.stdout


def test_planned_but_absent_path_passes(tmp_path: Path):
    """A plan may cite the test file its own build creates — planned paths are legal."""
    make_plan(
        tmp_path,
        files="`tests/demo/test_new.py`",
        commands="- `uv run pytest tests/demo/test_new.py::test_x` — pass: exit 0",
    )
    result = lint(tmp_path)
    assert result.returncode == 0, result.stdout + result.stderr


def test_missing_template_section_is_red(tmp_path: Path):
    """Template completeness is lint-owned; a dropped required section goes red."""
    spec = SPEC.format(issue="#7", branch="`chore/7-demo`").replace("## Guardrails\n\nNone.\n", "")
    make_plan(tmp_path, spec=spec)
    result = lint(tmp_path)
    assert result.returncode == 1
    assert "FAIL sections-complete" in result.stdout
    assert "Guardrails" in result.stdout


@pytest.mark.timeout(120)
def test_uncollectable_pytest_node_is_red(tmp_path: Path):
    """An existing file whose named node doesn't collect is the unrunnable-command
    class the cpo-layer ledger hit three times; run from the real repo root so
    pytest resolution is the real thing."""
    make_plan(
        tmp_path,
        files="`tests/harness-layer/test_pipeline_formats.py`",
        commands=(
            "- `uv run pytest tests/harness-layer/test_pipeline_formats.py::test_nonexistent`"
            " — pass: exit 0"
        ),
    )
    result = lint(REPO_ROOT, folder=str(tmp_path / "specs" / "demo"))
    assert result.returncode == 1
    assert "FAIL command-runnable" in result.stdout
    assert "not collectable" in result.stdout


@pytest.mark.timeout(120)
def test_collectable_pytest_node_passes(tmp_path: Path):
    """The matching green path: a real node id collects and the lint stays quiet."""
    make_plan(
        tmp_path,
        files="`tests/harness-layer/test_pipeline_formats.py`",
        commands=(
            "- `uv run pytest "
            "tests/harness-layer/test_pipeline_formats.py::test_digest_categories_table_shape`"
            " — pass: exit 0"
        ),
    )
    result = lint(REPO_ROOT, folder=str(tmp_path / "specs" / "demo"))
    assert result.returncode == 0, result.stdout + result.stderr
