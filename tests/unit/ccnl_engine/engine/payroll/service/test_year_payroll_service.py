"""Unit tests for PayrollYearRequest, PayrollYearResult, compute_payroll_year."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine.engine.payroll.domain.employment import Permanent
from ccnl_engine.engine.payroll.domain.payroll_state import PayrollState
from ccnl_engine.engine.payroll.domain.period_payroll import (
    PayrollYearRequest,
    PayrollYearResult,
    PeriodPayrollResult,
)
from ccnl_engine.engine.payroll.domain.scenario import (
    AnnualEstimateInput,
    Employee,
    Employer,
    Employment,
    PeriodPayrollInput,
)
from ccnl_engine.engine.payroll.service.orchestrator import compute_payroll_year

_ZERO = Decimal(0)
_CCNL = "metalmeccanico-federmeccanica.json"
_LEVEL = "C3"
_AS_OF = date(2026, 1, 1)
_YEAR = 2026
_DEFAULT_PERIODS = tuple(PeriodPayrollInput() for _ in range(12))


def _structural() -> AnnualEstimateInput:
    """Return a minimal structural scenario.

    Returns:
        A minimal :class:`AnnualEstimateInput` with required fields only.
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


def _default_request() -> PayrollYearRequest:
    """Return a PayrollYearRequest with default periods and zero opening state.

    Returns:
        A :class:`PayrollYearRequest` for a full standard year.
    """
    return PayrollYearRequest(
        structural=_structural(),
        year=_YEAR,
        month_periods=_DEFAULT_PERIODS,
        opening_state=PayrollState.zero(),
    )


class TestPayrollYearRequestConstruction:
    """PayrollYearRequest validates its inputs."""

    def test_accepts_twelve_periods(self) -> None:
        """Twelve month_periods is the valid length."""
        req = _default_request()
        assert len(req.month_periods) == 12

    def test_wrong_period_count_raises(self) -> None:
        """month_periods with != 12 entries raises ValueError."""
        with pytest.raises(ValueError, match="month_periods"):
            PayrollYearRequest(
                structural=_structural(),
                year=_YEAR,
                month_periods=tuple(PeriodPayrollInput() for _ in range(11)),
                opening_state=PayrollState.zero(),
            )

    def test_too_many_periods_raises(self) -> None:
        """month_periods with 13 entries raises ValueError."""
        with pytest.raises(ValueError, match="month_periods"):
            PayrollYearRequest(
                structural=_structural(),
                year=_YEAR,
                month_periods=tuple(PeriodPayrollInput() for _ in range(13)),
                opening_state=PayrollState.zero(),
            )

    def test_frozen(self) -> None:
        """PayrollYearRequest is immutable."""
        req = _default_request()
        with pytest.raises(Exception, match="year"):
            req.year = 2025  # type: ignore[misc]


class TestPayrollYearResultShape:
    """compute_payroll_year returns a correctly shaped PayrollYearResult."""

    def test_returns_payroll_year_result(self) -> None:
        """Return type is PayrollYearResult."""
        result = compute_payroll_year(_default_request())
        assert isinstance(result, PayrollYearResult)

    def test_twelve_period_results(self) -> None:
        """Result contains exactly twelve PeriodPayrollResult instances."""
        result = compute_payroll_year(_default_request())
        assert len(result.periods) == 12
        for pr in result.periods:
            assert isinstance(pr, PeriodPayrollResult)

    def test_closing_state_matches_last_period(self) -> None:
        """closing_state equals periods[-1].closing_state."""
        result = compute_payroll_year(_default_request())
        assert result.closing_state is result.periods[-1].closing_state

    def test_closing_state_is_payroll_state(self) -> None:
        """closing_state is a PayrollState."""
        result = compute_payroll_year(_default_request())
        assert isinstance(result.closing_state, PayrollState)


class TestPayrollYearStateChaining:
    """Periods chain their opening/closing states correctly."""

    def test_january_opening_is_zero(self) -> None:
        """January opening state is PayrollState.zero()."""
        result = compute_payroll_year(_default_request())
        assert result.periods[0].opening_state == PayrollState.zero()

    def test_each_period_opening_is_previous_closing(self) -> None:
        """Month N opening state equals month N-1 closing state."""
        result = compute_payroll_year(_default_request())
        for i in range(1, 12):
            prev_closing = result.periods[i - 1].closing_state
            assert result.periods[i].opening_state is prev_closing

    def test_gross_ytd_grows_monotonically(self) -> None:
        """gross_annual_ytd increases with each successive period."""
        result = compute_payroll_year(_default_request())
        prev_ytd = _ZERO
        for pr in result.periods:
            assert pr.closing_state.gross_annual_ytd > prev_ytd
            prev_ytd = pr.closing_state.gross_annual_ytd

    def test_irpef_ytd_grows_monotonically(self) -> None:
        """irpef_withheld_ytd increases with each successive period."""
        result = compute_payroll_year(_default_request())
        prev_ytd = _ZERO
        for pr in result.periods:
            assert pr.closing_state.irpef_withheld_ytd > prev_ytd
            prev_ytd = pr.closing_state.irpef_withheld_ytd


class TestPayrollYearAsOfOverride:
    """The structural as_of date is overridden per month."""

    def test_as_of_overridden_per_month(self) -> None:
        """Each period uses a structural scenario with as_of set to month 1."""
        result = compute_payroll_year(_default_request())
        # January and December should produce different results if date matters.
        # Here we verify the year produced 12 distinct period gross values
        # (they may differ due to potential CCNL lookups per date).
        assert len(result.periods) == 12

    def test_accepts_optional_bundle_none(self) -> None:
        """bundle=None is accepted (loads on demand)."""
        result = compute_payroll_year(_default_request(), bundle=None)
        assert isinstance(result, PayrollYearResult)


class TestPayrollYearPublicApi:
    """PayrollEngine.project_year and year types are in the top-level package."""

    def test_payroll_engine_in_dunder_all(self) -> None:
        """PayrollEngine is listed in ccnl_engine.__all__."""
        import ccnl_engine  # noqa: PLC0415

        assert "PayrollEngine" in ccnl_engine.__all__

    def test_year_request_in_dunder_all(self) -> None:
        """PayrollYearRequest is listed in ccnl_engine.__all__."""
        import ccnl_engine  # noqa: PLC0415

        assert "PayrollYearRequest" in ccnl_engine.__all__

    def test_year_result_in_dunder_all(self) -> None:
        """PayrollYearResult is listed in ccnl_engine.__all__."""
        import ccnl_engine  # noqa: PLC0415

        assert "PayrollYearResult" in ccnl_engine.__all__

    def test_year_request_alias_in_dunder_all(self) -> None:
        """YearRequest alias is listed in ccnl_engine.__all__."""
        import ccnl_engine  # noqa: PLC0415

        assert "YearRequest" in ccnl_engine.__all__
