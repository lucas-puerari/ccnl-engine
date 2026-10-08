"""The tax years the bundle ships: a sector tax file and a sector INPS file."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from ccnl_engine.shared.domain.errors import UnsupportedTaxYearError
from ccnl_engine.tax.service import tax_resource_reader
from ccnl_engine.tax.service.surtax_loaders import load_surtax_rules
from ccnl_engine.tax.service.tax_resource_reader import (
    read_tax_rules_raw,
    supported_tax_years,
)

if TYPE_CHECKING:
    from collections.abc import Iterator

from ccnl_engine.contract.domain.identity import TaxSector


@pytest.fixture
def _fresh_cache() -> Iterator[None]:
    supported_tax_years.cache_clear()
    yield
    supported_tax_years.cache_clear()


def test_the_bundle_ships_2026_only() -> None:
    """Tax and INPS tables of 2026 are bundled, none of another year."""
    assert supported_tax_years() == (2026,)


@pytest.mark.usefixtures("_fresh_cache")
def test_a_year_needs_both_its_tax_and_its_inps_file(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A year with a tax file and no INPS file is not supported."""
    files = {
        "ccnl_engine.knowledge.tax.data": {2026, 2027},
        "ccnl_engine.knowledge.inps.data": {2026},
    }
    monkeypatch.setattr(tax_resource_reader, "_years", files.__getitem__)

    assert supported_tax_years() == (2026,)


def test_a_missing_sector_table_names_the_supported_years() -> None:
    """The error of a missing table lists the years the bundle ships."""
    with pytest.raises(UnsupportedTaxYearError) as info:
        read_tax_rules_raw(2027, TaxSector.TERZIARIO)

    assert info.value.supported == (2026,)
    assert info.value.sector == "terziario"


def test_a_missing_surtax_year_names_the_supported_years() -> None:
    """The surtax tables of an unbundled year raise with the same years."""
    with pytest.raises(UnsupportedTaxYearError) as info:
        load_surtax_rules(2027)

    assert info.value.supported == (2026,)
