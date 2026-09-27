"""The capability matrix combines catalog status and rule provenance."""

from __future__ import annotations

import pytest

from ccnl_engine.knowledge.service.capability_catalog_loader import (
    load_capability_catalog,
)
from ccnl_engine.payroll.domain.capability_catalog import (
    CapabilityEntry,
    CapabilityStatus,
)
from scripts.docs.gen_capability_matrix import (
    build_page,
    capability_label,
    capability_rows,
    latest_catalog_year,
)

_COMPUTED = CapabilityEntry("irpef", CapabilityStatus.COMPUTED, "IRPEF")


@pytest.mark.parametrize(
    ("status", "counts", "label"),
    [
        (CapabilityStatus.NOT_COMPUTED, {"verified": 2}, "unavailable"),
        (CapabilityStatus.BLOCKED, {}, "unavailable"),
        (CapabilityStatus.PARTIALLY_COMPUTED, {"verified": 2}, "simplified"),
        (CapabilityStatus.COMPUTED, {"derived": 3, "assumed": 1}, "simplified"),
        (CapabilityStatus.COMPUTED, {"missing": 1}, "simplified"),
        (CapabilityStatus.COMPUTED, {"verified": 2}, "verified"),
        (CapabilityStatus.COMPUTED, {"verified": 1, "derived": 1}, "implemented"),
        (CapabilityStatus.COMPUTED, {}, "implemented"),
    ],
)
def test_label(status: CapabilityStatus, counts: dict[str, int], label: str) -> None:
    """Unavailable wins, then simplified, then verified, then implemented."""
    entry = CapabilityEntry("x", status)
    assert capability_label(entry, counts) == label


@pytest.mark.parametrize(
    ("status", "label"),
    [
        (CapabilityStatus.COMPUTED, "caller-supplied"),
        (CapabilityStatus.PARTIALLY_COMPUTED, "caller-supplied"),
        (CapabilityStatus.NOT_COMPUTED, "unavailable"),
    ],
)
def test_caller_supplied_label(status: CapabilityStatus, label: str) -> None:
    """A capability computed from caller values is labelled so, not verified."""
    entry = CapabilityEntry("overtime", status)
    assert capability_label(entry, {"verified": 1}) == label


def test_rows_show_rule_counts_by_status() -> None:
    """A row counts the rules by status; no rules reads as none bundled."""
    catalog = load_capability_catalog(latest_catalog_year())
    counts = {"irpef": {"verified": 0, "derived": 24, "assumed": 0, "missing": 0}}
    rows = capability_rows(catalog, counts)
    (irpef,) = [row for row in rows if row.startswith("| `irpef` ")]
    (inail,) = [row for row in rows if row.startswith("| `inail` ")]
    assert irpef.endswith("| computed | implemented | 0 / 24 / 0 / 0 |")
    assert inail.endswith("| partially_computed | simplified | none bundled |")
    assert len(rows) == len(catalog.capabilities) + 2


def test_page_holds_both_tables() -> None:
    """The page lists every catalog capability and every CCNL."""
    page = build_page(latest_catalog_year())
    assert "## Capabilities" in page
    assert "## CCNL coverage" in page
    assert "| `base_salary` | Paga base contrattuale | computed | simplified |" in page
    assert "\u2014" not in page.split("## CCNL coverage")[0]
