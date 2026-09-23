"""Tests for PayrollEngine — the unified period entry point."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from ccnl_engine.api.requests import PayrollRequest, PayrollYearRequest
from ccnl_engine.engine.payroll.service.engine import PayrollEngine
from ccnl_engine.payroll.domain.calendar import ExtraMonthSchedule, WorkCalendar
from ccnl_engine.payroll.domain.period import PeriodCalculationResult, PeriodState
from ccnl_engine.payroll.domain.run import PayrollRun

_ZERO = Decimal(0)
_CCNL = "metalmeccanico-federmeccanica.json"
_LEVEL = "C3"


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

    def test_result_carries_run(self) -> None:
        """PayrollEngine.calculate propagates the run to the result."""
        engine = PayrollEngine.from_builtin_data()
        req = _payroll_request()
        result = engine.calculate(req)
        assert result.run is req.run
        assert result.run is not None
        assert result.run.run_id == "2026-01-regular"


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
