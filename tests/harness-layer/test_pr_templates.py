"""Pins the GitHub templates to the pipeline commands and conventions that fill them.

The 8 PR templates duplicate a ~35-line tail GitHub gives no way to share, and the
sections in that tail are written by `/harness-layer:harness-build`, appended to by
`/harness-layer:harness-review`, and merged on by `/harness-layer:harness-ship`. Nothing
enforced either link, so both drifted: three sections the commands write (`## Plan`,
`## Dev Notes`, `## Follow-ups`) existed in no template, and every manifest row shipped a
`#<taskId>` placeholder that GitHub autolinks to an unrelated issue — the exact shape
`harness-build.md` tells the agent to avoid.

The issue side has the same shape. `specs/_templates/issues/README.md` requires each CLI
skeleton's `##` headings to match its web form's field labels one-to-one, because the two
paths must produce the same issue body; no test enforced that either.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
PR_TEMPLATE_DIR = REPO_ROOT / ".github" / "PULL_REQUEST_TEMPLATE"
ISSUE_FORM_DIR = REPO_ROOT / ".github" / "ISSUE_TEMPLATE"
ISSUE_SKELETON_DIR = REPO_ROOT / "specs" / "_templates" / "issues"
WORKFLOW_DOC = REPO_ROOT / ".claude" / "rules" / "git-workflow.md"

# Where the duplicated block starts. Everything from here to EOF must match byte for byte.
SHARED_TAIL_START = "## Test Evidence"

# Sections the pipeline commands write into or read out of the PR body. A template missing
# one forces the build agent to invent the heading, and `## Build Status` missing means
# harness-ship has no approved SHA to pass to `gh pr merge --match-head-commit`.
REQUIRED_PR_SECTIONS = (
    "Summary",
    "Plan",
    "Test Evidence",
    "Risk & Rollback",
    "Agent Task Manifest",
    "Build Status",
    "Review Reports",
    "Dev Notes",
    "Follow-ups",
)

SKELETON_TO_FORM = {
    "feature.md": "feature.yml",
    "bug.md": "bug.yml",
    "chore.md": "chore.yml",
    "epic.md": "epic.yml",
}


def _pr_templates() -> list[Path]:
    return sorted(PR_TEMPLATE_DIR.glob("*.md"))


def _tail(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    index = text.find(f"\n{SHARED_TAIL_START}\n")
    assert index != -1, f"{path.name} has no '{SHARED_TAIL_START}' section"
    return text[index + 1 :]


def _headings(text: str) -> list[str]:
    return re.findall(r"^## (.+)$", text, re.M)


def _commit_types() -> dict[str, str]:
    """Return {type: emoji} from git-workflow.md's emoji-to-type table."""
    rows = re.findall(
        r"^\|\s*(\S+)\s*\|\s*`(\w+)`\s*\|", WORKFLOW_DOC.read_text(encoding="utf-8"), re.M
    )
    return {commit_type: emoji for emoji, commit_type in rows}


COMMIT_TYPES = _commit_types()


def test_commit_type_table_parses():
    """A parser that matched nothing would make the coverage and emoji tests vacuous."""
    assert len(COMMIT_TYPES) == 8, f"expected 8 commit types, parsed {sorted(COMMIT_TYPES)}"
    assert COMMIT_TYPES["feat"] == "✨"


def test_every_commit_type_has_a_pr_template():
    """pr-process.md mandates one template per commit type. A type added to the workflow
    table without a template leaves harness-build with no `--body-file` to fill."""
    assert {p.stem for p in _pr_templates()} == set(COMMIT_TYPES)


@pytest.mark.parametrize("path", _pr_templates(), ids=lambda p: p.name)
def test_pr_template_tail_is_byte_identical(path: Path):
    """GitHub cannot include a shared partial into a PR template, so the tail is copied 8
    times. Without this test a fix lands in one file and the other seven keep the bug."""
    reference = _tail(PR_TEMPLATE_DIR / "feat.md")
    assert _tail(path) == reference, (
        f"{path.name}'s tail differs from feat.md's. The block from '{SHARED_TAIL_START}' "
        f"to EOF must be identical in all 8 templates — update every one in the same commit."
    )


@pytest.mark.parametrize("path", _pr_templates(), ids=lambda p: p.name)
def test_pr_template_carries_every_section_the_pipeline_writes(path: Path):
    """A heading the commands write but the template omits gets invented ad hoc, so the
    section name varies per PR and harness-ship/harness-review can no longer find it."""
    headings = _headings(path.read_text(encoding="utf-8"))
    missing = [s for s in REQUIRED_PR_SECTIONS if s not in headings]
    assert not missing, f"{path.name} is missing pipeline sections: {missing}"


@pytest.mark.parametrize("path", _pr_templates(), ids=lambda p: p.name)
def test_pr_template_leads_with_summary_then_plan(path: Path):
    """Reviewers read intent before evidence; the type-specific sections come after."""
    assert _headings(path.read_text(encoding="utf-8"))[:2] == ["Summary", "Plan"]


@pytest.mark.parametrize("path", _pr_templates(), ids=lambda p: p.name)
def test_manifest_placeholder_is_not_an_autolink(path: Path):
    """`#<taskId>` renders as a cross-link to an unrelated issue, spamming its timeline
    with a backref. harness-build.md tells the agent to use bare kebab-case IDs; the
    template used to hand it the opposite."""
    offenders = [
        line
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.startswith("|") and re.search(r"#<[\w-]+>", line)
    ]
    assert not offenders, (
        f"{path.name} has a `#`-prefixed task placeholder, which GitHub autolinks: {offenders}"
    )


@pytest.mark.parametrize("path", _pr_templates(), ids=lambda p: p.name)
def test_pr_title_hint_uses_the_type_s_gitmoji(path: Path):
    """git-workflow.md pairs one emoji per type, and harness-ship derives the squash-commit
    subject from the PR title — a wrong emoji there propagates into main's history."""
    first_line = path.read_text(encoding="utf-8").splitlines()[0]
    expected = f"{COMMIT_TYPES[path.stem]} {path.stem}("
    assert expected in first_line, f"{path.name} title hint should contain '{expected}'"


@pytest.mark.parametrize(("skeleton", "form"), sorted(SKELETON_TO_FORM.items()))
def test_issue_skeleton_headings_match_the_form_field_labels(skeleton: str, form: str):
    """Issue forms cannot be submitted from the CLI, so harness-plan fills the paired
    skeleton instead. If the two disagree, the same kind of issue gets a different body
    depending on whether a human or an agent filed it."""
    # Field labels sit at exactly 6 spaces under `attributes:`; checkbox options are
    # deeper and prefixed with `- `, so this indent anchor skips them.
    labels = re.findall(
        r"^ {6}label: (.+)$", (ISSUE_FORM_DIR / form).read_text(encoding="utf-8"), re.M
    )
    headings = _headings((ISSUE_SKELETON_DIR / skeleton).read_text(encoding="utf-8"))
    assert headings == labels, (
        f"{skeleton} headings and {form} field labels have drifted:\n"
        f"  skeleton: {headings}\n  form:     {labels}"
    )
