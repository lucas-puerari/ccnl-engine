"""Unit tests for TemporalContext domain type."""

from __future__ import annotations

from datetime import date

import pytest

from ccnl_engine.payroll.domain.employment_context import TemporalContext
from ccnl_engine.payroll.domain.tax_year import TaxYearBasis, TaxYearPolicy
from ccnl_engine.shared.domain.errors import InvalidInputError


class TestTemporalContextFromPeriod:
    """TemporalContext.from_period builds the correct axis references."""

    def test_competence_is_first_day_of_period(self) -> None:
        """Competence axis is the first calendar day of the competence month."""
        tctx = TemporalContext.from_period(2026, 6, date(2026, 6, 28))
        assert tctx.competence == date(2026, 6, 1)

    def test_fiscal_year_equals_period_year(self) -> None:
        """A run paid in its competence year belongs to that year."""
        tctx = TemporalContext.from_period(2026, 6, date(2026, 6, 28))
        assert tctx.fiscal_year == 2026
        assert tctx.fiscal_year_basis is TaxYearBasis.CASH

    def test_fiscal_year_extended_cash(self) -> None:
        """December paid on 10 January stays in the competence year."""
        tctx = TemporalContext.from_period(2026, 12, date(2027, 1, 10))
        assert tctx.competence == date(2026, 12, 1)
        assert tctx.fiscal_year == 2026
        assert tctx.fiscal_year_basis is TaxYearBasis.EXTENDED_CASH

    def test_fiscal_year_follows_late_payment(self) -> None:
        """December paid in June two years later belongs to the payment year."""
        tctx = TemporalContext.from_period(2026, 12, date(2028, 6, 28))
        assert tctx.fiscal_year == 2028

    def test_explicit_policy(self) -> None:
        """An injected policy is used instead of the default."""
        tctx = TemporalContext.from_period(
            2026, 12, date(2027, 1, 13), policy=TaxYearPolicy()
        )
        assert tctx.fiscal_year == 2027

    def test_payment_before_competence_raises(self) -> None:
        """A payment before the competence period is rejected."""
        with pytest.raises(InvalidInputError):
            TemporalContext.from_period(2026, 6, date(2026, 5, 31))

    def test_payment_equals_supplied_payment_date(self) -> None:
        """Payment axis equals the supplied payment_date unchanged."""
        payment = date(2026, 6, 28)
        tctx = TemporalContext.from_period(2026, 6, payment)
        assert tctx.payment == payment

    def test_january_competence_date(self) -> None:
        """January period produces competence = first of January."""
        tctx = TemporalContext.from_period(2026, 1, date(2026, 1, 31))
        assert tctx.competence == date(2026, 1, 1)

    def test_december_competence_date(self) -> None:
        """December period produces competence = first of December."""
        tctx = TemporalContext.from_period(2026, 12, date(2026, 12, 31))
        assert tctx.competence == date(2026, 12, 1)
