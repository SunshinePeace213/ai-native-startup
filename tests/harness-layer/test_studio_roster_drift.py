"""Pins every studio role's `model:` and `effort:` to `.claude/rules/studio-layer/roster.md`.

`roster.md` claims to be the single source of truth for who runs each studio seat and
at what stamp, and says the two change together. Nothing enforced that — a role's
agent file could drift from its roster row (or vice versa) with no test to catch it.
These tests re-derive every expectation from the roster table itself, the way
`test_model_drift.py` re-derives from `model-selection.md`, so a stamp that no longer
matches its row breaks the build wherever it is declared.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
ROSTER_DOC = REPO_ROOT / ".claude" / "rules" / "studio-layer" / "roster.md"
AGENTS_DIR = REPO_ROOT / ".claude" / "agents" / "studio-layer"

# The principal's row declares this in its "May escalate" cell instead of an
# escalation path, marking it as the one row with no agent file by design.
NO_AGENT_FILE_MARKER = "No agent file"


@dataclass(frozen=True)
class RosterRow:
    function: str
    model: str
    effort: str
    escalate: str


def _table_rows(text: str) -> list[list[str]]:
    """Split a markdown table's body into cell lists, dropping header and separator.

    Same shape as `test_model_drift.py`'s `_table_rows`: structure, not prose, so a
    row is only ever read from its actual cells.
    """
    rows = []
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if not cells or set(cells[0]) <= {"-", ":"}:
            continue
        rows.append(cells)
    return rows[1:]  # drop the header row


def _first_code_token(cell: str) -> str | None:
    match = re.search(r"`([^`]+)`", cell)
    return match.group(1) if match else None


def _load_roster() -> list[RosterRow]:
    """Return every roster row, in table order, with its code-token cells unwrapped."""
    rows = []
    for cells in _table_rows(ROSTER_DOC.read_text(encoding="utf-8")):
        function = _first_code_token(cells[0])
        model = _first_code_token(cells[2])
        effort = _first_code_token(cells[3])
        if function is None or model is None or effort is None:
            continue
        rows.append(RosterRow(function=function, model=model, effort=effort, escalate=cells[4]))
    return rows


def _role_rows(rows: list[RosterRow]) -> list[RosterRow]:
    """Roster rows that declare an agent file — everything except the principal's."""
    return [r for r in rows if NO_AGENT_FILE_MARKER not in r.escalate]


def _frontmatter(path: Path) -> dict[str, str]:
    """Parse the top-level `key: value` pairs of a markdown file's YAML frontmatter.

    Same shape as `test_model_drift.py`'s `_frontmatter`: a folded multi-line value
    (like `description: >-`) is skipped by its indentation, so only scalar top-level
    fields like `name`, `model`, and `effort` are read.
    """
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


def _agent_files() -> dict[str, Path]:
    """Map each studio agent file's declared `name:` to its path."""
    found = {}
    for path in sorted(AGENTS_DIR.glob("*.md")):
        name = _frontmatter(path).get("name")
        if name:
            found[name] = path
    return found


def test_roster_table_parses():
    """A parser that silently matched nothing would make every other test in this file
    vacuously pass. This guards the parser itself, so a reformatted roster table fails
    loudly here rather than quietly disabling the whole drift gate.
    """
    rows = _load_roster()
    assert len(rows) == 10, f"expected 10 roster rows (principal + 9 roles), got {len(rows)}"
    assert {r.model for r in rows} >= {"fable", "opus", "sonnet"}
    assert {r.effort for r in rows} >= {"xhigh", "high", "medium"}
    assert any(r.function == "principal" for r in rows)
    assert any(r.function == "studio-design-qa" for r in rows)


def test_principal_row_is_skipped():
    """The principal runs as the main session and is never spawned as a subagent, so its
    row must be excluded by what the table itself says (its escalation cell), not by a
    hard-coded name — otherwise a renamed or reordered principal row would silently stop
    being skipped, or a real role would be skipped by mistake.
    """
    rows = _load_roster()
    skipped = [r for r in rows if NO_AGENT_FILE_MARKER in r.escalate]
    assert len(skipped) == 1, f"expected exactly one no-agent-file row, found {len(skipped)}"
    assert skipped[0].function == "principal"
    role_rows = _role_rows(rows)
    assert len(role_rows) == 9
    assert all(r.function != "principal" for r in role_rows)


def test_every_roster_row_has_an_agent_file():
    """A role added to the roster with no matching agent file would never actually run —
    the roster would describe a seat nobody staffs. This fails naming the missing file
    so the gap is fixed instead of silently shipping.
    """
    role_rows = _role_rows(_load_roster())
    agent_files = _agent_files()
    missing = [r.function for r in role_rows if r.function not in agent_files]
    assert not missing, (
        "roster rows with no matching file under .claude/agents/studio-layer/: "
        + ", ".join(missing)
    )


def test_every_agent_file_has_a_roster_row():
    """An agent file with no roster row is an orphan: a seat nobody stamped a model or
    effort for, which means its deployment decision was never actually made. This fails
    naming the orphan file so it is either added to the roster or removed.
    """
    role_rows = _role_rows(_load_roster())
    functions = {r.function for r in role_rows}
    agent_files = _agent_files()
    orphans = [
        str(path.relative_to(REPO_ROOT))
        for name, path in agent_files.items()
        if name not in functions
    ]
    assert not orphans, "agent files with no roster row: " + ", ".join(orphans)


def test_agent_model_matches_its_roster_row():
    """The roster and its agent files must change together — a role's file naming a
    different model than its roster row means the deployment decision written down is
    not the one that actually runs.
    """
    role_rows = _role_rows(_load_roster())
    agent_files = _agent_files()
    mismatches = []
    for row in role_rows:
        path = agent_files.get(row.function)
        if path is None:
            continue  # the missing-file case is covered by its own test
        declared = _frontmatter(path).get("model")
        if declared != row.model:
            relative = path.relative_to(REPO_ROOT)
            mismatches.append(
                f"{relative}: roster says model '{row.model}', file says '{declared}'"
            )
    assert not mismatches, "\n".join(mismatches)


def test_agent_effort_matches_its_roster_row():
    """Same drift risk as the model stamp: an effort that no longer matches its roster
    row means the file quietly runs the role shallower or deeper than intended.
    """
    role_rows = _role_rows(_load_roster())
    agent_files = _agent_files()
    mismatches = []
    for row in role_rows:
        path = agent_files.get(row.function)
        if path is None:
            continue  # the missing-file case is covered by its own test
        declared = _frontmatter(path).get("effort")
        if declared != row.effort:
            relative = path.relative_to(REPO_ROOT)
            mismatches.append(
                f"{relative}: roster says effort '{row.effort}', file says '{declared}'"
            )
    assert not mismatches, "\n".join(mismatches)
