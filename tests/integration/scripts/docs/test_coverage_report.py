"""The contracts index shows three axes, coverage from the registry."""

from __future__ import annotations

from ccnl_engine.knowledge.service.capability_catalog_loader import (
    load_capability_catalog,
)
from scripts.docs.coverage_report import (
    build_coverage_report,
    bundled_ccnls,
    coverage_cells,
    latest_catalog_year,
    render_contracts_index,
)


def test_index_rows_are_the_derived_cells() -> None:
    """Every row prints the cells of the shared derivation, no percentage."""
    year = latest_catalog_year()
    catalog = load_capability_catalog(year)
    report = build_coverage_report(year)
    cells = {c.meta.ccnl_id: coverage_cells(catalog, c) for c in bundled_ccnls()}
    assert {row.ccnl_id: row.cells for row in report.ccnl_rows} == cells
    page = render_contracts_index(report, year)
    assert "Coverage %" not in page
    assert "| L1 | L2 | L3 | Limits | Sources (v / d / a / m) | Readiness |" in page


def test_ccnl_limits_and_sources() -> None:
    """A missing note shows as a limit; sources count the file's rules."""
    year = latest_catalog_year()
    rows = {row.ccnl_id: row for row in build_coverage_report(year).ccnl_rows}
    assert rows["ortofrutticoli-agrumari"].cells.limits == "leave, sickness"
    assert rows["anas"].cells.limits == "—"
    assert len(rows["anas"].sources.split(" / ")) == 4
