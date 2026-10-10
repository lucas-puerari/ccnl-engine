"""The capability matrix combines the registry with rule provenance."""

from __future__ import annotations

import pytest

from ccnl_engine.knowledge.capability.loaders import (
    load_capability_catalog,
)
from ccnl_engine.payroll.capability.models_catalog import (
    CapabilityApplicability,
    CapabilityEntry,
    CapabilityHandler,
    CapabilityImplementation,
    CapabilityLayer,
)
from scripts.docs.coverage_report import bundled_ccnls, coverage_cells
from scripts.docs.gen_capability_matrix import (
    build_page,
    capability_label,
    capability_rows,
    latest_catalog_year,
)

_IMPL = CapabilityImplementation


def _entry(implementation: CapabilityImplementation) -> CapabilityEntry:
    unsupported = implementation is _IMPL.UNSUPPORTED
    return CapabilityEntry(
        "x",
        CapabilityLayer.NET,
        implementation,
        CapabilityApplicability.OUTSIDE_INPUT
        if unsupported
        else CapabilityApplicability.ALWAYS,
        None if unsupported else CapabilityHandler.PIPELINE,
    )


@pytest.mark.parametrize(
    ("implementation", "counts", "label"),
    [
        (_IMPL.UNSUPPORTED, {"verified": 2}, "unavailable"),
        (_IMPL.CALLER_SUPPLIED, {"verified": 1}, "caller-supplied"),
        (_IMPL.PARTIAL, {"verified": 2}, "simplified"),
        (_IMPL.NATIVE, {"derived": 3, "assumed": 1}, "simplified"),
        (_IMPL.NATIVE, {"missing": 1}, "simplified"),
        (_IMPL.NATIVE, {"verified": 2}, "verified"),
        (_IMPL.NATIVE, {"verified": 1, "derived": 1}, "implemented"),
        (_IMPL.NATIVE, {}, "implemented"),
    ],
)
def test_label(
    implementation: CapabilityImplementation, counts: dict[str, int], label: str
) -> None:
    """Unavailable, caller-supplied, simplified, verified, implemented."""
    assert capability_label(_entry(implementation), counts) == label


def test_rows_show_the_registry_and_rule_counts() -> None:
    """A row shows every registry field and the rules by status."""
    catalog = load_capability_catalog(latest_catalog_year())
    counts = {"irpef": {"verified": 0, "derived": 24, "assumed": 0, "missing": 0}}
    rows = capability_rows(catalog, counts)
    (irpef,) = [row for row in rows if row.startswith("| `irpef` ")]
    (inail,) = [row for row in rows if row.startswith("| `inail` ")]
    assert irpef.endswith(
        "| net | native | always | pipeline | — | — | implemented | 0 / 24 / 0 / 0 |"
    )
    assert inail.endswith(
        "| unsupported | outside_input | — | `employer.inail_tariff_rate` | — "
        "| unavailable | none bundled |"
    )
    assert len(rows) == len(catalog.capabilities) + 2


def test_page_holds_both_tables() -> None:
    """The page lists every registry capability and every CCNL."""
    page = build_page(latest_catalog_year())
    assert "## Capabilities" in page
    assert "## CCNL coverage" in page
    assert "| `base_salary` | Paga base contrattuale | gross | native |" in page


def test_matrix_rows_are_the_index_cells() -> None:
    """Each CCNL row of the matrix prints the cells of the contracts index."""
    year = latest_catalog_year()
    catalog = load_capability_catalog(year)
    page = build_page(year)
    for ccnl in bundled_ccnls():
        cells = coverage_cells(catalog, ccnl)
        link = f"[{ccnl.meta.name}]({ccnl.meta.ccnl_id}.md)"
        l1, l2, l3 = cells.layers
        assert f"| {link} | {l1} | {l2} | {l3} | {cells.limits} |" in page
