"""Every bundled CCNL names a family of the catalog, and every family is used.

The family is descriptive metadata, kept apart from the INPS sector: a
family spans several INPS sectors and one INPS sector several families.
"""

from __future__ import annotations

from collections import defaultdict

from ccnl_engine.agreement.family.loaders import load_family_catalog
from ccnl_engine.catalog.loaders import list_contracts, load_ccnl

_BUNDLED = 133


def test_every_bundled_ccnl_names_a_family_of_the_catalog() -> None:
    """133/133 CCNLs carry a family id the catalog holds, with a reason."""
    known = load_family_catalog().by_id
    contracts = list_contracts()

    assert len(contracts) == _BUNDLED
    for summary in contracts:
        family = load_ccnl(summary.ccnl_id).meta.family
        assert family.id == summary.family
        assert set(family.ids) <= set(known), summary.ccnl_id
        assert family.reason.strip(), summary.ccnl_id


def test_every_family_of_the_catalog_has_a_ccnl() -> None:
    """No family of the catalog is empty."""
    used = {summary.family for summary in list_contracts()}

    assert used == set(load_family_catalog().by_id)


def test_a_family_is_not_the_inps_sector() -> None:
    """Metalworking spans industry and craft; one INPS sector spans many families."""
    sectors: dict[str, set[str]] = defaultdict(set)
    families: dict[str, set[str]] = defaultdict(set)
    for summary in list_contracts():
        tax_sector = load_ccnl(summary.ccnl_id).meta.tax_sector
        sectors[summary.family].add(tax_sector)
        families[tax_sector].add(summary.family)

    assert sectors["metalmeccanica"] == {"industria", "artigianato"}
    assert sectors["edilizia"] == {"edilizia", "artigianato"}
    assert len(families["terziario"]) > 1
