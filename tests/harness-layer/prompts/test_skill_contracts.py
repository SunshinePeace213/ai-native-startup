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


def frontmatter_lines(text: str) -> tuple[str, ...]:
    """The frontmatter block's physical lines, each right-stripped -- the
    unit a whole-entry pin is checked against. A substring check would let
    `# name: spec-review` (commented out) or `x-name: spec-review` (renamed)
    satisfy a `name: spec-review` pin even though neither line is the live
    key Claude resolves the skill by; matching a full stripped line closes
    that gap."""
    return tuple(line.rstrip() for line in frontmatter(text).splitlines())


def missing_pins(text: str, expectations: dict) -> list[str]:
    """Every pin `expectations` names that `text` fails to satisfy; [] when clean.

    `expectations` keys: `frontmatter` (whole `key: value` lines, matched
    exactly against a frontmatter physical line), `frontmatter_fragment` (a
    literal that is deliberately part of a longer frontmatter value rather
    than a whole entry, kept as a substring check -- unused by either skill
    today but mirrors test_command_contracts.py's pin classes), and `clause`
    (literals expected anywhere in the body).
    """
    problems = []
    for literal in expectations.get("frontmatter", ()):
        if literal not in frontmatter_lines(text):
            problems.append(f"frontmatter entry missing: {literal!r}")
    for literal in expectations.get("frontmatter_fragment", ()):
        if literal not in frontmatter(text):
            problems.append(f"frontmatter fragment missing: {literal!r}")
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


def _frontmatter_entry_mutated(text: str, entry: str, replacement: str) -> str:
    """`text` with the exact frontmatter line `entry` swapped for
    `replacement` -- simulates a key being commented out or renamed while
    the pinned text still appears somewhere on the line."""
    pattern = re.compile(rf"^{re.escape(entry)}$", re.MULTILINE)
    mutated, count = pattern.subn(lambda _m: replacement, text, count=1)
    assert count == 1, f"expected exactly one frontmatter line {entry!r} to mutate"
    return mutated


@pytest.mark.parametrize("skill", sorted(SKILL_EXPECTATIONS))
def test_commented_frontmatter_entry_is_flagged(skill):
    """CX1-2: a commented-out `name:` (`# name: spec-review`) still contains
    the pinned text as a substring, so the substring check this suite used
    to run would pass it silently even though Claude can no longer resolve
    the skill by that key. Only matching a whole, exact frontmatter line
    catches it."""
    entry = f"name: {skill}"
    text = (SKILLS_DIR / skill / "SKILL.md").read_text()
    mutated = _frontmatter_entry_mutated(text, entry, f"# {entry}")
    problems = missing_pins(mutated, SKILL_EXPECTATIONS[skill])
    assert any(entry in p for p in problems), problems


@pytest.mark.parametrize("skill", sorted(SKILL_EXPECTATIONS))
def test_prefixed_frontmatter_entry_is_flagged(skill):
    """CX1-2: a renamed key (`old-name: spec-review`) is a dead key Claude's
    frontmatter parser ignores, but it still contains the pinned text as a
    substring -- only matching a whole, exact frontmatter line catches it."""
    entry = f"name: {skill}"
    text = (SKILLS_DIR / skill / "SKILL.md").read_text()
    mutated = _frontmatter_entry_mutated(text, entry, f"old-{entry}")
    problems = missing_pins(mutated, SKILL_EXPECTATIONS[skill])
    assert any(entry in p for p in problems), problems
