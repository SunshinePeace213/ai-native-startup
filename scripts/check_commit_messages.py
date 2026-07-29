#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Validate commit subjects against git-workflow.md.

Checks the mechanical rules only: the `<emoji> <type>(<scope>): <description>`
shape, the emoji-to-type pairing, lowercase type and scope, a 72-character
subject cap, no trailing period, and no attribution trailers. Imperative mood is
not machine-checkable and is left to review.

Usage: check_commit_messages.py <base>..<head>
"""

import re
import subprocess
import sys

# The eight allowed pairs, from git-workflow.md. Keys are stored without the
# U+FE0F variation selector so both spellings of an emoji compare equal.
EMOJI_TYPE = {
    "✨": "feat",
    "🐛": "fix",
    "📝": "docs",
    "🎨": "style",
    "♻": "refactor",
    "⚡": "perf",
    "✅": "test",
    "🔧": "chore",
}

SUBJECT_RE = re.compile(r"^(?P<emoji>\S+) (?P<type>\w+)(?:\((?P<scope>[^)]*)\))?: (?P<desc>.+)$")
SHORTCODE_RE = re.compile(r"^:[a-z0-9_+-]+:$")
MAX_SUBJECT = 72
BANNED_TRAILERS = ("Signed-off-by:", "Co-Authored-By: Claude", "Co-authored-by: Claude")


def check_subject(subject: str) -> list[str]:
    """Rule violations in one subject line; empty means it conforms."""
    problems = []
    if len(subject) > MAX_SUBJECT:
        problems.append(f"subject is {len(subject)} chars, max {MAX_SUBJECT}")

    match = SUBJECT_RE.match(subject)
    if not match:
        problems.append("does not match `<emoji> <type>(<scope>): <description>`")
        return problems

    emoji = match["emoji"].replace("️", "")
    if SHORTCODE_RE.match(match["emoji"]):
        problems.append(f"uses the shortcode {match['emoji']} -- write the literal emoji")
    elif emoji not in EMOJI_TYPE:
        problems.append(f"{match['emoji']} is not one of the eight allowed emoji")
    elif EMOJI_TYPE[emoji] != match["type"]:
        problems.append(f"{match['emoji']} pairs with `{EMOJI_TYPE[emoji]}`, not `{match['type']}`")

    if match["type"] != match["type"].lower():
        problems.append(f"type `{match['type']}` must be lowercase")
    if match["scope"] is None:
        problems.append("missing `(<scope>)`")
    elif match["scope"] != match["scope"].lower():
        problems.append(f"scope `{match['scope']}` must be lowercase")
    if match["desc"].endswith("."):
        problems.append("description ends with a period")
    return problems


def check_body(body: str) -> list[str]:
    """Trailers git-workflow.md forbids on automated commits."""
    return [f"carries a `{t}` trailer" for t in BANNED_TRAILERS if t in body]


def commits(rev_range: str) -> list[tuple[str, str, str]]:
    """(sha, subject, body) per non-merge commit in the range."""
    out = subprocess.run(
        ["git", "log", "--no-merges", "--format=%H%x1f%s%x1f%b%x1e", rev_range],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    rows = []
    for record in out.split("\x1e"):
        record = record.strip("\n")
        if not record:
            continue
        sha, subject, body = record.split("\x1f", 2)
        rows.append((sha, subject, body))
    return rows


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__, file=sys.stderr)
        return 2

    failed = 0
    for sha, subject, body in commits(sys.argv[1]):
        problems = check_subject(subject) + check_body(body)
        if problems:
            failed += 1
            print(f"{sha[:9]} {subject}")
            for problem in problems:
                print(f"    - {problem}")

    if failed:
        print(f"\n{failed} commit(s) violate git-workflow.md", file=sys.stderr)
        return 1
    print("all commit messages conform to git-workflow.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
