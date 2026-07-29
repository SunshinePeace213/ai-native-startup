"""Contract tests for the commit-message linter.

git-workflow.md's format is what commitlint and changelog tooling parse, and CI
now blocks a PR that breaks it. A linter that accepts a malformed subject, or
rejects a valid one, is worse than none -- the first lets drift through, the
second trains people to bypass the gate. These pin both directions.
"""

import importlib.util
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "check_commit_messages.py"

spec = importlib.util.spec_from_file_location("check_commit_messages", SCRIPT)
ccm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ccm)


@pytest.mark.parametrize(
    "subject",
    [
        "✨ feat(api): add user login endpoint",
        "🐛 fix(hooks): fail open on malformed stdin",
        "📝 docs(discovery): record the brainstorm pass",
        "🎨 style(tests): regroup the wiring fixtures",
        "♻️ refactor(harness): split build from review",
        "⚡️ perf(scan): cache the compiled patterns",
        "✅ test(wiring): read registrars from frontmatter only",
        "🔧 chore(ci): add the first workflow",
    ],
)
def test_every_allowed_pair_is_accepted(subject):
    """All eight emoji-type pairs in the git-workflow.md table must pass, or the
    linter blocks legitimate work and gets bypassed."""
    assert ccm.check_subject(subject) == []


def test_variation_selector_spelling_is_accepted():
    """♻️ and ⚡️ carry a U+FE0F selector that ♻ and ⚡ lack. Both render
    identically, so rejecting either spelling is a false failure."""
    assert ccm.check_subject("♻️ refactor(x): y") == []
    assert ccm.check_subject("♻ refactor(x): y") == []


@pytest.mark.parametrize(
    ("subject", "fragment"),
    [
        ("✨ fix(api): mismatched pair", "pairs with"),
        ("🚀 feat(api): emoji not in the table", "not one of the eight"),
        (":sparkles: feat(api): shortcode instead of emoji", "shortcode"),
        ("✨ feat(API): uppercase scope", "must be lowercase"),
        ("✨ feat(api): trailing period.", "ends with a period"),
        ("✨ feat: missing the scope", "missing `(<scope>)`"),
        ("just a plain sentence", "does not match"),
        ("✨ feat(api): " + "x" * 80, "max 72"),
    ],
)
def test_violations_are_caught(subject, fragment):
    """Each rule git-workflow.md states must actually fail the linter -- an
    unenforced rule is documentation, not a standard."""
    problems = ccm.check_subject(subject)
    assert any(fragment in p for p in problems), problems


@pytest.mark.parametrize(
    "body",
    [
        "Signed-off-by: Someone <a@b.c>",
        "Co-Authored-By: Claude <noreply@anthropic.com>",
        "Co-authored-by: Claude <noreply@anthropic.com>",
    ],
)
def test_banned_trailers_are_caught(body):
    """git-workflow.md forbids these on automated commits; they are invisible in
    the subject line, so only a body check catches them."""
    assert ccm.check_body(body) != []


def test_ordinary_body_is_clean():
    """A normal body with a Refs footer must not trip the trailer check."""
    assert ccm.check_body("Implements the thing.\n\nRefs #42") == []
