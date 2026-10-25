"""The contracts index shows three axes, coverage from the registry.

A row rates the core payroll path and names the contract's own limits;
what is the same for every contract is listed once, by scope.
"""

from __future__ import annotations

from ccnl_engine.capability.loaders import (
    load_capability_catalog,
)
from scripts.documentation.coverage.loaders import (
    SCOPES,
    build_coverage_report,
    bundled_ccnls,
    capability_scope,
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
    assert "| Core | Limits | Sources (v / d / a / m) | Readiness |" in page


def test_ccnl_limits_and_sources() -> None:
    """A missing note shows as a limit; sources count the file's rules."""
    year = latest_catalog_year()
    rows = {row.ccnl_id: row for row in build_coverage_report(year).ccnl_rows}
    assert (
        rows["ortofrutticoli-agrumari"].cells.limits
        == "base_salary, leave, seniority, sickness"
    )
    assert rows["anas"].cells.limits == "seniority"
    assert rows["federcasa"].cells.limits == "—"
    assert len(rows["anas"].sources.split(" / ")) == 4


def test_core_is_partial_only_when_the_contract_limits_a_core_capability() -> None:
    """Rows differ by contract: a core limit makes the core path partial."""
    year = latest_catalog_year()
    rows = {row.ccnl_id: row for row in build_coverage_report(year).ccnl_rows}

    assert rows["federcasa"].cells.core == "✅"
    assert rows["anas"].cells.core == "⚠️"
    assert len({row.cells.core for row in rows.values()}) == 2


def test_every_capability_has_one_scope_listed_once() -> None:
    """The page lists each registry capability under exactly one scope."""
    year = latest_catalog_year()
    catalog = load_capability_catalog(year)
    page = render_contracts_index(build_coverage_report(year), year)

    for entry in catalog.capabilities:
        assert capability_scope(entry) in SCOPES
        assert page.count(f"`{entry.feature}` ({entry.implementation.value})") == 1
    assert {capability_scope(e) for e in catalog.capabilities} == set(SCOPES)


def test_human_verified_needs_a_human_review_that_records_its_values() -> None:
    """A verified file without such a review is AI verified, never human."""
    year = latest_catalog_year()
    labels = {
        row.ccnl_id: row.verification_label
        for row in build_coverage_report(year).ccnl_rows
    }
    human = {
        ccnl.meta.ccnl_id
        for ccnl in bundled_ccnls()
        if any(
            review.reviewer_kind == "human" and review.checked
            for review in ccnl.verification.reviews
        )
    }
    assert {i for i, label in labels.items() if label == "Human verified"} <= human
    assert labels["commercio-confcommercio"] == "AI verified"
    assert labels["cooperative-sociali"] != "Human verified"


def test_index_leads_with_the_readiness_split() -> None:
    """The page states the tier counts before the total, from the data."""
    year = latest_catalog_year()
    report = build_coverage_report(year)
    page = render_contracts_index(report, year)
    production = sum(row.readiness == "production" for row in report.ccnl_rows)
    split = page.index(f"**{production} production, ")
    assert split < page.index("bundled contract configurations in all")
