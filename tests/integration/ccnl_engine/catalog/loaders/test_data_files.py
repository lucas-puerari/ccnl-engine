"""Tests for CCNL data loaders and bundled data files."""

from datetime import date
from decimal import Decimal

import pydantic
import pytest
from pydantic import ValidationError

from ccnl_engine.agreement.facade import CCNL, TaxSector
from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.errors import UnsupportedTaxYearError
from ccnl_engine.sector.loaders import load_year_rules
from ccnl_engine.sector.models import YearRules

# ---------------------------------------------------------------------------
# load_ccnl helper
# ---------------------------------------------------------------------------


class TestLoadCcnl:
    """Unit tests for the load_ccnl helper."""

    def test_commercio_loads(self) -> None:
        """load_ccnl loads the commercio JSON and returns a CCNL instance."""
        ccnl = load_ccnl("commercio-confcommercio")
        assert isinstance(ccnl, CCNL)
        assert ccnl.meta.ccnl_id == "commercio-confcommercio"
        assert ccnl.meta.cnel_code == "H011"

    def test_commercio_has_eight_levels(self) -> None:
        """Commercio CCNL must contain exactly 8 classification levels."""
        ccnl = load_ccnl("commercio-confcommercio")
        assert len(ccnl.levels) == 8

    def test_commercio_level4_november_2025_salary(self) -> None:
        """Level 4 paga base on 2025-11-01 must be EUR 1,257.46."""
        ccnl = load_ccnl("commercio-confcommercio")
        level4 = next(lv for lv in ccnl.levels if lv.code == "4")
        assert level4.base_salary.value_at(date(2025, 11, 1)) == Decimal("1257.46")

    def test_commercio_level4_march_2025_salary(self) -> None:
        """Level 4 paga base on 2025-03-01 must be EUR 1,222.46."""
        ccnl = load_ccnl("commercio-confcommercio")
        level4 = next(lv for lv in ccnl.levels if lv.code == "4")
        assert level4.base_salary.value_at(date(2025, 3, 1)) == Decimal("1222.46")

    def test_commercio_level4_april_2024_salary(self) -> None:
        """Level 4 paga base on 2024-04-01 must be EUR 1,192.46."""
        ccnl = load_ccnl("commercio-confcommercio")
        level4 = next(lv for lv in ccnl.levels if lv.code == "4")
        assert level4.base_salary.value_at(date(2024, 4, 1)) == Decimal("1192.46")

    def test_load_ccnl_is_cached(self) -> None:
        """Two calls with the same filename return the identical CCNL object."""
        first = load_ccnl("commercio-confcommercio")
        second = load_ccnl("commercio-confcommercio")
        assert first is second

    def test_load_ccnl_is_immutable(self) -> None:
        """Mutating a field on the returned CCNL raises ValidationError."""
        ccnl = load_ccnl("commercio-confcommercio")
        with pytest.raises(pydantic.ValidationError):
            ccnl.schema_version = "0.6"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# load_year_rules helper
# ---------------------------------------------------------------------------


class TestLoadYearRules:
    """Unit tests for the load_year_rules helper."""

    def test_2026_terziario_loads(self) -> None:
        """load_year_rules(2026, terziario, 50) returns a valid YearRules."""
        yr = load_year_rules(2026, TaxSector.TERZIARIO, 50)
        assert isinstance(yr, YearRules)
        assert yr.year == 2026

    def test_2026_industria_loads(self) -> None:
        """load_year_rules(2026, industria, 50) returns a valid YearRules."""
        yr = load_year_rules(2026, TaxSector.INDUSTRIA, 50)
        assert isinstance(yr, YearRules)
        assert yr.year == 2026

    def test_employer_tier_small(self) -> None:
        """Firms <=15 employees get the small-employer tier for industria."""
        yr_small = load_year_rules(2026, TaxSector.INDUSTRIA, 15)
        yr_medium = load_year_rules(2026, TaxSector.INDUSTRIA, 16)
        assert yr_small.inps is not None
        assert yr_medium.inps is not None
        assert yr_small.inps.employer_rate < yr_medium.inps.employer_rate

    def test_employer_tier_boundary(self) -> None:
        """Firms exactly at tier boundary are included in the lower tier."""
        yr_at = load_year_rules(2026, TaxSector.TERZIARIO, 15)
        yr_above = load_year_rules(2026, TaxSector.TERZIARIO, 16)
        assert yr_at.inps is not None
        assert yr_above.inps is not None
        assert yr_at.inps.employer_rate < yr_above.inps.employer_rate

    def test_missing_year_raises(self) -> None:
        """A year with no data file raises the unsupported tax year error."""
        with pytest.raises(UnsupportedTaxYearError) as info:
            load_year_rules(1900, TaxSector.TERZIARIO, 50)
        assert info.value.year == 1900
        assert info.value.sector == "terziario"

    def test_load_year_rules_is_cached(self) -> None:
        """Two calls with the same arguments return the same frozen object."""
        first = load_year_rules(2026, TaxSector.TERZIARIO, 50)
        assert load_year_rules(2026, TaxSector.TERZIARIO, 50) is first

    def test_load_year_rules_cannot_be_mutated(self) -> None:
        """A field, a nested model and the brackets are all read-only."""
        rules = load_year_rules(2026, TaxSector.TERZIARIO, 50)
        assert rules.inps is not None
        with pytest.raises(ValidationError):
            rules.inps.employee_rate = Decimal(0)  # type: ignore[misc]
        with pytest.raises(ValidationError):
            rules.year = 2027  # type: ignore[misc]
        assert isinstance(rules.irpef_brackets, tuple)


# ---------------------------------------------------------------------------
# CCNL Metalmeccanico Federmeccanica
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("on", "rate"),
    [(date(2026, 12, 31), "0.0150"), (date(2027, 1, 1), "0.0170")],
)
def test_byblos_employer_rate_of_the_paper_ccnl(on: date, rate: str) -> None:
    """Byblos Scheda 1.5%; ipotesi 10/02/2026: "Da gennaio 2027 [...] 0,2%"."""
    ccnl = load_ccnl("carta-cartone-assocarta")
    (fund,) = ccnl.parameters.employer_funds
    assert fund.code == "BYBLOS"
    assert fund.rate.value_at(on) == Decimal(rate)


def test_previambiente_enrolled_amount_from_2027() -> None:
    """Ipotesi 09/12/2025: 22 + 8.50 = 30.50 EUR from January 2027."""
    (fund,) = load_ccnl("igiene-ambientale-utilitalia").parameters.employer_funds
    assert fund.enrolled_monthly is not None
    assert fund.enrolled_monthly.value_at(date(2026, 12, 31)) == Decimal("22.00")
    assert fund.enrolled_monthly.value_at(date(2027, 1, 1)) == Decimal("30.50")
