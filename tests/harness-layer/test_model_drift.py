"""Pins every model and effort declaration in the harness to the model-selection roster.

`.claude/rules/model-selection.md` claims to be the single source of truth for model
choice, and forbids hard-coding model guidance into templates, tasks, or commands.
Nothing enforced that: the roster drifted away from the files that cite it (a dead dated
id survived in a skill reference, a task template hard-coded an alias pair the roster
never mentions) and no test could fail. These tests make the roster load-bearing — a
model or effort that no longer appears in it breaks the build wherever it is still
declared.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
ROSTER_DOC = REPO_ROOT / ".claude" / "rules" / "model-selection.md"

# `inherit` is the documented "make no choice" value, so it is never drift.
NON_ROSTER_MODELS = {"inherit"}

# A dated id pins one model version forever, which the roster explicitly bans. These two
# sites name one on purpose — as the counter-example and as an error-message format hint.
DATED_ID_ALLOWLIST = {
    Path(".claude/rules/model-selection.md"),
    Path(".claude/skills/meta-agent/scripts/validate_agent.py"),
}
DATED_ID_RE = re.compile(r"claude-(?:opus|sonnet|haiku|fable)-\d")

DECLARATION_ROOTS = (".claude", ".codex", ".agents")


def _table_rows(section: str) -> list[list[str]]:
    """Split a markdown table body into cell lists, dropping header and separator."""
    rows = []
    for line in section.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if not cells or set(cells[0]) <= {"-", ":"}:
            continue
        rows.append(cells)
    return rows[1:]  # drop the header row


def _section(doc: str, heading: str) -> str:
    """Return the body of one `## heading` section."""
    match = re.search(rf"^## {re.escape(heading)}$(.*?)(?=^## |\Z)", doc, re.M | re.S)
    assert match, f"model-selection.md has no '## {heading}' section"
    return match.group(1)


def _first_code_token(cell: str) -> str | None:
    match = re.search(r"`([^`]+)`", cell)
    return match.group(1) if match else None


def _load_roster() -> tuple[set[str], set[str]]:
    """Return (claude aliases, codex model ids) from the roster table."""
    claude, codex = set(), set()
    for cells in _table_rows(_section(ROSTER_DOC.read_text(encoding="utf-8"), "Roster")):
        name, invoke = _first_code_token(cells[0]), cells[1]
        if name is None:
            continue
        if "codex exec" in invoke:
            codex.add(name)
        else:
            claude.add(name)
    return claude, codex


def _load_efforts() -> tuple[set[str], set[str]]:
    """Return (efforts valid for Claude, efforts valid for Codex) from the effort table."""
    claude, codex = set(), set()
    for cells in _table_rows(_section(ROSTER_DOC.read_text(encoding="utf-8"), "Effort")):
        level = _first_code_token(cells[0])
        if level is None:
            continue
        if "✓" in cells[1]:
            claude.add(level)
        if "✓" in cells[2]:
            codex.add(level)
    return claude, codex


CLAUDE_MODELS, CODEX_MODELS = _load_roster()
CLAUDE_EFFORTS, CODEX_EFFORTS = _load_efforts()


def _frontmatter(path: Path) -> dict[str, str]:
    """Parse the top-level `key: value` pairs of a markdown file's YAML frontmatter."""
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---", 4)
    if end == -1:
        return {}
    fields = {}
    for line in text[4:end].splitlines():
        if line.startswith((" ", "\t", "#")) or ":" not in line:
            continue
        key, _, value = line.partition(":")
        fields[key.strip()] = value.strip().strip("\"'")
    return fields


def _claude_declarations(field: str) -> list[tuple[Path, str]]:
    """Every `field:` frontmatter value across Claude agents, commands, and skills."""
    found = []
    for sub in ("agents", "commands", "skills"):
        for path in sorted((REPO_ROOT / ".claude" / sub).rglob("*.md")):
            value = _frontmatter(path).get(field)
            if value:
                found.append((path.relative_to(REPO_ROOT), value))
    return found


def _codex_declarations(key: str) -> list[tuple[Path, str]]:
    """Every `key = "value"` assignment across the Codex agent TOML files."""
    found = []
    for path in sorted((REPO_ROOT / ".codex" / "agents").glob("*.toml")):
        for match in re.finditer(rf'^{re.escape(key)}\s*=\s*"([^"]+)"', path.read_text(), re.M):
            found.append((path.relative_to(REPO_ROOT), match.group(1)))
    return found


def test_roster_parses_into_both_provider_families():
    """A parser that silently matched nothing would make every other test vacuously pass.

    This guards the parser itself, so a reformatted roster table fails loudly here rather
    than quietly disabling the whole gate.
    """
    assert "opus" in CLAUDE_MODELS and "fable" in CLAUDE_MODELS
    assert any(m.startswith("gpt-") for m in CODEX_MODELS)
    assert {"low", "medium", "high"} <= CLAUDE_EFFORTS
    assert "ultra" in CODEX_EFFORTS and "ultra" not in CLAUDE_EFFORTS


def test_roster_never_lists_a_dated_claude_id_as_a_choice():
    """Aliases track the current model; a dated id in the roster would pin it forever."""
    for cells in _table_rows(_section(ROSTER_DOC.read_text(encoding="utf-8"), "Roster")):
        assert not DATED_ID_RE.search(cells[0]), f"roster offers a dated id: {cells[0]}"


@pytest.mark.parametrize(("path", "model"), _claude_declarations("model"), ids=lambda v: str(v))
def test_claude_frontmatter_model_is_on_the_roster(path: Path, model: str):
    """An agent or command naming a retired alias silently falls back to the session model,
    so the deployment decision the roster encodes is lost without any error."""
    assert model in CLAUDE_MODELS | NON_ROSTER_MODELS, (
        f"{path} declares model '{model}', which model-selection.md does not list. "
        f"Roster: {sorted(CLAUDE_MODELS)}"
    )


@pytest.mark.parametrize(("path", "effort"), _claude_declarations("effort"), ids=lambda v: str(v))
def test_claude_frontmatter_effort_is_on_the_roster(path: Path, effort: str):
    """Claude Code clamps an unsupported effort to the next level down instead of failing,
    so a stale level quietly runs the work shallower than the author intended."""
    assert effort in CLAUDE_EFFORTS, (
        f"{path} declares effort '{effort}', which is not a Claude effort level. "
        f"Roster: {sorted(CLAUDE_EFFORTS)}"
    )


@pytest.mark.parametrize(("path", "model"), _codex_declarations("model"), ids=lambda v: str(v))
def test_codex_agent_model_is_on_the_roster(path: Path, model: str):
    """Codex agents pin their model explicitly rather than inheriting config.toml, so a
    retired id fails the review round at run time instead of at commit time."""
    assert model in CODEX_MODELS, (
        f"{path} declares model '{model}', which model-selection.md does not list. "
        f"Roster: {sorted(CODEX_MODELS)}"
    )


@pytest.mark.parametrize(
    ("path", "effort"), _codex_declarations("model_reasoning_effort"), ids=lambda v: str(v)
)
def test_codex_agent_effort_is_on_the_roster(path: Path, effort: str):
    """Same clamp risk as the Claude side, on the provider whose review gate we depend on."""
    assert effort in CODEX_EFFORTS, (
        f"{path} declares effort '{effort}', which is not a Codex effort level. "
        f"Roster: {sorted(CODEX_EFFORTS)}"
    )


def test_no_dated_claude_model_id_outside_the_allowlist():
    """A dated id outdates itself the moment the alias moves on — exactly how
    `claude-sonnet-4-20250514` survived in a skill reference long after that model retired."""
    offenders = []
    for root in DECLARATION_ROOTS:
        for path in sorted((REPO_ROOT / root).rglob("*")):
            if not path.is_file() or path.suffix not in {".md", ".py", ".toml", ".json"}:
                continue
            relative = path.relative_to(REPO_ROOT)
            if relative.parts[:2] == (".claude", "worktrees"):
                continue  # mounted worktrees are other branches' trees, not this one's
            if relative in DATED_ID_ALLOWLIST:
                continue
            for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                if DATED_ID_RE.search(line):
                    offenders.append(f"{relative}:{number}: {line.strip()}")
    assert not offenders, "dated model ids found; use a roster alias:\n" + "\n".join(offenders)


def test_task_templates_defer_to_the_roster_instead_of_naming_models():
    """model-selection.md forbids hard-coding model guidance in templates. A template that
    names its own pair drifts independently of the roster and seeds every plan built from
    it — which is how `opus complex / sonnet otherwise` outlived the roster that dropped it.
    """
    offenders = []
    for path in sorted((REPO_ROOT / "specs" / "_templates").rglob("*.md")):
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if "**Model / Effort:**" not in line:
                continue
            if "model-selection.md" not in line:
                offenders.append(f"{path.relative_to(REPO_ROOT)}:{number}: {line.strip()}")
    assert not offenders, (
        "task templates must point at model-selection.md, not name models:\n" + "\n".join(offenders)
    )
