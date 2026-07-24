"""Contract pins for .agents/skills/{spec-review,implementation-review}/SKILL.md,
plus cross-consistency asserts tying the prompt files to each other and to the
Stop-hook's REQUIRED_SECTIONS.

Both skills are driven by `codex exec` and parsed by the harness-plan /
harness-review orchestrators that read their report files: the frontmatter
`name:` is how Claude resolves the skill by name, the verdict-line grammar
(including the em-dash) is what the orchestrator's verdict parser matches
against, and the report-filename pattern is what both the skill's own
Output-contract instructions and the orchestrator's upsert-search agree on.
A dropped or drifted pin here breaks that parsing silently, the same class
of defect the #40/#42 command-section regressions were.
"""

import re
from pathlib import Path

import pytest

SKILLS_DIR = Path(__file__).resolve().parents[3] / ".agents" / "skills"
TEMPLATES_DIR = Path(__file__).resolve().parents[3] / "specs" / "_templates"

FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---", re.DOTALL)
SECTION_RE = re.compile(r"^## (.+)$", re.MULTILINE)

VERDICT_APPROVED = "### Round N — Verdict: approved"
VERDICT_CHANGES_REQUESTED = "### Round N — Verdict: changes-requested"


def frontmatter(text: str) -> str:
    """The raw YAML frontmatter block between the file's `---` fences."""
    match = FRONTMATTER_RE.match(text)
    return match.group(1) if match else ""


def section_headings(text: str) -> tuple[str, ...]:
    """The file's `##` heading set, in file order."""
    return tuple(SECTION_RE.findall(text))


def missing_pins(text: str, expectations: dict) -> list[str]:
    """Every pin `expectations` names that `text` fails to satisfy; [] when clean.

    `expectations` keys: `frontmatter` (literal lines expected inside the
    frontmatter block) and `clause` (literals expected anywhere in the body).
    """
    problems = []
    for literal in expectations.get("frontmatter", ()):
        if literal not in frontmatter(text):
            problems.append(f"frontmatter missing: {literal!r}")
    for literal in expectations.get("clause", ()):
        if literal not in text:
            problems.append(f"clause missing: {literal!r}")
    return problems


# Verbatim from spec.md's ## Load-Bearing Contract Inventory (skill rows only).
SKILL_EXPECTATIONS = {
    "spec-review": {
        "frontmatter": ("name: spec-review",),
        "clause": (
            VERDICT_APPROVED,
            VERDICT_CHANGES_REQUESTED,
            "CX<N>-<i>",
            "(repeat of",
            "**Issue-comment digest:**",
            "codex-spec-review-round-N.md",
            "[plan-time]",
            "[child-build-time]",
            "[post-merge]",
            "Reviewed head SHA:",
        ),
    },
    "implementation-review": {
        "frontmatter": ("name: implementation-review",),
        "clause": (
            VERDICT_APPROVED,
            VERDICT_CHANGES_REQUESTED,
            "CX<N>-<i>",
            "(repeat of",
            "(spec-defect)",
            "**Issue-comment digest:**",
            "codex-impl-review-round-N.md",
            "Base SHA:",
            "Reviewed head SHA:",
            "Mode:",
            "Lenses:",
        ),
    },
}


@pytest.mark.parametrize("skill", sorted(SKILL_EXPECTATIONS))
def test_skill_contract_pins_hold(skill):
    """Every pin traces to a real consumer: `name:` is how Claude resolves
    the skill, and each clause is a literal the harness-plan/harness-review
    orchestrators (or the skill's own Output-contract instructions) parse
    out of the report file this skill writes. A silently dropped pin breaks
    that parsing with no error at the point of loss."""
    text = (SKILLS_DIR / skill / "SKILL.md").read_text()
    assert missing_pins(text, SKILL_EXPECTATIONS[skill]) == []


def test_each_skill_frontmatter_name_equals_its_directory():
    """Claude resolves a skill by its containing directory name; if
    frontmatter `name:` drifts from the directory, the skill still loads
    (directory-keyed) but any code that reads `name:` to identify it --
    or a human auditing the frontmatter -- gets a lie."""
    for skill in SKILL_EXPECTATIONS:
        text = (SKILLS_DIR / skill / "SKILL.md").read_text()
        assert f"name: {skill}" in frontmatter(text)


def test_plan_and_spec_review_agree_on_report_filename_pattern():
    """harness-plan.md's Codex-Cross-Review step names the report file it
    expects the spec-review skill to write; if the two prompts drift on the
    filename pattern, the orchestrator looks for a report file the skill
    never creates and the round silently produces no read-back verdict."""
    plan_text = (
        Path(__file__).resolve().parents[3]
        / ".claude"
        / "commands"
        / "harness-layer"
        / "harness-plan.md"
    ).read_text()
    skill_text = (SKILLS_DIR / "spec-review" / "SKILL.md").read_text()
    assert "codex-spec-review-round-" in plan_text
    assert "codex-spec-review-round-" in skill_text


def test_review_and_implementation_review_agree_on_report_filename_pattern():
    """Same coupling as above, for harness-review.md and the
    implementation-review skill."""
    review_text = (
        Path(__file__).resolve().parents[3]
        / ".claude"
        / "commands"
        / "harness-layer"
        / "harness-review.md"
    ).read_text()
    skill_text = (SKILLS_DIR / "implementation-review" / "SKILL.md").read_text()
    assert "codex-impl-review-round-" in review_text
    assert "codex-impl-review-round-" in skill_text


def test_both_skills_share_identical_verdict_line_grammar():
    """The harness-plan/harness-review orchestrators parse the report's
    first line to decide approved vs changes-requested; if the two skills'
    verdict grammar drifts (even by dash character -- U+2014 em-dash vs a
    plain hyphen), a byte-exact parser matches one skill's reports and
    silently fails to match the other's."""
    for skill in SKILL_EXPECTATIONS:
        text = (SKILLS_DIR / skill / "SKILL.md").read_text()
        assert VERDICT_APPROVED in text
        assert VERDICT_CHANGES_REQUESTED in text
        assert "—" in VERDICT_APPROVED  # guard the literal itself, not just presence


def test_required_sections_appear_in_matching_template(load_hook_module):
    """check_spec_completeness.py's REQUIRED_SECTIONS is the Stop-hook's gate
    for /harness-layer:harness-plan; if a specs/_templates/ file is renamed
    or a heading drifts from what the hook requires, a freshly-drafted spec
    copied straight from the template can never satisfy the gate -- a
    template rename would silently strand every future plan."""
    hook = load_hook_module("check_spec_completeness.py")
    for filename, sections in hook.REQUIRED_SECTIONS.items():
        template_text = (TEMPLATES_DIR / filename).read_text()
        template_sections = section_headings(template_text)
        missing = [s for s in sections if s not in template_sections]
        assert not missing, (filename, missing)
