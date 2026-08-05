"""Contract tests for scripts/impl_lint.py — the deterministic implementation gate.

Each test builds a hermetic scratch git repository (own config, own identity) so
the lint's git-range logic is exercised for real — the eval-harness lesson: a
harness that fakes what the code resolves against measures the harness, not the
change.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
IMPL_LINT = REPO_ROOT / "scripts" / "impl_lint.py"

CRITERIA = """# Acceptance Criteria: Demo

## Acceptance Criteria

- **AC1** — the check script exits 0.

## Validation Commands

### AC1 — the check runs

{commands}
"""

NOTES = """# Implementation Notes: Demo

## Log

- **2026-08-06 · hand-off `do-the-thing`** — checks/ac1.sh
  - `bash specs/demo/checks/ac1.sh` → exit 0
"""


def hermetic_env() -> dict[str, str]:
    return {
        **os.environ,
        "GIT_CONFIG_GLOBAL": os.devnull,
        "GIT_CONFIG_SYSTEM": os.devnull,
        "GIT_AUTHOR_NAME": "t",
        "GIT_AUTHOR_EMAIL": "t@t",
        "GIT_COMMITTER_NAME": "t",
        "GIT_COMMITTER_EMAIL": "t@t",
    }


def git(root: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=root, env=hermetic_env(), check=True, capture_output=True)


def commit_all(root: Path, message: str) -> None:
    git(root, "add", "-A")
    git(root, "commit", "-m", message)


def make_repo(
    tmp_path: Path,
    *,
    commands: str = "- `bash specs/demo/checks/ac1.sh` — pass: exit 0",
    check_body: str = "#!/usr/bin/env bash\nexit 0\n",
    notes: str = NOTES,
    build_message: str = "🔧 chore(demo): build the thing\n\nRefs #7",
) -> Path:
    folder = tmp_path / "specs" / "demo"
    (folder / "checks").mkdir(parents=True)
    (folder / "acceptance-criteria.md").write_text(CRITERIA.format(commands=commands))
    (folder / "checks" / "ac1.sh").write_text(check_body)
    git(tmp_path, "init", "-q", "-b", "main")
    commit_all(tmp_path, "🔧 chore(demo): seed plan\n\nRefs #7")
    git(tmp_path, "checkout", "-q", "-b", "work")
    (folder / "implementation-notes.md").write_text(notes)
    commit_all(tmp_path, build_message)
    return tmp_path


def lint(root: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(IMPL_LINT), "specs/demo"],
        cwd=root,
        env=hermetic_env(),
        capture_output=True,
        text=True,
        timeout=110,
    )


def test_compliant_repo_passes(tmp_path: Path):
    """Green path, including the origin-less fallback to the local main base."""
    result = lint(make_repo(tmp_path))
    assert result.returncode == 0, result.stdout + result.stderr
    assert "all checks passed" in result.stdout


def test_failing_validation_command_is_red(tmp_path: Path):
    """A criterion whose command exits non-zero is a promise, not evidence (I2)."""
    result = lint(make_repo(tmp_path, check_body="#!/usr/bin/env bash\nexit 1\n"))
    assert result.returncode == 1
    assert "FAIL validation-commands" in result.stdout
    assert "exit 1" in result.stdout


def test_bad_commit_subject_is_red(tmp_path: Path):
    """Commit format is lint-owned (I7); a free-text subject goes red."""
    result = lint(make_repo(tmp_path, build_message="fixed stuff"))
    assert result.returncode == 1
    assert "FAIL commit-format" in result.stdout


def test_missing_refs_footer_is_red(tmp_path: Path):
    """The Refs footer is the durable join key; a conforming subject without it fails."""
    result = lint(make_repo(tmp_path, build_message="🔧 chore(demo): build the thing"))
    assert result.returncode == 1
    assert "missing `Refs #N` footer" in result.stdout


def test_discovery_commit_is_exempt_from_refs(tmp_path: Path):
    """Discovery commits predate the issue by design — they must not false-positive."""
    root = make_repo(tmp_path)
    (root / "specs" / "demo" / "note.md").write_text("discovery page\n")
    commit_all(root, "📝 docs(discovery): capture unknowns board")
    result = lint(root)
    assert result.returncode == 0, result.stdout + result.stderr


def test_orphan_import_is_red(tmp_path: Path):
    """An unused import in changed Python is the I6 orphan class, caught by ruff."""
    root = make_repo(tmp_path)
    (root / "orphan.py").write_text("import os\n")
    commit_all(root, "🔧 chore(demo): add module\n\nRefs #7")
    result = lint(root)
    assert result.returncode == 1
    assert "FAIL orphans" in result.stdout


def test_missing_notes_evidence_is_red(tmp_path: Path):
    """A log entry with no `command` → result line is a claim without evidence (I3)."""
    result = lint(make_repo(tmp_path, notes="# Implementation Notes\n\n## Log\n\n- did work\n"))
    assert result.returncode == 1
    assert "FAIL notes-evidence" in result.stdout


def test_manual_command_needs_recorded_output(tmp_path: Path):
    """A `manual:` entry passes only when its output shows up in the notes."""
    commands = (
        "- `bash specs/demo/checks/ac1.sh` — pass: exit 0\n"
        "- `manual: eyeball the rendered page` — pass: looks right; recorded in notes"
    )
    root = make_repo(tmp_path, commands=commands)
    result = lint(root)
    assert result.returncode == 1
    assert "manual check has no recorded output" in result.stdout

    notes = root / "specs" / "demo" / "implementation-notes.md"
    notes.write_text(
        NOTES + "- **2026-08-06 · manual** — eyeball the rendered page → looks right\n"
    )
    result = lint(root)
    assert result.returncode == 0, result.stdout + result.stderr
