#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Stop hook for /harness-layer:harness-plan: block the run from ending until
the per-plan spec folder is complete.

Two checks only: (1) all four files exist, (2) each file has its required
'##' sections. Exit 2 => deny stop; stderr is fed back to Claude so it
completes the gaps. The gate is session-scoped: it reads the Stop-hook stdin
JSON, resolves the invoking session's root from its 'cwd', and gates only the
newest-modified plan folder under THAT root's specs/ -- never any other
worktree's specs/, so a concurrent planning session cannot steal or mask the
target. Underscore-prefixed dirs (_templates) and discovery-only chain folders
(a discovery/ subdir with no spec files yet) are excluded.

Malformed/empty stdin or a cwd outside any git repo degrades down a fixed
fallback chain -- never crash, never exit 2 on plumbing (fail-open).

On a structurally-complete folder, a second pass lints the selected folder's
acceptance-criteria.md '## Validation Commands' bullets: a bullet with no stage
tag, or invoking neither a committed check script nor pytest, or a [plan-time]
check whose path is absent, blocks (exit 2). Later-stage paths not present yet
and absolute-promise wording in spec.md warn only (WARN: on stderr, exit code
unchanged, capped at 10).
"""

import json
import os
import re
import subprocess
import sys
from pathlib import Path, PurePosixPath

REQUIRED_SECTIONS: dict[str, tuple[str, ...]] = {
    "spec.md": (
        "Task Description",
        "Objective",
        "Non-Goals",
        "Requirements & Decisions",
        "Tracking",
        "Relevant Files",
        "Edge Cases",
        "Red Flags",
        "Codex Verification",
        "References",
        "Self Validation",
    ),
    "tasks.md": (
        "Team Orchestration",
        "Team Members",
        "Step by Step Tasks",
    ),
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


def read_stdin_cwd() -> str | None:
    """The session's cwd from the Stop payload, or None if stdin is empty or
    malformed (fail-open: plumbing noise must not crash the gate)."""
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return None
    if isinstance(data, dict):
        cwd = data.get("cwd")
        if isinstance(cwd, str) and cwd:
            return cwd
    return None


def git_toplevel(cwd: str | None) -> Path | None:
    """`git rev-parse --show-toplevel`, run in `cwd` when given; None on any
    failure (not a repo, missing dir, git absent)."""
    args = ["git"]
    if cwd is not None:
        args += ["-C", cwd]
    args += ["rev-parse", "--show-toplevel"]
    try:
        proc = subprocess.run(args, capture_output=True, text=True)
    except OSError:
        return None
    if proc.returncode == 0 and proc.stdout.strip():
        return Path(proc.stdout.strip())
    return None


def resolve_root(stdin_cwd: str | None) -> Path:
    """Session root, first success wins: git toplevel of the stdin cwd -> the
    stdin cwd itself (if a directory) -> $CLAUDE_PROJECT_DIR -> git toplevel of
    the process cwd -> Path.cwd()."""
    if stdin_cwd:
        top = git_toplevel(stdin_cwd)
        if top is not None:
            return top
        if Path(stdin_cwd).is_dir():
            return Path(stdin_cwd)
    env_root = os.environ.get("CLAUDE_PROJECT_DIR")
    if env_root:
        return Path(env_root)
    top = git_toplevel(None)
    if top is not None:
        return top
    return Path.cwd()


def discovery_only(folder: Path) -> bool:
    """A chain folder holding only pre-plan discovery output — not yet a plan."""
    return (folder / "discovery").is_dir() and not any(
        (folder / name).is_file() for name in REQUIRED_SECTIONS
    )


def newest_plan_folder(root: Path) -> Path | None:
    specs = root / "specs"
    folders = [
        folder
        for folder in specs.iterdir()
        if folder.is_dir() and not folder.name.startswith("_") and not discovery_only(folder)
    ]
    return max(folders, key=lambda folder: folder.stat().st_mtime, default=None)


STAGE_TAGS = ("[plan-time]", "[child-build-time]", "[post-merge]")
WARN_CAP = 10
_CODE = re.compile(r"`([^`]+)`")
_LEGEND = re.compile(r"^`\[(?:plan-time|child-build-time|post-merge)\]`\s*[—–-]")
_PROMISE = re.compile(
    r"\b(?:always|never|guaranteed|guarantees|under no circumstances|in all cases)\b",
    re.IGNORECASE,
)


def validation_bullets(text: str) -> list[tuple[int, str]]:
    """(line_no, bullet_text) for each command bullet under '## Validation
    Commands' — section lines starting '- ', minus the stage-tag legend
    definitions and intro/continuation prose. Empty if the section is absent."""
    out: list[tuple[int, str]] = []
    in_section = False
    for lineno, line in enumerate(text.splitlines(), 1):
        if line.startswith("## "):
            in_section = line.strip() == "## Validation Commands"
            continue
        if not in_section or not line.startswith("- "):
            continue
        content = line[2:].strip()
        if _LEGEND.match(content):
            continue  # stage-tag definition, not a command
        out.append((lineno, content))
    return out


def command_target(content: str) -> tuple[str, str] | None:
    """(kind, path) for a bullet's committed-check invocation -- kind is
    'script' (`uv run --script`) or 'pytest' (`uv run pytest`), path is the
    target it names -- or None if it invokes neither."""
    for span in _CODE.findall(content):
        span = span.strip()
        m = re.match(r"uv run --script\s+(\S+)", span)
        if m:
            return ("script", m.group(1))
        m = re.match(r"uv run pytest\s+(\S+)", span)
        if m:
            return ("pytest", m.group(1).split("::")[0])
    return None


def lint_validation_commands(folder: Path, root: Path) -> tuple[list[str], list[str]]:
    """(blocks, warns) message lines for the folder's acceptance-criteria.md
    Validation Commands (runs only when that section exists — a missing section
    is already caught by the required-sections check) and spec.md wording."""
    blocks: list[str] = []
    warns: list[str] = []
    text = (folder / "acceptance-criteria.md").read_text(errors="replace")
    for lineno, bullet in validation_bullets(text):
        loc = f"acceptance-criteria.md:{lineno}"
        stage = next((tag for tag in STAGE_TAGS if tag in bullet), None)
        if stage is None:
            blocks.append(
                f"  - {loc}: no stage tag ([plan-time]/[child-build-time]/[post-merge]): {bullet}"
            )
            continue
        target = command_target(bullet)
        if target is None:
            blocks.append(
                f"  - {loc}: invokes neither `uv run --script …` nor `uv run pytest …`: {bullet}"
            )
            continue
        kind, path = target
        pure = PurePosixPath(path)
        if pure.is_absolute() or ".." in pure.parts:
            blocks.append(
                f"  - {loc}: check path must be repo-relative (no absolute or '..'): {path}"
            )
            continue
        if kind == "script":
            checks_dir = PurePosixPath(folder.relative_to(root)) / "checks"
            if checks_dir not in pure.parents:
                blocks.append(f"  - {loc}: script check must live under {checks_dir}/: {path}")
                continue
        present = (root / path).is_file() if kind == "script" else (root / path).exists()
        if not present:
            if stage == "[plan-time]":
                blocks.append(f"  - {loc}: [plan-time] check path does not exist: {path}")
            else:
                warns.append(f"{loc}: {stage} path not present yet (the build creates it): {path}")

    spec = folder / "spec.md"
    if spec.is_file():
        for lineno, line in enumerate(spec.read_text(errors="replace").splitlines(), 1):
            if _PROMISE.search(line):
                warns.append(f"spec.md:{lineno}: absolute-promise wording — soften or qualify")
    return blocks, warns


def main() -> int:
    root = resolve_root(read_stdin_cwd())
    if not (root / "specs").is_dir():
        return 0  # no specs dir under this session's root -> nothing to gate

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
        missing += [
            f"  - {name}: missing section '## {section}'"
            for section in sections
            if f"## {section}" not in text
        ]

    if missing:
        print(f"Stop blocked: spec folder '{folder}' is incomplete:", file=sys.stderr)
        print("\n" + "\n".join(missing), file=sys.stderr)
        print(
            "\nComplete the missing files/sections (compare against specs/_templates/), "
            "then stop again.",
            file=sys.stderr,
        )
        return 2

    blocks, warns = lint_validation_commands(folder, root)
    for warning in warns[:WARN_CAP]:
        print(f"WARN: {warning}", file=sys.stderr)
    if blocks:
        print(
            f"Stop blocked: validation commands in '{folder}/acceptance-criteria.md' "
            "are non-compliant:",
            file=sys.stderr,
        )
        print("\n" + "\n".join(blocks), file=sys.stderr)
        print(
            "\nEach bullet needs a stage tag and a committed check "
            "(`uv run --script specs/<plan>/checks/…` or `uv run pytest …`); "
            "[plan-time] checks must exist now.",
            file=sys.stderr,
        )
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
