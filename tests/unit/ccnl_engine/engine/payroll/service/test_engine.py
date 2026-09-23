"""Tests for PayrollEngine — the unified period entry point."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from ccnl_engine.api.requests import PayrollRequest, PayrollYearRequest
from ccnl_engine.engine.payroll.domain.period_payroll import PeriodId
from ccnl_engine.engine.payroll.service.engine import PayrollEngine
from ccnl_engine.payroll.domain.calendar import ExtraMonthSchedule, WorkCalendar
from ccnl_engine.payroll.domain.period import (
    PeriodCalculationRequest,
    PeriodCalculationResult,
    PeriodState,
)
from ccnl_engine.payroll.domain.run import PayrollRun

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


def _payroll_request() -> PayrollRequest:
    return PayrollRequest(
        run=PayrollRun.regular(2026, 1),
        payment_date=date(2026, 1, 28),
        ccnl_slug=_CCNL,
        level_code=_LEVEL,
        opening_state=PeriodState.zero(),
    )


class TestPayrollEngineConstruction:
    """PayrollEngine can be constructed with default args or from_builtin_data."""

    def test_default_construction(self) -> None:
        """PayrollEngine() with no args succeeds."""
        engine = PayrollEngine()
        assert isinstance(engine, PayrollEngine)

    def test_from_builtin_data(self) -> None:
        """from_builtin_data() returns a PayrollEngine instance."""
        engine = PayrollEngine.from_builtin_data()
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


class TestCalculate:
    """PayrollEngine.calculate accepts PayrollRequest with PayrollRun."""

    def test_returns_period_calculation_result(self) -> None:
        """Calculate returns a PeriodCalculationResult."""
        engine = PayrollEngine.from_builtin_data()
        result = engine.calculate(_payroll_request())
        assert isinstance(result, PeriodCalculationResult)

    def test_period_gross_positive(self) -> None:
        """Calculate produces a positive period_gross."""
        engine = PayrollEngine.from_builtin_data()
        result = engine.calculate(_payroll_request())
        assert result.period_gross > _ZERO

    def test_period_net_positive(self) -> None:
        """Calculate produces a positive period_net."""
        engine = PayrollEngine.from_builtin_data()
        result = engine.calculate(_payroll_request())
        assert result.period_net > _ZERO

    def test_matches_calculate_period_output(self) -> None:
        """Calculate and calculate_period produce the same gross and net."""
        engine = PayrollEngine.from_builtin_data()
        result_new = engine.calculate(_payroll_request())
        result_old = engine.calculate_period(_period_request())
        assert result_new.period_gross == result_old.period_gross
        assert result_new.period_net == result_old.period_net


class TestCalculateYear:
    """PayrollEngine.calculate_year accepts PayrollYearRequest."""

    def test_returns_year_result(self) -> None:
        """calculate_year returns a YearCalculationResult with period_results."""
        engine = PayrollEngine.from_builtin_data()
        request = PayrollYearRequest(
            year=2026,
            ccnl_slug=_CCNL,
            level_code=_LEVEL,
            calendar=WorkCalendar(
                year=2026,
                extra_months=(
                    ExtraMonthSchedule(name="tredicesima", payment_month=12),
                ),
            ),
        )
        result = engine.calculate_year(request)
        assert len(result.period_results) == 13
        assert result.annual_gross > _ZERO
