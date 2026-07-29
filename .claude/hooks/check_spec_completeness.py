#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Stop hook for /harness-layer:harness-plan: block the run from ending until
the per-plan spec folder is complete.

Three checks: (1) all four files exist, (2) each file has its required '##'
sections, (3) each required section carries real content — not empty, and
not a leftover '<placeholder>' from specs/_templates/. Exit 2 => deny stop;
stderr is fed back to Claude so it completes the gaps. The gated folder is
the newest-modified plan folder across the main specs/ and any worktree's
specs/ (/harness-layer:harness-plan drafts in a worktree), excluding
underscore-prefixed dirs (_templates) and discovery-only chain folders (a
discovery/ subdir with no spec files yet).
"""

import os
import re
import subprocess
import sys
from pathlib import Path

REQUIRED_SECTIONS: dict[str, tuple[str, ...]] = {
    "spec.md": (
        "Tracking",
        "Task Description",
        "Objective",
        "Non-Goals",
        "Requirements & Decisions",
        "Relevant Files",
        "Edge Cases",
        "Risk & Rollback",
        "Guardrails",
        "Codex Verification",
    ),
    "tasks.md": ("Step by Step Tasks",),
    "acceptance-criteria.md": (
        "Acceptance Criteria",
        "Validation Commands",
    ),
    "decisions.md": (
        "Summary",
        "Resolved Decisions",
        "Assumptions",
        "Open Questions / Out of Scope",
    ),
}


COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
# A template slot: an angle-bracket span opening on a word character and holding a
# space, e.g. `<one or two sentences …>`. Paths (`<type>/<N>-<slug>`) and autolinks
# have no inner space, so filled content survives.
PLACEHOLDER_RE = re.compile(r"<[A-Za-z#][^<>]*\s[^<>]*>")


def section_body(text: str, section: str) -> str | None:
    """The lines under '## <section>', up to the next '#'/'## ' heading.

    Returns None when the heading is absent. HTML comments are stripped first, so
    the template's guidance never counts as content; fenced code is tracked so a
    '## ' inside a block does not end the section early.
    """
    heading = f"## {section}"
    body: list[str] = []
    capturing = False
    fenced = False
    for line in COMMENT_RE.sub("", text).splitlines():
        if line.lstrip().startswith("```"):
            fenced = not fenced
        elif not fenced and line.startswith("#"):
            if line.rstrip() == heading:
                capturing = True
                continue
            if capturing and not line.startswith("###"):
                break
            if capturing:
                body.append(line)
            continue
        if capturing:
            body.append(line)
    return "\n".join(body) if capturing else None


def resolve_root() -> Path:
    env_root = os.environ.get("CLAUDE_PROJECT_DIR")
    if env_root:
        return Path(env_root)
    proc = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True)
    if proc.returncode == 0 and proc.stdout.strip():
        return Path(proc.stdout.strip())
    return Path.cwd()


def discovery_only(folder: Path) -> bool:
    """A chain folder holding only pre-plan discovery output — not yet a plan."""
    return (folder / "discovery").is_dir() and not any(
        (folder / name).is_file() for name in REQUIRED_SECTIONS
    )


def newest_plan_folder(root: Path) -> Path | None:
    specs_dirs = [root / "specs", *sorted((root / ".claude" / "worktrees").glob("*/specs"))]
    folders = [
        folder
        for specs in specs_dirs
        if specs.is_dir()
        for folder in specs.iterdir()
        if folder.is_dir() and not folder.name.startswith("_") and not discovery_only(folder)
    ]
    return max(folders, key=lambda folder: folder.stat().st_mtime, default=None)


def main() -> int:
    root = resolve_root()
    if not (root / "specs").is_dir():
        return 0  # no specs dir at all -> nothing to gate

    folder = newest_plan_folder(root)
    if folder is None:
        print("Stop blocked: no plan folder found under specs/.", file=sys.stderr)
        return 2

    missing: list[str] = []
    for name, sections in REQUIRED_SECTIONS.items():
        path = folder / name
        if not path.is_file():
            missing.append(f"  - MISSING FILE: {name}")
            continue
        text = path.read_text(errors="replace")
        for section in sections:
            body = section_body(text, section)
            if body is None:
                missing.append(f"  - {name}: missing section '## {section}'")
            elif not body.strip():
                missing.append(f"  - {name}: section '## {section}' is empty")
            elif (leftover := PLACEHOLDER_RE.search(body)) is not None:
                missing.append(
                    f"  - {name}: section '## {section}' still holds the template "
                    f"placeholder {leftover.group()}"
                )

    if missing:
        print(f"Stop blocked: spec folder '{folder}' is incomplete:", file=sys.stderr)
        print("\n" + "\n".join(missing), file=sys.stderr)
        print(
            "\nWrite the missing files/sections and replace every placeholder with real "
            "content (compare against specs/_templates/), then stop again.",
            file=sys.stderr,
        )
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
