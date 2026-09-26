"""Unit tests for the tax year attribution of a run from its payment date."""

from __future__ import annotations

from datetime import date

import pytest

from ccnl_engine.payroll.domain.tax_year import (
    DEFAULT_PAYMENT_DAY,
    TaxYearBasis,
    TaxYearPolicy,
    monthly_payment_date,
)
from ccnl_engine.shared.domain.errors import InvalidInputError

_DECEMBER_2026 = date(2026, 12, 1)
_POLICY = TaxYearPolicy()


@pytest.mark.parametrize(
    ("competence", "payment", "tax_year", "basis"),
    [
        (_DECEMBER_2026, date(2026, 12, 1), 2026, TaxYearBasis.CASH),
        (_DECEMBER_2026, date(2026, 12, 27), 2026, TaxYearBasis.CASH),
        (_DECEMBER_2026, date(2027, 1, 1), 2026, TaxYearBasis.EXTENDED_CASH),
        (_DECEMBER_2026, date(2027, 1, 10), 2026, TaxYearBasis.EXTENDED_CASH),
        (_DECEMBER_2026, date(2027, 1, 12), 2026, TaxYearBasis.EXTENDED_CASH),
        (_DECEMBER_2026, date(2027, 1, 13), 2027, TaxYearBasis.CASH),
        (_DECEMBER_2026, date(2027, 6, 28), 2027, TaxYearBasis.CASH),
        (_DECEMBER_2026, date(2028, 1, 10), 2028, TaxYearBasis.CASH),
        (_DECEMBER_2026, date(2028, 6, 28), 2028, TaxYearBasis.CASH),
        (date(2026, 11, 1), date(2027, 1, 5), 2026, TaxYearBasis.EXTENDED_CASH),
        (date(2027, 1, 1), date(2027, 1, 10), 2027, TaxYearBasis.CASH),
        (date(2025, 12, 1), date(2027, 1, 10), 2027, TaxYearBasis.CASH),
    ],
)
def test_attribution(
    competence: date, payment: date, tax_year: int, basis: TaxYearBasis
) -> None:
    """TUIR art. 51 c. 1: cash principle with the 12 January extension."""
    attribution = _POLICY.attribute(competence, payment)

    assert attribution.tax_year == tax_year
    assert attribution.basis is basis


def test_payment_before_competence_raises() -> None:
    """A payment before the competence period starts is rejected."""
    with pytest.raises(InvalidInputError, match="before the start") as info:
        _POLICY.attribute(_DECEMBER_2026, date(2026, 11, 30))
    assert info.value.feature == "tax_year"


class TestMonthlyPaymentDate:
    """monthly_payment_date pays a run on a fixed day of its month."""

    def test_default_day(self) -> None:
        """The default day is the 28th, present in every month."""
        assert monthly_payment_date(2026, 2, DEFAULT_PAYMENT_DAY) == date(2026, 2, 28)

    @pytest.mark.parametrize("day", [1, 10, 28])
    def test_valid_days(self, day: int) -> None:
        """Every day from 1 to 28 is accepted."""
        assert monthly_payment_date(2026, 2, day) == date(2026, 2, day)

    @pytest.mark.parametrize("day", [0, 29, 31, -1])
    def test_invalid_days(self, day: int) -> None:
        """A day some month does not have is rejected."""
        with pytest.raises(InvalidInputError, match="payment day") as info:
            monthly_payment_date(2026, 1, day)
        assert info.value.feature == "payment_date"
