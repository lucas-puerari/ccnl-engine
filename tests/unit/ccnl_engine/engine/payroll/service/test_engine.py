"""Tests for PayrollEngine — the unified period/year entry point."""

from __future__ import annotations

import warnings
from datetime import date
from decimal import Decimal

from ccnl_engine.engine.payroll.domain.employment import Permanent
from ccnl_engine.engine.payroll.domain.payroll_state import PayrollState
from ccnl_engine.engine.payroll.domain.period_payroll import (
    AnnualPayrollSummary,
    PayrollYearRequest,
    PayrollYearResult,
    PeriodPayrollRequest,
    PeriodPayrollResult,
)
from ccnl_engine.engine.payroll.domain.scenario import (
    AnnualEstimateInput,
    Employee,
    Employer,
    Employment,
    PeriodPayrollInput,
)
from ccnl_engine.engine.payroll.service.engine import PayrollEngine

_ZERO = Decimal(0)
_CCNL = "metalmeccanico-federmeccanica.json"
_LEVEL = "C3"
_AS_OF = date(2026, 1, 1)


def _structural() -> AnnualEstimateInput:
    """Build a minimal structural scenario for tests.

    Returns:
        A minimal :class:`AnnualEstimateInput` using the Federmeccanica CCNL.
    """
    return AnnualEstimateInput(
        employee=Employee(level_code=_LEVEL),
        employment=Employment(
            ccnl=_CCNL,
            contract=Permanent(),
            employer=Employer(num_employees=50),
            as_of=_AS_OF,
        ),
    )


def _period_request() -> PeriodPayrollRequest:
    """Build a minimal period request with zero opening state.

    Returns:
        A :class:`PeriodPayrollRequest` for January with zero YTD.
    """
    return PeriodPayrollRequest(
        structural=_structural(),
        period=PeriodPayrollInput(),
        opening_state=PayrollState.zero(),
    )


def _year_request() -> PayrollYearRequest:
    """Build a minimal year request for 2026.

    Returns:
        A :class:`PayrollYearRequest` for 2026 with default monthly events.
    """
    return PayrollYearRequest(
        structural=_structural(),
        year=2026,
        month_periods=tuple(PeriodPayrollInput() for _ in range(12)),
        opening_state=PayrollState.zero(),
    )


class TestPayrollEngineConstruction:
    """PayrollEngine can be constructed with or without optional args."""

    def test_default_construction(self) -> None:
        """PayrollEngine() with no args succeeds."""
        engine = PayrollEngine()
        assert isinstance(engine, PayrollEngine)

    def test_construction_with_none_args(self) -> None:
        """PayrollEngine(bundle=None, repo=None) is explicit default."""
        engine = PayrollEngine(bundle=None, repo=None)
        assert isinstance(engine, PayrollEngine)


class TestCalculatePeriod:
    """PayrollEngine.calculate_period delegates to compute_period_payroll."""

    def test_returns_period_payroll_result(self) -> None:
        """calculate_period returns a PeriodPayrollResult."""
        engine = PayrollEngine()
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            result = engine.calculate_period(_period_request())
        assert isinstance(result, PeriodPayrollResult)

    def test_period_gross_positive(self) -> None:
        """calculate_period produces a positive period_gross."""
        engine = PayrollEngine()
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            result = engine.calculate_period(_period_request())
        assert result.period_gross > _ZERO

    def test_period_net_positive(self) -> None:
        """calculate_period produces a positive period_net."""
        engine = PayrollEngine()
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            result = engine.calculate_period(_period_request())
        assert result.period_net > _ZERO

    def test_closing_state_is_payroll_state(self) -> None:
        """calculate_period closing_state is a PayrollState."""
        engine = PayrollEngine()
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            result = engine.calculate_period(_period_request())
        assert isinstance(result.closing_state, PayrollState)


class TestProjectYear:
    """PayrollEngine.project_year delegates to compute_payroll_year."""

    def test_returns_payroll_year_result(self) -> None:
        """project_year returns a PayrollYearResult."""
        engine = PayrollEngine()
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            result = engine.project_year(_year_request())
        assert isinstance(result, PayrollYearResult)

    def test_twelve_period_results(self) -> None:
        """project_year produces exactly twelve period results."""
        engine = PayrollEngine()
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            result = engine.project_year(_year_request())
        assert len(result.periods) == 12

    def test_closing_state_equals_last_period(self) -> None:
        """project_year closing_state matches December's closing state."""
        engine = PayrollEngine()
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            result = engine.project_year(_year_request())
        assert result.closing_state == result.periods[-1].closing_state


class TestSummarize:
    """PayrollEngine.summarize aggregates a YearResult into annual totals."""

    def test_returns_annual_payroll_summary(self) -> None:
        """Summarize returns an AnnualPayrollSummary."""
        engine = PayrollEngine()
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            year_result = engine.project_year(_year_request())
            summary = engine.summarize(year_result)
        assert isinstance(summary, AnnualPayrollSummary)

    def test_total_gross_equals_sum_of_periods(self) -> None:
        """summarize.total_gross equals the sum of period_gross values."""
        engine = PayrollEngine()
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            year_result = engine.project_year(_year_request())
            summary = engine.summarize(year_result)
        expected = sum(p.period_gross for p in year_result.periods)
        assert summary.total_gross == expected

    def test_total_net_positive(self) -> None:
        """summarize.total_net is positive."""
        engine = PayrollEngine()
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            year_result = engine.project_year(_year_request())
            summary = engine.summarize(year_result)
        assert summary.total_net > _ZERO
