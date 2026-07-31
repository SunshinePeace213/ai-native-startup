"""Contract tests for the four studio check scripts.

They are plain CLIs, not hooks, so each runs through `uv run --script` with its target
as argv[1] and is judged by its exit code and its file:line diagnostics: 0 pass, 1 a
countable failure, 2 the check could not run its arithmetic. Every fixture is built
under tmp_path so the suite stays parallel-safe.
"""

import shutil
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPTS = REPO_ROOT / ".claude" / "scripts" / "studio-layer"
SKILL = REPO_ROOT / ".claude" / "skills" / "studio-layer" / "studio-client-questions" / "SKILL.md"

STATES = ("hover", "focus", "disabled", "loading", "empty", "error")

INVENTORY = """\
| Component | Breakpoints | Colour tokens used |
| --- | --- | --- |
| PrimaryButton | mobile, desktop | `--accent`, `--on-accent` |
| SearchResults | mobile, desktop | `--text`, `--bg` |
"""

TOKENS = """\
| Foreground | Background | Kind | Used for |
| --- | --- | --- | --- |
| `--on-accent` `#FFFFFF` | `--accent` `#8C4A1F` | ui-component | button label |
| `--text` `#2C2825` | `--bg` `#FAF8F5` | normal-text | body copy |

| Target | Width (px) | Height (px) |
| --- | --- | --- |
| PrimaryButton | 44 | 44 |
| SearchResults | 44 | 32 |
"""

BRIEF = """\
# Project brief

- **Revision rounds:** 2 (plus polish)
"""

CHANGE_ORDER = """\
# Change order 1

- **Requested:** swap the hero video for a still image
- **Cost — rounds:** 1
- **Cost — time:** 3 business days
- **Approved by:** Jordan Reyes · 2026-08-14
"""


def run_check(script: Path | str, target) -> subprocess.CompletedProcess:
    path = script if isinstance(script, Path) else SCRIPTS / script
    return subprocess.run(
        ["uv", "run", "--script", str(path), str(target)],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )


def write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def matrix(breakpoints=("mobile", "desktop"), rows=None, columns=STATES) -> str:
    """A states matrix; rows maps a component to its per-state cell overrides."""
    rows = {"PrimaryButton": {}, "SearchResults": {}} if rows is None else rows
    out = []
    for breakpoint_name in breakpoints:
        out += [
            f"### {breakpoint_name}",
            "",
            "| Component | " + " | ".join(columns) + " |",
            "| --- |" + " --- |" * len(columns),
        ]
        out += [
            "| " + component + " | " + " | ".join(cells.get(c, "specified") for c in columns) + " |"
            for component, cells in rows.items()
        ]
        out.append("")
    return "\n".join(out)


def handoff(tmp_path: Path, *, states=None, tokens=TOKENS, inventory=INVENTORY) -> Path:
    """A project carrying a signed inventory and a handoff; returns the project dir."""
    project = tmp_path / "clients" / "acme" / "site"
    if inventory is not None:
        write(project / "structure" / "inventory.md", inventory)
    write(project / "handoff" / "states-matrix.md", matrix() if states is None else states)
    write(project / "handoff" / "tokens.md", tokens)
    return project


def skill_dimensions() -> list[str]:
    """The dimension names, re-derived from the shipped question bank."""
    names, inside = [], False
    for line in SKILL.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            inside = line[3:].strip() == "Dimensions"
        elif inside and line.startswith("### "):
            names.append(line[4:].strip())
    return names


def notes_for(dimensions, blank=()) -> str:
    body = []
    for name in dimensions:
        body += [f"## {name}", ""]
        if name not in blank:
            body += [f"Established with the client: {name.lower()} is settled.", ""]
    return "\n".join(body)


def revisions(tmp_path: Path, *, brief=BRIEF, rounds=(), change_orders=()) -> Path:
    """A project with a signed brief, a revision log, and any change orders."""
    project = tmp_path / "clients" / "acme" / "site"
    if brief is not None:
        write(project / "definition" / "project-brief.md", brief)
    log = ["| Round | Date | Requested | Change order |", "| --- | --- | --- | --- |"]
    log += [f"| {n} | 2026-08-1{n} | a change | {ref} |" for n, ref in rounds]
    write(project / "prototype" / "revision-log.md", "\n".join(log) + "\n")
    for name, text in change_orders:
        write(project / "change-orders" / name, text)
    return project


# --- AC6: question coverage is re-derived from the skill ------------------------------


def test_unanswered_dimension_fails(tmp_path):
    """A dimension left silent is the failure the coverage check exists to catch: the
    notes carry its heading but nothing under it, and silence is not an answer."""
    dimensions = skill_dimensions()
    notes = write(tmp_path / "notes.md", notes_for(dimensions, blank={dimensions[3]}))
    result = run_check("check_question_coverage.py", notes)
    assert result.returncode == 1, result.stdout
    assert f"{notes}:" in result.stdout
    assert dimensions[3] in result.stdout


def test_explicit_na_because_passes(tmp_path):
    """'N/A, because ...' is a decision the client made, not a gap -- the check must
    accept it, or the only way to close a dimension would be to invent an answer."""
    dimensions = skill_dimensions()
    body = notes_for(dimensions, blank={dimensions[3]})
    body = body.replace(
        f"## {dimensions[3]}\n\n",
        f"## {dimensions[3]}\n\nN/A, because the client sells offline only.\n\n",
    )
    notes = write(tmp_path / "notes.md", body)
    result = run_check("check_question_coverage.py", notes)
    assert result.returncode == 0, result.stdout


def test_adding_a_skill_dimension_changes_what_is_required(tmp_path):
    """The proof that the checker re-derives the list rather than carrying a copy: the
    same notes pass, then fail, because the skill beside the script gained a heading."""
    scripts = tmp_path / ".claude" / "scripts" / "studio-layer"
    scripts.mkdir(parents=True)
    staged = scripts / "check_question_coverage.py"
    shutil.copy(SCRIPTS / "check_question_coverage.py", staged)
    skill = (
        tmp_path / ".claude" / "skills" / "studio-layer" / "studio-client-questions" / "SKILL.md"
    )
    two = "# Bank\n\n## Dimensions\n\n### Budget\n\n### Brand voice\n"
    write(skill, two)
    notes = write(tmp_path / "notes.md", notes_for(["Budget", "Brand voice"]))

    assert run_check(staged, notes).returncode == 0

    write(skill, two + "\n### Success at six months\n")
    result = run_check(staged, notes)
    assert result.returncode == 1, result.stdout
    assert "Success at six months" in result.stdout


# --- AC11: the states matrix counts cells and cannot pass empty -----------------------


def test_full_matrix_passes(tmp_path):
    """Every inventory component has a row at every breakpoint it declares, and every
    state on it is specified -- the only shape that should exit 0."""
    project = handoff(tmp_path)
    result = run_check("check_states_matrix.py", project / "handoff" / "states-matrix.md")
    assert result.returncode == 0, result.stdout


def test_single_blank_cell_fails_and_names_it(tmp_path):
    """One blank cell is the whole point: the diagnostic must name the file, line,
    component, breakpoint and state so the gap is fixable without hunting."""
    states = matrix(rows={"PrimaryButton": {"focus": ""}, "SearchResults": {}})
    project = handoff(tmp_path, states=states)
    target = project / "handoff" / "states-matrix.md"
    result = run_check("check_states_matrix.py", target)
    assert result.returncode == 1, result.stdout
    assert f"{target}:5: PrimaryButton at mobile leaves 'focus' unfilled" in result.stdout
    assert result.stdout.count("unfilled") == 2  # mobile and desktop


def test_component_row_with_no_states_fails(tmp_path):
    """A row present but empty is unfilled, not skipped -- otherwise adding a bare row
    for a component would satisfy the check that its states are specced."""
    rows = {
        "PrimaryButton": {},
        "SearchResults": {},
        "Card": dict.fromkeys(STATES, ""),
    }
    inventory = INVENTORY + "| Card | mobile, desktop | `--surface` |\n"
    project = handoff(tmp_path, states=matrix(rows=rows), inventory=inventory)
    result = run_check("check_states_matrix.py", project / "handoff" / "states-matrix.md")
    assert result.returncode == 1, result.stdout
    for state in STATES:
        assert f"Card at mobile leaves '{state}' unfilled" in result.stdout
    assert "no matrix row for Card" not in result.stdout


def test_matrix_with_no_component_rows_fails(tmp_path):
    """A matrix with headers and no rows must fail against the signed inventory, naming
    every pair it does not cover -- an empty table is the emptiest vacuous pass."""
    project = handoff(tmp_path, states=matrix(rows={}))
    result = run_check("check_states_matrix.py", project / "handoff" / "states-matrix.md")
    assert result.returncode == 1, result.stdout
    for component in ("PrimaryButton", "SearchResults"):
        for breakpoint_name in ("mobile", "desktop"):
            assert f"no matrix row for {component} at breakpoint {breakpoint_name}" in result.stdout


def test_matrix_with_no_breakpoints_fails(tmp_path):
    """Cells only count under a '### <breakpoint>' heading. A bare table specifies no
    breakpoint, so every pair the inventory declares is still missing."""
    states = "| Component | " + " | ".join(STATES) + " |\n| --- |" + " --- |" * len(STATES) + "\n"
    states += "| PrimaryButton | " + " | ".join(["specified"] * len(STATES)) + " |\n"
    project = handoff(tmp_path, states=states)
    result = run_check("check_states_matrix.py", project / "handoff" / "states-matrix.md")
    assert result.returncode == 1, result.stdout
    assert result.stdout.count("no matrix row for") == 4


def test_missing_state_column_fails(tmp_path):
    """Dropping a column must not drop the requirement -- an absent state reads exactly
    like a blank cell, or a matrix could shrink its way to green."""
    columns = tuple(state for state in STATES if state != "error")
    project = handoff(tmp_path, states=matrix(columns=columns))
    result = run_check("check_states_matrix.py", project / "handoff" / "states-matrix.md")
    assert result.returncode == 1, result.stdout
    assert result.stdout.count("leaves 'error' unfilled") == 4


# --- AC12: contrast and tap targets are computed, not asserted ------------------------


def test_known_pair_matches_hand_computed_ratio(tmp_path):
    """Pin the arithmetic, not the branching. #8A837A on #FAF8F5, computed by hand:

    sRGB channels linearise as c/12.92 below 0.03928, else ((c+0.055)/1.055)**2.4.
    Foreground (138, 131, 122) -> (0.254153, 0.226963, 0.194618);
    L_fg = 0.2126*0.254153 + 0.7152*0.226963 + 0.0722*0.194618 = 0.230408.
    Background (250, 248, 245) -> (0.955973, 0.938686, 0.913099);
    L_bg = 0.2126*0.955973 + 0.7152*0.938686 + 0.0722*0.913099 = 0.940514.
    Ratio = (0.940514 + 0.05) / (0.230408 + 0.05) = 0.990514 / 0.280408 = 3.5324 -> 3.53:1.

    Declared normal-text (4.5:1), so the script must print that computed value.
    """
    tokens = TOKENS.replace(
        "| `--text` `#2C2825` | `--bg` `#FAF8F5` | normal-text | body copy |",
        "| `--text` `#8A837A` | `--bg` `#FAF8F5` | normal-text | body copy |",
    )
    project = handoff(tmp_path, tokens=tokens)
    result = run_check("check_contrast.py", project / "handoff" / "tokens.md")
    assert result.returncode == 1, result.stdout
    assert "3.53:1" in result.stdout
    assert "Soriza project threshold" in result.stdout


def test_pair_below_threshold_fails(tmp_path):
    """A pair under its threshold is a countable failure naming the pair and the file
    line, never a soft warning."""
    tokens = TOKENS.replace("`--text` `#2C2825`", "`--text` `#CCCCCC`")
    project = handoff(tmp_path, tokens=tokens)
    target = project / "handoff" / "tokens.md"
    result = run_check("check_contrast.py", target)
    assert result.returncode == 1, result.stdout
    assert f"{target}:4:" in result.stdout
    assert "#CCCCCC" in result.stdout


def test_undersized_tap_target_fails(tmp_path):
    """Shrinking one target below 24 px is what flips the verdict, so the compliant
    fixture is checked too -- otherwise a red for any other reason would read as proof."""
    compliant = handoff(tmp_path / "compliant") / "handoff" / "tokens.md"
    assert run_check("check_contrast.py", compliant).returncode == 0

    tokens = TOKENS.replace("| SearchResults | 44 | 32 |", "| SearchResults | 20 | 32 |")
    project = handoff(tmp_path / "undersized", tokens=tokens)
    result = run_check("check_contrast.py", project / "handoff" / "tokens.md")
    assert result.returncode == 1, result.stdout
    assert "SearchResults is 20x32 px" in result.stdout


def test_empty_pair_table_fails(tmp_path):
    """No pairs is nothing to compute, not a clean bill of health -- exit 2, so the
    designer is told the table is empty rather than that the palette is fine."""
    tokens = TOKENS.replace(
        "| `--on-accent` `#FFFFFF` | `--accent` `#8C4A1F` | ui-component | button label |\n", ""
    )
    tokens = tokens.replace(
        "| `--text` `#2C2825` | `--bg` `#FAF8F5` | normal-text | body copy |\n", ""
    )
    project = handoff(tmp_path, tokens=tokens)
    result = run_check("check_contrast.py", project / "handoff" / "tokens.md")
    assert result.returncode == 2, result.stdout
    assert "empty" in result.stdout


def test_empty_target_table_fails(tmp_path):
    """Same for tap targets: an empty target table cannot be measured, so it exits 2
    rather than reporting every inventory component as merely uncovered."""
    tokens = TOKENS.replace("| PrimaryButton | 44 | 44 |\n| SearchResults | 44 | 32 |\n", "")
    project = handoff(tmp_path, tokens=tokens)
    result = run_check("check_contrast.py", project / "handoff" / "tokens.md")
    assert result.returncode == 2, result.stdout
    assert "empty" in result.stdout


def test_malformed_hex_exits_2(tmp_path):
    """A typo must never be reported as a contrast failure a designer would chase --
    that distinction is what makes exit 1 trustworthy."""
    tokens = TOKENS.replace("`#2C2825`", "`#2C282`")
    project = handoff(tmp_path, tokens=tokens)
    result = run_check("check_contrast.py", project / "handoff" / "tokens.md")
    assert result.returncode == 2, result.stdout
    assert "#RRGGBB" in result.stdout


def test_one_compliant_pair_cannot_stand_in_for_the_rest(tmp_path):
    """The vacuous pass AC12 names: every pair and target left in the table is compliant,
    but the signed inventory declares components and tokens nothing checks."""
    tokens = TOKENS.replace(
        "| `--text` `#2C2825` | `--bg` `#FAF8F5` | normal-text | body copy |\n", ""
    )
    tokens = tokens.replace("| SearchResults | 44 | 32 |\n", "")
    project = handoff(tmp_path, tokens=tokens)
    result = run_check("check_contrast.py", project / "handoff" / "tokens.md")
    assert result.returncode == 1, result.stdout
    assert "colour token --text appears in no checked foreground/background pair" in result.stdout
    assert "SearchResults has no tap-target row" in result.stdout


@pytest.mark.parametrize(
    ("script", "target"),
    [("check_states_matrix.py", "states-matrix.md"), ("check_contrast.py", "tokens.md")],
)
def test_missing_inventory_exits_2(tmp_path, script, target):
    """Without the client-signed component list both checks would quantify only over
    what the handoff happens to declare, so a missing baseline is never a pass."""
    project = handoff(tmp_path, inventory=None)
    result = run_check(script, project / "handoff" / target)
    assert result.returncode == 2, result.stdout
    assert "inventory" in result.stdout


# --- AC13: the revision count is arithmetic -------------------------------------------


def test_round_within_allowance_passes(tmp_path):
    """Rounds the client already bought need no paperwork."""
    project = revisions(tmp_path, rounds=[(1, "-"), (2, "-")])
    result = run_check("check_revision_count.py", project)
    assert result.returncode == 0, result.stdout


def test_round_past_allowance_without_change_order_fails(tmp_path):
    """The round nobody paid for is the one the counter exists to find."""
    project = revisions(tmp_path, rounds=[(1, "-"), (2, "-"), (3, "-")])
    result = run_check("check_revision_count.py", project)
    assert result.returncode == 1, result.stdout
    assert "round 3 is past the 2-round allowance" in result.stdout


def test_round_past_allowance_with_complete_change_order_passes(tmp_path):
    """A round past the allowance is legitimate once a complete change order buys it."""
    project = revisions(
        tmp_path,
        rounds=[(1, "-"), (2, "-"), (3, "`change-orders/1.md`")],
        change_orders=[("1.md", CHANGE_ORDER)],
    )
    result = run_check("check_revision_count.py", project)
    assert result.returncode == 0, result.stdout


def test_change_order_missing_cost_rounds_fails(tmp_path):
    """Presence is not enough: a change order with no cost buys nothing, so an empty
    document cannot be dropped in to clear the gate."""
    incomplete = CHANGE_ORDER.replace("- **Cost — rounds:** 1\n", "")
    project = revisions(
        tmp_path,
        rounds=[(1, "-"), (2, "-"), (3, "`change-orders/1.md`")],
        change_orders=[("1.md", incomplete)],
    )
    result = run_check("check_revision_count.py", project)
    assert result.returncode == 1, result.stdout
    assert "'Cost - rounds' is not an integer" in result.stdout


def test_unsigned_change_order_fails(tmp_path):
    """Nobody approved it, so it is a request, not an agreement."""
    unsigned = CHANGE_ORDER.replace("- **Approved by:** Jordan Reyes · 2026-08-14\n", "")
    project = revisions(
        tmp_path,
        rounds=[(1, "-"), (2, "-"), (3, "`change-orders/1.md`")],
        change_orders=[("1.md", unsigned)],
    )
    result = run_check("check_revision_count.py", project)
    assert result.returncode == 1, result.stdout
    assert "'Approved by' carries no YYYY-MM-DD date" in result.stdout


def test_changing_the_brief_allowance_changes_the_verdict(tmp_path):
    """The allowance is re-derived from the signed brief every run: one unchanged log
    flips verdict when the brief that sold the rounds says a different number."""
    project = revisions(tmp_path, rounds=[(1, "-"), (2, "-"), (3, "-")])
    assert run_check("check_revision_count.py", project).returncode == 1

    write(project / "definition" / "project-brief.md", BRIEF.replace("** 2 (", "** 3 ("))
    result = run_check("check_revision_count.py", project)
    assert result.returncode == 0, result.stdout


def test_brief_with_no_allowance_exits_2(tmp_path):
    """A missing baseline is a different defect from exceeding it: the brief never sold
    a number of rounds, so there is no arithmetic to do."""
    project = revisions(tmp_path, brief="# Project brief\n", rounds=[(1, "-")])
    result = run_check("check_revision_count.py", project)
    assert result.returncode == 2, result.stdout
    assert "Revision rounds" in result.stdout
