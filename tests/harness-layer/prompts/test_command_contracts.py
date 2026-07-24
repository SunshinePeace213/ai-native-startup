"""Contract pins for .claude/commands/harness-layer/*.md.

Command frontmatter keys select what the harness dispatches the command
with -- model alias, effort, tool gating, the Stop-hook registration -- so a
dropped key silently changes execution with no error at the point of loss.
`##` sections are the exact structure `check_spec_completeness.py` and a
human skim both expect. Clauses are literals other components parse at
runtime: report-file name patterns, marker-comment keys other steps
upsert-search for, and CLI flags a command's own instructions promise to
pass. Every pin here is taken verbatim from spec.md's
`## Load-Bearing Contract Inventory` (command rows only) -- an intentional
prompt change ships with its expectation update in the same commit.

The #40/#42 regressions this suite replays (see
test_report_and_instructions_regressions_are_caught below) are the reason
this file exists: both restored a whole `##` section that had silently
vanished from harness-build.md / harness-review.md, and nothing at the time
would have caught it before a human noticed the command behaving wrong.
"""

import re
from pathlib import Path

import pytest

COMMANDS_DIR = Path(__file__).resolve().parents[3] / ".claude" / "commands" / "harness-layer"

FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---", re.DOTALL)
SECTION_RE = re.compile(r"^## (.+)$", re.MULTILINE)


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
    `# model: fable` (commented out) or `x-model: fable` (renamed) satisfy a
    `model: fable` pin even though neither line is a live key the harness
    reads; matching a full stripped line closes that gap."""
    return tuple(line.rstrip() for line in frontmatter(text).splitlines())


def missing_pins(text: str, expectations: dict) -> list[str]:
    """Every pin `expectations` names that `text` fails to satisfy; [] when clean.

    `expectations` keys: `frontmatter` (whole `key: value` lines, matched
    exactly against a frontmatter physical line), `frontmatter_fragment` (a
    literal that is deliberately part of a longer frontmatter value -- e.g. a
    script name buried inside a nested `hooks:` command -- kept as a
    substring check because it is not a whole entry on its own), `sections`
    (the exact `##` heading tuple, in order -- missing AND unexpected
    headings both count, and so does reordering), and `clause` (literals
    expected anywhere in the body).
    """
    problems = []
    for literal in expectations.get("frontmatter", ()):
        if literal not in frontmatter_lines(text):
            problems.append(f"frontmatter entry missing: {literal!r}")
    for literal in expectations.get("frontmatter_fragment", ()):
        if literal not in frontmatter(text):
            problems.append(f"frontmatter fragment missing: {literal!r}")
    if "sections" in expectations:
        expected = expectations["sections"]
        actual = section_headings(text)
        if actual != expected:
            missing = [s for s in expected if s not in actual]
            extra = [s for s in actual if s not in expected]
            if missing:
                problems.append(f"sections missing: {missing}")
            if extra:
                problems.append(f"sections unexpected: {extra}")
            if not missing and not extra:
                problems.append(f"sections out of order: expected {expected}, got {actual}")
    for literal in expectations.get("clause", ()):
        if literal not in text:
            problems.append(f"clause missing: {literal!r}")
    return problems


# Verbatim from spec.md's ## Load-Bearing Contract Inventory (command rows only).
COMMAND_EXPECTATIONS = {
    "harness-plan.md": {
        "frontmatter": (
            "model: fable",
            "effort: xhigh",
            "disable-model-invocation: true",
            "disallowed-tools: Task, EnterPlanMode",
        ),
        "frontmatter_fragment": ("check_spec_completeness.py",),
        "sections": (
            "Variables",
            "Instructions",
            "Domain Knowledge",
            "Readiness Gate",
            "Workflow",
            "Output: Spec Folder",
            "Plan Artifacts",
            "Worktree & Handoff",
            "Revision Mode",
            "Codex Cross-Review",
            "Report",
        ),
        "clause": (
            "codex-spec-review-round-",
            "<!-- plan-links -->",
            "<!-- codex-spec-round-N -->",
            "HEAD:refs/heads/",
            "codex-runner",
            "gh issue develop",
            "--body-file",
        ),
    },
    "harness-build.md": {
        "frontmatter": (
            "model: fable",
            "disable-model-invocation: true",
        ),
        "sections": ("Variables", "Instructions", "Workflow", "Report"),
        "clause": (
            "--draft",
            "--body-file",
            "<!-- report:tidy -->",
            ".github/PULL_REQUEST_TEMPLATE/",
        ),
    },
    "harness-review.md": {
        "frontmatter": (
            "model: fable",
            "disable-model-invocation: true",
        ),
        "sections": (
            "Variables",
            "Instructions",
            "Workflow",
            "Review runner",
            "Back-to-planning exit (spec defects)",
            "Report",
        ),
        "clause": (
            "codex-impl-review-round-",
            "<!-- report:codex-round-N -->",
            "codex-runner",
            "implementation-review",
        ),
    },
    "harness-ship.md": {
        "frontmatter": (
            "model: sonnet",
            "effort: low",
            "disable-model-invocation: true",
            "allowed-tools: Bash(git *), Bash(gh *)",
        ),
        "sections": ("Variables", "Instructions", "Workflow", "Report"),
        "clause": ("--squash", "--match-head-commit"),
    },
    "harness-unknowns.md": {
        "frontmatter": (
            "model: fable",
            "effort: high",
            "disable-model-invocation: true",
            "disallowed-tools: Task, EnterPlanMode",
        ),
        "sections": (
            "Variables",
            "Instructions",
            "Modes",
            "Workflow",
            "Improved Prompt",
            "Report",
        ),
    },
    "harness-brainstorm.md": {
        "frontmatter": (
            "model: fable",
            "effort: high",
            "disable-model-invocation: true",
            "disallowed-tools: Task, EnterPlanMode",
        ),
        "sections": ("Variables", "Instructions", "Workflow", "Refined Prompt", "Report"),
    },
    "harness-prototypes.md": {
        "frontmatter": (
            "model: fable",
            "effort: high",
            "disable-model-invocation: true",
            "disallowed-tools: Task, EnterPlanMode",
        ),
        "sections": (
            "Variables",
            "Instructions",
            "Modes",
            "Workflow",
            "Improved Prompt",
            "Report",
        ),
    },
    "harness-interview.md": {
        "frontmatter": (
            "model: fable",
            "effort: high",
            "disable-model-invocation: true",
            "disallowed-tools: Task, EnterPlanMode",
        ),
        "sections": (
            "Variables",
            "Instructions",
            "Coverage Ledger",
            "Round Loop",
            "Output",
            "Report",
        ),
    },
    "kb.md": {
        "frontmatter": ("allowed-tools: Bash(curl *), WebFetch",),
        "sections": ("Variables", "Instructions", "Workflow", "Report"),
    },
}


@pytest.mark.parametrize("filename", sorted(COMMAND_EXPECTATIONS))
def test_command_contract_pins_hold(filename):
    """Every pin traces to a real consumer -- frontmatter keys select the
    dispatched model/effort/tool-gating and the Stop-hook registration,
    `##` sections are the exact structure check_spec_completeness.py and a
    human skim both expect, and clauses are literals other pipeline steps
    parse at runtime (report paths, marker-comment keys, gh flags). A
    silently dropped pin breaks its consumer with no error at the point of
    loss -- this is the machine check spec.md's inventory promises."""
    text = (COMMANDS_DIR / filename).read_text()
    assert missing_pins(text, COMMAND_EXPECTATIONS[filename]) == []


def _section_stripped(text: str, heading: str) -> str:
    """`text` with the named `##` section (heading through the next `##`,
    or EOF) removed -- simulates the section silently vanishing."""
    pattern = re.compile(rf"^## {re.escape(heading)}\n.*?(?=^## |\Z)", re.MULTILINE | re.DOTALL)
    stripped, count = pattern.subn("", text)
    assert count == 1, f"expected exactly one '## {heading}' section to strip"
    return stripped


@pytest.mark.parametrize(
    "filename,commit,pr",
    [
        ("harness-build.md", "3ce40db", "#40"),
        ("harness-review.md", "3ce40db", "#40"),
    ],
)
def test_report_section_removal_is_flagged(filename, commit, pr):
    """Replays the regression restored by commit 3ce40db (PR #40): the
    build/review split silently dropped the '## Report' end-of-session
    output contract from both commands. missing_pins must flag a section
    loss like this, not just verify a byte-identical file."""
    text = (COMMANDS_DIR / filename).read_text()
    stripped = _section_stripped(text, "Report")
    problems = missing_pins(stripped, COMMAND_EXPECTATIONS[filename])
    assert any("Report" in p for p in problems), (commit, pr, problems)


@pytest.mark.parametrize(
    "filename,commit,pr",
    [
        ("harness-build.md", "c4bf3fa", "#42"),
        ("harness-review.md", "c4bf3fa", "#42"),
    ],
)
def test_instructions_section_removal_is_flagged(filename, commit, pr):
    """Replays the regression restored by commit c4bf3fa (PR #42): the same
    build/review split silently dropped the '## Instructions'
    standing-rules section from both commands. missing_pins must flag a
    section loss like this, not just verify a byte-identical file."""
    text = (COMMANDS_DIR / filename).read_text()
    stripped = _section_stripped(text, "Instructions")
    problems = missing_pins(stripped, COMMAND_EXPECTATIONS[filename])
    assert any("Instructions" in p for p in problems), (commit, pr, problems)


def _frontmatter_entry_mutated(text: str, entry: str, replacement: str) -> str:
    """`text` with the exact frontmatter line `entry` swapped for
    `replacement` -- simulates a key being commented out or renamed while
    the pinned text still appears somewhere on the line."""
    pattern = re.compile(rf"^{re.escape(entry)}$", re.MULTILINE)
    mutated, count = pattern.subn(lambda _m: replacement, text, count=1)
    assert count == 1, f"expected exactly one frontmatter line {entry!r} to mutate"
    return mutated


FRONTMATTER_ENTRY_MUTATION_CASES = [
    ("harness-plan.md", "model: fable"),
    ("harness-ship.md", "allowed-tools: Bash(git *), Bash(gh *)"),
    ("harness-unknowns.md", "disallowed-tools: Task, EnterPlanMode"),
]


@pytest.mark.parametrize("filename,entry", FRONTMATTER_ENTRY_MUTATION_CASES)
def test_commented_frontmatter_entry_is_flagged(filename, entry):
    """CX1-2: a commented-out key (`# model: fable`) still contains the
    pinned text as a substring, so the substring check this suite used to
    run would pass it silently even though the key no longer takes effect.
    Only matching a whole, exact frontmatter line catches it."""
    text = (COMMANDS_DIR / filename).read_text()
    mutated = _frontmatter_entry_mutated(text, entry, f"# {entry}")
    problems = missing_pins(mutated, COMMAND_EXPECTATIONS[filename])
    assert any(entry in p for p in problems), problems


@pytest.mark.parametrize("filename,entry", FRONTMATTER_ENTRY_MUTATION_CASES)
def test_prefixed_frontmatter_entry_is_flagged(filename, entry):
    """CX1-2: a renamed key (`x-model: fable`) is a dead key the frontmatter
    parser ignores, but it still contains the pinned text as a substring --
    only matching a whole, exact frontmatter line catches it."""
    text = (COMMANDS_DIR / filename).read_text()
    mutated = _frontmatter_entry_mutated(text, entry, f"x-{entry}")
    problems = missing_pins(mutated, COMMAND_EXPECTATIONS[filename])
    assert any(entry in p for p in problems), problems
