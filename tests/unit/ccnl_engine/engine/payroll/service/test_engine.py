"""Tests for PayrollEngine — the unified period entry point."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from ccnl_engine.engine.payroll.domain.period_payroll import PeriodId
from ccnl_engine.engine.payroll.service.engine import PayrollEngine
from ccnl_engine.payroll.domain.period import (
    PeriodCalculationRequest,
    PeriodCalculationResult,
    PeriodState,
)

_ZERO = Decimal(0)
_CCNL = "metalmeccanico-federmeccanica.json"
_LEVEL = "C3"


def _period_request() -> PeriodCalculationRequest:
    """Build a minimal period-first request for January 2026.

    Returns:
        A :class:`PeriodCalculationRequest` for January 2026 with zero YTD.
    """
    return PeriodCalculationRequest(
        period_id=PeriodId(year=2026, month=1),
        payment_date=date(2026, 1, 28),
        ccnl_slug=_CCNL,
        level_code=_LEVEL,
        opening_state=PeriodState.zero(),
    )


class TestPayrollEngineConstruction:
    """PayrollEngine can be constructed with default args."""

    def test_default_construction(self) -> None:
        """PayrollEngine() with no args succeeds."""
        engine = PayrollEngine()
        assert isinstance(engine, PayrollEngine)


class TestCalculatePeriod:
    """PayrollEngine.calculate_period delegates to the period-first core."""

    def test_returns_period_calculation_result(self) -> None:
        """calculate_period returns a PeriodCalculationResult."""
        engine = PayrollEngine()
        result = engine.calculate_period(_period_request())
        assert isinstance(result, PeriodCalculationResult)

    def test_period_gross_positive(self) -> None:
        """calculate_period produces a positive period_gross."""
        engine = PayrollEngine()
        result = engine.calculate_period(_period_request())
        assert result.period_gross > _ZERO

    def test_period_net_positive(self) -> None:
        """calculate_period produces a positive period_net."""
        engine = PayrollEngine()
        result = engine.calculate_period(_period_request())
        assert result.period_net > _ZERO

    def test_closing_state_is_period_state(self) -> None:
        """calculate_period closing_state is a PeriodState."""
        engine = PayrollEngine()
        result = engine.calculate_period(_period_request())
        assert isinstance(result.closing_state, PeriodState)
