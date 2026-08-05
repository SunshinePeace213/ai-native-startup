"""Pins the v2 pipeline formats: the per-plan metrics block, the lessons digest,
and the findings-ledger header.

The v2 design measures the pipeline against one fixed set of run metrics (lane,
cycles per flavor, findings by standard, uncited-to-advisory count, fix commits,
unverified tail, disputed/overridden, lint catches). Two files must carry that
set — the summary template's ## Metrics block (written per plan at review time)
and the digest's ## Metrics log header (the trailing window the production-ready
targets are measured over). A field missing from either silently drops a target
from measurement, which is exactly the write-only-state failure the digest exists
to close.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SUMMARY_TEMPLATE = REPO_ROOT / "specs" / "_templates" / "summary.md"
DIGEST = REPO_ROOT / "specs" / "lessons" / "digest.md"
GATE_SKILL = REPO_ROOT / ".claude" / "skills" / "codex-gate" / "SKILL.md"

# Canonical metric -> (label in summary.md ## Metrics, column in the digest ## Metrics log).
METRIC_FIELDS = {
    "lane": ("**Lane:**", "Lane"),
    "spec cycles": ("**Spec gate:**", "Spec cycles"),
    "impl cycles": ("**Impl gate:**", "Impl cycles"),
    "findings by standard": ("**Findings by standard:**", "By standard"),
    "uncited to advisory": ("**Uncited→advisory:**", "Uncited→adv"),
    "fix commits": ("**Fix commits:**", "Fix commits"),
    "unverified tail": ("**Unverified tail:**", "Unverified tail"),
    "disputed": ("**Disputed:**", "Disputed"),
    "overridden": ("**Overridden:**", "Overridden"),
    "lint catches": ("**Lint catches (pre-Codex):**", "Lint catches"),
}

LEDGER_HEADER = "| ID | STD | Lens | Sev | Conf | Finding | Disposition | Evidence |"
CATEGORIES_HEADER = "| Surface | Category | Seen | Plans | Disposition |"


def _section(text: str, heading: str) -> str:
    match = re.search(rf"^## {re.escape(heading)}$(.*?)(?=^## |\Z)", text, re.M | re.S)
    assert match, f"missing '## {heading}' section"
    return match.group(1)


def _table_header(section: str) -> list[str]:
    """Cells of the first table header row in a section."""
    for line in section.splitlines():
        line = line.strip()
        if line.startswith("|"):
            return [c.strip() for c in line.strip("|").split("|")]
    pytest.fail("section has no table")


@pytest.mark.parametrize("metric", METRIC_FIELDS, ids=str)
def test_summary_template_metrics_block_carries_every_field(metric: str):
    """A plan whose summary lacks a metric can't feed the digest that measures it."""
    label = METRIC_FIELDS[metric][0]
    body = _section(SUMMARY_TEMPLATE.read_text(encoding="utf-8"), "Metrics")
    assert label in body, f"summary template ## Metrics lacks the {label} field"


@pytest.mark.parametrize("metric", METRIC_FIELDS, ids=str)
def test_digest_metrics_log_covers_every_field(metric: str):
    """The digest is where the trailing-window targets are read; a dropped column
    makes its target unmeasurable without anyone noticing."""
    column = METRIC_FIELDS[metric][1]
    header = _table_header(_section(DIGEST.read_text(encoding="utf-8"), "Metrics log"))
    assert any(column in cell for cell in header), (
        f"digest ## Metrics log header lacks a '{column}' column: {header}"
    )


def test_digest_categories_table_shape():
    """The category table is the plan-time read-back edge; harness-plan greps it
    by surface, so the column set is a contract, not a convention."""
    header = _table_header(_section(DIGEST.read_text(encoding="utf-8"), "Categories"))
    assert header == [c.strip() for c in CATEGORIES_HEADER.strip("|").split("|")]


def test_ledger_format_carries_std_and_lens_columns():
    """Blocking classification keys on the cited standard and the digest keys on
    the lens; a ledger without the columns can't record either."""
    assert LEDGER_HEADER in GATE_SKILL.read_text(encoding="utf-8"), (
        f"codex-gate SKILL.md must define the ledger header exactly as: {LEDGER_HEADER}"
    )


STANDARDS = {
    "S": REPO_ROOT / ".claude" / "rules" / "harness-layer" / "spec-standards.md",
    "I": REPO_ROOT / ".claude" / "rules" / "harness-layer" / "impl-standards.md",
}


def _stamped_ids(prefix: str) -> set[str]:
    """The stable IDs a standards file actually declares (`**S1 · Name**` rows)."""
    text = STANDARDS[prefix].read_text(encoding="utf-8")
    ids = set(re.findall(rf"\*\*({prefix}\d+) ·", text))
    assert ids, f"no stamped {prefix}<n> IDs parsed from {STANDARDS[prefix].name}"
    return ids


def _cluster_ids(prefix: str) -> set[str]:
    """Every standard ID the gate's lens-cluster table assigns to a lens or the lint."""
    section = _section(GATE_SKILL.read_text(encoding="utf-8"), "Lens clusters")
    ids = set(re.findall(rf"\b({prefix}\d+)\b", section))
    assert ids, f"no {prefix}<n> IDs parsed from the Lens clusters table"
    return ids


@pytest.mark.parametrize("prefix", ["S", "I"])
def test_lens_clusters_cover_every_stamped_standard(prefix: str):
    """Coverage is the panel's whole point: a standard no lens or lint owns is
    silently unreviewed, and a lens citing a phantom ID reviews against nothing.
    Both sides re-derive, so adding S9 without assigning it a lens fails here."""
    stamped, clustered = _stamped_ids(prefix), _cluster_ids(prefix)
    assert stamped == clustered, (
        f"unassigned standards: {sorted(stamped - clustered)}; "
        f"phantom cluster IDs: {sorted(clustered - stamped)}"
    )
