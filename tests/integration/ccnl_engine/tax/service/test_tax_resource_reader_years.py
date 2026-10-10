"""The tax years the bundle ships: a sector tax file and a sector INPS file."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

import pytest

from ccnl_engine.shared.domain.errors import UnsupportedTaxYearError
from ccnl_engine.tax.service import tax_resource_reader
from ccnl_engine.tax.service.surtax_loaders import load_surtax_rules
from ccnl_engine.tax.service.tax_annual_assembler import load_year_rules
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


def test_the_bundle_ships_2026_and_2027() -> None:
    """Tax and INPS tables of 2026 and 2027 are bundled, none of another year."""
    assert supported_tax_years() == (2026, 2027)


@pytest.mark.usefixtures("_fresh_cache")
def test_a_year_needs_both_its_tax_and_its_inps_file(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A year with a tax file and no INPS file is not supported."""
    files = {
        "taxation/annual": {2026, 2027},
        "social_security/contribution": {2026},
    }
    monkeypatch.setattr(tax_resource_reader, "_years", files.__getitem__)

    assert supported_tax_years() == (2026,)


def test_a_missing_sector_table_names_the_supported_years() -> None:
    """The error of a missing table lists the years the bundle ships."""
    with pytest.raises(UnsupportedTaxYearError) as info:
        read_tax_rules_raw(2028, TaxSector.TERZIARIO)

    assert info.value.supported == (2026, 2027)
    assert info.value.sector == "terziario"


def test_a_missing_surtax_year_names_the_supported_years() -> None:
    """The surtax tables of an unbundled year raise with the same years."""
    with pytest.raises(UnsupportedTaxYearError) as info:
        load_surtax_rules(2028)

    assert info.value.supported == (2026, 2027)


@pytest.mark.parametrize("sector", list(TaxSector))
def test_2027_tables_are_provisional(sector: TaxSector) -> None:
    """The 2027 tax and INPS tables are flagged provisional, the 2026 ones not."""
    rules = load_year_rules(2027, sector, 50)
    current = load_year_rules(2026, sector, 50)

    assert rules.ruleset is not None
    assert rules.inps_ruleset is not None
    assert rules.ruleset.provisional
    assert rules.inps_ruleset.provisional
    assert current.ruleset is not None
    assert not current.ruleset.provisional


def test_2027_irpef_brackets_are_those_of_the_testo_unico() -> None:
    """Art. 11 c. 1 D.Lgs. 117/2026: 23% to 28,000, 33% to 50,000, 43% above."""
    brackets = load_year_rules(2027, TaxSector.TERZIARIO, 50).irpef_brackets

    assert [(b.up_to, b.rate) for b in brackets] == [
        (Decimal(28000), Decimal("0.23")),
        (Decimal(50000), Decimal("0.33")),
        (None, Decimal("0.43")),
    ]
