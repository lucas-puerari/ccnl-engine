"""Hypothesis property tests for the period-first engine: §8.4 coverage.

Properties verified here hold for any structurally valid input that the
period-first engine accepts without raising.  They complement the scenario
tests in test_scenarios_period_first.py.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from hypothesis import given, settings
from hypothesis import strategies as st

from ccnl_engine.payroll.application.calculate_period import calculate_period
from ccnl_engine.payroll.application.reconcile import reconcile
from ccnl_engine.payroll.domain.ledger import AccountKind, LedgerEntry
from ccnl_engine.payroll.domain.period import (
    PeriodCalculationRequest,
    PeriodState,
)
from ccnl_engine.payroll.domain.period_payroll import PeriodId

_CCNL = "metalmeccanico-federmeccanica.json"
_LEVEL = "C3"
_YEAR = 2026

_MONTHS = st.integers(min_value=1, max_value=12)
_IRPEF_YTD = st.decimals(
    min_value=Decimal(0), max_value=Decimal(5000), places=2, allow_nan=False
)
_MONTHS_CLOSED = st.integers(min_value=0, max_value=11)


def _req(
    month: int,
    irpef_ytd: Decimal = Decimal(0),
    regular_periods_closed: int = 0,
) -> PeriodCalculationRequest:
    """Build a request for ``month`` of 2026 with the given YTD values.

    Returns:
        A :class:`PeriodCalculationRequest` for the given parameters.
    """
    return PeriodCalculationRequest(
        period_id=PeriodId(year=_YEAR, month=month),
        payment_date=date(_YEAR, month, 28),
        ccnl_slug=_CCNL,
        level_code=_LEVEL,
        opening_state=PeriodState(
            regular_periods_closed=regular_periods_closed,
            tax_withholding_periods_closed=regular_periods_closed,
            irpef_withheld_ytd=irpef_ytd,
        ),
    )


class TestReconcilePassesUnderHypothesis:
    """reconcile() reports no violations for any structurally valid input."""

    @given(month=_MONTHS)
    @settings(max_examples=12)
    def test_all_months_pass_reconcile(self, month: int) -> None:
        """Every calendar month for C3 satisfies all seven reconcile invariants."""
        opening = PeriodState.zero()
        result = calculate_period(_req(month=month))
        r = reconcile(result, opening)
        assert r.ok, f"Month {month}: {r.violations}"

    @given(month=_MONTHS, irpef_ytd=_IRPEF_YTD)
    @settings(max_examples=30)
    def test_any_irpef_ytd_passes_reconcile(
        self, month: int, irpef_ytd: Decimal
    ) -> None:
        """Any non-negative irpef_withheld_ytd opening value passes reconcile."""
        opening = PeriodState(irpef_withheld_ytd=irpef_ytd)
        result = calculate_period(_req(month=month, irpef_ytd=irpef_ytd))
        r = reconcile(result, opening)
        assert r.ok, f"Month {month}, ytd={irpef_ytd}: {r.violations}"


class TestDeterminism:
    """calculate_period is deterministic for identical inputs."""

    @given(month=_MONTHS, irpef_ytd=_IRPEF_YTD)
    @settings(max_examples=20)
    def test_same_input_same_output(self, month: int, irpef_ytd: Decimal) -> None:
        """Two calls with identical inputs produce bit-for-bit identical results."""
        req = _req(month=month, irpef_ytd=irpef_ytd)
        first = calculate_period(req)
        second = calculate_period(req)
        assert first.period_gross == second.period_gross
        assert first.period_net == second.period_net
        assert first.period_employer_cost == second.period_employer_cost
        assert first.closing_state == second.closing_state


class TestNetNonNegative:
    """period_net and period_gross are non-negative for any valid opening state."""

    @given(month=_MONTHS, irpef_ytd=_IRPEF_YTD)
    @settings(max_examples=30)
    def test_gross_non_negative(self, month: int, irpef_ytd: Decimal) -> None:
        """period_gross is always >= 0."""
        result = calculate_period(_req(month=month, irpef_ytd=irpef_ytd))
        assert result.period_gross >= Decimal(0)

    @given(month=_MONTHS, irpef_ytd=_IRPEF_YTD)
    @settings(max_examples=30)
    def test_net_non_negative(self, month: int, irpef_ytd: Decimal) -> None:
        """period_net is always >= 0 (trattamento integrative can compensate)."""
        result = calculate_period(_req(month=month, irpef_ytd=irpef_ytd))
        assert result.period_net >= Decimal(0)


class TestSerializationLossless:
    """Pydantic JSON round-trip is lossless for all periods."""

    @given(month=_MONTHS)
    @settings(max_examples=12)
    def test_all_ledger_entries_survive_json(self, month: int) -> None:
        """Every LedgerEntry in every month round-trips through JSON unchanged."""
        result = calculate_period(_req(month=month))
        for original in result.ledger_entries:
            restored = LedgerEntry.model_validate_json(original.model_dump_json())
            assert restored == original

    @given(month=_MONTHS)
    @settings(max_examples=12)
    def test_closing_state_fields_are_exact_decimal(self, month: int) -> None:
        """YTD accumulators in closing_state carry the exact Decimal amounts."""
        result = calculate_period(_req(month=month))
        irpef_from_ledger = sum(
            e.amount
            for e in result.ledger_entries
            if e.account == AccountKind.ORDINARY_TAX
        )
        assert result.closing_state.irpef_withheld_ytd == irpef_from_ledger


class TestOpeningPlusMovementsEqualsClosing:
    """I11: closing = opening + ledger movements, verified via hypothesis."""

    @given(month=_MONTHS, months_closed=_MONTHS_CLOSED)
    @settings(max_examples=24)
    def test_gross_ytd_accumulates_correctly(
        self, month: int, months_closed: int
    ) -> None:
        """gross_ytd closing = opening.gross_ytd + CASH_EARNINGS for any month."""
        opening_gross = Decimal("1000.00") * months_closed
        opening = PeriodState(
            regular_periods_closed=months_closed,
            tax_withholding_periods_closed=months_closed,
            gross_ytd=opening_gross,
        )
        req = PeriodCalculationRequest(
            period_id=PeriodId(year=_YEAR, month=month),
            payment_date=date(_YEAR, month, 28),
            ccnl_slug=_CCNL,
            level_code=_LEVEL,
            opening_state=opening,
        )
        result = calculate_period(req)
        cash = sum(
            e.amount
            for e in result.ledger_entries
            if e.account == AccountKind.CASH_EARNINGS
        )
        assert result.closing_state.gross_ytd == opening_gross + cash
