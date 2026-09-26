"""Unit tests for TemporalContext domain type."""

from __future__ import annotations

from datetime import date

from ccnl_engine.payroll.domain.employment_context import TemporalContext


class TestTemporalContextFromPeriod:
    """TemporalContext.from_period builds the correct axis references."""

    def test_competence_is_first_day_of_period(self) -> None:
        """Competence axis is the first calendar day of the competence month."""
        tctx = TemporalContext.from_period(2026, 6, date(2026, 6, 28))
        assert tctx.competence == date(2026, 6, 1)

    def test_fiscal_year_equals_period_year(self) -> None:
        """Fiscal year equals the period year for single-year contracts."""
        tctx = TemporalContext.from_period(2026, 6, date(2026, 6, 28))
        assert tctx.fiscal_year == 2026

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
