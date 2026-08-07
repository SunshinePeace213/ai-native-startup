"""Pins the wiki layer's command surface and standards rule to their sources of truth.

`AGENTS.md`'s Wiki Layer section registers the `/wiki:*` command family, and
`.claude/rules/wiki-layer/wiki-standards.md`'s Operations table declares each command's
model/effort stamp. Nothing enforced either link, so a command file could go missing or
unregistered, a frontmatter stamp could drift from the table that owns it, or the
standards rule could lose an obligation silently. These tests re-derive every expectation
from AGENTS.md, model-selection.md, and the rule file itself — never from the directory
under test — so a drift between them fails the build instead of surviving unnoticed.
"""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
AGENTS_DOC = REPO_ROOT / "AGENTS.md"
COMMANDS_DIR = REPO_ROOT / ".claude" / "commands" / "wiki"
STANDARDS_DOC = REPO_ROOT / ".claude" / "rules" / "wiki-layer" / "wiki-standards.md"
MODEL_SELECTION_DOC = REPO_ROOT / ".claude" / "rules" / "model-selection.md"

# Which commands carry `argument-hint` is a design decision spec.md states directly
# (ingest and query take user-supplied arguments; lint and status don't) — not something
# derivable from any parsed structure, so it is named here rather than re-parsed.
COMMAND_KEY_SETS = {
    "ingest": {"description", "model", "effort", "argument-hint"},
    "query": {"description", "model", "effort", "argument-hint"},
    "lint": {"description", "model", "effort"},
    "status": {"description", "model", "effort"},
}

REQUIRED_OPERATIONS = {f"/wiki:{name}" for name in COMMAND_KEY_SETS}


def _section(doc: str, heading: str) -> str:
    """Return the body of one exact '## heading' section."""
    match = re.search(rf"^## {re.escape(heading)}$(.*?)(?=^## |\Z)", doc, re.M | re.S)
    assert match, f"doc has no '## {heading}' section"
    return match.group(1)


def _section_containing(doc: str, keyword: str) -> str:
    """Return the body of the one '## ...' section whose heading contains keyword.

    Matches by keyword rather than exact heading text so a cosmetic heading rename
    doesn't break the test — a genuinely missing section still fails loudly.
    """
    pattern = rf"^## [^\n]*{re.escape(keyword)}[^\n]*$(.*?)(?=^## |\Z)"
    matched = re.findall(pattern, doc, re.M | re.S | re.I)
    assert matched, f"{STANDARDS_DOC.name} has no '## ' heading containing {keyword!r}"
    assert len(matched) == 1, f"{len(matched)} headings contain {keyword!r}; keyword is ambiguous"
    return matched[0]


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


def _first_code_token(cell: str) -> str | None:
    match = re.search(r"`([^`]+)`", cell)
    return match.group(1) if match else None


def _split_frontmatter(path: Path) -> tuple[dict[str, str | list[str]], str]:
    """Parse a markdown file's top-level YAML frontmatter into scalars and lists."""
    text = path.read_text(encoding="utf-8")
    assert text.startswith("---\n"), f"{path} has no opening frontmatter fence"
    end = text.find("\n---", 4)
    assert end != -1, f"{path} frontmatter never closes"
    header, body = text[4:end], text[end + 4 :]

    fields: dict[str, str | list[str]] = {}
    current_key: str | None = None
    for line in header.splitlines():
        if not line.strip():
            continue
        if line.startswith((" ", "\t")):
            item = line.strip()
            if item.startswith("- ") and current_key is not None:
                fields.setdefault(current_key, [])
                fields[current_key].append(item[2:].strip().strip("\"'"))
            continue
        key, _, value = line.partition(":")
        key, value = key.strip(), value.strip()
        current_key = key
        fields[key] = value.strip("\"'") if value else []
    return fields, body


def _registered_commands() -> set[str]:
    section = _section(AGENTS_DOC.read_text(encoding="utf-8"), "Wiki Layer")
    return set(re.findall(r"/wiki:(\w[\w-]*)", section))


def _operations_table() -> dict[str, tuple[str, str]]:
    section = _section_containing(STANDARDS_DOC.read_text(encoding="utf-8"), "Operations")
    ops = {}
    for cells in _table_rows(section):
        if len(cells) < 3:
            continue
        command, model, effort = (
            _first_code_token(cells[0]),
            _first_code_token(cells[1]),
            _first_code_token(cells[2]),
        )
        if command and model and effort:
            ops[command] = (model, effort)
    return ops


def _roster_column(heading: str) -> set[str]:
    """Collect the first code token of every row in one model-selection.md table."""
    section = _section(MODEL_SELECTION_DOC.read_text(encoding="utf-8"), heading)
    return {t for cells in _table_rows(section) if (t := _first_code_token(cells[0]))}


def test_command_registry():
    """AGENTS.md's Wiki Layer section registers exactly the files under commands/wiki/."""
    registered = _registered_commands()
    assert registered, "AGENTS.md's Wiki Layer section names no /wiki:<name> commands"

    files = {p.stem for p in COMMANDS_DIR.glob("*.md")}
    missing = registered - files
    unplanned = files - registered
    assert not missing, f"registered but no command file: {sorted(missing)}"
    assert not unplanned, f"command file with no registration: {sorted(unplanned)}"


def test_command_frontmatter():
    """Each command's frontmatter keys, model, and effort match the declared sources."""
    legal_models = _roster_column("Roster")
    legal_efforts = _roster_column("Effort")
    ops = _operations_table()
    assert ops, "wiki-standards.md Operations table parsed no rows"
    assert ops.keys() >= REQUIRED_OPERATIONS, (
        f"Operations table is missing rows for {REQUIRED_OPERATIONS - ops.keys()}"
    )

    command_files = sorted(COMMANDS_DIR.glob("*.md"))
    assert command_files, f"no command files found under {COMMANDS_DIR}"

    for path in command_files:
        name = path.stem
        expected_keys = COMMAND_KEY_SETS.get(name)
        assert expected_keys is not None, (
            f"{path.name} is not in COMMAND_KEY_SETS — add its expected frontmatter keys"
        )

        fields, _ = _split_frontmatter(path)
        assert set(fields.keys()) == expected_keys, (
            f"{path.name} frontmatter keys {sorted(fields.keys())} != "
            f"expected {sorted(expected_keys)}"
        )

        for key in ("description", *sorted(expected_keys & {"argument-hint"})):
            value = fields[key]
            assert isinstance(value, str) and value.strip(), (
                f"{path.name} frontmatter `{key}` is empty — {key!r} = {value!r}"
            )

        command_ref = f"/wiki:{name}"
        assert command_ref in ops, f"{command_ref} missing from the Operations table"
        expected_model, expected_effort = ops[command_ref]
        assert fields["model"] == expected_model, (
            f"{path.name} model '{fields['model']}' != Operations table '{expected_model}'"
        )
        assert fields["effort"] == expected_effort, (
            f"{path.name} effort '{fields['effort']}' != Operations table '{expected_effort}'"
        )
        assert fields["model"] in legal_models, (
            f"{path.name} model '{fields['model']}' is not a roster alias: {sorted(legal_models)}"
        )
        assert fields["effort"] in legal_efforts, (
            f"{path.name} effort '{fields['effort']}' is not a roster level: "
            f"{sorted(legal_efforts)}"
        )

    # A declaration, not a mention: an instruction line that opens by stating the
    # command is read-only. A passing reference to the phrase elsewhere won't match.
    _, query_body = _split_frontmatter(COMMANDS_DIR / "query.md")
    assert re.search(r"^\s*[-*]\s+Read-only\b[^\n]*\balways\b", query_body, re.M | re.I), (
        "query.md body has no instruction line declaring the command read-only, always"
    )


def test_standards_rule():
    """The standards rule is path-scoped and carries every AC4 obligation, section-scoped."""
    fields, _ = _split_frontmatter(STANDARDS_DOC)
    paths = fields.get("paths")
    assert isinstance(paths, list) and paths, (
        f"{STANDARDS_DOC.name} frontmatter has no `paths` list"
    )
    assert any(p in ("ai-docs/**", "ai-docs/wiki/**") for p in paths), (
        f"`paths` does not cover the wiki: {paths}"
    )

    doc = STANDARDS_DOC.read_text(encoding="utf-8")

    schema = _section_containing(doc, "Schema")
    core_fields = {"type", "domain", "status", "created", "updated", "sources", "related"}
    status_values = {"current", "superseded", "disputed"}
    code_spans = set(re.findall(r"`([^`]+)`", schema))
    missing_fields = core_fields - code_spans
    missing_statuses = status_values - code_spans
    assert not missing_fields, f"page-schema section missing field code spans: {missing_fields}"
    assert not missing_statuses, (
        f"page-schema section missing status-value code spans: {missing_statuses}"
    )

    linking = _section_containing(doc, "Linking")
    assert "at least one source" in linking.lower(), (
        "linking section has no every-claim-cites-at-least-one-source rule"
    )

    writing = _section_containing(doc, "Writing")
    writing_lower = writing.lower()
    assert "theme over chronology" in writing_lower.replace("-", " "), (
        "writing-standards section has no theme-over-chronology marker"
    )
    assert "anti-cramming" in writing_lower, "writing-standards section has no anti-cramming marker"
    assert "anti-thinning" in writing_lower, "writing-standards section has no anti-thinning marker"

    domains_section = _section_containing(doc, "Domain")
    assert "open-ended" in domains_section.lower(), (
        "domains section does not state that domains are open-ended"
    )
    assert "schema.md" in domains_section, (
        "domains section missing the per-domain schema.md contract"
    )
    for context in ("personal", "research", "books", "business", "engineering"):
        assert re.search(rf"\b{context}\b", domains_section, re.I), (
            f"domains section missing starter archetype '{context}'"
        )

    privacy = _section_containing(doc, "Privacy")
    privacy_lower = privacy.lower()
    assert "personal/index.md" in privacy_lower, "privacy section missing personal/index.md"
    assert "personal/log.md" in privacy_lower, "privacy section missing personal/log.md"
    assert "wiki/personal/assets/" in privacy_lower, (
        "privacy section missing personal assets folder obligation"
    )
    assert "secret" in privacy_lower and "pii" in privacy_lower, (
        "privacy section missing secret/PII stripping obligation"
    )

    obsidian = _section_containing(doc, "Obsidian")
    for plugin in ("Web Clipper", "Dataview", "Marp"):
        assert plugin in obsidian, f"Obsidian section missing plugin '{plugin}'"

    operations = _section_containing(doc, "Operations")
    ops = _operations_table()
    assert ops.keys() >= REQUIRED_OPERATIONS, (
        f"operations section is missing command rows for {REQUIRED_OPERATIONS - ops.keys()}"
    )
    assert operations.strip(), "operations section is empty"

    requirements = _section_containing(doc, "Requirements")
    requirements_lower = requirements.lower()
    assert "direct lane" in requirements_lower and "full lane" in requirements_lower, (
        "layer-requirements section has no lane-fit statement"
    )
    assert "100%" in requirements, "layer-requirements section missing metrics target 1 (100%)"
    assert "7 days" in requirements_lower, (
        "layer-requirements section missing metrics target 2 (7-day triage)"
    )
    assert "at least one source" in requirements_lower, (
        "layer-requirements section missing metrics target 3 (every claim cites a source)"
    )
    assert "at least one wiki page" in requirements_lower, (
        "layer-requirements section missing metrics target 4 (each plan cites a wiki page)"
    )
    for archetype in ("Prototyper", "Builder", "Maintainer"):
        assert archetype in requirements, (
            f"layer-requirements section missing archetype staffing '{archetype}'"
        )
