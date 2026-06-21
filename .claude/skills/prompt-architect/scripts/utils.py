"""Shared utilities for prompt-architect scripts.

Forked from skill-creator's utils.py and extended to handle all three
artifact types: skill (directory containing SKILL.md), command (single .md
file), and subagent (single .md file). All three share the same frontmatter
shape (name + description); only the disk layout differs.
"""

from pathlib import Path


def resolve_artifact_md(artifact_path: Path) -> Path:
    """Return the .md file holding the frontmatter for any artifact type.

    Skills are directories: SKILL.md lives inside.
    Commands and subagents are single .md files: they ARE the artifact.
    """
    if artifact_path.is_dir():
        return artifact_path / "SKILL.md"
    return artifact_path


def parse_skill_md(artifact_path: Path) -> tuple[str, str, str]:
    """Parse an artifact's markdown file, returning (name, description, full_content).

    Accepts skill directories, command files, or subagent files.
    """
    md_path = resolve_artifact_md(artifact_path)
    content = md_path.read_text()
    lines = content.split("\n")

    if lines[0].strip() != "---":
        raise ValueError(f"{md_path} missing frontmatter (no opening ---)")

    end_idx = None
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            end_idx = i
            break

    if end_idx is None:
        raise ValueError(f"{md_path} missing frontmatter (no closing ---)")

    name = ""
    description = ""
    frontmatter_lines = lines[1:end_idx]
    i = 0
    while i < len(frontmatter_lines):
        line = frontmatter_lines[i]
        if line.startswith("name:"):
            name = line[len("name:"):].strip().strip('"').strip("'")
        elif line.startswith("description:"):
            value = line[len("description:"):].strip()
            if value in (">", "|", ">-", "|-"):
                continuation_lines: list[str] = []
                i += 1
                while i < len(frontmatter_lines) and (frontmatter_lines[i].startswith("  ") or frontmatter_lines[i].startswith("\t")):
                    continuation_lines.append(frontmatter_lines[i].strip())
                    i += 1
                description = " ".join(continuation_lines)
                continue
            else:
                description = value.strip('"').strip("'")
        i += 1

    return name, description, content
